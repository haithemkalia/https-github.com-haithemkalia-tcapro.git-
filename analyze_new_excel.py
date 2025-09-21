#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour analyser la structure complète du fichier Excel
قائمة الزبائن معرض_أكتوبر2025 (26).xlsx
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import json

def analyze_excel_structure(file_path):
    """
    Analyser complètement la structure du fichier Excel
    """
    print(f"🔍 Analyse du fichier: {file_path}")
    print("=" * 80)
    
    if not os.path.exists(file_path):
        print(f"❌ Fichier non trouvé: {file_path}")
        return None
    
    try:
        # Lire le fichier Excel avec toutes les feuilles
        excel_file = pd.ExcelFile(file_path)
        print(f"📊 Nombre de feuilles: {len(excel_file.sheet_names)}")
        print(f"📋 Noms des feuilles: {excel_file.sheet_names}")
        print()
        
        analysis_results = {}
        
        for sheet_name in excel_file.sheet_names:
            print(f"📄 Analyse de la feuille: '{sheet_name}'")
            print("-" * 60)
            
            # Lire la feuille sans filtrer aucune donnée
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
            
            sheet_analysis = {
                'sheet_name': sheet_name,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'column_details': {},
                'sample_data': {},
                'data_types': {},
                'null_counts': {},
                'unique_counts': {},
                'sample_values': {}
            }
            
            print(f"📏 Dimensions: {len(df)} lignes × {len(df.columns)} colonnes")
            print(f"📋 Colonnes: {list(df.columns)}")
            print()
            
            # Analyser chaque colonne en détail
            for col in df.columns:
                print(f"🔸 Colonne: '{col}'")
                
                # Types de données
                data_type = str(df[col].dtype)
                non_null_count = df[col].count()
                null_count = df[col].isnull().sum()
                unique_count = df[col].nunique()
                
                # Échantillon de valeurs (premières 10 valeurs non-nulles)
                sample_values = df[col].dropna().head(10).tolist()
                
                # Valeurs uniques (si moins de 20)
                if unique_count <= 20:
                    unique_values = df[col].unique().tolist()
                else:
                    unique_values = "Trop de valeurs uniques (>20)"
                
                sheet_analysis['column_details'][col] = {
                    'data_type': data_type,
                    'non_null_count': non_null_count,
                    'null_count': null_count,
                    'unique_count': unique_count,
                    'sample_values': sample_values,
                    'unique_values': unique_values if unique_count <= 20 else "Trop nombreuses"
                }
                
                print(f"   Type: {data_type}")
                print(f"   Non-null: {non_null_count}, Null: {null_count}")
                print(f"   Valeurs uniques: {unique_count}")
                print(f"   Échantillon: {sample_values[:5]}")
                if unique_count <= 20:
                    print(f"   Toutes les valeurs: {unique_values}")
                print()
            
            # Afficher un échantillon des premières lignes
            print("📋 Échantillon des données (5 premières lignes):")
            print(df.head().to_string())
            print()
            
            # Rechercher des patterns spécifiques
            print("🔍 Recherche de patterns spécifiques:")
            
            # Chercher des colonnes qui pourraient contenir des IDs clients
            id_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['id', 'معرف', 'client', 'عميل'])]
            if id_columns:
                print(f"   Colonnes ID potentielles: {id_columns}")
                for id_col in id_columns:
                    sample_ids = df[id_col].dropna().head(10).tolist()
                    print(f"   Échantillon IDs dans '{id_col}': {sample_ids}")
            
            # Chercher des colonnes de statut/état
            status_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['status', 'état', 'حالة', 'statut'])]
            if status_columns:
                print(f"   Colonnes statut potentielles: {status_columns}")
                for status_col in status_columns:
                    unique_statuses = df[status_col].unique().tolist()
                    print(f"   États uniques dans '{status_col}': {unique_statuses}")
            
            # Chercher des colonnes de noms
            name_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['name', 'nom', 'اسم', 'الاسم'])]
            if name_columns:
                print(f"   Colonnes nom potentielles: {name_columns}")
            
            print()
            analysis_results[sheet_name] = sheet_analysis
        
        # Sauvegarder l'analyse dans un fichier JSON
        analysis_file = 'excel_analysis_results.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 Analyse sauvegardée dans: {analysis_file}")
        print("=" * 80)
        print("✅ Analyse terminée avec succès!")
        
        return analysis_results
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Chemin du fichier Excel
    excel_file = r"c:\Users\SERVEUR TCA\Desktop\VISA PRO2\قائمة الزبائن معرض_أكتوبر2025 (26).xlsx"
    
    # Analyser la structure
    results = analyze_excel_structure(excel_file)
    
    if results:
        print("\n🎯 Résumé de l'analyse:")
        for sheet_name, analysis in results.items():
            print(f"\n📄 Feuille '{sheet_name}':")
            print(f"   - {analysis['total_rows']} lignes")
            print(f"   - {analysis['total_columns']} colonnes")
            print(f"   - Colonnes: {', '.join(analysis['columns'][:5])}{'...' if len(analysis['columns']) > 5 else ''}")