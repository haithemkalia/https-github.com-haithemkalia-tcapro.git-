#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour la saisie manuelle d'IDs clients
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'src'))

from src.database.database_manager import DatabaseManager
from src.controllers.client_controller import ClientController

def test_manual_id_creation():
    """Tester la création de clients avec saisie manuelle d'ID"""
    
    print("🧪 Test de la saisie manuelle d'IDs clients...\n")
    
    try:
        # Initialiser le gestionnaire de base de données
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        # Vérifier l'état actuel de la base
        all_clients = client_controller.get_all_clients()
        print(f"📊 Nombre total de clients actuels : {len(all_clients)}")
        
        # Trouver les derniers IDs CLI
        cli_clients = [c for c in all_clients if c.get('client_id', '').startswith('CLI')]
        cli_clients.sort(key=lambda x: x.get('client_id', ''))
        
        if cli_clients:
            last_cli = cli_clients[-1]['client_id']
            print(f"🔢 Dernier ID CLI : {last_cli}")
        
        print("\n" + "="*50)
        print("🧪 TEST 1: Saisie manuelle d'ID CLI843")
        print("="*50)
        
        # Test 1: Créer un client avec ID CLI843
        test_client_1 = {
            'client_id': 'CLI843',
            'full_name': 'محمد عبدالهادي',
            'whatsapp_number': '21698765432',
            'nationality': 'تونسي',
            'passport_number': 'H979093',
            'passport_status': 'غير موجود',
            'application_date': '2025-09-15',
            'visa_status': 'التقديم',
            'responsible_employee': 'سفيان',
            'processed_by': 'هيثم'
        }
        
        try:
            result_1 = client_controller.add_client(test_client_1)
            if result_1:
                print(f"✅ Client créé avec succès - ID: CLI843")
                
                # Vérifier que le client existe
                created_client = client_controller.get_client_by_id('CLI843')
                if created_client:
                    print(f"✅ Vérification: Client trouvé - {created_client['full_name']}")
                else:
                    print("❌ Erreur: Client non trouvé après création")
            else:
                print("❌ Échec de la création du client")
                
        except Exception as e:
            print(f"❌ Erreur lors de la création: {str(e)}")
        
        print("\n" + "="*50)
        print("🧪 TEST 2: Saisie manuelle d'ID personnalisé")
        print("="*50)
        
        # Test 2: Créer un client avec ID personnalisé
        test_client_2 = {
            'client_id': 'TEST001',
            'full_name': 'أحمد محمد',
            'whatsapp_number': '21612345678',
            'nationality': 'ليبي',
            'passport_number': 'L123456',
            'passport_status': 'موجود',
            'application_date': '2025-01-15',
            'visa_status': 'قيد المراجعة',
            'responsible_employee': 'محمد',
            'processed_by': 'أحمد'
        }
        
        try:
            result_2 = client_controller.add_client(test_client_2)
            if result_2:
                print(f"✅ Client créé avec succès - ID: TEST001")
                
                # Vérifier que le client existe
                created_client = client_controller.get_client_by_id('TEST001')
                if created_client:
                    print(f"✅ Vérification: Client trouvé - {created_client['full_name']}")
                else:
                    print("❌ Erreur: Client non trouvé après création")
            else:
                print("❌ Échec de la création du client")
                
        except Exception as e:
            print(f"❌ Erreur lors de la création: {str(e)}")
        
        print("\n" + "="*50)
        print("🧪 TEST 3: Test de doublon d'ID")
        print("="*50)
        
        # Test 3: Tenter de créer un client avec un ID existant
        test_client_3 = {
            'client_id': 'CLI843',  # ID déjà utilisé
            'full_name': 'فاطمة أحمد',
            'whatsapp_number': '21687654321',
            'nationality': 'تونسي'
        }
        
        try:
            result_3 = client_controller.add_client(test_client_3)
            print("❌ Erreur: Le doublon d'ID n'a pas été détecté !")
        except ValueError as e:
            if "existe déjà" in str(e):
                print("✅ Validation des doublons fonctionne correctement")
                print(f"   Message d'erreur: {str(e)}")
            else:
                print(f"❌ Erreur inattendue: {str(e)}")
        except Exception as e:
            print(f"❌ Erreur inattendue: {str(e)}")
        
        print("\n" + "="*50)
        print("🧪 TEST 4: Test d'ID vide")
        print("="*50)
        
        # Test 4: Tenter de créer un client sans ID
        test_client_4 = {
            'client_id': '',  # ID vide
            'full_name': 'سارة محمد',
            'whatsapp_number': '21698765432',
            'nationality': 'تونسي'
        }
        
        try:
            result_4 = client_controller.add_client(test_client_4)
            print("❌ Erreur: L'ID vide n'a pas été détecté !")
        except ValueError as e:
            if "obligatoire" in str(e):
                print("✅ Validation d'ID obligatoire fonctionne correctement")
                print(f"   Message d'erreur: {str(e)}")
            else:
                print(f"❌ Erreur inattendue: {str(e)}")
        except Exception as e:
            print(f"❌ Erreur inattendue: {str(e)}")
        
        # État final
        print("\n" + "="*50)
        print("📊 ÉTAT FINAL DE LA BASE DE DONNÉES")
        print("="*50)
        
        final_clients = client_controller.get_all_clients()
        print(f"Nombre total de clients : {len(final_clients)}")
        
        # Afficher les nouveaux clients créés
        new_clients = [c for c in final_clients if c.get('client_id') in ['CLI843', 'TEST001']]
        if new_clients:
            print("\n🆕 Nouveaux clients créés :")
            for client in new_clients:
                print(f"   - {client['client_id']}: {client['full_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        return False

def cleanup_test_clients():
    """Nettoyer les clients de test créés"""
    
    print("\n🧹 Nettoyage des clients de test...")
    
    try:
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        test_ids = ['CLI843', 'TEST001']
        
        for test_id in test_ids:
            try:
                client = client_controller.get_client_by_id(test_id)
                if client:
                    success = client_controller.delete_client(test_id)
                    if success:
                        print(f"✅ Client {test_id} supprimé")
                    else:
                        print(f"❌ Échec de suppression de {test_id}")
                else:
                    print(f"ℹ️ Client {test_id} non trouvé")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {test_id}: {str(e)}")
        
        # Vérifier l'état final
        final_clients = client_controller.get_all_clients()
        print(f"\n📊 Nombre final de clients : {len(final_clients)}")
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {str(e)}")

if __name__ == "__main__":
    print("🚀 Démarrage des tests de saisie manuelle d'IDs...\n")
    
    success = test_manual_id_creation()
    
    if success:
        print("\n✅ Tests terminés avec succès !")
        
        # Demander si on doit nettoyer
        print("\n🧹 Nettoyage des clients de test...")
        cleanup_test_clients()
    else:
        print("\n❌ Échec des tests !")
    
    print("\n🏁 Fin des tests.")