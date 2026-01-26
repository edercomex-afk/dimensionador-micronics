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
with col_c: cliente = st.text_input("👤 Nome do Cliente")
with col_p: projeto = st.text_input("📂 Nome do Projeto")
with col_pr: produto = st.text_input("📦 Produto a ser filtrado")

col_opp, col_resp, col_vazio = st.columns(3)
with col_opp: n_opp = st.text_input("🔢 Nº OPP")
with col_resp: responsavel = st.text_input("👨‍💻 Responsável pelo projeto")

st.markdown("---")

# --- SIDEBAR: ENTRADA DE DADOS ---
st.sidebar.header("🚀 Capacidade e Operação")
solidos_dia = st.sidebar.number_input("Peso Total Sólidos Secos (ton/dia)", value=100.0, step=1.0)
horas_op = st.sidebar.number_input("Disponibilidade (Horas/dia)", value=20.0, step=0.5)
tempo_cycle = st.sidebar.number_input("Tempo de ciclo total (minutos)", value=60, step=1)

# SEÇÃO CONSOLIDADA: FLUXO DE POLPA
st.sidebar.header("💧 Fluxo de Polpa")
vol_polpa_dia = st.sidebar.number_input("Volume de Lodo/Polpa por dia (m³/dia)", value=500.0, step=10.0)
vazao_lh = st.sidebar.number_input("Vazão de Alimentação de Polpa (L/h)", value=50000.0, step=1000.0)

st.sidebar.header("🧪 Propriedades Físicas")
sg_solidos = st.sidebar.number_input("Gravidade Específica (Sólidos Secos)", value=2.8, step=0.1)
umidade_input = st.sidebar.number_input("Umidade Final da Torta (%)", value=20.0, step=0.5)
umidade = umidade_input / 100

st.sidebar.header("📝 Detalhes Técnicos")
temp_processo = st.sidebar.number_input("Temperatura (°C)", value=25)
ph_solucao = st.sidebar.number_input("pH da Solução", value=7.0, step=0.1)
lavador_lonas = st.sidebar.selectbox("Lavador de Lonas?", ["Sim", "Não"])
aut_nivel = st.sidebar.selectbox("Nível de Automatização", ["Baixo", "Médio", "Alto"])
lavador_torta = st.sidebar.selectbox("Lavador de Torta?", ["Sim", "Não"])
membrana = st.sidebar.selectbox("Membrana de Compressão?", ["Sim", "Não"])

st.sidebar.header("📐 Geometria da Placa")
recesso_manual = st.sidebar.number_input("Espessura de câmara (mm)", value=30.0, step=1.0)

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
vol_polpa_ciclo_L = (vol_polpa_dia / ciclos_dia) * 1000 if ciclos_dia > 0 else 0

# Densidade da torta
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_torta_m3 = (massa_seco_ciclo / (1 - umidade)) / dens_torta if (1-umidade) > 0 else 0
vol_total_L_req = vol_torta_m3 * 1000

# --- EXIBIÇÃO DE MÉTRICAS ---
st.subheader(f"Resumo Técnico: {produto if produto else 'Geral'}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Vol. Polpa p/ Ciclo", f"{vol_polpa_ciclo_L:,.0f} L")
col2.metric("Vol. Torta p/ Ciclo", f"{vol_total_L_req:,.0f} L")
col3.metric("Massa Seca p/ Ciclo", f"{massa_seco_ciclo:.2f} t")
col4.metric("Conc. Sólidos Calc.", f"{(solidos_dia/vol_polpa_dia)*100:.1f} %" if vol_polpa_dia > 0 else "0%")

st.subheader("📋 Opções de Dimensionamento")

res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso_manual / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    area_total = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_total if area_total > 0 else 0
    
    status = "✅ OK"
    obs = "-"
    
    if vol_total_L_req > vol_polpa_ciclo_L:
        status = "❌ Erro Dados"
        obs = "Volume de torta calculado é maior que o volume de polpa fornecido."
    elif fluxo > 500:
        status = "⚠️ Fluxo Alto"
        obs = f"Taxa de {fluxo:.0f} L/m²h acima do recomendado."
    elif p["nom"] == 1500 and num_placas > 120:
        status = "⚠️ Dividir"
        obs = "Limite de 120 placas excedido para 1500mm."
    elif num_placas > p["max"]:
        status = "❌ Excedeu Limite"
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
