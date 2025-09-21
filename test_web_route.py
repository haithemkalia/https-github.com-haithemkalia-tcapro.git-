#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la route web /clients pour vérifier l'affichage
"""

import requests
import json
from time import sleep

def test_web_clients_route():
    """Tester la route /clients de l'interface web"""
    print("🌐 Test de la route web /clients...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test de la page principale
        print("\n📄 Test de la page principale...")
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Page principale accessible")
        else:
            print(f"   ❌ Erreur page principale: {response.status_code}")
            return False
        
        # Test de la page clients
        print("\n👥 Test de la page clients...")
        clients_url = f"{base_url}/clients"
        response = requests.get(clients_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Page clients accessible")
            
            # Vérifier le contenu HTML
            html_content = response.text
            
            # Chercher des indicateurs de clients dans le HTML
            if "CLI" in html_content:  # Les IDs clients commencent par CLI
                print("   ✅ Des clients sont présents dans le HTML")
                
                # Compter approximativement les clients
                cli_count = html_content.count("CLI")
                print(f"   📊 Approximativement {cli_count} références de clients trouvées")
                
                # Vérifier la présence de noms arabes
                if "محمد" in html_content or "عبد" in html_content:
                    print("   ✅ Noms arabes détectés dans le HTML")
                else:
                    print("   ⚠️  Aucun nom arabe détecté")
                
                return True
            else:
                print("   ❌ Aucun client détecté dans le HTML")
                print("   📝 Extrait du HTML:")
                print(html_content[:500] + "..." if len(html_content) > 500 else html_content)
                return False
        else:
            print(f"   ❌ Erreur page clients: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Impossible de se connecter au serveur")
        print("   💡 Vérifiez que le serveur Flask est en cours d'exécution")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_api_clients_endpoint():
    """Tester l'endpoint API pour les clients"""
    print("\n🔌 Test de l'API clients...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test de l'endpoint API (si disponible)
        api_url = f"{base_url}/api/clients"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ API clients accessible")
            
            try:
                data = response.json()
                if isinstance(data, dict) and 'clients' in data:
                    clients = data['clients']
                    total = data.get('total', 0)
                    print(f"   📊 API retourne {len(clients)} clients, total: {total}")
                    
                    if clients:
                        first_client = clients[0]
                        print(f"   👤 Premier client: {first_client.get('full_name', 'N/A')}")
                        print(f"   🆔 ID: {first_client.get('client_id', 'N/A')}")
                    
                    return len(clients) > 0
                else:
                    print(f"   ⚠️  Format de réponse inattendu: {type(data)}")
                    return False
            except json.JSONDecodeError:
                print("   ⚠️  Réponse non-JSON")
                return False
        elif response.status_code == 404:
            print("   ℹ️  Endpoint API non trouvé (normal si pas d'API REST)")
            return True  # Pas d'erreur si pas d'API
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Impossible de se connecter au serveur pour l'API")
        return False
    except Exception as e:
        print(f"   ❌ Erreur API: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚨 TEST DE L'INTERFACE WEB APRÈS CORRECTION")
    print("=" * 60)
    
    # Attendre un peu que le serveur soit prêt
    print("⏳ Attente du démarrage du serveur...")
    sleep(2)
    
    success1 = test_web_clients_route()
    success2 = test_api_clients_endpoint()
    
    print("\n" + "=" * 60)
    if success1:
        print("✅ INTERFACE WEB FONCTIONNE CORRECTEMENT!")
        print("🎉 Les clients s'affichent maintenant dans l'interface")
        print("\n🌐 Accédez à: http://localhost:5000/clients")
    else:
        print("❌ PROBLÈME PERSISTANT AVEC L'INTERFACE WEB")
        print("💡 Vérifiez les logs du serveur Flask")
    
    print("\n📊 Résumé:")
    print(f"   - Interface web: {'✅ OK' if success1 else '❌ Erreur'}")
    print(f"   - API (optionnel): {'✅ OK' if success2 else '⚠️  Non disponible'}")

if __name__ == "__main__":
    main()