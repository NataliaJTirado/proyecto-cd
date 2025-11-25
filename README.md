# 🎓 Web Scraper - Indicadores UABC

Sistema automatizado para extraer datos históricos y actuales de los indicadores públicos de la Universidad Autónoma de Baja California.

## 📋 Descripción

Este scraper automatiza la descarga de 12 datasets clave de la UABC:

**Prioridad 1 (Críticos para análisis):**
- ✅ Alumnos de licenciatura: Histórico
- ✅ Alumnos de posgrado: Histórico
- ✅ Personal académico: Histórico
- ✅ Programas educativos de licenciatura: Histórico
- ✅ Programas educativos de posgrado: Histórico
- ✅ Relación alumnos por profesor
- ✅ Personal académico en el SNI: Histórico
- ✅ Cuerpos académicos

**Prioridad 2 (Complementarios):**
- Programas educativos de licenciatura (actual)
- Programas educativos de posgrado (actual)
- Personal administrativo y de servicios: Histórico

**Prioridad 3 (Opcionales):**
- Programas con acreditación internacional

---

## 🛠️ Instalación

### Requisitos previos

1. **Python 3.8 o superior**
   ```bash
   python --version
   ```

2. **Google Chrome** instalado en tu sistema
   - Descarga desde: https://www.google.com/chrome/

### Paso 1: Clonar o descargar el proyecto

```bash
cd tu_directorio_de_trabajo
# Si tienes el proyecto en un zip, descomprime aquí
```

### Paso 2: Crear entorno virtual (recomendado)

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Verificar ChromeDriver

El script intentará detectar automáticamente ChromeDriver. Si tienes problemas:

**Opción A - Instalación automática (recomendado):**
```bash
pip install webdriver-manager
```

**Opción B - Instalación manual:**
1. Descarga ChromeDriver: https://chromedriver.chromium.org/
2. Colócalo en tu PATH del sistema

---

## 🚀 Uso

### Ejecución básica

```bash
python scraper.py
```

### Menú interactivo

Al ejecutar, verás:

```
================================================================================
WEB SCRAPER - INDICADORES UABC
================================================================================

Opciones:
1. Extraer TODOS los datasets (12 datasets)
2. Extraer solo datasets PRIORITARIOS (prioridad 1)
3. Extraer datasets de PRIORIDAD 2
4. Salir

Selecciona una opción (1-4):
```

### Modo headless (sin ventana)

Cuando se te pregunte:
```
¿Ejecutar en modo headless (sin ventana)? (s/n):
```

- **n** (No): Verás el navegador abrirse y funcionar (útil para debugging)
- **s** (Sí): Ejecución en segundo plano (más rápido, ideal para producción)

---

## 📁 Estructura de archivos

```
uabc_scraper/
├── scraper.py              # Script principal
├── config.py               # Configuración de URLs y datasets
├── requirements.txt        # Dependencias
├── README.md              # Este archivo
├── downloads/             # Carpeta de descargas
│   ├── raw/              # Archivos Excel originales
│   └── processed/        # Archivos procesados (futuro)
└── logs/                 # Logs de ejecución
    └── scraper_YYYYMMDD_HHMMSS.log
```

---

## ⚙️ Configuración

### Modificar delays y timeouts

Edita `config.py`:

```python
SELENIUM_CONFIG = {
    "implicit_wait": 10,           # Espera implícita (segundos)
    "page_load_timeout": 30,       # Timeout de carga de página
    "download_timeout": 60,        # Timeout de descarga
    "delay_between_requests": 3,   # Delay entre peticiones
}
```

### Agregar nuevos datasets

En `config.py`, agrega a la lista `DATASETS`:

```python
{
    "nombre": "Nombre_Del_Dataset",
    "url": "/ruta/en/el/sitio",
    "descripcion": "Descripción del dataset",
    "prioridad": 1  # 1=crítico, 2=complementario, 3=opcional
}
```

---

## 📊 Logs y monitoreo

Los logs se guardan en `logs/scraper_YYYYMMDD_HHMMSS.log`

Ejemplo de log exitoso:
```
2024-11-22 15:30:45 - INFO - ============================================================
2024-11-22 15:30:45 - INFO - Extrayendo: Alumnos_Licenciatura_Historico
2024-11-22 15:30:45 - INFO - URL: https://indicadores.uabc.mx/...
2024-11-22 15:30:47 - INFO - Página cargada correctamente
2024-11-22 15:30:47 - INFO - Tabla 'tblData' encontrada
2024-11-22 15:30:48 - INFO - Haciendo click en botón de exportar...
2024-11-22 15:30:50 - INFO - ✓ Descarga exitosa: Alumnos_Licenciatura_Historico_20241122_153050.xlsx
2024-11-22 15:30:50 - INFO -   Tamaño: 45.32 KB
```

---

## 🔧 Solución de problemas

### Error: "ChromeDriver not found"

**Solución:**
```bash
pip install webdriver-manager
```

O descarga manualmente desde https://chromedriver.chromium.org/

### Error: "Timeout waiting for download"

**Causa:** El archivo tarda más de 60 segundos en descargarse.

**Solución:** Aumenta `download_timeout` en `config.py`:
```python
"download_timeout": 120,  # 2 minutos
```

### Error: "Element not found"

**Causa:** La estructura HTML del sitio cambió.

**Solución:** Actualiza los selectores en `config.py`:
```python
SELECTORS = {
    "tabla": "nuevo_id_de_tabla",
    "boton_excel": "nuevo_selector_de_boton",
}
```

### El navegador se cierra inmediatamente

**Causa:** Error en la inicialización del driver.

**Solución:** Ejecuta en modo **NO headless** para ver el error:
```
¿Ejecutar en modo headless? (s/n): n
```

### Descargas incompletas

**Solución:** Aumenta el delay entre peticiones en `config.py`:
```python
"delay_between_requests": 5,  # De 3 a 5 segundos
```

---

## 📈 Mejoras futuras

- [ ] Validación automática de integridad de archivos
- [ ] Conversión automática a CSV
- [ ] Limpieza y normalización de datos
- [ ] Exportación directa a base de datos
- [ ] Notificaciones por email al completar
- [ ] Retry automático en caso de fallos
- [ ] Dashboard de monitoreo en tiempo real

---

## 🤝 Contribuciones

Si encuentras errores o tienes sugerencias:

1. Revisa los logs en `logs/`
2. Describe el problema o mejora
3. Incluye el log completo del error

---

## 📝 Notas importantes

- **Respeta los términos de uso** del sitio de la UABC
- El script incluye delays para no sobrecargar el servidor
- Los archivos se renombran automáticamente con timestamp
- Los logs se guardan para auditoría

---

## 🎯 Ejemplo de uso completo

```bash
# 1. Activar entorno virtual
source venv/bin/activate  # Mac/Linux
# o
venv\Scripts\activate     # Windows

# 2. Ejecutar scraper
python scraper.py

# 3. Seleccionar opción 2 (solo prioritarios)
Selecciona una opción (1-4): 2

# 4. Ejecutar en modo normal (con ventana)
¿Ejecutar en modo headless? (s/n): n

# 5. Esperar a que termine (aparecerá resumen)

# 6. Revisar archivos en downloads/raw/
```

---

## 📧 Soporte

Para problemas técnicos:
1. Revisa la sección "Solución de problemas"
2. Consulta los logs en `logs/`
3. Verifica que tienes la última versión de Chrome

---

**Versión:** 1.0.0  
**Última actualización:** Noviembre 2024  
**Compatibilidad:** Python 3.8+, Chrome 90+
