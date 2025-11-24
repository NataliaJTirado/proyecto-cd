"""
Web Scraper para Indicadores UABC
Automatiza la descarga de datos históricos y actuales de la Universidad Autónoma de Baja California
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
import glob

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import BASE_URL, DATASETS, SELENIUM_CONFIG, SELECTORS, FOLDERS


class UabcScraper:
    """Scraper para extraer datos de indicadores UABC"""
    
    def __init__(self, headless=False):
        """
        Inicializa el scraper
        
        Args:
            headless (bool): Si es True, ejecuta el navegador sin interfaz gráfica
        """
        self.base_url = BASE_URL
        self.datasets = DATASETS
        self.setup_logging()
        self.setup_folders()
        self.driver = self.setup_driver(headless)
        self.download_folder = os.path.abspath(FOLDERS["raw"])
        
        self.stats = {
            "total": len(DATASETS),
            "exitosos": 0,
            "fallidos": 0,
            "inicio": datetime.now()
        }
        
    def setup_folders(self):
        """Crea las carpetas necesarias si no existen"""
        for folder in FOLDERS.values():
            Path(folder).mkdir(parents=True, exist_ok=True)
        self.log_message("Carpetas creadas/verificadas", "INFO")
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{FOLDERS['logs']}/scraper_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 80)
        self.logger.info("INICIANDO WEB SCRAPER - INDICADORES UABC")
        self.logger.info("=" * 80)
    
    def log_message(self, message, level="INFO"):
        """Registra un mensaje en el log"""
        if level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
    
    def setup_driver(self, headless=False):
        """
        Configura el WebDriver de Chrome
        
        Args:
            headless (bool): Ejecutar sin interfaz gráfica
            
        Returns:
            webdriver: Instancia del driver de Chrome
        """
        chrome_options = Options()
        
        # Configurar carpeta de descarga
        download_path = os.path.abspath(FOLDERS["raw"])
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Opciones adicionales
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Inicializar driver
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(SELENIUM_CONFIG["implicit_wait"])
            driver.set_page_load_timeout(SELENIUM_CONFIG["page_load_timeout"])
            self.log_message("WebDriver de Chrome inicializado correctamente")
            return driver
        except Exception as e:
            self.log_message(f"Error al inicializar WebDriver: {e}", "ERROR")
            raise
    
    def get_latest_download(self):
        """
        Obtiene el archivo más recientemente descargado
        
        Returns:
            str: Path del archivo descargado o None
        """
        download_folder = FOLDERS["raw"]
        files = glob.glob(f"{download_folder}/*.xls*")
        
        if not files:
            return None
        
        # Ordenar por fecha de modificación (más reciente primero)
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
    
    def wait_for_download(self, timeout=60):
        """
        Espera a que se complete la descarga
        
        Args:
            timeout (int): Tiempo máximo de espera en segundos
            
        Returns:
            bool: True si se completó la descarga, False si timeout
        """
        download_folder = FOLDERS["raw"]
        seconds = 0
        
        # Esperar a que aparezca un archivo .xls o .xlsx
        while seconds < timeout:
            files = glob.glob(f"{download_folder}/*.xls*")
            # Verificar que no haya archivos temporales de Chrome (.crdownload)
            temp_files = glob.glob(f"{download_folder}/*.crdownload")
            
            if files and not temp_files:
                # Esperar un segundo adicional para asegurar que terminó
                time.sleep(1)
                return True
            
            time.sleep(1)
            seconds += 1
        
        return False
    
    def select_filter_and_download(self, filter_value, suffix):
        """
        Selecciona un filtro y descarga el archivo
        
        Args:
            filter_value (str): Valor del filtro a seleccionar
            suffix (str): Sufijo para el nombre del archivo
            
        Returns:
            bool: True si fue exitoso, False si falló
        """
        try:
            wait = WebDriverWait(self.driver, 15)
            
            # Seleccionar el filtro
            self.log_message(f"  Seleccionando filtro: {filter_value}")
            select_element = wait.until(
                EC.presence_of_element_located((By.ID, "cbNivel"))
            )
            
            # Usar Select para cambiar el valor
            select = Select(select_element)
            select.select_by_visible_text(filter_value)
            
            # Esperar a que se recarguen los datos (la función onchange)
            self.log_message("  Esperando recarga de datos...")
            time.sleep(3)
            
            # Esperar a que la tabla se actualice
            wait.until(EC.presence_of_element_located((By.ID, SELECTORS["tabla"])))
            time.sleep(2)
            
            # Buscar botón de exportar
            boton_excel = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["boton_excel"]))
            )
            
            # Contar archivos antes
            files_before = set(glob.glob(f"{FOLDERS['raw']}/*.xls*"))
            
            self.log_message("  Descargando archivo...")
            boton_excel.click()
            
            # Esperar descarga
            if self.wait_for_download(SELENIUM_CONFIG["download_timeout"]):
                files_after = set(glob.glob(f"{FOLDERS['raw']}/*.xls*"))
                new_files = files_after - files_before
                
                if new_files:
                    downloaded_file = list(new_files)[0]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    extension = os.path.splitext(downloaded_file)[1]
                    new_filename = f"{FOLDERS['raw']}/{suffix}_{timestamp}{extension}"
                    
                    os.rename(downloaded_file, new_filename)
                    
                    file_size = os.path.getsize(new_filename) / 1024
                    self.log_message(f"  ✓ Descarga exitosa: {os.path.basename(new_filename)}")
                    self.log_message(f"    Tamaño: {file_size:.2f} KB")
                    return True
                    
            return False
            
        except Exception as e:
            self.log_message(f"  Error en filtro {filter_value}: {e}", "ERROR")
            return False
    
    def scrape_dataset(self, dataset):
        """
        Extrae un dataset específico
        
        Args:
            dataset (dict): Diccionario con la información del dataset
            
        Returns:
            bool: True si fue exitoso, False si falló
        """
        nombre = dataset["nombre"]
        url = dataset["url"]
        full_url = self.base_url + url
        
        self.log_message(f"\n{'='*60}")
        self.log_message(f"Extrayendo: {nombre}")
        self.log_message(f"URL: {full_url}")
        self.log_message(f"Descripción: {dataset['descripcion']}")
        
        try:
            # 1. Navegar a la URL
            self.driver.get(full_url)
            self.log_message("Página cargada correctamente")
            time.sleep(2)
            
            # 2. Esperar a que la tabla esté presente
            wait = WebDriverWait(self.driver, 15)
            tabla = wait.until(
                EC.presence_of_element_located((By.ID, SELECTORS["tabla"]))
            )
            self.log_message(f"Tabla '{SELECTORS['tabla']}' encontrada")
            
            # ===== CASOS ESPECIALES CON FILTROS =====
            
            # CASO 1: Programas educativos de licenciatura
            if nombre == "Programas_Licenciatura":
                self.log_message("Dataset con filtros múltiples detectado")
                success_count = 0
                
                # Descargar por Unidad académica
                if self.select_filter_and_download("Unidad académica", "Programas_Lic_UnidadAcademica"):
                    success_count += 1
                
                time.sleep(2)
                
                # Descargar por Área de conocimiento
                if self.select_filter_and_download("Área de conocimiento", "Programas_Lic_AreaConocimiento"):
                    success_count += 1
                
                if success_count == 2:
                    self.stats["exitosos"] += 1
                    return True
                else:
                    self.log_message(f"Solo se descargaron {success_count}/2 archivos", "WARNING")
                    self.stats["fallidos"] += 1
                    return False
            
            # CASO 2: Relación alumnos por profesor
            elif nombre == "Relacion_Alumnos_Profesor":
                self.log_message("Dataset con filtro detectado")
                
                # Descargar por Unidad académica
                if self.select_filter_and_download("Unidad académica", "Relacion_AlumnosProfesor_UnidadAcademica"):
                    self.stats["exitosos"] += 1
                    return True
                else:
                    self.stats["fallidos"] += 1
                    return False
            
            # CASO 3: Cuerpos académicos
            elif nombre == "Cuerpos_Academicos":
                self.log_message("Dataset con filtros múltiples detectado")
                success_count = 0
                
                # Descargar por Unidad académica
                if self.select_filter_and_download("Unidad académica", "CuerposAcademicos_UnidadAcademica"):
                    success_count += 1
                
                time.sleep(2)
                
                # Descargar por Área de conocimiento
                if self.select_filter_and_download("Área de conocimiento", "CuerposAcademicos_AreaConocimiento"):
                    success_count += 1
                
                if success_count == 2:
                    self.stats["exitosos"] += 1
                    return True
                else:
                    self.log_message(f"Solo se descargaron {success_count}/2 archivos", "WARNING")
                    self.stats["fallidos"] += 1
                    return False
            
            # ===== CASO NORMAL (sin filtros) =====
            else:
                # 3. Buscar y hacer click en el botón de exportar
                boton_excel = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["boton_excel"]))
                )
                
                # Contar archivos antes de la descarga
                files_before = set(glob.glob(f"{FOLDERS['raw']}/*.xls*"))
                
                self.log_message("Haciendo click en botón de exportar...")
                boton_excel.click()
                
                # 4. Esperar a que se complete la descarga
                self.log_message("Esperando descarga...")
                if self.wait_for_download(SELENIUM_CONFIG["download_timeout"]):
                    # Obtener archivo recién descargado
                    files_after = set(glob.glob(f"{FOLDERS['raw']}/*.xls*"))
                    new_files = files_after - files_before
                    
                    if new_files:
                        downloaded_file = list(new_files)[0]
                        
                        # Renombrar archivo con nombre descriptivo
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        extension = os.path.splitext(downloaded_file)[1]
                        new_filename = f"{FOLDERS['raw']}/{nombre}_{timestamp}{extension}"
                        
                        os.rename(downloaded_file, new_filename)
                        
                        file_size = os.path.getsize(new_filename) / 1024  # KB
                        self.log_message(f"✓ Descarga exitosa: {os.path.basename(new_filename)}")
                        self.log_message(f"  Tamaño: {file_size:.2f} KB")
                        
                        self.stats["exitosos"] += 1
                        return True
                    else:
                        self.log_message("No se detectó archivo nuevo descargado", "WARNING")
                        self.stats["fallidos"] += 1
                        return False
                else:
                    self.log_message("Timeout esperando descarga", "ERROR")
                    self.stats["fallidos"] += 1
                    return False
            
        except TimeoutException:
            self.log_message(f"Timeout: No se pudo cargar el elemento en {nombre}", "ERROR")
            self.stats["fallidos"] += 1
            return False
        except NoSuchElementException as e:
            self.log_message(f"Elemento no encontrado en {nombre}: {e}", "ERROR")
            self.stats["fallidos"] += 1
            return False
        except Exception as e:
            self.log_message(f"Error inesperado en {nombre}: {e}", "ERROR")
            self.stats["fallidos"] += 1
            return False
        finally:
            # Delay entre peticiones para no sobrecargar el servidor
            time.sleep(SELENIUM_CONFIG["delay_between_requests"])
    
    def scrape_all(self):
        """Extrae todos los datasets configurados"""
        self.log_message(f"\nIniciando extracción de {len(self.datasets)} datasets...")
        
        for i, dataset in enumerate(self.datasets, 1):
            self.log_message(f"\n[{i}/{len(self.datasets)}] Procesando...")
            self.scrape_dataset(dataset)
        
        self.print_summary()
    
    def scrape_priority(self, priority=1):
        """
        Extrae solo los datasets con prioridad específica
        
        Args:
            priority (int): Nivel de prioridad (1 = más importante)
        """
        datasets_filtered = [d for d in self.datasets if d.get("prioridad") == priority]
        
        self.log_message(f"\nExtrayendo {len(datasets_filtered)} datasets con prioridad {priority}...")
        
        for i, dataset in enumerate(datasets_filtered, 1):
            self.log_message(f"\n[{i}/{len(datasets_filtered)}] Procesando...")
            self.scrape_dataset(dataset)
        
        self.print_summary()
    
    def print_summary(self):
        """Imprime resumen de la ejecución"""
        duracion = datetime.now() - self.stats["inicio"]
        
        self.log_message("\n" + "="*80)
        self.log_message("RESUMEN DE EJECUCIÓN")
        self.log_message("="*80)
        self.log_message(f"Total de datasets: {self.stats['total']}")
        self.log_message(f"Exitosos: {self.stats['exitosos']} ✓")
        self.log_message(f"Fallidos: {self.stats['fallidos']} ✗")
        self.log_message(f"Tasa de éxito: {(self.stats['exitosos']/self.stats['total']*100):.1f}%")
        self.log_message(f"Duración: {duracion}")
        self.log_message(f"Archivos guardados en: {os.path.abspath(FOLDERS['raw'])}")
        self.log_message("="*80)
    
    def close(self):
        """Cierra el WebDriver y limpia recursos"""
        if self.driver:
            self.driver.quit()
            self.log_message("WebDriver cerrado correctamente")


def main():
    """Función principal"""
    print("\n" + "="*80)
    print("WEB SCRAPER - INDICADORES UABC")
    print("="*80)
    print("\nOpciones:")
    print("1. Extraer TODOS los datasets (12 datasets)")
    print("2. Extraer solo datasets PRIORITARIOS (prioridad 1)")
    print("3. Extraer datasets de PRIORIDAD 2")
    print("4. Salir")
    
    opcion = input("\nSelecciona una opción (1-4): ").strip()
    
    if opcion == "4":
        print("Saliendo...")
        return
    
    headless_input = input("\n¿Ejecutar en modo headless (sin ventana)? (s/n): ").strip().lower()
    headless = headless_input == "s"
    
    scraper = None
    try:
        scraper = UabcScraper(headless=headless)
        
        if opcion == "1":
            scraper.scrape_all()
        elif opcion == "2":
            scraper.scrape_priority(priority=1)
        elif opcion == "3":
            scraper.scrape_priority(priority=2)
        else:
            print("Opción no válida")
            return
        
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido por el usuario")
    except Exception as e:
        print(f"\nError fatal: {e}")
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()