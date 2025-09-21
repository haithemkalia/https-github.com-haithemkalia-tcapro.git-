#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import restructuré selon l'ordre exact des colonnes spécifié par l'utilisateur
"""

import pandas as pd
import sqlite3
import json
from datetime import datetime
import sys
import os

# Ajouter le dossier src au path
sys.path.append('src')

def restructured_import():
    """Import restructuré avec l'ordre exact des colonnes"""
    
    excel_file = "قائمة الزبائن معرض_أكتوبر2025 (40).xlsx"
    db_file = "visa_system.db"
    
    try:
        print("🔍 IMPORT RESTRUCTURÉ - ANALYSE APPROFONDIE")
        print("=" * 60)
        
        # 1. Lire le fichier Excel
        print("📂 Lecture du fichier Excel...")
        df = pd.read_excel(excel_file)
        
        # 2. Définir l'ordre exact des colonnes selon vos spécifications
        target_columns_order = [
            'ملاحظة',
            'اختيار الموظف مسؤول', 
            'الخلاصة',
            'من طرف',
            'حالة تتبع التأشيرة',
            'الجنسية',
            'حالة جواز السفر',
            'رقم جواز السفر',
            'تاريخ استلام للسفارة',
            'تاريخ التقديم        ',  # Note: avec espaces supplémentaires
            'رقم الواتساب',
            'الاسم الكامل',
            'معرف العميل'
        ]
        
        # 3. Mapping vers les noms de colonnes de base de données
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
            'تاريخ التقديم        ': 'application_date',  # Gérer les espaces
            'رقم الواتساب': 'whatsapp_number',
            'الاسم الكامل': 'full_name',
            'معرف العميل': 'client_id'
        }
        
        # 4. Filtrer et réorganiser les colonnes
        print("🔧 Filtrage et réorganisation des colonnes...")
        
        # Supprimer les colonnes 'Unnamed'
        df_clean = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Garder seulement les colonnes cibles dans l'ordre spécifié
        available_columns = []
        for target_col in target_columns_order:
            if target_col in df_clean.columns:
                available_columns.append(target_col)
            else:
                # Chercher des variantes (espaces, etc.)
                for col in df_clean.columns:
                    if str(col).strip() == target_col.strip():
                        available_columns.append(col)
                        break
        
        print(f"✅ Colonnes trouvées: {len(available_columns)}/{len(target_columns_order)}")
        
        # Réorganiser le DataFrame selon l'ordre exact
        df_ordered = df_clean[available_columns]
        
        # 5. Afficher la structure finale
        print("\n📋 STRUCTURE FINALE DES COLONNES:")
        print("-" * 50)
        for i, col in enumerate(df_ordered.columns, 1):
            db_col = column_mapping.get(col, col)
            print(f"{i:2d}. '{col}' → {db_col}")
        
        # 6. Afficher un échantillon des données
        print("\n📝 ÉCHANTILLON DE DONNÉES (3 premières lignes):")
        print("-" * 60)
        print(df_ordered.head(3).to_string())
        
        # 7. Préparer les données pour l'import
        print("\n💾 Préparation des données pour l'import...")
        
        # Nettoyer les données
        df_ordered = df_ordered.fillna('')
        
        # Convertir en dictionnaires
        records = []
        for index, row in df_ordered.iterrows():
            record = {}
            for col in df_ordered.columns:
                db_col = column_mapping.get(col, col)
                value = str(row[col]).strip() if pd.notna(row[col]) else ''
                record[db_col] = value
            records.append(record)
        
        print(f"✅ {len(records)} enregistrements préparés")
        
        # 8. Sauvegarder la structure pour l'interface web
        structure_info = {
            "column_order": [column_mapping.get(col, col) for col in df_ordered.columns],
            "arabic_headers": list(df_ordered.columns),
            "database_columns": [column_mapping.get(col, col) for col in df_ordered.columns],
            "total_records": len(records),
            "sample_data": records[:3] if records else []
        }
        
        with open('restructured_columns.json', 'w', encoding='utf-8') as f:
            json.dump(structure_info, f, ensure_ascii=False, indent=2)
        
        print("📄 Structure sauvegardée dans: restructured_columns.json")
        
        # 9. Vider la base de données existante
        print("\n🗑️ Nettoyage de la base de données...")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clients")
        conn.commit()
        print("✅ Base de données nettoyée")
        
        # 10. Importer les nouvelles données
        print("\n📥 Import des données restructurées...")
        
        success_count = 0
        error_count = 0
        
        for i, record in enumerate(records):
            try:
                # Générer un ID client si manquant
                if not record.get('client_id'):
                    record['client_id'] = f"CLI{i+1:03d}"
                
                # Préparer les données pour l'insertion
                insert_data = {
                    'client_id': record.get('client_id', ''),
                    'full_name': record.get('full_name', ''),
                    'whatsapp_number': record.get('whatsapp_number', ''),
                    'application_date': record.get('application_date', ''),
                    'transaction_date': record.get('transaction_date', ''),
                    'passport_number': record.get('passport_number', ''),
                    'passport_status': record.get('passport_status', ''),
                    'nationality': record.get('nationality', ''),
                    'visa_status': record.get('visa_status', ''),
                    'processed_by': record.get('processed_by', ''),
                    'summary': record.get('summary', ''),
                    'notes': record.get('notes', ''),
                    'responsible_employee': record.get('responsible_employee', ''),
                    'created_at': datetime.now().isoformat()
                }
                
                # Insérer dans la base de données
                columns = ', '.join(insert_data.keys())
                placeholders = ', '.join(['?' for _ in insert_data.values()])
                values = tuple(insert_data.values())
                
                cursor.execute(f"INSERT INTO clients ({columns}) VALUES ({placeholders})", values)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"❌ Erreur ligne {i+1}: {e}")
        
        conn.commit()
        conn.close()
        
        # 11. Résumé final
        print("\n🎉 IMPORT RESTRUCTURÉ TERMINÉ!")
        print("=" * 60)
        print(f"✅ Enregistrements importés: {success_count}")
        print(f"❌ Erreurs: {error_count}")
        print(f"📊 Total traité: {len(records)}")
        print(f"📋 Colonnes dans l'ordre: {len(available_columns)}")
        
        return {
            "success": True,
            "imported": success_count,
            "errors": error_count,
            "total": len(records),
            "columns": available_columns
        }
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import restructuré: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = restructured_import()
    print(f"\n📄 Résultat: {json.dumps(result, ensure_ascii=False)}")
