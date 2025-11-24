"""
Script de validación para verificar archivos descargados
Valida integridad, tamaño y estructura de los archivos Excel
"""

import os
import glob
from datetime import datetime
import pandas as pd
from pathlib import Path

from config import FOLDERS, DATASETS


class FileValidator:
    """Validador de archivos descargados"""
    
    def __init__(self):
        self.download_folder = FOLDERS["raw"]
        self.expected_datasets = [d["nombre"] for d in DATASETS]
        
    def get_downloaded_files(self):
        """Obtiene lista de archivos descargados"""
        files = glob.glob(f"{self.download_folder}/*.xls*")
        return files
    
    def validate_file_size(self, filepath, min_size_kb=1):
        """
        Valida que el archivo tenga un tamaño mínimo
        
        Args:
            filepath (str): Ruta del archivo
            min_size_kb (int): Tamaño mínimo en KB
            
        Returns:
            tuple: (bool, str) - (válido, mensaje)
        """
        if not os.path.exists(filepath):
            return False, "Archivo no existe"
        
        size_kb = os.path.getsize(filepath) / 1024
        
        if size_kb < min_size_kb:
            return False, f"Archivo muy pequeño: {size_kb:.2f} KB"
        
        return True, f"Tamaño OK: {size_kb:.2f} KB"
    
    def validate_excel_structure(self, filepath):
        """
        Valida que el Excel se pueda leer y tenga datos
        
        Args:
            filepath (str): Ruta del archivo
            
        Returns:
            tuple: (bool, str, dict) - (válido, mensaje, info)
        """
        try:
            # Intentar leer el archivo
            df = pd.read_excel(filepath, sheet_name=0)
            
            info = {
                "filas": len(df),
                "columnas": len(df.columns),
                "columnas_nombres": list(df.columns)
            }
            
            if len(df) == 0:
                return False, "Excel vacío (0 filas)", info
            
            if len(df.columns) == 0:
                return False, "Excel sin columnas", info
            
            return True, f"Excel válido: {len(df)} filas x {len(df.columns)} columnas", info
            
        except Exception as e:
            return False, f"Error al leer Excel: {str(e)}", {}
    
    def check_dataset_coverage(self):
        """
        Verifica qué datasets se descargaron
        
        Returns:
            dict: Información de cobertura
        """
        files = self.get_downloaded_files()
        file_basenames = [os.path.basename(f) for f in files]
        
        found = []
        missing = []
        
        for dataset_name in self.expected_datasets:
            # Buscar si algún archivo contiene el nombre del dataset
            dataset_found = any(dataset_name in basename for basename in file_basenames)
            
            if dataset_found:
                found.append(dataset_name)
            else:
                missing.append(dataset_name)
        
        return {
            "total_esperados": len(self.expected_datasets),
            "encontrados": len(found),
            "faltantes": len(missing),
            "lista_encontrados": found,
            "lista_faltantes": missing,
            "cobertura_pct": (len(found) / len(self.expected_datasets)) * 100
        }
    
    def generate_report(self):
        """Genera un reporte completo de validación"""
        print("\n" + "="*80)
        print("REPORTE DE VALIDACIÓN DE ARCHIVOS")
        print("="*80)
        
        files = self.get_downloaded_files()
        
        print(f"\nCarpeta: {os.path.abspath(self.download_folder)}")
        print(f"Archivos encontrados: {len(files)}")
        
        if not files:
            print("\n⚠️  No se encontraron archivos descargados")
            return
        
        print("\n" + "-"*80)
        print("VALIDACIÓN INDIVIDUAL DE ARCHIVOS")
        print("-"*80)
        
        valid_files = 0
        invalid_files = 0
        
        for i, filepath in enumerate(files, 1):
            filename = os.path.basename(filepath)
            print(f"\n[{i}/{len(files)}] {filename}")
            
            # Validar tamaño
            size_valid, size_msg = self.validate_file_size(filepath, min_size_kb=1)
            print(f"  Tamaño: {'✓' if size_valid else '✗'} {size_msg}")
            
            # Validar estructura
            struct_valid, struct_msg, info = self.validate_excel_structure(filepath)
            print(f"  Estructura: {'✓' if struct_valid else '✗'} {struct_msg}")
            
            if struct_valid and info:
                print(f"  Columnas: {', '.join(info['columnas_nombres'][:5])}{'...' if len(info['columnas_nombres']) > 5 else ''}")
            
            if size_valid and struct_valid:
                valid_files += 1
            else:
                invalid_files += 1
        
        # Reporte de cobertura
        print("\n" + "-"*80)
        print("COBERTURA DE DATASETS")
        print("-"*80)
        
        coverage = self.check_dataset_coverage()
        
        print(f"\nTotal esperado: {coverage['total_esperados']}")
        print(f"Encontrados: {coverage['encontrados']} ✓")
        print(f"Faltantes: {coverage['faltantes']} ✗")
        print(f"Cobertura: {coverage['cobertura_pct']:.1f}%")
        
        if coverage['lista_faltantes']:
            print(f"\n⚠️  Datasets faltantes:")
            for dataset in coverage['lista_faltantes']:
                print(f"  - {dataset}")
        
        # Resumen final
        print("\n" + "="*80)
        print("RESUMEN")
        print("="*80)
        print(f"Archivos válidos: {valid_files} ✓")
        print(f"Archivos inválidos: {invalid_files} ✗")
        print(f"Tasa de validación: {(valid_files/len(files)*100):.1f}%")
        
        if valid_files == len(files) and coverage['faltantes'] == 0:
            print("\n🎉 ¡TODAS LAS VALIDACIONES PASARON!")
        elif invalid_files > 0:
            print("\n⚠️  Hay archivos con problemas que requieren atención")
        elif coverage['faltantes'] > 0:
            print("\n⚠️  Faltan datasets por descargar")
        
        print("="*80)


def main():
    """Función principal"""
    print("\n🔍 VALIDADOR DE ARCHIVOS - INDICADORES UABC\n")
    
    validator = FileValidator()
    validator.generate_report()
    
    print("\n")


if __name__ == "__main__":
    main()
