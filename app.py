import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
from fpdf import FPDF

# 1. Configuração de Página
st.set_page_config(page_title="Dimensionador Micronics V53", layout="wide")

# Função para Gerar PDF
def create_pdf(empresa, projeto, opp, responsavel, cidade, estado, resultados_df, vol_dia, fluxo_h, pico, sg):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "CLEANOVA MICRONICS - MEMORIAL DE CALCULO", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(190, 10, f"Empresa: {empresa}")
    pdf.ln(7)
    pdf.cell(190, 10, f"Projeto: {projeto} | OPP: {opp}", ln=True)
    pdf.cell(190, 10, f"Responsavel: {responsavel}", ln=True)
    pdf.cell(190, 10, f"Localidade: {cidade}/{estado}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "RESUMO OPERACIONAL", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"- Volume de Lodo/Dia: {vol_dia:.2f} m3/dia", ln=True)
    pdf.cell(190, 8, f"- Taxa de Fluxo: {fluxo_h:.2f} m3/h", ln=True)
    pdf.cell(190, 8, f"- Vazao de Pico: {pico:,.0f} L/h", ln=True)
    pdf.cell(190, 8, f"- Grav. Especifica: {sg:.3f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "TABELA DE SELECAO", ln=True)
    pdf.set_font("Arial", "", 10)
    for index, row in resultados_df.iterrows():
        pdf.cell(190, 8, f"{row['Equipamento']} | Placas: {row['Qtd Placas']} | Area: {row['Área Total (m²)']} m2 | Taxa: {row['Taxa (kg/m².h)']}", ln=True)
    return pdf.output(dest="S").encode("latin-1")

def main():
    # Cabeçalho Técnico
    st.markdown("""
    <div style="background-color:#003366;padding:20px;border-radius:10px;margin-bottom:20px">
    <h1 style="color:white;text-align:center;margin:0;">CLEANOVA MICRONICS - DIMENSIONADOR V53</h1>
    <p style="color:white;text-align:center;margin:5px;">Memorial de Cálculo de Engenharia | Responsável: Eder</p>
    </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR COMPLETA RESTAURADA ---
    st.sidebar.header("📋 Identificação do Projeto")
    empresa = st.sidebar.text_input("**Empresa**", value="")
    nome_projeto = st.sidebar.text_input("**Nome do Projeto**", value="")
    num_opp = st.sidebar.text_input("**N° de OPP**", value="")
    
    mercados = sorted(["Mineração", "Químico", "Farmacêutico", "Cervejaria", "Sucos", "Fertilizantes", "Outros"])
    mercado_sel = st.sidebar.selectbox("**Mercado**", mercados)
    
    produtos = sorted(["Concentrado de Cobre", "Rejeito de Cobre", "Concentrado de Ferro", "Efluente Industrial", "Lodo Biológico", "Concentrado de Grafite", "Rejeito de Grafite", "Terras Raras", "Outros"])
    produto_sel = st.sidebar.selectbox("**Produto**", produtos)
    
    responsavel = st.sidebar.text_input("**Responsável pelo Projeto**", value="")
    
    col_cid, col_est = st.sidebar.columns(2)
    cidade = col_cid.text_input("**Cidade**", value="")
    estados_br = sorted(["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
    estado = col_est.selectbox("**Estado**", estados_br, index=estados_br.index("SP"))

    st.sidebar.divider()
    st.sidebar.header("📥 **Parâmetros de Processo**")
    prod_seca_dia = st.sidebar.number_input("**Peso total dos Sólidos (T/Dia)**", value=0.0)
    disponibilidade_perc = st.sidebar.slider("**Disponibilidade de Equipamento (%)**", 1, 100, 85)
    disponibilidade_h = (disponibilidade_perc / 100) * 24
    
    # Automação da Massa Seca horária exposta na sidebar
    prod_seca_hora = prod_seca_dia / disponibilidade_h if disponibilidade_h > 0 else 0
    st.sidebar.info(f"⚖️ **Massa Seca (t/h):** {prod_seca_hora:.3f}")
    
    vol_lodo_dia_input = st.sidebar.number_input("**Volume de lodo/dia (m³)**", value=0.0)
    conc_solidos = st.sidebar.number_input("**Conc. Sólidos (%w/w)**", value=0.0)
    umidade_torta = st.sidebar.number_input("**Umidade Final da Torta (%)**", value=20.0)

    st.sidebar.divider()
    st.sidebar.header("🧬 **Densidade e Geometria**")
    sg_solido = st.sidebar.number_input("**SG Sólido (g/cm³)**", value=2.70, format="%.2f")
    espessura_camara = st.sidebar.number_input("**Espessura da Câmara (mm)**", value=40, step=1)
    
    st.sidebar.divider()
    st.sidebar.header("🔄 **Ciclos e Operação**")
    vida_util_lona = st.sidebar.number_input("**Vida Útil da Lona (Ciclos)**", value=2000)
    tempo_ciclo_min = st.sidebar.number_input("**Tempo de Ciclo (min)**", value=60)
    custo_kwh_hora = st.sidebar.number_input("**Custo do KWH por hora (R$/h)**", value=0.0)
    pressao_operacao = st.sidebar.slider("**Pressão de Filtração (Bar)**", 1, 15, 6)

    # --- NÚCLEO DE CÁLCULO ---
    try:
        sg_lodo = 100 / ((conc_solidos / sg_solido) + (100 - conc_solidos)) if conc_solidos > 0 else 0
        massa_polpa_hora = prod_seca_hora / (conc_solidos / 100) if conc_solidos > 0 else 0
        taxa_fluxo_lodo_m3h = massa_polpa_hora / sg_lodo if sg_lodo > 0 else 0
        vol_lodo_dia_calc = taxa_fluxo_lodo_m3h * disponibilidade_h
        vazao_pico_lh = (taxa_fluxo_lodo_m3h * 1000) * 1.3
        ciclos_dia = (disponibilidade_h * 60) / tempo_ciclo_min if tempo_ciclo_min > 0 else 0
        
        massa_torta_ciclo = (prod_seca_hora * (tempo_ciclo_min / 60)) / (1 - (umidade_torta / 100))
        vol_torta_ciclo_m3 = massa_torta_ciclo / 1.8 
    except:
        sg_lodo = taxa_fluxo_lodo_m3h = vol_lodo_dia_calc = vazao_pico_lh = vol_torta_ciclo_m3 = 0.0

    # --- PAINEL PRINCIPAL ---
    st.write(f"### 🚀 Resumo Operacional")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.info(f"**Vol. Lodo/Dia**\n\n {vol_lodo_dia_calc:.2f} m³/dia")
    with c2: st.info(f"**Taxa Fluxo Lodo**\n\n {taxa_fluxo_lodo_m3h:.2f} m³/h")
    with c3: st.info(f"**Vazão Pico**\n\n {vazao_pico_lh:,.0f} L/h")
    with c4: st.info(f"**SG Lodo**\n\n {sg_lodo:.3f}")

    st.divider()

    st.write("### Dimensionamento de equipamento")
    mapa_filtros = [
        {"Modelo": "470mm", "Vol_Placa": 5.0, "Area_Placa": 0.40, "Limite": 80},
        {"Modelo": "630mm", "Vol_Placa": 11.5, "Area_Placa": 0.70, "Limite": 90},
        {"Modelo": "800mm", "Vol_Placa": 15.0, "Area_Placa": 1.10, "Limite": 100},
        {"Modelo": "1000mm", "Vol_Placa": 25.0, "Area_Placa": 1.80, "Limite": 100},
        {"Modelo": "1200mm", "Vol_Placa": 45.0, "Area_Placa": 2.60, "Limite": 100},
        {"Modelo": "1500mm", "Vol_Placa": 80.0, "Area_Placa": 4.10, "Limite": 150},
        {"Modelo": "2000mm", "Vol_Placa": 150.0, "Area_Placa": 7.50, "Limite": 180},
        {"Modelo": "2500mm", "Vol_Placa": 250.0, "Area_Placa": 12.00, "Limite": 180},
    ]

    lista_exibicao = []
    primeira_fora = False
    for f in mapa_filtros:
        num_placas = math.ceil((vol_torta_ciclo_m3 * 1000) / f["Vol_Placa"]) if vol_torta_ciclo_m3 > 0 else 0
        area_total = num_placas * f["Area_Placa"]
        taxa_filt = (prod_seca_hora * 1000) / area_total if area_total > 0 else 0
        
        excede = num_placas > f["Limite"]
        item = {"Equipamento": f["Modelo"], "Qtd Placas": str(num_placas) if not excede else f"⚠ {num_placas} (Excede {f['Limite']})", "Área Total (m²)": round(area_total, 2), "Taxa (kg/m².h)": round(taxa_filt, 2)}

        if not excede:
            lista_exibicao.append(item)
        elif not primeira_fora:
            lista_exibicao.append(item)
            primeira_fora = True
            break

    st.table(pd.DataFrame(lista_exibicao))

    # --- GRÁFICO DUAS LINHAS ---
    st.divider()
    col_graph, col_stats = st.columns([2, 1])
    with col_graph:
        st.subheader("📊 Gráfico de Performance e Saturação")
        t = np.linspace(0, tempo_ciclo_min if tempo_ciclo_min > 0 else 60, 100)
        v_acumulado = np.sqrt(t * (taxa_fluxo_lodo_m3h * 1.5)) if taxa_fluxo_lodo_m3h > 0 else np.zeros(100)
        v_setpoint = np.full(100, vol_torta_ciclo_m3) if vol_torta_ciclo_m3 > 0 else np.zeros(100)
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(t, v_acumulado, label="Volume Filtrado Acumulado", color="#003366", linewidth=2.5)
        ax.plot(t, v_setpoint, label="Capacidade Máxima da Câmara", color="#FF0000", linestyle="--", linewidth=2)
        ax.set_xlabel("Tempo de Ciclo (min)"); ax.set_ylabel("Volume (m³)"); ax.legend(); ax.grid(True, alpha=0.2)
        st.pyplot(fig)

    with col_stats:
        st.subheader("⚙️ Status")
        st.write(f"**Ciclos Diários:** {ciclos_dia:.1f}")
        tipo_bomba = "PEMO" if pressao_operacao <= 6 else "WARMAN"
        st.success(f"**Bomba:** {tipo_bomba}")
        st.info(f"**Pressão:** {pressao_operacao} Bar")

    # PDF
    try:
        pdf_data = create_pdf(empresa, nome_projeto, num_opp, responsavel, cidade, estado, pd.DataFrame(lista_exibicao), vol_lodo_dia_calc, taxa_fluxo_lodo_m3h, vazao_pico_lh, sg_lodo)
        st.sidebar.download_button(label="📥 Relatório PDF", data=pdf_data, file_name=f"Memorial_{num_opp}.pdf", mime="application/pdf")
    except: pass

if __name__ == "__main__":
    main()
