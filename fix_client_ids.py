#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger les معرف العميل (client_id) de CLI001 à CLI842 dans l'ordre chronologique
"""

import sqlite3
import sys
import os

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.database_manager import DatabaseManager

def fix_client_ids():
    """Corriger tous les client_id pour qu'ils suivent l'ordre CLI001 à CLI842"""
    
    print("🔧 Début de la correction des معرف العميل (client_id)...")
    
    # Initialiser le gestionnaire de base de données
    db_manager = DatabaseManager()
    
    # Obtenir une connexion directe pour les opérations en lot
    conn = db_manager.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Récupérer tous les clients ordonnés par leur ID de base de données (ordre chronologique)
        print("📊 Récupération des clients dans l'ordre chronologique...")
        cursor.execute('SELECT id, client_id, full_name FROM clients ORDER BY id ASC')
        clients = cursor.fetchall()
        
        total_clients = len(clients)
        print(f"📈 Total des clients trouvés: {total_clients}")
        
        if total_clients != 842:
            print(f"⚠️  ATTENTION: {total_clients} clients trouvés au lieu de 842!")
            response = input("Voulez-vous continuer quand même? (o/n): ")
            if response.lower() != 'o':
                print("❌ Opération annulée.")
                return False
        
        # Mettre à jour chaque client avec un nouvel ID séquentiel
        print("🔄 Mise à jour des client_id...")
        updated_count = 0
        
        for index, client in enumerate(clients, 1):
            new_client_id = f"CLI{index:03d}"  # CLI001, CLI002, etc.
            old_client_id = client['client_id']
            
            # Mettre à jour le client_id
            cursor.execute(
                'UPDATE clients SET client_id = ? WHERE id = ?',
                (new_client_id, client['id'])
            )
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✅ Client {client['id']}: {old_client_id} → {new_client_id} ({client['full_name'][:30]}...)")
            else:
                print(f"❌ Échec mise à jour client {client['id']}: {old_client_id}")
        
        # Valider les changements
        conn.commit()
        print(f"\n🎉 Mise à jour terminée! {updated_count}/{total_clients} clients mis à jour.")
        
        # Vérifier les résultats
        print("\n🔍 Vérification des résultats...")
        cursor.execute('SELECT client_id FROM clients ORDER BY id ASC LIMIT 10')
        first_10 = cursor.fetchall()
        
        print("📋 Premiers 10 client_id:")
        for client in first_10:
            print(f"   - {client['client_id']}")
        
        cursor.execute('SELECT client_id FROM clients ORDER BY id DESC LIMIT 5')
        last_5 = cursor.fetchall()
        
        print("📋 Derniers 5 client_id:")
        for client in reversed(last_5):
            print(f"   - {client['client_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def update_status_history():
    """Mettre à jour la table status_history si elle existe"""
    
    print("\n🔄 Vérification de la table status_history...")
    
    db_manager = DatabaseManager()
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        # Vérifier si la table status_history existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='status_history'
        """)
        
        if cursor.fetchone():
            print("📋 Table status_history trouvée. Mise à jour des références...")
            
            # Mettre à jour les références dans status_history
            cursor.execute("""
                UPDATE status_history 
                SET client_id = (
                    SELECT client_id 
                    FROM clients 
                    WHERE clients.id = status_history.client_db_id
                )
                WHERE EXISTS (
                    SELECT 1 
                    FROM clients 
                    WHERE clients.id = status_history.client_db_id
                )
            """)
            
            updated_history = cursor.rowcount
            conn.commit()
            print(f"✅ {updated_history} enregistrements mis à jour dans status_history.")
            
        else:
            print("ℹ️  Table status_history non trouvée. Aucune mise à jour nécessaire.")
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour de status_history: {str(e)}")
        conn.rollback()
        
    finally:
        conn.close()

def main():
    """Fonction principale"""
    print("🚀 Script de correction des معرف العميل (client_id)")
    print("=" * 60)
    
    # Étape 1: Corriger les client_id
    if fix_client_ids():
        print("\n" + "=" * 60)
        
        # Étape 2: Mettre à jour status_history
        update_status_history()
        
        print("\n" + "=" * 60)
        print("🎉 SUCCÈS: Tous les معرف العميل ont été corrigés!")
        print("📊 Les clients sont maintenant numérotés de CLI001 à CLI842 dans l'ordre chronologique.")
        
    else:
        print("\n" + "=" * 60)
        print("❌ ÉCHEC: La correction des معرف العميل a échoué.")
        return 1
    
    return 0

if __name__ == "__main__"