import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('data/visa_tracking.db')
cursor = conn.cursor()

# Analyser la structure de la table clients
print("=== STRUCTURE DE LA TABLE CLIENTS ===")
cursor.execute('PRAGMA table_info(clients)')
columns = cursor.fetchall()
for col in columns:
    print(f"{col[1]} - {col[2]}")

# Compter le nombre total de clients
cursor.execute('SELECT COUNT(*) FROM clients')
total_clients = cursor.fetchone()[0]
print(f"\n=== NOMBRE TOTAL DE CLIENTS: {total_clients} ===")

# Vérifier s'il y a des données
if total_clients == 0:
    print("ATTENTION: Aucun client trouvé dans la base de données data/visa_tracking.db")
    print("Vérification de la base alternative...")
    conn.close()
    
    # Vérifier visa_system.db
    try:
        conn = sqlite3.connect('visa_system.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM clients')
        alt_total = cursor.fetchone()[0]
        print(f"Clients trouvés dans visa_system.db: {alt_total}")
        
        if alt_total > 0:
            # Analyser les numéros WhatsApp dans la base alternative
            print("\n=== ANALYSE DES NUMÉROS WHATSAPP (visa_system.db) ===")
            
            # Compter les numéros WhatsApp non vides
            cursor.execute('SELECT COUNT(*) FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != ""')
            whatsapp_count = cursor.fetchone()[0]
            print(f"Numéros WhatsApp non vides: {whatsapp_count}")
            
            # Compter les numéros WhatsApp vides ou NULL
            cursor.execute('SELECT COUNT(*) FROM clients WHERE whatsapp_number IS NULL OR whatsapp_number = ""')
            empty_whatsapp = cursor.fetchone()[0]
            print(f"Numéros WhatsApp vides/NULL: {empty_whatsapp}")
            
            # Analyser les formats de numéros
            print("\n=== FORMATS DES NUMÉROS WHATSAPP ===")
            cursor.execute('SELECT whatsapp_number, COUNT(*) as count FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != "" GROUP BY whatsapp_number ORDER BY count DESC LIMIT 20')
            formats = cursor.fetchall()
            for fmt in formats:
                print(f"{fmt[0]} - {fmt[1]} occurrence(s)")
            
            # Vérifier les doublons
            print("\n=== DOUBLONS WHATSAPP ===")
            cursor.execute('SELECT whatsapp_number, COUNT(*) as count FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != "" GROUP BY whatsapp_number HAVING COUNT(*) > 1 ORDER BY count DESC')
            duplicates = cursor.fetchall()
            if duplicates:
                print(f"Nombre de numéros en doublon: {len(duplicates)}")
                for dup in duplicates[:10]:  # Afficher les 10 premiers
                    print(f"{dup[0]} - {dup[1]} occurrences")
            else:
                print("Aucun doublon trouvé")
            
            # Échantillon de numéros
            print("\n=== ÉCHANTILLON DE NUMÉROS WHATSAPP ===")
            cursor.execute('SELECT client_id, whatsapp_number FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != "" LIMIT 15')
            sample = cursor.fetchall()
            for s in sample:
                print(f"{s[0]}: {s[1]}")
        
    except Exception as e:
        print(f"Erreur lors de l'accès à visa_system.db: {e}")
else:
    # Analyser les numéros WhatsApp
    print("\n=== ANALYSE DES NUMÉROS WHATSAPP ===")
    
    # Compter les numéros WhatsApp non vides
    cursor.execute('SELECT COUNT(*) FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != ""')
    whatsapp_count = cursor.fetchone()[0]
    print(f"Numéros WhatsApp non vides: {whatsapp_count}")
    
    # Compter les numéros WhatsApp vides ou NULL
    cursor.execute('SELECT COUNT(*) FROM clients WHERE whatsapp_number IS NULL OR whatsapp_number = ""')
    empty_whatsapp = cursor.fetchone()[0]
    print(f"Numéros WhatsApp vides/NULL: {empty_whatsapp}")
    
    # Analyser les formats de numéros
    print("\n=== FORMATS DES NUMÉROS WHATSAPP ===")
    cursor.execute('SELECT whatsapp_number, COUNT(*) as count FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != "" GROUP BY whatsapp_number ORDER BY count DESC LIMIT 20')
    formats = cursor.fetchall()
    for fmt in formats:
        print(f"{fmt[0]} - {fmt[1]} occurrence(s)")
    
    # Vérifier les doublons
    print("\n=== DOUBLONS WHATSAPP ===")
    cursor.execute('SELECT whatsapp_number, COUNT(*) as count FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != "" GROUP BY whatsapp_number HAVING COUNT(*) > 1 ORDER BY count DESC')
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"Nombre de numéros en doublon: {len(duplicates)}")
        for dup in duplicates[:10]:  # Afficher les 10 premiers
            print(f"{dup[0]} - {dup[1]} occurrences")
    else:
        print("Aucun doublon trouvé")
    
    # Échantillon de numéros
    print("\n=== ÉCHANTILLON DE NUMÉROS WHATSAPP ===")
    cursor.execute('SELECT client_id, whatsapp_number FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != "" LIMIT 15')
    sample = cursor.fetchall()
    for s in sample:
        print(f"{s[0]}: {s[1]}")

conn.close()
print("\n=== ANALYSE TERMINÉE ===")