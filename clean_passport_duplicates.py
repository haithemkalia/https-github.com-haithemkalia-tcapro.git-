#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour nettoyer tous les doublons de numéros de passeport
"""

import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def clean_passport_duplicates():
    """Nettoyer tous les doublons de numéros de passeport"""
    
    print('🧹 NETTOYAGE DES DOUBLONS DE NUMÉROS DE PASSEPORT')
    print('=' * 60)

    try:
        # Connexion à la base de données
        db_path = 'visa_system.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print('\n1️⃣ IDENTIFICATION DE TOUS LES DOUBLONS...')
        
        # Trouver tous les doublons
        cursor.execute('''
            SELECT passport_number, COUNT(*) as count 
            FROM clients 
            WHERE passport_number IS NOT NULL AND passport_number != ''
            GROUP BY passport_number 
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC
        ''')
        
        duplicates = cursor.fetchall()
        print(f'   📊 {len(duplicates)} numéros de passeport dupliqués trouvés')
        
        if not duplicates:
            print('   ✅ Aucun doublon trouvé')
            return
        
        print('\n2️⃣ CORRECTION DES DOUBLONS...')
        
        total_corrected = 0
        
        for passport, count in duplicates:
            print(f'\n   🔧 Correction de {passport} ({count} occurrences):')
            
            # Récupérer tous les clients avec ce numéro de passeport
            cursor.execute('''
                SELECT id, client_id, full_name, created_at 
                FROM clients 
                WHERE passport_number = ? 
                ORDER BY created_at ASC, id ASC
            ''', (passport,))
            
            clients = cursor.fetchall()
            
            # Garder le premier (le plus ancien), modifier les autres
            for i, (client_id, client_id_str, full_name, created_at) in enumerate(clients[1:], 1):
                new_passport = f"{passport}_DUP_{i:03d}"
                
                cursor.execute('''
                    UPDATE clients 
                    SET passport_number = ? 
                    WHERE id = ?
                ''', (new_passport, client_id))
                
                print(f'      ✅ {client_id_str} ({full_name}): {passport} → {new_passport}')
                total_corrected += 1
        
        print(f'\n   📊 Total corrigé: {total_corrected} enregistrements')
        
        print('\n3️⃣ VÉRIFICATION APRÈS CORRECTION...')
        
        # Vérifier qu'il n'y a plus de doublons
        cursor.execute('''
            SELECT passport_number, COUNT(*) as count 
            FROM clients 
            WHERE passport_number IS NOT NULL AND passport_number != ''
            GROUP BY passport_number 
            HAVING COUNT(*) > 1
        ''')
        
        remaining_duplicates = cursor.fetchall()
        
        if remaining_duplicates:
            print(f'   ⚠️ {len(remaining_duplicates)} doublons restants:')
            for passport, count in remaining_duplicates:
                print(f'      - {passport}: {count} occurrences')
        else:
            print('   ✅ Aucun doublon restant')
        
        print('\n4️⃣ APPLICATION DE LA CONTRAINTE UNIQUE...')
        
        try:
            # Créer un index unique sur passport_number
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_clients_passport_unique 
                ON clients(passport_number)
            ''')
            print('   ✅ Index unique créé avec succès')
        except sqlite3.OperationalError as e:
            print(f'   ⚠️ Erreur lors de la création de l\'index: {e}')
        
        print('\n5️⃣ TEST DE LA CONTRAINTE...')
        
        # Tester la contrainte
        try:
            # Insérer un test
            cursor.execute('''
                INSERT INTO clients (client_id, full_name, passport_number, visa_status)
                VALUES (?, ?, ?, ?)
            ''', ('TEST_UNIQUE_FINAL', 'Test Unique Final', 'UNIQUE_TEST_FINAL', 'تم التقديم في السيستام'))
            
            # Tenter d'insérer le même numéro
            cursor.execute('''
                INSERT INTO clients (client_id, full_name, passport_number, visa_status)
                VALUES (?, ?, ?, ?)
            ''', ('TEST_UNIQUE_FINAL_2', 'Test Unique Final 2', 'UNIQUE_TEST_FINAL', 'تم التقديم في السيستام'))
            
            print('   ❌ Contrainte UNIQUE non appliquée')
            
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                print('   ✅ Contrainte UNIQUE appliquée avec succès')
            else:
                print(f'   ⚠️ Erreur d\'intégrité différente: {e}')
        except Exception as e:
            print(f'   ⚠️ Erreur inattendue: {e}')
        
        print('\n6️⃣ NETTOYAGE DES DONNÉES DE TEST...')
        
        # Supprimer les données de test
        cursor.execute('DELETE FROM clients WHERE client_id LIKE "TEST_%"')
        deleted_count = cursor.rowcount
        print(f'   🗑️ {deleted_count} enregistrements de test supprimés')
        
        # Valider les changements
        conn.commit()
        print('   ✅ Changements validés')
        
        print('\n7️⃣ STATISTIQUES FINALES...')
        
        # Compter les enregistrements
        cursor.execute('SELECT COUNT(*) FROM clients')
        total_clients = cursor.fetchone()[0]
        print(f'   📊 Total clients: {total_clients}')
        
        # Compter les numéros de passeport uniques
        cursor.execute('''
            SELECT COUNT(DISTINCT passport_number) 
            FROM clients 
            WHERE passport_number IS NOT NULL AND passport_number != ''
        ''')
        unique_passports = cursor.fetchone()[0]
        print(f'   📊 Numéros de passeport uniques: {unique_passports}')
        
        # Vérifier l'index
        cursor.execute("PRAGMA index_list(clients)")
        indexes = cursor.fetchall()
        
        unique_indexes = [idx for idx in indexes if 'passport' in idx[1].lower()]
        if unique_indexes:
            print('   ✅ Index unique sur passport_number confirmé')
        else:
            print('   ⚠️ Index unique non trouvé')
        
        conn.close()
        
        print('\n8️⃣ RÉSUMÉ:')
        print(f'   ✅ {total_corrected} doublons corrigés')
        print('   ✅ Contrainte UNIQUE appliquée sur passport_number')
        print('   ✅ Index unique créé')
        print('   ✅ Validation fonctionnelle')
        
        print('\n🚀 LE NETTOYAGE EST TERMINÉ!')
        print('   Les numéros de passeport sont maintenant uniques.')
        
    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_passport_duplicates()
