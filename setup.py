#!/usr/bin/env python3
"""
Script de configuración inicial rápida
Verifica y configura todo lo necesario para el scraper
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def check_python_version():
    """Verifica la versión de Python"""
    print_header("1. VERIFICANDO VERSIÓN DE PYTHON")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    
    print("✓ Versión de Python OK")
    return True


def check_chrome():
    """Verifica si Chrome está instalado"""
    print_header("2. VERIFICANDO GOOGLE CHROME")
    
    try:
        # Intentar ejecutar chrome
        if sys.platform == "win32":
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            if os.path.exists(chrome_path):
                print("✓ Google Chrome encontrado")
                return True
        else:
            result = subprocess.run(
                ["which", "google-chrome"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✓ Google Chrome encontrado en: {result.stdout.strip()}")
                return True
        
        print("⚠️  Google Chrome no detectado")
        print("Descarga desde: https://www.google.com/chrome/")
        return False
        
    except Exception as e:
        print(f"⚠️  No se pudo verificar Chrome: {e}")
        return False


def create_folders():
    """Crea las carpetas necesarias"""
    print_header("3. CREANDO ESTRUCTURA DE CARPETAS")
    
    folders = [
        "downloads/raw",
        "downloads/processed",
        "logs"
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"✓ {folder}/")
    
    print("\n✓ Estructura de carpetas creada")
    return True


def install_dependencies():
    """Instala las dependencias de Python"""
    print_header("4. INSTALANDO DEPENDENCIAS")
    
    print("Instalando paquetes desde requirements.txt...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("\n✓ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al instalar dependencias: {e}")
        return False


def test_imports():
    """Prueba que se puedan importar los módulos necesarios"""
    print_header("5. VERIFICANDO MÓDULOS")
    
    modules = [
        ("selenium", "Selenium WebDriver"),
        ("pandas", "Pandas"),
        ("openpyxl", "OpenPyXL")
    ]
    
    all_ok = True
    
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - No instalado")
            all_ok = False
    
    return all_ok


def create_test_script():
    """Crea un script de prueba simple"""
    print_header("6. CREANDO SCRIPT DE PRUEBA")
    
    test_code = """#!/usr/bin/env python3
# Script de prueba rápida
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("Probando Selenium...")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")

try:
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com")
    print(f"✓ Título de la página: {driver.title}")
    driver.quit()
    print("✓ Selenium funcionando correctamente")
except Exception as e:
    print(f"❌ Error: {e}")
"""
    
    with open("test_selenium.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    print("✓ Script de prueba creado: test_selenium.py")
    return True


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("  🚀 CONFIGURACIÓN INICIAL - WEB SCRAPER UABC")
    print("="*70)
    
    checks = [
        ("Python", check_python_version),
        ("Chrome", check_chrome),
        ("Carpetas", create_folders),
        ("Dependencias", install_dependencies),
        ("Módulos", test_imports),
        ("Script de prueba", create_test_script)
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error en {name}: {e}")
            results[name] = False
    
    # Resumen final
    print("\n" + "="*70)
    print("  📊 RESUMEN DE CONFIGURACIÓN")
    print("="*70)
    
    for name, success in results.items():
        status = "✓" if success else "❌"
        print(f"{status} {name}")
    
    print("\n" + "="*70)
    
    all_ok = all(results.values())
    
    if all_ok:
        print("\n🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
        print("\nPróximos pasos:")
        print("1. Ejecuta el script de prueba:")
        print("   python test_selenium.py")
        print("\n2. Si la prueba funciona, ejecuta el scraper:")
        print("   python scraper.py")
    else:
        print("\n⚠️  Hay problemas que requieren atención")
        print("\nRevisa los errores arriba y:")
        print("1. Instala Chrome si no lo tienes")
        print("2. Verifica tu versión de Python (3.8+)")
        print("3. Intenta instalar dependencias manualmente:")
        print("   pip install -r requirements.txt")
    
    print("\n" + "="*70)
    print()


if __name__ == "__main__":
    main()
