#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour supprimer le client problématique avec ID 'محمد_عبدالهادي_2708'
"""

import sqlite3
import os

def delete_problematic_client():
    """Supprimer le client avec l'ID problématique"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'visa_tracking.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée : {db_path}")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ID du client problématique
        problematic_id = 'محمد_عبدالهادي_2708'
        
        # Vérifier si le client existe
        cursor.execute("SELECT client_id, full_name FROM clients WHERE client_id = ?", (problematic_id,))
        client = cursor.fetchone()
        
        if client:
            print(f"🔍 Client trouvé : {client[0]} - {client[1]}")
            
            # Supprimer le client
            cursor.execute("DELETE FROM clients WHERE client_id = ?", (problematic_id,))
            
            # Supprimer les entrées dans status_history si elles existent
            cursor.execute("DELETE FROM status_history WHERE client_id = ?", (problematic_id,))
            
            # Valider les changements
            conn.commit()
            
            print(f"✅ Client supprimé avec succès : {problematic_id}")
            
            # Vérifier le nombre total de clients restants
            cursor.execute("SELECT COUNT(*) FROM clients")
            total_clients = cursor.fetchone()[0]
            print(f"📊 Nombre total de clients restants : {total_clients}")
            
            # Vérifier les derniers IDs
            cursor.execute("SELECT client_id FROM clients WHERE client_id LIKE 'CLI%' ORDER BY client_id DESC LIMIT 5")
            last_ids = cursor.fetchall()
            print("🔢 Derniers IDs CLI :")
            for id_tuple in last_ids:
                print(f"   - {id_tuple[0]}")
                
        else:
            print(f"ℹ️ Client non trouvé : {problematic_id}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {str(e)}")
        return False

if __name__ == "__main__":
    print("🗑️ Suppression du client problématique...")
    success = delete_problematic_client()
    
    if success:
        print("\n✅ Opération terminée avec succès !")
    else:
        print("\n❌ Échec de l'opération !")