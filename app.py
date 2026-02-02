import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import io

# 1. Configuração da página
st.set_page_config(page_title="Cleanova Micronics | V54.8 Master", layout="wide")

# --- FUNÇÕES AUXILIARES ---
def clean_txt(text):
    return str(text).encode('latin-1', 'ignore').decode('latin-1')

def validar_taxa(taxa_calc, material_selecionado):
    referencias = {
        "Cobre": 300, "Efluente industrial": 50, "Ferro": 450, "Grafite": 150, 
        "Lama Vermelha": 60, "Litio": 120, "Niquel": 250, "Ouro": 200, 
        "Rejeito de Cobre": 180, "Rejeito de Ferro": 220, "Rejeito de Grafite": 110,
        "Rejeito de ouro": 150, "Rejeito de terras raras": 90, "Terras Raras": 100
    }
    limite = referencias.get(material_selecionado, 100)
    if taxa_calc <= limite:
        return "✅ Segura", "Dimensionamento robusto.", "green"
    elif taxa_calc <= limite * 1.3:
        return "🟡 Atencao", "Taxa agressiva. Exige polimeros.", "orange"
    else:
        return "🔴 Critica", "Risco de torta umida. Aumente o filtro.", "red"

def gerar_grafico(pressao_alvo, vazao_pico):
    tempo = np.linspace(0, 45, 100)
    pressao = pressao_alvo * (1 - np.exp(-0.15 * tempo))
    vazao = vazao_pico * np.exp(-0.12 * tempo)
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.set_xlabel('Tempo (min)')
    ax1.set_ylabel('Pressao (Bar)', color='tab:red')
    ax1.plot(tempo, pressao, color='tab:red', linewidth=3)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Vazao (L/h)', color='tab:blue')
    ax2.plot(tempo, vazao, color='tab:blue', linewidth=3)
    plt.title("Curva de Performance: Filtro e Bomba")
    fig.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=120)
    plt.close(fig)
    img_buf.seek(0)
    return img_buf

# --- FUNÇÃO PDF ---
def gerar_pdf_final(d_cli, res_list, opex_detalhe, bomba, img_graf, diagnostico, taxa):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, clean_txt("ESTUDO TECNICO DE FILTRACAO - V54.8"), ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 7, clean_txt(f"Cliente: {d_cli['cliente']}"), 1)
    pdf.cell(95, 7, clean_txt(f"OPP: {d_cli['opp']}"), 1, ln=True)
    pdf.cell(63, 7, clean_txt(f"Material: {d_cli['produto']}"), 1)
    pdf.cell(63, 7, clean_txt(f"Mercado: {d_cli['mercado']}"), 1)
    pdf.cell(64, 7, clean_txt(f"Estado: {d_cli['estado']}"), 1, ln=True) # Estado no PDF
    pdf.cell(190, 7, clean_txt(f"Responsavel: {d_cli['resp']}"), 1, ln=True)
    pdf.ln(5)

    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 8, clean_txt(f"TAXA: {taxa:.1f} kg/m2.h | STATUS: {diagnostico}"), ln=True, fill=True)
    pdf.ln(5)

    with open("temp_v548.png", "wb") as f: f.write(img_graf.getbuffer())
    pdf.image("temp_v548.png", x=25, y=None, w=160)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 9)
    pdf.cell(45, 8, "Modelo", 1); pdf.cell(25, 8, "Placas", 1); pdf.cell(35, 8, "Area (m2)", 1); pdf.cell(85, 8, "Status", 1, ln=True)
    pdf.set_font("Arial", "", 9)
    for r in res_list:
        pdf.cell(45, 8, clean_txt(r["Modelo (mm)"]), 1)
        pdf.cell(25, 8, str(r["Placas"]), 1)
        pdf.cell(35, 8, f"{r['Area']:.1f}", 1)
        pdf.cell(85, 8, clean_txt(r["Status"].replace("✅", "OK").replace("❌", "Limite")), 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, clean_txt(f"OPEX Total Estimado: R$ {opex_detalhe['total']:,.2f}/mes"), ln=True)
    pdf.cell(190, 8, clean_txt(f"Bomba Recomendada: {bomba}"), ln=True)
    return pdf.output(dest="S").encode("latin-1", "ignore")

# --- INTERFACE ---
st.title("Cleanova Micronics | Dimensionador V54.8")

# Cabeçalho - Linha 1
c1, c2, c3 = st.columns(3)
u_cliente = c1.text_input("**Cliente**")
u_projeto = c2.text_input("**Projeto**")
u_opp = c3.text_input("**Numero da OPP**")

# Cabeçalho - Linha 2
c4, c5, c6 = st.columns(3)
u_produto = c4.selectbox("**Material de Referencia**", sorted([
    "Cobre", "Efluente industrial", "Ferro", "Grafite", "Lama Vermelha", 
    "Litio", "Niquel", "Ouro", "Rejeito de Cobre", "Rejeito de Ferro", 
    "Rejeito de Grafite", "Rejeito de ouro", "Rejeito de terras raras", "Terras Raras"
]))
u_mercado = c5.selectbox("**Mercado**", sorted([
    "Alimentos", "Bebidas", "Farmáceutico", "Mineração", "Química"
]))
u_resp = c6.text_input("**Responsavel**")

# Cabeçalho - Linha 3 (NOVA)
c7, c8, c9 = st.columns([1, 2, 2]) # Ajuste de proporção para o Estado não ficar gigante
u_estado = c7.selectbox("**Estado**", sorted([
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", 
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", 
    "SP", "SE", "TO"
]))

# Sidebar
st.sidebar.header("🚀 Processo")
solidos_dia = st.sidebar.number_input("Sólidos (t/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade (%)", 0, 100, 90)
tempo_cycle = st.sidebar.number_input("Ciclo (min)", value=45)
vazao_pico = st.sidebar.number_input("Vazão Pico (L/h)", value=50000.0)
sg_solidos = st.sidebar.number_input("SG Sólidos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade (%)", value=20.0)
recesso = st.sidebar.number_input("Recesso (mm)", value=30.0)
pressao_manual = st.sidebar.slider("Pressão (Bar)", 1, 15, 7)

st.sidebar.header("💰 OPEX Config")
custo_kwh = st.sidebar.number_input("Custo Energia (R$/kWh)", value=0.65)
custo_lona_un = st.sidebar.number_input("Preço Lona (R$/unid)", value=450.0)
vida_lona_ciclos = st.sidebar.number_input("Vida útil lona (Ciclos)", value=2000)

# CÁLCULOS (Lógica mantida)
umidade = umidade_input / 100
disp_h = 24 * (utilizacao_pct / 100)
ciclos_dia = (disp_h * 60) / tempo_cycle if tempo_cycle > 0 else 0
massa_seco_ciclo = (solidos_dia * 1000) / ciclos_dia if ciclos_dia > 0 else 0
dens_torta = 1 / (((1 - umidade) / sg_solidos) + (umidade / 1.0)) if sg_solidos > 0 else 1
vol_req = ((massa_seco_ciclo / (1 - umidade)) / dens_torta)

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
    status = "✅ OK" if n_placas <= p["max"] else "❌ Limite"
    if status == "✅ OK" or not exibiu_erro:
        res_list.append({"Modelo (mm)": f"{p['nom']}x{p['nom']}", "Placas": n_placas, "Area": n_placas * p["area_ref"], "Status": status})
        if "❌" in status: exibiu_erro = True

# TAXA E OPEX
area_sel = res_list[0]["Area"] if res_list else 1
taxa_calc = massa_seco_ciclo / (area_sel * (tempo_cycle / 60))
status_t, msg_t, cor_t = validar_taxa(taxa_calc, u_produto)

energia_mes = (20 * disp_h * 30) * custo_kwh
n_placas_ref = res_list[0]["Placas"] if res_list else 0
lonas_mes = ((ciclos_dia * 30) / vida_lona_ciclos) * (n_placas_ref * 2) * custo_lona_un
total_opex = energia_mes + lonas_mes
marca_bomba = "PEMO (Italia)" if pressao_manual <= 6 else "WEIR (Warman/GEHO)"

# EXIBIÇÃO
st.table(res_list)
st.markdown(f"### Diagnostico para {u_produto}: :{cor_t}[{status_t}] - {taxa_calc:.1f} kg/m2.h")

col_g, col_o = st.columns([2, 1])
with col_g:
    buf = gerar_grafico(pressao_manual, vazao_pico)
    st.image(buf)
with col_o:
    st.info(f"⚡ Energia: R$ {energia_mes:,.2f}")
    st.info(f"🧵 Lonas: R$ {lonas_mes:,.2f}")
    st.success(f"💰 Total OPEX: R$ {total_opex:,.2f}")
    st.markdown(f"**Bomba:** {marca_bomba}")

st.markdown("---")
if st.button("📄 Gerar Relatorio Tecnico PDF"):
    if u_cliente and u_opp and u_resp:
        d_c = {"cliente": u_cliente, "projeto": u_projeto, "opp": u_opp, "resp": u_resp, "produto": u_produto, "mercado": u_mercado, "estado": u_estado}
        pdf_b = gerar_pdf_final(d_c, res_list, {"total": total_opex}, marca_bomba, buf, status_t, taxa_calc)
        st.download_button("⬇️ Baixar Estudo", data=pdf_b, file_name=f"Estudo_Micronics_{u_opp}.pdf")
    else:
        st.error("Preencha os campos obrigatórios no cabeçalho.")
