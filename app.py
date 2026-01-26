import streamlit as st
import math
import os
from fpdf import FPDF
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR PDF (VERSÃO COM ASSINATURAS E RESPONSÁVEL)
# ---------------------------------------------------------
def gerar_pdf_estudo(cliente, projeto, produto, mercado, opp, resp, dados_tec, res_unicos):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho do Relatório
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "Estudo Tecnico de Dimensionamento - Cleanova Micronics", ln=True, align="C")
        pdf.ln(5)
        
        # Dados de Identificação
        pdf.set_font("Arial", "B", 10)
        # Limpeza de caracteres incompatíveis com latin-1
        pdf.cell(95, 7, f"Cliente: {cliente}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 7, f"Mercado: {mercado}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.cell(95, 7, f"Projeto: {projeto}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 7, f"N. OPP: {opp}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        # Campo Responsável Corrigido
        pdf.cell(190, 7, f"Responsavel pelo Projeto: {resp}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.ln(5)

        # Dados Informativos (Temp, pH, etc)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, "Especificacoes de Processo:", ln=True)
        pdf.set_font("Arial", "", 9)
        info_txt = f"Produto: {produto} | Temp: {dados_tec['temp']}C | pH: {dados_tec['ph']} | Lavagem Lona: {dados_tec['lav_l']} | Lavagem Torta: {dados_tec['lav_t']} | Membrana: {dados_tec['mem']}"
        pdf.multi_cell(190, 7, info_txt.encode('latin-1', 'ignore').decode('latin-1'), border=1)
        pdf.ln(8)
        
        # Tabela de Resultados
        pdf.set_font("Arial", "B", 10)
        pdf.cell(50, 10, "Modelo", 1)
        pdf.cell(30, 10, "Placas", 1)
        pdf.cell(40, 10, "Area (m2)", 1)
        pdf.cell(40, 10, "Fluxo (L/m2h)", 1)
        pdf.cell(30, 10, "Status", 1, ln=True)
        
        pdf.set_font("Arial", "", 9)
        for r in res_unicos:
            status_limpo = r["Status"].replace("✅", "").replace("❌", "").replace("⚠️", "").strip()
            pdf.cell(50, 10, r["Modelo (mm)"], 1)
            pdf.cell(30, 10, str(r["Placas"]), 1)
            pdf.cell(40, 10, r["Área Total (m²)"], 1)
            pdf.cell(40, 10, r["Fluxo (L/m²h)"], 1)
            pdf.cell(30, 10, status_limpo, 1, ln=True)
            
        # --- SEÇÃO DE VALIDAÇÃO E ASSINATURAS ---
        pdf.ln(20)
        data_atual = datetime.now().strftime("%d/%m/%Y")
        pdf.set_font("Arial", "I", 9)
        pdf.cell(190, 10, f"Documento gerado em: {data_atual}", ln=True, align="R")
        pdf.ln(10)
        
        # Linhas de Assinatura
        y_atual = pdf.get_y()
        pdf.line(10, y_atual, 90, y_atual)      # Linha 1
        pdf.line(110, y_atual, 190, y_atual)    # Linha 2
        
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(80, 5, "Elaborado (Responsavel)", 0, align="C")
        pdf.cell(20, 5, "", 0) # Espaço
        pdf.cell(80, 5, "Conferido (Validacao)", 0, ln=True, align="C")
        
        pdf.set_font("Arial", "", 8)
        pdf.cell(80, 5, f"{resp}".encode('latin-1', 'ignore').decode('latin-1'), 0, align="C")
        
        return pdf.output(dest="S").encode("latin-1", "ignore")
    except Exception as e:
        return f"Erro ao gerar PDF: {str(e)}"

# ---------------------------------------------------------
# LAYOUT PRINCIPAL (STREAMLIT)
# ---------------------------------------------------------
logo_url = "https://www.cleanova.com/wp-content/uploads/2023/10/Cleanova_Logo_Main_RGB.png"
col_l, col_t = st.columns([1, 3])
with col_l: st.image(logo_url, width=280)
with col_t: st.title("Dimensionador de Filtro Prensa")

st.sidebar.image(logo_url, use_container_width=True)
st.markdown("---")

# IDENTIFICAÇÃO
r1_c1, r1_c2, r1_c3 = st.columns(3)
with r1_c1: cliente = st.text_input("👤 Nome do Cliente")
with r1_c2: projeto = st.text_input("📂 Nome do Projeto")
with r1_c3: mercado = st.text_input("🏭 Mercado")

r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1: produto = st.text_input("📦 Produto")
with r2_c2: n_opp = st.text_input("🔢 Nº OPP")
with r2_c3: responsavel = st.text_input("👨‍💻 Responsável pelo Projeto")

st.markdown("---")

# SIDEBAR DADOS
st.sidebar.header("🚀 Capacidade")
solidos_dia = st.sidebar.number_input("Peso Seco (ton/dia)", value=100.0)
horas_op = st.sidebar.number_input("Horas/dia", value=20.0)
tempo_cycle = st.sidebar.number_input("Ciclo (min)", value=60)

st.sidebar.header("📝 Dados de Processo")
temp_processo = st.sidebar.number_input("Temperatura (°C)", value=25)
ph_solucao = st.sidebar.number_input("pH", value=7.0)
lav_lona = st.sidebar.selectbox("Lavagem de Lona?", ["Sim", "Não"])
lav_torta = st.sidebar.selectbox("Lavagem de Torta?", ["Sim", "Não"])
membrana = st.sidebar.selectbox("Membrana?", ["Sim", "Não"])

st.sidebar.header("🧪 Propriedades Técnicas")
vazao_lh = st.sidebar.number_input("Vazão de Alimentação (L/h)", value=50000.0)
sg_solidos = st.sidebar.number_input("SG Sólidos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Torta (%)", value=20.0)
recesso = st.sidebar.number_input("Espessura câmara (mm)", value=30.0)

# CÁLCULOS
umidade = umidade_input / 100
ciclos_dia = (horas_op * 60) / tempo_cycle if tempo_cycle > 0 else 0
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_total_L_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100},
]

# RESULTADOS
st.subheader("📋 Resultados do Dimensionamento")
res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    area_t = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_t if area_t > 0 else 0
    res_list.append({
        "Modelo (mm)": f"{p['nom']} x {p['nom']}",
        "Placas": num_placas,
        "Área Total (m²)": f"{area_t:.2f}",
        "Fluxo (L/m²h)": f"{fluxo:.1f}",
        "Status": "✅ OK" if num_placas <= p["max"] else "❌ Limite"
    })
st.table(res_list)

# BOTÃO PDF
st.markdown("---")
if cliente and n_opp and responsavel:
    dados_tec = {
        "temp": temp_processo, "ph": ph_solucao, 
        "lav_l": lav_lona, "lav_t": lav_torta, "mem": membrana
    }
    pdf_bytes = gerar_pdf_estudo(cliente, projeto, produto, mercado, n_opp, responsavel, dados_tec, res_list)
    
    if isinstance(pdf_bytes, bytes):
        st.download_button(label="📄 Gerar Relatório PDF Final", data=pdf_bytes, 
                           file_name=f"Estudo_Tecnico_{cliente}_{n_opp}.pdf", mime="application/pdf")
else:
    st.info("💡 Preencha o Cliente, Nº OPP e Responsável para gerar o documento.")
