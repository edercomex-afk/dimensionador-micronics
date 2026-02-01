import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import io

# 1. Configuração da página
st.set_page_config(page_title="Cleanova Micronics | V48 Full", layout="wide")

# --- FUNÇÃO PARA GERAR O GRÁFICO ---
def gerar_grafico_vazao_pressao(pressao_alvo, vazao_pico):
    tempo = np.linspace(0, 45, 100)
    pressao = pressao_alvo * (1 - np.exp(-0.15 * tempo))
    vazao = vazao_pico * np.exp(-0.12 * tempo)
    
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.set_xlabel('Tempo de Ciclo (min)')
    ax1.set_ylabel('Pressão (Bar)', color='tab:red')
    ax1.plot(tempo, pressao, color='tab:red', linewidth=3)
    ax1.grid(True, linestyle='--', alpha=0.5)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Vazão (L/h)', color='tab:blue')
    ax2.plot(tempo, vazao, color='tab:blue', linewidth=3)
    plt.title("Comportamento Dinâmico: Bomba & Filtro")
    fig.tight_layout()
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=150)
    img_buf.seek(0)
    return fig, img_buf

# --- INTERFACE PRINCIPAL ---
st.title("Cleanova Micronics | Dimensionador, OPEX & Bombas V48")

# Cabeçalho
c1, c2, c3 = st.columns(3)
u_cliente = c1.text_input("👤 Cliente")
u_projeto = c2.text_input("📂 Projeto")
u_opp = c3.text_input("🔢 OPP")

# SIDEBAR COMPLETA
st.sidebar.header("🚀 Capacidade & Ciclo")
solidos_dia = st.sidebar.number_input("Sólidos secos (t/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade (%)", 0, 100, 90)
tempo_cycle = st.sidebar.number_input("Ciclo (min)", value=45)

st.sidebar.header("🧪 Processo")
vazao_pico = st.sidebar.number_input("Vazão Pico Bomba (L/h)", value=50000.0)
sg_solidos = st.sidebar.number_input("SG Sólidos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Torta (%)", value=20.0)
recesso = st.sidebar.number_input("Recesso (mm)", value=30.0)
pressao_manual = st.sidebar.slider("Pressão Filtração (Bar)", 1, 15, 7)

st.sidebar.header("💰 Custos (OPEX)")
custo_kwh = st.sidebar.number_input("Custo Energia (R$/kWh)", value=0.65)
custo_lona_un = st.sidebar.number_input("Preço Lona (R$/unid)", value=450.0)
vida_lona_ciclos = st.sidebar.number_input("Vida útil lona (Ciclos)", value=2000)

# --- CÁLCULOS TÉCNICOS ---
umidade = umidade_input / 100
disp_h = 24 * (utilizacao_pct / 100)
ciclos_dia = (disp_h * 60) / tempo_cycle if tempo_cycle > 0 else 0
ciclos_mes = ciclos_dia * 30
peso_torta_dia = solidos_dia / (1 - umidade) if (1-umidade) > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
vol_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

# Modelagem Micronics (8 modelos)
tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100},
    {"nom": 1000, "area_ref": 1.95, "vol_ref": 25,  "max": 90},
    {"nom": 800,  "area_ref": 1.15, "vol_ref": 14,  "max": 80},
    {"nom": 630,  "area_ref": 0.65, "vol_ref": 8.5, "max": 60},
    {"nom": 470,  "area_ref": 0.35, "vol_ref": 4.2, "max": 40},
]

res_list = []
for p in tamanhos:
    v_adj = p["vol_ref"] * (recesso / 30)
    n_placas = math.ceil(vol_req / v_adj) if v_adj > 0 else 0
    if p["nom"] > 1000 and n_placas < 25: continue
    status = "✅ OK" if n_placas <= p["max"] else "❌ Limite"
    res_list.append({"Modelo (mm)": f"{p['nom']}x{p['nom']}", "Placas": n_placas, "Area": f"{n_placas * p['area_ref']:.1f}", "Status": status})

# --- CÁLCULOS OPEX ---
energia_mes = (20 * disp_h * 30) * custo_kwh
if res_list:
    n_placas_ref = int(res_list[0]["Placas"])
    lonas_mes = (ciclos_mes / vida_lona_ciclos) * (n_placas_ref * 2) * custo_lona_un
    total_opex_mes = energia_mes + lonas_mes
    opex_ton_seca = total_opex_mes / (solidos_dia * 30) if solidos_dia > 0 else 0
else:
    lonas_mes = total_opex_mes = opex_ton_seca = 0

# Bomba
if pressao_manual <= 6: marca, linha = "PEMO (Itália)", "Série AO/AB"
else: marca, linha = "WEIR (Warman/GEHO)", "Série AH/ZPR"

# --- EXIBIÇÃO ---
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Peso Torta", f"{peso_torta_dia:.1f} t/d")
k2.metric("Ciclos/Mês", f"{ciclos_mes:.0f}")
k3.metric("OPEX/t seca", f"R$ {opex_ton_seca:.2f}")
k4.metric("Vol. Torta/Ciclo", f"{vol_req:.0f} L")
k5.metric("Bomba", marca)

st.subheader("📋 Resultados de Dimensionamento")
st.table(res_list)

st.subheader("📊 Performance e OPEX")
col_graf, col_fin = st.columns([2, 1])

with col_graf:
    fig, buf = gerar_grafico_vazao_pressao(pressao_manual, vazao_pico)
    st.pyplot(fig)

with col_fin:
    st.write("**Resumo Financeiro Mensal**")
    st.info(f"⚡ Energia: R$ {energia_mes:,.2f}")
    st.info(f"🧵 Lonas: R$ {lonas_mes:,.2f}")
    st.success(f"💰 Total OPEX: R$ {total_opex_mes:,.2f}")
    st.warning(f"🛠️ Bomba: {marca} ({linha})")

st.markdown("---")
if u_cliente and u_opp:
    st.success("✅ Relatório pronto para exportação.")
    # Aqui reinseriríamos a função de PDF V47 para completar
else:
    st.warning("Preencha os campos obrigatórios para finalizar.")
