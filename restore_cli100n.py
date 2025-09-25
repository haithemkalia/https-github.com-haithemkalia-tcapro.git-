#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de restauration urgente de CLI100N et des 1001 clients
"""

import sqlite3
import json
from datetime import datetime

def restore_critical_data():
    """Restaurer CLI100N et les données critiques depuis la sauvegarde"""
    print("🚨 RESTAURATION URGENTE DES DONNÉES")
    print("=" * 50)
    
    # 1. Charger la sauvegarde critique
    print("1️⃣  Chargement de la sauvegarde...")
    try:
        with open('BACKUP_CRITICAL_1001_CLIENTS.json', 'r', encoding='utf-8') as f:
            backup = json.load(f)
        print(f"✅ Sauvegarde chargée: {backup['total_clients']} clients")
    except Exception as e:
        print(f"❌ Erreur chargement sauvegarde: {e}")
        return False
    
    # 2. Vérifier l'état actuel
    print("\n2️⃣  Vérification de l'état actuel...")
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM clients')
    current_total = cursor.fetchone()[0]
    print(f"📊 Clients actuels: {current_total}")
    
    cursor.execute('SELECT COUNT(*) FROM clients WHERE client_id = ?', ('CLI100N',))
    cli100n_current = cursor.fetchone()[0]
    print(f"🎯 CLI100N présent: {cli100n_current > 0}")
    
    # 3. Restaurer CLI100N spécifiquement
    if backup['cli100n_exists'] and not cli100n_current:
        print("\n3️⃣  Restauration de CLI100N...")
        cli100n_data = backup['cli100n_data']
        
        # Préparer la requête d'insertion
        columns = list(cli100n_data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        values = [cli100n_data[col] for col in columns]
        
        insert_query = f"INSERT INTO clients ({', '.join(columns)}) VALUES ({placeholders})"
        
        try:
            cursor.execute(insert_query, values)
            conn.commit()
            print(f"✅ CLI100N restauré avec succès!")
            print(f"   - ID: {cli100n_data['client_id']}")
            print(f"   - Nom: {cli100n_data['full_name']}")
            print(f"   - Téléphone: {cli100n_data['whatsapp_number']}")
        except Exception as e:
            print(f"❌ Erreur restauration CLI100N: {e}")
            # Vérifier si c'est un doublon
            if "UNIQUE constraint failed" in str(e):
                print("⚠️  CLI100N existe déjà (contrainte unique)")
    
    # 4. Vérifier les clients manquants
    print("\n4️⃣  Analyse des clients manquants...")
    cursor.execute('SELECT client_id FROM clients ORDER BY client_id')
    current_clients = {row[0] for row in cursor.fetchall()}
    
    backup_clients = {client['client_id'] for client in backup['all_clients']}
    missing_clients = backup_clients - current_clients
    
    print(f"📊 Clients dans sauvegarde: {len(backup_clients)}")
    print(f"📊 Clients actuels: {len(current_clients)}")
    print(f"📊 Clients manquants: {len(missing_clients)}")
    
    if missing_clients:
        print(f"📝 Premiers clients manquants: {list(missing_clients)[:5]}")
    
    # 5. Restaurer les clients manquants (optionnel)
    if len(missing_clients) > 0 and len(missing_clients) < 50:  # Pas trop de clients
        print(f"\n5️⃣  Restauration de {len(missing_clients)} clients manquants...")
        
        clients_to_restore = [
            client for client in backup['all_clients'] 
            if client['client_id'] in missing_clients
        ]
        
        restored_count = 0
        for client_data in clients_to_restore:
            try:
                columns = list(client_data.keys())
                placeholders = ', '.join(['?' for _ in columns])
                values = [client_data[col] for col in columns]
                
                insert_query = f"INSERT INTO clients ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(insert_query, values)
                restored_count += 1
                
                if restored_count % 100 == 0:
                    print(f"   Restaurés: {restored_count}/{len(clients_to_restore)}")
                    
            except Exception as e:
                print(f"   Erreur {client_data['client_id']}: {e}")
                continue
        
        conn.commit()
        print(f"✅ {restored_count} clients restaurés avec succès!")
    
    # 6. Vérification finale
    print("\n6️⃣  Vérification finale...")
    cursor.execute('SELECT COUNT(*) FROM clients')
    final_total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM clients WHERE client_id = ?', ('CLI100N',))
    cli100n_final = cursor.fetchone()[0]
    
    print(f"📊 Total final: {final_total} clients")
    print(f"🎯 CLI100N présent: {cli100n_final > 0}")
    
    # Différence
    difference = final_total - current_total
    if difference > 0:
        print(f"✅ +{difference} clients ajoutés")
    elif difference < 0:
        print(f"⚠️  {difference} clients perdus")
    else:
        print("ℹ️  Aucun changement dans le total")
    
    conn.close()
    
    # 7. Rapport
    print("\n" + "=" * 50)
    print("📋 RAPPORT DE RESTAURATION")
    print("=" * 50)
    print(f"🕐 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Clients avant: {current_total}")
    print(f"📊 Clients après: {final_total}")
    print(f"🎯 CLI100N restauré: {'✅ Oui' if cli100n_final > 0 else '❌ Non'}")
    print(f"📈 Différence: {difference:+d}")
    
    if final_total >= 1001:
        print("🎉 OBJECTIF ATTEINT: 1001+ clients restaurés!")
    else:
        print(f"⚠️  OBJECTIF MANQUÉ: {1001 - final_total} clients manquants")
    
    return final_total >= 1001 and cli100n_final > 0

if __name__ == "__main__":
    success = restore_critical_data()
    
    if success:
        print("\n✅ RESTAURATION RÉUSSIE!")
        print("🚀 Vous pouvez maintenant vérifier vos clients avec:")
        print("   python verify_cli100n.py")
    else:
        print("\n❌ RESTAURATION ÉCHOUÉE")
        print("📞 Contactez le support technique")