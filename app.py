import streamlit as st
import math

# Configuração da página
st.set_page_config(page_title="Dimensionamento Micronics V5", layout="wide")

st.title("🛠️ Dimensionador de Filtro Prensa - Micronics")
st.markdown("---")

# --- SIDEBAR: ENTRADA DE DADOS ---
st.sidebar.header("📊 Disponibilidade e Operação")
horas_op = st.sidebar.slider("Horas de operação por dia", 1, 24, 20)
tempo_ciclo = st.sidebar.number_input("Tempo de ciclo total (minutos)", value=60)
solidos_dia = st.sidebar.number_input("Peso total de sólidos (ton/dia)", value=100.0)

st.sidebar.header("🧪 Propriedades Físicas")
densidade_polpa = st.sidebar.number_input("Densidade da Polpa (g/cm³)", value=1.5, step=0.01, format="%.2f")
sg_solidos = st.sidebar.number_input("Gravidade Específica (Sólidos)", value=2.8)
umidade = st.sidebar.slider("Umidade da torta (%)", 15, 25, 20) / 100

st.sidebar.header("📐 Geometria da Placa")
recesso_manual = st.sidebar.number_input("Espessura de câmara desejada (mm)", min_value=1, max_value=100, value=30)

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
ciclos_dia = (horas_op * 60) / tempo_ciclo
massa_seco_ciclo = solidos_dia / ciclos_dia
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0))
vol_torta_m3 = (massa_seco_ciclo / (1 - umidade)) / dens_torta
vol_total_L = vol_torta_m3 * 1000

# --- EXIBIÇÃO ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Vol. Torta Requerido", f"{vol_total_L:.0f} L")
col2.metric("Ciclos por Dia", f"{ciclos_dia:.1f}")
col3.metric("Massa Seca/Ciclo", f"{massa_seco_ciclo:.2f} t")
col4.metric("Densidade Polpa", f"{densidade_polpa} g/cm³")

st.subheader("📋 Opções de Dimensionamento com Área Total")

res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso_manual / 30)
    num_placas = math.ceil(vol_total_L / vol_ajustado)
    
    # CÁLCULO DA ÁREA FILTRANTE TOTAL
    area_total = num_placas * p["area_ref"]
    
    status = "✅ OK"
    obs = "-"
    
    if p["nom"] == 1500 and num_placas > 120:
        status = "⚠️ Dividir"
        obs = f"Sugerido 2 filtros de {math.ceil(num_placas/2)} placas"
    elif num_placas > p["max"]:
        status = "❌ Excede Limite"
        obs = f"Máximo: {p['max']} placas"
    
    res_list.append({
        "Modelo (mm)": f"{p['nom']} x {p['nom']}",
        "Placas Necessárias": num_placas,
        "Área Total (m²)": f"{area_total:.2f}",
        "Vol. Câmara (L)": f"{vol_ajustado:.1f}",
        "Status": status,
        "Observação": obs
    })

st.table(res_list)
st.info("A Área Total (m²) é calculada multiplicando a área unitária da placa pelo número de placas propostas.")
