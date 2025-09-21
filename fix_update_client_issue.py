#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger le problème de sauvegarde des modifications client
"""

import sqlite3
import sys
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'src'))

def fix_database_schema():
    """Ajouter le champ updated_at à la table clients"""
    db_path = 'visa_system.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne updated_at existe déjà
        cursor.execute("PRAGMA table_info(clients)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'updated_at' not in columns:
            print("Ajout de la colonne 'updated_at' à la table clients...")
            cursor.execute("ALTER TABLE clients ADD COLUMN updated_at TIMESTAMP")
            conn.commit()
            print("✅ Colonne 'updated_at' ajoutée avec succès")
        else:
            print("✅ La colonne 'updated_at' existe déjà")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification de la base : {e}")
        return False

def test_update_functionality():
    """Tester la fonctionnalité de mise à jour"""
    try:
        from src.database.database_manager import DatabaseManager
        from src.controllers.client_controller import ClientController
        
        # Initialiser les composants
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        # Récupérer le premier client pour test
        clients = db_manager.get_all_clients()
        if not clients:
            print("❌ Aucun client trouvé pour le test")
            return False
        
        test_client = clients[0]
        client_id = test_client['client_id']
        
        print(f"🧪 Test de mise à jour du client {client_id}")
        print(f"Nom actuel: {test_client['full_name']}")
        
        # Préparer les données de test
        updated_data = {
            'client_id': client_id,
            'full_name': test_client['full_name'] + ' (MODIFIÉ)',
            'whatsapp_number': test_client['whatsapp_number'],
            'whatsapp_number_clean': test_client['whatsapp_number_clean'],
            'application_date': test_client['application_date'],
            'transaction_date': test_client['transaction_date'],
            'passport_number': test_client['passport_number'],
            'passport_status': test_client['passport_status'],
            'passport_status_normalized': test_client['passport_status_normalized'],
            'nationality': test_client['nationality'],
            'visa_status': test_client['visa_status'],
            'visa_status_normalized': test_client['visa_status_normalized'],
            'processed_by': test_client['processed_by'],
            'summary': test_client['summary'],
            'notes': test_client['notes'],
            'responsible_employee': test_client['responsible_employee']
        }
        
        # Tenter la mise à jour
        success = client_controller.update_client(client_id, updated_data)
        
        if success:
            print("✅ Mise à jour réussie via le contrôleur")
            
            # Vérifier que les changements ont été sauvegardés
            updated_client = db_manager.get_client_by_id(client_id)
            if updated_client and '(MODIFIÉ)' in updated_client['full_name']:
                print("✅ Les modifications ont été correctement sauvegardées")
                print(f"Nouveau nom: {updated_client['full_name']}")
                
                # Restaurer le nom original
                original_data = dict(updated_data)
                original_data['full_name'] = test_client['full_name']
                client_controller.update_client(client_id, original_data)
                print("✅ Nom original restauré")
                
                return True
            else:
                print("❌ Les modifications n'ont pas été sauvegardées")
                return False
        else:
            print("❌ Échec de la mise à jour via le contrôleur")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("🔧 Correction du problème de sauvegarde des modifications client")
    print("=" * 60)
    
    # Étape 1: Corriger le schéma de la base de données
    print("\n1. Correction du schéma de la base de données...")
    if not fix_database_schema():
        print("❌ Échec de la correction du schéma")
        return
    
    # Étape 2: Tester la fonctionnalité
    print("\n2. Test de la fonctionnalité de mise à jour...")
    if test_update_functionality():
        print("\n✅ SUCCÈS: Le problème de sauvegarde a été corrigé !")
        print("Les modifications client sont maintenant correctement sauvegardées.")
    else:
        print("\n❌ ÉCHEC: Le problème persiste")
        print("Une investigation plus approfondie est nécessaire.")

if __name__ == '__main__':
    main()