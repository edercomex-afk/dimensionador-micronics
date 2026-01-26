import streamlit as st
import math
import os

# Configuração da página
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# --- LÓGICA DO LOGOTIPO ---
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

# --- SIDEBAR: ENTRADA DE DADOS ---
st.sidebar.header("🚀 Capacidade e Operação")
solidos_dia = st.sidebar.number_input("Peso Total Sólidos Secos (ton/dia)", value=100.0)
vol_polpa_dia = st.sidebar.number_input("Volume de Lodo/Polpa (m³/dia)", value=500.0)
horas_op = st.sidebar.number_input("Disponibilidade (Horas/dia)", value=20.0)
tempo_cycle = st.sidebar.number_input("Tempo de ciclo total (minutos)", value=60)

st.sidebar.header("💧 Fluxo de Polpa")
vazao_lh = st.sidebar.number_input("Vazão de Alimentação (L/h)", value=50000.0)

st.sidebar.header("🧪 Propriedades Físicas")
sg_solidos = st.sidebar.number_input("Gravidade Específica (Sólidos)", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Final da Torta (%)", value=20.0)
umidade = umidade_input / 100
recesso_manual = st.sidebar.number_input("Espessura de câmara (mm)", value=30.0)

# --- BASE DE DADOS TÉCNICA (Ordenada do maior para o menor) ---
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
vol_total_L_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

# --- TABELA DE RESULTADOS ---
st.subheader("📋 Opções de Dimensionamento e Sugestões")

res_list = []
for i, p in enumerate(tamanhos):
    vol_ajustado = p["vol_ref"] * (recesso_manual / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    area_total = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_total if area_total > 0 else 0
    
    status = "✅ OK"
    obs = "-"
    
    # LÓGICA DE SUGESTÃO:
    if num_placas > p["max"]:
        status = "❌ Excedeu Limite"
        # Tenta encontrar o modelo maior que funciona
        sugestao = None
        for j in range(i - 1, -1, -1): # Olha para os modelos acima na lista
            p_maior = tamanhos[j]
            vol_aj_maior = p_maior["vol_ref"] * (recesso_manual / 30)
            placas_maior = math.ceil(vol_total_L_req / vol_aj_maior)
            if placas_maior <= p_maior["max"]:
                sugestao = f"Sugerido: Modelo {p_maior['nom']} com {placas_maior} placas."
                break
        
        if p["nom"] == 1500:
            obs = f"Limite 120 atingido. {sugestao if sugestao else 'Dividir em 2 filtros.'}"
        else:
            obs = f"Máx {p['max']} placas. {sugestao if sugestao else 'Usar modelo maior.'}"
            
    elif fluxo > 500:
        status = "⚠️ Fluxo Alto"
        obs = f"Taxa de {fluxo:.0f} L/m²h acima do recomendado."

    res_list.append({
        "Modelo (mm)": f"{p['nom']} x {p['nom']}",
        "Placas": num_placas,
        "Área Total (m²)": f"{area_total:.2f}",
        "Taxa Fluxo (L/m²h)": f"{fluxo:.1f}",
        "Status": status,
        "Observação": obs
    })

st.table(res_list)
