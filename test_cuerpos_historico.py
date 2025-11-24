"""
Script de prueba para descargar SOLO Cuerpos Académicos: Histórico
"""

from scraper import UabcScraper
from config import DATASETS

print("\n" + "="*80)
print("DESCARGA DE CUERPOS ACADÉMICOS: HISTÓRICO")
print("="*80)

# Encontrar el dataset
dataset = next((d for d in DATASETS if d["nombre"] == "Cuerpos_Academicos_Historico"), None)

if not dataset:
    print("\n❌ ERROR: Dataset 'Cuerpos_Academicos_Historico' no encontrado en config.py")
    exit(1)

print(f"\n✓ Dataset encontrado:")
print(f"  Nombre: {dataset['nombre']}")
print(f"  URL: {dataset['url']}")
print(f"  Descripción: {dataset['descripcion']}")
print(f"  Prioridad: {dataset['prioridad']}")

respuesta = input("\n¿Ejecutar en modo NO headless para ver el proceso? (s/n): ")
headless = respuesta.strip().lower() != 's'

scraper = None

try:
    print("\nIniciando scraper...\n")
    scraper = UabcScraper(headless=headless)
    
    print("Descargando Cuerpos_Academicos_Historico...")
    resultado = scraper.scrape_dataset(dataset)
    
    if resultado:
        print("\n" + "="*80)
        print("✓ DESCARGA EXITOSA")
        print("="*80)
        print("\nRevisa la carpeta downloads/raw/ para encontrar el archivo:")
        print("  Cuerpos_Academicos_Historico_TIMESTAMP.xls")
    else:
        print("\n" + "="*80)
        print("❌ DESCARGA FALLIDA")
        print("="*80)
        print("\nRevisa los logs en logs/ para más detalles del error")
    
except KeyboardInterrupt:
    print("\n\n⚠️  Proceso interrumpido por el usuario")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if scraper:
        scraper.close()
    print("\n" + "="*80)
    print("Proceso finalizado")
    print("="*80 + "\n")
