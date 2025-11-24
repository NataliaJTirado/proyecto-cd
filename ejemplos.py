"""
Ejemplo de uso programático del scraper
Para automatización avanzada sin menú interactivo
"""

from scraper import UabcScraper
from config import DATASETS


def ejemplo_basico():
    """Ejemplo básico: extraer todos los datasets"""
    print("Ejemplo 1: Extraer todos los datasets\n")
    
    scraper = UabcScraper(headless=True)
    
    try:
        scraper.scrape_all()
    finally:
        scraper.close()


def ejemplo_prioridad():
    """Ejemplo: extraer solo datasets prioritarios"""
    print("Ejemplo 2: Extraer solo prioridad 1\n")
    
    scraper = UabcScraper(headless=True)
    
    try:
        scraper.scrape_priority(priority=1)
    finally:
        scraper.close()


def ejemplo_dataset_especifico():
    """Ejemplo: extraer dataset específico por nombre"""
    print("Ejemplo 3: Extraer dataset específico\n")
    
    # Buscar dataset por nombre
    dataset_nombre = "Alumnos_Licenciatura_Historico"
    dataset = next((d for d in DATASETS if d["nombre"] == dataset_nombre), None)
    
    if not dataset:
        print(f"Dataset '{dataset_nombre}' no encontrado")
        return
    
    scraper = UabcScraper(headless=False)  # Con ventana para ver el proceso
    
    try:
        scraper.scrape_dataset(dataset)
    finally:
        scraper.close()


def ejemplo_multiples_especificos():
    """Ejemplo: extraer múltiples datasets específicos"""
    print("Ejemplo 4: Extraer datasets específicos\n")
    
    # Lista de nombres de datasets que queremos
    nombres_deseados = [
        "Alumnos_Licenciatura_Historico",
        "Alumnos_Posgrado_Historico",
        "Personal_Academico_Historico"
    ]
    
    # Filtrar datasets
    datasets_a_extraer = [d for d in DATASETS if d["nombre"] in nombres_deseados]
    
    print(f"Extrayendo {len(datasets_a_extraer)} datasets específicos...")
    
    scraper = UabcScraper(headless=True)
    
    try:
        for dataset in datasets_a_extraer:
            scraper.scrape_dataset(dataset)
        
        scraper.print_summary()
    finally:
        scraper.close()


def ejemplo_con_manejo_errores():
    """Ejemplo: uso con manejo completo de errores"""
    print("Ejemplo 5: Con manejo robusto de errores\n")
    
    scraper = None
    
    try:
        scraper = UabcScraper(headless=True)
        
        # Intentar extraer todos
        scraper.scrape_all()
        
        # Verificar resultados
        if scraper.stats["fallidos"] > 0:
            print(f"\n⚠️  Hubo {scraper.stats['fallidos']} fallos")
            print("Considera revisar los logs para más detalles")
        else:
            print("\n✓ Todos los datasets se extrajeron exitosamente")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        print("Revisa los logs para más información")
    finally:
        if scraper:
            scraper.close()


def ejemplo_programado():
    """Ejemplo: para programar ejecuciones automáticas"""
    print("Ejemplo 6: Para cron jobs o tareas programadas\n")
    
    import sys
    
    scraper = None
    exit_code = 0
    
    try:
        scraper = UabcScraper(headless=True)
        scraper.scrape_priority(priority=1)
        
        # Verificar si todo fue exitoso
        if scraper.stats["fallidos"] == 0:
            print("\n✓ Ejecución completada sin errores")
            exit_code = 0
        else:
            print(f"\n⚠️  Ejecución completada con {scraper.stats['fallidos']} errores")
            exit_code = 1
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit_code = 2
    finally:
        if scraper:
            scraper.close()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("EJEMPLOS DE USO - WEB SCRAPER UABC")
    print("="*80)
    print("\nSelecciona un ejemplo:")
    print("1. Extraer todos los datasets")
    print("2. Extraer solo prioridad 1")
    print("3. Extraer dataset específico")
    print("4. Extraer múltiples específicos")
    print("5. Con manejo completo de errores")
    print("6. Para cron jobs (programado)")
    print("\n")
    
    opcion = input("Selecciona (1-6): ").strip()
    
    print("\n")
    
    if opcion == "1":
        ejemplo_basico()
    elif opcion == "2":
        ejemplo_prioridad()
    elif opcion == "3":
        ejemplo_dataset_especifico()
    elif opcion == "4":
        ejemplo_multiples_especificos()
    elif opcion == "5":
        ejemplo_con_manejo_errores()
    elif opcion == "6":
        ejemplo_programado()
    else:
        print("Opción no válida")
