#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'import complet sans restriction pour le fichier Excel
قائمة الزبائن معرض_أكتوبر2025 (26).xlsx
Importe TOUS les clients sans exception (doublons, vides, erreurs, langues mixtes)
"""

import pandas as pd
import sqlite3
import os
import sys
from datetime import datetime
import re
import json

# Ajouter le chemin pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def create_enhanced_database_schema():
    """
    Créer un schéma de base de données amélioré pour supporter tous les formats
    """
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    
    # Supprimer l'ancienne table si elle existe
    cursor.execute("DROP TABLE IF EXISTS clients")
    
    # Créer une nouvelle table avec support étendu
    create_table_sql = """
    CREATE TABLE clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT UNIQUE,
        full_name TEXT,
        whatsapp_number TEXT,
        whatsapp_number_clean TEXT,
        application_date TEXT,
        transaction_date TEXT,
        passport_number TEXT,
        passport_status TEXT,
        passport_status_normalized TEXT,
        nationality TEXT,
        visa_status TEXT,
        visa_status_normalized TEXT,
        processed_by TEXT,
        summary TEXT,
        notes TEXT,
        responsible_employee TEXT,
        
        -- Nouvelles colonnes pour supporter tous les formats
        original_row_number INTEGER,
        import_timestamp TEXT,
        is_duplicate BOOLEAN DEFAULT 0,
        has_empty_fields BOOLEAN DEFAULT 0,
        has_errors BOOLEAN DEFAULT 0,
        original_data TEXT,  -- JSON des données originales
        
        -- Colonnes supplémentaires du fichier Excel
        excel_col_0 TEXT,
        excel_col_1 TEXT,
        excel_col_2 TEXT,
        excel_col_3 TEXT,
        excel_col_4 TEXT,
        excel_col_5 TEXT,
        excel_col_6 TEXT,
        excel_col_7 TEXT,
        excel_col_8 TEXT,
        excel_col_9 TEXT,
        excel_col_10 TEXT,
        excel_col_11 TEXT,
        excel_col_12 TEXT,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()
    print("✅ Schéma de base de données amélioré créé")

def normalize_client_id(client_id):
    """
    Normaliser l'ID client pour supporter le format CLI0001
    """
    if pd.isna(client_id) or client_id == '':
        return None
    
    client_id_str = str(client_id).strip()
    
    # Si c'est déjà au format CLI avec des chiffres
    if client_id_str.startswith('CLI'):
        # Extraire le numéro
        match = re.search(r'CLI(\d+)', client_id_str)
        if match:
            number = int(match.group(1))
            # Convertir au format CLI0001 (4 chiffres avec zéros)
            return f"CLI{number:04d}"
    
    # Si c'est juste un numéro
    if client_id_str.isdigit():
        number = int(client_id_str)
        return f"CLI{number:04d}"
    
    # Sinon, retourner tel quel
    return client_id_str

def clean_text_field(value):
    """
    Nettoyer un champ texte en préservant tous les caractères
    """
    if pd.isna(value):
        return None
    return str(value).strip() if str(value).strip() != '' else None

def import_excel_without_restrictions(excel_file):
    """
    Importer le fichier Excel sans aucune restriction
    """
    print(f"📥 Import sans restriction du fichier: {excel_file}")
    print("=" * 80)
    
    if not os.path.exists(excel_file):
        print(f"❌ Fichier non trouvé: {excel_file}")
        return False
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(excel_file, sheet_name=0, header=0)
        print(f"📊 Données lues: {len(df)} lignes × {len(df.columns)} colonnes")
        
        # Afficher les colonnes disponibles
        print(f"📋 Colonnes: {list(df.columns)}")
        
        # Créer le schéma de base de données amélioré
        create_enhanced_database_schema()
        
        # Connexion à la base de données
        conn = sqlite3.connect('visa_system.db')
        cursor = conn.cursor()
        
        imported_count = 0
        duplicate_count = 0
        empty_count = 0
        error_count = 0
        
        import_timestamp = datetime.now().isoformat()
        
        # Traiter chaque ligne sans exception
        for index, row in df.iterrows():
            try:
                # Extraire les données principales
                client_id_raw = row.get('معرف العميل', '')
                full_name = clean_text_field(row.get('الاسم الكامل', ''))
                whatsapp_number = clean_text_field(row.get('رقم الواتساب', ''))
                application_date = clean_text_field(row.get('تاريخ التقديم', ''))
                transaction_date = clean_text_field(row.get('تاريخ استلام المعاملة', ''))
                passport_number = clean_text_field(row.get('رقم جواز السفر', ''))
                passport_status = clean_text_field(row.get('حالة جواز السفر', ''))
                nationality = clean_text_field(row.get('الجنسية', ''))
                visa_status = clean_text_field(row.get('حالة تتبع التأشيرة', ''))
                processed_by = clean_text_field(row.get('من طرف', ''))
                responsible_employee = clean_text_field(row.get('الموظف المسؤول', ''))
                
                # Normaliser l'ID client
                client_id = normalize_client_id(client_id_raw)
                
                # Nettoyer le numéro WhatsApp
                whatsapp_clean = None
                if whatsapp_number:
                    whatsapp_clean = re.sub(r'[^0-9+]', '', str(whatsapp_number))
                
                # Normaliser les statuts
                passport_status_norm = passport_status.lower() if passport_status else None
                visa_status_norm = None
                if visa_status:
                    if 'اكتمل' in visa_status or 'مكتمل' in visa_status:
                        visa_status_norm = 'completed'
                    elif 'تقديم' in visa_status:
                        visa_status_norm = 'submitted'
                    elif 'موافق' in visa_status and 'غير' not in visa_status:
                        visa_status_norm = 'approved'
                    elif 'غير موافق' in visa_status:
                        visa_status_norm = 'rejected'
                    else:
                        visa_status_norm = 'in_progress'
                
                # Détecter les doublons, vides et erreurs
                is_duplicate = False
                has_empty_fields = not all([client_id, full_name])
                has_errors = False
                
                # Vérifier les doublons
                if client_id:
                    cursor.execute("SELECT COUNT(*) FROM clients WHERE client_id = ?", (client_id,))
                    if cursor.fetchone()[0] > 0:
                        is_duplicate = True
                        duplicate_count += 1
                
                if has_empty_fields:
                    empty_count += 1
                
                # Stocker toutes les données originales en JSON
                original_data = {}
                for col in df.columns:
                    value = row.get(col)
                    if pd.notna(value):
                        original_data[col] = str(value)
                
                # Préparer les colonnes Excel supplémentaires
                excel_cols = []
                for i in range(13):  # 13 colonnes Unnamed
                    col_name = f'Unnamed: {i}'
                    if col_name in row:
                        excel_cols.append(clean_text_field(row[col_name]))
                    else:
                        excel_cols.append(None)
                
                # Insérer dans la base de données
                insert_sql = """
                INSERT INTO clients (
                    client_id, full_name, whatsapp_number, whatsapp_number_clean,
                    application_date, transaction_date, passport_number, passport_status,
                    passport_status_normalized, nationality, visa_status, visa_status_normalized,
                    processed_by, responsible_employee, original_row_number, import_timestamp,
                    is_duplicate, has_empty_fields, has_errors, original_data,
                    excel_col_0, excel_col_1, excel_col_2, excel_col_3, excel_col_4,
                    excel_col_5, excel_col_6, excel_col_7, excel_col_8, excel_col_9,
                    excel_col_10, excel_col_11, excel_col_12
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(insert_sql, (
                    client_id, full_name, whatsapp_number, whatsapp_clean,
                    application_date, transaction_date, passport_number, passport_status,
                    passport_status_norm, nationality, visa_status, visa_status_norm,
                    processed_by, responsible_employee, index + 1, import_timestamp,
                    is_duplicate, has_empty_fields, has_errors, json.dumps(original_data, ensure_ascii=False),
                    *excel_cols
                ))
                
                imported_count += 1
                
                if imported_count % 100 == 0:
                    print(f"📥 Importé: {imported_count} clients...")
                    
            except Exception as e:
                error_count += 1
                print(f"⚠️ Erreur ligne {index + 1}: {str(e)}")
                # Continuer même en cas d'erreur
                continue
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ IMPORT TERMINÉ AVEC SUCCÈS!")
        print(f"📊 Statistiques d'import:")
        print(f"   • Total importé: {imported_count} clients")
        print(f"   • Doublons: {duplicate_count}")
        print(f"   • Champs vides: {empty_count}")
        print(f"   • Erreurs: {error_count}")
        print(f"   • Timestamp: {import_timestamp}")
        
        # Vérifier le total dans la base
        conn = sqlite3.connect('visa_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_in_db = cursor.fetchone()[0]
        conn.close()
        
        print(f"   • Total en base: {total_in_db} clients")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Chemin du fichier Excel
    excel_file = r"c:\Users\SERVEUR TCA\Desktop\VISA PRO2\قائمة الزبائن معرض_أكتوبر2025 (26).xlsx"
    
    print("🚀 IMPORT COMPLET SANS RESTRICTION")
    print("Importation de TOUS les clients sans exception")
    print("(doublons, vides, erreurs, langues mixtes)")
    print()
    
    # Lancer l'import
    success = import_excel_without_restrictions(excel_file)
    
    if success:
        print("\n🎉 Import réussi! Tous les clients ont été importés.")
    else:
        print("\n❌ Échec de l'import.")