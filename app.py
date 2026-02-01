import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import io

# 1. Configuração da página
st.set_page_config(page_title="Cleanova Micronics | V46 Full", layout="wide")

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
    
    plt.title(f"Comportamento Operacional: Bomba & Filtro")
    fig.tight_layout()
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=150)
    img_buf.seek(0)
    return fig, img_buf

# --- INTERFACE PRINCIPAL ---
st.title("Cleanova Micronics | Engenharia de Aplicação V46")
st.markdown("---")

# CABEÇALHO (Dados do Cliente)
c1, c2, c3 = st.columns(3)
cliente = c1.text_input("👤 Nome do Cliente")
projeto = c2.text_input("📂 Nome do Projeto")
n_opp = c3.text_input("🔢 Número da OPP")

c4, c5, c6 = st.columns(3)
produto = c4.text_input("📦 Produto")
mercado = c5.text_input("🏭 Mercado")
responsavel = c6.text_input("👨‍💻 Responsável")

st.markdown("---")

# SIDEBAR (Todos os parâmetros de volta)
st.sidebar.header("🚀 Capacidade & Ciclo")
solidos_dia = st.sidebar.number_input("Sólidos secos/dia (ton/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade Operacional (%)", 0, 100, 90)
tempo_cycle = st.sidebar.number_input("Tempo de Ciclo (min)", value=45)

st.sidebar.header("🧪 Propriedades do Lodo")
vazao_input = st.sidebar.number_input("Vazão de Pico (L/h)", value=50000.0)
vol_lodo_dia = st.sidebar.number_input("Volume lodo/dia (m³/dia)", value=500.0)
sg_solidos = st.sidebar.number_input("SG Sólidos Secos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Torta (%)", value=20.0)
recesso = st.sidebar.number_input("Espessura câmara (mm)", value=30.0)
pressao_input = st.sidebar.slider("Pressão de Filtração (Bar)", 1, 15, 7)

st.sidebar.header("💰 OPEX")
custo_kwh = st.sidebar.number_input("Custo Energia (R$/kWh)", value=0.65)
custo_lona_un = st.sidebar.number_input("Preço Lona (R$/unid)", value=450.0)
vida_lona_ciclos = st.sidebar.number_input("Vida útil lona (Ciclos)", value=2000)

# --- CÁLCULOS TÉCNICOS ---
umidade = umidade_input / 100
disp_h = 24 * (utilizacao_pct / 100)
ciclos_dia = (disp_h * 60) / tempo_cycle if tempo_cycle > 0 else 0
ciclos_mes = ciclos_dia * 30

peso_torta_dia = solidos_dia / (1 - umidade) if (1-umidade) > 0 else 0
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_total_L_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

# Lógica de Modelos
tamanhos = [
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70, "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37, "max": 100},
    {"nom": 1000, "area_ref": 1.95, "vol_ref": 25, "max": 90}
]
res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    res_list.append({"Modelo (mm)": f"{p['nom']}x{p['nom']}", "Placas": num_placas, "Area": f"{num_placas * p['area_ref']:.1f}"})

# Lógica de Bomba (Pemo / Weir)
if pressao_input <= 6:
    marca, tipo = "PEMO (Itália)", "Série AO/AB - Centrífuga Revestida"
else:
    marca, tipo = "WEIR (Warman/GEHO)", "Série Warman AH ou GEHO ZPR"

# --- EXIBIÇÃO ---
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Peso Torta", f"{peso_torta_dia:.1f} t/d")
k2.metric("Horas Úteis", f"{disp_h:.1f} h/d")
k3.metric("Ciclos/Mês", f"{ciclos_mes:.0f}")
k4.metric("Vol. Requerido", f"{vol_total_L_req:.0f} L")
k5.metric("Pressão", f"{pressao_input} Bar")

st.subheader("📋 Performance por Modelo")
st.table(res_list)

col_graf, col_bomba = st.columns([2, 1])
with col_graf:
    st.subheader("📊 Gráfico de Performance (Pressão x Vazão)")
    fig, buf = gerar_grafico_vazao_pressao(pressao_input, vazao_input)
    st.pyplot(fig)

with col_bomba:
    st.subheader("🛡️ Bomba Recomendada")
    st.success(f"**Marca:** {marca}")
    st.info(f"**Tipo:** {tipo}")
    st.write(f"Vazão de Pico: {vazao_input:,.0f} L/h")

st.markdown("---")
if cliente and n_opp:
    st.success("✅ Tudo pronto para o relatório!")
else:
    st.warning("⚠️ Preencha os dados do cliente para habilitar o PDF.")
