import streamlit as st
import math
import os
from fpdf import FPDF

# 1. Configuração da página (Deve ser a primeira linha Streamlit)
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR PDF (CORRIGIDA PARA CARACTERES ESPECIAIS)
# ---------------------------------------------------------
def gerar_pdf_estudo(cliente, projeto, produto, mercado, opp, resp, res_unicos, res_multi):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Título do Relatório
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "Estudo Tecnico de Dimensionamento - Cleanova Micronics", ln=True, align="C")
        pdf.ln(10)
        
        # Informações do Projeto (Limpando caracteres incompatíveis com latin-1)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(95, 8, f"Cliente: {cliente}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 8, f"Mercado: {mercado}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.cell(95, 8, f"Projeto: {projeto}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 8, f"Produto: {produto}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.cell(95, 8, f"Nº OPP: {opp}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 8, f"Responsavel: {resp}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
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
            # Remove emojis para evitar erro no PDF
            status_limpo = r["Status"].replace("✅", "").replace("❌", "").replace("⚠️", "").strip()
            
            pdf.cell(50, 10, r["Modelo (mm)"], 1)
            pdf.cell(30, 10, str(r["Placas"]), 1)
            pdf.cell(40, 10, r["Área Total (m²)"], 1)
            pdf.cell(40, 10, r["Fluxo (L/m²h)"], 1)
            pdf.cell(30, 10, status_limpo, 1, ln=True)
            
        return pdf.output(dest="S").encode("latin-1", "ignore")
    except Exception as e:
        return f"Erro: {str(e)}"

# ---------------------------------------------------------
# LOGOTIPO E TÍTULO
# ---------------------------------------------------------
logo_url = "https://www.cleanova.com/wp-content/uploads/2023/10/Cleanova_Logo_Main_RGB.png"
col_l, col_t = st.columns([1, 3])
with col_l: 
    st.image(logo_url, width=300)
with col_t: 
    st.title("Dimensionador de Filtro Prensa")

st.sidebar.image(logo_url, use_container_width=True)
st.markdown("---")

# ---------------------------------------------------------
# CABEÇALHO DE IDENTIFICAÇÃO
# ---------------------------------------------------------
row1_c1, row1_c2, row1_c3 = st.columns(3)
with row1_c1: cliente = st.text_input("👤 Nome do Cliente")
with row1_c2: projeto = st.text_input("📂 Nome do Projeto")
with row1_c3: mercado = st.text_input("🏭 Mercado (Ex: Mineracao)")

row2_c1, row2_c2, row2_c3 = st.columns(3)
with row2_c1: produto = st.text_input("📦 Produto")
with row2_c2: n_opp = st.text_input("🔢 Nº OPP")
with row2_c3: responsavel = st.text_input("👨‍💻 Responsavel")

st.markdown("---")

# ---------------------------------------------------------
# SIDEBAR: DADOS TÉCNICOS
# ---------------------------------------------------------
st.sidebar.header("🚀 Capacidade e Operacao")
solidos_dia = st.sidebar.number_input("Peso Solidos Secos (ton/dia)", value=100.0)
horas_op = st.sidebar.number_input("Disponibilidade (Horas/dia)", value=20.0)
tempo_cycle = st.sidebar.number_input("Tempo de ciclo total (minutos)", value=60)

st.sidebar.header("💧 Fluxo de Polpa")
vol_polpa_dia = st.sidebar.number_input("Volume Lodo/Polpa (m³/dia)", value=500.0)
vazao_lh = st.sidebar.number_input("Vazao de Alimentacao (L/h)", value=50000.0)
