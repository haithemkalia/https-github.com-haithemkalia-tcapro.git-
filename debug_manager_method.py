#!/usr/bin/env python3
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.database_manager import DatabaseManager

db = DatabaseManager()

# Tester la méthode get_all_clients
clients, total = db.get_all_clients(1, 10000)

print(f"Méthode get_all_clients a retourné:")
print(f"  - Total: {total}")
print(f"  - Nombre de clients dans la liste: {len(clients)}")

# Vérifier s'il y a des doublons
client_ids = []
for client in clients:
    client_id = client['client_id']
    client_ids.append(client_id)

unique_client_ids = set(client_ids)
print(f"  - Nombre de client_id uniques: {len(unique_client_ids)}")
print(f"  - Nombre total de client_id: {len(client_ids)}")

if len(client_ids) != len(unique_client_ids):
    print("⚠️ Des doublons ont été trouvés!")
    from collections import Counter
    id_counts = Counter(client_ids)
    duplicates = {id_: count for id_, count in id_counts.items() if count > 1}
    print(f"client_id en double: {duplicates}")
else:
    print("✅ Aucun doublon trouvé")

# Vérifier la plage de client_id
if client_ids:
    # Trier comme nombres puisque les IDs sont numériques
    numeric_ids = [int(id_) for id_ in client_ids if id_.isdigit()]
    if numeric_ids:
        min_id = min(numeric_ids)
        max_id = max(numeric_ids)
        print(f"  - Plage de client_id: {min_id} à {max_id}")
        print(f"  - Nombre attendu: {max_id - min_id + 1}")

# Comparer avec le comptage direct
count_result = db.execute_query("SELECT COUNT(*) as count FROM clients")
if count_result:
    direct_count = count_result[0]['count']
    print(f"\nComptage direct depuis la base: {direct_count}")

print(f"\nDifférence: {total - 975} (devrait être 0)")