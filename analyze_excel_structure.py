#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'analyse approfondie du fichier Excel pour restructurer l'interface
"""

import pandas as pd
import json
from datetime import datetime

def analyze_excel_deep():
    """Analyse approfondie du fichier Excel"""
    excel_file = "قائمة الزبائن معرض_أكتوبر2025 (40).xlsx"
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(excel_file)
        
        print("🔍 ANALYSE APPROFONDIE DU FICHIER EXCEL")
        print("=" * 60)
        
        # 1. Informations générales
        print(f"📊 Nombre total de lignes: {len(df)}")
        print(f"📊 Nombre total de colonnes: {len(df.columns)}")
        print()
        
        # 2. Analyse des colonnes
        print("📋 COLONNES DÉTECTÉES:")
        print("-" * 40)
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. '{col}' (type: {type(col).__name__})")
        print()
        
        # 3. Colonnes cibles spécifiées par l'utilisateur
        target_columns = [
            'ملاحظة',
            'اختيار الموظف مسؤول', 
            'الخلاصة',
            'من طرف',
            'حالة تتبع التأشيرة',
            'الجنسية',
            'حالة جواز السفر',
            'رقم جواز السفر',
            'تاريخ استلام للسفارة',
            'تاريخ التقديم',
            'رقم الواتساب',
            'الاسم الكامل',
            'معرف العميل'
        ]
        
        print("🎯 COLONNES CIBLES (ordre spécifié):")
        print("-" * 40)
        for i, col in enumerate(target_columns, 1):
            print(f"{i:2d}. '{col}'")
        print()
        
        # 4. Correspondance entre colonnes Excel et colonnes cibles
        print("🔗 CORRESPONDANCE COLONNES:")
        print("-" * 40)
        
        def normalize_text(text):
            """Normaliser le texte pour la comparaison"""
            if pd.isna(text):
                return ""
            return str(text).strip().replace('  ', ' ')
        
        found_columns = []
        missing_columns = []
        
        for target in target_columns:
            found = False
            for excel_col in df.columns:
                if normalize_text(excel_col) == normalize_text(target):
                    found_columns.append((target, excel_col))
                    found = True
                    break
            if not found:
                missing_columns.append(target)
        
        print("✅ COLONNES TROUVÉES:")
        for target, excel_col in found_columns:
            print(f"   '{target}' ← '{excel_col}'")
        
        if missing_columns:
            print("\n❌ COLONNES MANQUANTES:")
            for col in missing_columns:
                print(f"   '{col}'")
        
        # 5. Analyse des données d'exemple
        print("\n📝 ÉCHANTILLON DE DONNÉES (5 premières lignes):")
        print("-" * 60)
        
        # Afficher les colonnes trouvées avec leurs données
        if found_columns:
            sample_df = df[found_columns[0][1]:found_columns[-1][1]] if len(found_columns) > 1 else df[[found_columns[0][1]]]
            print(sample_df.head().to_string())
        
        # 6. Recommandations pour la restructuration
        print("\n💡 RECOMMANDATIONS POUR LA RESTRUCTURATION:")
        print("-" * 60)
        
        recommendations = {
            "database_schema": {
                "table_name": "clients",
                "columns": []
            },
            "web_interface": {
                "table_headers": [],
                "column_order": []
            },
            "mapping": {}
        }
        
        # Générer le schéma de base de données
        column_mapping = {
            'ملاحظة': 'notes',
            'اختيار الموظف مسؤول': 'responsible_employee', 
            'الخلاصة': 'summary',
            'من طرف': 'processed_by',
            'حالة تتبع التأشيرة': 'visa_status',
            'الجنسية': 'nationality',
            'حالة جواز السفر': 'passport_status',
            'رقم جواز السفر': 'passport_number',
            'تاريخ استلام للسفارة': 'transaction_date',
            'تاريخ التقديم': 'application_date',
            'رقم الواتساب': 'whatsapp_number',
            'الاسم الكامل': 'full_name',
            'معرف العميل': 'client_id'
        }
        
        for target_col in target_columns:
            db_col = column_mapping.get(target_col, target_col.lower().replace(' ', '_'))
            recommendations["database_schema"]["columns"].append({
                "arabic_name": target_col,
                "database_name": db_col,
                "type": "TEXT"
            })
            recommendations["web_interface"]["table_headers"].append(target_col)
            recommendations["web_interface"]["column_order"].append(db_col)
            recommendations["mapping"][target_col] = db_col
        
        # Sauvegarder les recommandations
        with open('restructure_recommendations.json', 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, ensure_ascii=False, indent=2)
        
        print("✅ Schéma de base de données généré")
        print("✅ Structure d'interface web définie")
        print("✅ Mapping des colonnes créé")
        print("📄 Fichier de recommandations sauvegardé: restructure_recommendations.json")
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return None

if __name__ == "__main__":
    result = analyze_excel_deep()
    if result:
        print(f"\n🎉 Analyse terminée avec succès!")
        print(f"📊 {len(result['database_schema']['columns'])} colonnes analysées")
    else:
        print("\n💥 Échec de l'analyse")
