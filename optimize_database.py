#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'optimisation de la base de données pour améliorer les performances
"""

import sqlite3
import os
from datetime import datetime

def optimize_database(db_path='visa_system.db'):
    """
    Optimiser la base de données en ajoutant des index et en optimisant la structure
    """
    print(f"🔧 Début de l'optimisation de la base de données: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Erreur: Base de données {db_path} non trouvée")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Ajouter des index pour améliorer les performances des requêtes
        print("📊 Ajout des index de performance...")
        
        # Index sur client_id (déjà unique mais améliore les recherches)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_client_id ON clients(client_id)")
        
        # Index sur full_name pour les recherches par nom
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_full_name ON clients(full_name)")
        
        # Index sur whatsapp_number pour les recherches par WhatsApp
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_whatsapp ON clients(whatsapp_number)")
        
        # Index sur passport_number pour les recherches par passeport
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_passport ON clients(passport_number)")
        
        # Index sur visa_status pour les filtres de statut
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_visa_status ON clients(visa_status)")
        
        # Index sur nationality pour les filtres de nationalité
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nationality ON clients(nationality)")
        
        # Index sur responsible_employee pour les filtres d'employé
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_employee ON clients(responsible_employee)")
        
        # Index sur created_at pour le tri par date
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON clients(created_at)")
        
        # Index composé pour les recherches multiples
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_combo ON clients(full_name, client_id, whatsapp_number, passport_number)")
        
        # 2. Ajouter la colonne updated_at si elle n'existe pas
        print("🔄 Vérification de la colonne updated_at...")
        cursor.execute("PRAGMA table_info(clients)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'updated_at' not in columns:
            print("➕ Ajout de la colonne updated_at...")
            cursor.execute("ALTER TABLE clients ADD COLUMN updated_at TIMESTAMP")
            # Initialiser avec created_at pour les enregistrements existants
            cursor.execute("UPDATE clients SET updated_at = created_at WHERE updated_at IS NULL")
        
        # 3. Optimiser la base de données
        print("⚡ Optimisation de la base de données...")
        cursor.execute("VACUUM")
        cursor.execute("ANALYZE")
        
        # 4. Vérifier les statistiques
        print("📈 Statistiques de la base de données:")
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_clients = cursor.fetchone()[0]
        print(f"   - Total clients: {total_clients}")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='clients'")
        indexes = cursor.fetchall()
        print(f"   - Index créés: {len(indexes)}")
        for idx in indexes:
            print(f"     • {idx[0]}")
        
        # 5. Tester les performances d'une requête
        print("🚀 Test de performance d'une requête...")
        start_time = datetime.now()
        cursor.execute("SELECT * FROM clients WHERE full_name LIKE '%محمد%' ORDER BY client_id DESC LIMIT 10")
        results = cursor.fetchall()
        end_time = datetime.now()
        query_time = (end_time - start_time).total_seconds() * 1000
        print(f"   - Requête de recherche: {query_time:.2f}ms ({len(results)} résultats)")
        
        conn.commit()
        print("✅ Optimisation terminée avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'optimisation: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def check_database_performance(db_path='visa_system.db'):
    """
    Vérifier les performances actuelles de la base de données
    """
    print(f"📊 Analyse des performances de: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Test de différentes requêtes
        tests = [
            ("SELECT COUNT(*) FROM clients", "Comptage total"),
            ("SELECT * FROM clients ORDER BY client_id DESC LIMIT 50", "Liste paginée"),
            ("SELECT * FROM clients WHERE full_name LIKE '%محمد%'", "Recherche par nom"),
            ("SELECT * FROM clients WHERE visa_status = 'التقديم'", "Filtre par statut"),
            ("SELECT visa_status, COUNT(*) FROM clients GROUP BY visa_status", "Statistiques par statut")
        ]
        
        print("\n⏱️  Temps d'exécution des requêtes:")
        for query, description in tests:
            start_time = datetime.now()
            cursor.execute(query)
            results = cursor.fetchall()
            end_time = datetime.now()
            query_time = (end_time - start_time).total_seconds() * 1000
            print(f"   - {description}: {query_time:.2f}ms ({len(results)} résultats)")
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Script d'optimisation de la base de données TCA")
    print("=" * 50)
    
    # Vérifier les performances avant optimisation
    print("\n📊 AVANT OPTIMISATION:")
    check_database_performance()
    
    # Optimiser la base de données
    print("\n🔧 OPTIMISATION EN COURS:")
    success = optimize_database()
    
    if success:
        # Vérifier les performances après optimisation
        print("\n📈 APRÈS OPTIMISATION:")
        check_database_performance()
        
        print("\n🎉 Optimisation terminée! Votre système devrait être plus rapide maintenant.")
    else:
        print("\n❌ L'optimisation a échoué. Vérifiez les erreurs ci-dessus.")