#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Créer le client CLI100N avec la structure correcte de la table
"""

import sqlite3
import datetime

def create_cli100n_correct():
    try:
        conn = sqlite3.connect('visa_system.db')
        cursor = conn.cursor()
        
        print("🎯 CRÉATION DE CLI100N (Structure Correcte)")
        print("=" * 45)
        
        # Vérifier d'abord si CLI100N existe déjà
        cursor.execute("SELECT COUNT(*) FROM clients WHERE client_id = 'CLI100N'")
        exists = cursor.fetchone()[0]
        
        if exists > 0:
            print("⚠️  CLI100N existe déjà!")
            # Afficher les détails
            cursor.execute("SELECT client_id, full_name, whatsapp_number, passport_number, nationality, visa_status FROM clients WHERE client_id = 'CLI100N'")
            client = cursor.fetchone()
            if client:
                print(f"Détails existants:")
                print(f"  - ID: {client[0]}")
                print(f"  - Nom: {client[1]}")
                print(f"  - WhatsApp: {client[2]}")
                print(f"  - Passeport: {client[3]}")
                print(f"  - Nationalité: {client[4]}")
                print(f"  - Statut: {client[5]}")
            return
        
        # Créer CLI100N avec la structure correcte
        client_data = {
            'client_id': 'CLI100N',
            'full_name': 'نور الدين بن علي',  # Noureddine Ben Ali
            'whatsapp_number': '+21650100100',
            'whatsapp_number_clean': '21650100100',
            'application_date': '2025-09-25',
            'transaction_date': '2025-09-25',
            'passport_number': 'N100XYZ',
            'passport_status': 'جديد',  # Nouveau
            'passport_status_normalized': 'جديد',
            'nationality': 'تونسي',  # Tunisien
            'visa_status': 'جديد',  # Nouveau
            'visa_status_normalized': 'جديد',
            'processed_by': 'محمد السعيدي',  # Mohamed Saidi
            'summary': 'عميل جديد - تاشيرة سياحية',  # Nouveau client - visa touristique
            'notes': 'تم إنشاء CLI100N عبر النظام',  # CLI100N créé via le système
            'responsible_employee': 'محمد السعيدي',  # Mohamed Saidi
            'original_row_number': 1000,
            'import_timestamp': datetime.datetime.now().isoformat(),
            'is_duplicate': False,
            'has_empty_fields': False,
            'has_errors': False,
            'original_data': 'CLI100N|نور الدين بن علي|+21650100100|N100XYZ|تونسي|جديد|سياحية|فرنسا',
            'excel_col_0': 'CLI100N',
            'excel_col_1': 'نور الدين بن علي',
            'excel_col_2': '+21650100100',
            'excel_col_3': 'N100XYZ',
            'excel_col_4': 'تونسي',
            'excel_col_5': 'جديد',
            'excel_col_6': 'سياحية',
            'excel_col_7': 'فرنسا',
            'excel_col_8': '',
            'excel_col_9': '',
            'excel_col_10': '',
            'excel_col_11': '',
            'excel_col_12': '',
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat(),
            'auto_generated_id': True,
            'empty_name_accepted': False,
            'extra_data': '{\"created_by\": \"system\", \"purpose\": \"demo\"}'
        }
        
        # Insérer le client
        insert_query = """
        INSERT INTO clients (
            client_id, full_name, whatsapp_number, whatsapp_number_clean,
            application_date, transaction_date, passport_number, passport_status,
            passport_status_normalized, nationality, visa_status, visa_status_normalized,
            processed_by, summary, notes, responsible_employee, original_row_number,
            import_timestamp, is_duplicate, has_empty_fields, has_errors, original_data,
            excel_col_0, excel_col_1, excel_col_2, excel_col_3, excel_col_4, excel_col_5,
            excel_col_6, excel_col_7, excel_col_8, excel_col_9, excel_col_10, excel_col_11,
            excel_col_12, created_at, updated_at, auto_generated_id, empty_name_accepted,
            extra_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            client_data['client_id'],
            client_data['full_name'],
            client_data['whatsapp_number'],
            client_data['whatsapp_number_clean'],
            client_data['application_date'],
            client_data['transaction_date'],
            client_data['passport_number'],
            client_data['passport_status'],
            client_data['passport_status_normalized'],
            client_data['nationality'],
            client_data['visa_status'],
            client_data['visa_status_normalized'],
            client_data['processed_by'],
            client_data['summary'],
            client_data['notes'],
            client_data['responsible_employee'],
            client_data['original_row_number'],
            client_data['import_timestamp'],
            client_data['is_duplicate'],
            client_data['has_empty_fields'],
            client_data['has_errors'],
            client_data['original_data'],
            client_data['excel_col_0'],
            client_data['excel_col_1'],
            client_data['excel_col_2'],
            client_data['excel_col_3'],
            client_data['excel_col_4'],
            client_data['excel_col_5'],
            client_data['excel_col_6'],
            client_data['excel_col_7'],
            client_data['excel_col_8'],
            client_data['excel_col_9'],
            client_data['excel_col_10'],
            client_data['excel_col_11'],
            client_data['excel_col_12'],
            client_data['created_at'],
            client_data['updated_at'],
            client_data['auto_generated_id'],
            client_data['empty_name_accepted'],
            client_data['extra_data']
        )
        
        cursor.execute(insert_query, values)
        conn.commit()
        
        print("✅ CLI100N créé avec succès!")
        print(f"📋 Détails du nouveau client:")
        print(f"  🔑 ID: {client_data['client_id']}")
        print(f"  👤 Nom: {client_data['full_name']}")
        print(f"  📱 WhatsApp: {client_data['whatsapp_number']}")
        print(f"  📘 Passeport: {client_data['passport_number']}")
        print(f"  🌍 Nationalité: {client_data['nationality']}")
        print(f"  📊 Statut: {client_data['visa_status']}")
        print(f"  👨‍💼 Traité par: {client_data['processed_by']}")
        print(f"  📅 Date: {client_data['application_date']}")
        
        # Vérifier la création
        cursor.execute("SELECT COUNT(*) FROM clients WHERE client_id = 'CLI100N'")
        count = cursor.fetchone()[0]
        print(f"\n🔍 Vérification: {count} client(s) CLI100N trouvé(s)")
        
        # Afficher le nouveau total
        cursor.execute("SELECT COUNT(*) FROM clients")
        total = cursor.fetchone()[0]
        print(f"📊 Nouveau total des clients: {total}")
        
        # Vérifier la position dans la séquence
        cursor.execute("""
            SELECT client_id, full_name 
            FROM clients 
            WHERE client_id BETWEEN 'CLI099' AND 'CLI101'
            ORDER BY client_id
        """)
        neighbors = cursor.fetchall()
        print(f"\n🏘️  Voisins de CLI100N:")
        for client in neighbors:
            print(f"  {client[0]}: {client[1]}")
        
        conn.close()
        
        print("\n🎉 CLI100N est maintenant disponible dans إدارة العملاء!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    create_cli100n_correct()