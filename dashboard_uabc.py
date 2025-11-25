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

pagina = st.sidebar.radio(
    "Navegación",
    [
        "Limpieza de Datos",
        "Análisis Descriptivo",
        "Análisis Predictivo"
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




# ============================================================================
# PÁGINA: ANÁLISIS PREDICTIVO
# ============================================================================

elif pagina == "Análisis Predictivo":
    st.title("🔮 Análisis Predictivo 2025-2030")
    st.markdown("---")
    
    st.markdown("""
    ## Proyecciones de Capacidad Académica UABC
    
    Este análisis proyecta la evolución de la capacidad académica institucional 
    para el periodo 2025-2030, utilizando modelos de regresión lineal sobre datos históricos.
    """)
    
    # Verificar si existen las visualizaciones
    archivos_html = [
        "proyeccion_matricula_2025_2030.html",
        "proyeccion_personal_academico_2025_2030.html",
        "proyeccion_ratio_alumnos_profesor.html",
        "proyeccion_sni_2025_2030.html",
        "necesidades_contratacion_anual.html"
    ]
    
    archivos_existen = all(os.path.exists(f) for f in archivos_html)
    
    if not archivos_existen:
        st.warning("⚠️ Las visualizaciones predictivas aún no han sido generadas. Ejecuta el script `analisis_predictivo_yohali.py` primero.")
    else:
        # Tabs para cada proyección
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Matrícula",
            "👥 Personal Académico",
            "📏 Ratio Alumnos-Profesor",
            "🔬 Académicos SNI",
            "📋 Contrataciones"
        ])
        
        with tab1:
            st.subheader("Proyección de Matrícula Estudiantil 2025-2030")
            st.markdown("Proyección del crecimiento de la matrícula total (licenciatura + posgrado)")
            
            with open("proyeccion_matricula_2025_2030.html", 'r', encoding='utf-8') as f:
                html_content = f.read()
                st.components.v1.html(html_content, height=600, scrolling=True)
        
        with tab2:
            st.subheader("Personal Académico: Tendencia vs Necesario")
            st.markdown("Comparación entre el crecimiento proyectado con tendencia actual vs personal necesario para mantener ratios óptimos")
            
            with open("proyeccion_personal_academico_2025_2030.html", 'r', encoding='utf-8') as f:
                html_content = f.read()
                st.components.v1.html(html_content, height=600, scrolling=True)
        
        with tab3:
            st.subheader("Evolución del Ratio Alumnos-Profesor")
            st.markdown("Proyección del ratio alumnos-profesor comparado con el objetivo institucional")
            
            with open("proyeccion_ratio_alumnos_profesor.html", 'r', encoding='utf-8') as f:
                html_content = f.read()
                st.components.v1.html(html_content, height=600, scrolling=True)
        
        with tab4:
            st.subheader("Proyección de Académicos en el SNI")
            st.markdown("Crecimiento proyectado del personal académico en el Sistema Nacional de Investigadores")
            
            with open("proyeccion_sni_2025_2030.html", 'r', encoding='utf-8') as f:
                html_content = f.read()
                st.components.v1.html(html_content, height=600, scrolling=True)
        
        with tab5:
            st.subheader("Plan de Contrataciones 2025-2030")
            st.markdown("Necesidades anuales de contratación de personal académico")
            
            with open("necesidades_contratacion_anual.html", 'r', encoding='utf-8') as f:
                html_content = f.read()
                st.components.v1.html(html_content, height=600, scrolling=True)
        
        st.markdown("---")
        
        # Resumen ejecutivo
        st.header("📊 Resumen Ejecutivo")
        
        # Cargar datos del CSV
        if os.path.exists("proyecciones_2025_2030.csv"):
            df_proyecciones = pd.read_csv("proyecciones_2025_2030.csv")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Matrícula Proyectada 2030",
                    f"{df_proyecciones['Matricula_Proyectada'].iloc[-1]:,.0f}",
                    delta=f"+{df_proyecciones['Matricula_Proyectada'].iloc[-1] - df_proyecciones['Matricula_Proyectada'].iloc[0]:,.0f}"
                )
            
            with col2:
                st.metric(
                    "Personal Necesario 2030",
                    f"{df_proyecciones['Personal_Necesario'].iloc[-1]:,.0f}",
                    delta=f"{df_proyecciones['Personal_Necesario'].iloc[-1] - df_proyecciones['Personal_Necesario'].iloc[0]:,.0f}"
                )
            
            with col3:
                st.metric(
                    "Ratio Proyectado 2030",
                    f"{df_proyecciones['Ratio_Proyectado'].iloc[-1]:.1f}:1"
                )
            
            st.markdown("---")
            
            st.subheader("Tabla de Proyecciones Completas")
            st.dataframe(df_proyecciones, use_container_width=True, hide_index=True)
            
            # Descarga
            csv = df_proyecciones.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Descargar proyecciones (CSV)",
                data=csv,
                file_name="proyecciones_2025_2030.csv",
                mime="text/csv"
            )
        
        st.markdown("---")
        
        # Validación de Hipótesis H5
        st.header("🎯 Validación de Hipótesis H5")
        
        st.markdown("""
        **Hipótesis H5:** Si las tendencias actuales continúan, la UABC necesitará 
        incrementar su planta docente en al menos un 15% para 2030 para mantener ratios óptimos.
        
        **Resultado:** ✗ La hipótesis se **RECHAZA**
        
        **Análisis:** Las proyecciones muestran que la UABC cuenta actualmente con un 
        ratio alumnos-profesor de 10.9:1, significativamente mejor que el estándar 
        recomendado de 12:1. Para 2030, el ratio proyectado será de 11.4:1, que sigue 
        siendo excelente.
        
        **Conclusión:** Este hallazgo revela una fortaleza institucional - la UABC ha 
        logrado mantener una planta docente robusta que permite atención de calidad.
        """)





