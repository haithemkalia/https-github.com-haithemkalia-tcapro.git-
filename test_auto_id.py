#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour la génération automatique des IDs clients
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers.client_controller import ClientController
from src.database.database_manager import DatabaseManager

def test_auto_id_generation():
    """Tester la génération automatique des IDs clients"""
    print("🧪 Test de génération automatique des IDs clients")
    print("=" * 60)
    
    # Initialiser le gestionnaire de base de données et le contrôleur
    db_manager = DatabaseManager()
    client_controller = ClientController(db_manager)
    
    # Test 1: Vérifier la génération d'ID sans données existantes
    print("\n📋 Test 1: Génération d'ID de base")
    generated_id = client_controller.generate_client_id()
    print(f"✅ ID généré: {generated_id}")
    
    # Test 2: Vérifier que l'ID commence bien à CLI843
    expected_start = 843
    if generated_id.startswith('CLI'):
        id_number = int(generated_id[3:])
        if id_number >= expected_start:
            print(f"✅ L'ID commence correctement à partir de CLI{expected_start} ou plus")
        else:
            print(f"❌ L'ID devrait commencer à CLI{expected_start}, mais a généré {generated_id}")
    else:
        print(f"❌ L'ID ne commence pas par 'CLI': {generated_id}")
    
    # Test 3: Tester l'ajout d'un client avec ID vide
    print("\n📋 Test 3: Ajout d'un client avec ID vide (génération automatique)")
    test_client_data = {
        'client_id': '',  # ID vide pour tester la génération automatique
        'full_name': 'Test Client Auto ID',
        'whatsapp_number': '+216123456789',
        'nationality': 'تونسي',
        'visa_status': 'التقديم',
        'passport_status': 'موجود'
    }
    
    try:
        # Ajouter le client (l'ID devrait être généré automatiquement)
        result = client_controller.add_client(test_client_data)
        if result:
            print("✅ Client ajouté avec succès avec ID généré automatiquement")
            
            # Récupérer le client pour vérifier l'ID généré
            all_clients = client_controller.get_all_clients()
            test_client = None
            for client in all_clients:
                if client.get('full_name') == 'Test Client Auto ID':
                    test_client = client
                    break
            
            if test_client:
                generated_client_id = test_client.get('client_id')
                print(f"✅ ID du client ajouté: {generated_client_id}")
                
                # Nettoyer - supprimer le client de test
                client_controller.delete_client(generated_client_id)
                print(f"🧹 Client de test supprimé: {generated_client_id}")
            else:
                print("❌ Impossible de trouver le client de test")
        else:
            print("❌ Échec de l'ajout du client")
            
    except Exception as e:
        print(f"❌ Erreur lors du test d'ajout: {e}")
    
    # Test 4: Vérifier la séquence d'IDs
    print("\n📋 Test 4: Vérification de la séquence d'IDs")
    try:
        # Générer plusieurs IDs pour vérifier la séquence
        ids = []
        for i in range(3):
            test_data = {
                'client_id': '',
                'full_name': f'Test Sequence {i+1}',
                'nationality': 'ليبي',
                'visa_status': 'التقديم',
                'passport_status': 'موجود'
            }
            
            result = client_controller.add_client(test_data)
            if result:
                # Trouver le client ajouté
                all_clients = client_controller.get_all_clients()
                for client in all_clients:
                    if client.get('full_name') == f'Test Sequence {i+1}':
                        ids.append(client.get('client_id'))
                        break
        
        print(f"✅ IDs générés en séquence: {ids}")
        
        # Vérifier que les IDs sont consécutifs
        if len(ids) == 3:
            numbers = [int(id_str[3:]) for id_str in ids]
            if numbers[1] == numbers[0] + 1 and numbers[2] == numbers[1] + 1:
                print("✅ Les IDs sont bien consécutifs")
            else:
                print(f"❌ Les IDs ne sont pas consécutifs: {numbers}")
        
        # Nettoyer les clients de test
        for client_id in ids:
            if client_id:
                client_controller.delete_client(client_id)
                print(f"🧹 Client de test supprimé: {client_id}")
                
    except Exception as e:
        print(f"❌ Erreur lors du test de séquence: {e}")
    
    print("\n🎯 Test de génération automatique d'ID terminé!")
    print("=" * 60)

if __name__ == '__main__':
    test_auto_id_generation()