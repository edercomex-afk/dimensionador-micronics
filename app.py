import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

# 1. Configuração de Página
st.set_page_config(page_title="Dimensionador Micronics V53", layout="wide")

def main():
    # Cabeçalho Técnico Restaurado (Versão Eder)
    st.markdown("""
    <div style="background-color:#003366;padding:20px;border-radius:10px;margin-bottom:20px">
    <h1 style="color:white;text-align:center;margin:0;">CLEANOVA MICRONICS - DIMENSIONADOR V53</h1>
    <p style="color:white;text-align:center;margin:5px;">Memorial de Cálculo de Engenharia | Responsável: Eder</p>
    </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR (INPUTS ORIGINAIS V53) ---
    st.sidebar.header("📥 Parâmetros de Processo")
    prod_seca = st.sidebar.number_input("Massa Seca (t/h)", value=10.0)
    horas_op = st.sidebar.number_input("Operação (h/dia)", value=20)
    conc_solidos = st.sidebar.number_input("Conc. Sólidos (%w/w)", value=30.0)
    
    st.sidebar.divider()
    st.sidebar.header("🧬 Densidade e Ciclos")
    sg_solido = st.sidebar.number_input("SG Sólido (g/cm³)", value=2.70, format="%.2f")
    vida_util_lona = st.sidebar.number_input("Vida Útil da Lona (Ciclos)", value=2000)
    tempo_ciclo_min = st.sidebar.number_input("Tempo de Ciclo (min)", value=60)
    
    st.sidebar.divider()
    st.sidebar.header("⚙️ Operação")
    pressao_operacao = st.sidebar.slider("Pressão de Filtração (Bar)", 1, 15, 6)

    # --- NÚCLEO DE CÁLCULO (BALANÇO HIDRÁULICO) ---
    # Densidade da polpa (Considerando SG Água = 1.0 fixo internamente)
    rho_polpa = 100 / ((conc_solidos / sg_solido) + (100 - conc_solidos))
    
    # Taxa de fluxo de lodo m³/h
    massa_polpa_hora = prod_seca / (conc_solidos / 100)
    taxa_fluxo_lodo_m3h = massa_polpa_hora / rho_polpa
    
    # Volume de lodo por dia
    vol_lodo_dia = taxa_fluxo_lodo_m3h * horas_op
    
    # Vazão de Pico (L/h)
    vazao_pico_lh = (taxa_fluxo_lodo_m3h * 1000) * 1.3
    
    # Ciclos da lona
    ciclos_dia = (horas_op * 60) / tempo_ciclo_min
    trocas_lona_ano = (ciclos_dia * 365) / vida_util_lona

    # --- TABELA DE SELEÇÃO DE FILTROS (CENTRAL) ---
    # Baseado no volume de torta necessário por ciclo
    vol_torta_ciclo_m3 = (prod_seca * (tempo_ciclo_min/60)) / 1.8 # SG Torta médio fixo 1.8 para seleção

    mapa_filtros = [
        {"Modelo": "800mm", "Vol_Placa": 15, "Area_Placa": 1.1},
        {"Modelo": "1000mm", "Vol_Placa": 25, "Area_Placa": 1.8},
        {"Modelo": "1200mm", "Vol_Placa": 45, "Area_Placa": 2.6},
        {"Modelo": "1500mm", "Vol_Placa": 80, "Area_Placa": 4.1},
        {"Modelo": "2000mm", "Vol_Placa": 150, "Area_Placa": 7.5},
    ]

    selecao_final = []
    for f in mapa_filtros:
        num_placas = math.ceil((vol_torta_ciclo_m3 * 1000) / f["Vol_Placa"])
        area_total = num_placas * f["Area_Placa"]
        taxa_filt = (prod_seca * 1000) / area_total
        selecao_final.append({
            "Equipamento": f["Modelo"],
            "Qtd Placas": int(num_placas),
            "Área Total (m²)": round(area_total, 2),
            "Taxa (kg/m².h)": round(taxa_filt, 2)
        })

    # --- EXPOSIÇÃO DOS DADOS NO LAYOUT ---
    tab1, tab2, tab3 = st.tabs(["📋 Seleção de Filtro", "📈 OPEX & Performance", "📖 Memorial"])

    with tab1:
        st.subheader("Resultados de Fluxo e Seleção de Ativos")
        
        # Métricas em destaque conforme solicitado
        c1, c2, c3 = st.columns(3)
        c1.metric("Volume de Lodo/Dia", f"{vol_lodo_dia:.2f} m³/dia")
        c2.metric("Taxa Fluxo Lodo", f"{taxa_fluxo_lodo_m3h:.2f} m³/h")
        c3.metric("Vazão de Pico", f"{vazao_pico_lh:,.0f} L/h")
        
        st.write("### Tabela de Dimensionamento de Placas")
        st.table(pd.DataFrame(selecao_final))
        
        st.divider()
        tipo_bomba = "PEMO" if pressao_operacao <= 6 else "WARMAN"
        st.info(f"Bomba Sugerida: **{tipo_bomba}** para operação em {pressao_operacao} Bar.")

    with tab2:
        col_opex1, col_opex2 = st.columns(2)
        with col_opex1:
            st.subheader("Vida Útil da Lona")
            st.write(f"**Ciclos Diários:** {ciclos_dia:.1f}")
            st.write(f"**Trocas de Lona/Ano:** {trocas_lona_ano:.2f}")
            
            # Farol de Performance
            fig, ax = plt.subplots(figsize=(6, 2))
            taxa_plot = selecao_final[1]["Taxa (kg/m².h)"] # Referência modelo 1000mm
            ax.barh(["Taxa Filtração"], [taxa_plot], color='green' if taxa_plot < 300 else 'orange')
            ax.set_xlim(0, 600)
            st.pyplot(fig)
            
        with col_opex2:
            st.subheader("Estimativa de OPEX")
            fig2, ax2 = plt.subplots(figsize=(4, 4))
            ax2.pie([50, 25, 25], labels=['Energia', 'Lonas', 'Peças'], autopct='%1.1f%%', colors=['#003366', '#ff9900', '#c0c0c0'])
            st.pyplot(fig2)

    with tab3:
        st.subheader("Memória de Cálculo")
        st.latex(r"Vol_{dia} = Fluxo_{m3/h} \cdot Horas_{op}")
        st.latex(r"Q_{pico} (L/h) = (Fluxo_{m3/h} \cdot 1000) \cdot 1.3")
        st.latex(r"SG_{polpa} = \frac{100}{\frac{C_w}{SG_s} + (100 - C_w)}")

if __name__ == "__main__":
    main()
