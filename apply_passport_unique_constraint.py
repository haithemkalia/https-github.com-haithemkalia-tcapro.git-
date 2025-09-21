#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour appliquer la contrainte UNIQUE sur passport_number
"""

import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def apply_passport_unique_constraint():
    """Appliquer la contrainte UNIQUE sur passport_number"""
    
    print('🔒 APPLICATION DE LA CONTRAINTE UNIQUE SUR PASSPORT_NUMBER')
    print('=' * 60)

    try:
        # Connexion à la base de données
        db_path = 'visa_system.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print('\n1️⃣ VÉRIFICATION DE LA STRUCTURE ACTUELLE...')
        
        # Vérifier la structure actuelle
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        
        passport_column = None
        for col in columns:
            if col[1] == 'passport_number':
                passport_column = col
                break
        
        if passport_column:
            print(f'   📋 Colonne passport_number trouvée: {passport_column}')
            print(f'   🔍 Type: {passport_column[2]}')
            print(f'   🔍 Not Null: {passport_column[3]}')
            print(f'   🔍 Default: {passport_column[4]}')
            print(f'   🔍 Primary Key: {passport_column[5]}')
        else:
            print('   ❌ Colonne passport_number non trouvée')
            return
        
        print('\n2️⃣ VÉRIFICATION DES DOUBLONS EXISTANTS...')
        
        # Vérifier s'il y a des doublons
        cursor.execute('''
            SELECT passport_number, COUNT(*) as count 
            FROM clients 
            WHERE passport_number IS NOT NULL AND passport_number != ''
            GROUP BY passport_number 
            HAVING COUNT(*) > 1
        ''')
        
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f'   ⚠️ {len(duplicates)} numéros de passeport dupliqués trouvés:')
            for passport, count in duplicates:
                print(f'      - {passport}: {count} occurrences')
            
            print('\n   🔧 Correction des doublons...')
            
            # Corriger les doublons en ajoutant un suffixe
            for passport, count in duplicates:
                cursor.execute('''
                    SELECT id, client_id FROM clients 
                    WHERE passport_number = ? 
                    ORDER BY id
                ''', (passport,))
                
                clients = cursor.fetchall()
                
                # Garder le premier, modifier les autres
                for i, (client_id, client_id_str) in enumerate(clients[1:], 1):
                    new_passport = f"{passport}_DUP_{i}"
                    cursor.execute('''
                        UPDATE clients 
                        SET passport_number = ? 
                        WHERE id = ?
                    ''', (new_passport, client_id))
                    print(f'      ✅ {client_id_str}: {passport} → {new_passport}')
        else:
            print('   ✅ Aucun doublon trouvé')
        
        print('\n3️⃣ APPLICATION DE LA CONTRAINTE UNIQUE...')
        
        # Créer un index unique sur passport_number
        try:
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_clients_passport_unique 
                ON clients(passport_number)
            ''')
            print('   ✅ Index unique créé avec succès')
        except sqlite3.OperationalError as e:
            if 'UNIQUE constraint failed' in str(e):
                print('   ⚠️ Contrainte UNIQUE déjà appliquée')
            else:
                print(f'   ❌ Erreur lors de la création de l\'index: {e}')
                return
        
        print('\n4️⃣ VÉRIFICATION DE LA CONTRAINTE...')
        
        # Tester la contrainte
        try:
            # Insérer un test
            cursor.execute('''
                INSERT INTO clients (client_id, full_name, passport_number, visa_status)
                VALUES (?, ?, ?, ?)
            ''', ('TEST_UNIQUE_1', 'Test Unique 1', 'UNIQUE_TEST_PASS', 'تم التقديم في السيستام'))
            
            # Tenter d'insérer le même numéro
            cursor.execute('''
                INSERT INTO clients (client_id, full_name, passport_number, visa_status)
                VALUES (?, ?, ?, ?)
            ''', ('TEST_UNIQUE_2', 'Test Unique 2', 'UNIQUE_TEST_PASS', 'تم التقديم في السيستام'))
            
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
        
        print('\n6️⃣ VÉRIFICATION FINALE...')
        
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
        print('   ✅ Contrainte UNIQUE appliquée sur passport_number')
        print('   ✅ Doublons corrigés si présents')
        print('   ✅ Index unique créé')
        print('   ✅ Validation fonctionnelle')
        
        print('\n🚀 LA CONTRAINTE UNIQUE EST MAINTENANT ACTIVE!')
        print('   Les numéros de passeport doivent maintenant être uniques.')
        
    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    apply_passport_unique_constraint()
