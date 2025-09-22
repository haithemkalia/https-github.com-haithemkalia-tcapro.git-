#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛂 نظام تتبع التأشيرات الذكي - TCA
Application Render avec base de données préchargée
"""

import os
import sys
import sqlite3
import tempfile
import shutil
from pathlib import Path

# Configuration Render
os.environ['RENDER'] = 'true'
os.environ['PYTHONPATH'] = 'src'

# Utiliser la base de données principale au lieu de la copier
def setup_render_database():
    """Préparer la base de données principale pour Render"""
    
    # Utiliser la base de données principale qui contient tous les clients
    # Priorité: visa_system.db > clients.db > data/visa_tracking.db
    
    main_db = None
    
    if os.path.exists('visa_system.db'):
        main_db = 'visa_system.db'
    elif os.path.exists('clients.db'):
        main_db = 'clients.db'
    elif os.path.exists('data/visa_tracking.db'):
        main_db = 'data/visa_tracking.db'
    else:
        # Aucun fichier DB direct. Essayer de restaurer depuis un backup inclus dans le repo
        print("⚠️ Aucune base de données principale trouvée. Tentative de restauration depuis un backup...")
        backup_candidates = []
        # Chercher des fichiers de backup connus dans le repo
        for fname in os.listdir('.'):
            if fname.startswith('visa_system_backup_') and fname.endswith('.db') and os.path.isfile(fname):
                backup_candidates.append(fname)
        # Prendre le plus récent lexicalement (suffixe timestamp dans le nom)
        backup_candidates.sort(reverse=True)
        if backup_candidates:
            newest_backup = backup_candidates[0]
            try:
                shutil.copyfile(newest_backup, 'visa_system.db')
                print(f"🔁 Base restaurée depuis le backup: {newest_backup} -> visa_system.db")
                main_db = 'visa_system.db'
            except Exception as e:
                print(f"❌ Échec de restauration depuis le backup {newest_backup}: {e}")
        if not main_db:
            print("❌ Aucune base de données principale ou backup trouvée!")
            return False
    
    # Pour Render, utiliser directement la base principale
    target_db = main_db
    
    print(f"🔄 Configuration de la base de données Render...")
    print(f"📁 Base de données principale: {main_db}")
    
    try:
        # Vérifier que la base contient des données
        conn = sqlite3.connect(main_db)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM clients')
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Base de données configurée avec {count} clients!")
        print(f"📊 Utilisation de la base principale: {main_db}")
        
        # Créer un lien symbolique ou utiliser directement la base
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration de la base: {e}")
        return False

# Configurer la base de données avant d'importer Flask
if not setup_render_database():
    print("❌ Impossible de configurer la base de données")
    sys.exit(1)

# Importer Flask et l'application
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime

# Ajouter le dossier src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.database_manager import DatabaseManager
from controllers.client_controller import ClientController
from controllers.whatsapp_controller import WhatsAppController
from utils.excel_handler import ExcelHandler
from models.client import Client
from export_endpoint import add_export_to_app

# Configuration de l'application Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'tca_visa_tracking_secret_key_2024_render'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Créer le dossier uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialiser les contrôleurs
db_manager = DatabaseManager()
client_controller = ClientController(db_manager)
whatsapp_controller = WhatsAppController(db_manager)
excel_handler = ExcelHandler()

# Ajouter les routes d'export
add_export_to_app(app, client_controller)

# Configuration pour les templates RTL
@app.context_processor
def inject_rtl_support():
    """Injecter le support RTL dans tous les templates"""
    from datetime import datetime
    return {
        'rtl_support': True,
        'app_title': '🛂 نظام تتبع التأشيرات الذكي - TCA',
        'company_name': 'شركة تونس للاستشارات والخدمات',
        'facebook_link': 'https://www.facebook.com/share/1D4dHp2z74/?mibextid=wwXIfr',
        'current_datetime': datetime.now().strftime('%Y-%m-%d %H:%M')
    }

# Health check
@app.route('/health')
def health_check():
    """Vérifier que l'application fonctionne"""
    try:
        # Tester la connexion DB
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM clients')
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'environment': 'render',
            'clients_count': count
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Routes principales
@app.route('/')
def index():
    """Page d'accueil avec statistiques"""
    try:
        # Récupérer les statistiques
        all_clients, total_count = client_controller.get_all_clients(page=1, per_page=10000)
        
        stats = {
            'total_clients': total_count,
            'by_status': {},
            'by_nationality': {},
            'by_employee': {},
            'recent_clients': all_clients[:5] if all_clients else []
        }
        
        # Calculer les statistiques
        for status in Client.VISA_STATUS_OPTIONS:
            count = len([c for c in all_clients if c.get('visa_status') == status])
            stats['by_status'][status] = count
        
        for nationality in Client.NATIONALITY_OPTIONS:
            count = len([c for c in all_clients if c.get('nationality') == nationality])
            stats['by_nationality'][nationality] = count
        
        for employee in Client.EMPLOYEE_OPTIONS:
            count = len([c for c in all_clients if c.get('responsible_employee') == employee])
            stats['by_employee'][employee] = count
        
        return render_template('index.html', stats=stats, clients=all_clients)
        
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
        default_stats = {
            'total_clients': 0,
            'by_status': {},
            'by_nationality': {},
            'by_employee': {},
            'recent_clients': []
        }
        return render_template('index.html', stats=default_stats, clients=[])

@app.route('/clients')
def clients():
    """Liste des clients"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search_term = request.args.get('search', '')
        
        if search_term:
            clients, total = client_controller.search_clients(search_term, page, per_page)
        else:
            clients, total = client_controller.get_all_clients(page, per_page)
        
        total_pages = (total + per_page - 1) // per_page
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1 if page > 1 else None,
            'next_num': page + 1 if page < total_pages else None
        }
        
        return render_template('clients.html', 
                             clients=clients,
                             pagination=pagination,
                             search_term=search_term)
    
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
        return render_template('clients.html', clients=[], pagination={})

# Alias pour clients_list (utilisé dans les templates)
@app.route('/clients_list')
def clients_list():
    """Alias pour la route clients"""
    return clients()

# Ajouter d'autres routes nécessaires...

@app.route('/add_client')
def add_client():
    """Page d'ajout de client"""
    return redirect(url_for('add_client_form'))

@app.route('/client/edit/<client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    """Modifier un client existant"""
    try:
        client = client_controller.get_client_by_id(client_id)
        if not client:
            flash('العميل غير موجود', 'error')
            return redirect(url_for('clients_list'))
        
        if request.method == 'POST':
            # Récupérer l'ancien statut pour les notifications
            old_status = client.get('visa_status')
            
            # Récupérer les données du formulaire
            client_data = {
                'client_id': request.form.get('client_id', '').strip(),
                'full_name': request.form.get('full_name', '').strip(),
                'whatsapp_number': request.form.get('whatsapp_number', '').strip(),
                'file_date': request.form.get('application_date', '').strip(),
                'reception_date': request.form.get('receipt_date', '').strip(),
                'passport_number': request.form.get('passport_number', '').strip(),
                'passport_status': request.form.get('passport_status', '').strip(),
                'nationality': request.form.get('nationality', '').strip(),
                'visa_status': request.form.get('visa_status', 'التقديم').strip(),
                'processed_by': request.form.get('processed_by', '').strip(),
                'summary': request.form.get('summary', '').strip(),
                'notes': request.form.get('notes', '').strip(),
                'responsible_employee': request.form.get('responsible_employee', '').strip()
            }
            
            # Mettre à jour le client
            success = client_controller.update_client(client_id, client_data)
            
            if success:
                flash('تم تحديث العميل بنجاح! ✅', 'success')
                
                # Envoyer notification WhatsApp si le statut a changé
                new_status = client_data.get('visa_status')
                if (old_status != new_status and 
                    whatsapp_controller.is_whatsapp_enabled() and 
                    client_data.get('whatsapp_number')):
                    whatsapp_controller.send_status_notification(
                        client_data['client_id'], 
                        new_status, 
                        client_data['whatsapp_number']
                    )
                
                return redirect(url_for('clients_list'))
            else:
                flash('فشل في تحديث العميل', 'error')
        
        return render_template('edit_client.html',
                             client=client,
                             passport_statuses=Client.PASSPORT_STATUS_OPTIONS,
                             nationalities=Client.NATIONALITY_OPTIONS,
                             visa_statuses=Client.VISA_STATUS_OPTIONS,
                             employees=Client.EMPLOYEE_OPTIONS)
        
    except Exception as e:
        flash(f'خطأ في تحديث العميل: {str(e)}', 'error')
        return redirect(url_for('clients_list'))

@app.route('/analytics')
def analytics():
    """Page d'analyse avancée"""
    try:
        # Importer le service d'analyse
        from src.services.analytics_service import AnalyticsService
        
        # Créer le service d'analyse avec le gestionnaire de base de données
        analytics_service = AnalyticsService(db_manager)
        
        # Obtenir l'analyse complète
        analysis = analytics_service.get_comprehensive_analysis()
        
        return render_template('analytics.html', analysis=analysis)
    except Exception as e:
        print(f"Erreur lors du chargement de l'analyse: {e}")
        # Retourner une structure d'analyse vide en cas d'erreur
        analysis = {
            'overview': {'total_clients': 0, 'success_rate': 0, 'active_clients': 0},
            'visa_status_analysis': {'phase_analysis': {}},
            'nationality_analysis': {'nationality_distribution': {}, 'top_nationalities': []},
            'employee_analysis': {'employee_ranking': []},
            'performance_metrics': {'phase_conversion_rates': {}, 'efficiency_score': 0},
            'trends': {'overall_trend': 'stable', 'emerging_patterns': []},
            'geographic_analysis': {'regional_summary': {}},
            'detailed_reports': {'executive_summary': {'total_clients': 0, 'success_rate': 0}, 'recommendations': []}
        }
        return render_template('analytics.html', analysis=analysis)

@app.route('/analytics_dashboard')
def analytics_dashboard():
    """Alias pour la page d'analytiques"""
    return analytics()

@app.route('/settings')
def settings():
    """Page des paramètres"""
    try:
        # Créer l'objet settings avec les paramètres par défaut
        settings = {
            'whatsapp_enabled': True,
            'facebook_link': 'https://www.facebook.com/share/1D4dHp2z74/?mibextid=wwXIfr'
        }
        
        return render_template('settings.html', settings=settings)
    except Exception as e:
        print(f"Erreur lors du chargement des paramètres: {e}")
        # Retourner une structure settings vide en cas d'erreur
        settings = {
            'whatsapp_enabled': False,
            'facebook_link': ''
        }
        return render_template('settings.html', settings=settings)

@app.route('/import_excel')
def import_excel():
    """Page d'import Excel"""
    return render_template('import_excel.html')

@app.route('/unrestricted_import_page')
def unrestricted_import_page():
    """Page d'import sans restrictions"""
    return render_template('unrestricted_import.html')

@app.route('/client/delete/<client_id>', methods=['POST'])
def delete_client(client_id):
    """Supprimer un client avec confirmation et feedback"""
    try:
        # Récupérer les informations du client avant suppression
        client_info = client_controller.get_client_by_id(client_id)
        if not client_info:
            flash('❌ العميل غير موجود!', 'error')
            return redirect(url_for('clients_list'))
        
        client_name = client_info.get('full_name', 'غير محدد')
        
        # Supprimer le client
        success = client_controller.delete_client(client_id)
        
        if success:
            flash(f'✅ تم حذف العميل "{client_name}" بنجاح!', 'success')
        else:
            flash(f'❌ فشل في حذف العميل "{client_name}"', 'error')
    except Exception as e:
        flash(f'❌ خطأ في حذف العميل: {str(e)}', 'error')
    
    return redirect(url_for('clients_list'))

@app.route('/client/add', methods=['GET', 'POST'])
def add_client_form():
    """Ajouter un nouveau client"""
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            client_data = {
                'client_id': request.form.get('client_id', '').strip(),
                'full_name': request.form.get('full_name', '').strip(),
                'whatsapp_number': request.form.get('whatsapp_number', '').strip(),
                'file_date': request.form.get('application_date', '').strip(),
                'reception_date': request.form.get('receipt_date', '').strip(),
                'passport_number': request.form.get('passport_number', '').strip(),
                'passport_status': request.form.get('passport_status', '').strip(),
                'nationality': request.form.get('nationality', '').strip(),
                'visa_status': request.form.get('visa_status', 'التقديم').strip(),
                'processed_by': request.form.get('processed_by', '').strip(),
                'summary': request.form.get('summary', '').strip(),
                'notes': request.form.get('notes', '').strip(),
                'responsible_employee': request.form.get('responsible_employee', '').strip()
            }
            
            # Validation des champs obligatoires
            if not client_data['full_name']:
                flash('يرجى إدخال الاسم الكامل', 'error')
                return render_template('add_client.html', 
                                     nationalities=Client.NATIONALITY_OPTIONS,
                                     passport_statuses=Client.PASSPORT_STATUS_OPTIONS,
                                     visa_statuses=Client.VISA_STATUS_OPTIONS,
                                     employees=Client.EMPLOYEE_OPTIONS)
            
            if not client_data['passport_number']:
                flash('يرجى إدخال رقم جواز السفر', 'error')
                return render_template('add_client.html', 
                                     nationalities=Client.NATIONALITY_OPTIONS,
                                     passport_statuses=Client.PASSPORT_STATUS_OPTIONS,
                                     visa_statuses=Client.VISA_STATUS_OPTIONS,
                                     employees=Client.EMPLOYEE_OPTIONS)
            
            # Vérifier l'unicité du numéro de passeport
            if not db_manager.is_passport_number_unique(client_data['passport_number']):
                flash('رقم جواز السفر موجود مسبقاً. يرجى إدخال رقم آخر.', 'error')
                return render_template('add_client.html', 
                                     nationalities=Client.NATIONALITY_OPTIONS,
                                     passport_statuses=Client.PASSPORT_STATUS_OPTIONS,
                                     visa_statuses=Client.VISA_STATUS_OPTIONS,
                                     employees=Client.EMPLOYEE_OPTIONS)
            
            # Ajouter le client
            client_id = client_controller.add_client(client_data)
            
            if client_id:
                flash('تم إضافة العميل بنجاح! ✅', 'success')
                
                # Envoyer message de bienvenue WhatsApp si activé
                if whatsapp_controller.is_whatsapp_enabled() and client_data.get('whatsapp_number'):
                    whatsapp_controller.send_welcome_notification(client_data['client_id'])
                
                return redirect(url_for('clients_list'))
            else:
                flash('فشل في إضافة العميل', 'error')
                
        except Exception as e:
            flash(f'خطأ في إضافة العميل: {str(e)}', 'error')
    
    return render_template('add_client.html',
                         passport_statuses=Client.PASSPORT_STATUS_OPTIONS,
                         nationalities=Client.NATIONALITY_OPTIONS,
                         visa_statuses=Client.VISA_STATUS_OPTIONS,
                         employees=Client.EMPLOYEE_OPTIONS)

if __name__ == '__main__':
    # Configuration pour Render
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 Démarrage de l'application TCA sur Render...")
    print(f"📊 Port: {port}")
    print(f"🗄️  Base de données: {tempfile.gettempdir()}/visa_system_render.db")
    
    app.run(host='0.0.0.0', port=port, debug=False)