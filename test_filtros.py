"""
Script de prueba para datasets con filtros
Prueba solo los 3 datasets problemáticos
"""

from scraper import UabcScraper
from config import DATASETS

# Datasets con filtros a probar
datasets_con_filtros = [
    "Programas_Licenciatura",
    "Relacion_Alumnos_Profesor", 
    "Cuerpos_Academicos"
]

print("\n" + "="*80)
print("PRUEBA DE DATASETS CON FILTROS")
print("="*80)
print("\nDatasets a probar:")
for i, nombre in enumerate(datasets_con_filtros, 1):
    print(f"  {i}. {nombre}")

print("\n")
respuesta = input("¿Ejecutar modo NO headless para ver el proceso? (s/n): ")
headless = respuesta.strip().lower() != 's'

scraper = None

try:
    scraper = UabcScraper(headless=headless)
    
    # Filtrar solo los datasets con filtros
    datasets_a_probar = [d for d in DATASETS if d["nombre"] in datasets_con_filtros]
    
    print(f"\n{len(datasets_a_probar)} datasets encontrados para probar\n")
    
    for i, dataset in enumerate(datasets_a_probar, 1):
        print(f"\n[{i}/{len(datasets_a_probar)}] Probando {dataset['nombre']}...")
        scraper.scrape_dataset(dataset)
    
    scraper.print_summary()
    
    print("\n" + "="*80)
    print("ARCHIVOS ESPERADOS:")
    print("="*80)
    print("\nProgramas_Licenciatura debe generar:")
    print("  ✓ Programas_Lic_UnidadAcademica_TIMESTAMP.xls")
    print("  ✓ Programas_Lic_AreaConocimiento_TIMESTAMP.xls")
    print("\nRelacion_Alumnos_Profesor debe generar:")
    print("  ✓ Relacion_AlumnosProfesor_UnidadAcademica_TIMESTAMP.xls")
    print("\nCuerpos_Academicos debe generar:")
    print("  ✓ CuerposAcademicos_UnidadAcademica_TIMESTAMP.xls")
    print("  ✓ CuerposAcademicos_AreaConocimiento_TIMESTAMP.xls")
    print("\nTotal esperado: 5 archivos")
    print("="*80)
    
except KeyboardInterrupt:
    print("\n\nProceso interrumpido")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
finally:
    if scraper:
        scraper.close()
    print("\nRevisa los logs en logs/ para más detalles\n")
