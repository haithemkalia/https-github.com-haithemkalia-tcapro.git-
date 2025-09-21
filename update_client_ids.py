#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour mettre à jour tous les IDs clients au format officiel CLI001
"""

import sqlite3
import json
from datetime import datetime

def update_client_ids():
    """Mettre à jour tous les IDs clients au format CLI001"""
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    
    try:
        # Récupérer tous les clients avec leurs IDs actuels
        cursor.execute('SELECT id, client_id, full_name FROM clients ORDER BY id')
        clients = cursor.fetchall()
        
        print(f"📊 {len(clients)} clients trouvés")
        
        # Créer un mapping des anciens IDs vers les nouveaux
        id_mapping = {}
        new_id_counter = 1
        
        for db_id, old_client_id, full_name in clients:
            # Générer le nouveau ID au format CLI001
            new_client_id = f"CLI{new_id_counter:03d}"
            id_mapping[old_client_id] = new_client_id
            
            print(f"🔄 {old_client_id} → {new_client_id} ({full_name})")
            new_id_counter += 1
        
        # Mettre à jour tous les IDs
        updated_count = 0
        for old_id, new_id in id_mapping.items():
            cursor.execute('UPDATE clients SET client_id = ? WHERE client_id = ?', (new_id, old_id))
            updated_count += 1
        
        conn.commit()
        
        print(f"✅ {updated_count} IDs mis à jour avec succès")
        
        # Vérifier le résultat
        cursor.execute('SELECT COUNT(*) FROM clients')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT client_id FROM clients ORDER BY client_id LIMIT 5')
        sample_ids = [row[0] for row in cursor.fetchall()]
        
        return {
            'success': True,
            'updated_count': updated_count,
            'total_clients': total,
            'sample_ids': sample_ids
        }
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()

if __name__ == '__main__':
    result = update_client_ids()
    print(json.dumps(result, ensure_ascii=False))
