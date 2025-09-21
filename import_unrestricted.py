#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'import SANS RESTRICTION pour le fichier Excel
Importe TOUS les clients sans exception, doublons, colonnes vides inclus
"""

import pandas as pd
import sqlite3
from datetime import datetime
import json

def safe_str(value):
    """Convertir une valeur en string de manière sécurisée"""
    if pd.isna(value) or value is None:
        return ''
    return str(value).strip()

def import_all_clients_unrestricted():
    """Importer TOUS les clients sans aucune restriction"""
    
    # Lire le fichier Excel
    print("📁 Lecture du fichier Excel...")
    df = pd.read_excel('قائمة الزبائن معرض_أكتوبر2025 (38).xlsx')
    
    print(f"📊 Fichier lu: {len(df)} lignes trouvées")
    
    # Connexion à la base de données
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    
    # Compter les clients existants
    cursor.execute('SELECT COUNT(*) FROM clients')
    initial_count = cursor.fetchone()[0]
    print(f"📈 Clients existants dans la base: {initial_count}")
    
    imported_count = 0
    error_count = 0
    
    # Traiter chaque ligne SANS EXCEPTION
    for index, row in df.iterrows():
        try:
            # Extraire TOUTES les données telles qu'elles sont
            client_data = {
                'client_id': safe_str(row.get('معرف العميل', f'AUTO_{datetime.now().strftime("%Y%m%d%H%M%S")}_{index}')),
                'full_name': safe_str(row.get('الاسم الكامل', '')),
                'whatsapp_number': safe_str(row.get('رقم الواتساب', '')),
                'whatsapp_number_clean': safe_str(row.get('رقم الواتساب', '')).replace(' ', '').replace('-', '').replace('+', ''),
                'application_date': safe_str(row.get('تاريخ التقديم', '')),
                'transaction_date': safe_str(row.get('تاريخ استلام المعملة', '')),
                'passport_number': safe_str(row.get('رقم جواز السفر', '')),
                'passport_status': safe_str(row.get('حالة جواز السفر', '')),
                'passport_status_normalized': safe_str(row.get('حالة جواز السفر', '')),
                'nationality': safe_str(row.get('الجنسية', '')),
                'visa_status': safe_str(row.get('حالة تتبع التأشيرة', 'التقديم')),
                'visa_status_normalized': safe_str(row.get('حالة تتبع التأشيرة', 'التقديم')),
                'processed_by': safe_str(row.get('من طرف', '')),
                'summary': safe_str(row.get('الخلاصة', '')),
                'notes': safe_str(row.get('ملاحضة', '')),
                'responsible_employee': safe_str(row.get('اختيار الموظف', '')),
                'original_row_number': index + 1,
                'import_timestamp': datetime.now().isoformat(),
                'is_duplicate': False,  # Accepter TOUS les doublons
                'has_empty_fields': bool(not safe_str(row.get('الاسم الكامل', ''))),
                'has_errors': False,
                'original_data': json.dumps({col: safe_str(row.get(col, '')) for col in df.columns if col not in [
                    'معرف العميل', 'الاسم الكامل', 'رقم الواتساب', 'تاريخ التقديم', 
                    'تاريخ استلام المعملة', 'رقم جواز السفر', 'حالة جواز السفر', 
                    'الجنسية', 'حالة تتبع التأشيرة', 'من طرف', 'الخلاصة', 'ملاحضة', 'اختيار الموظف'
                ]}, ensure_ascii=False),
                'created_at': datetime.now().isoformat()
            }
            
            # Ajouter les colonnes Excel supplémentaires
            for i in range(13):
                col_name = f'excel_col_{i}'
                client_data[col_name] = safe_str(row.get(df.columns[i] if i < len(df.columns) else ''))
            
            # Insérer SANS VALIDATION
            cursor.execute("""
                INSERT INTO clients (
                    client_id, full_name, whatsapp_number, whatsapp_number_clean,
                    application_date, transaction_date, passport_number, passport_status,
                    passport_status_normalized, nationality, visa_status, visa_status_normalized,
                    processed_by, summary, notes, responsible_employee, original_row_number,
                    import_timestamp, is_duplicate, has_empty_fields, has_errors,
                    original_data,
                    excel_col_0, excel_col_1, excel_col_2, excel_col_3, excel_col_4,
                    excel_col_5, excel_col_6, excel_col_7, excel_col_8, excel_col_9,
                    excel_col_10, excel_col_11, excel_col_12,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client_data['client_id'], client_data['full_name'], client_data['whatsapp_number'],
                client_data['whatsapp_number_clean'], client_data['application_date'],
                client_data['transaction_date'], client_data['passport_number'],
                client_data['passport_status'], client_data['passport_status_normalized'],
                client_data['nationality'], client_data['visa_status'],
                client_data['visa_status_normalized'], client_data['processed_by'],
                client_data['summary'], client_data['notes'], client_data['responsible_employee'],
                client_data['original_row_number'], client_data['import_timestamp'],
                client_data['is_duplicate'], client_data['has_empty_fields'], 
                client_data['has_errors'], client_data['original_data'],
                client_data['excel_col_0'], client_data['excel_col_1'], client_data['excel_col_2'],
                client_data['excel_col_3'], client_data['excel_col_4'], client_data['excel_col_5'],
                client_data['excel_col_6'], client_data['excel_col_7'], client_data['excel_col_8'],
                client_data['excel_col_9'], client_data['excel_col_10'], client_data['excel_col_11'],
                client_data['excel_col_12'],
                client_data['created_at']
            ))
            
            imported_count += 1
            
            if imported_count % 50 == 0:
                print(f"✅ {imported_count} clients importés...")
                
        except Exception as e:
            error_count += 1
            print(f"❌ Erreur ligne {index + 1}: {str(e)}")
            continue
    
    # Valider les changements
    conn.commit()
    
    # Compter le nouveau total
    cursor.execute('SELECT COUNT(*) FROM clients')
    final_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n🎉 IMPORT TERMINÉ!")
    print(f"📊 Lignes traitées: {len(df)}")
    print(f"✅ Clients importés: {imported_count}")
    print(f"❌ Erreurs: {error_count}")
    print(f"📈 Total avant import: {initial_count}")
    print(f"📈 Total après import: {final_count}")
    print(f"➕ Nouveaux clients ajoutés: {final_count - initial_count}")
    
    return {
        'success': True,
        'imported': imported_count,
        'errors': error_count,
        'total_before': initial_count,
        'total_after': final_count,
        'new_clients': final_count - initial_count
    }

if __name__ == '__main__':
    result = import_all_clients_unrestricted()
    print(f"\n📋 Résultat final: {result}")