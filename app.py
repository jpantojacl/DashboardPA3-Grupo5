import streamlit as st
import pandas as pd
import plotly.express as px
import re
import collections

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard - ML & Football Scouting",
    page_icon="⚽",
    layout="wide"
)

# Forzar estilo claro en Plotly
px.defaults.template = "simple_white"
px.defaults.color_discrete_sequence = ["#1D4ED8"]  # azul fuerte

# ==========================================
# ESTILOS
# ==========================================
st.markdown("""
    <style>

    .main-title { 
        font-size:30px !important; 
        font-weight: bold; 
        color: #FFFFFF !important; 
        text-align: center; 
        margin-bottom: 10px; 
    }

    .subtitle { 
        font-size:16px !important; 
        color: #FFFFFF !important; 
        text-align: center; 
        margin-bottom: 30px; 
    }

    [data-testid="stSidebar"] * {
        font-size: 15px !important;
        color: white !important;
    }

    [data-testid="stSidebar"] {
        width: 400px !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        width: 400px !important;
    }

    [data-testid="stSidebar"] .element-container {
        margin-bottom: -10px !important;
    }

    </style>
""", unsafe_allow_html=True)
