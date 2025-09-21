#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Déboguer la génération des IDs
"""

import sqlite3

def debug_id_generation():
    """Déboguer la génération des IDs"""
    
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    
    try:
        print("🔍 DÉBOGAGE DE LA GÉNÉRATION DES IDs")
        print("=" * 50)
        
        # 1. Vérifier tous les IDs CLI existants
        cursor.execute("SELECT client_id FROM clients WHERE client_id LIKE 'CLI%' ORDER BY client_id DESC LIMIT 10")
        rows = cursor.fetchall()
        
        print("📊 DERNIERS IDs CLI EXISTANTS:")
        for i, row in enumerate(rows, 1):
            print(f"   {i}. {row[0]}")
        
        # 2. Extraire les numéros et trouver le maximum
        cli_numbers = []
        for row in rows:
            client_id = row[0]
            if client_id.startswith('CLI'):
                try:
                    number = int(client_id[3:])  # Extraire le numéro après "CLI"
                    cli_numbers.append(number)
                except ValueError:
                    print(f"   ⚠️  ID invalide: {client_id}")
        
        if cli_numbers:
            max_number = max(cli_numbers)
            print(f"\n✅ Numéro maximum trouvé: {max_number}")
            print(f"✅ Dernier ID: CLI{max_number:03d}")
            print(f"✅ Prochain ID devrait être: CLI{max_number + 1:03d}")
        else:
            print("❌ Aucun numéro CLI valide trouvé")
        
        # 3. Tester la logique de génération
        print(f"\n🔧 TEST DE LA LOGIQUE DE GÉNÉRATION:")
        
        # Simuler la logique actuelle
        existing_numbers = cli_numbers
        if existing_numbers:
            next_number = max(existing_numbers) + 1
        else:
            next_number = 1
        
        print(f"   • Nombres existants: {existing_numbers[:5]}... (total: {len(existing_numbers)})")
        print(f"   • Maximum: {max(existing_numbers) if existing_numbers else 'N/A'}")
        print(f"   • Prochain numéro: {next_number}")
        print(f"   • Prochain ID: CLI{next_number:03d}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    debug_id_generation()
