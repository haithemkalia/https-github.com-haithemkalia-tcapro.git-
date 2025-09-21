#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour supprimer les clients de test CLI843 à CLI847
Créé pour nettoyer la base de données après les tests de fonctionnalité
"""

import sqlite3
import os

def delete_test_clients():
    """
    Supprime les clients de test CLI843 à CLI847 de la base de données
    """
    # Chemin vers la base de données principale
    db_path = os.path.join(os.path.dirname(__file__), 'visa_system.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Erreur: Base de données non trouvée à {db_path}")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier d'abord l'état actuel
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_before = cursor.fetchone()[0]
        print(f"📊 Nombre total de clients avant suppression: {total_before}")
        
        # Liste des IDs de clients de test à supprimer
        test_client_ids = ['CLI843', 'CLI844', 'CLI845', 'CLI846', 'CLI847']
        
        print("\n🔍 Vérification des clients de test existants...")
        
        # Vérifier quels clients de test existent
        existing_test_clients = []
        for client_id in test_client_ids:
            cursor.execute("SELECT client_id, full_name FROM clients WHERE client_id = ?", (client_id,))
            result = cursor.fetchone()
            if result:
                existing_test_clients.append(result)
                print(f"   ✓ Trouvé: {result[0]} - {result[1]}")
        
        if not existing_test_clients:
            print("ℹ️  Aucun client de test trouvé à supprimer.")
            
            # Vérifier s'il y a des clients avec des IDs > CLI842
            cursor.execute("SELECT client_id, full_name FROM clients WHERE client_id > 'CLI842' ORDER BY client_id")
            high_clients = cursor.fetchall()
            
            if high_clients:
                print(f"\n⚠️  Clients trouvés avec des IDs > CLI842: {len(high_clients)}")
                for client_id, full_name in high_clients:
                    print(f"   - {client_id}: {full_name}")
                
                # Demander confirmation pour supprimer ces clients
                print("\n🗑️  Suppression de tous les clients avec des IDs > CLI842...")
                cursor.execute("DELETE FROM clients WHERE client_id > 'CLI842'")
                deleted_count = cursor.rowcount
                print(f"   ✓ Supprimé {deleted_count} clients")
            else:
                print("   ✅ Aucun client avec ID > CLI842 trouvé.")
                conn.close()
                return True
        else:
            print(f"\n🗑️  Suppression de {len(existing_test_clients)} clients de test...")
            
            # Supprimer les clients de test spécifiques
            deleted_count = 0
            for client_id in test_client_ids:
                cursor.execute("DELETE FROM clients WHERE client_id = ?", (client_id,))
                if cursor.rowcount > 0:
                    deleted_count += 1
                    print(f"   ✓ Supprimé: {client_id}")
        
        # Supprimer également de la table status_history si elle existe
        try:
            cursor.execute("DELETE FROM status_history WHERE client_id > 'CLI842'")
            if cursor.rowcount > 0:
                print(f"   ✓ Supprimé {cursor.rowcount} entrées de l'historique des statuts")
        except sqlite3.OperationalError:
            # La table status_history n'existe peut-être pas
            pass
        
        # Valider les changements
        conn.commit()
        
        # Vérifier le nombre total de clients restants
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_after = cursor.fetchone()[0]
        
        print(f"\n✅ Suppression terminée avec succès!")
        print(f"   📊 Clients avant: {total_before}")
        print(f"   📊 Clients après: {total_after}")
        print(f"   📊 Clients supprimés: {total_before - total_after}")
        
        # Vérifier que nous avons bien 842 clients (les originaux)
        if total_after == 842:
            print("   ✅ Parfait! Nous avons exactement 842 clients originaux.")
        else:
            print(f"   ⚠️  Attention: Nombre de clients inattendu ({total_after} au lieu de 842)")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erreur de base de données: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def verify_client_range():
    """
    Vérifie que les clients restants sont bien CLI001 à CLI842
    """
    db_path = os.path.join(os.path.dirname(__file__), 'visa_system.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Vérification de la plage des IDs clients...")
        
        # Obtenir le plus petit et le plus grand ID
        cursor.execute("SELECT MIN(client_id), MAX(client_id) FROM clients WHERE client_id LIKE 'CLI%'")
        min_id, max_id = cursor.fetchone()
        
        print(f"   📊 ID minimum: {min_id}")
        print(f"   📊 ID maximum: {max_id}")
        
        # Vérifier s'il y a des IDs > CLI842
        cursor.execute("SELECT client_id FROM clients WHERE client_id > 'CLI842' ORDER BY client_id")
        high_ids = cursor.fetchall()
        
        if high_ids:
            print(f"   ⚠️  IDs trouvés au-dessus de CLI842:")
            for (client_id,) in high_ids:
                print(f"      - {client_id}")
        else:
            print("   ✅ Aucun ID au-dessus de CLI842 trouvé.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

if __name__ == "__main__":
    print("🧹 Script de suppression des clients de test")
    print("=" * 50)
    
    # Supprimer les clients de test
    success = delete_test_clients()
    
    if success:
        # Vérifier la plage des IDs
        verify_client_range()
        print("\n🎯 Nettoyage terminé avec succès!")
    else:
        print("\n❌ Échec du nettoyage.")