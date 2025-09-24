#!/usr/bin/env python3
import sqlite3
import os

# Connexion à la base de données
db_path = 'visa_system.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Compter le nombre total de clients
cursor.execute("SELECT COUNT(*) FROM clients")
total_count = cursor.fetchone()[0]
print(f"Nombre total de clients dans la base: {total_count}")

# Récupérer les IDs pour vérifier les doublons
cursor.execute("SELECT id FROM clients ORDER BY id")
ids = [row[0] for row in cursor.fetchall()]
print(f"Nombre d'IDs récupérés: {len(ids)}")

# Vérifier les doublons
unique_ids = set(ids)
print(f"Nombre d'IDs uniques: {len(unique_ids)}")

if len(ids) != len(unique_ids):
    print("⚠️ Des doublons ont été trouvés!")
    from collections import Counter
    id_counts = Counter(ids)
    duplicates = {id_: count for id_, count in id_counts.items() if count > 1}
    print(f"IDs en double: {duplicates}")
else:
    print("✅ Aucun doublon trouvé")

# Vérifier la plage d'IDs
if ids:
    min_id = min(ids)
    max_id = max(ids)
    print(f"Plage d'IDs: {min_id} à {max_id}")
    print(f"Nombre attendu d'IDs: {max_id - min_id + 1}")

# Vérifier s'il y a des IDs NULL ou vides
cursor.execute("SELECT COUNT(*) FROM clients WHERE id IS NULL OR id = ''")
null_ids = cursor.fetchone()[0]
print(f"Nombre d'IDs NULL ou vides: {null_ids}")

conn.close()