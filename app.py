import streamlit as st
import math
from fpdf import FPDF

# 1. Configuração da página
st.set_page_config(page_title="Cleanova Micronics | Dimensionador", layout="wide")

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR PDF (V41)
# ---------------------------------------------------------
def gerar_pdf_estudo(cliente, projeto, produto, mercado, opp, resp, dados_tec, res_unicos, kpis, opex):
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

        # Performance e Ciclos
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, "Indicadores de Performance e Operacao:", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(95, 7, f"Peso Total de Torta: {kpis['peso_torta_dia']:.2f} t/dia", 1)
        pdf.cell(95, 7, f"Ciclos Estimados: {kpis['ciclos_mes']:.0f} ciclos/mes", 1, ln=True)
        pdf.cell(95, 7, f"Producao Solidos Secos: {kpis['solidos_dia']:.2f} t/dia", 1)
        pdf.cell(95, 7, f"Disponibilidade: {kpis['disp_h']:.1f} h/dia", 1, ln=True)
        pdf.ln(5)

        # OPEX
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, "Estimativa de Custos Operacionais (OPEX):", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(63, 7, f"Energia/Mes: R$ {opex['energia_mes']:.2f}", 1)
        pdf.cell(63, 7, f"Lonas/Mes: R$ {opex['lonas_mes']:.2f}", 1)
        pdf.cell(64, 7, f"Custo Total: R$ {opex['total_t_seca']:.2f} / t seca", 1, ln=True)
        pdf.ln(8)
        
        # Tabela
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
        pdf.set_font("Arial", "B", 9)
        pdf.cell(80, 5, "Elaborado (Responsavel)", 0, align="C"); pdf.cell(20, 5, "", 0); pdf.cell(80, 5, "Conferido (Validacao)", 0, ln=True, align="C")
        
        return pdf.output(dest="S").encode("latin-1", "ignore")
    except Exception as e:
        return f"Erro ao gerar PDF: {str(e)}"

# ---------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------
st.title("Cleanova Micronics | Dimensionador & OPEX")
st.markdown("---")

c1, c2, c3 = st.columns(3)
cliente = c1.text_input("👤 Nome do Cliente")
projeto = c2.text_input("📂 Nome do Projeto")
mercado = c3.text_input("🏭 Mercado")

c4, c5, c6 = st.columns(3)
produto = c4.text_input("📦 Produto")
n_opp = c5.text_input("🔢 Nº OPP")
responsavel = c6.text_input("👨‍💻 Responsável")

st.markdown("---")

# SIDEBAR
st.sidebar.header("🚀 Capacidade")
solidos_dia = st.sidebar.number_input("Sólidos secos/dia (ton/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade Operacional (%)", 0, 100, 90)
tempo_cycle = st.sidebar.number_input("Ciclo (min)", value=45)

st.sidebar.header("🧪 Propriedades Técnicas")
vazao_lh = st.sidebar.number_input("Vazão de Alimentação (L/h)", value=50000.0)
vol_lodo_dia = st.sidebar.number_input("Volume lodo/dia (m³/dia)", value=500.0)
sg_solidos = st.sidebar.number_input("Gravidade específica sólidos secos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Torta (%)", value=20.0)
recesso = st.sidebar.number_input("Espessura câmara (mm)", value=30.0)

st.sidebar.header("💰 Custos Operacionais (OPEX)")
custo_kwh = st.sidebar.number_input("Custo Energia (R$/kWh)", value=0.65)
custo_lona_un = st.sidebar.number_input("Preço estimado lona (R$/unid)", value=450.0)
vida_lona_ciclos = st.sidebar.number_input("Vida útil lona (Ciclos)", value=2000)

# CÁLCULOS
umidade = umidade_input / 100
disp_h = 24 * (utilizacao_pct / 100)
ciclos_dia = (disp_h * 60) / tempo_cycle if tempo_cycle > 0 else 0
ciclos_mes = ciclos_dia * 30

conc_solidos_calc = (solidos_dia / vol_lodo_dia) * 100 if vol_lodo_dia > 0 else 0
peso_torta_dia = solidos_dia / (1 - umidade) if (1-umidade) > 0 else 0
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_total_L_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

# MODELOS
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

res_list = []
for p in tamanhos:
    vol_ajustado = p["vol_ref"] * (recesso / 30)
    num_placas = math.ceil(vol_total_L_req / vol_ajustado) if vol_ajustado > 0 else 0
    if p["nom"] > 1000 and num_placas < 25: continue
    
    area_t = num_placas * p["area_ref"]
    fluxo = vazao_lh / area_t if area_t > 0 else 0
    dry_solids_load = (solidos_dia * 1000) / area_t if area_t > 0 else 0
    
    res_list.append({
        "Modelo (mm)": f"{p['nom']}x{p['nom']}", "Placas": num_placas, "Area": f"{area_t:.1f}",
        "Fluxo": f"{fluxo:.1f}", "Dry Solids Load": f"{dry_solids_load:.1f}",
        "Status": "✅ OK" if num_placas <= p["max"] else "❌ Limite"
    })

# FINANCEIRO
energia_mes = (20 * disp_h * 30) * custo_kwh
if res_list:
    n_placas_ref = int(res_list[0]["Placas"])
    lonas_mes = (ciclos_mes / vida_lona_ciclos) * (n_placas_ref * 2) * custo_lona_un
    total_opex_mes = energia_mes + lonas_mes
    opex_ton_seca = total_opex_mes / (solidos_dia * 30) if solidos_dia > 0 else 0
else:
    lonas_mes = total_opex_mes = opex_ton_seca = 0

# --- EXIBIÇÃO ---
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Peso Torta", f"{peso_torta_dia:.1f} t/d")
k2.metric("Horas Úteis", f"{disp_h:.1f} h/d")
k3.metric("Ciclos/Mês", f"{ciclos_mes:.0f}")
k4.metric("OPEX / t seca", f"R$ {opex_ton_seca:.2f}")
k5.metric("Conc. Sólidos", f"{conc_solidos_calc:.1f} %")

st.subheader("📋 Performance por Modelo")
st.table(res_list)

st.subheader("💰 Resumo Financeiro Estimado (Mensal)")
f1, f2, f3 = st.columns(3)
f1.info(f"⚡ Energia: R$ {energia_mes:,.2f}")
f2.info(f"🧵 Lonas: R$ {lonas_mes:,.2f}")
f3.success(f"📊 Custo Total/Mês: R$ {total_opex_mes:,.2f}")

st.markdown("---")

# ZONA DE DOWNLOAD (Garantindo visibilidade)
if cliente and n_opp and responsavel:
    kpis_pdf = {"peso_torta_dia": peso_torta_dia, "disp_h": disp_h, "solidos_dia": solidos_dia, "ciclos_mes": ciclos_mes}
    opex_pdf = {"energia_mes": energia_mes, "lonas_mes": lonas_mes, "total_t_seca": opex_ton_seca}
    pdf_bytes = gerar_pdf_estudo(cliente, projeto, produto, mercado, n_opp, responsavel, {}, res_list, kpis_pdf, opex_pdf)
    
    # Criando um container centralizado para o botão
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        st.download_button(
            label="⬇️ BAIXAR RELATÓRIO PDF COMPLETO",
            data=pdf_bytes,
            file_name=f"Estudo_Micronics_{n_opp}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
else:
    st.warning("⚠️ O PDF será habilitado após preencher: Cliente, Nº OPP e Responsável.")
