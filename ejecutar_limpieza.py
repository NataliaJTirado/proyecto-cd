"""
Script para procesar y limpiar todos los datasets de UABC
Ejecuta la limpieza de datos y guarda los resultados en downloads/processed/
"""

import pandas as pd
import glob
import os
from pathlib import Path
from limpieza import (
    limpiar_dataset,
    generar_reporte_calidad,
    imprimir_reporte_calidad
)


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

CARPETA_RAW = "downloads/raw"
CARPETA_PROCESSED = "downloads/processed"
CARPETA_REPORTES = "downloads/reportes"

# Crear carpetas si no existen
Path(CARPETA_PROCESSED).mkdir(parents=True, exist_ok=True)
Path(CARPETA_REPORTES).mkdir(parents=True, exist_ok=True)


# ============================================================================
# MAPEO DE ARCHIVOS A TIPOS DE DATASET
# ============================================================================

MAPEO_DATASETS = {
    'Alumnos_Licenciatura_Historico': 'alumnos_licenciatura',
    'Alumnos_Posgrado_Historico': 'alumnos_posgrado',
    'Personal_Academico_Historico': 'personal_academico',
    'Personal_SNI_Historico': 'personal_sni',
    'Cuerpos_Academicos_Historico': 'cuerpos',
    'Programas_Licenciatura_Historico': 'programas_licenciatura',
    'Programas_Posgrado_Historico': 'programas_posgrado',
    'Relacion_AlumnosProfesor': 'relacion',
    'CuerposAcademicos_UnidadAcademica': 'cuerpos',
    'CuerposAcademicos_AreaConocimiento': 'cuerpos',
}


# ============================================================================
# FUNCIONES PRINCIPALES
# ============================================================================

def encontrar_archivos_raw():
    """
    Encuentra todos los archivos Excel en la carpeta raw
    
    Returns:
        list: Lista de rutas de archivos
    """
    patrones = [
        f"{CARPETA_RAW}/*.xls",
        f"{CARPETA_RAW}/*.xlsx"
    ]
    
    archivos = []
    for patron in patrones:
        archivos.extend(glob.glob(patron))
    
    return archivos


def extraer_tipo_dataset(nombre_archivo):
    """
    Extrae el tipo de dataset del nombre del archivo
    
    Args:
        nombre_archivo (str): Nombre del archivo
        
    Returns:
        str: Tipo de dataset o 'generico'
    """
    for patron, tipo in MAPEO_DATASETS.items():
        if patron in nombre_archivo:
            return tipo
    
    return 'generico'


def procesar_dataset(ruta_archivo):
    """
    Procesa un dataset individual: carga, limpia, guarda
    
    Args:
        ruta_archivo (str): Ruta al archivo a procesar
        
    Returns:
        dict: Resultados del procesamiento
    """
    nombre_archivo = os.path.basename(ruta_archivo)
    nombre_base = os.path.splitext(nombre_archivo)[0]
    tipo_dataset = extraer_tipo_dataset(nombre_archivo)
    
    print(f"\n{'='*80}")
    print(f"PROCESANDO: {nombre_archivo}")
    print(f"Tipo: {tipo_dataset}")
    print(f"{'='*80}")
    
    try:
        # 1. Cargar datos
        print("\n1. Cargando datos...")
        # Los archivos .xls son en realidad HTML
        if ruta_archivo.endswith('.xls'):
            # read_html retorna una lista de DataFrames, tomamos el primero
            dfs = pd.read_html(ruta_archivo, encoding='utf-8')
            df = dfs[0] if dfs else pd.DataFrame()
        else:
            df = pd.read_excel(ruta_archivo)
        print(f"   [OK] Cargados: {len(df)} filas, {len(df.columns)} columnas")
        
        # 2. Limpiar datos
        print("\n2. Limpiando datos...")
        df_limpio = limpiar_dataset(df, tipo_dataset)
        
        # 3. Generar reporte
        print("\n3. Generando reporte de calidad...")
        reporte = generar_reporte_calidad(df_limpio, nombre_base)
        imprimir_reporte_calidad(reporte)
        
        # 4. Guardar datos limpios
        print("\n4. Guardando datos limpios...")
        archivo_salida_csv = f"{CARPETA_PROCESSED}/{nombre_base}_limpio.csv"

        df_limpio.to_csv(archivo_salida_csv, index=False, encoding='utf-8-sig')

        print(f"   [OK] Guardado CSV: {archivo_salida_csv}")
        
        # 5. Guardar reporte
        archivo_reporte = f"{CARPETA_REPORTES}/{nombre_base}_reporte.txt"
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            f.write(f"REPORTE DE CALIDAD: {nombre_base}\n")
            f.write("="*80 + "\n\n")
            f.write(f"Filas: {reporte['n_filas']}\n")
            f.write(f"Columnas: {reporte['n_columnas']}\n\n")
            f.write("Columnas:\n")
            for col in reporte['columnas']:
                f.write(f"  - {col} ({reporte['tipos_datos'][col]})\n")
                if reporte['valores_nulos'][col] > 0:
                    f.write(f"    Nulos: {reporte['valores_nulos'][col]} ")
                    f.write(f"({reporte['porcentaje_nulos'][col]:.1f}%)\n")
        
        print(f"   [OK] Reporte guardado: {archivo_reporte}")
        
        return {
            'archivo': nombre_archivo,
            'tipo': tipo_dataset,
            'exitoso': True,
            'filas_originales': len(df),
            'filas_finales': len(df_limpio),
            'columnas_originales': len(df.columns),
            'columnas_finales': len(df_limpio.columns)
        }
    
    except Exception as e:
        print(f"\n[ERROR] ERROR al procesar {nombre_archivo}: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'archivo': nombre_archivo,
            'tipo': tipo_dataset,
            'exitoso': False,
            'error': str(e)
        }


def procesar_todos_los_datasets():
    """
    Procesa todos los datasets encontrados en la carpeta raw
    
    Returns:
        list: Lista de resultados de procesamiento
    """
    print("\n" + "="*80)
    print("PROCESAMIENTO MASIVO DE DATASETS - UABC")
    print("="*80)
    
    # Encontrar archivos
    archivos = encontrar_archivos_raw()
    
    if not archivos:
        print(f"\n[AVISO] No se encontraron archivos en {CARPETA_RAW}")
        print(f"   Asegúrate de ejecutar el scraper primero")
        return []
    
    print(f"\n[OK] Encontrados {len(archivos)} archivos para procesar")
    
    # Procesar cada archivo
    resultados = []
    for i, archivo in enumerate(archivos, 1):
        print(f"\n\n{'#'*80}")
        print(f"ARCHIVO {i}/{len(archivos)}")
        print(f"{'#'*80}")
        
        resultado = procesar_dataset(archivo)
        resultados.append(resultado)
    
    return resultados


def imprimir_resumen_procesamiento(resultados):
    """
    Imprime un resumen del procesamiento
    
    Args:
        resultados (list): Lista de resultados de procesamiento
    """
    print("\n\n" + "="*80)
    print("RESUMEN DEL PROCESAMIENTO")
    print("="*80)
    
    exitosos = [r for r in resultados if r['exitoso']]
    fallidos = [r for r in resultados if not r['exitoso']]
    
    print(f"\nESTADISTICAS:")
    print(f"   Total procesados: {len(resultados)}")
    print(f"   [OK] Exitosos: {len(exitosos)}")
    print(f"   [ERROR] Fallidos: {len(fallidos)}")
    
    if exitosos:
        print(f"\n[OK] DATASETS PROCESADOS CORRECTAMENTE:")
        for r in exitosos:
            reduccion_filas = r['filas_originales'] - r['filas_finales']
            reduccion_cols = r['columnas_originales'] - r['columnas_finales']
            
            print(f"\n   • {r['archivo']}")
            print(f"     Tipo: {r['tipo']}")
            print(f"     Filas: {r['filas_originales']} → {r['filas_finales']}", end="")
            if reduccion_filas > 0:
                print(f" (-{reduccion_filas})")
            else:
                print()
            print(f"     Columnas: {r['columnas_originales']} → {r['columnas_finales']}", end="")
            if reduccion_cols > 0:
                print(f" (-{reduccion_cols})")
            else:
                print()
    
    if fallidos:
        print(f"\n[ERROR] DATASETS CON ERRORES:")
        for r in fallidos:
            print(f"\n   • {r['archivo']}")
            print(f"     Error: {r['error']}")
    
    print("\n" + "="*80)
    
    print(f"\nARCHIVOS GENERADOS:")
    print(f"   Datos limpios: {CARPETA_PROCESSED}/")
    print(f"   Reportes: {CARPETA_REPORTES}/")
    
    print("\n" + "="*80 + "\n")


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    """
    Ejecutar el procesamiento masivo
    """
    
    print("""
    ===========================================================================

                  PROCESAMIENTO Y LIMPIEZA DE DATOS - UABC

    ===========================================================================
    """)
    
    # Mostrar configuración
    print("CONFIGURACIÓN:")
    print(f"  Carpeta de entrada: {CARPETA_RAW}")
    print(f"  Carpeta de salida: {CARPETA_PROCESSED}")
    print(f"  Carpeta de reportes: {CARPETA_REPORTES}")
    
    # Confirmar
    respuesta = input("\n¿Deseas continuar con el procesamiento? (s/n): ")
    
    if respuesta.lower() == 's':
        # Procesar todos los datasets
        resultados = procesar_todos_los_datasets()
        
        # Mostrar resumen
        if resultados:
            imprimir_resumen_procesamiento(resultados)
        
        print("\n[OK] PROCESAMIENTO COMPLETADO")
    else:
        print("\nProcesamiento cancelado por el usuario")