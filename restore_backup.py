#!/usr/bin/env python3
"""
Script pour restaurer les données clients depuis restructured_columns.json
"""

import json
import sqlite3
from datetime import datetime

def restore_clients_from_backup():
    """Restaurer les clients depuis le fichier restructured_columns.json"""
    
    # Charger les données depuis le backup
    try:
        with open('restructured_columns.json', 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        clients_data = backup_data.get('sample_data', [])
        total_records = backup_data.get('total_records', 0)
        
        print(f"📁 Backup trouvé avec {total_records} clients")
        print(f"📊 Nombre d'exemples dans le fichier: {len(clients_data)}")
        
    except FileNotFoundError:
        print("❌ Fichier restructured_columns.json non trouvé")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de lecture JSON: {e}")
        return False
    
    # Connexion à la base de données
    try:
        conn = sqlite3.connect('visa_system.db')
        cursor = conn.cursor()
        
        # Vider la table existante (optionnel)
        cursor.execute("DELETE FROM clients")
        print("🗑️ Table clients vidée")
        
        # Insérer les données
        inserted_count = 0
        for client in clients_data:
            try:
                cursor.execute("""
                    INSERT INTO clients (
                        client_id, full_name, nationality, passport_number,
                        passport_status, visa_status, application_date,
                        whatsapp_number, responsible_employee, processed_by,
                        summary, notes, transaction_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    client.get('client_id', ''),
                    client.get('full_name', ''),
                    client.get('nationality', ''),
                    client.get('passport_number', ''),
                    client.get('passport_status', ''),
                    client.get('visa_status', ''),
                    client.get('application_date', ''),
                    client.get('whatsapp_number', ''),
                    client.get('responsible_employee', ''),
                    client.get('processed_by', ''),
                    client.get('summary', ''),
                    client.get('notes', ''),
                    client.get('transaction_date', '')
                ))
                inserted_count += 1
                
            except sqlite3.Error as e:
                print(f"⚠️ Erreur lors de l'insertion du client {client.get('client_id', 'inconnu')}: {e}")
                continue
        
        conn.commit()
        print(f"✅ {inserted_count} clients restaurés avec succès")
        
        # Vérifier le total
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_in_db = cursor.fetchone()[0]
        print(f"📈 Total des clients dans la base: {total_in_db}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erreur de base de données: {e}")
        return False

def check_other_backup_sources():
    """Vérifier s'il existe d'autres sources de backup"""
    
    sources = []
    
    # Vérifier excel_analysis_results.json
    try:
        with open('excel_analysis_results.json', 'r', encoding='utf-8') as f:
            excel_data = json.load(f)
        
        for sheet_name, sheet_data in excel_data.items():
            if sheet_data.get('total_rows', 0) > 0:
                sources.append({
                    'source': f'excel_analysis_results.json - {sheet_name}',
                    'rows': sheet_data.get('total_rows', 0),
                    'columns': sheet_data.get('total_columns', 0)
                })
    except:
        pass
    
    return sources

if __name__ == "__main__":
    print("🔄 Démarrage de la restauration des données clients...")
    print("=" * 50)
    
    # Vérifier les sources de backup disponibles
    print("\n📋 Sources de backup disponibles:")
    sources = check_other_backup_sources()
    
    if sources:
        for source in sources:
            print(f"   📊 {source['source']}: {source['rows']} lignes, {source['columns']} colonnes")
    
    # Restaurer depuis restructured_columns.json
    print(f"\n🎯 Restauration depuis restructured_columns.json...")
    success = restore_clients_from_backup()
    
    if success:
        print("\n✅ Restauration terminée avec succès !")
        print("🌐 Vous pouvez maintenant accéder à:")
        print("   • http://localhost:5000/export - Page d'export")
        print("   • http://localhost:5000/export/json - Export JSON")
        print("   • http://localhost:5000/export/excel - Export Excel")
        print("   • http://localhost:5000/export/csv - Export CSV")
    else:
        print("\n❌ Échec de la restauration")