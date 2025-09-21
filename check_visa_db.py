import sqlite3

conn = sqlite3.connect('visa_system.db')
cursor = conn.cursor()

# Voir si la table clients existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
table_exists = cursor.fetchone()

if table_exists:
    cursor.execute('PRAGMA table_info(clients)')
    columns = cursor.fetchall()
    
    print('📊 STRUCTURE DE LA TABLE CLIENTS (visa_system.db):')
    print('=' * 60)
    for col in columns:
        print(f'{col[0]:2d}. {col[1]:<25} {col[2]:<15} NULL:{col[3]}')
else:
    print('❌ Table clients n\'existe pas dans visa_system.db')

conn.close()