import sqlite3
from datetime import datetime

print("=" * 60)
print("    SUPPRESSION DU CLIENT محمد_عبدالهادي_2708")
print("=" * 60)

# Connexion à la base de données
conn = sqlite3.connect('visa_system.db')
cursor = conn.cursor()

# 1. Vérifier l'existence du client
print("\n1. VÉRIFICATION DE L'EXISTENCE DU CLIENT")
print("-" * 50)

client_id = 'محمد_عبدالهادي_2708'
cursor.execute('SELECT * FROM clients WHERE client_id = ?', (client_id,))
client = cursor.fetchone()

if client:
    print(f"✅ Client trouvé: {client_id}")
    print(f"   Nom: {client[1] if len(client) > 1 else 'N/A'}")
    print(f"   Nationalité: {client[4] if len(client) > 4 else 'N/A'}")
else:
    print(f"❌ Client non trouvé: {client_id}")
    conn.close()
    exit()

# 2. Compter les clients avant suppression
cursor.execute('SELECT COUNT(*) FROM clients')
total_before = cursor.fetchone()[0]
print(f"\nNombre total de clients avant suppression: {total_before}")

# 3. Supprimer le client
print("\n2. SUPPRESSION DU CLIENT")
print("-" * 50)

cursor.execute('DELETE FROM clients WHERE client_id = ?', (client_id,))
rows_affected = cursor.rowcount

if rows_affected > 0:
    print(f"✅ Client supprimé avec succès: {client_id}")
    print(f"   Nombre de lignes affectées: {rows_affected}")
else:
    print(f"❌ Échec de la suppression: {client_id}")

# 4. Confirmer la suppression
print("\n3. CONFIRMATION DE LA SUPPRESSION")
print("-" * 50)

cursor.execute('SELECT * FROM clients WHERE client_id = ?', (client_id,))
client_check = cursor.fetchone()

if client_check is None:
    print(f"✅ Confirmation: Le client {client_id} a été supprimé")
else:
    print(f"❌ Erreur: Le client {client_id} existe encore")

# 5. Compter les clients après suppression
cursor.execute('SELECT COUNT(*) FROM clients')
total_after = cursor.fetchone()[0]
print(f"\nNombre total de clients après suppression: {total_after}")
print(f"Différence: {total_before - total_after} client(s) supprimé(s)")

# 6. Vérifier les clients restants avec format CLI
print("\n4. VÉRIFICATION DES CLIENTS CLI STANDARD")
print("-" * 50)

cursor.execute("SELECT COUNT(*) FROM clients WHERE client_id LIKE 'CLI%'")
cli_clients = cursor.fetchone()[0]
print(f"Clients avec format CLI standard: {cli_clients}")

# Vérifier s'il reste des clients avec format non-standard
cursor.execute("SELECT client_id, full_name FROM clients WHERE client_id NOT LIKE 'CLI%' LIMIT 5")
non_standard = cursor.fetchall()

if non_standard:
    print(f"\n⚠️  Clients avec format non-standard restants: {len(non_standard)}")
    for client in non_standard:
        print(f"   - {client[0]}: {client[1]}")
else:
    print("\n✅ Tous les clients ont maintenant le format CLI standard")

# 7. Afficher les derniers clients CLI pour vérification
print("\n5. DERNIERS CLIENTS CLI (VÉRIFICATION)")
print("-" * 50)

cursor.execute("SELECT client_id, full_name FROM clients WHERE client_id LIKE 'CLI%' ORDER BY client_id DESC LIMIT 5")
last_clients = cursor.fetchall()

for client in last_clients:
    print(f"{client[0]}: {client[1]}")

# Sauvegarder les changements
conn.commit()
conn.close()

print("\n" + "=" * 60)
print("    SUPPRESSION TERMINÉE AVEC SUCCÈS")
print("=" * 60)