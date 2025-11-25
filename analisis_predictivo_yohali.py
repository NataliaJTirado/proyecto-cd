"""
================================================================================
ANÁLISIS PREDICTIVO - CAPACIDAD ACADÉMICA UABC 2025-2030
================================================================================
Autor: Yohali
Objetivo: Proyectar matrícula, personal académico y necesidades de contratación

Hipótesis H5 a probar:
"Si las tendencias actuales continúan, la UABC necesitará incrementar su 
planta docente en al menos un 15% para 2030 para mantener ratios óptimos"
================================================================================
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
import glob
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
CARPETA_DATOS = "downloads/processed/"
RATIO_OPTIMO = 12  # Alumnos por profesor (puedes ajustarlo)
AÑOS_PROYECCION = [2025, 2026, 2027, 2028, 2029, 2030]

print("="*80)
print("ANÁLISIS PREDICTIVO - UABC 2025-2030")
print("="*80)

# ============================================================================
# 1. CARGAR DATOS PROCESADOS
# ============================================================================
print("\n📂 Cargando datos procesados...")

try:
    # Cargar datos históricos usando glob para encontrar archivos con timestamp
    archivo_lic = glob.glob(f"{CARPETA_DATOS}Alumnos_Licenciatura_Historico_*_limpio.csv")[0]
    archivo_pos = glob.glob(f"{CARPETA_DATOS}Alumnos_Posgrado_Historico_*_limpio.csv")[0]
    archivo_personal = glob.glob(f"{CARPETA_DATOS}Personal_Academico_Historico_*_limpio.csv")[0]
    archivo_sni = glob.glob(f"{CARPETA_DATOS}Personal_SNI_Historico_*_limpio.csv")[0]
    
    df_alumnos_lic = pd.read_csv(archivo_lic)
    df_alumnos_pos = pd.read_csv(archivo_pos)
    df_personal = pd.read_csv(archivo_personal)
    df_sni = pd.read_csv(archivo_sni)
    
    print("✓ Datos cargados correctamente")
    print(f"  - Alumnos licenciatura: {len(df_alumnos_lic)} registros")
    print(f"  - Alumnos posgrado: {len(df_alumnos_pos)} registros")
    print(f"  - Personal académico: {len(df_personal)} registros")
    print(f"  - Personal SNI: {len(df_sni)} registros")
    
except Exception as e:
    print(f"❌ Error al cargar datos: {e}")
    print("\nAsegúrate de haber ejecutado 'python ejecutar_limpieza.py' primero")
    exit()

# ============================================================================
# 2. PREPARAR DATOS PARA PROYECCIONES
# ============================================================================
print("\n📊 Preparando datos para proyecciones...")

# Extraer año de la columna periodo (formato: 2024-1, 2024-2)
df_alumnos_lic['Año'] = df_alumnos_lic['periodo'].str.split('-').str[0].astype(int)
df_alumnos_pos['Año'] = df_alumnos_pos['periodo'].str.split('-').str[0].astype(int)
df_personal['Año'] = df_personal['periodo'].str.split('-').str[0].astype(int)
df_sni['Año'] = df_sni['periodo'].str.split('-').str[0].astype(int)

# Renombrar columnas con los nombres reales de los archivos
df_alumnos_lic.rename(columns={'recuento_alumnos_de_licenciatura': 'Alumnos'}, inplace=True)
df_alumnos_pos.rename(columns={'uabc': 'Alumnos'}, inplace=True)
df_personal.rename(columns={'recuento': 'Personal_Academico'}, inplace=True)
df_sni.rename(columns={'recuento': 'Total_SNI'}, inplace=True)

# Totales anuales (promediar los dos semestres por año)
matricula_lic_anual = df_alumnos_lic.groupby('Año')['Alumnos'].mean().reset_index()
matricula_pos_anual = df_alumnos_pos.groupby('Año')['Alumnos'].mean().reset_index()
personal_anual = df_personal.groupby('Año')['Personal_Academico'].mean().reset_index()
sni_anual = df_sni.groupby('Año')['Total_SNI'].mean().reset_index()

# Calcular matrícula total
matricula_total = pd.merge(
    matricula_lic_anual, 
    matricula_pos_anual, 
    on='Año', 
    suffixes=('_Lic', '_Pos')
)
matricula_total['Total'] = matricula_total['Alumnos_Lic'] + matricula_total['Alumnos_Pos']

print("✓ Datos preparados")
print(f"  Años disponibles: {sorted(matricula_total['Año'].unique())}")

# ============================================================================
# 3. FUNCIÓN PARA HACER PROYECCIONES
# ============================================================================

def proyectar_con_regresion(df, columna_x, columna_y, años_futuro):
    """
    Proyecta valores futuros usando regresión lineal
    """
    # Preparar datos
    X = df[[columna_x]].values
    y = df[columna_y].values
    
    # Entrenar modelo
    modelo = LinearRegression()
    modelo.fit(X, y)
    
    # R² del modelo
    y_pred = modelo.predict(X)
    r2 = r2_score(y, y_pred)
    
    # Proyecciones
    X_futuro = np.array(años_futuro).reshape(-1, 1)
    proyecciones = modelo.predict(X_futuro)
    
    # Intervalo de confianza (aproximado)
    residuos = y - y_pred
    std_residuos = np.std(residuos)
    ic_95 = 1.96 * std_residuos
    
    return {
        'proyecciones': proyecciones,
        'r2': r2,
        'ic_95': ic_95,
        'modelo': modelo
    }

# ============================================================================
# 4. PROYECCIÓN 1: MATRÍCULA ESTUDIANTIL 2025-2030
# ============================================================================
print("\n" + "="*80)
print("📈 PROYECCIÓN 1: MATRÍCULA ESTUDIANTIL 2025-2030")
print("="*80)

# Proyectar matrícula total
resultado_matricula = proyectar_con_regresion(
    matricula_total, 
    'Año', 
    'Total', 
    AÑOS_PROYECCION
)

print(f"\n📊 Matrícula Proyectada:")
print(f"  R² del modelo: {resultado_matricula['r2']:.4f}")
print(f"\n  Año | Matrícula Estimada | IC 95%")
print("  " + "-"*50)
for año, valor in zip(AÑOS_PROYECCION, resultado_matricula['proyecciones']):
    ic = resultado_matricula['ic_95']
    print(f"  {año} | {valor:,.0f} alumnos | ±{ic:,.0f}")

# Crear visualización
fig1 = go.Figure()

# Datos históricos
fig1.add_trace(go.Scatter(
    x=matricula_total['Año'],
    y=matricula_total['Total'],
    mode='lines+markers',
    name='Histórico',
    line=dict(color='blue', width=3),
    marker=dict(size=8)
))

# Proyecciones
fig1.add_trace(go.Scatter(
    x=AÑOS_PROYECCION,
    y=resultado_matricula['proyecciones'],
    mode='lines+markers',
    name='Proyección',
    line=dict(color='red', width=3, dash='dash'),
    marker=dict(size=8)
))

# Intervalo de confianza
fig1.add_trace(go.Scatter(
    x=AÑOS_PROYECCION,
    y=resultado_matricula['proyecciones'] + resultado_matricula['ic_95'],
    mode='lines',
    name='IC 95% Superior',
    line=dict(width=0),
    showlegend=False
))

fig1.add_trace(go.Scatter(
    x=AÑOS_PROYECCION,
    y=resultado_matricula['proyecciones'] - resultado_matricula['ic_95'],
    mode='lines',
    name='IC 95%',
    line=dict(width=0),
    fillcolor='rgba(255, 0, 0, 0.2)',
    fill='tonexty'
))

fig1.update_layout(
    title='Proyección de Matrícula Total UABC 2025-2030',
    xaxis_title='Año',
    yaxis_title='Número de Alumnos',
    hovermode='x unified',
    template='plotly_white',
    height=500
)

fig1.write_html("proyeccion_matricula_2025_2030.html")
print("\n✓ Visualización guardada: proyeccion_matricula_2025_2030.html")

# ============================================================================
# 5. PROYECCIÓN 2: PERSONAL ACADÉMICO NECESARIO
# ============================================================================
print("\n" + "="*80)
print("👥 PROYECCIÓN 2: PERSONAL ACADÉMICO NECESARIO 2025-2030")
print("="*80)

# Proyectar personal académico con tendencia actual
resultado_personal = proyectar_con_regresion(
    personal_anual,
    'Año',
    'Personal_Academico',
    AÑOS_PROYECCION
)

# Calcular personal necesario para mantener ratio óptimo
personal_necesario = resultado_matricula['proyecciones'] / RATIO_OPTIMO

# Personal actual (último año disponible)
personal_actual = personal_anual['Personal_Academico'].iloc[-1]

print(f"\n📊 Personal Académico Proyectado:")
print(f"  R² del modelo: {resultado_personal['r2']:.4f}")
print(f"  Personal actual (2024): {personal_actual:,.0f} académicos")
print(f"  Ratio objetivo: {RATIO_OPTIMO} alumnos/profesor")
print(f"\n  Año | Con Tendencia | Necesario Ratio {RATIO_OPTIMO} | Diferencia")
print("  " + "-"*70)

diferencias = []
for año, proyectado, necesario in zip(AÑOS_PROYECCION, resultado_personal['proyecciones'], personal_necesario):
    diferencia = necesario - proyectado
    diferencias.append(diferencia)
    print(f"  {año} | {proyectado:,.0f} | {necesario:,.0f} | {diferencia:+,.0f}")

# Calcular incremento necesario total para 2030
incremento_necesario = (personal_necesario[-1] - personal_actual) / personal_actual * 100
print(f"\n🎯 HIPÓTESIS H5:")
print(f"  Incremento necesario 2024→2030: {incremento_necesario:.1f}%")
if incremento_necesario >= 15:
    print(f"  ✓ La hipótesis H5 se CONFIRMA (necesita ≥15%)")
else:
    print(f"  ✗ La hipótesis H5 se RECHAZA (necesita <15%)")

# Visualización
fig2 = go.Figure()

# Personal con tendencia actual
fig2.add_trace(go.Scatter(
    x=list(personal_anual['Año']) + AÑOS_PROYECCION,
    y=list(personal_anual['Personal_Academico']) + list(resultado_personal['proyecciones']),
    mode='lines+markers',
    name='Con Tendencia Actual',
    line=dict(color='orange', width=3)
))

# Personal necesario para ratio óptimo
años_completos = list(matricula_total['Año']) + AÑOS_PROYECCION
personal_necesario_historico = matricula_total['Total'] / RATIO_OPTIMO
personal_completo = list(personal_necesario_historico) + list(personal_necesario)

fig2.add_trace(go.Scatter(
    x=años_completos,
    y=personal_completo,
    mode='lines+markers',
    name=f'Necesario (Ratio {RATIO_OPTIMO}:1)',
    line=dict(color='green', width=3, dash='dash')
))

fig2.update_layout(
    title=f'Personal Académico: Tendencia vs Necesario (Ratio {RATIO_OPTIMO}:1)',
    xaxis_title='Año',
    yaxis_title='Número de Académicos',
    hovermode='x unified',
    template='plotly_white',
    height=500
)

fig2.write_html("proyeccion_personal_academico_2025_2030.html")
print("\n✓ Visualización guardada: proyeccion_personal_academico_2025_2030.html")

# ============================================================================
# 6. PROYECCIÓN 3: RATIO ALUMNOS-PROFESOR
# ============================================================================
print("\n" + "="*80)
print("📏 PROYECCIÓN 3: RATIO ALUMNOS-PROFESOR 2025-2030")
print("="*80)

# Calcular ratios históricos
ratios_historicos = matricula_total['Total'] / personal_anual['Personal_Academico']

# Ratios proyectados con tendencia actual
ratios_proyectados = resultado_matricula['proyecciones'] / resultado_personal['proyecciones']

print(f"\n📊 Evolución del Ratio:")
print(f"  Año | Ratio Proyectado | vs Óptimo ({RATIO_OPTIMO})")
print("  " + "-"*50)
for año, ratio in zip(AÑOS_PROYECCION, ratios_proyectados):
    diferencia = ratio - RATIO_OPTIMO
    indicador = "⚠️" if ratio > RATIO_OPTIMO * 1.1 else "✓"
    print(f"  {año} | {ratio:.1f}:1 | {diferencia:+.1f} {indicador}")

# Visualización
fig3 = go.Figure()

# Ratio histórico
fig3.add_trace(go.Scatter(
    x=matricula_total['Año'],
    y=ratios_historicos,
    mode='lines+markers',
    name='Histórico',
    line=dict(color='blue', width=3)
))

# Ratio proyectado
fig3.add_trace(go.Scatter(
    x=AÑOS_PROYECCION,
    y=ratios_proyectados,
    mode='lines+markers',
    name='Proyectado',
    line=dict(color='red', width=3, dash='dash')
))

# Línea de ratio óptimo
todos_años = list(matricula_total['Año']) + AÑOS_PROYECCION
fig3.add_hline(
    y=RATIO_OPTIMO, 
    line_dash="dot", 
    line_color="green",
    annotation_text=f"Ratio Óptimo ({RATIO_OPTIMO}:1)"
)

fig3.update_layout(
    title='Evolución y Proyección del Ratio Alumnos-Profesor',
    xaxis_title='Año',
    yaxis_title='Ratio (Alumnos por Profesor)',
    hovermode='x unified',
    template='plotly_white',
    height=500
)

fig3.write_html("proyeccion_ratio_alumnos_profesor.html")
print("\n✓ Visualización guardada: proyeccion_ratio_alumnos_profesor.html")

# ============================================================================
# 7. PROYECCIÓN 4: ACADÉMICOS EN EL SNI
# ============================================================================
print("\n" + "="*80)
print("🔬 PROYECCIÓN 4: ACADÉMICOS EN EL SNI 2025-2030")
print("="*80)

# Proyectar SNI
resultado_sni = proyectar_con_regresion(
    sni_anual,
    'Año',
    'Total_SNI',
    AÑOS_PROYECCION
)

print(f"\n📊 Académicos SNI Proyectados:")
print(f"  R² del modelo: {resultado_sni['r2']:.4f}")
print(f"\n  Año | SNI Estimado | Crecimiento vs {int(sni_anual['Año'].iloc[-1])}")
print("  " + "-"*50)

sni_base = sni_anual['Total_SNI'].iloc[-1]
for año, valor in zip(AÑOS_PROYECCION, resultado_sni['proyecciones']):
    crecimiento = (valor - sni_base) / sni_base * 100
    print(f"  {año} | {valor:,.0f} académicos | {crecimiento:+.1f}%")

# Visualización
fig4 = go.Figure()

fig4.add_trace(go.Scatter(
    x=sni_anual['Año'],
    y=sni_anual['Total_SNI'],
    mode='lines+markers',
    name='Histórico',
    line=dict(color='purple', width=3)
))

fig4.add_trace(go.Scatter(
    x=AÑOS_PROYECCION,
    y=resultado_sni['proyecciones'],
    mode='lines+markers',
    name='Proyección',
    line=dict(color='orange', width=3, dash='dash')
))

fig4.update_layout(
    title='Proyección de Académicos en el SNI 2025-2030',
    xaxis_title='Año',
    yaxis_title='Número de Académicos SNI',
    hovermode='x unified',
    template='plotly_white',
    height=500
)

fig4.write_html("proyeccion_sni_2025_2030.html")
print("\n✓ Visualización guardada: proyeccion_sni_2025_2030.html")

# ============================================================================
# 8. PROYECCIÓN 5: NECESIDADES DE CONTRATACIÓN ANUAL
# ============================================================================
print("\n" + "="*80)
print("📋 PROYECCIÓN 5: NECESIDADES DE CONTRATACIÓN ANUAL")
print("="*80)

# Calcular contrataciones necesarias año por año
contrataciones_anuales = []
personal_acumulado = personal_actual

print(f"\n📊 Plan de Contrataciones 2025-2030:")
print(f"  Personal actual (2024): {personal_actual:,.0f}")
print(f"\n  Año | Personal Necesario | Contrataciones Anuales | Acumulado")
print("  " + "-"*70)

for i, (año, necesario) in enumerate(zip(AÑOS_PROYECCION, personal_necesario)):
    if i == 0:
        contratacion = necesario - personal_actual
    else:
        contratacion = necesario - personal_necesario[i-1]
    
    contrataciones_anuales.append(contratacion)
    personal_acumulado += contratacion
    
    print(f"  {año} | {necesario:,.0f} | +{contratacion:,.0f} | {personal_acumulado:,.0f}")

total_contrataciones = sum(contrataciones_anuales)
print(f"\n  📌 Total de contrataciones necesarias 2025-2030: {total_contrataciones:,.0f}")
print(f"  📌 Promedio anual: {total_contrataciones/6:,.0f} académicos")

# Visualización
fig5 = go.Figure()

fig5.add_trace(go.Bar(
    x=AÑOS_PROYECCION,
    y=contrataciones_anuales,
    name='Contrataciones Necesarias',
    marker_color='teal',
    text=[f'{int(x):,}' for x in contrataciones_anuales],
    textposition='outside'
))

fig5.add_hline(
    y=np.mean(contrataciones_anuales),
    line_dash="dash",
    line_color="red",
    annotation_text=f"Promedio: {np.mean(contrataciones_anuales):,.0f}"
)

fig5.update_layout(
    title='Necesidades de Contratación Anual 2025-2030',
    xaxis_title='Año',
    yaxis_title='Número de Contrataciones',
    template='plotly_white',
    height=500
)

fig5.write_html("necesidades_contratacion_anual.html")
print("\n✓ Visualización guardada: necesidades_contratacion_anual.html")

# ============================================================================
# 9. RESUMEN EJECUTIVO
# ============================================================================
print("\n" + "="*80)
print("📊 RESUMEN EJECUTIVO - ANÁLISIS PREDICTIVO")
print("="*80)

print(f"""
PROYECCIONES CLAVE PARA 2030:

1. MATRÍCULA ESTUDIANTIL
   • Matrícula actual (2024): {matricula_total['Total'].iloc[-1]:,.0f} alumnos
   • Matrícula proyectada 2030: {resultado_matricula['proyecciones'][-1]:,.0f} alumnos
   • Crecimiento: {((resultado_matricula['proyecciones'][-1]/matricula_total['Total'].iloc[-1])-1)*100:.1f}%

2. PERSONAL ACADÉMICO
   • Personal actual (2024): {personal_actual:,.0f} académicos
   • Personal necesario 2030: {personal_necesario[-1]:,.0f} académicos
   • Incremento necesario: {incremento_necesario:.1f}%
   • Total contrataciones 2025-2030: {total_contrataciones:,.0f}

3. RATIO ALUMNOS-PROFESOR
   • Ratio actual: {ratios_historicos.iloc[-1]:.1f}:1
   • Ratio proyectado 2030: {ratios_proyectados[-1]:.1f}:1
   • Ratio óptimo objetivo: {RATIO_OPTIMO}:1

4. ACADÉMICOS SNI
   • SNI actual: {sni_base:,.0f}
   • SNI proyectado 2030: {resultado_sni['proyecciones'][-1]:,.0f}
   • Incremento: {((resultado_sni['proyecciones'][-1]/sni_base)-1)*100:.1f}%

VALIDACIÓN HIPÓTESIS H5:
{"✓ CONFIRMADA" if incremento_necesario >= 15 else "✗ RECHAZADA"} - Se requiere incremento de {incremento_necesario:.1f}% 
(hipótesis planteaba ≥15%)
""")

# ============================================================================
# 10. GUARDAR RESULTADOS EN CSV
# ============================================================================
print("\n💾 Guardando resultados en CSV...")

# DataFrame con todas las proyecciones
df_proyecciones = pd.DataFrame({
    'Año': AÑOS_PROYECCION,
    'Matricula_Proyectada': resultado_matricula['proyecciones'],
    'Personal_Con_Tendencia': resultado_personal['proyecciones'],
    'Personal_Necesario': personal_necesario,
    'Contrataciones_Anuales': contrataciones_anuales,
    'Ratio_Proyectado': ratios_proyectados,
    'SNI_Proyectado': resultado_sni['proyecciones']
})

df_proyecciones.to_csv('proyecciones_2025_2030.csv', index=False)
print("✓ Resultados guardados en: proyecciones_2025_2030.csv")

# ============================================================================
# FIN DEL ANÁLISIS
# ============================================================================
print("\n" + "="*80)
print("✅ ANÁLISIS PREDICTIVO COMPLETADO")
print("="*80)
print("\nArchivos generados:")
print("  1. proyeccion_matricula_2025_2030.html")
print("  2. proyeccion_personal_academico_2025_2030.html")
print("  3. proyeccion_ratio_alumnos_profesor.html")
print("  4. proyeccion_sni_2025_2030.html")
print("  5. necesidades_contratacion_anual.html")
print("  6. proyecciones_2025_2030.csv")
print("\nAbre los archivos .html en tu navegador para ver las visualizaciones interactivas.")
print("="*80)