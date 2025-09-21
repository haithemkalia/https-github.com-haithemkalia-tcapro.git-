#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier l'état actuel de la base de données clients
"""

import sqlite3
import os

def check_current_clients():
    """
    Vérifie l'état actuel de la base de données
    """
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'visa_tracking.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Erreur: Base de données non trouvée à {db_path}")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 État actuel de la base de données:")
        print("=" * 50)
        
        # Compter le nombre total de clients
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_clients = cursor.fetchone()[0]
        print(f"📊 Nombre total de clients: {total_clients}")
        
        # Obtenir les derniers IDs clients
        cursor.execute("SELECT client_id, full_name FROM clients ORDER BY rowid DESC LIMIT 10")
        recent_clients = cursor.fetchall()
        
        print("\n🔍 Les 10 derniers clients ajoutés:")
        for i, (client_id, full_name) in enumerate(recent_clients, 1):
            print(f"   {i:2d}. {client_id} - {full_name}")
        
        # Chercher spécifiquement les clients CLI843+
        cursor.execute("SELECT client_id, full_name FROM clients WHERE client_id >= 'CLI843' ORDER BY client_id")
        test_clients = cursor.fetchall()
        
        if test_clients:
            print(f"\n⚠️  Clients de test trouvés (CLI843+): {len(test_clients)}")
            for client_id, full_name in test_clients:
                print(f"   - {client_id}: {full_name}")
        else:
            print("\n✅ Aucun client de test (CLI843+) trouvé.")
        
        # Vérifier la plage des IDs
        cursor.execute("SELECT MIN(client_id), MAX(client_id) FROM clients WHERE client_id LIKE 'CLI%'")
        min_id, max_id = cursor.fetchone()
        
        print(f"\n📊 Plage des IDs:")
        print(f"   Minimum: {min_id}")
        print(f"   Maximum: {max_id}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erreur de base de données: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    check_current_clients()