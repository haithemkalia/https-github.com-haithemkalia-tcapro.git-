#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test d'ajout de client avec génération automatique d'ID
"""

import sys
sys.path.append('src')

from controllers.client_controller import ClientController
from database.database_manager import DatabaseManager

def test_add_client():
    """Test d'ajout de client"""
    
    try:
        # Initialiser le contrôleur
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        print("🧪 TEST D'AJOUT DE CLIENT")
        print("=" * 50)
        
        # 1. Vérifier l'état actuel
        print("📊 État actuel...")
        all_clients, total = client_controller.get_all_clients(page=1, per_page=1000)
        
        # Trouver le dernier ID CLI
        cli_numbers = []
        for client in all_clients:
            client_id = client.get('client_id', '')
            if client_id.startswith('CLI'):
                try:
                    number = int(client_id[3:])
                    cli_numbers.append(number)
                except ValueError:
                    continue
        
        if cli_numbers:
            max_number = max(cli_numbers)
            print(f"✅ Dernier ID existant: CLI{max_number:03d}")
            print(f"📊 Total clients: {total}")
        else:
            print("❌ Aucun ID CLI trouvé")
            return False
        
        # 2. Créer un client de test
        print(f"\n🔧 Test d'ajout de client...")
        
        test_client_data = {
            'full_name': 'Test Client Auto ID',
            'whatsapp_number': '123456789',
            'application_date': '01/01/2025',
            'nationality': 'Test',
            'visa_status': 'التقديم',
            'notes': 'Client de test pour vérifier la génération automatique d\'ID'
        }
        
        # Ajouter le client (sans client_id - génération automatique)
        try:
            new_client_id = client_controller.add_client(test_client_data)
            print(f"✅ Client ajouté avec l'ID: {new_client_id}")
            
            # Vérifier que l'ID est correct
            expected_id = f"CLI{max_number + 1:03d}"
            if new_client_id == expected_id:
                print(f"✅ ID correct! Attendu: {expected_id}, Obtenu: {new_client_id}")
            else:
                print(f"❌ ID incorrect! Attendu: {expected_id}, Obtenu: {new_client_id}")
            
            # Vérifier que le client existe dans la base
            added_client = client_controller.get_client_by_id(new_client_id)
            if added_client:
                print(f"✅ Client trouvé dans la base: {added_client.get('full_name')}")
            else:
                print(f"❌ Client non trouvé dans la base")
            
            # Supprimer le client de test
            success = client_controller.delete_client(new_client_id)
            if success:
                print(f"✅ Client de test supprimé")
            else:
                print(f"⚠️  Client de test non supprimé (à nettoyer manuellement)")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout du client: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    test_add_client()
