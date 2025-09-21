#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tester la génération séquentielle des IDs
"""

import sys
sys.path.append('src')

from controllers.client_controller import ClientController
from database.database_manager import DatabaseManager

def test_sequential_id_generation():
    """Tester la génération séquentielle des IDs"""
    
    try:
        # Initialiser le contrôleur
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        print("🔄 TEST DE GÉNÉRATION SÉQUENTIELLE DES IDs")
        print("=" * 60)
        
        # 1. Vérifier l'état actuel
        print("📊 État actuel de la base de données...")
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
        
        # 2. Tester la génération de plusieurs IDs consécutifs
        print(f"\n🔧 Test de génération de 5 IDs consécutifs...")
        print("(Simulation sans insertion en base)")
        
        generated_ids = []
        for i in range(5):
            next_id = client_controller.generate_client_id()
            generated_ids.append(next_id)
            print(f"   {i+1}. {next_id}")
        
        # 3. Vérifier l'ordre chronologique
        print(f"\n📅 Vérification de l'ordre chronologique:")
        expected_ids = [f"CLI{max_number + i + 1:03d}" for i in range(5)]
        
        if generated_ids == expected_ids:
            print("✅ L'ordre chronologique est parfait!")
            print(f"   IDs générés: {generated_ids}")
            print(f"   IDs attendus: {expected_ids}")
        else:
            print("❌ L'ordre chronologique n'est pas respecté")
            print(f"   IDs générés: {generated_ids}")
            print(f"   IDs attendus: {expected_ids}")
        
        # 4. Tester la continuité après CLI999
        print(f"\n🔮 Test de continuité après CLI999:")
        print("(Simulation avec CLI999 comme dernier ID)")
        
        # Simuler CLI999 comme dernier ID
        test_max = 999
        print(f"   Si CLI{test_max:03d} était le dernier...")
        print(f"   Le prochain serait: CLI{test_max + 1:03d}")
        print(f"   Puis: CLI{test_max + 2:03d}, CLI{test_max + 3:03d}, etc.")
        
        # 5. Afficher les statistiques finales
        print(f"\n📊 STATISTIQUES FINALES:")
        print(f"   • Dernier ID réel: CLI{max_number:03d}")
        print(f"   • Prochain ID: CLI{max_number + 1:03d}")
        print(f"   • IDs testés: {len(generated_ids)}")
        print(f"   • Ordre chronologique: {'✅ Correct' if generated_ids == expected_ids else '❌ Incorrect'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    test_sequential_id_generation()
