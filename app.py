import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF

# Configuração da página
st.set_page_config(page_title="Cleanova Micronics | V44", layout="wide")

# --- FUNÇÃO PARA GERAR O GRÁFICO DE FILTRAÇÃO ---
def plot_curva_filtracao(pressao_alvo, vazao_pico):
    tempo = np.linspace(0, 45, 100) # Simulação de um ciclo de 45 min
    
    # Simulação da pressão (Curva logarítmica de subida)
    pressao = pressao_alvo * (1 - np.exp(-0.15 * tempo))
    
    # Simulação da vazão (Curva exponencial de queda)
    vazao = vazao_pico * np.exp(-0.12 * tempo)
    
    fig, ax1 = plt.subplots(figsize=(8, 4))

    color = 'tab:red'
    ax1.set_xlabel('Tempo de Ciclo (min)')
    ax1.set_ylabel('Pressão (Bar)', color=color)
    ax1.plot(tempo, pressao, color=color, linewidth=3, label='Pressão')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Vazão (L/h)', color=color)
    ax2.plot(tempo, vazao, color=color, linewidth=3, label='Vazão')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title(f"Comportamento da Bomba no Ciclo ({pressao_alvo} Bar)")
    fig.tight_layout()
    return fig

# --- INTERFACE ---
st.title("Cleanova Micronics | Dimensionador & Gráficos V44")
st.markdown("---")

# Dados Iniciais
c1, c2, c3 = st.columns(3)
cliente = c1.text_input("👤 Cliente")
n_opp = c2.text_input("🔢 Nº OPP")
responsavel = c3.text_input("👨‍💻 Responsável")

# Sidebar
st.sidebar.header("⚙️ Parâmetros Técnicos")
vazao_pico = st.sidebar.number_input("Vazão de Pico da Bomba (L/h)", value=50000.0)
pressao_manual = st.sidebar.slider("Pressão de Filtração (Bar)", 1, 15, 7)

# Lógica de Marcas (Pemo / Weir)
if pressao_manual <= 6:
    marca, linha = "PEMO (Itália)", "Série AO/AB - Centrífuga de Alta Abrasão"
else:
    marca, linha = "WEIR (Warman/GEHO)", "Série Warman AH ou GEHO ZPR"

# --- ÁREA DE GRÁFICOS E RESULTADOS ---
st.subheader("📊 Comportamento Dinâmico da Filtração")

col_graf, col_info = st.columns([2, 1])

with col_graf:
    # Gerar e mostrar o gráfico
    figura = plot_curva_filtracao(pressao_manual, vazao_pico)
    st.pyplot(figura)
    st.caption("O gráfico acima simula a interação entre a Bomba e o Filtro Prensa durante o ciclo de 45 min.")

with col_info:
    st.info(f"**Marca Recomendada:** \n{marca}")
    st.success(f"**Linha Proposta:** \n{linha}")
    st.metric("Pressão de Compactação", f"{pressao_manual} Bar")
    st.metric("Vazão Inicial", f"{vazao_pico:,.0f} L/h")

# Tabela de Performance (Exemplo para preencher o app)
st.markdown("---")
st.subheader("📋 Resumo do Estudo")
st.table([
    {"Item": "Modelo do Filtro", "Especificação": "1500x1500mm"},
    {"Item": "Número de Placas", "Especificação": "80 unidades"},
    {"Item": "Bomba de Alimentação", "Especificação": f"{marca} - {linha}"},
    {"Item": "Pressão de Trabalho", "Especificação": f"{pressao_manual} Bar"}
])

# --- REQUISITOS PARA FUNCIONAR ---
# Lembre-se de adicionar 'matplotlib' e 'numpy' no seu arquivo requirements.txt!
