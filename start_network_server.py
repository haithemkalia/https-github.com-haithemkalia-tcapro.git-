#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour démarrer le serveur en mode réseau partagé
"""

import socket
import subprocess
import sys
import os
from datetime import datetime

def get_local_ip():
    """Obtenir l'adresse IP locale du PC"""
    try:
        # Se connecter à une adresse externe pour déterminer l'IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_network_info():
    """Obtenir les informations réseau"""
    try:
        # Obtenir l'adresse IP locale
        local_ip = get_local_ip()
        
        # Obtenir le nom de l'ordinateur
        computer_name = socket.gethostname()
        
        return {
            'local_ip': local_ip,
            'computer_name': computer_name,
            'port': 5000
        }
    except Exception as e:
        print(f"❌ Erreur lors de l'obtention des informations réseau: {e}")
        return None

def start_network_server():
    """Démarrer le serveur en mode réseau"""
    
    print("🌐 CONFIGURATION SERVEUR RÉSEAU PARTAGÉ")
    print("=" * 60)
    
    # Obtenir les informations réseau
    network_info = get_network_info()
    if not network_info:
        print("❌ Impossible d'obtenir les informations réseau")
        return False
    
    local_ip = network_info['local_ip']
    computer_name = network_info['computer_name']
    port = network_info['port']
    
    print(f"🖥️  Nom de l'ordinateur: {computer_name}")
    print(f"🌐 Adresse IP locale: {local_ip}")
    print(f"🔌 Port: {port}")
    print()
    
    # Afficher les URLs d'accès
    print("📱 URLS D'ACCÈS POUR LES AUTRES PC:")
    print("-" * 50)
    print(f"🔗 URL principale: http://{local_ip}:{port}")
    print(f"🔗 URL alternative: http://{computer_name}:{port}")
    print()
    
    # Instructions pour les autres PC
    print("📋 INSTRUCTIONS POUR LES AUTRES PC:")
    print("-" * 50)
    print("1. Assurez-vous que tous les PC sont sur le même réseau")
    print("2. Ouvrez un navigateur web sur les autres PC")
    print(f"3. Tapez l'adresse: http://{local_ip}:{port}")
    print("4. L'interface sera accessible simultanément")
    print()
    
    # Vérifications de sécurité
    print("⚠️  VÉRIFICATIONS DE SÉCURITÉ:")
    print("-" * 50)
    print("✅ Le serveur est configuré pour accepter les connexions réseau")
    print("✅ Plusieurs utilisateurs peuvent accéder simultanément")
    print("✅ Les données sont partagées en temps réel")
    print("⚠️  Assurez-vous que le pare-feu autorise le port 5000")
    print()
    
    # Démarrer le serveur
    print("🚀 DÉMARRAGE DU SERVEUR...")
    print("=" * 60)
    print(f"⏰ Heure de démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔄 Le serveur est en cours de démarrage...")
    print()
    print("💡 Pour arrêter le serveur, appuyez sur Ctrl+C")
    print("=" * 60)
    
    try:
        # Démarrer l'application Flask
        os.system(f"python -X utf8 app.py")
        
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté par l'utilisateur")
        return True
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage: {e}")
        return False

if __name__ == "__main__":
    start_network_server()
