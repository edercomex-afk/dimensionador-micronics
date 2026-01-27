import streamlit as st
import math
from fpdf import FPDF
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR PDF (ATUALIZADA)
# ---------------------------------------------------------
def gerar_pdf_estudo(cliente, projeto, produto, mercado, opp, resp, dados_tec, res_unicos, kpis):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Título do Relatório
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "ESTUDO TECNICO DE DIMENSIONAMENTO", ln=True, align="C")
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "CLEANOVA MICRONICS", ln=True, align="C")
        pdf.ln(5)
        
        # Dados de Identificação
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 7, f"Cliente: {cliente}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 7, f"Mercado: {mercado}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.cell(95, 7, f"Projeto: {projeto}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 7, f"N. OPP: {opp}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.cell(190, 7, f"Responsavel pelo Projeto: {resp}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.ln(5)

        # Resumo de Performance
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, "Indicadores de Performance Requeridos:", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(95, 7, f"Peso Total de Torta: {kpis['peso_torta_dia']:.2f} ton/dia", 1)
        pdf.cell(95, 7, f"Volume Lodo Diario: {kpis['vol_lodo_dia']:.2f} m3/dia", 1, ln=True)
        pdf.cell(95, 7, f"Disponibilidade: {kpis['disp_pct']}% ({kpis['disp_h']:.1f} h/dia)", 1)
        pdf.cell(95, 7, f"Conc. Solidos Alimentacao: {kpis['conc_sol']:.2f} %", 1, ln=True)
        pdf.ln(5)

        # Dados Informativos
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, "Especificacoes de Processo:", ln=True)
        pdf.set_font("Arial", "", 9)
        info_txt = f"Produto: {produto} | Temp: {dados_tec['temp']}C | pH: {dados_tec['ph']} | Lavagem Lona: {dados_tec['lav_l']} | Lavagem Torta: {dados_tec['lav_t']} | Membrana: {dados_tec['mem']}"
        pdf.multi_cell(190, 7, info_txt.encode('latin-1', 'ignore').decode('latin-1'), border=1)
        pdf.ln(8)
        
        # Tabela de Resultados
        pdf.set_font("Arial", "B", 9)
        pdf.cell(40, 10, "Modelo", 1); pdf.cell(20, 10, "Placas", 1); pdf.cell(30, 10, "Area (m2)", 1); 
        pdf.cell(30, 10, "Fluxo (L/m2h)", 1); pdf.cell(45, 10, "Dry Solids (kg/m2/d)", 1); pdf.cell(25, 10, "Status", 1, ln=True)
        
        pdf.set_font("Arial", "", 8)
        for r in res_unicos:
            status_limpo = r["Status"].replace("✅", "").replace("❌", "").replace("⚠️", "").strip()
            pdf.cell(40, 10, r["Modelo (mm)"], 1)
            pdf.cell(20, 10, str(r["Placas"]), 1)
            pdf.cell(30, 10, r["Area"], 1)
            pdf.cell(30, 10, r["Fluxo"], 1)
            pdf.cell(45, 10, r["Dry Solids Load"], 1)
            pdf.cell(25, 10, status_limpo, 1, ln=True)
            
        # Assinaturas
        pdf.ln(20)
        data_atual = datetime.now().strftime("%d/%m/%Y")
        pdf.set_font("Arial", "I", 9)
        pdf.cell(190, 10, f"Documento gerado em: {data_atual}", ln=True, align="R")
        pdf.ln(15)
        pdf.line(10, pdf.get_y(), 90, pdf.get_y())
        pdf.line(110, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(80, 5, "Elaborado (Responsavel)", 0, align="C")
        pdf.cell(20, 5, "", 0) 
        pdf.cell(80, 5, "Conferido (Validacao)", 0, ln=True, align="C")
        
        return pdf.output(dest="S").encode("latin-1", "ignore")
    except Exception as e:
        return f"Erro ao gerar PDF: {str(e)}"

# ---------------------------------------------------------
# INTERFACE PRINCIPAL
# ---------------------------------------------------------
st.title("Cleanova Micronics | Dimensionador de Filtro Prensa")
st.markdown("---")

# IDENTIFICAÇÃO
col1, col2, col3 = st.columns(3)
with col1: cliente = st.text_input("👤 Nome do Cliente")
with col2: projeto = st.text_input("📂 Nome do Projeto")
with col3: mercado = st.text_input("🏭 Mercado (Ex: Mineracao)")

col4, col5, col6 = st.columns(3)
with col4: produto = st.text_input("📦 Produto")
with col5: n_opp = st.text_input("🔢 Nº OPP")
with col6: responsavel = st.text_input("👨‍💻 Responsável pelo Projeto")

st.markdown("---")

# SIDEBAR DADOS
st.sidebar.header("🚀 Capacidade")
solidos_dia = st.sidebar.number_input("Sólidos secos/dia (ton/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade Operacional (%)", 0, 100, 80)
tempo_cycle = st.sidebar.number_input("Ciclo (min)", value=60)

st.sidebar.header("📝 Processo")
temp_proc = st.sidebar.number_input("Temperatura (°C)", value=25)
ph_sol = st.sidebar.number_input("pH", value=7.0)
lav_lona = st.sidebar.selectbox("Lavagem de Lona?", ["Sim", "Não"])
lav_torta = st.sidebar.selectbox("Lavagem de Torta?", ["Sim", "Não"])
membrana = st.sidebar.selectbox("Membrana?", ["Sim", "Não"])

st.sidebar.header("🧪 Propriedades Técnicas")
vazao_lh = st.sidebar.number_input("Vazão de Alimentação (L/h)", value=50000.0)
# NOVO CAMPO ADICIONADO ABAIXO
vol_lodo_dia = st.sidebar.number_input("Volume de lodo/polpa por dia (m³/dia)", value=500.0)
sg_solidos = st.sidebar.number_input("Gravidade específica dos sólidos secos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Torta (%)", value=20.0)
recesso = st.sidebar.number_input("Espessura câmara (mm)", value=30.0)

# CÁLCULOS TÉCNICOS
umidade = umidade_input / 100
disp_horas = 24 * (utilizacao_pct / 100)
ciclos_dia = (disp_horas * 60) / tempo_cycle if tempo_cycle > 0 else 0

# Concentração de sólidos calculada (Peso Sólidos / Volume Lodo)
conc_solidos_calc = (solidos_dia / vol_lodo_dia) * 100 if vol_lodo_dia > 0 else 0

peso_torta_dia = solidos_dia / (1 - umidade) if (1-umidade) > 0 else 0
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0

dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_total_L_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

# MÉTRICAS RÁPIDAS NO TOPO
k1, k2, k3, k4 = st.columns(4)
k1.metric("Peso Torta Total", f"{peso_torta_dia:.2f} t/dia")
k2.metric("Disponibilidade", f"{disp_horas:.1f} h/dia")
k3.metric("Ciclos por dia", f"{ciclos_dia:.1f}")
k4.metric("Conc. Sólidos", f"{conc_solidos_calc:.1f} %")

# RESULTADOS
st.subheader("📋 Resultados do Dimensionamento")

tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100},
]

res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    area_t = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_t if area_t > 0 else 0
    dry_solids_load = (solidos_dia * 1000) / area_t if area_t > 0 else 0
    
    res_list.append({
        "Modelo (mm)": f"{p['nom']} x {p['nom']}",
        "Placas": num_placas,
        "Area": f"{area_t:.2f}",
        "Fluxo": f"{fluxo:.1f}",
        "Dry Solids Load": f"{dry_solids_load:.1f}",
        "Status": "✅ OK" if num_placas <= p["max"] else "❌ Limite"
    })
st.table(res_list)

# BOTÃO PDF
st.markdown("---")
if cliente and n_opp and responsavel:
    dados_tec = {"temp": temp_proc, "ph": ph_sol, "lav_l": lav_lona, "lav_t": lav_torta, "mem": membrana}
    kpis_pdf = {
        "peso_torta_dia": peso_torta_dia, 
        "disp_pct": utilizacao_pct, 
        "disp_h": disp_horas,
        "vol_lodo_dia": vol_lodo_dia,
        "conc_sol": conc_solidos_calc
    }
    
    pdf_bytes = gerar_pdf_estudo(cliente, projeto, produto, mercado, n_opp, responsavel, dados_tec, res_list, kpis_pdf)
    
    if isinstance(pdf_bytes, bytes):
        st.download_button(label="📄 Gerar Relatório PDF Final", data=pdf_bytes, 
                           file_name=f"Estudo_{cliente}_{n_opp}.pdf", mime="application/pdf")
else:
    st.info("💡 Preencha o Cliente, Nº OPP e Responsável para habilitar o PDF.")
