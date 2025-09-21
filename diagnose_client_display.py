#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour le problème d'affichage des clients
Après l'import de 844 clients, aucun ne s'affiche dans l'interface
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers.client_controller import ClientController
from src.database.database_manager import DatabaseManager
import sqlite3

def diagnose_client_display():
    """Diagnostiquer le problème d'affichage des clients"""
    
    print("🔍 Diagnostic du problème d'affichage des clients...")
    print("="*60)
    
    try:
        # 1. Vérifier la base de données directement
        print("\n1️⃣ Vérification directe de la base de données:")
        
        # Vérifier les fichiers de base de données
        db_files = ['visa_system.db', 'clients.db', 'data/visa_tracking.db']
        for db_file in db_files:
            if os.path.exists(db_file):
                print(f"   ✅ {db_file} existe")
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM clients")
                    count = cursor.fetchone()[0]
                    print(f"   📊 {db_file}: {count} clients")
                    
                    # Afficher quelques exemples
                    cursor.execute("SELECT client_id, full_name FROM clients LIMIT 5")
                    samples = cursor.fetchall()
                    for sample in samples:
                        print(f"      - {sample[0]}: {sample[1]}")
                    
                    conn.close()
                except Exception as e:
                    print(f"   ❌ Erreur avec {db_file}: {e}")
            else:
                print(f"   ❌ {db_file} n'existe pas")
        
        # 2. Tester le DatabaseManager
        print("\n2️⃣ Test du DatabaseManager:")
        try:
            db_manager = DatabaseManager()
            print(f"   ✅ DatabaseManager initialisé")
            print(f"   📁 Chemin de la DB: {db_manager.db_path}")
            
            # Test de connexion
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients")
            count = cursor.fetchone()[0]
            print(f"   📊 Clients via DatabaseManager: {count}")
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Erreur DatabaseManager: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Tester le ClientController
        print("\n3️⃣ Test du ClientController:")
        try:
            db_manager = DatabaseManager()
            client_controller = ClientController(db_manager)
            print(f"   ✅ ClientController initialisé")
            
            # Test get_all_clients
            all_clients = client_controller.get_all_clients()
            print(f"   📊 get_all_clients(): {len(all_clients)} clients")
            
            # Afficher quelques exemples
            for i, client in enumerate(all_clients[:5]):
                print(f"      {i+1}. {client.get('client_id', 'N/A')}: {client.get('full_name', 'N/A')}")
            
            # Test avec pagination
            paginated_clients = client_controller.get_all_clients(page=1, per_page=25)
            print(f"   📄 get_all_clients(page=1, per_page=25): {len(paginated_clients)} clients")
            
        except Exception as e:
            print(f"   ❌ Erreur ClientController: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. Tester les requêtes SQL spécifiques
        print("\n4️⃣ Test des requêtes SQL:")
        try:
            db_manager = DatabaseManager()
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            # Requête de base
            cursor.execute("SELECT COUNT(*) FROM clients")
            total_count = cursor.fetchone()[0]
            print(f"   📊 Total clients: {total_count}")
            
            # Requête avec ORDER BY (comme dans get_all_clients)
            cursor.execute("SELECT COUNT(*) FROM clients ORDER BY client_id DESC")
            ordered_count = cursor.fetchone()[0]
            print(f"   📊 Clients avec ORDER BY: {ordered_count}")
            
            # Requête avec LIMIT (comme dans pagination)
            cursor.execute("SELECT client_id, full_name FROM clients ORDER BY client_id DESC LIMIT 5")
            limited_results = cursor.fetchall()
            print(f"   📄 Top 5 clients:")
            for result in limited_results:
                print(f"      - {result[0]}: {result[1]}")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Erreur requêtes SQL: {e}")
            import traceback
            traceback.print_exc()
        
        # 5. Vérifier la structure de la table
        print("\n5️⃣ Vérification de la structure de la table:")
        try:
            db_manager = DatabaseManager()
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(clients)")
            columns = cursor.fetchall()
            print(f"   📋 Colonnes de la table clients:")
            for col in columns:
                print(f"      - {col[1]} ({col[2]})")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Erreur structure table: {e}")
        
        # 6. Test de la route Flask (simulation)
        print("\n6️⃣ Simulation de la route Flask:")
        try:
            from app import app
            with app.test_client() as client:
                response = client.get('/clients')
                print(f"   🌐 Status code: {response.status_code}")
                print(f"   📄 Content length: {len(response.data)} bytes")
                
                # Vérifier si 'aucun client' apparaît dans la réponse
                content = response.data.decode('utf-8')
                if 'aucun client' in content.lower() or 'no client' in content.lower():
                    print(f"   ⚠️  Message 'aucun client' détecté dans la réponse")
                else:
                    print(f"   ✅ Pas de message 'aucun client' détecté")
                
        except Exception as e:
            print(f"   ❌ Erreur test route: {e}")
        
        print("\n" + "="*60)
        print("🏁 Diagnostic terminé")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_client_display()