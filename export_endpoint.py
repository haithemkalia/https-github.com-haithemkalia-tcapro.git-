#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoint d'export pour Flask - Ajouter à votre application
"""

from flask import Flask, jsonify, send_file, render_template_string, make_response, request
import pandas as pd
import json
from datetime import datetime
import io
import os
from pathlib import Path

# Template HTML simple pour l'export
EXPORT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Export des Clients - TCA Visa System</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .export-btn { 
            background: #007bff; color: white; padding: 10px 20px; 
            text-decoration: none; border-radius: 5px; margin: 10px;
            display: inline-block;
        }
        .export-btn:hover { background: #0056b3; }
        .info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Export des Données Clients</h1>
        
        <div class="info">
            <h3>📊 Statistiques Actuelles</h3>
            <p><strong>Total Clients:</strong> {{ stats.total_clients }}</p>
            <p><strong>Exporté le:</strong> {{ stats.export_date }}</p>
        </div>
        
        <h2>📥 Formats d'Export Disponibles</h2>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="/export/json" class="export-btn">📄 Exporter en JSON</a>
            <a href="/export/excel" class="export-btn">📊 Exporter en Excel</a>
            <a href="/export/csv" class="export-btn">📋 Exporter en CSV</a>
        </div>
        
        <div class="info">
            <h3>ℹ️ Instructions</h3>
            <ol>
                <li>Cliquez sur le format souhaité pour télécharger les données</li>
                <li>Le fichier JSON contient toutes les données avec métadonnées</li>
                <li>Le fichier Excel est prêt pour l'import dans d'autres systèmes</li>
                <li>Le fichier CSV est compatible avec tous les tableurs</li>
            </ol>
        </div>
        
        {% if message %}
        <div class="{{ message.type }}">
            {{ message.text }}
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

def create_export_routes(app, client_controller):
    """Créer les routes d'export pour l'application Flask"""
    
    @app.route('/export')
    def export_home():
        """Page d'accueil pour l'export"""
        try:
            # Récupérer les statistiques
            clients, total = client_controller.get_all_clients(page=1, per_page=1)
            
            stats = {
                'total_clients': total,
                'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return render_template_string(EXPORT_TEMPLATE, stats=stats)
            
        except Exception as e:
            return f"Erreur: {str(e)}", 500
    
    @app.route('/export/json')
    def export_json():
        """Exporter tous les clients en JSON"""
        try:
            # Récupérer TOUS les clients
            all_clients = []
            page = 1
            per_page = 1000
            
            while True:
                clients, total = client_controller.get_all_clients(page=page, per_page=per_page)
                if not clients:
                    break
                all_clients.extend(clients)
                if len(all_clients) >= total:
                    break
                page += 1
                if page > 20:  # Sécurité
                    break
            
            # Créer la structure d'export
            export_data = {
                "export_info": {
                    "timestamp": datetime.now().isoformat(),
                    "total_clients": len(all_clients),
                    "source": "TCA Visa Tracking System",
                    "format": "JSON"
                },
                "clients": all_clients
            }
            
            # Créer le fichier JSON en mémoire
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
            
            # Créer une réponse avec le fichier JSON
            response = make_response(json_str)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename=clients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            
            return response
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/export/excel')
    def export_excel():
        """Exporter tous les clients en Excel"""
        try:
            # Récupérer les paramètres de filtrage depuis la requête
            search = request.args.get('search', '').strip()
            status = request.args.get('status', '').strip()
            nationality = request.args.get('nationality', '').strip()
            employee = request.args.get('employee', '').strip()
            
            # Récupérer TOUS les clients avec les filtres
            all_clients = []
            page = 1
            per_page = 1000
            
            while True:
                # Appliquer les filtres si nécessaire
                if search or status or nationality or employee:
                    # Construire le dictionnaire de filtres
                    filters = {}
                    if search:
                        filters['search'] = search
                    if status:
                        filters['visa_status'] = status
                    if nationality:
                        filters['nationality'] = nationality
                    if employee:
                        filters['responsible_employee'] = employee
                    
                    # Utiliser la fonction de recherche avec filtres
                    clients, total = client_controller.get_filtered_clients(
                        filters=filters,
                        page=page,
                        per_page=per_page
                    )
                else:
                    # Sinon récupérer tous les clients
                    clients, total = client_controller.get_all_clients(page=page, per_page=per_page)
                
                if not clients:
                    break
                all_clients.extend(clients)
                if len(all_clients) >= total:
                    break
                page += 1
                if page > 20:  # Sécurité
                    break
            
            # Convertir en DataFrame
            df_data = []
            for client in all_clients:
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
                    # Pour les objets Row ou autres
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
                df_data.append(client_data)
            
            df = pd.DataFrame(df_data)
            
            # Créer le fichier Excel en mémoire
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Clients', index=False)
                
                # Ajuster la largeur des colonnes
                workbook = writer.book
                worksheet = writer.sheets['Clients']
                
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Préparer la réponse
            output.seek(0)
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename=clients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            
            return response
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/export/csv')
    def export_csv():
        """Exporter tous les clients en CSV"""
        try:
            # Récupérer TOUS les clients
            all_clients = []
            page = 1
            per_page = 1000
            
            while True:
                clients, total = client_controller.get_all_clients(page=page, per_page=per_page)
                if not clients:
                    break
                all_clients.extend(clients)
                if len(all_clients) >= total:
                    break
                page += 1
                if page > 20:  # Sécurité
                    break
            
            # Convertir en DataFrame
            df_data = []
            for client in all_clients:
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
                    # Pour les objets Row ou autres
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
                df_data.append(client_data)
            
            df = pd.DataFrame(df_data)
            
            # Créer le CSV en mémoire
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_data = csv_buffer.getvalue()
            
            # Créer la réponse
            response = make_response(csv_data.encode('utf-8'))
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=clients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            return response
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def add_export_to_app(app, client_controller):
    """Ajouter les routes d'export à l'application Flask"""
    create_export_routes(app, client_controller)
    print("✅ Routes d'export ajoutées:")
    print("   - /export (page d'accueil)")
    print("   - /export/json (export JSON)")
    print("   - /export/excel (export Excel)")
    print("   - /export/csv (export CSV)")

if __name__ == "__main__":
    print("Ce script doit être importé dans votre application Flask principale (app.py)")
    print("Utilisez: from export_endpoint import add_export_to_app")
    print("Puis: add_export_to_app(app, client_controller)")