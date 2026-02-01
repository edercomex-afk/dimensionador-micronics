import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import io

# 1. Configuração da página
st.set_page_config(page_title="Cleanova Micronics | V45 Pro", layout="wide")

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
    
    plt.title(f"Comportamento Operacional: Bomba & Filtro")
    fig.tight_layout()
    
    # Salvar o gráfico em memória para o PDF
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=150)
    img_buf.seek(0)
    return fig, img_buf

# --- FUNÇÃO PDF V45 (COM IMAGEM DO GRÁFICO) ---
def gerar_pdf_completo(cliente, opp, resp, bomba_dados, img_grafico):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "ESTUDO TECNICO DE FILTRACAO E BOMBEAMENTO", ln=True, align="C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "CLEANOVA MICRONICS", ln=True, align="C")
    pdf.ln(10)
    
    # Dados Gerais
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 8, f"Cliente: {cliente}", 1)
    pdf.cell(95, 8, f"N. OPP: {opp}", 1, ln=True)
    pdf.cell(190, 8, f"Responsavel Tecnico: {resp}", 1, ln=True)
    pdf.ln(5)

    # Especificação da Bomba
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 10, "1. Especificacao da Bomba Homologada", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, f"Marca Sugerida: {bomba_dados['marca']}", ln=True)
    pdf.cell(190, 7, f"Modelo: {bomba_dados['tipo']}", ln=True)
    pdf.cell(190, 7, f"Vazao de Pico: {bomba_dados['vazao']:,.0f} L/h", ln=True)
    pdf.cell(190, 7, f"Pressao de Compactacao: {bomba_dados['pressao']} Bar", ln=True)
    pdf.ln(5)

    # Inserir o Gráfico no PDF
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "2. Curva de Performance (Pressao x Vazao)", ln=True, fill=True)
    
    # Salva o buffer da imagem em um arquivo temporário para o FPDF ler
    with open("temp_chart.png", "wb") as f:
        f.write(img_grafico.getbuffer())
    
    pdf.image("temp_chart.png", x=15, y=None, w=180)
    pdf.ln(5)
    
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(190, 5, "Nota: O grafico acima representa a simulacao teorica do comportamento da bomba selecionada em relacao a resistencia da torta durante um ciclo de 45 minutos.")

    return pdf.output(dest="S").encode("latin-1", "ignore")

# --- INTERFACE PRINCIPAL ---
st.title("Cleanova Micronics | Engenharia de Aplicação V45")
st.markdown("---")

c1, c2, c3 = st.columns(3)
u_cliente = c1.text_input("👤 Nome do Cliente")
u_opp = c2.text_input("🔢 Número da OPP")
u_resp = c3.text_input("👨‍💻 Responsável")

st.sidebar.header("⚙️ Parâmetros de Projeto")
vazao_input = st.sidebar.number_input("Vazão de Pico (L/h)", value=50000.0)
pressao_input = st.sidebar.slider("Pressão de Filtração (Bar)", 1, 15, 7)

# Lógica de Marcas
if pressao_input <= 6:
    marca, tipo = "PEMO (Itália)", "Série AO/AB - Revestida em Borracha"
else:
    marca, tipo = "WEIR (Warman/GEHO)", "Série Warman AH ou GEHO ZPR"

# Geração de Gráfico
fig, buf = gerar_grafico_vazao_pressao(pressao_input, vazao_input)

# Exibição
col_graf, col_info = st.columns([2, 1])
with col_graf:
    st.subheader("📊 Gráfico de Performance")
    st.pyplot(fig)

with col_info:
    st.subheader("🛡️ Bomba Proposta")
    st.success(f"**Marca:** {marca}")
    st.info(f"**Tipo:** {tipo}")
    st.metric("Pressão de Compactação", f"{pressao_input} Bar")
    st.metric("Vazão de Pico", f"{vazao_input:,.0f} L/h")

st.markdown("---")

# Botão de PDF
if u_cliente and u_opp:
    b_dados = {"marca": marca, "tipo": tipo, "pressao": pressao_input, "vazao": vazao_input}
    pdf_bytes = gerar_pdf_completo(u_cliente, u_opp, u_resp, b_dados, buf)
    
    st.download_button(
        label="📄 Baixar Relatório Técnico Profissional (PDF)",
        data=pdf_bytes,
        file_name=f"Proposta_Micronics_{u_opp}.pdf",
        mime="application/pdf"
    )
else:
    st.warning("⚠️ Preencha o Cliente e a OPP para gerar o relatório com gráfico.")
