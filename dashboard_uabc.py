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
    ["Inicio", "Datos Limpios", "Análisis Descriptivo"]
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

    ### 📌 Navegación
    - **Datos Limpios**: Visualiza las tablas de datos procesados
    - **Análisis Descriptivo**: Respuestas visuales a las 5 preguntas
    """)

# ====================================================================
# PÁGINA 1: LIMPIEZA
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

else:
    st.title("Análisis Descriptivo de la Capacidad Académica UABC")

    # ================================================================
    # PREGUNTA 1: TASA DE CRECIMIENTO DE MATRÍCULA
    # ================================================================

    st.markdown("---")
    st.header("Tasa de Crecimiento Anual de la Matrícula (Últimos 6 años)")

    # Preparar datos
    alumnos_lic['año'] = alumnos_lic['periodo'].apply(extraer_anio)
    alumnos_pos['año'] = alumnos_pos['periodo'].apply(extraer_anio)

    # Columnas correctas
    col_lic = 'recuento_alumnos_de_licenciatura'
    col_pos = 'uabc'  # Total de posgrado

    # Agrupar por año (promedio de los dos semestres)
    lic_anual = alumnos_lic.groupby('año')[col_lic].mean().reset_index()
    pos_anual = alumnos_pos.groupby('año')[col_pos].mean().reset_index()

    # Calcular tasas de crecimiento
    lic_anual['crecimiento_%'] = lic_anual[col_lic].pct_change() * 100
    pos_anual['crecimiento_%'] = pos_anual[col_pos].pct_change() * 100

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de evolución de matrícula
        fig1 = go.Figure()

        fig1.add_trace(go.Scatter(
            x=lic_anual['año'],
            y=lic_anual[col_lic],
            mode='lines+markers',
            name='Licenciatura',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10)
        ))

        fig1.add_trace(go.Scatter(
            x=pos_anual['año'],
            y=pos_anual[col_pos],
            mode='lines+markers',
            name='Posgrado',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=10)
        ))

        fig1.update_layout(
            title="Evolución de la Matrícula por Nivel Educativo",
            xaxis_title="Año",
            yaxis_title="Número de Estudiantes",
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Gráfico de tasas de crecimiento
        fig2 = go.Figure()

        fig2.add_trace(go.Bar(
            x=lic_anual['año'][1:],  # Excluir primer año (sin crecimiento)
            y=lic_anual['crecimiento_%'][1:],
            name='Licenciatura',
            marker_color='#1f77b4'
        ))

        fig2.add_trace(go.Bar(
            x=pos_anual['año'][1:],
            y=pos_anual['crecimiento_%'][1:],
            name='Posgrado',
            marker_color='#ff7f0e'
        ))

        fig2.update_layout(
            title="Tasa de Crecimiento Anual (%)",
            xaxis_title="Año",
            yaxis_title="Crecimiento (%)",
            barmode='group',
            height=400
        )

        fig2.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)

        st.plotly_chart(fig2, use_container_width=True)

    # Tabla resumen
    st.subheader("📋 Resumen Estadístico")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Tasa Promedio Licenciatura",
            f"{lic_anual['crecimiento_%'][1:].mean():.2f}%",
            delta=f"Total: +{lic_anual[col_lic].iloc[-1] - lic_anual[col_lic].iloc[0]:,.0f}"
        )

    with col2:
        st.metric(
            "Tasa Promedio Posgrado",
            f"{pos_anual['crecimiento_%'][1:].mean():.2f}%",
            delta=f"Total: +{pos_anual[col_pos].iloc[-1] - pos_anual[col_pos].iloc[0]:,.0f}"
        )

    with col3:
        total_inicial = lic_anual[col_lic].iloc[0] + pos_anual[col_pos].iloc[0]
        total_final = lic_anual[col_lic].iloc[-1] + pos_anual[col_pos].iloc[-1]
        st.metric(
            "Crecimiento Total",
            f"{((total_final - total_inicial) / total_inicial * 100):.2f}%",
            delta=f"+{total_final - total_inicial:,.0f} estudiantes"
        )

    # ================================================================
    # PREGUNTA 2: DISTRIBUCIÓN DEL PERSONAL ACADÉMICO
    # ================================================================

    st.markdown("---")
    st.header("Distribución del Personal Académico por Tipo de Contratación")

    st.info(
        "**Nota**: Los datos actuales solo muestran el total de personal académico. Se requieren datos adicionales sobre tipos de contratación (PTC, PA, Técnicos Académicos) para responder completamente esta pregunta.")

    docentes_hist['año'] = docentes_hist['periodo'].apply(extraer_anio)

    # Gráfico de evolución del personal académico
    fig3 = px.line(
        docentes_hist,
        x='periodo',
        y='recuento',
        markers=True,
        title='Evolución del Personal Académico Total'
    )

    fig3.update_traces(line_color='#2ca02c', line_width=3, marker=dict(size=10))
    fig3.update_layout(
        xaxis_title="Periodo",
        yaxis_title="Número de Académicos",
        height=400
    )

    st.plotly_chart(fig3, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Personal Académico (2018)",
            f"{docentes_hist['recuento'].iloc[0]:,}"
        )
    with col2:
        st.metric(
            "Personal Académico (Actual)",
            f"{docentes_hist['recuento'].iloc[-1]:,}",
            delta=f"{docentes_hist['recuento'].iloc[-1] - docentes_hist['recuento'].iloc[0]:,}"
        )

    # ================================================================
    # PREGUNTA 3: RATIO ALUMNOS-PROFESOR POR UNIDAD ACADÉMICA
    # ================================================================

    st.markdown("---")
    st.header("Ratio Alumnos-Profesor por Unidad Académica")

    # Limpiar nombres de columnas
    ratio_clean = ratio.copy()
    ratio_clean.columns = ['campus', 'unidad_academica', 'ratio_licenciatura', 'ratio_posgrado']

    # Crear columna combinada de campus-unidad
    ratio_clean['nombre_completo'] = ratio_clean['campus'] + ' - ' + ratio_clean['unidad_academica']

    # Ordenar por ratio de licenciatura
    ratio_clean = ratio_clean.sort_values('ratio_licenciatura', ascending=True)

    # Gráfico de barras horizontales
    fig4 = go.Figure()

    fig4.add_trace(go.Bar(
        y=ratio_clean['nombre_completo'],
        x=ratio_clean['ratio_licenciatura'],
        name='Licenciatura',
        orientation='h',
        marker_color='#1f77b4'
    ))

    fig4.add_trace(go.Bar(
        y=ratio_clean['nombre_completo'],
        x=ratio_clean['ratio_posgrado'],
        name='Posgrado',
        orientation='h',
        marker_color='#ff7f0e'
    ))

    # Línea de promedio
    promedio_lic = ratio_clean['ratio_licenciatura'].mean()

    fig4.update_layout(
        title='Ratio Alumnos-Profesor por Unidad Académica',
        xaxis_title='Ratio Alumnos/Profesor',
        yaxis_title='',
        barmode='group',
        height=800,
        showlegend=True
    )

    fig4.add_vline(x=promedio_lic, line_dash="dash", line_color="red",
                   annotation_text=f"Promedio: {promedio_lic:.2f}")

    st.plotly_chart(fig4, use_container_width=True)

    # Top 5 y Bottom 5
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔴 Mayor Ratio (Mayor carga)")
        top5 = ratio_clean.nlargest(5, 'ratio_licenciatura')[['nombre_completo', 'ratio_licenciatura']]
        st.dataframe(top5, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("🟢 Menor Ratio (Menor carga)")
        bottom5 = ratio_clean.nsmallest(5, 'ratio_licenciatura')[['nombre_completo', 'ratio_licenciatura']]
        st.dataframe(bottom5, hide_index=True, use_container_width=True)

    # ================================================================
    # PREGUNTA 4: EVOLUCIÓN DE ACADÉMICOS EN SNI
    # ================================================================

    st.markdown("---")
    st.header("Evolución de Académicos en el SNI")

    sni_hist['año'] = sni_hist['periodo'].apply(extraer_anio)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Gráfico de área
        fig5 = px.area(
            sni_hist,
            x='periodo',
            y='recuento',
            title='Crecimiento de Miembros del SNI'
        )

        fig5.update_traces(line_color='#9467bd', fillcolor='rgba(148, 103, 189, 0.3)')
        fig5.update_layout(
            xaxis_title="Periodo",
            yaxis_title="Número de Académicos en SNI",
            height=400
        )

        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.metric(
            "Miembros SNI (2018)",
            f"{sni_hist['recuento'].iloc[0]}"
        )
        st.metric(
            "Miembros SNI (Actual)",
            f"{sni_hist['recuento'].iloc[-1]}",
            delta=f"+{sni_hist['recuento'].iloc[-1] - sni_hist['recuento'].iloc[0]}"
        )

        crecimiento_sni = (
                    (sni_hist['recuento'].iloc[-1] - sni_hist['recuento'].iloc[0]) / sni_hist['recuento'].iloc[0] * 100)
        st.metric(
            "Crecimiento Total",
            f"{crecimiento_sni:.1f}%"
        )

    st.info(
        "📌 **Nota**: Se requieren datos adicionales sobre distribución por nivel SNI (Candidato, I, II, III, Emérito) para un análisis más detallado.")

    # ================================================================
    # PREGUNTA 5: PROGRAMAS EDUCATIVOS ACREDITADOS
    # ================================================================

    st.markdown("---")
    st.header("Crecimiento de Programas Educativos")

    programas_lic['año'] = programas_lic['periodo'].apply(extraer_anio)
    programas_pos['año'] = programas_pos['periodo'].apply(extraer_anio)

    # Gráfico combinado
    fig6 = go.Figure()

    # Detectar columna correcta de programas
    col_prog_lic = [col for col in programas_lic.columns if 'recuento' in col.lower() or 'programas' in col.lower()]
    col_prog_pos = [col for col in programas_pos.columns if 'recuento' in col.lower() or 'programas' in col.lower()]

    # Si no encuentra columnas específicas, usar columnas numéricas
    if not col_prog_lic:
        col_prog_lic = [col for col in programas_lic.columns if
                        programas_lic[col].dtype in ['int64', 'float64'] and col != 'fecha']
    if not col_prog_pos:
        col_prog_pos = [col for col in programas_pos.columns if
                        programas_pos[col].dtype in ['int64', 'float64'] and col != 'fecha']

    col_prog_lic = col_prog_lic[0] if col_prog_lic else programas_lic.columns[1]
    col_prog_pos = col_prog_pos[0] if col_prog_pos else programas_pos.columns[1]

    fig6.add_trace(go.Scatter(
        x=programas_lic['periodo'],
        y=programas_lic[col_prog_lic],
        mode='lines+markers',
        name='Licenciatura',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))

    fig6.add_trace(go.Scatter(
        x=programas_pos['periodo'],
        y=programas_pos[col_prog_pos],
        mode='lines+markers',
        name='Posgrado',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=10)
    ))

    fig6.update_layout(
        title='Evolución de Programas Educativos',
        xaxis_title='Periodo',
        yaxis_title='Número de Programas',
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig6, use_container_width=True)

    # Resumen
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Programas Lic (Actual)",
            f"{programas_lic[col_prog_lic].iloc[-1]}",
            delta=f"{programas_lic[col_prog_lic].iloc[-1] - programas_lic[col_prog_lic].iloc[0]}"
        )

    with col2:
        st.metric(
            "Programas Pos (Actual)",
            f"{programas_pos[col_prog_pos].iloc[-1]}",
            delta=f"{programas_pos[col_prog_pos].iloc[-1] - programas_pos[col_prog_pos].iloc[0]}"
        )

    with col3:
        total_prog = programas_lic[col_prog_lic].iloc[-1] + programas_pos[col_prog_pos].iloc[-1]
        st.metric(
            "Total Programas",
            f"{total_prog}"
        )

    st.info(
        "📌 **Nota**: Se requieren datos sobre organismos acreditadores (CACECA, CONAIC, etc.) para un análisis más profundo de la calidad educativa.")

    # ================================================================
    # CONCLUSIONES
    # ================================================================

    st.markdown("---")
    st.header("📌 Conclusiones Generales")

    st.markdown(f"""
    ### Hallazgos Principales:

    1. **Matrícula**: 
       - Crecimiento promedio de **{lic_anual['crecimiento_%'][1:].mean():.2f}%** en licenciatura
       - Crecimiento promedio de **{pos_anual['crecimiento_%'][1:].mean():.2f}%** en posgrado

    2. **Personal Académico**: 
       - De **{docentes_hist['recuento'].iloc[0]:,}** a **{docentes_hist['recuento'].iloc[-1]:,}** académicos
       - Cambio de **{docentes_hist['recuento'].iloc[-1] - docentes_hist['recuento'].iloc[0]:,}** académicos

    3. **Ratio Alumnos-Profesor**: 
       - Promedio institucional: **{promedio_lic:.2f}** alumnos por profesor
       - Variación significativa entre unidades académicas

    4. **SNI**: 
       - Crecimiento de **{crecimiento_sni:.1f}%** en membresía
       - De **{sni_hist['recuento'].iloc[0]}** a **{sni_hist['recuento'].iloc[-1]}** miembros

    5. **Programas Educativos**: 
       - Total actual: **{total_prog}** programas
       - Estabilidad en la oferta educativa

    ### Recomendaciones:
    - Monitorear unidades con ratio alumnos-profesor elevado
    - Continuar fortaleciendo la investigación (SNI)
    - Planificar contrataciones basadas en crecimiento proyectado
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