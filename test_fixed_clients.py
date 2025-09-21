#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du ClientController après correction
"""

import sys
from pathlib import Path

# Ajouter le dossier src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_fixed_client_controller():
    """Tester le ClientController après correction"""
    print("🔧 Test du ClientController corrigé...")
    
    try:
        from database.database_manager import DatabaseManager
        from controllers.client_controller import ClientController
        
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        print(f"✅ ClientController initialisé")
        
        # Test get_all_clients
        print("\n📊 Test get_all_clients()...")
        clients, total = client_controller.get_all_clients(page=1, per_page=10)
        print(f"   Résultat: {len(clients)} clients, total: {total}")
        
        if clients:
            print(f"   Type du premier client: {type(clients[0])}")
            print(f"   Premier client: {clients[0]}")
            
            # Vérifier les clés importantes
            first_client = clients[0]
            if isinstance(first_client, dict):
                print(f"   ✅ Client est un dictionnaire")
                print(f"   ID: {first_client.get('client_id', 'N/A')}")
                print(f"   Nom: {first_client.get('full_name', 'N/A')}")
                print(f"   Statut: {first_client.get('visa_status', 'N/A')}")
            else:
                print(f"   ❌ Client n'est pas un dictionnaire: {type(first_client)}")
        else:
            print(f"   ❌ Aucun client retourné")
        
        # Test avec plus de clients
        print("\n📊 Test avec 50 clients...")
        clients_50, total_50 = client_controller.get_all_clients(page=1, per_page=50)
        print(f"   Résultat: {len(clients_50)} clients, total: {total_50}")
        
        # Test search_clients
        print("\n🔍 Test search_clients()...")
        search_results, search_total = client_controller.search_clients("محمد", page=1, per_page=10)
        print(f"   Résultat recherche 'محمد': {len(search_results)} clients, total: {search_total}")
        
        if search_results:
            print(f"   Premier résultat: {search_results[0].get('full_name', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_interface_simulation():
    """Simuler l'appel depuis l'interface web"""
    print("\n🌐 Simulation de l'interface web...")
    
    try:
        # Simuler ce que fait l'application Flask
        from database.database_manager import DatabaseManager
        from controllers.client_controller import ClientController
        
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        # Simuler la route /clients
        page = 1
        per_page = 25  # Valeur par défaut de la pagination
        
        clients, total = client_controller.get_all_clients(page=page, per_page=per_page)
        
        print(f"   Simulation route /clients:")
        print(f"   - Page: {page}")
        print(f"   - Par page: {per_page}")
        print(f"   - Clients récupérés: {len(clients)}")
        print(f"   - Total: {total}")
        print(f"   - Pages totales: {(total + per_page - 1) // per_page}")
        
        if clients:
            print(f"   ✅ Interface web devrait afficher {len(clients)} clients")
            return True
        else:
            print(f"   ❌ Interface web n'affichera aucun client")
            return False
            
    except Exception as e:
        print(f"❌ Erreur simulation web: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("🚨 TEST DU CLIENTCONTROLLER CORRIGÉ")
    print("=" * 60)
    
    success1 = test_fixed_client_controller()
    success2 = test_web_interface_simulation()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ TOUS LES TESTS RÉUSSIS - Le problème est résolu!")
        print("🎉 Les clients devraient maintenant s'afficher correctement")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ - Problème persistant")
    
    print("\n💡 Redémarrez le serveur Flask pour appliquer les corrections.")

if __name__ == "__main__":
    main()