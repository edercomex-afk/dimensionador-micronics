import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np

# 1. Configuração de Página
st.set_page_config(page_title="Dimensionador Micronics V53", layout="wide")

def main():
    # Cabeçalho Técnico (Banner Azul)
    st.markdown("""
    <div style="background-color:#003366;padding:20px;border-radius:10px;margin-bottom:20px">
    <h1 style="color:white;text-align:center;margin:0;">CLEANOVA MICRONICS - DIMENSIONADOR V53</h1>
    <p style="color:white;text-align:center;margin:5px;">Memorial de Cálculo de Engenharia | Responsável: Eder</p>
    </div>
    """, unsafe_allow_html=True)

    # Listas de Seleção
    estados_br = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
                  "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
    
    mercados = ["Mineração", "Químico", "Farmacêutico", "Cervejaria", "Sucos", "Fertilizantes", "Outros"]

    # --- SIDEBAR (IDENTIFICAÇÃO COM TÍTULOS EM NEGRITO E CAMPOS VAZIOS) ---
    st.sidebar.header("📋 Identificação do Projeto")
    empresa = st.sidebar.text_input("**Empresa**", value="")
    nome_projeto = st.sidebar.text_input("**Nome do Projeto**", value="")
    num_opp = st.sidebar.text_input("**N° de OPP**", value="")
    
    mercado_sel = st.sidebar.selectbox("**Mercado**", mercados)
    responsavel = st.sidebar.text_input("**Responsável pelo Projeto**", value="")
    
    col_cid, col_est = st.sidebar.columns(2)
    cidade = col_cid.text_input("**Cidade**", value="")
    estado = col_est.selectbox("**Estado**", estados_br, index=24) # SP Padrão

    st.sidebar.divider()
    st.sidebar.header("📥 **Parâmetros de Processo**")
    prod_seca_dia = st.sidebar.number_input("**Massa Seca (t/Dia)**", value=0.0)
    prod_seca_hora = st.sidebar.number_input("**Massa Seca (t/h)**", value=0.0)
    vol_lodo_dia_input = st.sidebar.number_input("**Volume de lodo/dia (m³)**", value=0.0)
    disponibilidade_h = st.sidebar.slider("**Disponibilidade de Equipamento (h/dia)**", 1, 24, 20)
    conc_solidos = st.sidebar.number_input("**Conc. Sólidos (%w/w)**", value=0.0)
    
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
        trocas_lona_ano = (ciclos_dia * 365) / vida_util_lona if vida_util_lona > 0 else 0
        custo_energia_diario = disponibilidade_h * custo_kwh_hora
    except:
        sg_lodo = taxa_fluxo_lodo_m3h = vol_lodo_dia_calc = vazao_pico_lh = 0.0

    # --- CARDS DE RESUMO OPERACIONAL ---
    st.write(f"### 🚀 Resumo Operacional: {empresa if empresa else '---'} - {nome_projeto if nome_projeto else '---'}")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.info(f"**Vol. Lodo/Dia (Calc)**\n\n {vol_lodo_dia_calc:.2f} m³/dia")
    with c2: st.info(f"**Taxa Fluxo Lodo**\n\n {taxa_fluxo_lodo_m3h:.2f} m³/h")
    with c3: st.info(f"**Vazão Pico**\n\n {vazao_pico_lh:,.0f} L/h")
    with c4: st.info(f"**Grav. Específica Lodo**\n\n {sg_lodo:.3f}")

    st.divider()

    # --- TABELA DE SELEÇÃO DE FILTROS ---
    vol_torta_ciclo_m3 = (prod_seca_hora * (tempo_ciclo_min/60)) / 1.8 if prod_seca_hora > 0 else 0
    mapa_filtros = [
        {"Modelo": "800mm", "Vol_Placa": 15, "Area_Placa": 1.1},
        {"Modelo": "1000mm", "Vol_Placa": 25, "Area_Placa": 1.8},
        {"Modelo": "1200mm", "Vol_Placa": 45, "Area_Placa": 2.6},
        {"Modelo": "1500mm", "Vol_Placa": 80, "Area_Placa": 4.1},
        {"Modelo": "2000mm", "Vol_Placa": 150, "Area_Placa": 7.5},
    ]

    selecao_final = []
    for f in mapa_filtros:
        num_placas = math.ceil((vol_torta_ciclo_m3 * 1000) / f["Vol_Placa"]) if vol_torta_ciclo_m3 > 0 else 0
        area_total = num_placas * f["Area_Placa"]
        taxa_filt = (prod_seca_hora * 1000) / area_total if area_total > 0 else 0
        selecao_final.append({
            "Equipamento": f["Modelo"],
            "Qtd Placas": int(num_placas),
            "Área Total (m²)": round(area_total, 2),
            "Taxa (kg/m².h)": round(taxa_filt, 2)
        })

    # --- LAYOUT DE ABAS ---
    tab1, tab2 = st.tabs(["📋 Seleção e Dimensionamento", "📉 Performance Dinâmica & OPEX"])

    with tab1:
        # Removidas as informações redundantes que apareciam aqui
        st.write("### Dimensionamento de Ativos")
        st.table(pd.DataFrame(selecao_final))
        tipo_bomba = "PEMO" if pressao_operacao <= 6 else "WARMAN"
        st.success(f"Hardware Sugerido: Bomba **{tipo_bomba}** para operação em {pressao_operacao} Bar.")

    with tab2:
        col_perf, col_opex = st.columns(2)
        
        with col_perf:
            st.subheader("📈 Performance Dinâmica Estimada")
            if taxa_fluxo_lodo_m3h > 0:
                t = np.linspace(1, tempo_ciclo_min, 50)
                v_acumulado = np.sqrt(t * (taxa_fluxo_lodo_m3h * 2)) 
                fig_perf, ax_perf = plt.subplots()
                ax_perf.plot(t, v_acumulado, color='#003366', linewidth=2)
                ax_perf.set_xlabel("Tempo de Ciclo (min)")
                ax_perf.set_ylabel("Volume Acumulado (m³)")
                ax_perf.grid(True, alpha=0.3)
                st.pyplot(fig_perf)
            else:
                st.write("Insira os parâmetros de processo para visualizar a performance.")

        with col_opex:
            st.subheader("Custos e Ciclos")
            st.write(f"**Responsável:** {responsavel if responsavel else '---'}")
            st.write(f"**Ciclos Diários:** {ciclos_dia:.1f}")
            st.write(f"**Custo Energia/Dia:** R$ {custo_energia_diario:.2f}")
            fig2, ax2 = plt.subplots(figsize=(4, 4))
            ax2.pie([50, 25, 25], labels=['Energia', 'Lonas', 'Manut'], autopct='%1.1f%%', colors=['#003366', '#ff9900', '#c0c0c0'])
            st.pyplot(fig2)

if __name__ == "__main__":
    main()
