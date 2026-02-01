import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import io

# 1. Configuração da página
st.set_page_config(page_title="Cleanova Micronics | V47 Final Pro", layout="wide")

# --- FUNÇÃO PARA GERAR O GRÁFICO (SALVANDO EM MEMÓRIA) ---
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
    plt.savefig(img_buf, format='png', dpi=150)
    img_buf.seek(0)
    return fig, img_buf

# --- FUNÇÃO PDF V47 (COMPLETA COM GRÁFICO E TABELA) ---
def gerar_pdf_estudo(cliente, opp, resp, res_unicos, kpis, opex, bomba, img_grafico):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "ESTUDO TECNICO DE FILTRACAO", ln=True, align="C")
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "CLEANOVA MICRONICS", ln=True, align="C")
        pdf.ln(10)
        
        # Cabeçalho
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 8, f"Cliente: {cliente}", 1)
        pdf.cell(95, 8, f"OPP: {opp}", 1, ln=True)
        pdf.ln(5)

        # Gráfico
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "Performance de Bombeamento", ln=True)
        with open("temp_chart.png", "wb") as f:
            f.write(img_grafico.getbuffer())
        pdf.image("temp_chart.png", x=15, y=None, w=170)
        pdf.ln(5)

        # Tabela de Modelos
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 8, "Modelo", 1); pdf.cell(25, 8, "Placas", 1); pdf.cell(35, 8, "Area (m2)", 1); pdf.cell(90, 8, "Bomba Sugerida", 1, ln=True)
        pdf.set_font("Arial", "", 9)
        for r in res_unicos:
            pdf.cell(40, 8, r["Modelo (mm)"], 1)
            pdf.cell(25, 8, str(r["Placas"]), 1)
            pdf.cell(35, 8, r["Area"], 1)
            pdf.cell(90, 8, bomba['marca'], 1, ln=True)
            
        return pdf.output(dest="S").encode("latin-1", "ignore")
    except Exception as e: return f"Erro PDF: {str(e)}"

# --- INTERFACE PRINCIPAL ---
st.title("Cleanova Micronics | Dimensionador & Gráficos V47")

# Cabeçalho
c1, c2, c3 = st.columns(3)
u_cliente = c1.text_input("👤 Cliente")
u_projeto = c2.text_input("📂 Projeto")
u_opp = c3.text_input("🔢 OPP")

# Sidebar
st.sidebar.header("🚀 Capacidade")
solidos_dia = st.sidebar.number_input("Sólidos secos (t/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade (%)", 0, 100, 90)
tempo_cycle = st.sidebar.number_input("Ciclo (min)", value=45)

st.sidebar.header("🧪 Processo")
vazao_pico = st.sidebar.number_input("Vazão Pico (L/h)", value=50000.0)
sg_solidos = st.sidebar.number_input("SG Sólidos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade (%)", value=20.0)
recesso = st.sidebar.number_input("Recesso (mm)", value=30.0)
pressao_manual = st.sidebar.slider("Pressão Filtração (Bar)", 1, 15, 7)

# Cálculos Base
umidade = umidade_input / 100
disp_h = 24 * (utilizacao_pct / 100)
ciclos_dia = (disp_h * 60) / tempo_cycle if tempo_cycle > 0 else 0
ciclos_mes = ciclos_dia * 30
peso_torta_dia = solidos_dia / (1 - umidade) if (1-umidade) > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_req = (( (solidos_dia/ciclos_dia) / (1-umidade) ) / dens_torta) * 1000

# Modelagem Micronics (8 modelos)
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
    v_adj = p["vol_ref"] * (recesso / 30)
    n_placas = math.ceil(vol_req / v_adj) if v_adj > 0 else 0
    if p["nom"] > 1000 and n_placas < 25: continue
    status = "✅ OK" if n_placas <= p["max"] else "❌ Limite"
    res_list.append({"Modelo (mm)": f"{p['nom']}x{p['nom']}", "Placas": n_placas, "Area": f"{n_placas * p['area_ref']:.1f}", "Status": status})

# Bomba
if pressao_manual <= 6: marca, tipo = "PEMO (Itália)", "Série AO/AB"
else: marca, tipo = "WEIR (Warman/GEHO)", "Série AH/ZPR"

# Exibição
k1, k2, k3 = st.columns(3)
k1.metric("Ciclos/Mês", f"{ciclos_mes:.0f}")
k2.metric("Vol. Torta/Ciclo", f"{vol_req:.0f} L")
k3.metric("Bomba", marca)

st.subheader("📋 Resultados de Dimensionamento")
st.table(res_list)

fig, buf = gerar_grafico_vazao_pressao(pressao_manual, vazao_pico)
st.pyplot(fig)

if u_cliente and u_opp:
    b_dados = {"marca": marca, "tipo": tipo, "pressao": pressao_manual, "vazao": vazao_pico}
    pdf_b = gerar_pdf_estudo(u_cliente, u_opp, "Engenharia", res_list, {}, {}, b_dados, buf)
    st.download_button("📄 Baixar Relatório V47", data=pdf_b, file_name=f"Estudo_{u_opp}.pdf")
else:
    st.warning("Preencha Cliente e OPP para liberar o PDF.")
