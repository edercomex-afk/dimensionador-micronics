import streamlit as st
import math
import os

# Configuração da página
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# --- LÓGICA DO LOGOTIPO ---
logo_path = "logo.png"
if os.path.exists(logo_path):
    col_logo, col_titulo = st.columns([1, 3])
    with col_logo:
        st.image(logo_path, width=350)
    with col_titulo:
        st.title("Dimensionador de Filtro Prensa")
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.title("Cleanova Micronics | Dimensionador")

st.markdown("---")

# --- CABEÇALHO DE IDENTIFICAÇÃO ---
col_c, col_p, col_pr = st.columns(3)
with col_c:
    cliente = st.text_input("👤 Nome do Cliente")
with col_p:
    projeto = st.text_input("📂 Nome do Projeto")
with col_pr:
    produto = st.text_input("📦 Produto a ser filtrado")

col_opp, col_resp, col_vazio = st.columns(3)
with col_opp:
    n_opp = st.text_input("🔢 Nº OPP")
with col_resp:
    responsavel = st.text_input("👨‍💻 Responsável")

st.markdown("---")

# --- SIDEBAR: ENTRADA DE DADOS ---
st.sidebar.header("🚀 Capacidade e Operação")
solidos_dia = st.sidebar.number_input("Peso Total Sólidos Secos (ton/dia)", value=100.0)
horas_op = st.sidebar.number_input("Disponibilidade (Horas/dia)", value=20.0)
tempo_cycle = st.sidebar.number_input("Tempo de ciclo total (minutos)", value=60)

# NOVA ENTRADA: VAZÃO DE ALIMENTAÇÃO
st.sidebar.header("💧 Fluxo de Polpa")
vazao_lh = st.sidebar.number_input("Vazão de Alimentação de Polpa (L/h)", value=50000.0, step=1000.0)

st.sidebar.header("🧪 Propriedades Físicas")
sg_solidos = st.sidebar.number_input("Gravidade Específica (Sólidos Secos)", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Final da Torta (%)", value=20.0)
umidade = umidade_input / 100

st.sidebar.header("📝 Detalhes Técnicos")
temp_processo = st.sidebar.number_input("Temperatura (°C)", value=25)
ph_solucao = st.sidebar.number_input("pH da Solução", value=7.0)
lavador_lonas = st.sidebar.selectbox("Lavador de Lonas?", ["Sim", "Não"])
aut_nivel = st.sidebar.selectbox("Nível de Automatização", ["Baixo", "Médio", "Alto"])
lavador_torta = st.sidebar.selectbox("Lavador de Torta?", ["Sim", "Não"])
membrana = st.sidebar.selectbox("Membrana de Compressão?", ["Sim", "Não"])

st.sidebar.header("📐 Geometria da Placa")
recesso_manual = st.sidebar.number_input("Espessura de câmara (mm)", value=30.0)

# --- BASE DE DADOS TÉCNICA ---
tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100},
    {"nom": 1000, "area_ref": 1.80, "vol_ref": 25,  "max": 100},
    {"nom": 800,  "area_ref": 1.10, "vol_ref": 15,  "max": 84},
    {"nom": 630,  "area_ref": 0.65, "vol_ref": 9,   "max": 74},
    {"nom": 400,  "area_ref": 0.25, "vol_ref": 3,   "max": 74},
]

# --- LÓGICA DE CÁLCULO ---
ciclos_dia = (horas_op * 60) / tempo_cycle if tempo_cycle > 0 else 0
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_torta_m3 = (massa_seco_ciclo / (1 - umidade)) / dens_torta if (1-umidade) > 0 else 0
vol_total_L = vol_torta_m3 * 1000

# --- EXIBIÇÃO DE MÉTRICAS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Vol. Torta p/ Ciclo", f"{vol_total_L:.0f} L")
col2.metric("Massa p/ Ciclo", f"{massa_seco_ciclo:.2f} t")
col3.metric("Vazão de Polpa", f"{vazao_lh:,.0f} L/h")
col4.metric("Ciclos p/ Dia", f"{ciclos_dia:.1f}")

st.subheader("📋 Opções de Dimensionamento e Fluxo")

res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso_manual / 30)
    num_placas = math.ceil(vol_total_L / vol_ajustado) if vol_ajustado > 0 else 0
    area_total = num_placas * p["area_ref"]
    
    # CÁLCULO DA TAXA DE FILTRAÇÃO (Fluxo)
    fluxo = vazao_lh / area_total if area_total > 0 else 0
    
    status = "✅ OK"
    obs = "-"
    
    # Alerta de Fluxo (Exemplo: Alerta se acima de 450 L/m²h)
    if fluxo > 450:
        status = "⚠️ Fluxo Alto"
        obs = f"Taxa de {fluxo:.0f} L/m²h excede recomendação."
    elif p["nom"] == 1500 and num_placas > 120:
        status = "⚠️ Dividir"
        obs = f"Sugerido 2 filtros de {math.ceil(num_placas/2)} placas."
    elif num_placas > p["max"]:
        status = "❌ Excedeu Placas"
        obs = f"Máximo {p['max']} placas."
    
    res_list.append({
        "Modelo (mm)": f"{p['nom']} x {p['nom']}",
        "Placas": num_placas,
        "Área Total (m²)": f"{area_total:.2f}",
        "Taxa Fluxo (L/m²h)": f"{fluxo:.1f}",
        "Status": status,
        "Observação": obs
    })

st.table(res_list)
st.info("💡 A Taxa de Fluxo (L/m²h) ajuda a validar se a lona e a bomba estão equilibradas para o ciclo desejado.")
