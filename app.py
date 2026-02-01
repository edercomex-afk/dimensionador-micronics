import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import io

# 1. Configuração da página
st.set_page_config(page_title="Cleanova Micronics | V51 Pro", layout="wide")

# --- FUNÇÃO PARA GERAR O GRÁFICO ---
def gerar_grafico_vazao_pressao(pressao_alvo, vazao_pico):
    tempo = np.linspace(0, 45, 100)
    pressao = pressao_alvo * (1 - np.exp(-0.15 * tempo))
    vazao = vazao_pico * np.exp(-0.12 * tempo)
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.set_xlabel('Tempo de Ciclo (min)')
    ax1.set_ylabel('Pressão (Bar)', color='tab:red')
    ax1.plot(tempo, pressao, color='tab:red', linewidth=3)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Vazão (L/h)', color='tab:blue')
    ax2.plot(tempo, vazao, color='tab:blue', linewidth=3)
    plt.title("Comportamento Dinâmico: Bomba & Filtro")
    fig.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=120)
    plt.close(fig) # Fecha para liberar memória
    img_buf.seek(0)
    return img_buf

# --- FUNÇÃO PDF COMPLETA ---
def gerar_pdf_final(dados_cliente, res_list, opex_dados, bomba_dados, img_buf):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "PROPOSTA TECNICA DE FILTRACAO", ln=True, align="C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "CLEANOVA MICRONICS", ln=True, align="C")
    pdf.ln(5)

    # Cabeçalho no PDF
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 7, f"Cliente: {dados_cliente['cliente']}", 1)
    pdf.cell(95, 7, f"Projeto: {dados_cliente['projeto']}", 1, ln=True)
    pdf.cell(63, 7, f"Produto: {dados_cliente['produto']}", 1)
    pdf.cell(63, 7, f"Mercado: {dados_cliente['mercado']}", 1)
    pdf.cell(64, 7, f"N. OPP: {dados_cliente['opp']}", 1, ln=True)
    pdf.ln(5)

    # Inserir Gráfico
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, "Comportamento Dinamico do Sistema (Pressao x Vazao)", ln=True, fill=True)
    with open("temp_pdf_chart.png", "wb") as f:
        f.write(img_buf.getbuffer())
    pdf.image("temp_pdf_chart.png", x=20, y=None, w=170)
    pdf.ln(5)

    # Tabela de Resultados
    pdf.set_font("Arial", "B", 10)
    pdf.cell(45, 8, "Modelo", 1); pdf.cell(25, 8, "Placas", 1); pdf.cell(35, 8, "Area (m2)", 1); pdf.cell(85, 8, "Status", 1, ln=True)
    pdf.set_font("Arial", "", 9)
    for r in res_list:
        pdf.cell(45, 8, r["Modelo (mm)"], 1)
        pdf.cell(25, 8, str(r["Placas"]), 1)
        pdf.cell(35, 8, r["Area"], 1)
        pdf.cell(85, 8, r["Status"], 1, ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, f"Bomba Sugerida: {bomba_dados['marca']} - {bomba_dados['tipo']}", ln=True)
    pdf.cell(190, 8, f"OPEX Mensal Estimado: R$ {opex_dados['total']:,.2f}", ln=True)

    return pdf.output(dest="S").encode("latin-1", "ignore")

# --- INTERFACE PRINCIPAL ---
st.title("Cleanova Micronics | Dimensionador Full V51")

# Cabeçalho - Todos os Itens Restaurados
c1, c2, c3 = st.columns(3)
cliente = c1.text_input("👤 Nome do Cliente")
projeto = c2.text_input("📂 Nome do Projeto")
n_opp = c3.text_input("🔢 Número da OPP")

c4, c5, c6 = st.columns(3)
produto = c4.text_input("📦 Produto")
mercado = c5.text_input("🏭 Mercado")
responsavel = c6.text_input("👨‍💻 Responsável")

st.markdown("---")

# Sidebar - Parâmetros Completos
st.sidebar.header("🚀 Capacidade & Ciclo")
solidos_dia = st.sidebar.number_input("Sólidos secos (t/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade (%)", 0, 100, 90)
tempo_cycle = st.sidebar.number_input("Tempo de Ciclo (min)", value=45)

st.sidebar.header("🧪 Processo")
vol_lodo_dia = st.sidebar.number_input("Volume Lodo (m³/dia)", value=500.0)
vazao_pico = st.sidebar.number_input("Vazão Pico Bomba (L/h)", value=50000.0)
sg_solidos = st.sidebar.number_input("SG Sólidos Secos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Torta (%)", value=20.0)
recesso = st.sidebar.number_input("Espessura câmara (mm)", value=30.0)
pressao_manual = st.sidebar.slider("Pressão Filtração (Bar)", 1, 15, 7)

st.sidebar.header("💰 OPEX")
custo_kwh = st.sidebar.number_input("Custo Energia (R$/kWh)", value=0.65)
custo_lona_un = st.sidebar.number_input("Preço Lona (R$/unid)", value=450.0)
vida_lona_ciclos = st.sidebar.number_input("Vida útil lona (Ciclos)", value=2000)

# --- CÁLCULOS ---
umidade = umidade_input / 100
disp_h = 24 * (utilizacao_pct / 100)
ciclos_dia = (disp_h * 60) / tempo_cycle if tempo_cycle > 0 else 0
ciclos_mes = ciclos_dia * 30
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
vol_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

# Seleção Inteligente de Modelos
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
exibiu_erro = False
for p in tamanhos:
    v_adj = p["vol_ref"] * (recesso / 30)
    n_placas = math.ceil(vol_req / v_adj) if v_adj > 0 else 0
    if p["nom"] > 1000 and n_placas < 25: continue
    
    if n_placas <= p["max"]:
        res_list.append({"Modelo (mm)": f"{p['nom']}x{p['nom']}", "Placas": n_placas, "Area": f"{n_placas * p['area_ref']:.1f}", "Status": "✅ OK"})
    elif not exibiu_erro:
        res_list.append({"Modelo (mm)": f"{p['nom']}x{p['nom']}", "Placas": n_placas, "Area": f"{n_placas * p['area_ref']:.1f}", "Status": "❌ Limite Excedido"})
        exibiu_erro = True

# Cálculos OPEX
energia_mes = (20 * disp_h * 30) * custo_kwh
n_placas_ref = res_list[0]["Placas"] if res_list else 0
lonas_mes = (ciclos_mes / vida_lona_ciclos) * (n_placas_ref * 2) * custo_lona_un
total_opex_mes = energia_mes + lonas_mes
opex_ton_seca = total_opex_mes / (solidos_dia * 30) if solidos_dia > 0 else 0

# Bomba Sugerida
if pressao_manual <= 6:
    marca, tipo = "PEMO (Itália)", "Série AO/AB - Centrífuga Revestida"
else:
    marca, tipo = "WEIR (Warman/GEHO)", "Série Warman AH ou GEHO ZPR"

# --- EXIBIÇÃO ---
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Vol. Lodo/Dia", f"{vol_lodo_dia:.0f} m³")
k2.metric("Ciclos/Mês", f"{ciclos_mes:.0f}")
k3.metric("OPEX/t seca", f"R$ {opex_ton_seca:.2f}")
k4.metric("Vol. Torta/Ciclo", f"{vol_req:.0f} L")
k5.metric("Bomba", marca)

st.subheader("📋 Dimensionamento e Performance")
st.table(res_list)

col_graf, col_fin = st.columns([2, 1])
with col_graf:
    graf_buf = gerar_grafico_vazao_pressao(pressao_manual, vazao_pico)
    st.image(graf_buf)
with col_fin:
    st.info(f"⚡ Energia: R$ {energia_mes:,.2f}")
    st.info(f"🧵 Lonas: R$ {lonas_mes:,.2f}")
    st.success(f"💰 Total OPEX: R$ {total_opex_mes:,.2f}")
    st.warning(f"🛠️ Bomba: {marca} - {tipo}")

# Geração do PDF
st.markdown("---")
if cliente and n_opp and responsavel:
    d_cliente = {"cliente": cliente, "projeto": projeto, "produto": produto, "mercado": mercado, "opp": n_opp}
    opex_p = {"total": total_opex_mes}
    bomba_p = {"marca": marca, "tipo": tipo}
    pdf_output = gerar_pdf_final(d_cliente, res_list, opex_p, bomba_p, graf_buf)
    st.download_button("📄 Baixar Relatório Técnico V51", data=pdf_output, file_name=f"Estudo_Micronics_{n_opp}.pdf", mime="application/pdf")
else:
    st.warning("⚠️ Preencha Nome do Cliente, Nº OPP e Responsável para liberar o PDF.")
