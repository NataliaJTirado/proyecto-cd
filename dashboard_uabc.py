"""
Dashboard de Análisis de Capacidad Académica - UABC
Proyecto: Evolución y Proyección de la Capacidad Académica Institucional
"""

import streamlit as st

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Análisis Capacidad Académica UABC",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SIDEBAR - NAVEGACIÓN
# ============================================================================

st.sidebar.title("Dashboard UABC")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegación",
    [
        "Limpieza de Datos",
        "Análisis Descriptivo"
    ]
)

# ============================================================================
# PÁGINA: LIMPIEZA DE DATOS
# ============================================================================

if pagina == "Limpieza de Datos":
    st.title("Limpieza de Datos")

# ============================================================================
# PÁGINA: ANÁLISIS DESCRIPTIVO
# ============================================================================

elif pagina == "Análisis Descriptivo":
    st.title("📈 Análisis Descriptivo")
