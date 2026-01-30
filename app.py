import streamlit as st
import math
from fpdf import FPDF
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Dimensionamento Cleanova Micronics", layout="wide")

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR PDF (ESTRUTURA MANTIDA)
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
        
        pdf.set_font("Arial", "B", 8)
        pdf.cell(35, 10, "Modelo", 1); pdf.cell(15, 10, "Placas", 1); pdf.cell(25, 10, "Area (m2)", 1); 
        pdf.cell(25, 10, "Fluxo (L/m2h)", 1); pdf.cell(65, 10, "Dry Solids Load (kg/m2/d)", 1); pdf.cell(25, 10, "Status", 1, ln=True)
        
        pdf.set_font("Arial", "", 8)
        for r in res_unicos:
            status_limpo = r["Status"].replace("✅", "").replace("❌", "").strip()
            pdf.cell(35, 10, r["Modelo (mm)"], 1)
            pdf.cell(15, 10, str(r["Placas"]), 1)
            pdf.cell(25, 10, r["Area"], 1)
            pdf.cell(25, 10, r["Fluxo"], 1)
            pdf.cell(65, 10, r["Dry Solids Load"], 1)
            pdf.cell(25, 10, status_limpo, 1, ln=True)
            
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 90, pdf.get_y()); pdf.line(110, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(80, 5, "Elaborado (Responsavel)", 0, align="C"); pdf.cell(20, 5, "", 0); pdf.cell(80, 5, "Conferido (Validacao)", 0, ln=True, align="C")
        
        return pdf.output(dest="S").encode("latin-1", "ignore")
    except Exception as e:
        return f"Erro ao gerar PDF: {str(e)}"

# ---------------------------------------------------------
# INTERFACE PRINCIPAL
# ---------------------------------------------------------
st.title("Cleanova Micronics | Dimensionador de Filtro Prensa")
st.markdown("---")

c1, c2, c3 = st.columns(3)
with c1: cliente = st.text_input("👤 Nome do Cliente")
with c2: projeto = st.text_input("📂 Nome do Projeto")
with c3: mercado = st.text_input("🏭 Mercado")

c4, c5, c6 = st.columns(3)
with c4: produto = st.text_input("📦 Produto")
with c5: n_opp = st.text_input("🔢 Nº OPP")
with c6: responsavel = st.text_input("👨‍💻 Responsável")

st.markdown("---")

# SIDEBAR
st.sidebar.header("🚀 Capacidade")
solidos_dia = st.sidebar.number_input("Sólidos secos/dia (ton/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade Operacional (%)", 0, 100, 80)
tempo_cycle = st.sidebar.number_input("Ciclo (min)", value=60)

st.sidebar.header("📝 Processo e Automação")
temp_proc = st.sidebar.number_input("Temperatura (°C)", value=25)
ph_sol = st.sidebar.number_input("pH", value=7.0)
nivel_auto = st.sidebar.selectbox("Nível de Automação", ["Manual", "Semiautomático", "Automático (Full)"])
lav_lona = st.sidebar.selectbox("Lavagem de Lona?", ["Sim", "Não"])
lav_torta = st.sidebar.selectbox("Lavagem de Torta?", ["Sim", "Não"])
membrana = st.sidebar.selectbox("Membrana?", ["Sim", "Não"])

st.sidebar.header("🧪 Propriedades Técnicas")
vazao_lh = st.sidebar.number_input("Vazão de Alimentação (L/h)", value=50000.0)
vol_lodo_dia = st.sidebar.number_input("Volume lodo/dia (m³/dia)", value=500.0)
sg_solidos = st.sidebar.number_input("Gravidade específica sólidos secos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Torta (%)", value=20.0)
recesso = st.sidebar.number_input("Espessura câmara (mm)", value=30.0)

# CÁLCULOS
umidade = umidade_input / 100
disp_h = 24 * (utilizacao_pct / 100)
ciclos_dia = (disp_h * 60) / tempo_cycle if tempo_cycle > 0 else 0
conc_solidos_calc = (solidos_dia / vol_lodo_dia) * 100 if vol_lodo_dia > 0 else 0
peso_torta_dia = solidos_dia / (1 - umidade) if (1-umidade) > 0 else 0
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_total_L_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

k1, k2, k3, k4 = st.columns(4)
k1.metric("Peso Torta Úmida", f"{peso_torta_dia:.1f} t/d")
k2.metric("Horas Úteis", f"{disp_h:.1f} h/d")
k3.metric("Ciclos/dia", f"{ciclos_dia:.1f}")
k4.metric("Conc. Sólidos", f"{conc_solidos_calc:.1f} %")

# LISTA COMPLETA DE MODELOS
tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100},
    {"nom": 1000, "area_ref": 1.95, "vol_ref": 25,  "max": 90},
    {"nom": 800,  "area_ref": 1.15, "vol_ref": 14,  "max": 80},
    {"nom": 630,  "area_ref": 0.65, "vol_ref": 8.5, "max": 60},
    {"nom": 470,  "area_ref": 0.35, "vol_ref": 4.2, "max": 40},
]

st.subheader("📋 Performance por Modelo")


res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    
    # REGRA: Ocultar modelos grandes (>1000mm) se resultarem em menos de 25 placas
    if p["nom"] > 1000 and num_placas < 25:
        continue
        
    area_t = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_t if area_t > 0 else 0
    dry_solids_load = (solidos_dia * 1000) / area_t if area_t > 0 else 0
    
    res_list.append({
        "Modelo (mm)": f"{p['nom']}x{p['nom']}", 
        "Placas": num_placas, 
        "Area": f"{area_t:.1f}",
        "Fluxo": f"{fluxo:.1f}", 
        "Dry Solids Load": f"{dry_solids_load:.1f}",
        "Status": "✅ OK" if num_placas <= p["max"] else "❌ Limite"
    })

if res_list:
    st.table(res_list)
else:
    st.warning("Nenhum modelo atende aos critérios com a configuração atual.")

# EXPORTAÇÃO (Restauração do botão com validação)
st.markdown("---")
if cliente and n_opp and responsavel:
    dados_tec = {"temp": temp_proc, "ph": ph_sol, "lav_l": lav_lona, "lav_t": lav_torta, "mem": membrana, "auto": nivel_auto}
    kpis_pdf = {"peso_torta_dia": peso_torta_dia, "disp_pct": utilizacao_pct, "disp_h": disp_h, "vol_lodo_dia": vol_lodo_dia, "conc_sol": conc_solidos_calc}
    
    pdf_bytes = gerar_pdf_estudo(cliente, projeto, produto, mercado, n_opp, responsavel, dados_tec, res_list, kpis_pdf)
    
    st.download_button(
        label="📄 Gerar Relatório PDF Final", 
        data=pdf_bytes, 
        file_name=f"Estudo_{cliente}_{n_opp}.pdf", 
        mime="application/pdf"
    )
else:
    st.info("💡 Para habilitar o PDF, preencha: Cliente, Nº OPP e Responsável.")
