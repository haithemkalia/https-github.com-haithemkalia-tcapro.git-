#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour supprimer totalement tous les clients de la base de données
"""

import sqlite3
import os
import shutil
from datetime import datetime

def backup_database():
    """Créer une sauvegarde de la base de données"""
    print("💾 Création d'une sauvegarde de sécurité...")
    
    db_path = 'visa_system.db'
    if not os.path.exists(db_path):
        print(f"❌ Base de données {db_path} non trouvée")
        return False
    
    # Créer le nom de sauvegarde avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'visa_system_backup_{timestamp}.db'
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Sauvegarde créée: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

def count_clients():
    """Compter le nombre de clients dans la base"""
    try:
        conn = sqlite3.connect('visa_system.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM clients')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"❌ Erreur lors du comptage: {e}")
        return -1

def delete_all_clients():
    """Supprimer tous les clients de la base de données"""
    print("🗑️ Suppression de tous les clients de la base de données")
    print("=" * 60)
    
    # Compter les clients avant suppression
    initial_count = count_clients()
    if initial_count == -1:
        return False
    
    print(f"📊 Nombre de clients avant suppression: {initial_count}")
    
    if initial_count == 0:
        print("ℹ️ La base de données est déjà vide")
        return True
    
    # Demander confirmation
    print(f"⚠️ ATTENTION: Vous allez supprimer {initial_count} clients!")
    confirmation = input("Tapez 'SUPPRIMER' pour confirmer: ")
    
    if confirmation != 'SUPPRIMER':
        print("❌ Opération annulée")
        return False
    
    # Créer une sauvegarde
    backup_path = backup_database()
    if not backup_path:
        print("❌ Impossible de créer une sauvegarde. Opération annulée.")
        return False
    
    try:
        conn = sqlite3.connect('visa_system.db')
        cursor = conn.cursor()
        
        print("🔥 Suppression de tous les clients...")
        
        # Supprimer tous les clients
        cursor.execute('DELETE FROM clients')
        deleted_count = cursor.rowcount
        
        # Réinitialiser l'auto-increment
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="clients"')
        
        conn.commit()
        
        # Vérifier que la table est vide
        final_count = count_clients()
        
        print(f"✅ {deleted_count} clients supprimés")
        print(f"📊 Nombre de clients après suppression: {final_count}")
        
        if final_count == 0:
            print("✅ Suppression totale réussie!")
            print(f"💾 Sauvegarde disponible: {backup_path}")
            
            # Vérifier la structure de la table
            cursor.execute('PRAGMA table_info(clients)')
            columns = cursor.fetchall()
            print(f"📋 Structure de la table préservée ({len(columns)} colonnes)")
            
            conn.close()
            return True
        else:
            print(f"❌ Erreur: {final_count} clients restants")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def verify_empty_database():
    """Vérifier que la base de données est vide"""
    print("\n🔍 Vérification finale...")
    
    try:
        conn = sqlite3.connect('visa_system.db')
        cursor = conn.cursor()
        
        # Vérifier le nombre de clients
        cursor.execute('SELECT COUNT(*) FROM clients')
        count = cursor.fetchone()[0]
        
        # Vérifier la structure
        cursor.execute('PRAGMA table_info(clients)')
        columns = cursor.fetchall()
        
        # Vérifier l'auto-increment
        cursor.execute('SELECT seq FROM sqlite_sequence WHERE name="clients"')
        seq_result = cursor.fetchone()
        
        conn.close()
        
        print(f"📊 Clients dans la base: {count}")
        print(f"📋 Colonnes dans la table: {len(columns)}")
        print(f"🔢 Auto-increment réinitialisé: {'Oui' if seq_result is None else 'Non'}")
        
        if count == 0:
            print("✅ Base de données complètement vide et prête")
            return True
        else:
            print(f"❌ {count} clients restants")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

if __name__ == '__main__':
    print("🚨 SUPPRESSION TOTALE DES CLIENTS TCA 🚨")
    print("=" * 60)
    
    success = delete_all_clients()
    
    if success:
        verify_empty_database()
        print("\n🎉 Opération terminée avec succès !")
        print("📝 La base de données est maintenant vide")
        print("🔄 Vous pouvez maintenant ajouter de nouveaux clients")
    else:
        print("\n💥 Opération échouée !")
        print("🔄 Veuillez vérifier les erreurs ci-dessus")