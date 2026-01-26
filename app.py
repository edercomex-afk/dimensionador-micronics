import streamlit as st
import math

# Configuração da página
st.set_page_config(page_title="Dimensionamento Micronics V7", layout="wide")

st.title("🛠️ Dimensionador de Filtro Prensa - Micronics")
st.markdown("---")

# --- SIDEBAR: ENTRADA DE DADOS ---
st.sidebar.header("🚀 Entrada Principal")
# Informação fundamental no topo
solidos_dia = st.sidebar.number_input("Peso Total de Sólidos Secos (ton/dia)", value=100.0, step=1.0)

st.sidebar.header("📊 Disponibilidade e Operação")
horas_op = st.sidebar.slider("Disponibilidade (Horas de operação/dia)", 1, 24, 20)
tempo_ciclo = st.sidebar.number_input("Tempo de ciclo total (minutos)", value=60)

st.sidebar.header("🧪 Propriedades Físicas")
densidade_polpa = st.sidebar.number_input("Densidade da Polpa (g/cm³)", value=1.5, step=0.01)
sg_solidos = st.sidebar.number_input("Gravidade Específica (Sólidos Secos)", value=2.8)
umidade = st.sidebar.slider("Umidade Final da Torta (%)", 15, 25, 20) / 100

st.sidebar.header("📝 Informações Adicionais (Opcionais)")
temp_processo = st.sidebar.number_input("Temperatura de Processo (°C)", value=25)
ph_solucao = st.sidebar.number_input("pH da Solução", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
lavador_lonas = st.sidebar.selectbox("Lavador de Lonas?", ["Sim", "Não"])
aut_nivel = st.sidebar.selectbox("Nível de Automatização", ["Baixo", "Médio", "Alto"])
lavador_torta = st.sidebar.selectbox("Lavador de Torta?", ["Sim", "Não"])
membrana = st.sidebar.selectbox("Membrana de Compressão?", ["Sim", "Não"])

st.sidebar.header("📐 Geometria da Placa")
recesso_manual = st.sidebar.number_input("Espessura de câmara (mm)", min_value=1, max_value=100, value=30)

# --- BASE DE DADOS TÉCNICA (Micronics) ---
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
# 1. Ciclos disponíveis por dia
ciclos_dia = (horas_op * 60) / tempo_ciclo

# 2. Massa que o filtro deve processar em cada ciclo (Ton seco)
massa_seco_ciclo = solidos_dia / ciclos_dia

# 3. Densidade da torta úmida (Sólido + Água nos poros)
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0))

# 4. Volume total de torta por ciclo em Litros
# Volume = Massa Total Úmida / Densidade da Torta
vol_torta_m3 = (massa_seco_ciclo / (1 - umidade)) / dens_torta
vol_total_L = vol_torta_m3 * 1000

# --- EXIBIÇÃO ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Massa Seca Total", f"{solidos_dia:.1f} t/dia")
col2.metric("Massa p/ Ciclo", f"{massa_seco_ciclo:.2f} t")
col3.metric("Vol. Torta p/ Ciclo", f"{vol_total_L:.0f} L")
col4.metric("Ciclos p/ Dia", f"{ciclos_dia:.1f}")

# Detalhes Adicionais
with st.expander("📋 Ver Detalhes Adicionais e Opcionais"):
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Temp:** {temp_processo} °C | **pH:** {ph_solucao}")
    c1.write(f"**Dens. Polpa:** {densidade_polpa} g/cm³")
    c2.write(f"**Lavador Lonas:** {lavador_lonas}")
    c2.write(f"**Lavador Torta:** {lavador_torta}")
    c3.write(f"**Automação:** {aut_nivel}")
    c3.write(f"**Membrana:** {membrana}")

st.subheader("📋 Opções de Dimensionamento Sugeridas")

res_list = []
for p in tamanhos:
    # Ajuste do volume baseado no recesso (Ref: 30mm)
    vol_ajustado = p["vol_ref"] * (recesso_manual / 30)
    num_placas = math.ceil(vol_total_L / vol_ajustado)
    area_total = num_placas * p["area_ref"]
    
    status = "✅ Disponível"
    obs = "-"
    if p["nom"] == 1500 and num_placas > 120:
        status = "⚠️ Dividir"
        obs = f"Sugerido 2 filtros de {math.ceil(num_placas/2)} placas"
    elif num_placas > p["max"]:
        status = "❌ Excede Limite"
        obs = f"Limite Máx: {p['max']} placas"
    
    res_list.append({
        "Modelo (mm)": f"{p['nom']} x {p['nom']}",
        "Placas Necessárias": num_placas,
        "Área Total (m²)": f"{area_total:.2f}",
        "Vol. Câmara (L)": f"{vol_ajustado:.1f}",
        "Status": status,
        "Observação": obs
    })

st.table(res_list)
