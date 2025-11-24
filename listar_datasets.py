"""
Listar todos los datasets configurados en el scraper
"""

from config import DATASETS

print("\n" + "="*80)
print("DATASETS CONFIGURADOS EN EL SCRAPER")
print("="*80)

# Agrupar por prioridad
prioridades = {}
for dataset in DATASETS:
    prioridad = dataset.get("prioridad", 0)
    if prioridad not in prioridades:
        prioridades[prioridad] = []
    prioridades[prioridad].append(dataset)

# Mostrar por prioridad
for prioridad in sorted(prioridades.keys()):
    datasets_prioridad = prioridades[prioridad]
    print(f"\n{'━'*80}")
    print(f"PRIORIDAD {prioridad} ({len(datasets_prioridad)} datasets)")
    print(f"{'━'*80}")
    
    for i, dataset in enumerate(datasets_prioridad, 1):
        print(f"\n{i}. {dataset['nombre']}")
        print(f"   URL: {dataset['url']}")
        print(f"   Descripción: {dataset['descripcion']}")

print("\n" + "="*80)
print(f"TOTAL: {len(DATASETS)} datasets configurados")
print("="*80)

# Verificar específicamente Cuerpos_Academicos_Historico
print("\n🔍 VERIFICACIÓN ESPECIAL:")
cuerpos_hist = next((d for d in DATASETS if d["nombre"] == "Cuerpos_Academicos_Historico"), None)

if cuerpos_hist:
    print("✓ Cuerpos_Academicos_Historico ESTÁ CONFIGURADO")
    print(f"  Prioridad: {cuerpos_hist['prioridad']}")
    print(f"  URL: {cuerpos_hist['url']}")
else:
    print("❌ Cuerpos_Academicos_Historico NO está configurado")

print("\n")
