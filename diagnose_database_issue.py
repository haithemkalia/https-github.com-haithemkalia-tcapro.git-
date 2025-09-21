#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour le problème d'affichage des clients
"""

import sys
import os
from pathlib import Path
import sqlite3

# Ajouter le dossier src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def check_database_files():
    """Vérifier l'existence et la taille des fichiers de base de données"""
    print("🔍 Vérification des fichiers de base de données...")
    
    db_files = [
        'visa_tracking.db',
        'data/visa_tracking.db',
        'clients.db',
        'visa_system.db'
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            print(f"   ✅ {db_file}: {size:,} bytes")
        else:
            print(f"   ❌ {db_file}: Fichier non trouvé")

def test_direct_database_connection():
    """Tester la connexion directe à la base de données"""
    print("\n🔗 Test de connexion directe à la base de données...")
    
    db_files = ['visa_tracking.db', 'data/visa_tracking.db', 'clients.db', 'visa_system.db']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Vérifier les tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"\n   📊 {db_file}:")
                print(f"     Tables: {[table[0] for table in tables]}")
                
                # Si la table clients existe, compter les enregistrements
                if any('clients' in table[0].lower() for table in tables):
                    for table in tables:
                        table_name = table[0]
                        if 'clients' in table_name.lower():
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                            count = cursor.fetchone()[0]
                            print(f"     Clients dans {table_name}: {count}")
                            
                            # Afficher quelques exemples
                            if count > 0:
                                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                                samples = cursor.fetchall()
                                print(f"     Exemples: {len(samples)} enregistrements")
                                for i, sample in enumerate(samples):
                                    print(f"       {i+1}: {sample[:3]}...")  # Premiers champs seulement
                
                conn.close()
                
            except Exception as e:
                print(f"   ❌ Erreur avec {db_file}: {e}")

def test_application_database_manager():
    """Tester le DatabaseManager de l'application"""
    print("\n🏗️ Test du DatabaseManager de l'application...")
    
    try:
        from database.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        print(f"   ✅ DatabaseManager initialisé")
        print(f"   📁 Chemin de la base: {db_manager.db_path}")
        
        # Tester la connexion
        conn = db_manager.get_connection()
        if conn:
            print(f"   ✅ Connexion établie")
            
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients")
            count = cursor.fetchone()[0]
            print(f"   📊 Nombre de clients: {count}")
            
            if count > 0:
                cursor.execute("SELECT client_id, full_name FROM clients LIMIT 5")
                samples = cursor.fetchall()
                print(f"   📋 Exemples de clients:")
                for client_id, name in samples:
                    print(f"     - {client_id}: {name}")
            
            conn.close()
        else:
            print(f"   ❌ Impossible d'établir la connexion")
            
    except Exception as e:
        print(f"   ❌ Erreur DatabaseManager: {e}")
        import traceback
        traceback.print_exc()

def test_client_controller():
    """Tester le ClientController"""
    print("\n👥 Test du ClientController...")
    
    try:
        from database.database_manager import DatabaseManager
        from controllers.client_controller import ClientController
        
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        print(f"   ✅ ClientController initialisé")
        
        # Tester get_all_clients
        clients = client_controller.get_all_clients()
        print(f"   📊 get_all_clients() retourne: {len(clients)} clients")
        
        if clients:
            print(f"   📋 Premiers clients:")
            for i, client in enumerate(clients[:3]):
                print(f"     {i+1}: {client.get('client_id', 'N/A')} - {client.get('full_name', 'N/A')}")
        else:
            print(f"   ⚠️  Aucun client retourné par get_all_clients()")
            
    except Exception as e:
        print(f"   ❌ Erreur ClientController: {e}")
        import traceback
        traceback.print_exc()

def check_cache_system():
    """Vérifier le système de cache"""
    print("\n💾 Vérification du système de cache...")
    
    try:
        from utils.cache_manager import CacheManager
        
        cache = CacheManager()
        print(f"   ✅ CacheManager initialisé")
        
        # Vérifier le cache des clients
        cached_clients = cache.get('all_clients')
        if cached_clients is not None:
            print(f"   📊 Cache 'all_clients': {len(cached_clients)} clients")
            print(f"   🗑️  Nettoyage du cache...")
            cache.clear()
            print(f"   ✅ Cache nettoyé")
        else:
            print(f"   ℹ️  Pas de cache 'all_clients' trouvé")
            
    except Exception as e:
        print(f"   ❌ Erreur Cache: {e}")

def main():
    """Fonction principale de diagnostic"""
    print("🚨 DIAGNOSTIC DU PROBLÈME D'AFFICHAGE DES CLIENTS")
    print("=" * 60)
    
    check_database_files()
    test_direct_database_connection()
    test_application_database_manager()
    test_client_controller()
    check_cache_system()
    
    print("\n" + "=" * 60)
    print("✅ Diagnostic terminé!")
    print("\nAnalysez les résultats ci-dessus pour identifier le problème.")

if __name__ == "__main__":
    main()