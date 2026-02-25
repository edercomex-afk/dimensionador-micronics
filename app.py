import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

# Configuração da página - Cleanova Micronics V43
st.set_page_config(page_title="Cleanova Micronics | Dimensionador V43", layout="wide")

# --- FUNÇÕES TÉCNICAS ---
def plot_curva_filtracao(pressao_alvo, vazao_pico):
    tempo = np.linspace(0, 45, 100)
    pressao = pressao_alvo * (1 - np.exp(-0.15 * tempo))
    vazao = vazao_pico * np.exp(-0.12 * tempo)
    
    fig, ax1 = plt.subplots(figsize=(8, 4))
    color = 'tab:red'
    ax1.set_xlabel('Tempo de Ciclo (min)')
    ax1.set_ylabel('Pressão (Bar)', color=color)
    ax1.plot(tempo, pressao, color=color, linewidth=3)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Vazão (L/h)', color=color)
    ax2.plot(tempo, vazao, color=color, linewidth=3)
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title(f"Comportamento Dinâmico ({pressao_alvo} Bar)")
    fig.tight_layout()
    return fig

# --- SIDEBAR: PARÂMETROS ---
st.sidebar.image("https://www.micronicsinc.com/wp-content/uploads/2022/03/Micronics-Engineered-Filtration-Group-Logo.png", width=200)
st.sidebar.header("⚙️ Configurações Gerais")

vazao_pico = st.sidebar.number_input("Vazão de Pico da Bomba (L/h)", value=50000.0)
pressao_manual = st.sidebar.slider("Pressão de Filtração (Bar)", 1, 15, 7)

st.sidebar.markdown("---")
st.sidebar.header("🧬 Densidade e Geometria")
ge_solidos = st.sidebar.number_input("Gravidade específica dos Sólidos Secos (g/cm³)", value=2.70, format="%.2f")
espessura_camara = st.sidebar.number_input("Espessura da Câmara (mm)", value=40)

# --- CORPO PRINCIPAL: ABAS (As janelas que haviam sumido) ---
tab_dim, tab_paralelo, tab_relatorio = st.tabs([
    "📊 Dimensionamento Principal", 
    "🔗 Alternativas em Paralelo", 
    "📝 Resumo Técnico"
])

with tab_dim:
    st.title("Dimensionador & Gráficos")
    
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("👤 Cliente")
    n_opp = c2.text_input("🔢 Nº OPP")
    responsavel = c3.text_input("👨‍💻 Responsável")

    col_graf, col_info = st.columns([2, 1])

    with col_graf:
        figura = plot_curva_filtracao(pressao_manual, vazao_pico)
        st.pyplot(figura)

    with col_info:
        marca = "PEMO (Itália)" if pressao_manual <= 6 else "WEIR (Warman/GEHO)"
        st.info(f"**Bomba:** {marca}")
        st.metric("Pressão", f"{pressao_manual} Bar")
        st.metric("G.E. Sólidos", f"{ge_solidos} g/cm³")

with tab_paralelo:
    st.header("Alternativas com Filtros em Paralelo")
    st.write("Configuração de múltiplos equipamentos para alta vazão.")
    # Aqui você pode inserir a lógica de filtros em paralelo que possuía na V43

with tab_relatorio:
    st.header("Resumo do Estudo")
    st.table([
        {"Item": "Cliente", "Valor": cliente},
        {"Item": "Bomba", "Valor": marca},
        {"Item": "G.E. Sólidos", "Valor": f"{ge_solidos} g/cm³"},
        {"Item": "Espessura Câmara", "Valor": f"{espessura_camara} mm"}
    ])
