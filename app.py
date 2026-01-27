import streamlit as st
import math
from fpdf import FPDF
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR PDF (ATUALIZADA COM NOVOS KPIs)
# ---------------------------------------------------------
def gerar_pdf_estudo(cliente, projeto, produto, mercado, opp, resp, dados_tec, res_unicos, kpis):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Título
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "ESTUDO TECNICO DE DIMENSIONAMENTO", ln=True, align="C")
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "CLEANOVA MICRONICS", ln=True, align="C")
        pdf.ln(5)
        
        # Dados de Identificação
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 7, f"Cliente: {cliente}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 7, f"Mercado: {mercado}".encode('latin-1', 'ignore').decode('latin-1'), 0, ln=True)
        pdf.cell(95, 7, f"N. OPP: {opp}".encode('latin-1', 'ignore').decode('latin-1'), 0)
        pdf.cell(95, 7, f"Data: {datetime.now().strftime('%d/%m/%Y')}", 0, ln=True)
        pdf.ln(5)

        # KPIs de Performance do Dia
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, "Indicadores de Performance (Diario):", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(95, 7, f"Peso Total de Torta: {kpis['peso_torta_dia']:.2f} ton/dia", 1)
        pdf.cell(95, 7, f"Area Filtrante Requerida: {kpis['area_req']:.2f} m2", 1, ln=True)
        pdf.ln(5)
        
        # Tabela de Resultados
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 10, "Modelo", 1); pdf.cell(20, 10, "Placas", 1); pdf.cell(30, 10, "Area (m2)", 1); 
        pdf.cell(35, 10, "Fluxo (L/m2h)", 1); pdf.cell(40, 10, "Dry Solids (kg/m2/d)", 1); pdf.cell(25, 10, "Status", 1, ln=True)
        
        pdf.set_font("Arial", "", 8)
        for r in res_unicos:
            status_limpo = r["Status"].replace("✅", "").replace("❌", "").strip()
            pdf.cell(40, 10, r["Modelo (mm)"], 1)
            pdf.cell(20, 10, str(r["Placas"]), 1)
            pdf.cell(30, 10, r["Area"], 1)
            pdf.cell(35, 10, r["Fluxo"], 1)
            pdf.cell(40, 10, r["Dry Solids Load"], 1)
            pdf.cell(25, 10, status_limpo, 1, ln=True)
            
        # Assinaturas
        pdf.ln(20)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(95, 5, "__________________________", 0, align="C")
        pdf.cell(95, 5, "__________________________", 0, ln=True, align="C")
        pdf.cell(95, 5, f"Elaborado: {resp}".encode('latin-1', 'ignore').decode('latin-1'), 0, align="C")
        pdf.cell(95, 5, "Conferido (Validacao)", 0, ln=True, align="C")
        
        return pdf.output(dest="S").encode("latin-1", "ignore")
    except Exception as e:
        return f"Erro ao gerar PDF: {str(e)}"

# ---------------------------------------------------------
# INTERFACE PRINCIPAL
# ---------------------------------------------------------
st.title("Cleanova Micronics | Dimensionador")

# IDENTIFICAÇÃO
c1, c2, c3 = st.columns(3)
with c1: cliente = st.text_input("👤 Nome do Cliente")
with c2: mercado = st.text_input("🏭 Mercado")
with c3: n_opp = st.text_input("🔢 Nº OPP")

# SIDEBAR DADOS
st.sidebar.header("🚀 Capacidade")
solidos_dia = st.sidebar.number_input("Sólidos Secos (ton/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade Operacional (%)", 0, 100, 80)
tempo_cycle = st.sidebar.number_input("Ciclo Total (minutos)", value=60)

st.sidebar.header("💧 Fluxo e Propriedades")
vazao_lh = st.sidebar.number_input("Vazão de Alimentação (L/h)", value=50000.0)
sg_solidos = st.sidebar.number_input("SG Sólidos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Torta (%)", value=20.0)
recesso = st.sidebar.number_input("Espessura câmara (mm)", value=30.0)
responsavel = st.sidebar.text_input("👨‍💻 Responsável", value="Engenharia")

# ---------------------------------------------------------
# CÁLCULOS TÉCNICOS
# ---------------------------------------------------------
disponibilidade_horas = 24 * (utilizacao_pct / 100)
ciclos_dia = (disponibilidade_horas * 60) / tempo_cycle if tempo_cycle > 0 else 0

umidade = umidade_input / 100
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1

# Peso Total de Torta (Sólidos + Água)
peso_torta_dia = solidos_dia / (1 - umidade)
peso_torta_ciclo = peso_torta_dia / ciclos_dia if ciclos_dia > 0 else 0

# Volume Requerido
vol_torta_ciclo_m3 = (peso_torta_ciclo / dens_torta)
vol_total_L_req = vol_torta_ciclo_m3 * 1000

# ---------------------------------------------------------
# RESULTADOS E INDICADORES
# ---------------------------------------------------------
st.markdown("---")
k1, k2, k3 = st.columns(3)
k1.metric("Peso Torta Total", f"{peso_torta_dia:.2f} t/dia")
k2.metric("Disponibilidade", f"{disponibilidade_horas:.1f} h/dia ({utilizacao_pct}%)")
k3.metric("Ciclos p/ dia", f"{ciclos_dia:.1f}")

tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100},
]

st.subheader("📋 Performance por Modelo de Filtro")
res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    area_t = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_t if area_t > 0 else 0
    
    # Dry Solids per Unit of Filter Area per Day (kg/m²/day)
    # Fórmula: (Sólidos Secos Dia * 1000) / Área Total
    dry_solids_load = (solidos_dia * 1000) / area_t if area_t > 0 else 0
    
    res_list.append({
        "Modelo (mm)": f"{p['nom']}x{p['nom']}",
        "Placas": num_placas,
        "Area": f"{area_t:.1f}",
        "Fluxo": f"{fluxo:.1f}",
        "Dry Solids Load": f"{dry_solids_load:.1f}",
        "Status": "✅ OK" if num_placas <= p["max"] else "❌ Limite"
    })

st.table(res_list)

# ---------------------------------------------------------
# BOTÃO PDF
# ---------------------------------------------------------
st.markdown("---")
if cliente and n_opp:
    # Capturando área do primeiro modelo que deu "OK" para o resumo
    area_sugerida = next((float(r["Area"]) for r in res_list if "OK" in r["Status"]), 0)
    kpis_pdf = {"peso_torta_dia": peso_torta_dia, "area_req": area_sugerida}
    
    pdf_bytes = gerar_pdf_estudo(cliente, "Projeto", "Produto", mercado, n_opp, responsavel, {}, res_list, kpis_pdf)
    
    st.download_button("📄 Baixar Relatório Técnico PDF", data=pdf_bytes, 
                       file_name=f"Micronics_{cliente}_{n_opp}.pdf", mime="application/pdf")
else:
    st.info("💡 Preencha Nome e OPP para liberar o PDF.")
