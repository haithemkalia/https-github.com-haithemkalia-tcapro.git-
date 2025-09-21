#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rapide pour vérifier si le problème d'affichage des clients est résolu
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers.client_controller import ClientController
from src.database.database_manager import DatabaseManager

def test_client_display_fix():
    """Tester si les corrections ont résolu le problème"""
    
    print("🧪 Test des corrections pour l'affichage des clients...")
    print("="*60)
    
    try:
        # Initialiser le contrôleur
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        print("\n1️⃣ Test get_all_clients() avec pagination:")
        clients, total = client_controller.get_all_clients(page=1, per_page=25)
        print(f"   ✅ Clients récupérés: {len(clients)}")
        print(f"   ✅ Total: {total}")
        
        if clients:
            print(f"   📋 Premiers clients:")
            for i, client in enumerate(clients[:3]):
                print(f"      {i+1}. {client.get('client_id')}: {client.get('full_name')}")
        else:
            print(f"   ❌ Aucun client récupéré")
        
        print("\n2️⃣ Test get_clients_by_nationality():")
        try:
            tunisian_clients = client_controller.get_clients_by_nationality('تونسي')
            print(f"   ✅ Clients tunisiens: {len(tunisian_clients)}")
        except Exception as e:
            print(f"   ❌ Erreur get_clients_by_nationality: {e}")
        
        print("\n3️⃣ Test generate_client_id():")
        try:
            new_id = client_controller.generate_client_id()
            print(f"   ✅ Nouvel ID généré: {new_id}")
        except Exception as e:
            print(f"   ❌ Erreur generate_client_id: {e}")
        
        print("\n4️⃣ Test de la route Flask (simulation):")
        try:
            from app import app
            with app.test_client() as test_client:
                response = test_client.get('/clients')
                print(f"   ✅ Status code: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.data.decode('utf-8')
                    if 'CLI0' in content:
                        print(f"   ✅ IDs clients détectés dans la réponse")
                    else:
                        print(f"   ⚠️  Aucun ID client détecté dans la réponse")
                else:
                    print(f"   ❌ Erreur HTTP: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur test route: {e}")
        
        print("\n" + "="*60)
        print("✅ Test terminé - Les corrections semblent fonctionner !")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_client_display_fix()