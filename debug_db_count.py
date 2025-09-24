#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import DatabaseManager

db = DatabaseManager()

# Récupérer tous les clients avec la même méthode que l'API
clients, total = db.get_all_clients(1, 10000)

print(f"Nombre total de clients via db_manager.get_all_clients(): {total}")
print(f"Nombre de clients dans la liste: {len(clients)}")

# Vérifier s'il y a des doublons
ids = [client['id'] for client in clients]
unique_ids = set(ids)
print(f"Nombre d'IDs uniques: {len(unique_ids)}")
print(f"Nombre total d'IDs: {len(ids)}")

if len(ids) != len(unique_ids):
    print("⚠️ Des doublons ont été trouvés!")
    duplicates = {}
    for client_id in ids:
        duplicates[client_id] = duplicates.get(client_id, 0) + 1
    
    for client_id, count in duplicates.items():
        if count > 1:
            print(f"ID {client_id} apparaît {count} fois")
else:
    print("✅ Aucun doublon trouvé")

# Vérifier la plage d'IDs
if clients:
    min_id = min(ids)
    max_id = max(ids)
    print(f"Plage d'IDs: {min_id} à {max_id}")
    print(f"Nombre attendu d'IDs: {max_id - min_id + 1}")

# Compter directement dans la base de données
count_result = db.execute_query("SELECT COUNT(*) as count FROM clients")
if count_result:
    direct_count = count_result[0]['count']
    print(f"Nombre direct depuis la base de données: {direct_count}")