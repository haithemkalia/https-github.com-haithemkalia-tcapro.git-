#!/usr/bin/env python3
import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('visa_system.db')
cursor = conn.cursor()

# Voir la structure de la table
cursor.execute("PRAGMA table_info(clients)")
columns = cursor.fetchall()
print("Structure de la table clients:")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

print("\n" + "="*50)

# Compter avec client_id
cursor.execute("SELECT COUNT(*) FROM clients")
total_with_client_id = cursor.fetchone()[0]
print(f"Nombre total avec client_id: {total_with_client_id}")

# Vérifier s'il y a des client_id NULL
cursor.execute("SELECT COUNT(*) FROM clients WHERE client_id IS NULL OR client_id = ''")
null_client_ids = cursor.fetchone()[0]
print(f"Nombre de client_id NULL ou vides: {null_client_ids}")

# Récupérer tous les client_id
cursor.execute("SELECT client_id FROM clients ORDER BY client_id")
client_ids = [row[0] for row in cursor.fetchall()]
print(f"Nombre de client_id récupérés: {len(client_ids)}")

# Vérifier les doublons sur client_id
unique_client_ids = set(client_ids)
print(f"Nombre de client_id uniques: {len(unique_client_ids)}")

if len(client_ids) != len(unique_client_ids):
    print("⚠️ Des doublons ont été trouvés sur client_id!")
    from collections import Counter
    id_counts = Counter(client_ids)
    duplicates = {id_: count for id_, count in id_counts.items() if count > 1}
    print(f"client_id en double: {duplicates}")
else:
    print("✅ Aucun doublon trouvé sur client_id")

# Vérifier s'il y a une colonne id séparée
cursor.execute("SELECT COUNT(*) FROM clients WHERE id IS NOT NULL")
has_id_column = cursor.fetchone()[0]
if has_id_column > 0:
    print(f"\n⚠️ Il y a {has_id_column} lignes avec une valeur dans la colonne 'id'")

conn.close()