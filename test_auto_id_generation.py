#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tester la génération automatique des IDs après CLI972
"""

import sys
sys.path.append('src')

from controllers.client_controller import ClientController
from database.database_manager import DatabaseManager

def test_auto_id_generation():
    """Tester la génération automatique des IDs"""
    
    try:
        # Initialiser le contrôleur
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        print("🔍 TEST DE GÉNÉRATION AUTOMATIQUE DES IDs")
        print("=" * 60)
        
        # 1. Vérifier le dernier ID existant
        print("📊 Vérification des IDs existants...")
        all_clients, total = client_controller.get_all_clients(page=1, per_page=1000)
        
        # Extraire tous les numéros CLI
        cli_numbers = []
        for client in all_clients:
            client_id = client.get('client_id', '')
            if client_id.startswith('CLI'):
                try:
                    number = int(client_id[3:])  # Extraire le numéro après "CLI"
                    cli_numbers.append(number)
                except ValueError:
                    continue
        
        if cli_numbers:
            max_number = max(cli_numbers)
            print(f"✅ Dernier ID trouvé: CLI{max_number:03d}")
            print(f"📊 Total de clients: {total}")
        else:
            print("❌ Aucun ID CLI trouvé")
            return False
        
        # 2. Tester la génération du prochain ID
        print("\n🔧 Test de génération du prochain ID...")
        next_id = client_controller.generate_client_id()
        print(f"✅ Prochain ID généré: {next_id}")
        
        # 3. Vérifier que c'est bien CLI973
        expected_next = f"CLI{max_number + 1:03d}"
        if next_id == expected_next:
            print(f"✅ Correct! Le prochain ID sera: {expected_next}")
        else:
            print(f"❌ Erreur! Attendu: {expected_next}, Obtenu: {next_id}")
        
        # 4. Tester la génération de plusieurs IDs
        print("\n🔄 Test de génération de plusieurs IDs...")
        test_ids = []
        for i in range(5):
            test_id = client_controller.generate_client_id()
            test_ids.append(test_id)
            print(f"   {i+1}. {test_id}")
        
        # 5. Vérifier l'ordre chronologique
        print("\n📅 Vérification de l'ordre chronologique...")
        sorted_ids = sorted(test_ids)
        if test_ids == sorted_ids:
            print("✅ L'ordre chronologique est respecté")
        else:
            print("❌ L'ordre chronologique n'est pas respecté")
        
        # 6. Afficher les statistiques
        print(f"\n📊 STATISTIQUES:")
        print(f"   • Dernier ID existant: CLI{max_number:03d}")
        print(f"   • Prochain ID généré: {next_id}")
        print(f"   • Total clients: {total}")
        print(f"   • IDs testés: {len(test_ids)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    test_auto_id_generation()
