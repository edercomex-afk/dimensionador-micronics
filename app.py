import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Configuração de Página
st.set_page_config(page_title="Dimensionador Micronics V54", layout="wide")

def main():
    # Cabeçalho Profissional (Restaurado)
    st.markdown("""
    <div style="background-color:#003366;padding:20px;border-radius:10px;margin-bottom:20px">
    <h1 style="color:white;text-align:center;margin:0;">CLEANOVA MICRONICS - DIMENSIONADOR V54</h1>
    <p style="color:white;text-align:center;margin:5px;">Memorial de Cálculo de Engenharia | Responsável: Eder</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Substituindo o st.ln(2) que causava o erro por espaços vazios
    st.write("")
    st.write("")

    # 2. Entrada de Dados (Layout V54)
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

    # 3. Cálculos Técnicos (Sem ocultar dados)
    # Cálculo da Densidade da Polpa
    rho_polpa = 100 / ((conc_solidos / rho_solido) + ((100 - conc_solidos) / rho_liquido))
    
    # Balanço de Massas
    massa_polpa_hora = prod_seca / (conc_solidos / 100)
    vol_polpa_hora = massa_polpa_hora / rho_polpa
    
    # Dados de Volume e Vazão (Conforme solicitado pelo Eder)
    vol_lodo_dia = vol_polpa_hora * horas_op
    vazao_pico_lh = (vol_polpa_hora * 1000) * 1.3 # 30% de margem de pico
    
    # Performance
    taxa_especifica = (prod_seca * 1000) / area_filtracao

    # 4. Memorial de Resultados (Tabela Técnica)
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

    # 5. Gráfico de Performance - O Farol (Restaurado)
    st.header("3. Análise de Performance (Farol)")
    
    # Lógica de cores baseada nos limites de kg/m2.h
    if taxa_especifica <= 300:
        cor_grafico = '#2ecc71' # Verde
        status_msg = "Operação Otimizada (Verde)"
    elif taxa_especifica <= 450:
        cor_grafico = '#f1c40f' # Amarelo
        status_msg = "Operação Crítica / Atenção (Amarelo)"
    else:
        cor_grafico = '#e74c3c' # Vermelho
        status_msg = "Sobrecarga / Aumentar Área (Vermelho)"

    fig, ax = plt.subplots(figsize=(10, 2))
    ax.barh(["Taxa de Filtração"], [taxa_especifica], color=cor_grafico)
    ax.set_xlim(0, 600)
    # Linhas de referência
    ax.axvline(300, color='black', linestyle='--', alpha=0.5)
    ax.axvline(450, color='black', linestyle='--', alpha=0.5)
    ax.set_title(f"Status: {status_msg}")
    st.pyplot(fig)

    # 6. Seleção de Bomba e Fórmulas
    st.markdown("---")
    col_fim1, col_fim2 = st.columns(2)
    
    with col_fim1:
        st.subheader("Hardware Selecionado")
        tipo_bomba = "PEMO (Borracha)" if pressao_operacao <= 6 else "WARMAN / WEIR (Alta Pressão)"
        st.write(f"**Bomba Principal:** {tipo_bomba}")
        st.write(f"**Vazão Requerida (Pico):** {vazao_pico_lh:,.2f} L/h")
        st.write(f"**Pressão de Projeto:** {pressao_operacao} Bar")

    with col_fim2:
        st.subheader("Memória de Cálculo (LaTeX)")
        st.latex(r"V_{dia} = V_{hora} \cdot H_{op}")
        st.latex(r"Q_{pico} (L/h) = (V_{hora} \cdot 1000) \cdot 1.3")

if __name__ == "__main__":
    main()
