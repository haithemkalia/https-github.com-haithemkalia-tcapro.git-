#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Créer le client CLI100N automatiquement
"""

import sqlite3
import datetime
import hashlib

def create_cli100n():
    try:
        conn = sqlite3.connect('visa_system.db')
        cursor = conn.cursor()
        
        print("🎯 CRÉATION DE CLI100N")
        print("=" * 30)
        
        # Vérifier d'abord si CLI100N existe déjà
        cursor.execute("SELECT COUNT(*) FROM clients WHERE client_id = 'CLI100N'")
        exists = cursor.fetchone()[0]
        
        if exists > 0:
            print("⚠️  CLI100N existe déjà!")
            # Afficher les détails
            cursor.execute("SELECT * FROM clients WHERE client_id = 'CLI100N'")
            client = cursor.fetchone()
            print(f"Détails: {client}")
            return
        
        # Créer CLI100N
        client_data = {
            'client_id': 'CLI100N',
            'full_name': 'نور الدين بن علي',  # Noureddine Ben Ali
            'passport_number': 'N100XYZ',
            'nationality': 'تونسي',  # Tunisien
            'date_of_birth': '1990-05-15',
            'phone': '+21650100100',
            'email': 'nouredine.benali@email.tn',
            'address': 'تونس، منطقة النصر',  # Tunis, région Nasr
            'visa_type': 'سياحية',  # Touristique
            'visa_status': 'جديد',  # Nouveau
            'destination_country': 'فرنسا',  # France
            'travel_date': '2025-12-01',
            'return_date': '2025-12-15',
            'employee_name': 'محمد السعيدي',  # Mohamed Saidi
            'notes': 'عميل جديد - تاشيرة سياحية',  # Nouveau client - visa touristique
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat()
        }
        
        # Insérer le client
        insert_query = """
        INSERT INTO clients (
            client_id, full_name, passport_number, nationality, date_of_birth,
            phone, email, address, visa_type, visa_status, destination_country,
            travel_date, return_date, employee_name, notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            client_data['client_id'],
            client_data['full_name'],
            client_data['passport_number'],
            client_data['nationality'],
            client_data['date_of_birth'],
            client_data['phone'],
            client_data['email'],
            client_data['address'],
            client_data['visa_type'],
            client_data['visa_status'],
            client_data['destination_country'],
            client_data['travel_date'],
            client_data['return_date'],
            client_data['employee_name'],
            client_data['notes'],
            client_data['created_at'],
            client_data['updated_at']
        )
        
        cursor.execute(insert_query, values)
        conn.commit()
        
        print("✅ CLI100N créé avec succès!")
        print(f"📋 Détails:")
        print(f"  - ID: {client_data['client_id']}")
        print(f"  - Nom: {client_data['full_name']}")
        print(f"  - Passeport: {client_data['passport_number']}")
        print(f"  - Nationalité: {client_data['nationality']}")
        print(f"  - Statut: {client_data['visa_status']}")
        print(f"  - Téléphone: {client_data['phone']}")
        print(f"  - Email: {client_data['email']}")
        
        # Vérifier la création
        cursor.execute("SELECT COUNT(*) FROM clients WHERE client_id = 'CLI100N'")
        count = cursor.fetchone()[0]
        print(f"\n🔍 Vérification: {count} client(s) CLI100N trouvé(s)")
        
        # Afficher le nouveau total
        cursor.execute("SELECT COUNT(*) FROM clients")
        total = cursor.fetchone()[0]
        print(f"📊 Nouveau total des clients: {total}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    create_cli100n()