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

st.markdown("---")

# --- CABEÇALHO ---
c1, c2, c3 = st.columns(3)
with c1: cliente = st.text_input("👤 Cliente")
with c2: projeto = st.text_input("📂 Projeto")
with c3: produto = st.text_input("📦 Produto")

# --- SIDEBAR: ENTRADA DE DADOS ---
st.sidebar.header("🚀 Capacidade e Operação")
solidos_dia = st.sidebar.number_input("Peso Total Sólidos Secos (ton/dia)", value=100.0)

# NOVO CAMPO: VOLUME DE POLPA POR DIA
vol_polpa_dia = st.sidebar.number_input("Volume de Lodo/Polpa por dia (m³/dia)", value=500.0)

horas_op = st.sidebar.number_input("Disponibilidade (Horas/dia)", value=20.0)
tempo_cycle = st.sidebar.number_input("Tempo de ciclo total (minutos)", value=60)

st.sidebar.header("💧 Fluxo de Polpa")
vazao_lh = st.sidebar.number_input("Vazão de Alimentação de Polpa (L/h)", value=50000.0)

st.sidebar.header("🧪 Propriedades Físicas")
sg_solidos = st.sidebar.number_input("Gravidade Específica (Sólidos)", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Final da Torta (%)", value=20.0)
umidade = umidade_input / 100

st.sidebar.header("📐 Geometria")
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
ciclos_dia = (horas_op * 60) / tempo_cycle
massa_seco_ciclo = solidos_dia / ciclos_dia
vol_polpa_ciclo_L = (vol_polpa_dia / ciclos_dia) * 1000

# Cálculo do volume de torta (Espaço ocupado nas câmaras)
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0))
vol_torta_m3 = (massa_seco_ciclo / (1 - umidade)) / dens_torta
vol_total_L_requerido = vol_torta_m3 * 1000

# --- EXIBIÇÃO ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Vol. Polpa p/ Ciclo", f"{vol_polpa_ciclo_L:,.0f} L")
col2.metric("Vol. Torta p/ Ciclo", f"{vol_total_L_requerido:.0f} L")
col3.metric("Massa Seca p/ Ciclo", f"{massa_seco_ciclo:.2f} t")
col4.metric("Conc. Sólidos Calc.", f"{(solidos_dia/vol_polpa_dia)*100:.1f} %")

st.subheader("📋 Dimensionamento e Verificação de Processo")

res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso_manual / 30)
    num_placas = math.ceil(vol_total_L_requerido / vol_ajustado)
    area_total = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_total
    
    status = "✅ OK"
    obs = "-"
    
    # Validação de Volume: Polpa vs Torta
    # Se o volume da torta for quase igual ao da polpa, o ciclo é muito curto ou lodo muito denso
    if vol_total_L_requerido > vol_polpa_ciclo_L:
        status = "❌ Erro Dados"
        obs = "Vol. de Torta calculado maior que Vol. de Polpa alimentado."
    elif fluxo > 500:
        status = "⚠️ Fluxo Alto"
        obs = f"Fluxo de {fluxo:.0f} L/m²h acima do ideal."
    elif p["nom"] == 1500 and num_placas > 120:
        status = "⚠️ Dividir"
        obs = f"Limite de 120 placas. Sugerido dividir."
    
    res_list.append({
        "Modelo (mm)": f"{p['nom']} x {p['nom']}",
        "Placas": num_placas,
        "Área Total (m²)": f"{area_total:.2f}",
        "Taxa Fluxo (L/m²h)": f"{fluxo:.1f}",
        "Status": status,
        "Observação": obs
    })

st.table(res_list)
