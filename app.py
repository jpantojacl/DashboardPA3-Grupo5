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

    /* ======== TÍTULO PRINCIPAL ======== */
    .main-title { 
        font-size:30px !important; 
        font-weight: bold; 
        color: #FFFFFF !important; 
        text-align: center; 
        margin-bottom: 10px; 
    }

    /* ======== SUBTÍTULO ======== */
    .subtitle { 
        font-size:16px !important; 
        color: #FFFFFF !important; 
        text-align: center; 
        margin-bottom: 30px; 
    }

    /* ======== AJUSTES DEL SIDEBAR ======== */

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


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("🔍 Información del Proyecto")

    st.markdown("**Pregunta de Investigación:**")
    st.info(
        "¿De qué manera el uso de algoritmos supervisados de machine learning "
        "optimiza la precisión del scouting para la identificación de talento "
        "emergente en el fútbol profesional?"
    )
    st.markdown("**Keywords Autorizadas:**")
    st.code(
        '1. "Machine learning"\n'
        '2. "Scouting"\n'
        '3. "Talent identification"\n'
        '4. "Soccer"'
    )

    st.markdown("---")
    st.subheader("📥 Carga de Datos")
    uploaded_file = st.file_uploader("Sube el archivo CSV", type=["csv"])

# ==========================================
# CARGA DE DATOS
# ==========================================
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

df = None
if uploaded_file:
    df = load_data(uploaded_file)

    # 🔥 CORRECCIÓN: renombrar columnas
    df = df.rename(columns={
        "Cited by": "Cantidad de citaciones",
        "Short Title": "Título"
    })

    st.sidebar.success("Dataset cargado con éxito")

# ==========================================
# TÍTULOS PRINCIPALES
# ==========================================
st.markdown(
    '<div class="main-title">⚽ Machine Learning y Búsqueda de Talento</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Lectura y análisis del archivo</div>',
    unsafe_allow_html=True
)

# ==========================================
# SI HAY DATA → MOSTRAR DASHBOARD
# ==========================================
if df is not None:

    required_cols = ["Authors", "Title", "Year", "Abstract", "Cantidad de citaciones", "Source title"]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        st.error(f"❌ El archivo no contiene las columnas necesarias: {missing}")
        st.stop()
    else:
        st.success("✅ El dataset contiene todos los metadatos esenciales requeridos por Scopus.")

    # ==========================================
    # FILTROS
    # ==========================================
    st.markdown("### 🎛️ Filtros Globales")

    col_f1, col_f2 = st.columns(2)

    with col_f1:
        years = sorted(df["Year"].dropna().unique())
        selected_years = st.multiselect("Filtrar por Año:", years, default=years)

    with col_f2:
        min_cit, max_cit = int(df["Cantidad de citaciones"].min()), int(df["Cantidad de citaciones"].max())
        cit_range = st.slider("Rango de Citaciones:", min_cit, max_cit, (min_cit, max_cit))

    df_filtered = df[
        (df["Year"].isin(selected_years)) &
        (df["Cantidad de citaciones"].between(cit_range[0], cit_range[1]))
    ]

    # ==========================================
    # MÉTRICAS
    # ==========================================
    st.markdown("### 📊 Resumen General")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Artículos", len(df_filtered))
    col2.metric("Años", f"{df_filtered['Year'].min()} - {df_filtered['Year'].max()}")
    col3.metric("Citaciones Totales", int(df_filtered['Cantidad de citaciones'].sum()))
    col4.metric("Máx Citaciones", int(df_filtered['Cantidad de citaciones'].max()))

    # ==========================================
    # TABS
    # ==========================================
    tab1, tab2, tab3 = st.tabs(["📋 Explorador", "📊 Gráficos", "🔤 Análisis de Texto"])

    # ==========================================
    # TAB 1
    # ==========================================
    with tab1:
        st.subheader("📋 Explorador del Dataset")
        st.dataframe(df_filtered, use_container_width=True)

    # ==========================================
    # FUNCIÓN PARA APLICAR ESTILO
    # ==========================================
    def apply_style(fig):
        fig.update_layout(
            font=dict(color
