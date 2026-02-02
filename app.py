import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import io

# 1. Configuração da página
st.set_page_config(page_title="Cleanova Micronics | V54 Inteligente", layout="wide")

def clean_txt(text):
    return str(text).encode('latin-1', 'ignore').decode('latin-1')

# --- FUNÇÃO DO SEMÁFORO DE TAXA ---
def validar_taxa(taxa_calc, material_selecionado):
    # Referências de mercado (kg/m2.h)
    referencias = {
        "Ferro": 450,
        "Rejeito": 220,
        "Litio": 120,
        "Quimico": 50,
        "Biologico": 10
    }
    limite = referencias.get(material_selecionado, 100)
    
    if taxa_calc <= limite:
        return "✅ Segura", "Seu dimensionamento está conservador e robusto.", "green"
    elif taxa_calc <= limite * 1.3:
        return "🟡 Atenção", "Taxa agressiva. Exigirá condicionamento químico perfeito.", "orange"
    else:
        return "🔴 Crítica", "Risco alto de torta úmida. Sugerimos aumentar o filtro.", "red"

# --- FUNÇÃO GRÁFICO ---
def gerar_grafico(pressao_alvo, vazao_pico):
    tempo = np.linspace(0, 45, 100)
    pressao = pressao_alvo * (1 - np.exp(-0.15 * tempo))
    vazao = vazao_pico * np.exp(-0.12 * tempo)
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.set_xlabel('Tempo (min)')
    ax1.set_ylabel('Pressao (Bar)', color='tab:red')
    ax1.plot(tempo, pressao, color='tab:red', linewidth=3)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Vazao (L/h)', color='tab:blue')
    ax2.plot(tempo, vazao, color='tab:blue', linewidth=3)
    plt.title("Curva de Performance: Filtro e Bomba")
    fig.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=100)
    plt.close(fig)
    img_buf.seek(0)
    return img_buf

# --- INTERFACE ---
st.title("Cleanova Micronics | Dimensionador V54 (Consultivo)")

# Cabeçalho em Negrito
c1, c2, c3 = st.columns(3)
cliente = c1.text_input("**Cliente**")
projeto = c2.text_input("**Projeto**")
n_opp = c3.text_input("**Numero da OPP**")

c4, c5, c6 = st.columns(3)
produto = c4.selectbox("**Material de Referência**", ["Ferro", "Rejeito", "Litio", "Quimico", "Biologico"])
mercado = c5.text_input("**Mercado**")
responsavel = c6.text_input("**Responsavel**")

# Sidebar
st.sidebar.header("🚀 Capacidade")
solidos_dia = st.sidebar.number_input("Sólidos (t/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade (%)", 0, 100, 90)
tempo_cycle = st.sidebar.number_input("Ciclo (min)", value=45)

st.sidebar.header("🧪 Processo")
vol_lodo_dia = st.sidebar.number_input("Volume Lodo (m³/dia)", value=500.0)
vazao_pico = st.sidebar.number_input("Vazão Pico Bomba (L/h)", value=50000.0)
sg_solidos = st.sidebar.number_input("SG Sólidos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade (%)", value=20.0)
recesso = st.sidebar.number_input("Recesso (mm)", value=30.0)
pressao_manual = st.sidebar.slider("Pressão (Bar)", 1, 15, 7)

# CÁLCULOS
umidade = umidade_input / 100
disp_h = 24 * (utilizacao_pct / 100)
ciclos_dia = (disp_h * 60) / tempo_cycle if tempo_cycle > 0 else 0
massa_seco_ciclo = (solidos_dia * 1000) / ciclos_dia if ciclos_dia > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta)

# Modelos
tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100},
]

res_list = []
exibiu_erro = False
for p in tamanhos:
    v_adj = p["vol_ref"] * (recesso / 30)
    n_placas = math.ceil(vol_req / v_adj) if v_adj > 0 else 0
    if p["nom"] > 1000 and n_placas < 25: continue
    
    if n_placas <= p["max"]:
        res_list.append({"Modelo (mm)": f"{p['nom']}x{p['nom']}", "Placas": n_placas, "Area": n_placas * p["area_ref"], "Status": "✅ OK"})
    elif not exibiu_erro:
        res_list.append({"Modelo (mm)": f"{p['nom']}x{p['nom']}", "Placas": n_placas, "Area": n_placas * p["area_ref"], "Status": "❌ Limite"})
        exibiu_erro = True

# KPI DE TAXA (O Coração da V54)
area_selecionada = res_list[0]["Area"] if res_list else 1
taxa_calc = massa_seco_ciclo / (area_selecionada * (tempo_cycle / 60))
status_t, msg_t, cor_t = validar_taxa(taxa_calc, produto)

# OPEX
marca = "PEMO (Italia)" if pressao_manual <= 6 else "WEIR (Warman/GEHO)"

# EXIBIÇÃO
k1, k2, k3 = st.columns(3)
k1.metric("Taxa de Filtração", f"{taxa_calc:.1f} kg/m².h")
k2.metric("Vol. Torta/Ciclo", f"{vol_req:.0f} L")
k3.metric("Bomba", marca)

st.subheader("📋 Resultados de Dimensionamento")
st.table(res_list)

# SEMÁFORO VISUAL
st.markdown(f"### Diagnóstico Micronics: :{cor_t}[{status_t}]")
st.info(f"**Análise:** {msg_t} (Referência para {produto}: {taxa_calc:.1f} vs Limite Ideal)")

col_graf, col_fin = st.columns([2, 1])
with col_graf:
    graf_buf = gerar_grafico(pressao_manual, vazao_pico)
    st.image(graf_buf)
with col_fin:
    st.success(f"💰 Bomba Recomendada: {marca}")
