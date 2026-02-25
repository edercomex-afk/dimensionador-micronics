import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuração da página - Mantendo o padrão Cleanova Micronics
st.set_page_config(page_title="Cleanova Micronics | Dimensionador V53", layout="wide")

# --- NAVEGAÇÃO POR ABAS (Para evitar que as janelas sumam) ---
aba1, aba2, aba3 = st.tabs(["📊 Dimensionamento Principal", "🧬 Densidade e Geometria", "🔗 Filtros em Paralelo"])

with aba1:
    st.title("Dimensionador de Filtro Prensa")
    col1, col2 = st.columns(2)
    with col1:
        vazao = st.number_input("Vazão de Pico (L/h)", value=50000)
        pressao = st.slider("Pressão de Filtração (Bar)", 1, 15, 7)
    
    # Lógica de seleção de bomba
    marca = "PEMO (Itália)" if pressao <= 6 else "WEIR (Warman/GEHO)"
    st.info(f"Bomba Recomendada: {marca}")

with aba2:
    st.header("🧬 Densidade e Geometria")
    st.markdown("---")
    
    # Inclusão dos campos que você mostrou na captura de tela
    col_a, col_b = st.columns(2)
    with col_a:
        ge_solidos = st.number_input(
            "Gravidade específica dos Sólidos Secos (g/cm³)", 
            value=2.70, 
            format="%.2f"
        )
    with col_b:
        espessura_camara = st.number_input(
            "Espessura da Câmara (mm)", 
            value=40
        )
    
    st.success(f"Dados registrados para o cálculo de volume de torta.")

with aba3:
    st.header("🔗 Alternativas com Filtros em Paralelo")
    st.write("Configurações de redundância e aumento de capacidade.")
