"""
Dashboard de Análisis de Capacidad Académica - UABC
Proyecto: Evolución y Proyección de la Capacidad Académica Institucional
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import glob
import re
from pathlib import Path
from scipy.stats import pearsonr, f_oneway

# ============================================================================ 
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Análisis Capacidad Académica UABC",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
        nombre_completo = os.path.basename(archivo).replace("_reporte.txt", "")
        # Limpiar nombre del dataset (quitar timestamp _YYYYMMDD_HHMMSS)
        nombre_limpio = re.sub(r'_\d{8}_\d{6}$', '', nombre_completo)

        with open(archivo, 'r', encoding='utf-8') as f:
            # Usar nombre limpio como clave, pero guardar también el nombre completo
            reportes[nombre_limpio] = {
                'contenido': f.read(),
                'nombre_completo': nombre_completo
            }

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

        # Limpiar nombre del dataset (quitar timestamp _YYYYMMDD_HHMMSS)
        nombre_limpio = re.sub(r'_\d{8}_\d{6}$', '', nombre_base)
        nombre_display = nombre_limpio.replace('_', ' ')

        stats.append({
            'Dataset': nombre_display,
            'Filas Originales': filas_raw,
            'Filas Limpias': len(df_limpio),
            'Filas Removidas': filas_raw - len(df_limpio),
            'Columnas Originales': cols_raw,
            'Columnas Limpias': len(df_limpio.columns),
            'Columnas Removidas': cols_raw - len(df_limpio.columns)
        })

    return pd.DataFrame(stats)

# ============================================================================ 
# FUNCIONES PARA CARGA DE DATOS (para páginas de análisis)
# ============================================================================

PATH = "downloads/processed/"

def cargar(patron):
    """Carga el archivo CSV más reciente que coincida con el patrón"""
    archivos = glob.glob(os.path.join(PATH, f"{patron}*_limpio.csv"))
    if not archivos:
        return None
    archivo_mas_reciente = max(archivos, key=os.path.getmtime)
    return pd.read_csv(archivo_mas_reciente)

def extraer_anio(periodo):
    """Función para extraer año del periodo (2018-2 -> 2018)"""
    try:
        return int(str(periodo).split('-')[0])
    except:
        # si no sigue ese patrón, intentar convertir directo a int si es posible
        try:
            return int(periodo)
        except:
            return None

# Intentar cargar archivos (solo si existen)
try:
    alumnos_lic = cargar("Alumnos_Licenciatura_Historico")
    alumnos_pos = cargar("Alumnos_Posgrado_Historico")
    docentes_hist = cargar("Personal_Academico_Historico")
    sni_hist = cargar("Personal_SNI_Historico")
    programas_lic = cargar("Programas_Licenciatura_Historico")
    programas_pos = cargar("Programas_Posgrado_Historico")
    ratio = cargar("Relacion_AlumnosProfesor_UnidadAcademica")
    datos_cargados = True
except Exception:
    # si falla cualquier lectura, marcar como no cargado para mostrar mensajes
    alumnos_lic = alumnos_pos = docentes_hist = sni_hist = programas_lic = programas_pos = ratio = None
    datos_cargados = False

# ============================================================================ 
# SIDEBAR - NAVEGACIÓN
# ============================================================================

st.sidebar.title("Dashboard UABC")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegación",
    [
        "Inicio",
        "Limpieza de Datos",
        "Datos Limpios",
        "Análisis Descriptivo",
        "Analisis Inferencial",      # <-- sección nueva (sin tilde, tal como pediste)
        "Análisis Predictivo"
    ]
)

# ============================================================================ 
# PÁGINA: INICIO
# ============================================================================

if pagina == "Inicio":
    st.title("📊 Análisis de Capacidad Académica UABC")
    st.markdown("### Evolución y Proyección de la Capacidad Académica Institucional")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📚 Estudiantes (2025)",
            value="70,791",
            delta="Licenciatura + Posgrado"
        )

    with col2:
        st.metric(
            label="👨‍🏫 Académicos",
            value="6,422",
            delta="Año 2025"
        )

    with col3:
        st.metric(
            label="💰 Presupuesto",
            value="$6,135 M",
            delta="Millones de pesos"
        )

    with col4:
        if datos_cargados and sni_hist is not None:
            try:
                st.metric(
                    label="🔬 SNI",
                    value=f"{sni_hist['recuento'].iloc[-1]}",
                    delta=f"+{sni_hist['recuento'].iloc[-1] - sni_hist['recuento'].iloc[0]} desde 2018"
                )
            except Exception:
                st.metric(
                    label="🔬 SNI",
                    value="N/A",
                    delta="Datos no disponibles"
                )
        else:
            st.metric(
                label="🔬 SNI",
                value="N/A",
                delta="Datos no disponibles"
            )

    st.markdown("---")
    st.markdown("""
    ## 🎯 Preguntas de Investigación Descriptivas

    Este dashboard responde a las siguientes preguntas clave:

    1. **¿Cuál ha sido la tasa de crecimiento anual de la matrícula en los últimos 6 años?**
    2. **¿Cómo se distribuye actualmente el personal académico por tipo de contratación?**
    3. **Qué unidades académicas tienen el mayor/menor ratio alumnos-profesor?**
    4. **Cuál ha sido la evolución de los académicos en el SNI?**
    5. **Cómo ha crecido el número de programas educativos acreditados?**

    ---
    """)

# ============================================================================ 
# PÁGINA: LIMPIEZA DE DATOS
# ============================================================================

elif pagina == "Limpieza de Datos":
    st.title("Reporte de Limpieza de Datos")
    st.markdown("---")

    # Cargar reportes y estadísticas
    reportes = cargar_reportes()
    stats_df = obtener_estadisticas_datasets()

    if stats_df.empty:
        st.warning("⚠️ No se encontraron datos procesados. Ejecuta primero el script de limpieza (ejecutar_limpieza.py)")
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

                # Obtener información del reporte
                nombre_completo = reportes[dataset_seleccionado]['nombre_completo']
                contenido_reporte = reportes[dataset_seleccionado]['contenido']

                # Mostrar reporte en un contenedor
                with st.expander("Ver reporte completo", expanded=True):
                    st.text(contenido_reporte)

                # Mostrar vista previa de datos
                st.subheader("Vista Previa de Datos Limpios")

                archivo_csv = f"downloads/processed/{nombre_completo}_limpio.csv"
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

# ============================================================================ 
# PÁGINA: DATOS LIMPIOS
# ============================================================================

elif pagina == "Datos Limpios":
    st.title("📁 Exploración de Datos Limpios")
    st.markdown("---")
    
    st.markdown("""
    Esta sección permite explorar los datasets procesados y realizar consultas básicas.
    """)
    
    processed_path = "downloads/processed"
    
    if not os.path.exists(processed_path):
        st.warning("⚠️ No se encontró la carpeta de datos procesados.")
    else:
        archivos = glob.glob(f"{processed_path}/*_limpio.csv")
        
        if not archivos:
            st.warning("⚠️ No se encontraron archivos procesados.")
        else:
            nombres_archivos = [os.path.basename(f).replace("_limpio.csv", "").replace("_", " ") for f in archivos]
            
            archivo_seleccionado = st.selectbox(
                "Selecciona un dataset:",
                range(len(archivos)),
                format_func=lambda i: nombres_archivos[i]
            )
            
            if archivo_seleccionado is not None:
                df = pd.read_csv(archivos[archivo_seleccionado])
                
                st.subheader(f"Dataset: {nombres_archivos[archivo_seleccionado]}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Filas", len(df))
                with col2:
                    st.metric("Columnas", len(df.columns))
                with col3:
                    st.metric("Memoria", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                
                st.markdown("---")
                
                # Vista previa
                st.subheader("Vista Previa")
                num_filas = st.slider("Número de filas a mostrar:", 5, 100, 10)
                st.dataframe(df.head(num_filas), use_container_width=True)
                
                st.markdown("---")
                
                # Información de columnas
                st.subheader("Información de Columnas")
                
                info_df = pd.DataFrame({
                    'Columna': df.columns,
                    'Tipo': df.dtypes.values,
                    'No Nulos': df.count().values,
                    '% Completo': (df.count().values / len(df) * 100).round(2)
                })
                
                st.dataframe(info_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # Estadísticas descriptivas
                st.subheader("Estadísticas Descriptivas")
                
                if df.select_dtypes(include=['number']).columns.any():
                    st.dataframe(df.describe(), use_container_width=True)
                else:
                    st.info("Este dataset no contiene columnas numéricas.")
                
                st.markdown("---")
                
                # Descarga
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Descargar dataset completo (CSV)",
                    data=csv_data,
                    file_name=f"{nombres_archivos[archivo_seleccionado].replace(' ', '_')}_limpio.csv",
                    mime="text/csv"
                )

# ============================================================================ 
# PÁGINA: ANÁLISIS DESCRIPTIVO
# ============================================================================

elif pagina == "Análisis Descriptivo":
    st.title("📈 Análisis Descriptivo")
    
    if not datos_cargados:
        st.warning("⚠️ No se pudieron cargar los datos necesarios. Asegúrate de que los archivos procesados existen en la carpeta 'downloads/processed'.")
    else:
        st.markdown("---")
        
        # ================================================================
        # PREGUNTA 1: CRECIMIENTO DE MATRÍCULA
        # ================================================================
        
        st.header("1. Crecimiento de la Matrícula Estudiantil")
        
        if alumnos_lic is not None and alumnos_pos is not None:
            # Preparar datos de licenciatura
            alumnos_lic['año'] = alumnos_lic['periodo'].apply(extraer_anio)
            # usar columna 'recuento' si existe, si no usar 'recuento_alumnos_de_licenciatura'
            col_lic = 'recuento' if 'recuento' in alumnos_lic.columns else 'recuento_alumnos_de_licenciatura'
            lic_anual = alumnos_lic.groupby('año')[col_lic].sum().reset_index()
            lic_anual['crecimiento_%'] = lic_anual[col_lic].pct_change() * 100
            
            # Preparar datos de posgrado
            alumnos_pos['año'] = alumnos_pos['periodo'].apply(extraer_anio)
            col_pos = 'recuento' if 'recuento' in alumnos_pos.columns else 'uabc' if 'uabc' in alumnos_pos.columns else None
            if col_pos is None:
                pos_anual = pd.DataFrame({'año': [], 'recuento': []})
            else:
                pos_anual = alumnos_pos.groupby('año')[col_pos].sum().reset_index()
                pos_anual['crecimiento_%'] = pos_anual[col_pos].pct_change() * 100
            
            # Gráfico 1: Evolución de matrícula
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=lic_anual['año'], y=lic_anual[col_lic],
                mode='lines+markers', name='Licenciatura',
                line=dict(color='blue', width=3)
            ))
            if not pos_anual.empty:
                fig1.add_trace(go.Scatter(
                    x=pos_anual['año'], y=pos_anual[col_pos],
                    mode='lines+markers', name='Posgrado',
                    line=dict(color='green', width=3)
                ))
            fig1.update_layout(
                title='Evolución de la Matrícula (2018-2025)',
                xaxis_title='Año',
                yaxis_title='Número de Alumnos',
                hovermode='x unified'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Gráfico 2: Tasa de crecimiento
            fig2 = go.Figure()
            if len(lic_anual) > 1:
                fig2.add_trace(go.Bar(
                    x=lic_anual['año'][1:], y=lic_anual['crecimiento_%'][1:], name='Licenciatura'
                ))
            if not pos_anual.empty and len(pos_anual) > 1:
                fig2.add_trace(go.Bar(
                    x=pos_anual['año'][1:], y=pos_anual['crecimiento_%'][1:], name='Posgrado'
                ))
            fig2.update_layout(
                title='Tasa de Crecimiento Anual (%)',
                xaxis_title='Año',
                yaxis_title='Crecimiento (%)',
                barmode='group'
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Datos de matrícula no disponibles")
        
        # ================================================================
        # PREGUNTA 2: PERSONAL ACADÉMICO
        # ================================================================
        
        st.markdown("---")
        st.header("2. Distribución del Personal Académico")
        
        if docentes_hist is not None:
            docentes_hist['año'] = docentes_hist['periodo'].apply(extraer_anio)
            
            fig3 = px.line(
                docentes_hist, x='periodo', y='recuento',
                markers=True, title='Evolución del Personal Académico'
            )
            fig3.update_layout(
                xaxis_title='Periodo',
                yaxis_title='Número de Académicos'
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Datos de personal académico no disponibles")
        
        # ================================================================
        # PREGUNTA 3: RATIO ALUMNOS-PROFESOR
        # ================================================================
        
        st.markdown("---")
        st.header("3. Ratio Alumnos-Profesor por Unidad Académica")
        
        if ratio is not None:
            ratio_clean = ratio.copy()
            # asegurar nombres esperados
            try:
                ratio_clean.columns = ['campus', 'unidad_academica', 'ratio_licenciatura', 'ratio_posgrado']
            except Exception:
                # si no coincide, intentar mantener lo que haya
                pass
            if 'ratio_licenciatura' in ratio_clean.columns:
                ratio_clean['nombre_completo'] = ratio_clean['campus'] + ' - ' + ratio_clean['unidad_academica']
                ratio_clean = ratio_clean.sort_values('ratio_licenciatura', ascending=True)
            
                fig4 = go.Figure()
                fig4.add_trace(go.Bar(
                    y=ratio_clean['nombre_completo'], x=ratio_clean['ratio_licenciatura'],
                    orientation='h', name='Licenciatura'
                ))
                if 'ratio_posgrado' in ratio_clean.columns:
                    fig4.add_trace(go.Bar(
                        y=ratio_clean['nombre_completo'], x=ratio_clean['ratio_posgrado'],
                        orientation='h', name='Posgrado'
                    ))
                fig4.update_layout(
                    title='Ratio Alumnos-Profesor por Unidad Académica',
                    xaxis_title='Ratio (Alumnos por Profesor)',
                    yaxis_title='Unidad Académica',
                    barmode='group',
                    height=800
                )
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.warning("El dataset de ratios no tiene la estructura esperada.")
        else:
            st.warning("Datos de ratio alumnos-profesor no disponibles")
        
        # ================================================================
        # PREGUNTA 4: EVOLUCIÓN DE MIEMBROS SNI
        # ================================================================
        
        st.markdown("---")
        st.header("4. Evolución del Personal en el SNI")
        
        if sni_hist is not None:
            sni_hist['año'] = sni_hist['periodo'].apply(extraer_anio)
            
            fig5 = px.area(
                sni_hist, x='periodo', y='recuento',
                title='Crecimiento de Miembros del SNI'
            )
            fig5.update_layout(
                xaxis_title='Periodo',
                yaxis_title='Número de Miembros SNI'
            )
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.warning("Datos de SNI no disponibles")
        
        # ================================================================
        # PREGUNTA 5: PROGRAMAS EDUCATIVOS
        # ================================================================
        
        st.markdown("---")
        st.header("5. Crecimiento de Programas Educativos")
        
        if programas_lic is not None and programas_pos is not None:
            programas_lic['año'] = programas_lic['periodo'].apply(extraer_anio)
            programas_pos['año'] = programas_pos['periodo'].apply(extraer_anio)
            
            fig6 = go.Figure()
            # intentar usar la segunda columna como conteo (como en tu código original)
            try:
                y_lic = programas_lic.iloc[:, 1]
            except:
                y_lic = None
            try:
                y_pos = programas_pos.iloc[:, 1]
            except:
                y_pos = None

            if y_lic is not None:
                fig6.add_trace(go.Scatter(
                    x=programas_lic['periodo'], y=y_lic,
                    mode='lines+markers', name='Licenciatura'
                ))
            if y_pos is not None:
                fig6.add_trace(go.Scatter(
                    x=programas_pos['periodo'], y=y_pos,
                    mode='lines+markers', name='Posgrado'
                ))
            fig6.update_layout(
                title='Evolución de Programas Educativos',
                xaxis_title='Periodo',
                yaxis_title='Número de Programas'
            )
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.warning("Datos de programas educativos no disponibles")

# ============================================================================ 
# PÁGINA: ANALISIS INFERENCIAL  (insertada entre descriptivo y predictivo)
# ============================================================================

elif pagina == "Analisis Inferencial":
    st.title("🔍 Analisis Inferencial")

    st.markdown("""
    Esta sección presenta **análisis estadísticos** para probar hipótesis y determinar relaciones significativas entre variables clave de la capacidad académica institucional.
    **Nivel de significancia:** α = 0.05 (95% de confianza)
    """)
    st.markdown("---")

    # Verificar que existan los datasets necesarios
    if alumnos_lic is None or docentes_hist is None:
        st.warning("⚠️ No hay datos suficientes para realizar análisis inferencial. Asegúrate de que los archivos procesados existen en 'downloads/processed'.")
    else:
        # Preparar datos por año
        alumnos_lic['año'] = alumnos_lic['periodo'].apply(extraer_anio)
        docentes_hist['año'] = docentes_hist['periodo'].apply(extraer_anio)

        # seleccionar columna correcta para matrícula licenciatura
        if 'recuento_alumnos_de_licenciatura' in alumnos_lic.columns:
            col_lic_infer = 'recuento_alumnos_de_licenciatura'
        elif 'recuento' in alumnos_lic.columns:
            col_lic_infer = 'recuento'
        else:
            # intentar primera columna numérica
            numeric_cols = alumnos_lic.select_dtypes(include=['number']).columns.tolist()
            col_lic_infer = numeric_cols[0] if numeric_cols else None

        # seleccionar columna correcta para personal académico
        if 'recuento' in docentes_hist.columns:
            col_doc_infer = 'recuento'
        else:
            numeric_cols_doc = docentes_hist.select_dtypes(include=['number']).columns.tolist()
            col_doc_infer = numeric_cols_doc[0] if numeric_cols_doc else None

        if col_lic_infer is None or col_doc_infer is None:
            st.error("No se encontraron columnas numéricas adecuadas para matrícula o personal en los datasets.")
        else:
            # Agrupar por año
            lic_por_anio = alumnos_lic.groupby('año')[col_lic_infer].mean().reset_index()
            personal_por_anio = docentes_hist.groupby('año')[col_doc_infer].mean().reset_index()

            # Asegurar que las series tengan el mismo rango de años para correlación
            merged = pd.merge(lic_por_anio, personal_por_anio, on='año', how='inner', suffixes=('_lic', '_doc'))
            if merged.empty or len(merged) < 2:
                st.info("No hay suficientes puntos (años) emparejados para calcular correlación.")
            else:
                # Tabs de análisis
                tab1, tab2, tab3 = st.tabs([
                    "📈 Matrícula vs Académicos",
                    "🏫 Ratios Campus",
                    "⏰ Desfases"
                ])

                # ==============================================================
                # TAB 1: MATRÍCULA VS PERSONAL ACADÉMICO
                # ==============================================================
                with tab1:
                    st.header("📈 Correlación: Matrícula vs Personal Académico")

                    st.markdown("""
                    **Pregunta:** ¿Existe correlación significativa entre crecimiento de matrícula y personal académico?
                    **Hipótesis H1:** La matrícula ha crecido más que el personal académico.
                    """)

                    # Calcular correlación usando las series emparejadas
                    x = merged[col_lic_infer + '_lic'] if (col_lic_infer + '_lic') in merged.columns else merged[col_lic_infer]
                    y = merged[col_doc_infer + '_doc'] if (col_doc_infer + '_doc') in merged.columns else merged[col_doc_infer]

                    try:
                        r, p_value = pearsonr(x.astype(float), y.astype(float))
                    except Exception:
                        r, p_value = float('nan'), float('nan')

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Correlación (r)", f"{r:.4f}" if pd.notna(r) else "N/A")
                    with col2:
                        st.metric("P-value", f"{p_value:.4f}" if pd.notna(p_value) else "N/A")
                    with col3:
                        if pd.notna(p_value):
                            st.metric("Resultado", "✅ SIGNIFICATIVO" if p_value < 0.05 else "❌ NO SIGNIFICATIVO")
                        else:
                            st.metric("Resultado", "N/A")

                    # Interpretación
                    if pd.notna(r):
                        if abs(r) < 0.3:
                            fuerza = "débil"
                        elif abs(r) < 0.7:
                            fuerza = "moderada"
                        else:
                            fuerza = "fuerte"
                        st.info(f"""
                        **Interpretación:** La correlación entre matrícula y personal académico es **{fuerza}** (r = {r:.4f}).  
                        Con un p-value de {p_value:.4f}, esta relación {'**ES significativa**' if p_value < 0.05 else '**NO es significativa**'} al 95%.
                        """)
                    else:
                        st.info("No fue posible calcular la correlación con los datos disponibles.")

                    # Gráfico de dispersión con línea de tendencia
                    fig = px.scatter(
                        merged,
                        x=x.name,
                        y=y.name,
                        labels={'x': 'Matrícula Licenciatura', 'y': 'Personal Académico'},
                        title='Relación Matrícula vs Personal Académico',
                        trendline="ols"
                    )
                    fig.update_traces(marker=dict(size=12))
                    st.plotly_chart(fig, use_container_width=True)

                    # Tasas de crecimiento (usar primer y último año disponibles)
                    try:
                        tasa_crecimiento_alumnos = ((merged[x.name].iloc[-1] / merged[x.name].iloc[0]) - 1) * 100
                        tasa_crecimiento_personal = ((merged[y.name].iloc[-1] / merged[y.name].iloc[0]) - 1) * 100
                    except Exception:
                        tasa_crecimiento_alumnos = tasa_crecimiento_personal = float('nan')

                    st.markdown("---")
                    st.subheader("📊 Tasas de Crecimiento Comparadas")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Crecimiento Matrícula (primer-último)", f"{tasa_crecimiento_alumnos:.2f}%" if pd.notna(tasa_crecimiento_alumnos) else "N/A")
                    with col2:
                        st.metric("Crecimiento Personal (primer-último)", f"{tasa_crecimiento_personal:.2f}%" if pd.notna(tasa_crecimiento_personal) else "N/A")

                    if pd.notna(tasa_crecimiento_alumnos) and pd.notna(tasa_crecimiento_personal):
                        if tasa_crecimiento_alumnos > tasa_crecimiento_personal:
                            st.warning(f"""
                            ⚠️ **Hallazgo:** La matrícula creció **{tasa_crecimiento_alumnos:.2f}%** 
                            vs **{tasa_crecimiento_personal:.2f}%** de personal.
                            Se confirma la hipótesis H1.
                            """)
                        else:
                            st.success("✅ El personal creció proporcionalmente a la matrícula.")
                    else:
                        st.info("No hay suficientes datos para comparar tasas de crecimiento.")

                # ==============================================================
                # TAB 2: ANOVA ENTRE CAMPUS
                # ==============================================================
                with tab2:
                    st.header("🏫 ANOVA: Ratios entre Campus")

                    if ratio is None:
                        st.info("No hay datos de ratio disponibles para este análisis.")
                    else:
                        ratio_clean = ratio.copy()
                        # intentar normalizar nombres de columnas esperadas
                        try:
                            ratio_clean.columns = ['campus', 'unidad_academica', 'ratio_licenciatura', 'ratio_posgrado']
                        except Exception:
                            pass

                        if 'ratio_licenciatura' not in ratio_clean.columns:
                            st.warning("El dataset de ratios no tiene la columna 'ratio_licenciatura' esperada.")
                        else:
                            # Preparar grupos
                            grupos_campus = []
                            nombres_campus = ratio_clean['campus'].unique()

                            for campus in nombres_campus:
                                datos = ratio_clean[ratio_clean['campus'] == campus]['ratio_licenciatura'].dropna()
                                if len(datos) > 0:
                                    grupos_campus.append(datos.astype(float))

                            if len(grupos_campus) >= 2:
                                try:
                                    f_stat, p_anova = f_oneway(*grupos_campus)
                                except Exception:
                                    f_stat, p_anova = float('nan'), float('nan')

                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("F-estadístico", f"{f_stat:.4f}" if pd.notna(f_stat) else "N/A")
                                with col2:
                                    st.metric("P-value", f"{p_anova:.4f}" if pd.notna(p_anova) else "N/A")
                                with col3:
                                    if pd.notna(p_anova):
                                        st.metric("Resultado", "✅ HAY DIFERENCIAS" if p_anova < 0.05 else "❌ NO HAY DIFERENCIAS")
                                    else:
                                        st.metric("Resultado", "N/A")

                                # Boxplot
                                fig_box = px.box(
                                    ratio_clean,
                                    x='campus',
                                    y='ratio_licenciatura',
                                    color='campus',
                                    title='Distribución de Ratios por Campus'
                                )
                                st.plotly_chart(fig_box, use_container_width=True)

                                # Tabla
                                st.subheader("📊 Estadísticas por Campus")
                                stats_campus = ratio_clean.groupby('campus')['ratio_licenciatura'].agg(
                                    ['mean', 'median', 'std', 'min', 'max']
                                )
                                st.dataframe(stats_campus, use_container_width=True)
                            else:
                                st.info("No hay suficientes grupos para realizar ANOVA.")

                # ==============================================================
                # TAB 3: DESFASES TEMPORALES
                # ==============================================================
                with tab3:
                    st.header("⏰ Desfases Temporales")

                    fig_series = make_subplots(specs=[[{"secondary_y": True}]])
                    fig_series.add_trace(
                        go.Scatter(x=merged['año'], y=merged[x.name], name='Matrícula'),
                        secondary_y=False
                    )
                    fig_series.add_trace(
                        go.Scatter(x=merged['año'], y=merged[y.name], name='Personal Académico'),
                        secondary_y=True
                    )

                    fig_series.update_layout(title="Evolución Temporal: Matrícula vs Personal", height=500)
                    st.plotly_chart(fig_series, use_container_width=True)

                # ==============================================================
                # RESUMEN FINAL
                # ==============================================================
                st.markdown("---")
                st.subheader("📋 Resumen de Resultados")

                resumen = pd.DataFrame({
                    'Análisis': ['Matrícula vs Académicos', 'Ratios entre Campus'],
                    'Correlación/F-stat': [f"r = {r:.4f}" if pd.notna(r) else 'N/A', f"F = {f_stat:.4f}" if 'f_stat' in locals() and pd.notna(f_stat) else 'N/A'],
                    'P-value': [f"{p_value:.4f}" if pd.notna(p_value) else 'N/A', f"{p_anova:.4f}" if 'p_anova' in locals() and pd.notna(p_anova) else 'N/A'],
                    'Resultado': [
                        '✅ Significativo' if pd.notna(p_value) and p_value < 0.05 else '❌ No significativo' if pd.notna(p_value) else 'N/A',
                        '✅ Hay diferencias' if ('p_anova' in locals() and pd.notna(p_anova) and p_anova < 0.05) else '❌ No hay diferencias' if 'p_anova' in locals() and pd.notna(p_anova) else 'N/A'
                    ]
                })

                st.dataframe(resumen, use_container_width=True, hide_index=True)

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
        "proyeccion_sni_2025_2030.html"
    ]
    
    archivos_existen = all(os.path.exists(f) for f in archivos_html)
    
    if not archivos_existen:
        st.warning("⚠️ Las visualizaciones predictivas aún no han sido generadas. Ejecuta el script `analisis_predictivo_yohali.py` primero.")
    else:
        # Tabs para cada proyección
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Matrícula",
            "👥 Personal Académico",
            "📏 Ratio Alumnos-Profesor",
            "🔬 Académicos SNI"
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

# ============================================================================ 
# FOOTER
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Universidad Autónoma de Baja California**  
Proyecto: Evolución y Proyección de Capacidad Académica  
Año: 2024-2025
""")
