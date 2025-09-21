#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test direct de la génération d'ID
"""

import sqlite3
import sys
sys.path.append('src')

def test_direct_id_generation():
    """Test direct de la génération d'ID"""
    
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    
    try:
        print("🔍 TEST DIRECT DE GÉNÉRATION D'ID")
        print("=" * 50)
        
        # 1. Récupérer tous les client_id directement de la base
        cursor.execute("SELECT client_id FROM clients")
        all_client_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Total de client_id dans la base: {len(all_client_ids)}")
        
        # 2. Filtrer les IDs CLI
        cli_ids = [cid for cid in all_client_ids if cid.startswith('CLI')]
        print(f"📊 IDs CLI trouvés: {len(cli_ids)}")
        
        # 3. Extraire les numéros
        cli_numbers = []
        for client_id in cli_ids:
            try:
                number = int(client_id[3:])  # Extraire après "CLI"
                cli_numbers.append(number)
            except ValueError:
                print(f"   ⚠️  ID invalide: {client_id}")
        
        print(f"📊 Numéros CLI valides: {len(cli_numbers)}")
        
        if cli_numbers:
            max_number = max(cli_numbers)
            next_number = max_number + 1
            next_id = f"CLI{next_number:03d}"
            
            print(f"✅ Maximum trouvé: {max_number}")
            print(f"✅ Prochain ID: {next_id}")
            
            # 4. Vérifier que cet ID n'existe pas déjà
            if next_id not in all_client_ids:
                print(f"✅ {next_id} est disponible")
            else:
                print(f"❌ {next_id} existe déjà!")
                
                # Trouver le prochain ID disponible
                test_number = next_number
                while f"CLI{test_number:03d}" in all_client_ids:
                    test_number += 1
                print(f"✅ Prochain ID disponible: CLI{test_number:03d}")
        else:
            print("❌ Aucun numéro CLI valide trouvé")
        
        # 5. Afficher les 10 derniers IDs
        print(f"\n📋 10 DERNIERS IDs CLI:")
        cli_ids_sorted = sorted(cli_ids, key=lambda x: int(x[3:]) if x[3:].isdigit() else 0, reverse=True)
        for i, cid in enumerate(cli_ids_sorted[:10], 1):
            print(f"   {i:2d}. {cid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    test_direct_id_generation()
