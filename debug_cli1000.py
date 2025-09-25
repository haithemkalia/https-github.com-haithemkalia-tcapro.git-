import sqlite3

conn = sqlite3.connect('visa_system.db')
cursor = conn.cursor()

# Vérifier CLI1000 en détail
cursor.execute('SELECT * FROM clients WHERE client_id = ?', ('CLI1000',))
cli1000 = cursor.fetchone()
if cli1000:
    print('CLI1000 trouvé:')
    # Obtenir les noms de colonnes
    cursor.execute('PRAGMA table_info(clients)')
    columns = [col[1] for col in cursor.fetchall()]
    for i, value in enumerate(cli1000):
        print(f'  {columns[i]}: {value}')
else:
    print('CLI1000 NON trouvé dans la base de données!')

# Vérifier le tri SQL en détail
cursor.execute('''
    SELECT client_id, full_name,
           CASE WHEN client_id IS NULL OR client_id = '' THEN 1 ELSE 0 END as sort_order,
           CAST(SUBSTR(client_id, 4) AS INTEGER) as numeric_part,
           SUBSTR(client_id, 4) as substr_part
    FROM clients 
    WHERE client_id LIKE 'CLI%'
    ORDER BY 
        CASE WHEN client_id IS NULL OR client_id = '' THEN 1 ELSE 0 END ASC,
        CAST(SUBSTR(client_id, 4) AS INTEGER) DESC 
    LIMIT 20
''')
results = cursor.fetchall()
print('\nTop 20 clients avec détails de tri:')
for row in results:
    print(f'  {row[0]} - {row[1]} | sort: {row[2]}, numeric: {row[3]}, substr: "{row[4]}"')

conn.close()