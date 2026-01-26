import streamlit as st
import math
import os
from fpdf import FPDF

# Configuração da página
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR PDF (O motor do relatório)
# ---------------------------------------------------------
def gerar_pdf_estudo(cliente, projeto, produto, res_unicos, res_multi):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Estudo Tecnico de Dimensionamento - Cleanova Micronics", ln=True, align="C")
    pdf.ln(10)
    
    # Informações Básicas
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, f"Cliente: {cliente}", ln=True)
    pdf.cell(190, 8, f"Projeto: {projeto}", ln=True)
    pdf.cell(190, 8, f"Produto: {produto}", ln=True)
    pdf.ln(10)
    
    # Tabela 1: Filtro Único
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 10, "Opcoes de Filtro Unico:", ln=True)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(50, 10, "Modelo", 1)
    pdf.cell(30, 10, "Placas", 1)
    pdf.cell(40, 10, "Area (m2)", 1)
    pdf.cell(40, 10, "Fluxo (L/m2h)", 1)
    pdf.cell(30, 10, "Status", 1, ln=True)
    
    pdf.set_font("Arial", "", 9)
    for r in res_unicos:
        pdf.cell(50, 10, r["Modelo (mm)"], 1)
        pdf.cell(30, 10, str(r["Placas"]), 1)
        pdf.cell(40, 10, r["Área Total (m²)"], 1)
        pdf.cell(40, 10, r["Fluxo (L/m²h)"], 1)
        pdf.cell(30, 10, r["Status"], 1, ln=True)
    
    pdf.ln(10)
    
    # Tabela 2: Filtros em Paralelo
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 10, "Alternativas em Paralelo (Redundancia):", ln=True)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(60, 10, "Configuracao", 1)
    pdf.cell(40, 10, "Placas/Filtro", 1)
    pdf.cell(50, 10, "Area Total (m2)", 1)
    pdf.cell(40, 10, "Status", 1, ln=True)
    
    pdf.set_font("Arial", "", 9)
    for m in res_multi:
        pdf.cell(60, 10, m["Configuração"], 1)
        pdf.cell(40, 10, str(m["Placas por Filtro"]), 1)
        pdf.cell(50, 10, m["Área Total Combinada (m²)"], 1)
        pdf.cell(40, 10, m["Status"], 1, ln=True)
        
    return pdf.output(dest="S").encode("latin-1")

# ---------------------------------------------------------
# LAYOUT E LÓGICA DO APP
# ---------------------------------------------------------
logo_path = "logo.png"
logo_url = "https://www.cleanova.com/wp-content/uploads/2023/10/Cleanova_Logo_Main_RGB.png"

if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
    col_l, col_t = st.columns([1, 3])
    with col_l: st.image(logo_path, width=350)
    with col_t: st.title("Dimensionador de Filtro Prensa")
else:
    st.sidebar.image(logo_url, use_container_width=True)
    col_l, col_t = st.columns([1, 3])
    with col_l: st.image(logo_url, width=350)
    with col_t: st.title("Dimensionador de Filtro Prensa")

st.markdown("---")

# --- CABEÇALHO ---
c1, c2, c3 = st.columns(3)
with c1: cliente = st.text_input("👤 Nome do Cliente")
with c2: projeto = st.text_input("📂 Nome do Projeto")
with c3: produto = st.text_input("📦 Produto")

# --- SIDEBAR: ENTRADA DE DADOS ---
st.sidebar.header("🚀 Capacidade e Operação")
solidos_dia = st.sidebar.number_input("Peso Total Sólidos Secos (ton/dia)", value=100.0)
horas_op = st.sidebar.number_input("Disponibilidade (Horas/dia)", value=20.0)
tempo_cycle = st.sidebar.number_input("Tempo de ciclo total (minutos)", value=60)

st.sidebar.header("💧 Fluxo de Polpa")
vol_polpa_dia = st.sidebar.number_input("Volume de Lodo/Polpa (m³/dia)", value=500.0)
vazao_lh = st.sidebar.number_input("Vazão de Alimentação (L/h)", value=50000.0)

st.sidebar.header("🧪 Propriedades Físicas")
sg_solidos = st.sidebar.number_input("Gravidade Específica", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Final Torta (%)", value=20.0)
recesso_manual = st.sidebar.number_input("Espessura de câmara (mm)", value=30.0)
umidade = umidade_input / 100

# --- BASE DE DADOS TÉCNICA ---
tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100},
]

# --- LÓGICA DE CÁLCULO ---
ciclos_dia = (horas_op * 60) / tempo_cycle if tempo_cycle > 0 else 0
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_total_L_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

# --- TABELA DE RESULTADOS (SOLUÇÃO ÚNICA) ---
st.subheader("📋 Opções de Dimensionamento (Filtro Único)")
res_list = []
for i, p in enumerate(tamanhos):
    vol_ajustado = p["vol_ref"] * (recesso_manual / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    area_total = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_total if area_total > 0 else 0
    
    res_list.append({
        "Modelo (mm)": f"{p['nom']} x {p['nom']}",
        "Placas": num_placas,
        "Área Total (m²)": f"{area_total:.2f}",
        "Fluxo (L/m²h)": f"{fluxo:.1f}",
        "Status": "✅ OK" if num_placas <= p["max"] else "❌ Excede Limite"
    })
st.table(res_list)

# --- QUADRO: ALTERNATIVAS MULTI-FILTRO ---
st.markdown("---")
st.subheader("🔄 Alternativas com Filtros em Paralelo (Redundância)")
st.info("Abaixo, calculamos a configuração necessária caso opte por dividir a carga em 2 equipamentos.")

multi_list = []
for nom_alvo in [2000, 1500]:
    p_ref = next(item for item in tamanhos if item["nom"] == nom_alvo)
    vol_aj_ref = p_ref["vol_ref"] * (recesso_manual / 30)
    placas_por_filtro = math.ceil((vol_total_L_req / 2) / vol_aj_ref)
    area_por_filtro = placas_por_filtro * p_ref["area_ref"]
    
    multi_list.append({
        "Configuração": f"2x Filtros {nom_alvo} x {nom_alvo}",
        "Placas por Filtro": placas_por_filtro,
        "Total de Placas": placas_por_filtro * 2,
        "Área Total Combinada (m²)": f"{area_por_filtro * 2:.2f}",
        "Status": "✅ Recomendado" if placas_por_filtro <= p_ref["max"] else "⚠️ Limite Alto"
    })
st.table(multi_list)

# ---------------------------------------------------------
# BOTÃO DE DOWNLOAD PDF
# ---------------------------------------------------------
st.markdown("---")
if st.button("📄 Gerar Relatório PDF"):
    pdf_output = gerar_pdf_estudo(cliente, projeto, produto, res_list, multi_list)
    st.download_button(
        label="📥 Baixar Estudo Técnico",
        data=pdf_output,
        file_name=f"Estudo_Cleanova_{cliente}.pdf",
        mime="application/pdf"
    )
