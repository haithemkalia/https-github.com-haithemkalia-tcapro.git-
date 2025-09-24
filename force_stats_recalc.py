#!/usr/bin/env python3
from src.utils.cache_manager import cache_manager
import requests

# Invalider le cache des statistiques
cache_manager.delete('dashboard_stats')
print('Cache des statistiques invalidé')

# Forcer le recalcul en appelant l'API
response = requests.get('http://localhost:5000/api/stats')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Total clients après recalcul: {data.get("total_clients", "non trouvé")}')
else:
    print(f'Erreur: {response.text}')