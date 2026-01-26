import streamlit as st
import math
import os

# Configuração da página
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# --- LÓGICA DO LOGOTIPO (Via Link Direto para garantir exibição) ---
logo_url = "https://www.cleanova.com/wp-content/uploads/2023/10/Cleanova_Logo_Main_RGB.png"
col_logo, col_titulo = st.columns([1, 3])
with col_logo:
    st.image(logo_url, width=350)
with col_titulo:
    st.title("Dimensionador de Filtro Prensa")
st.sidebar.image(logo_url, use_container_width=True)

st.markdown("---")

# --- CABEÇALHO ---
c1, c2, c3 = st.columns(3)
with c1: cliente = st.text_input("👤 Nome do Cliente")
with c2: projeto = st.text_input("📂 Nome do Projeto")
with c3: produto = st.text_input("📦 Produto")

col_opp, col_resp, col_vazio = st.columns(3)
with col_opp: n_opp = st.text_input("🔢 Nº OPP")
with col_resp: responsavel = st.text_input("👨‍💻 Responsável")

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

dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_torta_m3 = (massa_seco_ciclo / (1 - umidade)) / dens_torta if (1-umidade) > 0 else 0
vol_total_L_req = vol_torta_m3 * 1000

# --- EXIBIÇÃO DE MÉTRICAS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Vol. Polpa p/ Ciclo", f"{vol_polpa_ciclo_L:,.0f} L")
col2.metric("Vol. Torta p/ Ciclo", f"{vol_total_L_req:,.0f} L")
col3.metric("Conc. Sólidos Calc.", f"{(solidos_dia/vol_polpa_dia)*100:.1f} %" if vol_polpa_dia > 0 else "0%")
col4.metric("Ciclos p/ Dia", f"{ciclos_dia:.1f}")

st.subheader("📋 Opções de Dimensionamento e Consultoria Técnica")

res_list = []
for i, p in enumerate(tamanhos):
    vol_ajustado = p["vol_ref"] * (recesso_manual / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    area_total = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_total if area_total > 0 else 0
    
    status = "✅ OK"
    obs = "-"
    
    # LÓGICA DE SUGESTÃO E ALERTAS
    if vol_total_L_req > vol_polpa_ciclo_L:
        status = "❌ Erro Dados"
        obs = "Volume de torta calculado > Volume de polpa alimentado."
    elif num_placas > p["max"]:
        status = "❌ Excedeu Placas"
        sugestao = None
        # Busca modelo maior que comporte o volume
        for j in range(i - 1, -1, -1): 
            p_maior = tamanhos[j]
            vol_aj_maior = p_maior["vol_ref"] * (recesso_manual / 30)
            placas_maior = math.ceil(vol_total_L_req / vol_aj_maior)
            if placas_maior <= p_maior["max"]:
                sugestao = f"Sugerido: {p_maior['nom']}x{p_maior['nom']} com {placas_maior} placas."
                break
        obs = f"Máx {p['max']} placas. {sugestao if sugestao else 'Dividir em 2 filtros.'}"
    elif fluxo > 500:
        status = "⚠️ Fluxo Alto"
        obs = f"Taxa de {fluxo:.0f} L/m²h acima do ideal."
    
    res_list.append({
        "Modelo (mm)": f"{p['nom']} x {p['nom']}",
        "Placas": num_placas,
        "Área Total (m²)": f"{area_total:.2f}",
        "Taxa Fluxo (L/m²h)": f"{fluxo:.1f}",
        "Status": status,
        "Observação": obs
    })

st.table(res_list)
