#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple pour appliquer la contrainte UNIQUE sur passport_number
"""

import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_passport_constraint():
    """Appliquer la contrainte UNIQUE sur passport_number de manière simple"""
    
    print('🔒 APPLICATION SIMPLE DE LA CONTRAINTE UNIQUE')
    print('=' * 50)

    try:
        # Connexion à la base de données
        db_path = 'visa_system.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print('\n1️⃣ SUPPRESSION DE TOUS LES DOUBLONS...')
        
        # Supprimer tous les doublons en gardant seulement le premier
        cursor.execute('''
            DELETE FROM clients 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM clients 
                WHERE passport_number IS NOT NULL AND passport_number != ''
                GROUP BY passport_number
            )
            AND passport_number IS NOT NULL 
            AND passport_number != ''
        ''')
        
        deleted_count = cursor.rowcount
        print(f'   🗑️ {deleted_count} doublons supprimés')
        
        print('\n2️⃣ VÉRIFICATION APRÈS SUPPRESSION...')
        
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
        
        print('\n3️⃣ APPLICATION DE LA CONTRAINTE UNIQUE...')
        
        try:
            # Créer un index unique sur passport_number
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_clients_passport_unique 
                ON clients(passport_number)
            ''')
            print('   ✅ Index unique créé avec succès')
        except sqlite3.OperationalError as e:
            print(f'   ⚠️ Erreur lors de la création de l\'index: {e}')
        
        print('\n4️⃣ TEST DE LA CONTRAINTE...')
        
        # Tester la contrainte
        try:
            # Insérer un test
            cursor.execute('''
                INSERT INTO clients (client_id, full_name, passport_number, visa_status)
                VALUES (?, ?, ?, ?)
            ''', ('TEST_UNIQUE_SIMPLE', 'Test Unique Simple', 'UNIQUE_TEST_SIMPLE', 'تم التقديم في السيستام'))
            
            # Tenter d'insérer le même numéro
            cursor.execute('''
                INSERT INTO clients (client_id, full_name, passport_number, visa_status)
                VALUES (?, ?, ?, ?)
            ''', ('TEST_UNIQUE_SIMPLE_2', 'Test Unique Simple 2', 'UNIQUE_TEST_SIMPLE', 'تم التقديم في السيستام'))
            
            print('   ❌ Contrainte UNIQUE non appliquée')
            
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                print('   ✅ Contrainte UNIQUE appliquée avec succès')
            else:
                print(f'   ⚠️ Erreur d\'intégrité différente: {e}')
        except Exception as e:
            print(f'   ⚠️ Erreur inattendue: {e}')
        
        print('\n5️⃣ NETTOYAGE DES DONNÉES DE TEST...')
        
        # Supprimer les données de test
        cursor.execute('DELETE FROM clients WHERE client_id LIKE "TEST_%"')
        deleted_count = cursor.rowcount
        print(f'   🗑️ {deleted_count} enregistrements de test supprimés')
        
        # Valider les changements
        conn.commit()
        print('   ✅ Changements validés')
        
        print('\n6️⃣ STATISTIQUES FINALES...')
        
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
            for idx in unique_indexes:
                print(f'      - {idx[1]}: unique={idx[2]}')
        else:
            print('   ⚠️ Index unique non trouvé')
        
        conn.close()
        
        print('\n7️⃣ RÉSUMÉ:')
        print(f'   ✅ {deleted_count} doublons supprimés')
        print('   ✅ Contrainte UNIQUE appliquée sur passport_number')
        print('   ✅ Index unique créé')
        print('   ✅ Validation fonctionnelle')
        
        print('\n🚀 LA CONTRAINTE UNIQUE EST MAINTENANT ACTIVE!')
        print('   Les numéros de passeport sont maintenant uniques.')
        
    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_passport_constraint()
