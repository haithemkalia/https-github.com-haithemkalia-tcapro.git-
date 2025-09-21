#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour vérifier la structure exacte de la table clients"""

import sqlite3

def check_table_structure():
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    
    cursor.execute('PRAGMA table_info(clients)')
    columns = cursor.fetchall()
    
    print('Structure de la table clients:')
    print('=' * 50)
    for i, col in enumerate(columns):
        col_name = col[1]
        data_type = col[2]
        not_null = 'NOT NULL' if col[3] else 'NULL'
        default = f'DEFAULT {col[4]}' if col[4] else ''
        primary_key = 'PRIMARY KEY' if col[5] else ''
        
        print(f'{i+1:2d}. {col_name:<25} {data_type:<10} {not_null:<8} {default:<15} {primary_key}')
    
    print(f'\nTotal: {len(columns)} colonnes')
    
    # Vérifier les contraintes
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='clients'")
    create_sql = cursor.fetchone()[0]
    print(f'\nSQL de création de la table:')
    print(create_sql)
    
    conn.close()

if __name__ == '__main__':
    check_table_structure()