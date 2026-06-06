import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# ==========================================
# ESTILOS
# ==========================================
st.markdown("""
    <style>
    .main-title { font-size:40px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 10px; }
    .subtitle { font-size:18px !important; color: #4B5563; text-align: center; margin-bottom: 30px; }
    .card { background-color: #F3F4F6; padding: 20px; border-radius: 10px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5323/5323871.png", width=100)
    st.header("🔍 Información del Proyecto")
    st.info("¿Cómo optimiza el ML el scouting de talento emergente en el fútbol profesional?")

    st.subheader("📥 Carga de Datos")
    uploaded_file = st.file_uploader("Sube el archivo CSV exportado de Scopus", type=["csv"])

# ==========================================
# CARGA DE DATOS
# ==========================================
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

df = None
if uploaded_file:
    df = load_data(uploaded_file)
    st.sidebar.success("Dataset cargado con éxito")

# ==========================================
# TÍTULOS PRINCIPALES
# ==========================================
st.markdown('<div class="main-title">⚽ Machine Learning & Scouting de Fútbol</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Análisis del Estado del Arte de la Literatura Científica (Scopus)</div>', unsafe_allow_html=True)

# ==========================================
# SI HAY DATA → MOSTRAR DASHBOARD
# ==========================================
if df is not None:

    # ==========================================
    # VALIDACIÓN DE COLUMNAS
    # ==========================================
    required_cols = ["Authors", "Title", "Year", "Source title", "Cited by", "Abstract"]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        st.error(f"El archivo no contiene las columnas necesarias: {missing}")
        st.stop()

    # ==========================================
    # FILTROS GLOBALES
    # ==========================================
    st.markdown("### 🎛️ Filtros Globales")

    col_f1, col_f2 = st.columns(2)

    with col_f1:
        years = sorted(df["Year"].dropna().unique())
        selected_years = st.multiselect("Filtrar por Año:", years, default=years)

    with col_f2:
        min_cit, max_cit = int(df["Cited by"].min()), int(df["Cited by"].max())
        cit_range = st.slider("Rango de Citaciones:", min_cit, max_cit, (min_cit, max_cit))

    df_filtered = df[
        (df["Year"].isin(selected_years)) &
        (df["Cited by"].between(cit_range[0], cit_range[1]))
    ]

    # ==========================================
    # MÉTRICAS PRINCIPALES
    # ==========================================
    st.markdown("### 📊 Resumen General")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Artículos", len(df_filtered))
    col2.metric("Años", f"{df_filtered['Year'].min()} - {df_filtered['Year'].max()}")
    col3.metric("Citaciones Totales", int(df_filtered['Cited by'].sum()))
    col4.metric("Máx Citaciones", int(df_filtered['Cited by'].max()))

    # ==========================================
    # TABS
    # ==========================================
    tab1, tab2, tab3 = st.tabs(["📋 Explorador", "📊 Gráficos", "🔤 Análisis de Texto"])

    # ==========================================
    # TAB 1: EXPLORADOR
    # ==========================================
    with tab1:
        st.subheader("📋 Explorador del Dataset")
        st.dataframe(df_filtered, use_container_width=True)

    # ==========================================
    # TAB 2: GRÁFICOS INTERACTIVOS
    # ==========================================
    with tab2:
        st.subheader("📊 Visualizaciones Interactivas")

        col_g1, col_g2 = st.columns(2)

        # --- Publicaciones por Año ---
        with col_g1:
            st.markdown("#### 📈 Publicaciones por Año")
            year_counts = df_filtered["Year"].value_counts().sort_index()
            fig = px.bar(
                x=year_counts.index,
                y=year_counts.values,
                labels={"x": "Año", "y": "Cantidad"},
                title="Tendencia de Publicaciones"
            )
            st.plotly_chart(fig, use_container_width=True)

        # --- Top 5 Citados ---
        with col_g2:
            st.markdown("#### 🏆 Top 5 Artículos más Citados")
            top5 = df_filtered.sort_values("Cited by", ascending=False).head(5)
            fig2 = px.bar(
                top5,
                x="Cited by",
                y="Title",
                orientation="h",
                title="Artículos con Mayor Impacto",
                labels={"Cited by": "Citaciones", "Title": "Título"}
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ==========================================
    # TAB 3: ANÁLISIS DE TEXTO
    # ==========================================
    with tab3:
        st.subheader("🔤 Frecuencia de Palabras en Abstracts")

        stopwords = set([
            'the','a','in','of','and','to','is','for','with','on','by','at','an','this','that','from','as','are','it','we',
            'player','players','football','soccer','scouting','talent','identification','machine','learning','data','using',
            'used','analysis','team','sports','study','results','proposed','performance','our','based','was','were','their',
            'how','which'
        ])

        words_list = []
        for abstract in df_filtered["Abstract"].dropna():
            words = re.findall(r'\b\w+\b', abstract.lower())
            words_list.extend([w for w in words if w not in stopwords and len(w) > 2])

        word_counts = collections.Counter(words_list).most_common(15)

        if word_counts:
            words_df = pd.DataFrame(word_counts, columns=["Palabra", "Frecuencia"])
            fig3 = px.bar(
                words_df.sort_values("Frecuencia"),
                x="Frecuencia",
                y="Palabra",
                title="Palabras Más Frecuentes en Abstracts"
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No se encontraron suficientes palabras para el análisis.")

else:
    st.info("💡 Sube un archivo CSV desde el menú lateral para comenzar.")
