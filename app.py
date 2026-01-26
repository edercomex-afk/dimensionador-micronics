import streamlit as st
import math
import os
from fpdf import FPDF

# 1. Configuração da página (DEVE ser a primeira linha de comando Streamlit)
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR PDF
# ---------------------------------------------------------
import streamlit as st
import math
import os
from fpdf import FPDF

# 1. Configuração da página
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR PDF (VERSÃO CORRIGIDA - SEM EMOJIS)
# ---------------------------------------------------------
def gerar_pdf_estudo(cliente, projeto, produto, mercado, opp, resp, res_unicos, res_multi):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Título
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "Estudo Tecnico de Dimensionamento - Cleanova Micronics", ln=True, align="C")
        pdf.ln(10)
        
        # Informações do Projeto (Limpando acentos incompatíveis)
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
            # LIMPEZA DE EMOJIS PARA O PDF
            status_limpo = r["Status"].replace("✅", "").replace("❌", "").replace("⚠️", "").strip()
            
            pdf.cell(50, 10, r["Modelo (mm)"], 1)
            pdf.cell(30, 10, str(r["Placas"]), 1)
            pdf.cell(40, 10, r["Área Total (m²)"], 1)
            pdf.cell(40, 10, r["Fluxo (L/m²h)"], 1)
            pdf.cell(30, 10, status_limpo, 1, ln=True)
        
        return pdf.output(dest="S").encode("latin-1", "ignore")
    except Exception as e:
        return str(e)

# ---------------------------------------------------------
# LAYOUT E LÓGICA DO APLICATIVO (O restante do código)
# ---------------------------------------------------------
logo_url = "https://www.cleanova.com/wp-content/uploads/2023/10/Cleanova_Logo_Main_RGB.png"
col_l, col_t = st.columns([1, 3])
with col_l: st.image(logo_url, width=300)
with col_t: st.title("Dimensionador de Filtro Prensa")

st.sidebar.image(logo_url, use_container_width=True)
st.markdown("---")

# CABEÇALHO
r1_c1, r1_c2, r1_c3 = st.columns(3)
with r1_c1: cliente = st.text_input("👤 Nome do Cliente")
with r1_c2: projeto = st.text_input("📂 Nome do Projeto")
with r1_c3: mercado = st.text_input("🏭 Mercado (Ex: Mineração)")

r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1: produto = st.text_input("📦 Produto")
with r2_c2: n_opp = st.text_input("🔢 Nº OPP")
with r2_c3: responsavel = st.text_input("👨‍💻 Responsável")

st.markdown("---")

# SIDEBAR DADOS TÉCNICOS
st.sidebar.header("🚀 Operação")
solidos_dia = st.sidebar.number_input("Peso Sólidos Secos (ton/dia)", value=100.0)
horas_op = st.sidebar.number_input("Disponibilidade (Horas/dia)", value=20.0)
tempo_cycle = st.sidebar.number_input("Ciclo total (minutos)", value=60)

st.sidebar.header("💧 Fluxo")
vol_polpa_dia = st.sidebar.number_input("Volume Lodo (m³/dia)", value=500.0)
vazao_lh = st.sidebar.number_input("Vazão Alimentação (L/h)", value=50000.0)

st.sidebar.header("🧪 Propriedades")
sg_solidos = st.sidebar.number_input("SG Sólidos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Torta (%)", value=20.0)
recesso_manual = st.sidebar.number_input("Espessura câmara (mm)", value=30.0)
umidade = umidade_input / 100

# CÁLCULOS
tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100},
]

ciclos_dia = (horas_op * 60) / tempo_cycle if tempo_cycle > 0 else 0
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_total_L_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

# TABELA PRINCIPAL
st.subheader("📋 Opções de Dimensionamento")
res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso_manual / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    area_total = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_total if area_total > 0 else 0
    res_list.append({
        "Modelo (mm)": f"{p['nom']} x {p['nom']}",
        "Placas": num_placas,
        "Área Total (m²)": f"{area_total:.2f}",
        "Fluxo (L/m²h)": f"{fluxo:.1f}",
        "Status": "✅ OK" if num_placas <= p["max"] else "❌ Limite"
    })
st.table(res_list)

# TABELA REDUNDÂNCIA
st.subheader("🔄 Alternativas em Paralelo")
multi_list = []
for nom_alvo in [2000, 1500]:
    p_ref = next(item for item in tamanhos if item["nom"] == nom_alvo)
    placas_por_filtro = math.ceil((vol_total_L_req / 2) / (p_ref["vol_ref"] * (recesso_manual / 30)))
    multi_list.append({
        "Configuração": f"2x Filtros {nom_alvo} mm",
        "Placas/Filtro": placas_por_filtro,
        "Status": "✅ Recomendado" if placas_por_filtro <= p_ref["max"] else "⚠️ Limite Alto"
    })
st.table(multi_list)

# BOTÃO DE PDF
st.markdown("---")
if cliente and n_opp:
    pdf_output = gerar_pdf_estudo(cliente, projeto, produto, mercado, n_opp, responsavel, res_list, multi_list)
    if isinstance(pdf_output, bytes):
        st.download_button(
            label="📄 Baixar Relatório em PDF",
            data=pdf_output,
            file_name=f"Estudo_Cleanova_{cliente}_{n_opp}.pdf",
            mime="application/pdf"
        )
    else:
        st.error(f"Erro ao gerar PDF: {pdf_output}")
else:
    st.info("💡 Preencha o Nome do Cliente e o Nº OPP para habilitar o PDF.")

# ---------------------------------------------------------
# LOGOTIPO
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
# CABEÇALHO
# ---------------------------------------------------------
row1_c1, row1_c2, row1_c3 = st.columns(3)
with row1_c1: cliente = st.text_input("👤 Nome do Cliente")
with row1_c2: projeto = st.text_input("📂 Nome do Projeto")
with row1_c3: mercado = st.text_input("🏭 Mercado (Ex: Mineração)")

row2_c1, row2_c2, row2_c3 = st.columns(3)
with row2_c1: produto = st.text_input("📦 Produto")
with row2_c2: n_opp = st.text_input("🔢 Nº OPP")
with row2_c3: responsavel = st.text_input("👨‍💻 Responsável")

st.markdown("---")

# ---------------------------------------------------------
# SIDEBAR DADOS TÉCNICOS
# ---------------------------------------------------------
st.sidebar.header("🚀 Operação")
solidos_dia = st.sidebar.number_input("Peso Sólidos Secos (ton/dia)", value=100.0)
horas_op = st.sidebar.number_input("Disponibilidade (Horas/dia)", value=20.0)
tempo_cycle = st.sidebar.number_input("Ciclo total (minutos)", value=60)

st.sidebar.header("💧 Fluxo")
vol_polpa_dia = st.sidebar.number_input("Volume Lodo (m³/dia)", value=500.0)
vazao_lh = st.sidebar.number_input("Vazão Alimentação (L/h)", value=50000.0)

st.sidebar.header("🧪 Propriedades")
sg_solidos = st.sidebar.number_input("SG Sólidos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Torta (%)", value=20.0)
recesso_manual = st.sidebar.number_input("Espessura câmara (mm)", value=30.0)
umidade = umidade_input / 100

# ---------------------------------------------------------
# CÁLCULOS E TABELAS
# ---------------------------------------------------------
tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100},
]

ciclos_dia = (horas_op * 60) / tempo_cycle if tempo_cycle > 0 else 0
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_total_L_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

# Tabela Principal
st.subheader("📋 Opções de Dimensionamento")
res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso_manual / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    area_total = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_total if area_total > 0 else 0
    res_list.append({
        "Modelo (mm)": f"{p['nom']} x {p['nom']}",
        "Placas": num_placas,
        "Área Total (m²)": f"{area_total:.2f}",
        "Fluxo (L/m²h)": f"{fluxo:.1f}",
        "Status": "✅ OK" if num_placas <= p["max"] else "❌ Limite"
    })
st.table(res_list)

# Tabela Redundância
st.subheader("🔄 Alternativas em Paralelo")
multi_list = []
for nom_alvo in [2000, 1500]:
    p_ref = next(item for item in tamanhos if item["nom"] == nom_alvo)
    placas_por_filtro = math.ceil((vol_total_L_req / 2) / (p_ref["vol_ref"] * (recesso_manual / 30)))
    multi_list.append({
        "Configuração": f"2x Filtros {nom_alvo} mm",
        "Placas/Filtro": placas_por_filtro,
        "Status": "✅ Recomendado" if placas_por_filtro <= p_ref["max"] else "⚠️ Limite Alto"
    })
st.table(multi_list)

# ---------------------------------------------------------
# BOTÃO DE PDF (ESTA É A PARTE QUE DEVE APARECER)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📥 Finalizar Estudo Técnico")

if cliente and n_opp: # O botão só ativa se você preencher Cliente e OPP
    pdf_output = gerar_pdf_estudo(cliente, projeto, produto, mercado, n_opp, responsavel, res_list, multi_list)
    
    if isinstance(pdf_output, bytes):
        st.download_button(
            label="📄 Baixar Relatório em PDF",
            data=pdf_output,
            file_name=f"Cleanova_Micronics_{cliente}_{n_opp}.pdf",
            mime="application/pdf"
        )
    else:
        st.error(f"Erro ao gerar PDF: {pdf_output}")
else:
    st.warning("⚠️ Preencha o Nome do Cliente e o Nº OPP para habilitar o download do PDF.")
