#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test de l'API clients"""

import requests

def test_clients_api():
    try:
        response = requests.get('http://localhost:5000/clients')
        print(f'Status code: {response.status_code}')
        print(f'Nombre de clients dans la réponse: {response.text.count("<tr>")}')
        
        if response.status_code == 200:
            # Chercher les noms de clients dans la réponse
            if 'سالم علي' in response.text:
                print("✅ Le premier client (سالم علي) est bien affiché")
            else:
                print("❌ Le premier client n'est pas affiché")
                
            # Vérifier s'il y a des liens WhatsApp
            if 'https://wa.me/' in response.text:
                print("✅ Des liens WhatsApp sont présents")
            else:
                print("❌ Aucun lien WhatsApp trouvé")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    test_clients_api()