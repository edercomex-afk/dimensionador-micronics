import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

# 1. Configuração de Página
st.set_page_config(page_title="Dimensionador Micronics V53", layout="wide")

def main():
    # Cabeçalho Técnico Restaurado
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
    st.sidebar.header("🧬 Densidades (SG) e Torta")
    # Densidade expressa em g/cm³ conforme solicitado
    sg_solido = st.sidebar.number_input("SG Sólido (g/cm³)", value=2.70, format="%.2f")
    sg_liquido = st.sidebar.number_input("SG Líquido (g/cm³)", value=1.00, format="%.2f")
    sg_torta = st.sidebar.number_input("SG Torta Formada (g/cm³)", value=1.80, format="%.2f")
    
    st.sidebar.divider()
    st.sidebar.header("🔄 Ciclos e Manutenção")
    vida_util_lona = st.sidebar.number_input("Vida Útil da Lona (Ciclos)", value=2000)
    tempo_ciclo_min = st.sidebar.number_input("Tempo de Ciclo (min)", value=60)
    
    st.sidebar.divider()
    pressao_operacao = st.sidebar.slider("Pressão de Filtração (Bar)", 1, 15, 6)

    # --- NÚCLEO DE CÁLCULO ---
    # Conversão g/cm³ é equivalente a t/m³ para o cálculo
    rho_polpa = 100 / ((conc_solidos / sg_solido) + ((100 - conc_solidos) / sg_liquido))
    massa_polpa_hora = prod_seca / (conc_solidos / 100)
    vol_polpa_hora = massa_polpa_hora / rho_polpa
    
    # Unidades de Volume e Vazão
    vol_lodo_dia = vol_polpa_hora * horas_op
    vazao_pico_lh = (vol_polpa_hora * 1000) * 1.3
    
    # Cálculos de Ciclo
    ciclos_dia = (horas_op * 60) / tempo_ciclo_min
    trocas_lona_ano = (ciclos_dia * 365) / vida_util_lona
    vol_torta_ciclo = (prod_seca * (tempo_ciclo_min/60)) / sg_torta

    # --- TABELA DE SELEÇÃO DE FILTROS (CENTRAL) ---
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
            "Placas": int(num_placas),
            "Área Total (m²)": round(area_total, 2),
            "Taxa (kg/m².h)": round(taxa, 2)
        })

    # --- EXPOSIÇÃO DOS DADOS ---
    tab1, tab2 = st.tabs(["📋 Seleção e Dimensionamento", "📈 Análise OPEX e Ciclos"])

    with tab1:
        st.subheader("Balanço Hidráulico e Tabela de Seleção")
        c1, c2, c3 = st.columns(3)
        c1.metric("Volume Lodo/Dia", f"{vol_lodo_dia:.2f} m³/dia")
        c2.metric("Vazão de Pico", f"{vazao_pico_lh:,.0f} L/h")
        c3.metric("SG Polpa", f"{rho_polpa:.3f} g/cm³")
        
        st.table(pd.DataFrame(selecao_final))
        
        st.divider()
        tipo_bomba = "PEMO" if pressao_operacao <= 6 else "WARMAN"
        st.info(f"Bomba Recomendada: **{tipo_bomba}** | Pressão: {pressao_operacao} Bar")

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Ciclos e Vida Útil")
            st.write(f"**Ciclos por Dia:** {ciclos_dia:.1f}")
            st.write(f"**Trocas de Lona/Ano:** {trocas_lona_ano:.2f}")
            
            # Gráfico Farol
            fig, ax = plt.subplots(figsize=(6, 2))
            taxa_atual = selecao_final[2]["Taxa (kg/m².h)"] # Exemplo 1200mm
            ax.barh(["Taxa de Filtração"], [taxa_atual], color='orange' if taxa_atual > 300 else 'green')
            ax.set_xlim(0, 600)
            st.pyplot(fig)
            
        with col_b:
            st.subheader("Estimativa de OPEX")
            fig2, ax2 = plt.subplots(figsize=(5, 5))
            ax2.pie([50, 25, 25], labels=['Energia', 'Lonas', 'Peças'], autopct='%1.1f%%', colors=['#003366', '#ff9900', '#c0c0c0'])
            st.pyplot(fig2)

if __name__ == "__main__":
    main()
