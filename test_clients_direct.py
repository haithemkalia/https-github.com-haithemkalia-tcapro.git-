#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test direct des clients sans cache
"""

import sys
from pathlib import Path

# Ajouter le dossier src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_direct_clients():
    """Tester la récupération directe des clients"""
    print("🔍 Test direct de récupération des clients...")
    
    try:
        from database.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        print(f"✅ DatabaseManager initialisé")
        
        # Test direct de la méthode get_all_clients du DatabaseManager
        print("\n📊 Test DatabaseManager.get_all_clients()...")
        clients, total = db_manager.get_all_clients(page=1, per_page=10)
        print(f"   Résultat: {len(clients)} clients, total: {total}")
        
        if clients:
            print(f"   Type du premier client: {type(clients[0])}")
            print(f"   Premier client: {clients[0]}")
            
            # Convertir en dict si nécessaire
            if hasattr(clients[0], '_asdict'):
                client_dict = clients[0]._asdict()
                print(f"   Converti en dict: {client_dict}")
            elif hasattr(clients[0], 'keys'):
                client_dict = dict(clients[0])
                print(f"   Converti en dict: {client_dict}")
        
        # Test sans pagination
        print("\n📊 Test sans pagination...")
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients ORDER BY client_id DESC LIMIT 5")
        raw_clients = cursor.fetchall()
        print(f"   Résultat brut: {len(raw_clients)} clients")
        
        if raw_clients:
            print(f"   Type: {type(raw_clients[0])}")
            print(f"   Premier client brut: {raw_clients[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_client_controller_without_cache():
    """Tester le ClientController en désactivant temporairement le cache"""
    print("\n👥 Test ClientController sans cache...")
    
    try:
        from database.database_manager import DatabaseManager
        from controllers.client_controller import ClientController
        
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        # Accéder directement à la méthode sans décorateur
        print("   Test de la méthode get_all_clients sans cache...")
        
        # Appeler la méthode directement sur l'instance
        # En contournant le décorateur
        original_method = ClientController.get_all_clients.__wrapped__
        clients, total = original_method(client_controller, page=1, per_page=10)
        
        print(f"   Résultat sans cache: {len(clients)} clients, total: {total}")
        
        if clients:
            print(f"   Type: {type(clients[0])}")
            print(f"   Premier client: {clients[0]}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Fonction principale"""
    print("🚨 TEST DIRECT DES CLIENTS")
    print("=" * 50)
    
    test_direct_clients()
    test_client_controller_without_cache()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés!")

if __name__ == "__main__":
    main()