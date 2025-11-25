import pandas as pd
import numpy as np
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


# ============================================================================

def limpiar_nombres_columnas(df):
    """
    Limpia y estandariza los nombres de columnas
    
    Args:
        df (pd.DataFrame): DataFrame con columnas a limpiar
        
    Returns:
        pd.DataFrame: DataFrame con columnas limpias
    """
    df = df.copy()
    
    # Manejar MultiIndex primero
    if isinstance(df.columns, pd.MultiIndex):
        # Convertir MultiIndex a nombres simples
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]
    
    # Convertir todas las columnas a string
    df.columns = df.columns.astype(str)
    
    # Convertir a minúsculas
    df.columns = df.columns.str.lower()
    
    # Remover espacios extra
    df.columns = df.columns.str.strip()
    
    # Reemplazar espacios por guiones bajos
    df.columns = df.columns.str.replace(' ', '_')
    
    # Remover caracteres especiales excepto guión bajo
    df.columns = df.columns.str.replace(r'[^a-z0-9_]', '', regex=True)
    
    # Remover guiones bajos múltiples
    df.columns = df.columns.str.replace(r'_+', '_', regex=True)
    
    # Remover guiones bajos al inicio/final
    df.columns = df.columns.str.strip('_')
    
    return df


def detectar_y_convertir_tipos(df):
    """
    Detecta y convierte automáticamente los tipos de datos correctos
    
    Args:
        df (pd.DataFrame): DataFrame a convertir
        
    Returns:
        pd.DataFrame: DataFrame con tipos correctos
    """
    df = df.copy()
    
    for col in df.columns:
        # Intentar convertir a numérico
        try:
            # Remover comas de miles si existen
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '')
            
            # Convertir a numérico
            df[col] = pd.to_numeric(df[col], errors='ignore')
        except:
            pass
        
        # Si es string, limpiar espacios
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
    
    return df


def remover_filas_vacias(df, umbral=0.5):
    """
    Remueve filas que están mayormente vacías
    
    Args:
        df (pd.DataFrame): DataFrame a limpiar
        umbral (float): Proporción mínima de valores no nulos (0-1)
        
    Returns:
        pd.DataFrame: DataFrame sin filas vacías
    """
    df = df.copy()
    
    # Calcular proporción de valores no nulos por fila
    proporcion_no_nulos = df.notna().sum(axis=1) / len(df.columns)
    
    # Mantener solo filas que cumplan el umbral
    df_limpio = df[proporcion_no_nulos >= umbral].copy()
    
    filas_removidas = len(df) - len(df_limpio)
    if filas_removidas > 0:
        print(f"[OK] Removidas {filas_removidas} filas vacías")
    
    return df_limpio


def remover_columnas_vacias(df, umbral=0.5):
    """
    Remueve columnas que están mayormente vacías
    
    Args:
        df (pd.DataFrame): DataFrame a limpiar
        umbral (float): Proporción mínima de valores no nulos (0-1)
        
    Returns:
        pd.DataFrame: DataFrame sin columnas vacías
    """
    df = df.copy()
    
    # Calcular proporción de valores no nulos por columna
    proporcion_no_nulos = df.notna().sum() / len(df)
    
    # Columnas a mantener
    columnas_mantener = proporcion_no_nulos[proporcion_no_nulos >= umbral].index
    
    df_limpio = df[columnas_mantener].copy()
    
    columnas_removidas = len(df.columns) - len(df_limpio.columns)
    if columnas_removidas > 0:
        print(f"[OK] Removidas {columnas_removidas} columnas vacías")
    
    return df_limpio


# ============================================================================

def limpiar_periodos(df, columna_periodo='periodo'):
    """
    Limpia y estandariza la columna de periodos (ej: 2018-2, 2019-1)
    
    Args:
        df (pd.DataFrame): DataFrame con columna de periodo
        columna_periodo (str): Nombre de la columna de periodo
        
    Returns:
        pd.DataFrame: DataFrame con periodo estandarizado
    """
    df = df.copy()
    
    if columna_periodo not in df.columns:
        # Intentar encontrar columna de periodo
        posibles = [col for col in df.columns if 'periodo' in col.lower()]
        if posibles:
            columna_periodo = posibles[0]
        else:
            print(f"  No se encontró columna de periodo")
            return df
    
    # Convertir a string
    df[columna_periodo] = df[columna_periodo].astype(str)
    
    # Remover espacios
    df[columna_periodo] = df[columna_periodo].str.strip()
    
    # Estandarizar formato (YYYY-S donde S es 1 o 2)
    # Ejemplos: "2018-2", "2019 1", "2020/2" → "2020-2"
    df[columna_periodo] = df[columna_periodo].str.replace(r'[\s/]+', '-', regex=True)
    
    # Validar formato
    patron = r'^\d{4}-[12]$'
    validos = df[columna_periodo].str.match(patron)
    
    if not validos.all():
        invalidos = df[~validos][columna_periodo].unique()
        print(f"  Periodos inválidos encontrados: {invalidos}")
    
    return df


def agregar_columna_fecha(df, columna_periodo='periodo'):
    """
    Agrega columna de fecha basada en el periodo académico

    Args:
        df (pd.DataFrame): DataFrame con columna de periodo
        columna_periodo (str): Nombre de la columna de periodo

    Returns:
        pd.DataFrame: DataFrame con columna 'fecha' agregada
    """
    df = df.copy()

    if columna_periodo not in df.columns:
        print(f"  Columna '{columna_periodo}' no encontrada")
        return df

    def periodo_a_fecha(periodo):
        """Convierte periodo (ej: 2018-2) a fecha en formato YYYY-MM-DD"""
        try:
            año, semestre = str(periodo).split('-')
            # Semestre 1 = Enero, Semestre 2 = Julio
            mes = '01' if semestre == '1' else '07'
            # Retornar como string en formato ISO
            return f"{año}-{mes}-01"
        except:
            return None

    df['fecha'] = df[columna_periodo].apply(periodo_a_fecha)

    return df


def limpiar_valores_numericos(df, columnas=None):
    """
    Limpia valores numéricos removiendo símbolos y convirtiendo a float
    
    Args:
        df (pd.DataFrame): DataFrame a limpiar
        columnas (list): Lista de columnas a limpiar. Si None, limpia todas las numéricas
        
    Returns:
        pd.DataFrame: DataFrame con valores numéricos limpios
    """
    df = df.copy()
    
    if columnas is None:
        # Detectar columnas numéricas
        columnas = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in columnas:
        if col in df.columns:
            # Convertir a string primero
            df[col] = df[col].astype(str)
            
            # Remover símbolos de moneda, comas, espacios
            df[col] = df[col].str.replace(r'[$,\s]', '', regex=True)
            
            # Convertir a numérico
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def validar_rango_valores(df, columna, min_val=None, max_val=None, 
                          accion='advertir'):
    """
    Valida que los valores estén dentro de un rango esperado
    
    Args:
        df (pd.DataFrame): DataFrame a validar
        columna (str): Nombre de la columna
        min_val (float): Valor mínimo esperado
        max_val (float): Valor máximo esperado
        accion (str): 'advertir', 'remover', o 'corregir'
        
    Returns:
        pd.DataFrame: DataFrame validado
    """
    df = df.copy()
    
    if columna not in df.columns:
        print(f"  Columna '{columna}' no encontrada")
        return df
    
    # Encontrar valores fuera de rango
    fuera_rango = pd.Series([False] * len(df))
    
    if min_val is not None:
        fuera_rango |= df[columna] < min_val
    
    if max_val is not None:
        fuera_rango |= df[columna] > max_val
    
    if fuera_rango.any():
        n_invalidos = fuera_rango.sum()
        
        if accion == 'advertir':
            print(f"  {n_invalidos} valores fuera de rango en '{columna}'")
            print(f"   Valores: {df[fuera_rango][columna].tolist()}")
        
        elif accion == 'remover':
            df = df[~fuera_rango].copy()
            print(f"[OK] Removidas {n_invalidos} filas con valores fuera de rango")
        
        elif accion == 'corregir':
            if min_val is not None:
                df.loc[df[columna] < min_val, columna] = min_val
            if max_val is not None:
                df.loc[df[columna] > max_val, columna] = max_val
            print(f"[OK] Corregidos {n_invalidos} valores fuera de rango")
    
    return df


def detectar_duplicados(df, subset=None):
    """
    Detecta y reporta filas duplicadas
    
    Args:
        df (pd.DataFrame): DataFrame a revisar
        subset (list): Columnas a considerar para duplicados. Si None, usa todas
        
    Returns:
        pd.DataFrame: DataFrame con duplicados marcados
    """
    df = df.copy()
    
    duplicados = df.duplicated(subset=subset, keep=False)
    n_duplicados = duplicados.sum()
    
    if n_duplicados > 0:
        print(f"  {n_duplicados} filas duplicadas encontradas")
        df['es_duplicado'] = duplicados
    else:
        print("[OK] No se encontraron duplicados")
    
    return df


def remover_duplicados(df, subset=None, keep='first'):
    """
    Remueve filas duplicadas
    
    Args:
        df (pd.DataFrame): DataFrame a limpiar
        subset (list): Columnas a considerar. Si None, usa todas
        keep (str): 'first', 'last', o False
        
    Returns:
        pd.DataFrame: DataFrame sin duplicados
    """
    df_antes = len(df)
    df = df.drop_duplicates(subset=subset, keep=keep).copy()
    df_despues = len(df)
    
    removidos = df_antes - df_despues
    if removidos > 0:
        print(f"[OK] Removidas {removidos} filas duplicadas")
    
    return df


# ============================================================================

def limpiar_alumnos_historico(df):
    """
    Limpieza específica para datasets de alumnos históricos
    
    Args:
        df (pd.DataFrame): DataFrame de alumnos históricos
        
    Returns:
        pd.DataFrame: DataFrame limpio
    """
    print("\n[Alumnos] Limpiando datos de alumnos...")
    
    # 1. Limpiar nombres de columnas
    df = limpiar_nombres_columnas(df)
    
    # 2. Limpiar periodos
    df = limpiar_periodos(df)
    
    # 3. Agregar fecha
    df = agregar_columna_fecha(df)
    
    # 4. Detectar y convertir tipos
    df = detectar_y_convertir_tipos(df)
    
    # 5. Remover filas y columnas vacías
    df = remover_filas_vacias(df)
    df = remover_columnas_vacias(df)
    
    # 6. Validar valores (alumnos no pueden ser negativos)
    columnas_numericas = df.select_dtypes(include=[np.number]).columns
    for col in columnas_numericas:
        if col != 'fecha':
            df = validar_rango_valores(df, col, min_val=0, accion='advertir')
    
    # 7. Remover duplicados
    df = remover_duplicados(df, subset=['periodo'])
    
    # 8. Ordenar por periodo
    df = df.sort_values('periodo').reset_index(drop=True)
    
    print("[OK] Limpieza completada\n")
    
    return df


def limpiar_personal_historico(df):
    """
    Limpieza específica para datasets de personal académico histórico
    
    Args:
        df (pd.DataFrame): DataFrame de personal histórico
        
    Returns:
        pd.DataFrame: DataFrame limpio
    """
    print("\n[Personal] Limpiando datos de personal academico...")
    
    # Aplicar limpieza similar a alumnos
    df = limpiar_nombres_columnas(df)
    df = limpiar_periodos(df)
    df = agregar_columna_fecha(df)
    df = detectar_y_convertir_tipos(df)
    df = remover_filas_vacias(df)
    df = remover_columnas_vacias(df)
    
    # Validar valores
    columnas_numericas = df.select_dtypes(include=[np.number]).columns
    for col in columnas_numericas:
        if col != 'fecha':
            df = validar_rango_valores(df, col, min_val=0, accion='advertir')
    
    df = remover_duplicados(df, subset=['periodo'])
    df = df.sort_values('periodo').reset_index(drop=True)
    
    print("[OK] Limpieza completada\n")
    
    return df


def limpiar_cuerpos_academicos(df):
    """
    Limpieza específica para cuerpos académicos
    
    Args:
        df (pd.DataFrame): DataFrame de cuerpos académicos
        
    Returns:
        pd.DataFrame: DataFrame limpio
    """
    print("\n[Cuerpos] Limpiando datos de cuerpos academicos...")
    
    df = limpiar_nombres_columnas(df)
    
    # Solo limpiar periodos si existe la columna
    columnas_lower = [str(col).lower() for col in df.columns]
    tiene_periodo = any('periodo' in col for col in columnas_lower)
    
    if tiene_periodo:
        df = limpiar_periodos(df)
        df = agregar_columna_fecha(df)
        df = remover_duplicados(df, subset=['periodo'])
        df = df.sort_values('periodo').reset_index(drop=True)
    else:
        df = remover_duplicados(df)
    
    df = detectar_y_convertir_tipos(df)
    df = remover_filas_vacias(df)
    df = remover_columnas_vacias(df)
    
    print("[OK] Limpieza completada\n")
    
    return df


def limpiar_relacion_alumnos_profesor(df):
    """
    Limpieza específica para relación alumnos-profesor por unidad
    
    Args:
        df (pd.DataFrame): DataFrame de relación alumnos-profesor
        
    Returns:
        pd.DataFrame: DataFrame limpio
    """
    print("\n[Relacion] Limpiando datos de relacion alumnos-profesor...")
    
    df = limpiar_nombres_columnas(df)
    df = detectar_y_convertir_tipos(df)
    df = remover_filas_vacias(df)
    df = remover_columnas_vacias(df)
    
    # Validar ratios (deben ser positivos y razonables)
    for col in df.select_dtypes(include=[np.number]).columns:
        df = validar_rango_valores(df, col, min_val=0, max_val=100, 
                                   accion='advertir')
    
    df = remover_duplicados(df)
    
    print("[OK] Limpieza completada\n")
    
    return df


def limpiar_dataset_sin_periodo(df):
    """
    Limpieza para datasets sin columna de periodo
    (Datos filtrados por unidad académica, área de conocimiento, etc.)
    
    Args:
        df (pd.DataFrame): DataFrame sin periodo
        
    Returns:
        pd.DataFrame: DataFrame limpio
    """
    print("\n Limpiando dataset sin periodo (datos agregados)...")
    
    # Manejar MultiIndex en columnas si existe
    if isinstance(df.columns, pd.MultiIndex):
        print("   -> Aplanando MultiIndex en columnas...")
        # Convertir MultiIndex a nombres simples
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]
    
    df = limpiar_nombres_columnas(df)
    df = detectar_y_convertir_tipos(df)
    df = remover_filas_vacias(df, umbral=0.3)  # Más permisivo
    df = remover_columnas_vacias(df, umbral=0.3)  # Más permisivo
    
    # Validar valores numéricos (más permisivo)
    columnas_numericas = df.select_dtypes(include=[np.number]).columns
    for col in columnas_numericas:
        # Advertir pero no remover
        df = validar_rango_valores(df, col, min_val=0, accion='advertir')
    
    df = remover_duplicados(df)
    
    print("[OK] Limpieza completada\n")
    
    return df


# ============================================================================

def limpiar_dataset(df, tipo_dataset):
    """
    Función principal que aplica la limpieza apropiada según el tipo de dataset
    
    Args:
        df (pd.DataFrame): DataFrame a limpiar
        tipo_dataset (str): Tipo de dataset ('alumnos', 'personal', 'cuerpos', 
                           'relacion', 'programas')
        
    Returns:
        pd.DataFrame: DataFrame limpio
    """
    print(f"\n{'='*60}")
    print(f"INICIANDO LIMPIEZA: {tipo_dataset.upper()}")
    print(f"{'='*60}")
    print(f"Filas originales: {len(df)}")
    print(f"Columnas originales: {len(df.columns)}")
    
    # Verificar si tiene MultiIndex en columnas
    if isinstance(df.columns, pd.MultiIndex):
        print("  Dataset tiene MultiIndex, usando limpieza especial...")
        df_limpio = limpiar_dataset_sin_periodo(df)
        print(f"\nFilas finales: {len(df_limpio)}")
        print(f"Columnas finales: {len(df_limpio.columns)}")
        print(f"{'='*60}\n")
        return df_limpio
    
    # Verificar si tiene columna de periodo
    tiene_periodo = False
    if len(df.columns) > 0:
        # Buscar columna que contenga 'periodo'
        columnas_lower = [str(col).lower() for col in df.columns]
        tiene_periodo = any('periodo' in col for col in columnas_lower)
    
    # Si no tiene periodo, es un dataset agregado (por unidad, área, etc.)
    if not tiene_periodo and tipo_dataset in ['cuerpos', 'relacion', 'programas']:
        print("  Dataset sin columna 'periodo', usando limpieza para datos agregados...")
        df_limpio = limpiar_dataset_sin_periodo(df)
        print(f"\nFilas finales: {len(df_limpio)}")
        print(f"Columnas finales: {len(df_limpio.columns)}")
        print(f"{'='*60}\n")
        return df_limpio
    
    # Limpieza normal según tipo
    if tipo_dataset in ['alumnos', 'alumnos_licenciatura', 'alumnos_posgrado']:
        df_limpio = limpiar_alumnos_historico(df)
    
    elif tipo_dataset in ['personal', 'personal_academico', 'personal_sni']:
        df_limpio = limpiar_personal_historico(df)
    
    elif tipo_dataset == 'cuerpos':
        if tiene_periodo:
            df_limpio = limpiar_cuerpos_academicos(df)
        else:
            df_limpio = limpiar_dataset_sin_periodo(df)
    
    elif tipo_dataset == 'relacion':
        if tiene_periodo:
            df_limpio = limpiar_alumnos_historico(df)  # Similar a alumnos
        else:
            df_limpio = limpiar_dataset_sin_periodo(df)
    
    elif tipo_dataset in ['programas', 'programas_licenciatura', 'programas_posgrado']:
        if tiene_periodo:
            df_limpio = limpiar_alumnos_historico(df)  # Similar a alumnos
        else:
            df_limpio = limpiar_dataset_sin_periodo(df)
    
    else:
        print(f"  Tipo de dataset '{tipo_dataset}' no reconocido")
        print("Aplicando limpieza genérica...")
        df_limpio = df.copy()
        
        # Manejar MultiIndex si existe
        if isinstance(df_limpio.columns, pd.MultiIndex):
            df_limpio.columns = ['_'.join(map(str, col)).strip() for col in df_limpio.columns.values]
        
        df_limpio = limpiar_nombres_columnas(df_limpio)
        df_limpio = detectar_y_convertir_tipos(df_limpio)
        df_limpio = remover_filas_vacias(df_limpio)
        df_limpio = remover_columnas_vacias(df_limpio)
    
    print(f"\nFilas finales: {len(df_limpio)}")
    print(f"Columnas finales: {len(df_limpio.columns)}")
    print(f"{'='*60}\n")
    
    return df_limpio

# ============================================================================

def generar_reporte_calidad(df, nombre_dataset):
    """
    Genera un reporte de calidad de datos
    
    Args:
        df (pd.DataFrame): DataFrame a analizar
        nombre_dataset (str): Nombre del dataset
        
    Returns:
        dict: Diccionario con métricas de calidad
    """
    reporte = {
        'nombre_dataset': nombre_dataset,
        'n_filas': len(df),
        'n_columnas': len(df.columns),
        'columnas': df.columns.tolist(),
        'tipos_datos': df.dtypes.to_dict(),
        'valores_nulos': df.isnull().sum().to_dict(),
        'porcentaje_nulos': (df.isnull().sum() / len(df) * 100).to_dict(),
        'filas_duplicadas': df.duplicated().sum(),
        'memoria_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
    }
    
    # Estadísticas numéricas
    columnas_numericas = df.select_dtypes(include=[np.number]).columns
    if len(columnas_numericas) > 0:
        reporte['estadisticas_numericas'] = df[columnas_numericas].describe().to_dict()
    
    return reporte


def imprimir_reporte_calidad(reporte):
    """
    Imprime un reporte de calidad de datos de forma legible
    
    Args:
        reporte (dict): Diccionario con métricas de calidad
    """
    print("\n" + "="*60)
    print(f"REPORTE DE CALIDAD: {reporte['nombre_dataset']}")
    print("="*60)
    
    print(f"\ DIMENSIONES:")
    print(f"   Filas: {reporte['n_filas']:,}")
    print(f"   Columnas: {reporte['n_columnas']}")
    
    print(f"\n COLUMNAS:")
    for col in reporte['columnas']:
        tipo = reporte['tipos_datos'][col]
        nulos = reporte['valores_nulos'][col]
        pct_nulos = reporte['porcentaje_nulos'][col]
        print(f"   • {col} ({tipo})")
        if nulos > 0:
            print(f"       {nulos} nulos ({pct_nulos:.1f}%)")
    
    if reporte['filas_duplicadas'] > 0:
        print(f"\n  DUPLICADOS: {reporte['filas_duplicadas']} filas")
    else:
        print(f"\n[OK] SIN DUPLICADOS")
    
    print(f"\n MEMORIA: {reporte['memoria_mb']:.2f} MB")
    print("="*60 + "\n")