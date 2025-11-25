"""
Dashboard de Análisis de Capacidad Académica - UABC
Proyecto: Evolución y Proyección de la Capacidad Académica Institucional
"""

import streamlit as st
import pandas as pd
import os
import glob
from pathlib import Path

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
# FUNCIONES AUXILIARES
# ============================================================================

@st.cache_data
def cargar_reportes():
    """Carga todos los reportes de limpieza disponibles"""
    reportes_path = "downloads/reportes"
    reportes = {}

    if not os.path.exists(reportes_path):
        return {}

    for archivo in glob.glob(f"{reportes_path}/*_reporte.txt"):
        nombre = os.path.basename(archivo).replace("_reporte.txt", "")
        with open(archivo, 'r', encoding='utf-8') as f:
            reportes[nombre] = f.read()

    return reportes

@st.cache_data
def obtener_estadisticas_datasets():
    """Obtiene estadísticas de los datasets procesados"""
    processed_path = "downloads/processed"
    raw_path = "downloads/raw"

    stats = []

    if not os.path.exists(processed_path):
        return pd.DataFrame()

    for archivo in glob.glob(f"{processed_path}/*_limpio.csv"):
        nombre_base = os.path.basename(archivo).replace("_limpio.csv", "")

        # Cargar dataset limpio
        df_limpio = pd.read_csv(archivo)

        # Buscar archivo original
        archivo_raw = None
        for ext in ['.xls', '.xlsx']:
            posible = f"{raw_path}/{nombre_base}{ext}"
            if os.path.exists(posible):
                archivo_raw = posible
                break

        # Obtener info del archivo original
        filas_raw = 0
        cols_raw = 0
        if archivo_raw:
            try:
                if archivo_raw.endswith('.xls'):
                    dfs = pd.read_html(archivo_raw, encoding='utf-8')
                    df_raw = dfs[0] if dfs else pd.DataFrame()
                else:
                    df_raw = pd.read_excel(archivo_raw)
                filas_raw = len(df_raw)
                cols_raw = len(df_raw.columns)
            except:
                pass

        stats.append({
            'Dataset': nombre_base.replace('_', ' '),
            'Filas Originales': filas_raw,
            'Filas Limpias': len(df_limpio),
            'Filas Removidas': filas_raw - len(df_limpio),
            'Columnas Originales': cols_raw,
            'Columnas Limpias': len(df_limpio.columns),
            'Columnas Removidas': cols_raw - len(df_limpio.columns)
        })

    return pd.DataFrame(stats)

# ============================================================================
# PÁGINA: LIMPIEZA DE DATOS
# ============================================================================

if pagina == "Limpieza de Datos":
    st.title("Reporte de Limpieza de Datos")
    st.markdown("---")

    # Cargar reportes y estadísticas
    reportes = cargar_reportes()
    stats_df = obtener_estadisticas_datasets()

    if stats_df.empty:
        st.warning("No se encontraron datos procesados. Ejecuta primero el script de limpieza (ejecutar_limpieza.py)")
    else:
        # ============================================================
        # SECCIÓN 1: RESUMEN GENERAL
        # ============================================================
        st.header("1. Resumen General de la Limpieza")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Datasets Procesados",
                len(stats_df)
            )

        with col2:
            total_filas_removidas = stats_df['Filas Removidas'].sum()
            st.metric(
                "Total Filas Removidas",
                f"{total_filas_removidas:,}"
            )

        with col3:
            total_columnas_removidas = stats_df['Columnas Removidas'].sum()
            st.metric(
                "Total Columnas Removidas",
                total_columnas_removidas
            )

        with col4:
            total_filas_finales = stats_df['Filas Limpias'].sum()
            st.metric(
                "Total Filas Finales",
                f"{total_filas_finales:,}"
            )

        st.markdown("---")

        # ============================================================
        # SECCIÓN 2: TABLA DE ESTADÍSTICAS
        # ============================================================
        st.header("2. Estadísticas por Dataset")

        # Calcular porcentajes
        stats_display = stats_df.copy()
        stats_display['% Filas Removidas'] = (
            (stats_display['Filas Removidas'] / stats_display['Filas Originales'] * 100)
            .fillna(0)
            .round(2)
        )

        # Mostrar tabla
        st.dataframe(
            stats_display,
            use_container_width=True,
            hide_index=True
        )

        # Opción de descarga
        csv = stats_display.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="Descargar estadísticas (CSV)",
            data=csv,
            file_name="estadisticas_limpieza.csv",
            mime="text/csv"
        )

        st.markdown("---")

        # ============================================================
        # SECCIÓN 3: REPORTES DETALLADOS
        # ============================================================
        st.header("3. Reportes Detallados por Dataset")

        if reportes:
            # Selector de dataset
            dataset_seleccionado = st.selectbox(
                "Selecciona un dataset para ver su reporte:",
                options=list(reportes.keys()),
                format_func=lambda x: x.replace('_', ' ')
            )

            if dataset_seleccionado:
                st.subheader(f"Reporte: {dataset_seleccionado.replace('_', ' ')}")

                # Mostrar reporte en un contenedor
                with st.expander("Ver reporte completo", expanded=True):
                    st.text(reportes[dataset_seleccionado])

                # Mostrar vista previa de datos
                st.subheader("Vista Previa de Datos Limpios")

                archivo_csv = f"downloads/processed/{dataset_seleccionado}_limpio.csv"
                if os.path.exists(archivo_csv):
                    df = pd.read_csv(archivo_csv)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Filas", len(df))
                    with col2:
                        st.metric("Columnas", len(df.columns))

                    # Mostrar primeras filas
                    st.dataframe(df.head(10), use_container_width=True)

                    # Botón de descarga
                    csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="Descargar dataset limpio (CSV)",
                        data=csv_data,
                        file_name=f"{dataset_seleccionado}_limpio.csv",
                        mime="text/csv"
                    )
        else:
            st.info("No se encontraron reportes. Ejecuta el script de limpieza primero.")

        st.markdown("---")

        # ============================================================
        # SECCIÓN 4: CAMBIOS Y TRANSFORMACIONES
        # ============================================================
        st.header("4. Cambios y Transformaciones Aplicadas")

        st.markdown("""
        ### Transformaciones Aplicadas Durante la Limpieza:

        #### Limpieza General (Todos los Datasets):
        - Nombres de columnas estandarizados (minúsculas, sin espacios)
        - Eliminación de filas completamente vacías
        - Eliminación de columnas completamente vacías
        - Corrección de tipos de datos

        #### Limpieza Específica por Tipo:

        **Alumnos (Licenciatura y Posgrado):**
        - Extracción de año del periodo
        - Validación de rangos de valores
        - Eliminación de duplicados por periodo

        **Personal Académico:**
        - Extracción de año del periodo
        - Normalización de conteos
        - Validación de valores numéricos

        **Cuerpos Académicos:**
        - Normalización de estados/grados
        - Limpieza de nombres de instituciones
        - Validación de campos obligatorios

        **Programas (Licenciatura y Posgrado):**
        - Normalización de nombres de programas
        - Validación de categorías
        - Limpieza de áreas de conocimiento

        **Relación Alumnos-Profesor:**
        - Validación de ratios
        - Normalización de unidades académicas
        """)

        st.markdown("---")

        # ============================================================
        # INFORMACIÓN ADICIONAL
        # ============================================================
        st.info("""
        **Nota:** Los datos limpios están disponibles en formato CSV y Excel en la carpeta `downloads/processed/`.
        Los reportes detallados se encuentran en `downloads/reportes/`.
        """)

# ============================================================================
# PÁGINA: ANÁLISIS DESCRIPTIVO
# ============================================================================

elif pagina == "Análisis Descriptivo":
    st.title(" Análisis Descriptivo")
