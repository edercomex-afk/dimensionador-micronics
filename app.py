import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

# 1. Configuração de Página e Sidebar
st.set_page_config(page_title="Dimensionador Micronics V53", layout="wide")

def main():
    # Cabeçalho Técnico
    st.markdown("""
    <div style="background-color:#003366;padding:20px;border-radius:10px;margin-bottom:20px">
    <h1 style="color:white;text-align:center;margin:0;">CLEANOVA MICRONICS - DIMENSIONADOR V53</h1>
    <p style="color:white;text-align:center;margin:5px;">Memorial de Cálculo de Engenharia | Responsável: Eder</p>
    </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR (INPUTS ORIGINAIS) ---
    st.sidebar.header("📥 Dados de Processo")
    prod_seca = st.sidebar.number_input("Massa Seca (t/h)", value=10.0)
    horas_op = st.sidebar.number_input("Operação (h/dia)", value=20)
    conc_solidos = st.sidebar.number_input("Conc. Sólidos (%w/w)", value=30.0)
    
    st.sidebar.divider()
    st.sidebar.header("🧬 Densidades e Torta")
    rho_solido = st.sidebar.number_input("Dens. Sólido (t/m³)", value=2.70)
    rho_torta = st.sidebar.number_input("Dens. Torta (t/m³)", value=1.80)
    espessura_camara = st.sidebar.selectbox("Espessura da Câmara (mm)", [30, 40, 50], index=1)
    
    st.sidebar.divider()
    st.sidebar.header("💰 Parâmetros OPEX")
    custo_kwh = st.sidebar.number_input("Energia (R$/kWh)", value=0.65)
    pressao_operacao = st.sidebar.slider("Pressão (Bar)", 1, 15, 6)

    # --- NÚCLEO DE CÁLCULO ---
    rho_polpa = 100 / ((conc_solidos / rho_solido) + ((100 - conc_solidos) / 1.0))
    massa_polpa_hora = prod_seca / (conc_solidos / 100)
    vol_polpa_hora = massa_polpa_hora / rho_polpa
    
    # Cálculos Requisitados pelo Eder
    vol_lodo_dia = vol_polpa_hora * horas_op
    vazao_pico_lh = (vol_polpa_hora * 1000) * 1.3
    
    # Cálculo de Volume por Ciclo (Considerando 1 ciclo por hora para base)
    vol_torta_ciclo = (prod_seca / rho_torta) 

    # --- LÓGICA DE SELEÇÃO DO FILTRO (TABELA CENTRAL) ---
    # Definição de volumes por placa (litros) - Valores exemplo Micronics
    mapa_filtros = [
        {"Modelo": "800mm", "Vol_Placa": 15, "Area_Placa": 1.1},
        {"Modelo": "1000mm", "Vol_Placa": 25, "Area_Placa": 1.8},
        {"Modelo": "1200mm", "Vol_Placa": 45, "Area_Placa": 2.6},
        {"Modelo": "1500mm", "Vol_Placa": 80, "Area_Placa": 4.1},
        {"Modelo": "2000mm", "Vol_Placa": 150, "Area_Placa": 7.5},
    ]

    selecao_final = []
    for f in mapa_filtros:
        num_placas = math.ceil((vol_torta_ciclo * 1000) / f["Vol_Placa"])
        area_total = num_placas * f["Area_Placa"]
        taxa = (prod_seca * 1000) / area_total
        selecao_final.append({
            "Equipamento": f["Modelo"],
            "Placas Necessárias": num_placas,
            "Área Total (m²)": round(area_total, 2),
            "Taxa (kg/m².h)": round(taxa, 2)
        })

    # --- LAYOUT PRINCIPAL ---
    tab1, tab2, tab3 = st.tabs(["📋 Seleção do Filtro", "📈 Gráficos & OPEX", "📖 Memorial Hidráulico"])

    with tab1:
        st.subheader("Tabela de Seleção de Ativos")
        st.write("Selecione o modelo adequado baseado na quantidade de placas e taxa:")
        st.table(pd.DataFrame(selecao_final))
        
        st.divider()
        st.subheader("Definição de Bomba")
        tipo_bomba = "PEMO (Borracha)" if pressao_operacao <= 6 else "WARMAN (Metálica)"
        st.info(f"Para pressão de **{pressao_operacao} Bar**, utilizar bomba **{tipo_bomba}**.")

    with tab2:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("Distribuição de Custos (OPEX)")
            fig2, ax2 = plt.subplots(figsize=(5, 5))
            ax2.pie([45, 30, 25], labels=['Energia', 'Lonas', 'Manut'], autopct='%1.1f%%', colors=['#003366', '#ff9900', '#c0c0c0'])
            st.pyplot(fig2)
        with col_g2:
            st.subheader("Análise de Volume Diário")
            st.metric("Volume Total Lodo", f"{vol_lodo_dia:.2f} m³/dia")
            st.metric("Vazão de Pico", f"{vazao_pico_lh:,.2f} L/h")

    with tab3:
        st.subheader("Fórmulas de Engenharia")
        st.latex(r"N_{placas} = \frac{V_{torta} \cdot 1000}{Vol_{unitário}}")
        st.latex(r"Q_{pico} (L/h) = (V_{hora} \cdot 1000) \cdot 1.3")

if __name__ == "__main__":
    main()
