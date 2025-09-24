#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.cache_manager import cache_manager
from src.controllers.client_controller import ClientController
from src.database.database_manager import DatabaseManager

# Créer le contrôleur avec le db_manager
db_manager = DatabaseManager()
client_controller = ClientController(db_manager)

# Invalider le cache
cache_manager.delete('dashboard_stats')
print("Cache invalidé")

# Appeler directement la méthode get_all_clients du contrôleur
clients, total = client_controller.get_all_clients(1, 10000)
print(f"\nRésultat direct du contrôleur:")
print(f"  Total retourné: {total}")
print(f"  Nombre de clients: {len(clients)}")

# Calculer les statuts
status_counts = {}
for client in clients:
    status = client.get('visa_status', '')
    status_counts[status] = status_counts.get(status, 0) + 1

print(f"\nRépartition par statut:")
total_from_statuses = 0
for status, count in sorted(status_counts.items()):
    print(f"  {status}: {count}")
    total_from_statuses += count

print(f"\nTotal calculé depuis les statuts: {total_from_statuses}")
print(f"Différence: {total - total_from_statuses}")

# Vérifier les statuts vides ou NULL
empty_status = [c for c in clients if not c.get('visa_status') or c.get('visa_status') == '']
print(f"\nClients avec statut vide: {len(empty_status)}")

if empty_status:
    print("Exemples de clients avec statut vide:")
    for i, client in enumerate(empty_status[:5]):
        print(f"  {i+1}. ID: {client.get('client_id')}, Nom: {client.get('full_name')}")