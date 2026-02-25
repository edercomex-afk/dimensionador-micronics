import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
from fpdf import FPDF

# 1. Configuração de Página
st.set_page_config(page_title="Dimensionador Micronics V53.2", layout="wide")

# Função para Gerar PDF
def create_pdf(empresa, projeto, opp, responsavel, cidade, estado, resultados_df, vol_dia, fluxo_h, pico, sg):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "CLEANOVA MICRONICS - MEMORIAL DE CALCULO", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(190, 10, f"Empresa: {empresa}", ln=True)
    pdf.cell(190, 10, f"Projeto: {projeto} | OPP: {opp}", ln=True)
    pdf.cell(190, 10, f"Responsavel: {responsavel}", ln=True)
    pdf.cell(190, 10, f"Localidade: {cidade}/{estado}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "RESUMO OPERACIONAL", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"- Volume de Lodo/Dia: {vol_dia:.2f} m3/dia", ln=True)
    pdf.cell(190, 8, f"- Taxa de Fluxo: {fluxo_h:.2f} m3/h", ln=True)
    pdf.cell(190, 8, f"- Vazao de Pico: {pico:,.0f} L/h", ln=True)
    pdf.cell(190, 8, f"- Grav. Especifica: {sg:.3f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "TABELA DE SELECAO", ln=True)
    pdf.set_font("Arial", "", 10)
    for index, row in resultados_df.iterrows():
        pdf.cell(190, 8, f"{row['Equipamento']} | Placas: {row['Qtd Placas']} | Area: {row['Área Total (m2)']} m2 | Taxa: {row['Taxa (kg/m2.h)']}", ln=True)
    return pdf.output(dest="S").encode("latin-1", errors="replace")

def main():
    # Cabeçalho Técnico (Banner Azul)
    st.markdown("""
    <div style="background-color:#003366;padding:20px;border-radius:10px;margin-bottom:20px">
    <h1 style="color:white;text-align:center;margin:0;">CLEANOVA MICRONICS - DIMENSIONADOR V53</h1>
    <p style="color:white;text-align:center;margin:5px;">Memorial de Cálculo de Engenharia | Responsável: Eder</p>
    </div>
    """, unsafe_allow_html=True)

    estados_br = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
                  "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
    mercados = ["Mineração", "Químico", "Farmacêutico", "Cervejaria", "Sucos", "Fertilizantes", "Outros"]
    
    # Lista de produtos conforme solicitado
    produtos = ["Concentrado", "Rejeito", "Minério de Ferro", "Lodo Biológico", "Outros"]

    # --- SIDEBAR: IDENTIFICAÇÃO ---
    st.sidebar.header("📋 Identificação do Projeto")
    empresa = st.sidebar.text_input("Empresa", value="")
    nome_projeto = st.sidebar.text_input("Nome do Projeto", value="")
    num_opp = st.sidebar.text_input("N° de OPP", value="")
    mercado_sel = st.sidebar.selectbox("Mercado", mercados)
    
    # Box de seleção de Produto (Editável/Sem automação de cálculos)
    produto_sel = st.sidebar.selectbox("Produto", produtos)
    
    responsavel_proj = st.sidebar.text_input("Responsável", value="Eder")
    
    col_cid, col_est = st.sidebar.columns(2)
    cidade = col_cid.text_input("Cidade", value="")
    estado = col_est.selectbox("Estado", estados_br, index=24)

    st.sidebar.divider()
    
    # --- SIDEBAR: PARÂMETROS DE PROCESSO ---
    st.sidebar.header("📥 Parâmetros de Processo")
    prod_seca_hora = st.sidebar.number_input("Massa Seca (t/h)", value=0.0)
    
    # Box para inserir volume de lodo por hora
    vol_lodo_hora_input = st.sidebar.number_input("Volume de lodo/hora (m³/h)", value=0.0)
    
    disponibilidade_h = st.sidebar.slider("Disponibilidade (h/dia)", 1, 24, 20)
    conc_solidos = st.sidebar.number_input("Conc. Sólidos (%w/w)", value=0.0)
    
    st.sidebar.divider()
    st.sidebar.header("🧬 Densidade e Geometria")
    sg_solido = st.sidebar.number_input("Gravidade específica dos Sólidos Secos (g/cm³)", value=2.70, format="%.2f")
    espessura_camara = st.sidebar.number_input("Espessura da Câmara (mm)", value=40, step=1)
    
    st.sidebar.divider()
    st.sidebar.header("🔄 Ciclos e Operação")
    tempo_ciclo_min = st.sidebar.number_input("Tempo de Ciclo (min)", value=60)
    pressao_operacao = st.sidebar.slider("Pressão de Filtração (Bar)", 1, 15, 6)

    # --- NÚCLEO DE CÁLCULO ---
    try:
        sg_lodo = 100 / ((conc_solidos / sg_solido) + (100 - conc_solidos)) if conc_solidos > 0 else 1.0
        
        # Prioriza o volume manual se preenchido
        if vol_lodo_hora_input > 0:
            taxa_fluxo_lodo_m3h = vol_lodo_hora_input
        else:
            massa_polpa_hora = prod_seca_hora / (conc_solidos / 100) if conc_solidos > 0 else 0
            taxa_fluxo_lodo_m3h = massa_polpa_hora / sg_lodo if sg_lodo > 0 else 0
            
        vol_lodo_dia_calc = taxa_fluxo_lodo_m3h * disponibilidade_h
        vazao_pico_lh = (taxa_fluxo_lodo_m3h * 1000) * 1.3
    except:
        sg_lodo = 1.0
        taxa_fluxo_lodo_m3h = vol_lodo_dia_calc = vazao_pico_lh = 0.0

    # --- EXIBIÇÃO PRINCIPAL ---
    st.write(f"### 🚀 Estudo Técnico: {produto_sel} - {empresa if empresa else '---'}")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.info(f"**Produto**\n\n {produto_sel}")
    with c2: st.info(f"**Fluxo de Lodo**\n\n {taxa_fluxo_lodo_m3h:.2f} m³/h")
    with c3: st.info(f"**Vazão Pico**\n\n {vazao_pico_lh:,.0f} L/h")
    with c4: st.info(f"**SG Lodo**\n\n {sg_lodo:.3f}")

    st.divider()

    # Tabela de dimensionamento simplificada
    vol_torta_ciclo_m3 = (taxa_fluxo_lodo_m3h * (tempo_ciclo_min/60)) * (conc_solidos/100) * (sg_lodo/1.8) if taxa_fluxo_lodo_m3h > 0 else 0
    mapa_filtros = [
        {"Modelo": "1000mm", "Vol_Placa": 25, "Area_Placa": 1.8},
        {"Modelo": "1200mm", "Vol_Placa": 45, "Area_Placa": 2.6},
        {"Modelo": "1500mm", "Vol_Placa": 80, "Area_Placa": 4.1},
        {"Modelo": "2000mm", "Vol_Placa": 150, "Area_Placa": 7.5},
    ]

    selecao_final = []
    for f in mapa_filtros:
        num_placas = math.ceil((vol_torta_ciclo_m3 * 1000) / f["Vol_Placa"]) if vol_torta_ciclo_m3 > 0 else 0
        area_total = num_placas * f["Area_Placa"]
        selecao_final.append({
            "Equipamento": f["Modelo"], 
            "Qtd Placas": int(num_placas), 
            "Área Total (m2)": round(area_total, 2), 
            "Taxa (kg/m2.h)": 0.0
        })

    st.write("### Seleção de Ativos")
    st.table(pd.DataFrame(selecao_final))

if __name__ == "__main__":
    main()
