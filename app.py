import streamlit as st
import math
from fpdf import FPDF
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR PDF (VERSÃO COMPLETA)
# ---------------------------------------------------------
def gerar_pdf_estudo(cliente, projeto, produto, mercado, opp, resp, kpis, res_unicos):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "ESTUDO TECNICO DE DIMENSIONAMENTO", ln=True, align="C")
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "CLEANOVA MICRONICS", ln=True, align="C")
        pdf.ln(5)
        
        # Identificação do Projeto
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 7, f"Cliente: {cliente}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 7, f"Mercado: {mercado}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.cell(95, 7, f"Projeto: {projeto}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 7, f"N. OPP: {opp}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.cell(95, 7, f"Produto: {produto}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 7, f"Responsavel: {resp}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.ln(5)

        # KPIs Técnicos
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, "Indicadores Operacionais Requeridos:", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(95, 7, f"Peso Total de Torta: {kpis['peso_torta_dia']:.2f} ton/dia", 1)
        pdf.cell(95, 7, f"Disponibilidade: {kpis['disp_h']:.1f} h/dia ({kpis['disp_pct']}%)", 1, ln=True)
        pdf.ln(5)
        
        # Tabela de Resultados
        pdf.set_font("Arial", "B", 9)
        pdf.cell(40, 10, "Modelo", 1); pdf.cell(20, 10, "Placas", 1); pdf.cell(30, 10, "Area (m2)", 1); 
        pdf.cell(30, 10, "Fluxo (L/m2h)", 1); pdf.cell(45, 10, "Dry Solids Load (kg/m2/d)", 1); pdf.cell(25, 10, "Status", 1, ln=True)
        
        pdf.set_font("Arial", "", 8)
        for r in res_unicos:
            status_limpo = r["Status"].replace("✅", "").replace("❌", "").strip()
            pdf.cell(40, 10, r["Modelo (mm)"], 1)
            pdf.cell(20, 10, str(r["Placas"]), 1)
            pdf.cell(30, 10, r["Area"], 1)
            pdf.cell(30, 10, r["Fluxo"], 1)
            pdf.cell(45, 10, r["Dry Solids Load"], 1)
            pdf.cell(25, 10, status_limpo, 1, ln=True)
            
        # Assinaturas e Data
        pdf.ln(20)
        data_atual = datetime.now().strftime("%d/%m/%Y")
        pdf.set_font("Arial", "I", 8)
        pdf.cell(190, 5, f"Documento gerado em: {data_atual}", ln=True, align="R")
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 90, pdf.get_y())
        pdf.line(110, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(80, 5, "Elaborado (Responsavel)", 0, align="C")
        pdf.cell(20, 5, "", 0) 
        pdf.cell(80, 5, "Conferido (Validacao)", 0, ln=True, align="C")
        
        return pdf.output(dest="S").encode("latin-1", "ignore")
    except Exception as e:
        return f"Erro: {str(e)}"

# ---------------------------------------------------------
# INTERFACE PRINCIPAL
# ---------------------------------------------------------
st.title("Cleanova Micronics | Dimensionador de Filtro Prensa")
st.markdown("---")

# CABEÇALHO RESTAURADO
row1_col1, row1_col2, row1_col3 = st.columns(3)
with row1_col1: cliente = st.text_input("👤 Nome do Cliente")
with row1_col2: projeto = st.text_input("📂 Nome do Projeto")
with row1_col3: mercado = st.text_input("🏭 Mercado (Ex: Mineração)")

row2_col1, row2_col2, row2_col3 = st.columns(3)
with row2_col1: produto = st.text_input("📦 Produto")
with row2_col2: n_opp = st.text_input("🔢 Nº OPP")
with row2_col3: responsavel = st.text_input("👨‍💻 Responsável pelo Estudo")

st.markdown("---")

# SIDEBAR DADOS TÉCNICOS
st.sidebar.header("🚀 Capacidade e Operação")
solidos_dia = st.sidebar.number_input("Sólidos Secos (ton/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade Operacional (%)", 0, 100, 80)
tempo_cycle = st.sidebar.number_input("Tempo de Ciclo Total (min)", value=60)

st.sidebar.header("💧 Fluxo e Propriedades")
vazao_lh = st.sidebar.number_input("Vazão de Alimentação (L/h)", value=50000.0)
sg_solidos = st.sidebar.number_input("SG Sólidos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Final Torta (%)", value=20.0)
recesso = st.sidebar.number_input("Espessura de Câmara (mm)", value=30.0)

# ---------------------------------------------------------
# CÁ
