#!/usr/bin/env python3
"""
Script pour peupler la base de données Render avec des données de test
"""

import os
import sys
import sqlite3
from datetime import datetime

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def populate_test_data():
    """Ajouter des données de test à la base de données"""
    
    # Définir le chemin de la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'clients.db')
    
    # Créer le répertoire data s'il n'existe pas
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Vérifier si la table existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='clients'
        """)
        
        if not cursor.fetchone():
            print("❌ La table 'clients' n'existe pas. Veuillez d'abord initialiser la base de données.")
            return False
        
        # Vérifier si des données existent déjà
        cursor.execute('SELECT COUNT(*) FROM clients')
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"ℹ️  La base de données contient déjà {count} clients.")
            response = input("Voulez-vous ajouter des données de test supplémentaires ? (o/n): ")
            if response.lower() != 'o':
                return False
        
        # Données de test réalistes
        test_clients = [
            {
                'client_id': 'CLI001',
                'full_name': 'Mohamed Ben Ahmed',
                'whatsapp_number': '+21650123456',
                'whatsapp_number_clean': '21650123456',
                'nationality': 'Tunisienne',
                'passport_number': 'T123456',
                'passport_status': 'Validé',
                'visa_status': 'En cours de traitement',
                'responsible_employee': 'Sarah Martinez',
                'application_date': '2024-01-15',
                'transaction_date': '2024-01-20',
                'processed_by': 'Sarah Martinez',
                'summary': 'Demande de visa touristique',
                'notes': 'Client urgent, départ prévu en mars'
            },
            {
                'client_id': 'CLI002',
                'full_name': 'Fatima Al-Zahraoui',
                'whatsapp_number': '+21698765432',
                'whatsapp_number_clean': '21698765432',
                'nationality': 'Marocaine',
                'passport_number': 'M789012',
                'passport_status': 'En cours',
                'visa_status': 'Documents reçus',
                'responsible_employee': 'Jean Dubois',
                'application_date': '2024-01-18',
                'transaction_date': '2024-01-22',
                'processed_by': 'Jean Dubois',
                'summary': 'Demande de visa étudiant',
                'notes': 'Inscription université confirmée'
            },
            {
                'client_id': 'CLI003',
                'full_name': 'Ali Hassan',
                'whatsapp_number': '+21655112233',
                'whatsapp_number_clean': '21655112233',
                'nationality': 'Tunisienne',
                'passport_number': 'T654321',
                'passport_status': 'Validé',
                'visa_status': 'Approuvé',
                'responsible_employee': 'Marie Laurent',
                'application_date': '2024-01-10',
                'transaction_date': '2024-01-25',
                'processed_by': 'Marie Laurent',
                'summary': 'Demande de visa business',
                'notes': 'Entrepreneur, voyage d\'affaires'
            },
            {
                'client_id': 'CLI004',
                'full_name': 'Amina Belhadj',
                'whatsapp_number': '+21644556677',
                'whatsapp_number_clean': '21644556677',
                'nationality': 'Tunisienne',
                'passport_number': 'T112233',
                'passport_status': 'Refusé',
                'visa_status': 'En attente de documents',
                'responsible_employee': 'Sarah Martinez',
                'application_date': '2024-01-12',
                'transaction_date': '2024-01-18',
                'processed_by': 'Sarah Martinez',
                'summary': 'Demande de visa familial',
                'notes': 'Documents complémentaires demandés'
            },
            {
                'client_id': 'CLI005',
                'full_name': 'Youssef Ben Youssef',
                'whatsapp_number': '+21677889900',
                'whatsapp_number_clean': '21677889900',
                'nationality': 'Tunisienne',
                'passport_number': 'T998877',
                'passport_status': 'Validé',
                'visa_status': 'Prêt pour départ',
                'responsible_employee': 'Jean Dubois',
                'application_date': '2024-01-08',
                'transaction_date': '2024-01-15',
                'processed_by': 'Jean Dubois',
                'summary': 'Demande de visa travail',
                'notes': 'Contrat de travail signé, départ imminent'
            }
        ]
        
        # Insérer les données
        inserted_count = 0
        for client in test_clients:
            try:
                cursor.execute('''
                    INSERT INTO clients (
                        client_id, full_name, whatsapp_number, whatsapp_number_clean,
                        nationality, passport_number, passport_status, visa_status,
                        responsible_employee, application_date, transaction_date,
                        processed_by, summary, notes, created_at, updated_at,
                        is_duplicate, auto_generated_id, empty_name_accepted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    client['client_id'],
                    client['full_name'],
                    client['whatsapp_number'],
                    client['whatsapp_number_clean'],
                    client['nationality'],
                    client['passport_number'],
                    client['passport_status'],
                    client['visa_status'],
                    client['responsible_employee'],
                    client['application_date'],
                    client['transaction_date'],
                    client['processed_by'],
                    client['summary'],
                    client['notes'],
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    False,  # is_duplicate
                    False,  # auto_generated_id
                    False   # empty_name_accepted
                ))
                inserted_count += 1
                
            except sqlite3.IntegrityError as e:
                print(f"⚠️  Client {client['client_id']} déjà existant: {e}")
                continue
        
        conn.commit()
        print(f"✅ {inserted_count} clients de test ajoutés avec succès!")
        
        # Afficher un résumé
        cursor.execute('SELECT COUNT(*) FROM clients')
        total_count = cursor.fetchone()[0]
        print(f"📊 Total des clients dans la base: {total_count}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors du peuplement des données: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    print("🚀 Démarrage du peuplement des données de test pour Render...")
    success = populate_test_data()
    
    if success:
        print("\n✅ Opération terminée avec succès!")
        print("💡 Vous pouvez maintenant vérifier vos clients sur le dashboard Render.")
    else:
        print("\n❌ L'opération a échoué.")
        sys.exit(1)