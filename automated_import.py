
import requests
import json

def import_to_render():
    # Ce script peut être utilisé pour importer automatiquement
    # les données vers votre instance Render
    
    # Charger le package de données
    with open('render_deployment_package.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    clients = data['clients']
    total = len(clients)
    
    print(f"Import de {total} clients...")
    
    # URL de votre instance Render (à adapter)
    base_url = "https://votre-instance-render.com"
    
    # Importer les clients un par un ou par lots
    # (Code à adapter selon l'API de votre instance)
    
    print("Import terminé!")

if __name__ == "__main__":
    import_to_render()
