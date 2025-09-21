#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'export direct depuis le cache de l'application Flask
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Ajouter le dossier src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def export_from_cache_direct():
    """Exporter directement depuis le cache"""
    
    print("🚀 Export direct depuis le cache de l'application...")
    print("="*60)
    
    try:
        # Importer le cache directement
        from cache_manager import cache
        
        print("📦 Exploration du cache...")
        
        # Voir toutes les clés du cache
        cache_keys = list(cache.cache.keys())
        print(f"   Clés trouvées dans le cache: {cache_keys}")
        
        all_clients = []
        
        # Chercher les données clients dans le cache
        for key in cache_keys:
            if 'clients' in key:
                print(f"   🔍 Analyse de la clé: {key}")
                value, timestamp = cache.cache[key]
                print(f"   📊 Type de données: {type(value)}")
                
                if isinstance(value, tuple) and len(value) == 2:
                    # Format (clients, total)
                    clients_data, total_count = value
                    print(f"   📈 Total clients: {total_count}")
                    
                    if isinstance(clients_data, list):
                        all_clients.extend(clients_data)
                        print(f"   ✅ Ajoutés {len(clients_data)} clients")
                elif isinstance(value, list):
                    all_clients.extend(value)
                    print(f"   ✅ Ajoutés {len(value)} clients")
        
        # Si pas de clients dans le cache, essayer une autre approche
        if not all_clients:
            print("\n🔄 Tentative d'accès via l'application Flask...")
            
            # Importer Flask et créer un contexte d'application
            from flask import Flask
            from src.controllers.client_controller import ClientController
            from src.database.database_manager import DatabaseManager
            
            # Créer une instance de l'application
            app = Flask(__name__)
            
            with app.app_context():
                db_manager = DatabaseManager()
                client_controller = ClientController(db_manager)
                
                # Essayer différentes méthodes pour récupérer les clients
                try:
                    # Méthode 1: get_all_clients
                    clients, total = client_controller.get_all_clients(page=1, per_page=10000)
                    if clients:
                        all_clients = clients
                        print(f"   ✅ Récupérés {len(all_clients)} clients via get_all_clients")
                except Exception as e1:
                    print(f"   ❌ Erreur get_all_clients: {e1}")
                    
                    # Méthode 2: get_filtered_clients sans filtres
                    try:
                        clients, total = client_controller.get_filtered_clients(filters={}, page=1, per_page=10000)
                        if clients:
                            all_clients = clients
                            print(f"   ✅ Récupérés {len(all_clients)} clients via get_filtered_clients")
                    except Exception as e2:
                        print(f"   ❌ Erreur get_filtered_clients: {e2}")
        
        if not all_clients:
            print("❌ Aucun client trouvé!")
            return False
        
        print(f"\n✅ Total de clients récupérés: {len(all_clients)}")
        
        # Créer un nom de fichier avec la date et l'heure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"clients_export_{timestamp}.json"
        excel_filename = f"clients_export_{timestamp}.xlsx"
        
        # 1. Sauvegarder en JSON
        print(f"\n💾 Sauvegarde en JSON: {json_filename}")
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "total_clients": len(all_clients),
                "source": "Flask Application Cache/Direct Access"
            },
            "clients": all_clients
        }
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ JSON sauvegardé: {json_filename}")
        
        # 2. Sauvegarder en Excel
        print(f"\n📊 Sauvegarde en Excel: {excel_filename}")
        
        # Convertir les données clients en DataFrame
        df_data = []
        for client in all_clients:
            # Extraire les données de chaque client
            if isinstance(client, dict):
                client_data = {
                    'client_id': client.get('client_id', ''),
                    'full_name': client.get('full_name', ''),
                    'whatsapp_number': client.get('whatsapp_number', ''),
                    'application_date': client.get('application_date', ''),
                    'transaction_date': client.get('transaction_date', ''),
                    'passport_number': client.get('passport_number', ''),
                    'passport_status': client.get('passport_status', ''),
                    'nationality': client.get('nationality', ''),
                    'visa_status': client.get('visa_status', ''),
                    'processed_by': client.get('processed_by', ''),
                    'summary': client.get('summary', ''),
                    'notes': client.get('notes', ''),
                    'responsible_employee': client.get('responsible_employee', ''),
                    'created_at': client.get('created_at', '')
                }
            else:
                # Si c'est un objet Row ou autre type
                try:
                    client_data = {
                        'client_id': getattr(client, 'client_id', ''),
                        'full_name': getattr(client, 'full_name', ''),
                        'whatsapp_number': getattr(client, 'whatsapp_number', ''),
                        'application_date': getattr(client, 'application_date', ''),
                        'transaction_date': getattr(client, 'transaction_date', ''),
                        'passport_number': getattr(client, 'passport_number', ''),
                        'passport_status': getattr(client, 'passport_status', ''),
                        'nationality': getattr(client, 'nationality', ''),
                        'visa_status': getattr(client, 'visa_status', ''),
                        'processed_by': getattr(client, 'processed_by', ''),
                        'summary': getattr(client, 'summary', ''),
                        'notes': getattr(client, 'notes', ''),
                        'responsible_employee': getattr(client, 'responsible_employee', ''),
                        'created_at': getattr(client, 'created_at', '')
                    }
                except:
                    continue
            
            df_data.append(client_data)
        
        # Créer le DataFrame et sauvegarder en Excel
        df = pd.DataFrame(df_data)
        
        # Sauvegarder en Excel avec mise en forme
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Clients', index=False)
            
            # Obtenir le workbook et la worksheet pour la mise en forme
            workbook = writer.book
            worksheet = writer.sheets['Clients']
            
            # Ajuster la largeur des colonnes
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Limiter à 50 caractères
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"   ✅ Excel sauvegardé: {excel_filename}")
        
        # 3. Sauvegarder aussi dans la base de données SQLite
        print(f"\n💾 Sauvegarde dans la base de données SQLite...")
        
        from src.database.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        saved_count = 0
        for client_data in df_data:
            try:
                # Nettoyer les données
                clean_data = {k: v for k, v in client_data.items() if v is not None and v != ''}
                if clean_data:
                    db_manager.add_client(clean_data)
                    saved_count += 1
            except Exception as e:
                print(f"   ⚠️ Erreur lors de la sauvegarde d'un client: {e}")
                continue
        
        print(f"   ✅ {saved_count} clients sauvegardés dans la base de données")
        
        # 4. Afficher un résumé des données exportées
        print(f"\n📈 Résumé de l'export:")
        print(f"   📊 Total clients: {len(all_clients)}")
        
        # Compter par statut de visa
        visa_status_counts = {}
        for client in all_clients:
            status = client.get('visa_status', 'Non défini') if isinstance(client, dict) else getattr(client, 'visa_status', 'Non défini')
            visa_status_counts[status] = visa_status_counts.get(status, 0) + 1
        
        print(f"   📋 Par statut de visa:")
        for status, count in visa_status_counts.items():
            print(f"      - {status}: {count}")
        
        print(f"\n✅ Export terminé avec succès!")
        print(f"📁 Fichiers créés:")
        print(f"   - {json_filename}")
        print(f"   - {excel_filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = export_from_cache_direct()
    if success:
        print("\n🎉 Vos données sont maintenant sauvegardées et prêtes à être importées sur Render!")
        print("\nProchaines étapes:")
        print("1. Téléchargez le fichier Excel créé")
        print("2. Sur Render, utilisez la fonction d'import Excel")
        print("3. Sélectionnez le fichier Excel pour importer vos clients")
    else:
        print("\n❌ L'export a échoué. Essayez d'arrêter et redémarrer l'application Flask.")