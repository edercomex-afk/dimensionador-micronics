import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Configuração de Página e Cabeçalho Profissional
st.set_page_config(page_title="Dimensionador Micronics V54", layout="wide")

def main():
    # Cabeçalho Original Restaurado
    st.markdown("""
    <div style="background-color:#003366;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">CLEANOVA MICRONICS - DIMENSIONADOR V54</h1>
    <p style="color:white;text-align:center;">Memorial de Cálculo de Engenharia | Responsável: Eder</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.ln(2)

    # 2. Entrada de Dados (Layout Limpo)
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
        pressao_operacao = st.number_input("Pressão (Bar)", value=6)
        area_filtracao = st.number_input("Área Filtro (m²)", value=150.0)

    # 3. Núcleo de Cálculos (Sem simplificações)
    rho_polpa = 100 / ((conc_solidos / rho_solido) + ((100 - conc_solidos) / rho_liquido))
    massa_polpa_hora = prod_seca / (conc_solidos / 100)
    vol_polpa_hora = massa_polpa_hora / rho_polpa
    
    # Unidades Críticas (Volume dia e Vazão Pico L/h)
    vol_lodo_dia = vol_polpa_hora * horas_op
    vazao_pico_lh = (vol_polpa_hora * 1000) * 1.3
    
    taxa_especifica = (prod_seca * 1000) / area_filtracao

    # 4. Resultados em Tabela Técnica (Sem caixas/cards)
    st.divider()
    st.header("2. Memorial de Resultados")
    
    res_data = {
        "Parâmetro": ["Densidade da Polpa", "Massa de Polpa Total", "Volume de Polpa Total", "Volume de Lodo por Dia", "Vazão de Pico (Enchimento)", "Taxa de Filtração"],
        "Valor": [f"{rho_polpa:.3f}", f"{massa_polpa_hora:.2f}", f"{vol_polpa_hora:.2f}", f"{vol_lodo_dia:.2f}", f"{vazao_pico_lh:,.2f}", f"{taxa_especifica:.2f}"],
        "Unidade": ["t/m³", "t/h", "m³/h", "m³/dia", "L/h", "kg/m².h"]
    }
    st.table(pd.DataFrame(res_data))

    # 5. Gráfico do Farol (Restaurado)
    st.header("3. Análise de Performance")
    
    # Lógica de cores para o gráfico
    cor_farol = 'green'
    if taxa_especifica > 450: cor_farol = 'red'
    elif taxa_especifica > 300: cor_farol = 'orange'

    fig, ax = plt.subplots(figsize=(8, 2))
    ax.barh(["Taxa Atual"], [taxa_especifica], color=cor_farol)
    ax.set_xlim(0, 600)
    ax.axvline(300, color='orange', linestyle='--', label='Limite Alerta')
    ax.axvline(450, color='red', linestyle='--', label='Limite Crítico')
    ax.set_xlabel("kg/m².h")
    st.pyplot(fig)

    # 6. Seleção de Bomba e Memorial
    st.divider()
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.subheader("Seleção de Hardware")
        tipo_bomba = "PEMO" if pressao_operacao <= 6 else "WARMAN / WEIR"
        st.write(f"**Bomba Definida:** {tipo_bomba}")
        st.write(f"**Critério:** {pressao_operacao} Bar de contrapressão.")
    
    with col_b2:
        st.subheader("Fórmulas Aplicadas")
        st.latex(r"V_{dia} = V_{hora} \cdot H_{op}")
        st.latex(r"Q_{pico} (L/h) = (V_{hora} \cdot 1000) \cdot 1.3")

if __name__ == "__main__":
    main()
