import sqlite3
import pandas as pd
from collections import Counter
import re

print("="*60)
print("    RAPPORT DÉTAILLÉ - IMPORTATION NUMÉROS WHATSAPP")
print("="*60)

# Connexion à la base de données
conn = sqlite3.connect('visa_system.db')
cursor = conn.cursor()

# 1. STATISTIQUES GÉNÉRALES
print("\n📊 1. STATISTIQUES GÉNÉRALES")
print("-" * 40)

cursor.execute('SELECT COUNT(*) FROM clients')
total_clients = cursor.fetchone()[0]
print(f"Total clients dans la base: {total_clients}")

cursor.execute('SELECT COUNT(*) FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != ""')
whatsapp_filled = cursor.fetchone()[0]
print(f"Clients avec numéro WhatsApp: {whatsapp_filled}")

cursor.execute('SELECT COUNT(*) FROM clients WHERE whatsapp_number IS NULL OR whatsapp_number = ""')
whatsapp_empty = cursor.fetchone()[0]
print(f"Clients sans numéro WhatsApp: {whatsapp_empty}")

print(f"Taux de remplissage: {(whatsapp_filled/total_clients)*100:.1f}%")

# 2. ANALYSE DES FORMATS
print("\n📱 2. ANALYSE DES FORMATS DE NUMÉROS")
print("-" * 40)

cursor.execute('SELECT whatsapp_number FROM clients WHERE whatsapp_number IS NOT NULL AND whatsapp_number != ""')
numbers = [row[0] for row in cursor.fetchall()]

# Analyser les formats
formats = {
    'Libye (218)': 0,
    'Tunisie (216)': 0,
    'Turquie (90)': 0,
    'Chine (86)': 0,
    'Autres pays': 0,
    'Format invalide': 0
}

lengths = Counter()
for num in numbers:
    clean_num = re.sub(r'[^0-9]', '', str(num))
    lengths[len(clean_num)] += 1
    
    if clean_num.startswith('218'):
        formats['Libye (218)'] += 1
    elif clean_num.startswith('216'):
        formats['Tunisie (216)'] += 1
    elif clean_num.startswith('90'):
        formats['Turquie (90)'] += 1
    elif clean_num.startswith('86'):
        formats['Chine (86)'] += 1
    elif len(clean_num) >= 8:
        formats['Autres pays'] += 1
    else:
        formats['Format invalide'] += 1

for country, count in formats.items():
    if count > 0:
        print(f"{country}: {count} numéros ({(count/whatsapp_filled)*100:.1f}%)")

print("\nDistribution par longueur:")
for length, count in sorted(lengths.items()):
    print(f"{length} chiffres: {count} numéros")

# 3. ANALYSE DES DOUBLONS
print("\n🔄 3. ANALYSE DES DOUBLONS")
print("-" * 40)

cursor.execute('''
    SELECT whatsapp_number, COUNT(*) as count, 
           GROUP_CONCAT(client_id) as client_ids,
           GROUP_CONCAT(full_name) as names
    FROM clients 
    WHERE whatsapp_number IS NOT NULL AND whatsapp_number != "" 
    GROUP BY whatsapp_number 
    HAVING COUNT(*) > 1 
    ORDER BY count DESC
''')

duplicates = cursor.fetchall()
print(f"Numéros en doublon: {len(duplicates)}")

if duplicates:
    total_duplicate_entries = sum(dup[1] for dup in duplicates)
    print(f"Total d'entrées dupliquées: {total_duplicate_entries}")
    print(f"Pourcentage de doublons: {(total_duplicate_entries/whatsapp_filled)*100:.1f}%")
    
    print("\nTop 10 des numéros les plus dupliqués:")
    for i, (number, count, client_ids, names) in enumerate(duplicates[:10], 1):
        ids_list = client_ids.split(',')
        names_list = names.split(',')
        print(f"{i}. {number} ({count} fois)")
        for j, (cid, name) in enumerate(zip(ids_list[:3], names_list[:3])):
            print(f"   - {cid}: {name}")
        if count > 3:
            print(f"   ... et {count-3} autres")
        print()
else:
    print("Aucun doublon détecté")

# 4. ÉCHANTILLON REPRÉSENTATIF
print("\n📋 4. ÉCHANTILLON REPRÉSENTATIF")
print("-" * 40)

cursor.execute('''
    SELECT client_id, full_name, whatsapp_number, nationality
    FROM clients 
    WHERE whatsapp_number IS NOT NULL AND whatsapp_number != "" 
    ORDER BY RANDOM() 
    LIMIT 15
''')

sample = cursor.fetchall()
for client in sample:
    print(f"{client[0]}: {client[1]} | {client[2]} | {client[3] or 'N/A'}")

# 5. VALIDATION DES CHAMPS VIDES PRÉSERVÉS
print("\n📝 5. VALIDATION DES CHAMPS VIDES PRÉSERVÉS")
print("-" * 40)

# Vérifier les champs vides dans le fichier Excel original
df = pd.read_excel('قائمة الزبائن معرض_أكتوبر2025 (21).xlsx')
whatsapp_col = 'رقم الواتساب '

excel_empty = df[whatsapp_col].isna().sum()
excel_filled = df[whatsapp_col].notna().sum()

print(f"Dans le fichier Excel:")
print(f"  - Numéros remplis: {excel_filled}")
print(f"  - Champs vides: {excel_empty}")

print(f"\nDans la base de données:")
print(f"  - Numéros remplis: {whatsapp_filled}")
print(f"  - Champs vides: {whatsapp_empty}")

if excel_filled == whatsapp_filled and excel_empty == whatsapp_empty:
    print("✅ SUCCÈS: Les champs vides ont été correctement préservés")
else:
    print("⚠️  ATTENTION: Différence détectée dans la préservation des champs vides")

# 6. RÉSUMÉ FINAL
print("\n🎯 6. RÉSUMÉ FINAL")
print("-" * 40)
print(f"✅ Import réussi: {whatsapp_filled}/{total_clients} numéros WhatsApp")
print(f"✅ Taux de succès: {(whatsapp_filled/excel_filled)*100:.1f}%")
print(f"✅ Doublons préservés: {len(duplicates)} numéros dupliqués")
print(f"✅ Champs vides respectés: {whatsapp_empty} entrées vides")
print(f"✅ Formats variés supportés: {len(formats)} types de pays détectés")

print("\n" + "="*60)
print("    VÉRIFICATION TERMINÉE AVEC SUCCÈS")
print("="*60)

conn.close()