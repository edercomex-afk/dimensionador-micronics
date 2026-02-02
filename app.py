import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

    # --- SIDEBAR (MENU LATERAL) ---
    st.sidebar.header("📥 Parâmetros de Entrada")
    
    prod_seca = st.sidebar.number_input("Massa Seca (t/h)", value=10.0)
    horas_op = st.sidebar.number_input("Operação (h/dia)", value=20)
    conc_solidos = st.sidebar.number_input("Conc. Sólidos (%w/w)", value=30.0)
    
    st.sidebar.divider()
    rho_solido = st.sidebar.number_input("Dens. Sólido (t/m³)", value=2.70)
    rho_liquido = st.sidebar.number_input("Dens. Líquido (t/m³)", value=1.00)
    rho_torta = st.sidebar.number_input("Dens. Torta (t/m³)", value=1.80)
    
    st.sidebar.divider()
    pressao_operacao = st.sidebar.slider("Pressão de Filtração (Bar)", 1, 15, 6)
    area_filtracao = st.sidebar.number_input("Área Filtro (m²)", value=150.0)
    custo_kwh = st.sidebar.number_input("Custo Energia (R$/kWh)", value=0.65)

    # --- NÚCLEO DE CÁLCULO ---
    rho_polpa = 100 / ((conc_solidos / rho_solido) + ((100 - conc_solidos) / rho_liquido))
    massa_polpa_hora = prod_seca / (conc_solidos / 100)
    vol_polpa_hora = massa_polpa_hora / rho_polpa
    
    vol_lodo_dia = vol_polpa_hora * horas_op
    vazao_pico_lh = (vol_polpa_hora * 1000) * 1.3
    taxa_especifica = (prod_seca * 1000) / area_filtracao

    # Cálculo Simplificado de OPEX (Exemplo V53)
    consumo_estimado = vol_polpa_hora * 2.5 # kWh/m3 presumido
    custo_energia_dia = consumo_estimado * horas_op * custo_kwh

    # --- LAYOUT PRINCIPAL ---
    
    tab1, tab2, tab3 = st.tabs(["📊 Resultados", "📈 Gráficos & OPEX", "📖 Fórmulas"])

    with tab1:
        st.header("Memorial de Resultados")
        res_data = {
            "Parâmetro": ["Densidade da Polpa", "Massa de Polpa Total", "Volume de Polpa Total", "Volume de Lodo por Dia", "Vazão de Pico (L/h)", "Taxa de Filtração"],
            "Valor": [f"{rho_polpa:.3f}", f"{massa_polpa_hora:.2f}", f"{vol_polpa_hora:.2f}", f"{vol_lodo_dia:.2f}", f"{vazao_pico_lh:,.2f}", f"{taxa_especifica:.2f}"],
            "Unidade": ["t/m³", "t/h", "m³/h", "m³/dia", "L/h", "kg/m².h"]
        }
        st.table(pd.DataFrame(res_data))
        
        st.subheader("Hardware Recomendado")
        tipo_bomba = "PEMO" if pressao_operacao <= 6 else "WARMAN / WEIR"
        st.info(f"Bomba Definida: **{tipo_bomba}** para operação em {pressao_operacao} Bar.")

    with tab2:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Status de Performance")
            # Gráfico de Barras Horizontal
            fig1, ax1 = plt.subplots(figsize=(6, 3))
            cor = 'green' if taxa_especifica <= 300 else 'orange' if taxa_especifica <= 450 else 'red'
            ax1.barh(["Taxa"], [taxa_especifica], color=cor)
            ax1.set_xlim(0, 600)
            ax1.axvline(300, color='black', linestyle='--')
            ax1.axvline(450, color='black', linestyle='--')
            st.pyplot(fig1)

        with col_g2:
            st.subheader("Distribuição de OPEX Estimado")
            # Gráfico de Pizza para OPEX
            fig2, ax2 = plt.subplots(figsize=(6, 3))
            labels = ['Energia', 'Manutenção', 'Lonas']
            sizes = [custo_energia_dia, custo_energia_dia*0.3, custo_energia_dia*0.2]
            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff','#99ff99'])
            st.pyplot(fig2)
            st.write(f"**Custo Estimado Energia:** R$ {custo_energia_dia:.2f}/dia")

    with tab3:
        st.subheader("Fórmulas Aplicadas")
        st.latex(r"V_{dia} = V_{hora} \cdot H_{op}")
        st.latex(r"Q_{pico} (L/h) = (V_{hora} \cdot 1000) \cdot 1.3")
        st.latex(r"\rho_{polpa} = \frac{100}{\frac{C_w}{\rho_{s}} + \frac{100 - C_w}{\rho_{l}}}")

if __name__ == "__main__":
    main()
