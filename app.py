import streamlit as st
import math

# Configuração da página
st.set_page_config(page_title="Dimensionador Cleanova Micronics V55", layout="wide")

def main():
    st.title("🏗️ Dimensionador Industrial - Cleanova Micronics")
    st.markdown(f"**Engenheiro Responsável:** Eder")
    st.divider()

    # --- ENTRADA DE DADOS (SIDEBAR) ---
    st.sidebar.header("📥 Parâmetros de Entrada")
    
    # Produção e Processo
    prod_seca_ton = st.sidebar.number_input("Produção de Sólidos Secos (ton/h)", value=10.0, step=0.5)
    conc_solidos_w = st.sidebar.number_input("Concentração de Sólidos na Polpa (% w/w)", value=30.0, step=1.0)
    horas_op = st.sidebar.number_input("Horas de Operação por Dia (h)", value=20, step=1)
    
    # Densidades
    rho_solido = st.sidebar.number_input("Densidade do Sólido (t/m³)", value=2.7, step=0.1)
    rho_liquido = st.sidebar.number_input("Densidade do Líquido (t/m³)", value=1.0, step=0.01)
    
    # Parâmetros de Filtração
    pressao_target = st.sidebar.slider("Pressão de Filtração (Bar)", 1, 15, 6)
    area_filtracao = st.sidebar.number_input("Área de Filtração do Filtro (m²)", value=150.0, step=10.0)

    # --- NÚCLEO DE CÁLCULO (MEMÓRIA TÉCNICA) ---
    
    # 1. Densidade da Polpa (Mistura)
    # Formula: 100 / ((%S / RhoS) + (%L / RhoL))
    rho_polpa = 100 / ((conc_solidos_w / rho_solido) + ((100 - conc_solidos_w) / rho_liquido))
    
    # 2. Volume de Lodo por Hora (m³/h)
    # Volume = Massa / (Densidade * Concentração)
    vol_lodo_hora = prod_seca_ton / (rho_polpa * (conc_solidos_w / 100))
    
    # 3. Volume de Lodo por Dia (m³/dia) - Requisito Eder
    vol_lodo_dia = vol_lodo_hora * horas_op
    
    # 4. Vazão de Pico (L/h) - Abaixo da unidade conforme solicitado
    # Considerando fator de pico para enchimento rápido (30% de margem)
    vazao_pico_lh = (vol_lodo_hora * 1000) * 1.3

    # 5. Taxa de Filtração Específica (kg/m².h)
    taxa_especifica = (prod_seca_ton * 1000) / area_filtracao

    # --- EXPOSIÇÃO DOS RESULTADOS ---
    
    col_res1, col_res2 = st.columns(2)

    with col_res1:
        st.subheader("💧 Balanço Hidráulico")
        container_h = st.container(border=True)
        container_h.metric("Volume de Lodo por Dia", f"{vol_lodo_dia:.2f} m³/dia")
        container_h.metric("Vazão de Pico", f"{vazao_pico_lh:,.2f} L/h")
        container_h.write(f"**Densidade da Polpa:** {rho_polpa:.3f} t/m³")

    with col_res2:
        st.subheader("⚙️ Performance do Equipamento")
        container_p = st.container(border=True)
        container_p.metric("Taxa de Filtração", f"{taxa_especifica:.2f} kg/m².h")
        
        # Lógica do Farol (Sinalizador)
        limite_referencia = 300 # Exemplo para Concentrado (pode ser dinâmico)
        porcentagem_limite = (taxa_especifica / limite_referencia) * 100

        if porcentagem_limite <= 100:
            st.success("Sinalizador: VERDE (Operação Segura)")
        elif porcentagem_limite <= 130:
            st.warning("Sinalizador: AMARELO (Operação Agressiva)")
        else:
            st.error("Sinalizador: VERMELHO (Risco de Sobrecarga)")

    st.divider()

    # --- ESPECIFICAÇÃO DE BOMBAS ---
    st.subheader("Pump Selector: Definição de Hardware")
    
    c1, c2 = st.columns(2)
    with c1:
        if pressao_target <= 6:
            st.info("### Bomba Selecionada: **PEMO**")
            st.write("""
            - **Tipo:** Centrífuga com revestimento em borracha.
            - **Justificativa:** Pressão dentro do limite de vulcanização. 
            - **Vantagem:** Alta resistência à abrasão e vazão de pico estável.
            """)
        else:
            st.info("### Bomba Selecionada: **WARMAN / WEIR**")
            st.write("""
            - **Tipo:** Bomba de Polpa Heavy Duty.
            - **Justificativa:** Pressão acima de 6 Bar exige carcaça metálica/reforçada.
            - **Vantagem:** Vence a perda de carga final do ciclo da torta.
            """)
            
    with c2:
        st.write("**Resumo Técnico para GitHub:**")
        st.code(f"""
        # Dados de Dimensionamento
        VOL_DIA = {vol_lodo_dia:.2f} m3
        VAZAO_PICO = {vazao_pico_lh:.2f} L/h
        PRESSAO = {pressao_target} Bar
        BOMBA = {"PEMO" if pressao_target <= 6 else "WARMAN"}
        """, language='python')

    # --- MEMORIAL DE CÁLCULO (EXPANDER) ---
    with st.expander("📖 Ver Detalhamento de Fórmulas e Relacionamentos"):
        st.markdown("### Fórmulas Aplicadas no Dimensionamento:")
        st.latex(r"V_{dia} = \left( \frac{M_{seca}}{\rho_{polpa} \cdot C_w} \right) \cdot H_{op}")
        st.latex(r"Q_{pico} (L/h) = (V_{hora} \cdot 1000) \cdot 1.3")
        st.latex(r"T_{esp} = \frac{M_{seca} \cdot 1000}{A}")
        st.markdown("""
        ---
        **Riscos de Dados Incorretos:**
        1. **Densidade Errada:** Impacta diretamente no volume total diário, podendo causar subdimensionamento da frota de filtros.
        2. **% Sólidos Baixo:** Aumenta a vazão de pico, podendo causar cavitação na bomba selecionada.
        """)

if __name__ == "__main__":
    main()
