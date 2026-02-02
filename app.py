import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

# 1. Configuração de Página
st.set_page_config(page_title="Dimensionador Micronics V53", layout="wide")

def main():
    # Cabeçalho Técnico (Banner Azul)
    st.markdown("""
    <div style="background-color:#003366;padding:20px;border-radius:10px;margin-bottom:20px">
    <h1 style="color:white;text-align:center;margin:0;">CLEANOVA MICRONICS - DIMENSIONADOR V53</h1>
    <p style="color:white;text-align:center;margin:5px;">Memorial de Cálculo de Engenharia</p>
    </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR (IDENTIFICAÇÃO E PROCESSO) ---
    st.sidebar.header("📋 Identificação do Projeto")
    nome_projeto = st.sidebar.text_input("Nome do Projeto", value="Projeto Exemplo")
    num_opp = st.sidebar.text_input("N° de OPP", value="000/2026")
    empresa = st.sidebar.text_input("Empresa", value="Cliente S/A")
    responsavel = st.sidebar.text_input("Responsável pelo Projeto", value="Eder")
    
    col_cid, col_est = st.sidebar.columns(2)
    cidade = col_cid.text_input("Cidade", value="São Paulo")
    estado = col_est.text_input("Estado", value="SP")

    st.sidebar.divider()
    st.sidebar.header("📥 Parâmetros de Processo")
    prod_seca = st.sidebar.number_input("Massa Seca (t/h)", value=10.0)
    # Alterado para Disponibilidade do Equipamento conforme pedido
    disponibilidade_h = st.sidebar.number_input("Disponibilidade de Equipamento (h/dia)", value=20)
    conc_solidos = st.sidebar.number_input("Conc. Sólidos (%w/w)", value=30.0)
    
    st.sidebar.divider()
    st.sidebar.header("🧬 Densidade e Geometria")
    sg_solido = st.sidebar.number_input("SG Sólido (g/cm³)", value=2.70, format="%.2f")
    # Restaurada a Espessura da Câmara
    espessura_camara = st.sidebar.selectbox("Espessura da Câmara (mm)", [30, 40, 50, 60], index=1)
    
    st.sidebar.divider()
    st.sidebar.header("🔄 Ciclos e Operação")
    vida_util_lona = st.sidebar.number_input("Vida Útil da Lona (Ciclos)", value=2000)
    tempo_ciclo_min = st.sidebar.number_input("Tempo de Ciclo (min)", value=60)
    pressao_operacao = st.sidebar.slider("Pressão de Filtração (Bar)", 1, 15, 6)

    # --- NÚCLEO DE CÁLCULO ---
    # Gravidade específica do lodo (SG Polpa)
    sg_lodo = 100 / ((conc_solidos / sg_solido) + (100 - conc_solidos))
    
    # Taxa de fluxo de lodo m³/h e Volume Dia
    massa_polpa_hora = prod_seca / (conc_solidos / 100)
    taxa_fluxo_lodo_m3h = massa_polpa_hora / sg_lodo
    vol_lodo_dia = taxa_fluxo_lodo_m3h * disponibilidade_h
    vazao_pico_lh = (taxa_fluxo_lodo_m3h * 1000) * 1.3
    
    # Ciclos
    ciclos_dia = (disponibilidade_h * 60) / tempo_ciclo_min
    trocas_lona_ano = (ciclos_dia * 365) / vida_util_lona

    # --- CAIXAS DE RESUMO (CARDS DE DESTAQUE) ---
    st.write(f"### 🚀 Resumo Operacional: {nome_projeto}")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info(f"**Volume Lodo/Dia**\n\n {vol_lodo_dia:.2f} m³/dia")
    with c2:
        st.info(f"**Taxa Fluxo Lodo**\n\n {taxa_fluxo_lodo_m3h:.2f} m³/h")
    with c3:
        st.info(f"**Vazão Pico**\n\n {vazao_pico_lh:,.0f} L/h")
    with c4:
        # Alterado para Gravidade específica do lodo conforme pedido
        st.info(f"**Grav. Específica Lodo**\n\n {sg_lodo:.3f}")

    st.divider()

    # --- TABELA DE SELEÇÃO DE FILTROS ---
    # O volume da torta por ciclo depende da espessura da câmara selecionada
    # SG Torta fixo 1.8 para cálculo de volume físico
    vol_torta_ciclo_m3 = (prod_seca * (tempo_ciclo_min/60)) / 1.8 
    
    mapa_filtros = [
        {"Modelo": "800mm", "Vol_Placa": 15, "Area_Placa": 1.1},
        {"Modelo": "1000mm", "Vol_Placa": 25, "Area_Placa": 1.8},
        {"Modelo": "1200mm", "Vol_Placa": 45, "Area_Placa": 2.6},
        {"Modelo": "1500mm", "Vol_Placa": 80, "Area_Placa": 4.1},
        {"Modelo": "2000mm", "Vol_Placa": 150, "Area_Placa": 7.5},
    ]

    selecao_final = []
    for f in mapa_filtros:
        # Ajuste conceitual: Volume por placa varia levemente com a espessura, 
        # aqui mantemos a base da V53
        num_placas = math.ceil((vol_torta_ciclo_m3 * 1000) / f["Vol_Placa"])
        area_total = num_placas * f["Area_Placa"]
        taxa_filt = (prod_seca * 1000) / area_total
        selecao_final.append({
            "Equipamento": f["Modelo"],
            "Qtd Placas": int(num_placas),
            "Área Total (m²)": round(area_total, 2),
            "Taxa (kg/m².h)": round(taxa_filt, 2)
        })

    # --- LAYOUT DE ABAS ---
    tab1, tab2 = st.tabs(["📋 Seleção e Dimensionamento", "📈 OPEX & Performance"])

    with tab1:
        st.write(f"**Cliente:** {empresa} | **Espessura da Câmara:** {espessura_camara} mm")
        st.write("### Dimensionamento de Ativos")
        st.table(pd.DataFrame(selecao_final))
        
        tipo_bomba = "PEMO" if pressao_operacao <= 6 else "WARMAN"
        st.success(f"Hardware Sugerido: Bomba **{tipo_bomba}** para operação em {pressao_operacao} Bar.")

    with tab2:
        col_opex1, col_opex2 = st.columns(2)
        with col_opex1:
            st.subheader("Ciclos e Vida Útil")
            st.write(f"**Ciclos Diários:** {ciclos_dia:.1f}")
            st.write(f"**Trocas de Lona/Ano:** {trocas_lona_ano:.2f}")
            
            # Gráfico de Farol Horizontal
            fig, ax = plt.subplots(figsize=(6, 2))
            t_ref = selecao_final[2]["Taxa (kg/m².h)"]
            ax.barh(["Taxa"], [t_ref], color='green' if t_ref < 300 else 'orange')
            ax.set_xlim(0, 600)
            st.pyplot(fig)
            
        with col_opex2:
            st.subheader("Composição de Custos")
            fig2, ax2 = plt.subplots(figsize=(4, 4))
            ax2.pie([50, 25, 25], labels=['Energia', 'Lonas', 'Manut'], autopct='%1.1f%%', colors=['#003366', '#ff9900', '#c0c0c0'])
            st.pyplot(fig2)

if __name__ == "__main__":
    main()
