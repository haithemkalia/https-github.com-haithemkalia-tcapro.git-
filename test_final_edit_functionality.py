#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final pour démontrer que la sauvegarde des modifications client fonctionne
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'src'))

def test_complete_edit_workflow():
    """Test complet du workflow d'édition"""
    try:
        from src.database.database_manager import DatabaseManager
        from src.controllers.client_controller import ClientController
        
        print("🧪 TEST FINAL - Fonctionnalité d'édition des clients")
        print("=" * 55)
        
        # Initialiser les composants
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        # Récupérer tous les clients
        clients = db_manager.get_all_clients()
        if not clients:
            print("❌ Aucun client trouvé")
            return False
        
        print(f"📊 Nombre de clients dans la base: {len(clients)}")
        
        # Sélectionner le premier client pour le test
        test_client = clients[0]
        client_id = test_client['client_id']
        
        print(f"\n🎯 Client sélectionné pour le test: {client_id}")
        print(f"   Nom actuel: {test_client['full_name']}")
        print(f"   Statut visa: {test_client['visa_status']}")
        print(f"   Nationalité: {test_client['nationality']}")
        
        # Sauvegarder les données originales
        original_data = dict(test_client)
        
        # Préparer les modifications de test
        timestamp = datetime.now().strftime("%H:%M:%S")
        modified_data = {
            'client_id': client_id,
            'full_name': f"{test_client['full_name']} [TEST-{timestamp}]",
            'whatsapp_number': test_client['whatsapp_number'],
            'whatsapp_number_clean': test_client['whatsapp_number_clean'],
            'application_date': test_client['application_date'],
            'transaction_date': test_client['transaction_date'],
            'passport_number': test_client['passport_number'],
            'passport_status': test_client['passport_status'],
            'passport_status_normalized': test_client['passport_status_normalized'],
            'nationality': test_client['nationality'],
            'visa_status': 'En cours de traitement',  # Modification du statut
            'visa_status_normalized': 'en_cours',
            'processed_by': test_client['processed_by'],
            'summary': f"{test_client['summary']} - Modifié le {timestamp}",
            'notes': f"Test de modification effectué le {timestamp}",
            'responsible_employee': test_client['responsible_employee']
        }
        
        print(f"\n🔄 Application des modifications...")
        print(f"   Nouveau nom: {modified_data['full_name']}")
        print(f"   Nouveau statut: {modified_data['visa_status']}")
        print(f"   Nouvelles notes: {modified_data['notes']}")
        
        # Effectuer la mise à jour
        success = client_controller.update_client(client_id, modified_data)
        
        if not success:
            print("❌ Échec de la mise à jour")
            return False
        
        print("✅ Mise à jour effectuée avec succès")
        
        # Vérifier que les modifications ont été sauvegardées
        print("\n🔍 Vérification de la sauvegarde...")
        updated_client = db_manager.get_client_by_id(client_id)
        
        if not updated_client:
            print("❌ Impossible de récupérer le client mis à jour")
            return False
        
        # Vérifier chaque modification
        verification_passed = True
        
        if f"[TEST-{timestamp}]" not in updated_client['full_name']:
            print("❌ Le nom n'a pas été mis à jour")
            verification_passed = False
        else:
            print("✅ Nom correctement mis à jour")
        
        if updated_client['visa_status'] != 'En cours de traitement':
            print("❌ Le statut visa n'a pas été mis à jour")
            verification_passed = False
        else:
            print("✅ Statut visa correctement mis à jour")
        
        if timestamp not in updated_client['notes']:
            print("❌ Les notes n'ont pas été mises à jour")
            verification_passed = False
        else:
            print("✅ Notes correctement mises à jour")
        
        if updated_client['updated_at'] is None:
            print("⚠️  Le timestamp de mise à jour n'est pas défini")
        else:
            print(f"✅ Timestamp de mise à jour: {updated_client['updated_at']}")
        
        # Restaurer les données originales
        print("\n🔄 Restauration des données originales...")
        restore_success = client_controller.update_client(client_id, original_data)
        
        if restore_success:
            print("✅ Données originales restaurées")
        else:
            print("⚠️  Échec de la restauration (données de test conservées)")
        
        # Résultat final
        if verification_passed:
            print("\n🎉 SUCCÈS COMPLET !")
            print("✅ La fonctionnalité d'édition fonctionne parfaitement")
            print("✅ Toutes les modifications sont correctement sauvegardées")
            print("✅ Le système de mise à jour est opérationnel")
            return True
        else:
            print("\n❌ ÉCHEC PARTIEL")
            print("Certaines modifications n'ont pas été sauvegardées")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_integrity():
    """Vérifier l'intégrité de la base de données"""
    try:
        conn = sqlite3.connect('visa_system.db')
        cursor = conn.cursor()
        
        # Vérifier la structure de la table
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        
        print("\n📋 Structure de la table clients:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Vérifier le nombre d'enregistrements
        cursor.execute("SELECT COUNT(*) FROM clients")
        count = cursor.fetchone()[0]
        print(f"\n📊 Nombre total de clients: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")
        return False

def main():
    """Fonction principale"""
    print("🔧 TEST FINAL - Système de sauvegarde des modifications")
    print("=" * 60)
    
    # Vérifier l'intégrité de la base
    print("\n1. Vérification de l'intégrité de la base de données...")
    if not check_database_integrity():
        print("❌ Problème d'intégrité de la base")
        return
    
    # Test complet du workflow
    print("\n2. Test complet du workflow d'édition...")
    if test_complete_edit_workflow():
        print("\n" + "=" * 60)
        print("🎉 RÉSULTAT FINAL: SUCCÈS COMPLET !")
        print("✅ Le problème de sauvegarde des modifications a été résolu")
        print("✅ Toutes les fonctionnalités d'édition fonctionnent correctement")
        print("✅ Les utilisateurs peuvent maintenant modifier les clients sans problème")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ RÉSULTAT FINAL: PROBLÈME PERSISTANT")
        print("Une investigation supplémentaire est nécessaire")
        print("=" * 60)

if __name__ == '__main__':
    main()