#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour trouver où sont réellement stockées les données
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.database_manager import DatabaseManager
from controllers.client_controller import ClientController
from cache_manager import cache
import json

def debug_data_sources():
    """Debugger toutes les sources de données possibles"""
    print("🔍 RECHERCHE DES DONNÉES CLIENTS")
    print("=" * 50)
    
    # 1. Vérifier la base de données SQLite
    print("\n📁 1. BASE DE DONNÉES SQLITE")
    print("-" * 30)
    db_manager = DatabaseManager()
    
    try:
        # Compter les clients dans la base de données
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients")
            count = cursor.fetchone()[0]
            print(f"   ✅ Clients dans SQLite: {count}")
            
            if count > 0:
                cursor.execute("SELECT client_id, full_name, visa_status FROM clients LIMIT 5")
                clients = cursor.fetchall()
                print("   📋 Exemples de clients:")
                for client in clients:
                    print(f"      - {client[0]}: {client[1]} ({client[2]})")
    except Exception as e:
        print(f"   ❌ Erreur SQLite: {e}")
    
    # 2. Vérifier le contrôleur client
    print("\n🎮 2. CONTRÔLEUR CLIENT")
    print("-" * 30)
    client_controller = ClientController(db_manager)
    
    try:
        # Tester get_all_clients
        clients, total = client_controller.get_all_clients(page=1, per_page=10)
        print(f"   ✅ Clients via controller: {total}")
        print(f"   ✅ Clients récupérés: {len(clients)}")
        
        if clients:
            print("   📋 Premiers clients:")
            for i, client in enumerate(clients[:3]):
                if isinstance(client, dict):
                    print(f"      - {client.get('client_id', 'N/A')}: {client.get('full_name', 'N/A')}")
                else:
                    print(f"      - Client {i}: {type(client)}")
    except Exception as e:
        print(f"   ❌ Erreur controller: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Vérifier le cache
    print("\n💾 3. CACHE")
    print("-" * 30)
    try:
        # Vérifier le cache directement
        cached_clients = cache.get('all_clients')
        if cached_clients:
            print(f"   ✅ Clients dans cache: {len(cached_clients)}")
            print("   📋 Exemples:")
            for client in cached_clients[:3]:
                if isinstance(client, dict):
                    print(f"      - {client.get('client_id', 'N/A')}: {client.get('full_name', 'N/A')}")
        else:
            print("   ❌ Aucun client dans le cache")
            
        # Lister toutes les clés de cache
        print("   🔑 Clés de cache disponibles:")
        # Note: SimpleCache n'a pas de méthode pour lister toutes les clés
        # On teste quelques clés courantes
        test_keys = ['all_clients', 'clients_page_1', 'stats', 'recent_clients']
        for key in test_keys:
            value = cache.get(key)
            if value:
                print(f"      - {key}: {len(value) if isinstance(value, list) else 'data'}")
            else:
                print(f"      - {key}: vide")
                
    except Exception as e:
        print(f"   ❌ Erreur cache: {e}")
    
    # 4. Vérifier les fichiers locaux
    print("\n📄 4. FICHIERS LOCAUX")
    print("-" * 30)
    
    # Chercher des fichiers de données
    data_files = []
    for ext in ['*.db', '*.json', '*.csv', '*.xlsx']:
        files = list(Path('.').glob(ext))
        data_files.extend(files)
    
    if data_files:
        print("   📋 Fichiers de données trouvés:")
        for file in data_files:
            size = file.stat().st_size if file.exists() else 0
            print(f"      - {file.name} ({size} bytes)")
    else:
        print("   ❌ Aucun fichier de données trouvé")
    
    # 5. Vérifier si les données sont dans l'application en mémoire
    print("\n🧠 5. APPLICATION EN MÉMOIRE")
    print("-" * 30)
    print("   💡 Pour vérifier les données en mémoire, l'application doit être en cours d'exécution")
    print("   💡 Essayez d'accéder à: http://localhost:5000/test-clients")
    
    # 6. Recommandations
    print("\n💡 RECOMMANDATIONS")
    print("-" * 30)
    print("   1. Si les données sont dans le cache mais pas dans SQLite:")
    print("      → Créer un script pour sauvegarder le cache dans SQLite")
    print("   2. Si les données sont uniquement en mémoire:")
    print("      → Utiliser l'endpoint /export pour les sauvegarder")
    print("   3. Si la base de données est vide:")
    print("      → Importer les données depuis l'ancienne source")

if __name__ == "__main__":
    debug_data_sources()