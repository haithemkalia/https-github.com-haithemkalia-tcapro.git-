#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'export des clients depuis le cache/application en cours d'exécution
Pour sauvegarder les données avant le déploiement sur Render
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Ajouter le dossier src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def export_clients_from_running_app():
    """Exporter les clients depuis l'application en cours d'exécution"""
    
    print("🚀 Export des clients depuis l'application en cours d'exécution...")
    print("="*60)
    
    try:
        # Importer les modules nécessaires
        from src.controllers.client_controller import ClientController
        from src.database.database_manager import DatabaseManager
        
        # Initialiser la base de données et le contrôleur
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        print("📊 Récupération de tous les clients...")
        
        # Récupérer TOUS les clients (sans pagination)
        all_clients = []
        page = 1
        per_page = 1000  # Récupérer 1000 clients par page
        
        while True:
            clients, total = client_controller.get_all_clients(page=page, per_page=per_page)
            
            if not clients:
                break
                
            all_clients.extend(clients)
            print(f"   📄 Page {page}: {len(clients)} clients récupérés")
            
            # Si on a récupéré tous les clients, on s'arrête
            if len(all_clients) >= total:
                break
                
            page += 1
            
            # Sécurité: limiter à 10 pages max pour éviter les boucles infinies
            if page > 10:
                break
        
        print(f"\n✅ Total de clients récupérés: {len(all_clients)}")
        
        if not all_clients:
            print("❌ Aucun client trouvé dans l'application!")
            return False
        
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
                "source": "Running Flask Application"
            },
            "clients": all_clients
        }
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ JSON sauvegardé: {json_filename}")
        
        # 2. Sauvegarder en Excel pour faciliter l'import
        print(f"\n📊 Sauvegarde en Excel: {excel_filename}")
        
        # Convertir les données clients en DataFrame
        df_data = []
        for client in all_clients:
            # Extraire les données de chaque client
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
        
        # 3. Afficher un résumé des données exportées
        print(f"\n📈 Résumé de l'export:")
        print(f"   📊 Total clients: {len(all_clients)}")
        
        # Compter par statut de visa
        visa_status_counts = {}
        for client in all_clients:
            status = client.get('visa_status', 'Non défini')
            visa_status_counts[status] = visa_status_counts.get(status, 0) + 1
        
        print(f"   📋 Par statut de visa:")
        for status, count in visa_status_counts.items():
            print(f"      - {status}: {count}")
        
        # Compter par nationalité
        nationality_counts = {}
        for client in all_clients:
            nationality = client.get('nationality', 'Non défini')
            nationality_counts[nationality] = nationality_counts.get(nationality, 0) + 1
        
        print(f"   🌍 Par nationalité:")
        for nationality, count in nationality_counts.items():
            print(f"      - {nationality}: {count}")
        
        # Compter par employé responsable
        employee_counts = {}
        for client in all_clients:
            employee = client.get('responsible_employee', 'Non défini')
            employee_counts[employee] = employee_counts.get(employee, 0) + 1
        
        print(f"   👥 Par employé responsable:")
        for employee, count in employee_counts.items():
            print(f"      - {employee}: {count}")
        
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
    success = export_clients_from_running_app()
    if success:
        print("\n🎉 Vos données sont maintenant sauvegardées et prêtes à être importées sur Render!")
        print("\nProchaines étapes:")
        print("1. Téléchargez le fichier Excel créé")
        print("2. Sur Render, utilisez la fonction d'import Excel")
        print("3. Sélectionnez le fichier Excel pour importer vos clients")
    else:
        print("\n❌ L'export a échoué. Vérifiez que l'application Flask est en cours d'exécution.")