#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exporter la liste complète des clients pour comparaison
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime

def export_complete_clients():
    print("📋 EXPORTATION DE LA LISTE COMPLÈTE DES CLIENTS")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('visa_system.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Obtenir le nombre total
        cursor.execute("SELECT COUNT(*) as total FROM clients")
        total = cursor.fetchone()['total']
        print(f"📊 Nombre total de clients: {total}")
        
        # Obtenir tous les clients avec tous leurs détails
        cursor.execute("""
            SELECT 
                client_id,
                full_name,
                whatsapp_number,
                passport_number,
                nationality,
                visa_status,
                application_date,
                transaction_date,
                processed_by,
                responsible_employee,
                passport_status,
                created_at,
                updated_at
            FROM clients 
            ORDER BY 
                CASE WHEN client_id IS NULL OR client_id = '' THEN 1 ELSE 0 END ASC,
                client_id ASC
        """)
        
        all_clients = cursor.fetchall()
        
        # Créer un DataFrame pour faciliter l'export
        df = pd.DataFrame([dict(client) for client in all_clients])
        
        print(f"📋 Nombre de clients récupérés: {len(df)}")
        
        # Sauvegarder en Excel
        excel_filename = f"clients_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(excel_filename, index=False, engine='openpyxl')
        print(f"💾 Fichier Excel créé: {excel_filename}")
        
        # Sauvegarder en JSON
        json_filename = f"clients_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        clients_list = df.to_dict('records')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(clients_list, f, ensure_ascii=False, indent=2, default=str)
        print(f"💾 Fichier JSON créé: {json_filename}")
        
        # Afficher les statistiques
        print(f"\n📈 Statistiques:")
        print(f"  - Total clients: {len(df)}")
        print(f"  - Premiers clients:")
        for i in range(min(5, len(df))):
            print(f"    {df.iloc[i]['client_id']}: {df.iloc[i]['full_name']}")
        
        print(f"\n  - Derniers clients:")
        for i in range(max(0, len(df)-5), len(df)):
            print(f"    {df.iloc[i]['client_id']}: {df.iloc[i]['full_name']}")
        
        # Vérifier CLI100N spécifiquement
        cli100n_rows = df[df['client_id'] == 'CLI100N']
        if not cli100n_rows.empty:
            print(f"\n✅ CLI100N trouvé:")
            print(f"  - Nom: {cli100n_rows.iloc[0]['full_name']}")
            print(f"  - Nationalité: {cli100n_rows.iloc[0]['nationality']}")
            print(f"  - WhatsApp: {cli100n_rows.iloc[0]['whatsapp_number']}")
            print(f"  - Passeport: {cli100n_rows.iloc[0]['passport_number']}")
        else:
            print(f"\n❌ CLI100N non trouvé dans la base")
        
        # Vérifier CLI1000
        cli1000_rows = df[df['client_id'] == 'CLI1000']
        if not cli1000_rows.empty:
            print(f"\n✅ CLI1000 trouvé:")
            print(f"  - Nom: {cli1000_rows.iloc[0]['full_name']}")
        
        # Compter par nationalité
        print(f"\n🌍 Répartition par nationalité:")
        nationality_counts = df['nationality'].value_counts().head(10)
        for nat, count in nationality_counts.items():
            print(f"  - {nat}: {count}")
        
        conn.close()
        
        return excel_filename, json_filename, len(df)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exportation: {e}")
        return None, None, 0

def check_render_status():
    """Vérifier l'état du site Render"""
    print(f"\n🌐 VÉRIFICATION DU SITE RENDER")
    print("=" * 35)
    
    try:
        import requests
        
        # Tester le site Render
        response = requests.get('https://https-github-com-haithemkalia-tcapro-git.onrender.com/clients', timeout=30)
        
        print(f"📊 Status Render: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Chercher des indicateurs de clients
            if 'CLI100' in content:
                print("✅ Des clients CLI100 sont présents sur Render")
            else:
                print("❌ Pas de clients CLI100 trouvés sur Render")
            
            if 'عمر الإدريسي' in content:
                print("✅ Omar Al-Idrissi (CLI1000) trouvé sur Render")
            else:
                print("❌ Omar Al-Idrissi non trouvé sur Render")
            
            # Compter les occurrences de client_id patterns
            import re
            client_pattern = r'CLI\d+'
            clients_found = re.findall(client_pattern, content)
            print(f"📊 Nombre de clients détectés: {len(set(clients_found))}")
            
            if clients_found:
                print(f"📝 Premiers clients: {list(set(clients_found))[:10]}")
        
        else:
            print(f"❌ Problème avec Render: {response.status_code}")
            print("💡 Le site semble en cours de démarrage ou avoir des problèmes")
            
    except Exception as e:
        print(f"❌ Erreur de connexion à Render: {e}")
        print("💡 Le site peut être en cours de démarrage")

if __name__ == "__main__":
    # Exporter les clients locaux
    excel_file, json_file, total_local = export_complete_clients()
    
    # Vérifier Render
    check_render_status()
    
    print(f"\n🎯 RÉSUMÉ:")
    print(f"  📁 Fichiers créés: {excel_file}, {json_file}")
    print(f"  🏠 Total local: {total_local} clients")
    print(f"  🌐 Vérifiez Render pour comparer")