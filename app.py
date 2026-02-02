import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Dimensionador Micronics V54 - Restore", layout="wide")

def main():
    st.title("Dimensionador de Filtro Prensa - Cleanova Micronics (V54)")
    st.write(f"**Engenheiro de Aplicação:** Eder")
    st.markdown("---")

    # --- BLOCO 1: ENTRADA DE DADOS (INPUTS) ---
    st.subheader("1. Parâmetros de Processo")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        prod_seca = st.number_input("Massa Seca (t/h)", value=10.0)
        horas_op = st.number_input("Operação (h/dia)", value=20)
    with col2:
        conc_solidos = st.number_input("Conc. Sólidos (%w/w)", value=30.0)
        rho_solido = st.number_input("Dens. Sólido (t/m³)", value=2.70)
    with col3:
        rho_liquido = st.number_input("Dens. Líquido (t/m³)", value=1.00)
        rho_torta = st.number_input("Dens. Torta (t/m³)", value=1.80)
    with col4:
        pressao_operacao = st.number_input("Pressão (Bar)", value=6)
        area_filtracao = st.number_input("Área Filtro (m²)", value=150.0)

    # --- MEMÓRIA DE CÁLCULO INTERNA ---
    # Densidade da Polpa
    rho_polpa = 100 / ((conc_solidos / rho_solido) + ((100 - conc_solidos) / rho_liquido))
    
    # Balanço de Massas e Volumes
    massa_polpa_hora = prod_seca / (conc_solidos / 100)
    vol_polpa_hora = massa_polpa_hora / rho_polpa
    
    # Unidades Requisitadas (Eder)
    vol_lodo_dia = vol_polpa_hora * horas_op
    vazao_pico_lh = (vol_polpa_hora * 1000) * 1.3
    
    # Performance
    taxa_especifica = (prod_seca * 1000) / area_filtracao

    # --- BLOCO 2: EXIBIÇÃO DE RESULTADOS (TABULAR - ESTILO V54) ---
    st.markdown("---")
    st.subheader("2. Resultados do Dimensionamento")

    # Criando um DataFrame para exibição limpa e técnica
    dados_processo = {
        "Descrição": [
            "Densidade da Polpa",
            "Massa de Polpa Total",
            "Volume de Polpa Total",
            "Volume de Lodo por Dia",
            "Vazão de Pico (Enchimento)",
            "Taxa de Filtração Específica"
        ],
        "Valor": [
            f"{rho_polpa:.3f}",
            f"{massa_polpa_hora:.2f}",
            f"{vol_polpa_hora:.2f}",
            f"{vol_lodo_dia:.2f}",
            f"{vazao_pico_lh:,.2f}",
            f"{taxa_especifica:.2f}"
        ],
        "Unidade": ["t/m³", "t/h", "m³/h", "m³/dia", "L/h", "kg/m².h"]
    }
    
    df_resultados = pd.DataFrame(dados_processo)
    st.table(df_resultados) # st.table remove a interatividade e foca na leitura fixa

    # --- BLOCO 3: SELEÇÃO DE EQUIPAMENTO (BOMBAS) ---
    st.markdown("---")
    st.subheader("3. Especificação de Periféricos")

    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        if pressao_operacao <= 6:
            st.success("### BOMBA: PEMO")
            st.write(f"Recomendada para pressão de {pressao_operacao} Bar.")
            st.write(f"Vazão de Pico suportada: {vazao_pico_lh:,.2f} L/h")
        else:
            st.warning("### BOMBA: WARMAN / WEIR")
            st.write(f"Recomendada para pressão de {pressao_operacao} Bar.")
            st.write(f"Construção robusta para alta perda de carga.")

    with col_b2:
        # Farol de Diagnóstico (Lógica de Cores)
        if taxa_especifica <= 300:
            st.info("STATUS: Operação Normal (Verde)")
        elif taxa_especifica <= 450:
            st.warning("STATUS: Operação em Limite Técnico (Amarelo)")
        else:
            st.error("STATUS: Sobrecarga de Área (Vermelho)")

    # --- BLOCO 4: MEMORIAL DE FÓRMULAS ---
    with st.expander("Ver Fórmulas Detalhadas (V54)"):
        st.latex(r"V_{dia} = \frac{M_{seca}}{\rho_{polpa} \cdot C_w} \cdot H_{op}")
        st.latex(r"Q_{pico} = (V_{hora} \cdot 1000) \cdot 1.3")
        st.latex(r"T_{esp} = \frac{M_{seca} \cdot 1000}{A}")

if __name__ == "__main__":
    main()
