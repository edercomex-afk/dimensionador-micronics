import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import io

# 1. Configuração da página
st.set_page_config(page_title="Cleanova Micronics | V52 Pro", layout="wide")

# --- FUNÇÃO PARA GERAR O GRÁFICO ---
def gerar_grafico_vazao_pressao(pressao_alvo, vazao_pico):
    tempo = np.linspace(0, 45, 100)
    pressao = pressao_alvo * (1 - np.exp(-0.15 * tempo))
    vazao = vazao_pico * np.exp(-0.12 * tempo)
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.set_xlabel('Tempo de Ciclo (min)')
    ax1.set_ylabel('Pressao (Bar)', color='tab:red')
    ax1.plot(tempo, pressao, color='tab:red', linewidth=3)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Vazao (L/h)', color='tab:blue')
    ax2.plot(tempo, vazao, color='tab:blue', linewidth=3)
    plt.title("Comportamento Dinamico: Bomba & Filtro")
    fig.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=120)
    plt.close(fig)
    img_buf.seek(0)
    return img_buf

# --- FUNÇÃO PDF CORRIGIDA (SEM ERROS DE UNICODE) ---
def gerar_pdf_final(dados_cliente, res_list, opex_dados, bomba_dados, img_buf):
    pdf = FPDF()
    pdf.add_page()
    
    # Função auxiliar para limpar texto para Latin-1
    def clean(text):
        return str(text).encode('latin-1', 'ignore').decode('latin-1')

    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, clean("ESTUDO TECNICO DE FILTRACAO"), ln=True, align="C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, clean("CLEANOVA MICRONICS"), ln=True, align="C")
    pdf.ln(5)

    # Dados do Cliente (Limpando caracteres especiais)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 7, clean(f"Cliente: {dados_cliente['cliente']}"), 1)
    pdf.cell(95, 7, clean(f"Projeto: {dados_cliente['projeto']}"), 1, ln=True)
    pdf.cell(63, 7, clean(f"Produto: {dados_cliente['produto']}"), 1)
    pdf.cell(63, 7, clean(f"Mercado: {dados_cliente['mercado']}"), 1)
    pdf.cell(64, 7, clean(f"OPP: {dados_cliente['opp']}"), 1, ln=True)
    pdf.ln(5)

    # Imagem do Gráfico
    with open("temp_pdf_chart.png", "wb") as f:
        f.write(img_buf.getbuffer())
    pdf.image("temp_pdf_chart.png", x=20, y=None, w=170)
    pdf.ln(5)

    # Tabela de Resultados
    pdf.set_font("Arial", "B", 10)
    pdf.cell(45, 8, "Modelo", 1); pdf.cell(25, 8, "Placas", 1); pdf.cell(35, 8, "Area (m2)", 1); pdf.cell(85, 8, "Status", 1, ln=True)
    pdf.set_font("Arial", "", 9)
    for r in res_list:
        pdf.cell(45, 8, clean(r["Modelo (mm)"]), 1)
        pdf.cell(25, 8, str(r["Placas"]), 1)
        pdf.cell(35, 8, clean(r["Area"]), 1)
        status_limpo = r["Status"].replace("✅", "OK").replace("❌", "Limite")
        pdf.cell(85, 8, clean(status_limpo), 1, ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, clean(f"Bomba Sugerida: {bomba_dados['marca']} - {bomba_dados['tipo']}"), ln=True)
    pdf.cell(190, 8, clean(f"OPEX Mensal Estimado: R$ {opex_dados['total']:,.2f}"), ln=True)

    return pdf.output(dest="S").encode("latin-1", "ignore")

# --- INTERFACE ---
st.title("Cleanova Micronics | Dimensionador V52")

# Cabeçalho
c1, c2, c3 = st.columns(3)
cliente = c1.text_input("Nome do Cliente")
projeto = c2.text_input("Nome do Projeto")
n_opp = c3.text_input("Numero da OPP")

c4, c5, c6 = st.columns(3)
produto = c4.text_input("Produto")
mercado = c5.text_input("Mercado")
responsavel = c6.text_input("Responsavel")

st.markdown("---")

# Sidebar
st.sidebar.header("Capacidade e Ciclo")
solidos_dia = st.sidebar.number_input("Solidos secos (t/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade (%)", 0, 100, 90)
tempo_cycle = st.sidebar.number_input("Tempo de Ciclo (min)", value=45)

st.sidebar.header("Processo")
vol_lodo_dia = st.sidebar.number_input("Volume Lodo (m3/dia)", value=500.0)
vazao_pico = st.sidebar.number_input("Vazao Pico Bomba (L/h)", value=50000.0)
sg_solidos = st.sidebar.number_input("SG Solidos Secos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade Torta (%)", value=20.0)
recesso = st.sidebar.number_input("Espessura camara (mm)", value=30.0)
pressao_manual = st.sidebar.slider("Pressao Filtracao (Bar)", 1, 15, 7)

st.sidebar.header("OPEX")
custo_kwh = st.sidebar.number_input("Custo Energia (R$/kWh)", value=0.65)
custo_lona_un = st.sidebar.number_input("Preco Lona (R$/unid)", value=450.0)
vida_lona_ciclos = st.sidebar.number_input("Vida util lona (Ciclos)", value=2000)

# --- CALCULOS ---
umidade = umidade_input / 100
disp_h = 24 * (utilizacao_pct / 100)
ciclos_dia = (disp_h * 60) / tempo_cycle if tempo_cycle > 0 else 0
ciclos_mes = ciclos_dia * 30
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
massa_seco_ciclo = solidos_dia / ciclos_dia if ciclos_dia > 0 else 0
vol_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta) * 1000

# Modelos
tamanhos = [
    {"nom": 2500, "area_ref": 6.25, "vol_ref": 165, "max": 190},
    {"nom": 2000, "area_ref": 4.50, "vol_ref": 125, "max": 160},
    {"nom": 1500, "area_ref": 4.50, "vol_ref": 70,  "max": 120},
    {"nom": 1200, "area_ref": 2.75, "vol_ref": 37,  "max": 100},
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

# OPEX
energia_mes = (20 * disp_h * 30) * custo_kwh
n_placas_ref = res_list[0]["Placas"] if res_list else 0
lonas_mes = (ciclos_mes / vida_lona_ciclos) * (n_placas_ref * 2) * custo_lona_un
total_opex_mes = energia_mes + lonas_mes
opex_ton_seca = total_opex_mes / (solidos_dia * 30) if solidos_dia > 0 else 0
marca = "PEMO (Italia)" if pressao_manual <= 6 else "WEIR (Warman/GEHO)"

# --- EXIBICAO ---
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Vol. Lodo/Dia", f"{vol_lodo_dia:.0f} m3")
k2.metric("Ciclos/Mes", f"{ciclos_mes:.0f}")
k3.metric("OPEX/t seca", f"R$ {opex_ton_seca:.2f}")
k4.metric("Vol. Torta/Ciclo", f"{vol_req:.0f} L")
k5.metric("Bomba", marca)

st.table(res_list)

graf_buf = gerar_grafico_vazao_pressao(pressao_manual, vazao_pico)
st.image(graf_buf)

if cliente and n_opp and responsavel:
    d_cliente = {"cliente": cliente, "projeto": projeto, "produto": produto, "mercado": mercado, "opp": n_opp}
    pdf_out = gerar_pdf_final(d_cliente, res_list, {"total": total_opex_mes}, {"marca": marca, "tipo": "Standard"}, graf_buf)
    st.download_button("Baixar Relatorio Tecnico V52", data=pdf_out, file_name=f"Estudo_Micronics.pdf", mime="application/pdf")
