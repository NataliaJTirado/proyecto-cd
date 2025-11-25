
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import glob

# ====================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ====================================================================

st.set_page_config(
    page_title="Análisis Capacidad Académica UABC",
    layout="wide"
)

# ====================================================================
# CARGA DE DATOS
# ====================================================================

PATH = "downloads/processed/"

def cargar(patron):
    """Carga el archivo CSV más reciente que coincida con el patrón"""
    archivos = glob.glob(os.path.join(PATH, f"{patron}*_limpio.csv"))
    if not archivos:
        raise FileNotFoundError(f"No se encontró ningún archivo que coincida con {patron}")
    archivo_mas_reciente = max(archivos, key=os.path.getmtime)
    return pd.read_csv(archivo_mas_reciente)

# Cargar archivos usando los patrones correctos
alumnos_lic = cargar("Alumnos_Licenciatura_Historico")
alumnos_pos = cargar("Alumnos_Posgrado_Historico")
docentes_hist = cargar("Personal_Academico_Historico")
sni_hist = cargar("Personal_SNI_Historico")
programas_lic = cargar("Programas_Licenciatura_Historico")
programas_pos = cargar("Programas_Posgrado_Historico")
ratio = cargar("Relacion_AlumnosProfesor_UnidadAcademica")

# Función para extraer año del periodo (2018-2 -> 2018)
def extraer_anio(periodo):
    return int(str(periodo).split('-')[0])

# ====================================================================
# SIDEBAR
# ====================================================================

st.sidebar.title("UABC Dashboard")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegación",
    ["Inicio", "Datos Limpios", "Análisis Descriptivo", "Análisis Predictivo"]
)

# ====================================================================
# PÁGINA INICIO
# ====================================================================

if pagina == "Inicio":
    st.title("Análisis de Capacidad Académica UABC")
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
        st.metric(
            label="🔬 SNI",
            value=f"{sni_hist['recuento'].iloc[-1]}",
            delta=f"+{sni_hist['recuento'].iloc[-1] - sni_hist['recuento'].iloc[0]} desde 2018"
        )

    st.markdown("---")
    st.markdown("""
    ## 🎯 Preguntas de Investigación Descriptivas

    Este dashboard responde a las siguientes preguntas clave:

    1. **¿Cuál ha sido la tasa de crecimiento anual de la matrícula en los últimos 6 años?**
    2. **¿Cómo se distribuye actualmente el personal académico por tipo de contratación?**
    3. **¿Qué unidades académicas tienen el mayor/menor ratio alumnos-profesor?**
    4. **¿Cuál ha sido la evolución de los académicos en el SNI?**
    5. **¿Cómo ha crecido el número de programas educativos acreditados?**

    ---
    """)

# ====================================================================
# PÁGINA 1: DATOS LIMPIOS
# ====================================================================

elif pagina == "Datos Limpios":
    st.title("Vista de Datos Limpios")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Alumnos Lic", "Alumnos Pos", "Personal Académico",
        "Personal SNI", "Programas Lic", "Programas Pos", "Ratio Alumnos-Profesor"
    ])

    with tab1:
        st.subheader("Alumnos Licenciatura Histórico")
        st.dataframe(alumnos_lic, use_container_width=True)
        st.download_button(
            "Descargar CSV",
            alumnos_lic.to_csv(index=False),
            "alumnos_licenciatura.csv",
            "text/csv"
        )

    with tab2:
        st.subheader("Alumnos Posgrado Histórico")
        st.dataframe(alumnos_pos, use_container_width=True)
        st.download_button(
            "Descargar CSV",
            alumnos_pos.to_csv(index=False),
            "alumnos_posgrado.csv",
            "text/csv"
        )

    with tab3:
        st.subheader("Personal Académico Histórico")
        st.dataframe(docentes_hist, use_container_width=True)
        st.download_button(
            "Descargar CSV",
            docentes_hist.to_csv(index=False),
            "personal_academico.csv",
            "text/csv"
        )

    with tab4:
        st.subheader("Personal SNI Histórico")
        st.dataframe(sni_hist, use_container_width=True)
        st.download_button(
            "Descargar CSV",
            sni_hist.to_csv(index=False),
            "personal_sni.csv",
            "text/csv"
        )

    with tab5:
        st.subheader("Programas Licenciatura Histórico")
        st.dataframe(programas_lic, use_container_width=True)
        st.download_button(
            "Descargar CSV",
            programas_lic.to_csv(index=False),
            "programas_licenciatura.csv",
            "text/csv"
        )

    with tab6:
        st.subheader("Programas Posgrado Histórico")
        st.dataframe(programas_pos, use_container_width=True)
        st.download_button(
            "Descargar CSV",
            programas_pos.to_csv(index=False),
            "programas_posgrado.csv",
            "text/csv"
        )

    with tab7:
        st.subheader("Relación Alumnos-Profesor por Unidad Académica")
        st.dataframe(ratio, use_container_width=True)
        st.download_button(
            "Descargar CSV",
            ratio.to_csv(index=False),
            "ratio_alumnos_profesor.csv",
            "text/csv"
        )

# ====================================================================
# PÁGINA 2: ANÁLISIS DESCRIPTIVO
# ====================================================================

elif pagina == "Análisis Descriptivo":

    st.title("Análisis Descriptivo de la Capacidad Académica UABC")

    # ================================================================
    # PREGUNTA 1: CRECIMIENTO DE MATRÍCULA
    # ================================================================

    st.markdown("---")
    st.header("Tasa de Crecimiento Anual de la Matrícula (Últimos 6 años)")

    alumnos_lic['año'] = alumnos_lic['periodo'].apply(extraer_anio)
    alumnos_pos['año'] = alumnos_pos['periodo'].apply(extraer_anio)

    col_lic = 'recuento_alumnos_de_licenciatura'
    col_pos = 'uabc'

    lic_anual = alumnos_lic.groupby('año')[col_lic].mean().reset_index()
    pos_anual = alumnos_pos.groupby('año')[col_pos].mean().reset_index()

    lic_anual['crecimiento_%'] = lic_anual[col_lic].pct_change() * 100
    pos_anual['crecimiento_%'] = pos_anual[col_pos].pct_change() * 100

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=lic_anual['año'], y=lic_anual[col_lic],
            mode='lines+markers', name='Licenciatura'
        ))
        fig1.add_trace(go.Scatter(
            x=pos_anual['año'], y=pos_anual[col_pos],
            mode='lines+markers', name='Posgrado'
        ))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=lic_anual['año'][1:], y=lic_anual['crecimiento_%'][1:], name='Licenciatura'
        ))
        fig2.add_trace(go.Bar(
            x=pos_anual['año'][1:], y=pos_anual['crecimiento_%'][1:], name='Posgrado'
        ))
        st.plotly_chart(fig2, use_container_width=True)

    # ================================================================
    # PREGUNTA 2: PERSONAL ACADÉMICO
    # ================================================================

    st.markdown("---")
    st.header("Distribución del Personal Académico")

    docentes_hist['año'] = docentes_hist['periodo'].apply(extraer_anio)

    fig3 = px.line(
        docentes_hist, x='periodo', y='recuento',
        markers=True, title='Evolución del Personal Académico'
    )

    st.plotly_chart(fig3, use_container_width=True)

    # ================================================================
    # PREGUNTA 3: RATIO ALUMNOS-PROFESOR
    # ================================================================

    st.markdown("---")
    st.header("Ratio Alumnos-Profesor por Unidad Académica")

    ratio_clean = ratio.copy()
    ratio_clean.columns = ['campus', 'unidad_academica', 'ratio_licenciatura', 'ratio_posgrado']
    ratio_clean['nombre_completo'] = ratio_clean['campus'] + ' - ' + ratio_clean['unidad_academica']
    ratio_clean = ratio_clean.sort_values('ratio_licenciatura', ascending=True)

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        y=ratio_clean['nombre_completo'], x=ratio_clean['ratio_licenciatura'],
        orientation='h', name='Licenciatura'
    ))

    fig4.add_trace(go.Bar(
        y=ratio_clean['nombre_completo'], x=ratio_clean['ratio_posgrado'],
        orientation='h', name='Posgrado'
    ))

    st.plotly_chart(fig4, use_container_width=True)

    # ================================================================
    # PREGUNTA 4: EVOLUCIÓN DE MIEMBROS SNI
    # ================================================================

    st.markdown("---")
    st.header("Evolución del Personal en el SNI")

    sni_hist['año'] = sni_hist['periodo'].apply(extraer_anio)

    fig5 = px.area(
        sni_hist, x='periodo', y='recuento',
        title='Crecimiento de Miembros del SNI'
    )
    st.plotly_chart(fig5, use_container_width=True)

    # ================================================================
    # PREGUNTA 5: PROGRAMAS EDUCATIVOS
    # ================================================================

    st.markdown("---")
    st.header("Crecimiento de Programas Educativos")

    programas_lic['año'] = programas_lic['periodo'].apply(extraer_anio)
    programas_pos['año'] = programas_pos['periodo'].apply(extraer_anio)

    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=programas_lic['periodo'], y=programas_lic.iloc[:, 1],
        mode='lines+markers', name='Licenciatura'
    ))
    fig6.add_trace(go.Scatter(
        x=programas_pos['periodo'], y=programas_pos.iloc[:, 1],
        mode='lines+markers', name='Posgrado'
    ))
    st.plotly_chart(fig6, use_container_width=True)

# ====================================================================
# PÁGINA 3: ANÁLISIS PREDICTIVO
# ====================================================================

elif pagina == "Análisis Predictivo":

    st.title("🔮 Análisis Predictivo 2025-2030")
    st.markdown("---")
    
    st.markdown("""
    ## Proyecciones de Capacidad Académica UABC
    
    Este análisis proyecta la evolución de la capacidad académica institucional 
    para el periodo 2025-2030, utilizando modelos de regresión lineal sobre datos históricos.
    """)
    
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
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Matrícula",
            "👥 Personal Académico",
            "📏 Ratio Alumnos-Profesor",
            "🔬 Académicos SNI",
            "📋 Contrataciones"
        ])
        
        with tab1:
            st.subheader("Proyección de Matrícula Estudiantil 2025-2030")
            with open("proyeccion_matricula_2025_2030.html", 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)
        
        with tab2:
            st.subheader("Personal Académico: Tendencia vs Necesario")
            with open("proyeccion_personal_academico_2025_2030.html", 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)
        
        with tab3:
            st.subheader("Evolución del Ratio Alumnos-Profesor")
            with open("proyeccion_ratio_alumnos_profesor.html", 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)
        
        with tab4:
            st.subheader("Proyección de Académicos en el SNI")
            with open("proyeccion_sni_2025_2030.html", 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)
        
        with tab5:
            st.subheader("Plan de Contrataciones 2025-2030")
            with open("necesidades_contratacion_anual.html", 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)
        
        st.markdown("---")
        
        # Resumen Ejecutivo
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
            
            st.download_button(
                label="📥 Descargar proyecciones (CSV)",
                data=df_proyecciones.to_csv(index=False),
                file_name="proyecciones_2025_2030.csv",
                mime="text/csv"
            )
        
        # Validación de Hipótesis
        st.markdown("---")
        st.header("🎯 Validación de Hipótesis H5")
        
        st.markdown("""
        **Hipótesis H5:** Si las tendencias actuales continúan, la UABC necesitará 
        incrementar su planta docente en al menos un 15% para 2030 para mantener ratios óptimos.
        
        **Resultado:** ✗ La hipótesis se **RECHAZA**
        
        **Análisis:** Las proyecciones muestran que la UABC cuenta actualmente con un 
        ratio alumnos-profesor de 10.9:1, significativamente mejor que el estándar 
        recomendado de 12:1. Para 2030, el ratio proyectado será de 11.4:1.
        
        **Conclusión:** La UABC ha logrado mantener una planta docente robusta.
        """)

# ====================================================================
# FOOTER
# ====================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Universidad Autónoma de Baja California**  
Proyecto: Evolución y Proyección de Capacidad Académica  
Año: 2024-2025
""")
