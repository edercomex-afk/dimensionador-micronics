import streamlit as st

# Configuração da página para aproveitar o espaço
st.set_page_config(page_title="Dimensionador Cleanova Micronics V55", layout="wide")

def main():
    st.title("🏗️ Dimensionador Industrial V55 - Cleanova Micronics")
    st.subheader(f"Responsável Técnico: Eder")
    st.divider()

    # --- SEÇÃO 1: ENTRADA DE DADOS COMPLETA ---
    st.header("1. Parâmetros de Entrada de Processo")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Produção")
        prod_seca = st.number_input("Produção de Sólidos Secos (ton/h)", value=10.0)
        horas_op = st.number_input("Horas de Operação por Dia (h/dia)", value=20)
        conc_solidos = st.number_input("Concentração de Sólidos na Polpa (% w/w)", value=30.0)

    with col2:
        st.markdown("### 🧬 Densidades")
        rho_solido = st.number_input("Densidade do Sólido (t/m³)", value=2.70)
        rho_liquido = st.number_input("Densidade do Líquido (t/m³)", value=1.00)
        rho_torta = st.number_input("Densidade da Torta Formada (t/m³)", value=1.80)

    with col3:
        st.markdown("### 📐 Equipamento")
        area_filtracao = st.number_input("Área de Filtração Total (m²)", value=150.0)
        pressao_operacao = st.slider("Pressão de Filtração (Bar)", 1, 15, 6)
        t_ciclo_min = st.number_input("Tempo de Ciclo Estimado (min)", value=60)

    st.divider()

    # --- SEÇÃO 2: MEMÓRIA DE CÁLCULO (BACKEND) ---
    
    # Cálculo da Densidade da Polpa
    rho_polpa = 100 / ((conc_solidos / rho_solido) + ((100 - conc_solidos) / rho_liquido))
    
    # Cálculo do Balanço de Massa por Hora
    massa_polpa_hora = prod_seca / (conc_solidos / 100)
    vol_polpa_hora = massa_polpa_hora / rho_polpa
    
    # Unidades Críticas solicitadas pelo Eder
    vol_lodo_dia = vol_polpa_hora * horas_op
    vazao_pico_lh = (vol_polpa_hora * 1000) * 1.3  # Fator de segurança de 30% para pico de enchimento
    
    # Cálculo de Performance
    taxa_especifica = (prod_seca * 1000) / area_filtracao

    # --- SEÇÃO 3: EXPOSIÇÃO DETALHADA DE RESULTADOS ---
    st.header("2. Resultados do Dimensionamento")

    # Bloco Hidráulico em Destaque
    st.info("### 💧 Balanço Hidráulico e Fluxo")
    c1, c2, c3 = st.columns(3)
    c1.metric("Volume de Lodo por Dia", f"{vol_lodo_dia:.2f} m³/dia")
    c2.metric("Vazão de Pico", f"{vazao_pico_lh:,.2f} L/h")
    c3.metric("Densidade da Polpa", f"{rho_polpa:.3f} t/m³")

    # Bloco de Performance
    st.success("### ⚙️ Performance e Capacidade")
    p1, p2, p3 = st.columns(3)
    p1.metric("Taxa de Filtração", f"{taxa_especifica:.2f} kg/m².h")
    p2.metric("Massa de Polpa total", f"{massa_polpa_hora:.2f} t/h")
    p3.metric("Volume de Polpa total", f"{vol_polpa_hora:.2f} m³/h")

    st.divider()

    # --- SEÇÃO 4: DEFINIÇÃO DE HARDWARE (BOMBAS) ---
    st.header("3. Especificação Técnica de Bombas")
    
    b1, b2 = st.columns(2)
    
    with b1:
        if pressao_operacao <= 6:
            st.markdown("#### ✅ Bomba Recomendada: **PEMO**")
            st.write("**Tipo:** Centrífuga revestida em borracha.")
            st.write(f"**Vazão de Projeto:** {vazao_pico_lh:,.0f} L/h para operar até {pressao_operacao} Bar.")
        else:
            st.markdown("#### ✅ Bomba Recomendada: **WARMAN / WEIR**")
            st.write("**Tipo:** Revestimento metálico ou borracha de alta pressão.")
            st.write(f"**Vazão de Projeto:** {vazao_pico_lh:,.0f} L/h para suportar {pressao_operacao} Bar.")

    with b2:
        st.markdown("#### 🚩 Alertas de Risco")
        if taxa_especifica > 450:
            st.error("ALERTA: Taxa acima do limite para Minério de Ferro!")
        elif taxa_especifica > 300:
            st.warning("ALERTA: Operação em zona crítica (Amarelo).")
        else:
            st.info("Operação dentro dos limites normais de filtrabilidade.")

    # --- SEÇÃO 5: MEMORIAL DE FÓRMULAS (PARA GITHUB) ---
    with st.expander("📚 Memorial Descritivo de Cálculos (LaTeX)"):
        st.write("Todos os cálculos seguem as normas da Cleanova Micronics:")
        st.latex(r"V_{dia} = \frac{M_{seca}}{\rho_{polpa} \cdot C_w} \cdot H_{op}")
        st.latex(r"Q_{pico} (L/h) = (V_{polpa/hora} \cdot 1000) \cdot 1.3")
        st.latex(r"\rho_{polpa} = \frac{100}{\frac{C_w}{\rho_{s}} + \frac{100 - C_w}{\rho_{l}}}")
        st.write("Onde: $C_w$ = Conc. Sólidos (%), $\\rho_{s}$ = Densidade Sólido, $\\rho_{l}$ = Densidade Líquido.")

if __name__ == "__main__":
    main()
