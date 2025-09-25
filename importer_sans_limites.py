#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏴‍☠️ IMPORTATEUR SANS LIMITES - ÉDITION ARABE
✅ Accepte TOUT sans vérification ni restriction
"""

import pandas as pd
import sqlite3
from datetime import datetime
import os

def importer_sans_limites():
    """Importation complète sans aucune restriction"""
    
    print("🎯 DÉBUT DE L'IMPORTATION SANS LIMITES")
    print("="*60)
    
    # Charger le fichier Excel
    fichier = 'clients_export_20250925_233544.xlsx'
    print(f"📁 Chargement de: {fichier}")
    
    df = pd.read_excel(fichier, engine='openpyxl', dtype=str)
    print(f"📊 Fichier chargé: {len(df)} clients trouvés")
    
    # Connexion à la base de données
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    
    # Compter avant import
    cursor.execute("SELECT COUNT(*) FROM clients")
    count_avant = cursor.fetchone()[0]
    print(f"📈 Clients avant import: {count_avant}")
    
    # Importer chaque ligne sans restriction
    importes = 0
    erreurs = 0
    
    for index, row in df.iterrows():
        try:
            # Préparer les données - accepter telles quelles
            data = {
                'client_id': str(row.get('معرف العميل', f'CLI{1000 + index}')),
                'full_name': str(row.get('الاسم الكامل', f'عميل_غير_مسمى_{index}')),
                'whatsapp_number': str(row.get('رقم الواتساب', 'غير_محدد')),
                'application_date': str(row.get('تاريخ التقديم', datetime.now().strftime('%Y-%m-%d'))),
                'transaction_date': str(row.get('تاريخ استلام للسفارة', datetime.now().strftime('%Y-%m-%d'))),
                'passport_number': str(row.get('رقم جواز السفر', 'غير_محدد')),
                'passport_status': str(row.get('حالة جواز السفر', 'غير_محدد')),
                'nationality': str(row.get('الجنسية', 'غير_محددة')),
                'visa_status': str(row.get('حالة تتبع التأشيرة', 'قيد_الانتظار')),
                'responsible_employee': str(row.get('اختيار الموظف', 'غير_محدد')),
                'processed_by': str(row.get('من طرف', 'غير_محدد')),
                'summary': str(row.get('الخلاصة', 'لا_يوجد')),
                'notes': str(row.get('ملاحظة', 'لا_يوجد')),
                'excel_col_1': '',
                'excel_col_2': '',
                'excel_col_3': '',
                'excel_col_4': '',
                'excel_col_5': '',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Insertion directe sans vérification
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = list(data.values())
            
            query = f"INSERT INTO clients ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)
            
            importes += 1
            
            if importes % 100 == 0:
                print(f"✅ {importes} clients importés...")
                
        except Exception as e:
            erreurs += 1
            print(f"⚠️ Erreur ligne {index} (ignorée): {str(e)}")
            continue
    
    conn.commit()
    
    # Compter après import
    cursor.execute("SELECT COUNT(*) FROM clients")
    count_apres = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "="*60)
    print("🏁 RÉSULTAT DE L'IMPORTATION")
    print("="*60)
    print(f"✅ Clients importés: {importes}")
    print(f"⚠️ Erreurs (ignorées): {erreurs}")
    print(f"📈 Total avant: {count_avant}")
    print(f"📊 Total après: {count_apres}")
    print(f"📈 Différence: {count_apres - count_avant}")
    
    return importes, erreurs

if __name__ == "__main__":
    print("🏴‍☠️ IMPORTATEUR SANS LIMITES")
    print("✅ Accepte tous les doublons")
    print("✅ Accepte toutes les données manquantes")
    print("✅ Génère automatiquement les IDs")
    print("✅ Aucune vérification effectuée")
    print("="*60)
    
    total_importes, total_erreurs = importer_sans_limites()
    
    print(f"\n🎉 Importation terminée!")
    print(f"📁 Base de données mise à jour: visa_system.db")
    
    # Vérifier le résultat
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clients")
    total_clients = cursor.fetchone()[0]
    cursor.execute("SELECT client_id, full_name FROM clients ORDER BY created_at DESC LIMIT 5")
    derniers = cursor.fetchall()
    conn.close()
    
    print(f"\n📊 Total général de clients: {total_clients}")
    print("🆔 5 derniers clients ajoutés:")
    for client in derniers:
        print(f"   {client[0]} - {client[1]}")