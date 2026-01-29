import streamlit as st
import math
from fpdf import FPDF
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR PDF (8 MODELOS)
# ---------------------------------------------------------
def gerar_pdf_estudo(cliente, projeto, produto, mercado, opp, resp, dados_tec, res_unicos, kpis):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "ESTUDO TECNICO DE DIMENSIONAMENTO", ln=True, align="C")
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "CLEANOVA MICRONICS", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 7, f"Cliente: {cliente}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 7, f"Mercado: {mercado}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.cell(95, 7, f"Projeto: {projeto}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 7, f"N. OPP: {opp}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.cell(190, 7, f"Responsavel: {resp}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, "Especificacoes de Processo e Automacao:", ln=True)
        pdf.set_font("Arial", "", 9)
        info_txt = (f"Produto: {produto} | Temp: {dados_tec['temp']}C | pH: {dados_tec['ph']} | "
                    f"Lavagem Lona: {dados_tec['lav_l']} | Lavagem Torta: {dados_tec['lav_t']} | "
                    f"Membrana: {dados_tec['mem']} | Automacao: {dados_tec['auto']}")
        pdf.multi_cell(190, 7, info_txt.encode('latin-1', 'ignore').decode('latin-1'), border=1)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, "Indicadores de Performance Requeridos:", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(95, 7, f"Peso Total de Torta: {kpis['peso_torta_dia']:.2f} t/dia", 1)
        pdf.cell(95, 7, f"Volume Lodo Diario: {kpis['vol_lodo_dia']:.2f} m3/dia", 1, ln=True)
        pdf.cell(95, 7, f"Disponibilidade: {kpis['disp_pct']}% ({kpis['disp_h']:.1f} h/dia)", 1)
        pdf.cell(95, 7, f"Conc. Solidos: {kpis['conc_sol']:.2f} %", 1, ln=True)
        pdf.ln(8)
        
        # Ajuste de fonte para caber 8 linhas
        pdf.set_font("Arial", "B", 8)
        pdf.cell(35, 10, "Modelo", 1); pdf.cell(15, 10, "Placas", 1); pdf.cell(25, 10, "Area (
