import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import io

# 1. Configuração da página
st.set_page_config(page_title="Cleanova Micronics | V54.2 Final", layout="wide")

# --- FUNÇÕES AUXILIARES ---
def clean_txt(text):
    return str(text).encode('latin-1', 'ignore').decode('latin-1')

def validar_taxa(taxa_calc, material_selecionado):
    referencias = {"Ferro": 450, "Rejeito": 220, "Litio": 120, "Quimico": 50, "Biologico": 10}
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
    pdf.cell(190, 10, clean_txt("ESTUDO TECNICO DE FILTRACAO - V54"), ln=True, align="C")
    pdf.ln(5)
    
    # Dados Cliente
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 7, clean_txt(f"Cliente: {d_cli['cliente']}"), 1)
    pdf.cell(95, 7, clean_txt(f"OPP: {d_cli['opp']}"), 1, ln=True)
    pdf.cell(95, 7, clean_txt(f"Produto: {d_cli['produto']}"), 1)
    pdf.cell(95, 7, clean_txt(f"Responsavel: {d_cli['resp']}"), 1, ln=True)
    pdf.ln(5)

    # Diagnóstico
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 8, clean_txt(f"TAXA CALCULADA: {taxa:.1f} kg/m2.h | STATUS: {diagnostico}"), ln=True, fill=True)
    pdf.ln(5)

    # Imagem Gráfico
    img_path = "temp_v54_final.png"
    with open(img_path, "wb") as f:
        f.write(img_graf.getbuffer())
    pdf.image(img_path, x=25, y=None, w=160)
    pdf.ln(5)

    # Tabela de Modelos
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
    pdf.cell(190, 8, clean_txt(f"Resumo OPEX: R$ {opex_detalhe['total']:,.2f}/mes"), ln=True)
    pdf.cell(190, 8, clean_txt(f"Bomba Recomendada: {bomba}"), ln=True)

    return pdf.output(dest="S").encode("latin-1", "ignore")

# --- INTERFACE ---
st.title("Cleanova Micronics | Dimensionador V54.2")

# Cabeçalho
c1, c2, c3 = st.columns(3)
u_cliente = c1.text_input("**Cliente**")
u_projeto = c2.text_input("**Projeto**")
u_opp = c3.text_input("**Numero da OPP**")

c4, c5, c6 = st.columns(3)
u_produto = c4.selectbox("**Material de Referencia**", ["Ferro", "Rejeito", "Litio", "Quimico", "Biologico"])
u_mercado = c5.text_input("**Mercado**")
u_resp = c6.text_input("**Responsavel**")

# Sidebar
st.sidebar.header("🚀 Parametros")
solidos_dia = st.sidebar.number_input("Sólidos (t/dia)", value=100.0)
utilizacao_pct = st.sidebar.slider("Disponibilidade (%)", 0, 100, 90)
tempo_cycle = st.sidebar.number_input("Ciclo (min)", value=45)
vazao_pico = st.sidebar.number_input("Vazão Pico (L/h)", value=50000.0)
sg_solidos = st.sidebar.number_input("SG Sólidos", value=2.8)
umidade_input = st.sidebar.number_input("Umidade (%)", value=20.0)
recesso = st.sidebar.number_input("Recesso (mm)", value=30.0)
pressao_manual = st.sidebar.slider("Pressão (Bar)", 1, 15, 7)

# CÁLCULOS
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

# TAXA E OPEX DETALHADO
area_sel = res_list[0]["Area"] if res_list else 1
taxa_calc = massa_seco_ciclo / (area_sel * (tempo_cycle / 60))
status_t, msg_t, cor_t = validar_taxa(taxa_calc, u_produto)

energia_mes = (20 * disp_h * 30) * 0.65
n_placas_ref = res_list[0]["Placas"] if res_list else 0
lonas_mes = ((ciclos_dia * 30) / 2000) * (n_placas_ref * 2) * 450.0
total_opex = energia_mes + lonas_mes
marca_bomba = "PEMO (Italia)" if pressao_manual <= 6 else "WEIR (Warman/GEHO)"

# EXIBIÇÃO FINAL
st.subheader("📋 Dimensionamento Sugerido")
st.table(res_list)

st.markdown(f"### Diagnóstico Micronics: :{cor_t}[{status_t}] - {taxa_calc:.1f} kg/m².h")
st.info(msg_t)

col_g, col_o = st.columns([2, 1])
with col_g:
    buf = gerar_grafico(pressao_manual, vazao_pico)
    st.image(buf)
with col_o:
    # Mostrando as 3 informações de OPEX como solicitado
    st.info(f"⚡ Energia: R$ {energia_mes:,.2f}")
    st.info(f"🧵 Lonas: R$ {lonas_mes:,.2f}")
    st.success(f"💰 Total OPEX: R$ {total_opex:,.2f}")
    st.markdown(f"**Bomba:** {marca_bomba}")

st.markdown("---")
# Botão do PDF (sempre visível, mas valida os campos ao clicar)
if st.button("📄 Gerar Relatório Técnico PDF"):
    if u_cliente and u_opp and u_resp:
        d_c = {"cliente": u_cliente, "projeto": u_projeto, "opp": u_opp, "resp": u_resp, "produto": u_produto}
        opex_d = {"total": total_opex, "energia": energia_mes, "lonas": lonas_mes}
        pdf_b = gerar_pdf_final(d_c, res_list, opex_d, marca_bomba, buf, status_t, taxa_calc)
        st.download_button("⬇️ Baixar Estudo Técnico", data=pdf_b, file_name=f"Estudo_Micronics_{u_opp}.pdf", mime="application/pdf")
    else:
        st.error("Por favor, preencha os campos 'Cliente', 'Numero da OPP' e 'Responsavel' no cabeçalho.")
