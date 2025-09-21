#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_database_content():
    """Vérifier le contenu de la base de données"""
    
    db_paths = ['data/visa_tracking.db', 'visa_system.db']
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"\n📂 Vérification de: {db_path}")
            print("=" * 50)
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Vérifier les tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"Tables trouvées: {[t[0] for t in tables]}")
                
                # Vérifier le nombre de clients
                cursor.execute("SELECT COUNT(*) FROM clients;")
                count = cursor.fetchone()[0]
                print(f"Nombre de clients: {count}")
                
                if count > 0:
                    # Vérifier les colonnes
                    cursor.execute("PRAGMA table_info(clients);")
                    columns = cursor.fetchall()
                    print(f"\nColonnes de la table clients:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
                    
                    # Vérifier quelques données
                    cursor.execute("SELECT client_id, full_name, responsible_employee, application_date FROM clients LIMIT 5;")
                    samples = cursor.fetchall()
                    print(f"\nÉchantillon de données:")
                    for sample in samples:
                        print(f"  ID: {sample[0]}, Nom: {sample[1]}, Employé: {sample[2]}, Date: {sample[3]}")
                
                conn.close()
                
            except Exception as e:
                print(f"Erreur: {e}")
        else:
            print(f"❌ {db_path} n'existe pas")

if __name__ == "__main__":
    check_database_content()