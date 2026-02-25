import streamlit as st
import pandas as pd
import math
import numpy as np
from fpdf import FPDF

# 1. Configuração de Página
st.set_page_config(page_title="Cleanova Micronics | V53.6", layout="wide")

def main():
    # Cabeçalho Técnico
    st.markdown("""
    <div style="background-color:#003366;padding:20px;border-radius:10px;margin-bottom:20px">
    <h1 style="color:white;text-align:center;margin:0;">CLEANOVA MICRONICS - DIMENSIONADOR V53</h1>
    <p style="color:white;text-align:center;margin:5px;">Memorial de Cálculo de Engenharia | Lógica de Placas Atualizada</p>
    </div>
    """, unsafe_allow_html=True)

    # --- CONFIGURAÇÃO TÉCNICA DOS FILTROS (CONFORME SOLICITADO) ---
    # Adicionamos os volumes médios por placa para cada tamanho para viabilizar o cálculo
    config_filtros = [
        {"Modelo": "470 x 470 mm", "Vol_Placa": 3.5, "Area_Placa": 0.38, "Min_Placas": 1, "Max_Placas": 36},
        {"Modelo": "630 x 630 mm", "Vol_Placa": 7.5, "Area_Placa": 0.68, "Min_Placas": 14, "Max_Placas": 40},
        {"Modelo": "800 x 800 mm", "Vol_Placa": 15.0, "Area_Placa": 1.10, "Min_Placas": 20, "Max_Placas": 60},
        {"Modelo": "1000 x 1000 mm", "Vol_Placa": 25.0, "Area_Placa": 1.80, "Min_Placas": 30, "Max_Placas": 80},
        {"Modelo": "1200 x 1200 mm", "Vol_Placa": 45.0, "Area_Placa": 2.60, "Min_Placas": 40, "Max_Placas": 100},
        {"Modelo": "1500 x 1500 mm", "Vol_Placa": 80.0, "Area_Placa": 4.10, "Min_Placas": 60, "Max_Placas": 120},
        {"Modelo": "2000 x 2000 mm", "Vol_Placa": 150.0, "Area_Placa": 7.50, "Min_Placas": 80, "Max_Placas": 180},
        {"Modelo": "2500 x 2500 mm", "Vol_Placa": 250.0, "Area_Placa": 12.00, "Min_Placas": 100, "Max_Placas": 180},
    ]

    # --- SIDEBAR ---
    st.sidebar.header("📋 Identificação do Projeto")
    empresa = st.sidebar.text_input("Empresa", value="")
    nome_projeto = st.sidebar.text_input("Nome do Projeto", value="")
    num_opp = st.sidebar.text_input("N° de OPP", value="")
    produto_sel = st.sidebar.selectbox("Produto", ["Concentrado de cobre", "Carbonato de Lítio", "Concentrado de Ferro", "Concentrado de Ouro", "Terras Raras", "Concentrado de Níquel", "Rejeito de terras raras", "Rejeito de Minério de Ferro", "Rejeito de Cobre", "Efluente industrial", "Lodo Biológico", "Massa Negra", "Concentrado de Zinco", "Lama Vermelha", "Outros"])
    vendedor_resp = st.sidebar.text_input("Vendedor Responsável", value="")
    
    st.sidebar.divider()
    st.sidebar.header("📥 Parâmetros de Processo")
    prod_seca_hora = st.sidebar.number_input("Massa Seca (t/h)", value=0.0)
    vol_lodo_hora_input = st.sidebar.number_input("Volume de lodo/hora (m³/h)", value=0.0)
    disponibilidade_h = st.sidebar.slider("Disponibilidade (h/dia)", 1, 24, 20)
    conc_solidos = st.sidebar.number_input("Conc. Sólidos (%w/w)", value=0.0)
    sg_solido = st.sidebar.number_input("Gravidade específica (g/cm³)", value=2.70)
    tempo_ciclo_min = st.sidebar.number_input("Tempo de Ciclo (min)", value=60)

    # --- NÚCLEO DE CÁLCULO ---
    try:
        sg_lodo = 100 / ((conc_solidos / sg_solido) + (100 - conc_solidos)) if conc_solidos > 0 else 1.0
        taxa_fluxo = vol_lodo_hora_input if vol_lodo_hora_input > 0 else (prod_seca_hora / (conc_solidos/100) / sg_lodo if conc_solidos > 0 else 0)
        vol_torta_ciclo_m3 = (taxa_fluxo * (tempo_ciclo_min/60)) * (conc_solidos/100) * (sg_lodo/1.8) if taxa_fluxo > 0 else 0
    except:
        taxa_fluxo = vol_torta_ciclo_m3 = 0.0

    # --- ABAS ---
    tab1, tab2 = st.tabs(["📋 Seleção de Ativos", "⚙️ Configuração dos Limites"])

    with tab1:
        st.write(f"### Filtros Sugeridos para: {produto_sel}")
        
        sugestoes = []
        for f in config_filtros:
            qtd_placas = math.ceil((vol_torta_ciclo_m3 * 1000) / f["Vol_Placa"]) if vol_torta_ciclo_m3 > 0 else 0
            
            # APLICAÇÃO DA LÓGICA DE FILTRAGEM (MIN/MAX)
            if f["Min_Placas"] <= qtd_placas <= f["Max_Placas"]:
                area_total = qtd_placas * f["Area_Placa"]
                sugestoes.append({
                    "Modelo": f["Modelo"],
                    "Placas Sugeridas": int(qtd_placas),
                    "Área Total (m²)": round(area_total, 2),
                    "Status": "✅ Adequado"
                })

        if sugestoes:
            st.table(pd.DataFrame(sugestoes))
        else:
            st.warning("Nenhum modelo se encaixa nos limites de placas para este volume. Tente ajustar o tempo de ciclo ou a massa seca.")

    with tab2:
        st.subheader("Tabela de Referência: Limites por Modelo")
        st.write("Esta é a lógica de restrição aplicada na aba de seleção:")
        df_limites = pd.DataFrame(config_filtros)[["Modelo", "Min_Placas", "Max_Placas"]]
        df_limites.columns = ["Tamanho do Filtro", "Qtd Mínima", "Qtd Máxima"]
        st.table(df_limites)

if __name__ == "__main__":
    main()
