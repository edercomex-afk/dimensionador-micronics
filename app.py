import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Configuração de Página
st.set_page_config(page_title="Dimensionador Micronics V53", layout="wide")

def main():
    # Cabeçalho Técnico Original (Fiel à V53)
    st.markdown("""
    <div style="background-color:#003366;padding:20px;border-radius:10px;margin-bottom:20px">
    <h1 style="color:white;text-align:center;margin:0;">CLEANOVA MICRONICS - DIMENSIONADOR V53</h1>
    <p style="color:white;text-align:center;margin:5px;">Memorial de Cálculo de Engenharia | Responsável: Eder</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")

    # 2. Entrada de Dados
    st.header("1. Parâmetros de Entrada")
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
        pressao_operacao = st.number_input("Pressão (Bar)", value=6.0)
        area_filtracao = st.number_input("Área Filtro (m²)", value=150.0)

    # 3. Memória de Cálculo
    rho_polpa = 100 / ((conc_solidos / rho_solido) + ((100 - conc_solidos) / rho_liquido))
    massa_polpa_hora = prod_seca / (conc_solidos / 100)
    vol_polpa_hora = massa_polpa_hora / rho_polpa
    
    # Unidades Críticas Restauradas
    vol_lodo_dia = vol_polpa_hora * horas_op
    vazao_pico_lh = (vol_polpa_hora * 1000) * 1.3
    
    taxa_especifica = (prod_seca * 1000) / area_filtracao

    # 4. Tabela de Resultados Técnica
    st.markdown("---")
    st.header("2. Memorial de Resultados")
    
    res_data = {
        "Parâmetro": [
            "Densidade da Polpa", 
            "Massa de Polpa Total", 
            "Volume de Polpa Total", 
            "Volume de Lodo por Dia", 
            "Vazão de Pico (Enchimento)", 
            "Taxa de Filtração"
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
    st.table(pd.DataFrame(res_data))

    # 5. Gráfico de Performance (Farol)
    st.header("3. Análise de Performance")
    
    if taxa_especifica <= 300:
        cor_grafico = 'green'
        status = "Operação Normal"
    elif taxa_especifica <= 450:
        cor_grafico = 'orange'
        status = "Atenção / Limite"
    else:
        cor_grafico = 'red'
        status = "Crítico / Sobrecarga"

    fig, ax = plt.subplots(figsize=(10, 2))
    ax.barh(["Taxa Atual"], [taxa_especifica], color=cor_grafico)
    ax.set_xlim(0, 600)
    ax.axvline(300, color='black', linestyle='--')
    ax.axvline(450, color='black', linestyle='--')
    ax.set_title(f"Status: {status}")
    st.pyplot(fig)

    # 6. Seleção de Hardware e Fórmulas
    st.markdown("---")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        st.subheader("Hardware")
        tipo_bomba = "PEMO" if pressao_operacao <= 6 else "WARMAN / WEIR"
        st.write(f"**Bomba Definida:** {tipo_bomba}")
        st.write(f"**Pressão de Projeto:** {pressao_operacao} Bar")

    with col_f2:
        st.subheader("Fórmulas")
        st.latex(r"V_{dia} = V_{hora} \cdot H_{op}")
        st.latex(r"Q_{pico} (L/h) = (V_{hora} \cdot 1000) \cdot 1.3")

if __name__ == "__main__":
    main()
