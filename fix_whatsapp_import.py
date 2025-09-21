import sqlite3
import pandas as pd
from datetime import datetime

# Vérifier la structure de visa_system.db
print("=== VÉRIFICATION DE LA STRUCTURE visa_system.db ===")
conn = sqlite3.connect('visa_system.db')
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(clients)')
columns = cursor.fetchall()
print("Colonnes dans visa_system.db:")
for col in columns:
    print(f"{col[1]} - {col[2]}")

# Vérifier les données WhatsApp actuelles
cursor.execute('SELECT COUNT(*) FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != ""')
whatsapp_filled = cursor.fetchone()[0]
print(f"\nNuméros WhatsApp remplis: {whatsapp_filled}")

# Lire le fichier Excel pour vérifier les colonnes exactes
print("\n=== VÉRIFICATION DU FICHIER EXCEL ===")
df = pd.read_excel('قائمة الزبائن معرض_أكتوبر2025 (21).xlsx')
print("Colonnes dans le fichier Excel:")
for i, col in enumerate(df.columns):
    print(f"{i}: '{col}'")

# Identifier la colonne WhatsApp exacte
whatsapp_col = None
for col in df.columns:
    if 'واتساب' in col:
        whatsapp_col = col
        print(f"\nColonne WhatsApp trouvée: '{whatsapp_col}'")
        break

if whatsapp_col:
    print(f"Valeurs non nulles dans {whatsapp_col}: {df[whatsapp_col].notna().sum()}")
    print(f"Échantillon: {df[whatsapp_col].dropna().head(5).tolist()}")
    
    # Corriger l'importation des numéros WhatsApp
    print("\n=== CORRECTION DE L'IMPORTATION WHATSAPP ===")
    
    updated_count = 0
    for index, row in df.iterrows():
        client_id = row.get('معرف العميل')
        whatsapp_number = row.get(whatsapp_col)
        
        if pd.notna(client_id) and pd.notna(whatsapp_number):
            # Mettre à jour le numéro WhatsApp pour ce client
            cursor.execute(
                "UPDATE clients SET whatsapp_number = ? WHERE client_id = ?",
                (str(whatsapp_number).strip(), str(client_id).strip())
            )
            if cursor.rowcount > 0:
                updated_count += 1
    
    conn.commit()
    print(f"Numéros WhatsApp mis à jour: {updated_count}")
    
    # Vérifier le résultat
    cursor.execute('SELECT COUNT(*) FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != ""')
    final_whatsapp = cursor.fetchone()[0]
    print(f"Numéros WhatsApp après correction: {final_whatsapp}")
    
    # Afficher un échantillon
    print("\n=== ÉCHANTILLON APRÈS CORRECTION ===")
    cursor.execute('SELECT client_id, full_name, whatsapp_number FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != "" LIMIT 10')
    sample = cursor.fetchall()
    for s in sample:
        print(f"{s[0]}: {s[1]} - {s[2]}")

conn.close()
print("\n=== CORRECTION TERMINÉE ===")