#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final pour vérifier que le problème est résolu
"""

import requests
import time
from bs4 import BeautifulSoup

def test_final_web_interface():
    """Test final de l'interface web"""
    print("🎯 TEST FINAL DE L'INTERFACE WEB")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    try:
        print("⏳ Attente du serveur...")
        time.sleep(2)
        
        # Test de la page clients
        print("\n🌐 Test de la page /clients...")
        response = requests.get(f"{base_url}/clients", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
        
        print(f"✅ Page accessible (Status: {response.status_code})")
        
        # Parser le HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Vérifier la présence du tableau
        table = soup.find('table', {'id': 'clientsTable'})
        if not table:
            print("❌ Tableau des clients non trouvé")
            return False
        
        print("✅ Tableau des clients trouvé")
        
        # Vérifier le tbody
        tbody = table.find('tbody')
        if not tbody:
            print("❌ Corps du tableau (tbody) non trouvé")
            return False
        
        print("✅ Corps du tableau trouvé")
        
        # Compter les lignes de clients
        rows = tbody.find_all('tr')
        print(f"📊 Nombre de lignes de clients: {len(rows)}")
        
        if len(rows) == 0:
            print("❌ Aucune ligne de client trouvée")
            
            # Vérifier s'il y a un message "لا توجد نتائج"
            no_results = soup.find(text=lambda text: text and "لا توجد نتائج" in text)
            if no_results:
                print("ℹ️  Message 'Aucun résultat' affiché")
            
            return False
        
        print(f"✅ {len(rows)} lignes de clients trouvées!")
        
        # Analyser la première ligne
        first_row = rows[0]
        cells = first_row.find_all('td')
        
        if len(cells) >= 2:
            client_id_cell = cells[0]
            name_cell = cells[1]
            
            client_id = client_id_cell.get_text(strip=True)
            name = name_cell.get_text(strip=True)
            
            print(f"\n👤 Premier client:")
            print(f"   - ID: {client_id}")
            print(f"   - Nom: {name}")
            
            # Vérifier que ce ne sont pas des valeurs vides
            if client_id and name:
                print("✅ Données client valides")
                return True
            else:
                print("❌ Données client vides")
                return False
        else:
            print(f"❌ Structure de ligne incorrecte: {len(cells)} cellules")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("💡 Assurez-vous que le serveur Flask est en cours d'exécution")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pagination_info():
    """Tester les informations de pagination"""
    print("\n📄 Test des informations de pagination...")
    
    try:
        response = requests.get("http://localhost:5000/clients", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Chercher les informations de pagination
        pagination_text = soup.find(text=lambda text: text and "عميل" in text and "عرض" in text)
        
        if pagination_text:
            print(f"✅ Informations de pagination trouvées: {pagination_text.strip()}")
            return True
        else:
            print("❌ Informations de pagination non trouvées")
            return False
            
    except Exception as e:
        print(f"❌ Erreur pagination: {e}")
        return False

def main():
    """Fonction principale"""
    clients_ok = test_final_web_interface()
    pagination_ok = test_pagination_info()
    
    print("\n" + "=" * 60)
    print("🏁 RÉSULTATS FINAUX:")
    print(f"   - Affichage des clients: {'✅ RÉSOLU' if clients_ok else '❌ Problème'}")
    print(f"   - Pagination: {'✅ OK' if pagination_ok else '⚠️  Partiel'}")
    
    if clients_ok:
        print("\n🎉 PROBLÈME RÉSOLU AVEC SUCCÈS!")
        print("✅ Les clients s'affichent maintenant correctement")
        print("🌐 Interface web fonctionnelle")
        print("\n📱 Accédez à: http://localhost:5000/clients")
    else:
        print("\n❌ PROBLÈME PERSISTANT")
        print("🔧 Des investigations supplémentaires sont nécessaires")
    
    return clients_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)