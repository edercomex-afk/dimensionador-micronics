import streamlit as st
import math

# Configuração da página
st.set_page_config(page_title="Dimensionamento Micronics V12", layout="wide")

st.title("🛠️ Dimensionador de Filtro Prensa - Micronics")

# --- CABEÇALHO DE IDENTIFICAÇÃO ---
col_c, col_p, col_pr = st.columns(3)
with col_c:
    cliente = st.text_input("👤 Nome do Cliente", placeholder="Ex: Arcor, Gerdau...")
with col_p:
    projeto = st.text_input("📂 Nome do Projeto", placeholder="Ex: Expansão Linha 02")
with col_pr:
    produto = st.text_input("📦 Produto a ser filtrado", placeholder="Ex: Concentrado de Zinco")

st.markdown("---")

# --- SIDEBAR: ENTRADA DE DADOS MANUAIS ---
st.sidebar.header("🚀 Capacidade e Operação")
solidos_dia = st.sidebar.number_input("Peso Total de Sólidos Secos (ton/dia)", value=100.0, step=1.0)
horas_op = st.sidebar.number_input("Disponibilidade (Horas/dia)", min_value=0.1, max_value=24.0, value=20.0, step=0.5)
tempo_cycle = st.sidebar.number_input("Tempo de ciclo total (minutos)", value=60, step=1)

st.sidebar.header("🧪 Propriedades Físicas")
sg_solidos = st.sidebar.number_input("Gravidade Específica (Sólidos)", value=2.8, step=0.1)
umidade_input = st.sidebar.number_input("Umidade Final da Torta (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.5)
umidade = umidade_input / 100

st.sidebar.header("📝 Detalhes Técnicos")
temp_processo = st.sidebar.number_input("Temperatura de Processo (°C)", value=25, step=1)
ph_solucao = st.sidebar.number_input("pH da Solução", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
lavador_lonas = st.sidebar.selectbox("Lavador de Lonas?", ["Sim", "Não"])
aut_nivel = st.sidebar.selectbox("Nível de Automatização", ["Baixo", "Médio", "Alto"])
lavador_torta = st.sidebar.selectbox("Lavador de Torta?", ["Sim", "Não"])
membrana = st.sidebar.selectbox("Membrana de Compressão?", ["Sim", "Não"])

st.sidebar.header("📐 Geometria da Placa")
recesso_manual = st.sidebar.number_input("Espessura de câmara (mm)", min_value=1.0, max_value=100.0, value=30.0, step=1.0)

# --- BASE DE DADOS TÉCNICA ---
tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190, "forn": "Dewatering, Jing Jin, Bright"},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160, "forn": "Micronics, Dewatering, Jing Jin, Bright"},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120, "forn": "Micronics, Dewatering, Jing Jin, Bright, Fugie"},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100, "forn": "Micronics, Dewatering, Jing Jin, Bright, Fugie"},
    {"nom": 1000, "area_ref": 1.80, "vol_ref": 25,  "max": 100, "forn": "Micronics, Dewatering, Jing Jin, Bright, Fugie"},
    {"nom": 800,  "area_ref": 1.10, "vol_ref": 15,  "max": 84,  "forn": "Micronics, Dewatering, Jing Jin, Bright, Fugie"},
    {"nom": 630,  "area_ref": 0.65, "vol_ref": 9,   "max": 74,  "forn": "Micronics, Dewatering, Jing Jin, Bright, Fugie"},
    {"nom": 400,  "area_ref": 0.25, "vol_ref": 3,   "max": 74,  "forn": "Micronics, Dewatering, Jing Jin, Bright, Fugie"},
]

# --- LÓGICA DE CÁLCULO ---
ciclos_dia = (horas_op * 60) / tempo_cycle if tempo_cycle > 0 else 0
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_torta_m3 = (massa_seco_ciclo / (1 - umidade)) / dens_torta if (1-umidade) > 0 else 0
vol_total_L = vol_torta_m3 * 1000

# --- EXIBIÇÃO ---
st.subheader(f"Resumo Técnico: {produto if produto else 'Geral'}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Massa Seca Total", f"{solidos_dia:.1f} t/dia")
col2.metric("Massa p/ Ciclo", f"{massa_seco_ciclo:.2f} t")
col3.metric("Vol. Torta p/ Ciclo", f"{vol_total_L:.0f} L")
col4.metric("Ciclos p/ Dia", f"{ciclos_dia:.1f}")

with st.expander("📋 Ver Detalhes do Projeto e Opcionais"):
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Cliente:** {cliente if cliente else '-'}")
    c1.write(f"**Projeto:** {projeto if projeto else '-'}")
    c2.write(f"**Temp:** {temp_processo} °C | **pH:** {ph_solucao}")
    c2.write(f"**Lavador Lonas:** {lavador_lonas}")
    c3.write(f"**Automação:** {aut_nivel} | **Lavador Torta:** {lavador_torta}")
    c3.write(f"**Membrana:** {membrana}")

st.subheader("📋 Opções de Dimension
