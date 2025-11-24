"""
Configuración de URLs y datasets para el scraper de indicadores UABC
"""

# URL base del sitio
BASE_URL = "https://indicadores.uabc.mx"

# Configuración de datasets a extraer
DATASETS = [
    {
        "nombre": "Alumnos_Licenciatura_Historico",
        "url": "/indicadores/historicos/historico_AL/historico_AL",
        "descripcion": "Histórico de alumnos de licenciatura",
        "prioridad": 1
    },
    {
        "nombre": "Alumnos_Posgrado_Historico",
        "url": "/indicadores/historicos/historico_AP/historico_AP",
        "descripcion": "Histórico de alumnos de posgrado",
        "prioridad": 1
    },
    {
        "nombre": "Personal_Academico_Historico",
        "url": "/indicadores/historicos/historico_PA/historico_PA",
        "descripcion": "Histórico de personal académico",
        "prioridad": 1
    },
    {
        "nombre": "Personal_Administrativo_Historico",
        "url": "/indicadores/historicos/historico_PAS/historico_PAS",
        "descripcion": "Histórico de personal administrativo y de servicios",
        "prioridad": 2
    },
    {
        "nombre": "Programas_Licenciatura",
        "url": "/indicadores/programasEducativosLicenciatura",
        "descripcion": "Programas educativos de licenciatura",
        "prioridad": 2
    },
    {
        "nombre": "Programas_Licenciatura_Acred_Internacional",
        "url": "/indicadores/programasEducativosLicenciaturaAcreditacionInternacional",
        "descripcion": "Programas de licenciatura con acreditación internacional",
        "prioridad": 3
    },
    {
        "nombre": "Programas_Licenciatura_Historico",
        "url": "/indicadores/historicos/historico_PEL/historico_PEL",
        "descripcion": "Histórico de programas educativos de licenciatura",
        "prioridad": 1
    },
    {
        "nombre": "Programas_Posgrado",
        "url": "/indicadores/programasEducativosPosgrado",
        "descripcion": "Programas educativos de posgrado",
        "prioridad": 2
    },
    {
        "nombre": "Programas_Posgrado_Historico",
        "url": "/indicadores/historicos/historico_PEP/historico_PEP",
        "descripcion": "Histórico de programas educativos de posgrado",
        "prioridad": 1
    },
    {
        "nombre": "Relacion_Alumnos_Profesor",
        "url": "/indicadores/PersonalAcademico/relacionAlumno_pa",
        "descripcion": "Relación alumnos por profesor",
        "prioridad": 1
    },
    {
        "nombre": "Personal_SNI_Historico",
        "url": "/indicadores/historicos/historico_PASNI/historico_PASNI",
        "descripcion": "Histórico de personal académico en el SNI",
        "prioridad": 1
    },
    {
        "nombre": "Cuerpos_Academicos",
        "url": "/indicadores/cuerposAcademicos/",
        "descripcion": "Cuerpos académicos",
        "prioridad": 1
    }
]

# Configuración de Selenium
SELENIUM_CONFIG = {
    "implicit_wait": 10,  # Segundos
    "page_load_timeout": 30,  # Segundos
    "download_timeout": 60,  # Segundos para esperar descarga
    "delay_between_requests": 3,  # Segundos entre cada petición
}

# Selectores HTML
SELECTORS = {
    "tabla": "tblData",  # ID de la tabla
    "boton_excel": "button[onclick*='exportTableToExcel']",  # Selector CSS del botón
    "link_regresar": "a[href='/indicadores/Ind_Publicos/']"
}

# Configuración de carpetas
FOLDERS = {
    "downloads": "downloads",
    "raw": "downloads/raw",
    "processed": "downloads/processed",
    "logs": "logs"
}
