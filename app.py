#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛂 نظام تتبع التأشيرات الذكي - TCA
شركة تونس للاستشارات والخدمات

Application Web Flask pour la gestion des visas
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response
# from export_endpoint import add_export_to_app  # Module supprimé lors du conflit Git
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import numpy as np
import urllib.parse

# Ajouter le dossier src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.database_manager import DatabaseManager
from controllers.client_controller import ClientController
from controllers.whatsapp_controller import WhatsAppController
from utils.excel_handler import ExcelHandler
from models.client import Client
from cache_manager import cache

# Configuration de l'application Flask
app = Flask(__name__)
app.secret_key = 'tca_visa_tracking_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Fonction helper pour convertir les types numpy/pandas en types Python natifs
def convert_to_json_serializable(obj):
    """Convertit les types numpy/pandas en types Python natifs pour JSON serialization"""
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_json_serializable(item) for item in obj)
    else:
        return obj

# Ajouter la fonction min au contexte Jinja2
@app.template_global()
def min_func(a, b):
    return min(a, b)

# Rendre les fonctions min et max disponibles dans les templates
app.jinja_env.globals['min'] = min
app.jinja_env.globals['max'] = max

# Créer le dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialiser les contrôleurs
db_manager = DatabaseManager()
client_controller = ClientController(db_manager)
whatsapp_controller = WhatsAppController(db_manager)
excel_handler = ExcelHandler()

# Importer et initialiser le contrôleur d'analyse
from src.controllers.analytics_controller import AnalyticsController
analytics_controller = AnalyticsController(db_manager)

# Ajouter les routes d'export (désactivé car module supprimé)
# add_export_to_app(app, client_controller)

# Configuration pour les fichiers statiques RTL
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

# Route de test pour vérifier le déploiement
@app.route('/health')
def health_check():
    """Vérifier que l'application fonctionne"""
    try:
        # Tester la connexion DB
        db_manager.get_connection()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'environment': 'production' if os.environ.get('VERCEL') else 'development'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Routes principales
@app.route('/', endpoint='index')
def index():
    """Page d'accueil avec tableau de bord - Statistiques complètes et précises"""
    try:
        # Récupérer TOUS les clients pour des statistiques précises
        all_clients, total_count = client_controller.get_all_clients(page=1, per_page=10000)  # Récupérer tous les clients
        
        stats = {
            'total_clients': total_count,
            'by_status': {},
            'by_nationality': {},
            'by_employee': {},
            'recent_clients': all_clients[:5] if all_clients else []
        }
        
        # Calculer les statistiques par statut - TOUS les clients
        for status in Client.VISA_STATUS_OPTIONS:
            count = len([c for c in all_clients if c.get('visa_status') == status])
            stats['by_status'][status] = count
        
        # Calculer les statistiques par nationalité - TOUS les clients
        for nationality in Client.NATIONALITY_OPTIONS:
            count = len([c for c in all_clients if c.get('nationality') == nationality])
            stats['by_nationality'][nationality] = count
        
        # Calculer les statistiques par employé - TOUS les clients
        for employee in Client.EMPLOYEE_OPTIONS:
            count = len([c for c in all_clients if c.get('responsible_employee') == employee])
            stats['by_employee'][employee] = count
        
        # Debug: afficher les statistiques calculées
        print(f"📊 STATISTIQUES CALCULÉES:")
        print(f"   Total clients: {total_count}")
        print(f"   Par statut: {stats['by_status']}")
        print(f"   Par nationalité: {stats['by_nationality']}")
        print(f"   Par employé: {stats['by_employee']}")
        
        return render_template('index.html', stats=stats, clients=all_clients,
                               app_title='نظام تتبع التأشيرات',
                               company_name='شركة تسهيل للخدمات',
                               facebook_link='https://facebook.com/yourpage')
        
    except Exception as e:
        flash(f'خطأ في تحميل البيانات: {str(e)}', 'error')
        # Créer une structure stats par défaut même en cas d'erreur
        default_stats = {
            'total_clients': 0,
            'by_status': {},
            'by_nationality': {},
            'by_employee': {},
            'recent_clients': []
        }
        return render_template('index.html', stats=default_stats, clients=[])

@app.route('/readable-clients')
def readable_clients():
    """Page des clients avec template lisible"""
    try:
        # Paramètres de pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Paramètres de filtrage
        search_term = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        nationality_filter = request.args.get('nationality', '')
        employee_filter = request.args.get('employee', '')
        
        # Construire les filtres
        filters = {}
        if search_term:
            filters['search'] = search_term
        if status_filter and status_filter in Client.VISA_STATUS_OPTIONS:
            filters['visa_status'] = status_filter
        if nationality_filter and nationality_filter in Client.NATIONALITY_OPTIONS:
            filters['nationality'] = nationality_filter
        if employee_filter and employee_filter in Client.EMPLOYEE_OPTIONS:
            filters['responsible_employee'] = employee_filter
        
        # Récupérer les clients avec pagination (optimisé)
        if filters:
            clients, total = client_controller.get_filtered_clients(filters, page, per_page)
        else:
            clients, total = client_controller.get_all_clients(page, min(per_page, 100))
        
        # Calculer les informations de pagination
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': page - 1 if has_prev else None,
            'next_num': page + 1 if has_next else None
        }
        
        return render_template('clients_readable.html', 
                             clients=clients,
                             pagination=pagination,
                             search_term=search_term,
                             status_filter=status_filter,
                             nationality_filter=nationality_filter,
                             employee_filter=employee_filter,
                             visa_statuses=Client.VISA_STATUS_OPTIONS,
                             nationalities=Client.NATIONALITY_OPTIONS,
                             employees=Client.EMPLOYEE_OPTIONS)
        
    except Exception as e:
        print(f"Erreur dans readable_clients: {e}")
        return f"Erreur: {e}", 500

@app.route('/test-clients')
def test_clients():
    """Page de test des clients avec template non-minifié"""
    try:
        # Récupérer les clients
        clients, total = client_controller.get_all_clients(1, 10)
        
        pagination = {
            'page': 1,
            'per_page': 10,
            'total': total,
            'total_pages': (total + 10 - 1) // 10,
            'has_prev': False,
            'has_next': total > 10,
            'prev_num': None,
            'next_num': 2 if total > 10 else None
        }
        
        # Debug: afficher les informations
        print(f"TEST DEBUG: Nombre de clients récupérés: {len(clients)}")
        print(f"TEST DEBUG: Total: {total}")
        print(f"TEST DEBUG: Premiers clients: {[c.get('client_id', 'N/A') for c in clients[:3]]}")
        
        return render_template('test_clients.html', 
                             clients=clients,
                             pagination=pagination)
        
    except Exception as e:
        print(f"Erreur dans test_clients: {e}")
        return f"Erreur: {e}", 500

@app.route('/clients', endpoint='clients_list')
def clients_list():
    """Page de liste des clients avec pagination et cache"""
    print(f"🎯 ROUTE /clients APPELÉE - DÉBUT DU TRAITEMENT")
    print(f"🎯 URL: {request.url}")
    print(f"🎯 ARGS: {dict(request.args)}")
    try:
        # Paramètres de pagination optimisés
        page = int(request.args.get('page', 1))
        per_page_param = request.args.get('per_page', '50')  # Réduit de 100 à 50
        
        # Permettre d'afficher tous les clients
        if per_page_param == 'all':
            per_page = 10000  # Nombre très élevé pour afficher tous les clients
        else:
            per_page = int(per_page_param)
        
        # Paramètres de filtrage
        search_term = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        nationality_filter = request.args.get('nationality', '')
        employee_filter = request.args.get('employee', '')
        
        # Construire les filtres
        filters = {}
        if search_term:
            filters['search'] = search_term
        if status_filter and status_filter in Client.VISA_STATUS_OPTIONS:
            filters['visa_status'] = status_filter
        if nationality_filter and nationality_filter in Client.NATIONALITY_OPTIONS:
            filters['nationality'] = nationality_filter
        if employee_filter and employee_filter in Client.EMPLOYEE_OPTIONS:
            filters['responsible_employee'] = employee_filter
        
        # Récupérer les clients avec pagination (optimisé)
        print(f"🎯 AVANT APPEL CONTRÔLEUR - page: {page}, per_page: {per_page}, filters: {filters}")
        if filters:
            clients, total = client_controller.get_filtered_clients(filters, page, per_page)
        else:
            # Permettre l'affichage de tous les clients avec pagination
            clients, total = client_controller.get_all_clients(page, per_page)
        print(f"🎯 APRÈS APPEL CONTRÔLEUR - clients: {len(clients)}, total: {total}")
        print(f"🎯 PREMIERS CLIENTS: {[c.get('client_id', 'N/A') for c in clients[:3]]}")
        print(f"🎯 TOUS LES CLIENTS: {[c.get('client_id', 'N/A') for c in clients]}")  # DEBUG: afficher tous les clients
        
        # Écrire dans un fichier log pour débogage
        with open('debug_route.log', 'w', encoding='utf-8') as f:
            f.write(f"Page: {page}, Per page: {per_page}\n")
            f.write(f"Total clients: {total}\n")
            f.write(f"Clients returned: {len(clients)}\n")
            f.write(f"Client IDs: {[c.get('client_id', 'N/A') for c in clients]}\n")
            f.write(f"CLI1000 present: {'CLI1000' in [c.get('client_id', 'N/A') for c in clients]}\n")
        
        # Calculer les informations de pagination
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': page - 1 if has_prev else None,
            'next_num': page + 1 if has_next else None
        }
        
        # Les données sont déjà dans le bon format pour visa_system.db
        mapped_clients = clients
        
        # Debug: afficher les informations CRITIQUES
        print(f"🐛 DEBUG CRITIQUE: Nombre de clients récupérés: {len(clients)}")
        print(f"🐛 DEBUG CRITIQUE: Total: {total}")
        print(f"🐛 DEBUG CRITIQUE: Premiers clients: {[c.get('client_id', 'N/A') for c in clients[:3]]}")
        print(f"🐛 DEBUG CRITIQUE: Base de données: {db_manager.db_path}")
        print(f"🐛 DEBUG CRITIQUE: Type de contrôleur: {type(client_controller)}")
        
        return render_template('clients.html', 
                             clients=mapped_clients,
                             pagination=pagination,
                             search_term=search_term,
                             status_filter=status_filter,
                             nationality_filter=nationality_filter,
                             employee_filter=employee_filter,
                             visa_statuses=Client.VISA_STATUS_OPTIONS,
                             nationalities=Client.NATIONALITY_OPTIONS,
                             employees=Client.EMPLOYEE_OPTIONS,
                             app_title='نظام تتبع التأشيرات',
                             company_name='شركة تسهيل للخدمات',
                             facebook_link='https://facebook.com/yourpage')
        
    except Exception as e:
        flash(f'خطأ في تحميل قائمة العملاء: {str(e)}', 'error')
        return render_template('clients.html', clients=[], pagination={'page': 1, 'total': 0, 'total_pages': 0})

@app.route('/client/add', methods=['GET', 'POST'], endpoint='add_client')
def add_client():
    """Ajouter un nouveau client"""
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            client_data = {
                'client_id': request.form.get('client_id', '').strip(),
                'full_name': request.form.get('full_name', '').strip(),
                'whatsapp_number': request.form.get('whatsapp_number', '').strip(),
                'application_date': request.form.get('application_date', '').strip(),
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
                'application_date': request.form.get('application_date', '').strip(),
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

@app.route('/import-excel-raw', methods=['POST'])
def import_excel_raw():
    """Importer TOUS les clients depuis le fichier Excel spécifique sans validation"""
    try:
        # Chemin du fichier Excel spécifique
        excel_file_path = os.path.join(os.getcwd(), 'قائمة الزبائن معرض_أكتوبر2025 (21).xlsx')
        
        if not os.path.exists(excel_file_path):
            return jsonify({
                'success': False,
                'error': 'Fichier Excel spécifique non trouvé'
            }), 404
        
        # Utiliser la nouvelle fonction d'import raw
        result = excel_handler.import_clients_raw(excel_file_path)
        
        if not result['success']:
            return jsonify(result), 400
        
        # Importer TOUTES les données dans la base sans validation
        imported_data = result['imported_data']
        success_count = 0
        error_count = 0
        errors_details = []
        
        for row_data in imported_data:
            try:
                # Fonction pour convertir toutes les valeurs en string
                def safe_str(value):
                    if pd.isna(value) or value is None:
                        return ''
                    return str(value).strip()
                
                # Fonction pour normaliser les valeurs selon les options valides
                def normalize_value(value, valid_options, default):
                    if not value or value == '':
                        return default
                    # Chercher une correspondance exacte ou partielle
                    for option in valid_options:
                        if value == option or option in value or value in option:
                            return option
                    return default
                
                # Créer un client même avec des données incomplètes
                client_data = {
                    'client_id': safe_str(row_data.get('client_id')) or f'AUTO_{success_count + error_count + 1}',
                    'full_name': safe_str(row_data.get('full_name')) or 'غير محدد',
                    'whatsapp_number': safe_str(row_data.get('whatsapp_number')),
                    'application_date': safe_str(row_data.get('file_date')),
                    'receipt_date': safe_str(row_data.get('reception_date')),
                    'passport_number': safe_str(row_data.get('passport_number')),
                    'passport_status': normalize_value(safe_str(row_data.get('passport_status')), ['موجود', 'غير موجود'], 'غير موجود'),
                    'nationality': normalize_value(safe_str(row_data.get('nationality')), ['ليبي', 'تونسي', 'أخرى'], 'أخرى'),
                    'visa_status': normalize_value(safe_str(row_data.get('visa_status')), ['التقديم', 'جواز في السفارة', 'استلام الجواز', 'تمت الموافقة على التأشيرة', 'التأشيرة غير موافق عليها', 'اكتملت العملية'], 'التقديم'),
                    'handled_by': safe_str(row_data.get('handled_by')),
                    'summary': safe_str(row_data.get('summary')),
                    'notes': safe_str(row_data.get('notes')),
                    'responsible_employee': normalize_value(safe_str(row_data.get('responsible_employee')), ['اميرة', 'محمد', 'سفيان', 'اميمة', 'ايلاف', 'انيس', 'وليد'], 'اميرة')
                }
                
                # Ajouter les données supplémentaires comme notes
                extra_data = []
                for key, value in row_data.items():
                    if key.startswith('extra_') and value:
                        extra_data.append(f"{key}: {value}")
                
                if extra_data:
                    if client_data['notes']:
                        client_data['notes'] += ' | ' + ' | '.join(extra_data)
                    else:
                        client_data['notes'] = ' | '.join(extra_data)
                
                client_controller.add_client_raw(client_data)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors_details.append(f"Ligne {success_count + error_count}: {str(e)}")
        
        return jsonify({
            'success': True,
            'total_rows': result['total_rows'],
            'success_count': success_count,
            'error_count': error_count,
            'message': f'Import terminé: {success_count} clients importés, {error_count} erreurs',
            'errors': errors_details[:10],  # Limiter à 10 erreurs
            'original_columns': result['original_columns']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur lors de l\'import: {str(e)}'
        }), 500

@app.route('/import-excel', methods=['GET', 'POST'])
def import_excel():
    """Importer des clients depuis un fichier Excel"""
    if request.method == 'POST':
        try:
            if 'excel_file' not in request.files:
                flash('لم يتم اختيار ملف', 'error')
                return redirect(request.url)
            
            file = request.files['excel_file']
            if file.filename == '':
                flash('لم يتم اختيار ملف', 'error')
                return redirect(request.url)
            
            if file and file.filename.lower().endswith(('.xlsx', '.xls')):
                # Sauvegarder le fichier temporairement
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Importer les données
                imported_clients = excel_handler.import_from_excel(filepath)
                
                success_count = 0
                error_count = 0
                
                for client_data in imported_clients:
                    try:
                        client_controller.add_client(client_data)
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"Erreur import client {client_data.get('client_id', 'N/A')}: {e}")
                
                # Supprimer le fichier temporaire
                os.remove(filepath)
                
                flash(f'تم استيراد {success_count} عميل بنجاح! ❌ فشل في استيراد {error_count} عميل', 'success')
                return redirect(url_for('clients_list'))
            else:
                flash('يرجى اختيار ملف Excel صحيح (.xlsx أو .xls)', 'error')
                
        except Exception as e:
            flash(f'خطأ في استيراد الملف: {str(e)}', 'error')
    
    return render_template('import_excel.html')

@app.route('/api/update-status', methods=['POST'])
def update_status_api():
    """API optimisée pour mettre à jour le statut d'un client"""
    try:
        data = request.get_json()
        client_id = data.get('client_id')
        new_status = data.get('status')
        
        if not client_id or not new_status:
            return jsonify({'success': False, 'message': 'معرف العميل والحالة مطلوبان'}), 400
        
        if new_status not in Client.VISA_STATUS_OPTIONS:
            return jsonify({'success': False, 'message': 'حالة غير صحيحة'}), 400
        
        # Récupérer le client pour les notifications
        client = client_controller.get_client_by_id(client_id)
        if not client:
            return jsonify({'success': False, 'message': 'العميل غير موجود'}), 404
        
        old_status = client.get('visa_status')
        
        # Éviter les mises à jour inutiles
        if old_status == new_status:
            return jsonify({
                'success': True, 
                'message': 'الحالة لم تتغير',
                'new_status': new_status
            })
        
        # Mettre à jour le statut
        success = client_controller.update_client_status(client_id, new_status)
        
        if success:
            # Envoyer notification WhatsApp seulement si nécessaire
            notification_sent = False
            if (whatsapp_controller.is_whatsapp_enabled() and 
                client.get('whatsapp_number')):
                try:
                    whatsapp_controller.send_status_notification(
                        client_id, 
                        new_status, 
                        client.get('whatsapp_number')
                    )
                    notification_sent = True
                except Exception as e:
                    print(f"⚠️ Erreur notification WhatsApp: {e}")
            
            return jsonify({
                'success': True, 
                'message': 'تم تحديث الحالة بنجاح',
                'new_status': new_status,
                'notification_sent': notification_sent
            })
        else:
            return jsonify({'success': False, 'message': 'فشل في تحديث الحالة'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'}), 500

@app.route('/api/client/<client_id>/update-field', methods=['POST'])
def update_client_field_api(client_id):
    """API pour mise à jour en ligne des champs client"""
    try:
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        
        if not field or value is None:
            return jsonify({'success': False, 'message': 'Champ et valeur requis'}), 400
        
        # Champs autorisés pour l'édition en ligne
        allowed_fields = ['visa_status', 'responsible_employee', 'application_date', 'transaction_date']
        
        if field not in allowed_fields:
            return jsonify({'success': False, 'message': 'Champ non autorisé'}), 400
        
        # Mettre à jour le champ
        success = client_controller.update_client_field(client_id, field, value)
        
        if success:
            return jsonify({'success': True, 'message': 'Champ mis à jour avec succès'})
        else:
            return jsonify({'success': False, 'message': 'Erreur lors de la mise à jour'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

@app.route('/api/client/<client_id>/send-whatsapp', methods=['POST'])
def send_whatsapp_test_api(client_id):
    """API pour envoyer un message WhatsApp de test"""
    try:
        from src.services.whatsapp_service import whatsapp_service
        
        # Récupérer les données du client
        client = client_controller.get_client_by_id(client_id)
        if not client:
            return jsonify({'success': False, 'message': 'Client non trouvé'}), 404
        
        phone_number = client.get('whatsapp_number', '')
        if not phone_number:
            return jsonify({'success': False, 'message': 'Numéro WhatsApp non fourni'}), 400
        
        # Récupérer le statut actuel
        current_status = client.get('visa_status', 'تم التقديم في السيستام')
        
        # Envoyer le message
        result = whatsapp_service.send_visa_status_notification(
            client, '', current_status  # Pas d'ancien statut pour un test
        )
        
        if result.get('success'):
            return jsonify({
                'success': True, 
                'message': 'Message WhatsApp envoyé avec succès',
                'phone_number': phone_number,
                'status': current_status
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'Erreur envoi WhatsApp: {result.get("error", "Erreur inconnue")}'
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

@app.route('/api/check-passport-unique', methods=['POST'])
def check_passport_unique():
    """Vérifier si un numéro de passeport est unique"""
    try:
        data = request.get_json()
        passport_number = data.get('passport_number', '').strip()
        
        if not passport_number:
            return jsonify({'unique': True, 'message': 'Numéro de passeport vide'})
        
        # Vérifier l'unicité
        is_unique = db_manager.is_passport_number_unique(passport_number)
        
        return jsonify({
            'unique': is_unique,
            'message': 'Numéro de passeport unique' if is_unique else 'Numéro de passeport déjà utilisé'
        })
        
    except Exception as e:
        return jsonify({
            'unique': False,
            'message': f'Erreur lors de la vérification: {str(e)}'
        }), 500

@app.route('/api/search-instant', methods=['GET'])
def search_instant_api():
    """API pour la recherche instantanée"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term or len(search_term) < 2:
            return jsonify({'results': [], 'total': 0})
        
        # Recherche instantanée avec limite pour les performances
        clients, total = client_controller.search_clients(search_term, page=1, per_page=20)
        
        # Formater les résultats pour l'affichage instantané
        results = []
        for client in clients:
            results.append({
                'client_id': client.get('client_id', ''),
                'full_name': client.get('full_name', ''),
                'whatsapp_number': client.get('whatsapp_number', ''),
                'visa_status': client.get('visa_status', ''),
                'nationality': client.get('nationality', ''),
                'passport_number': client.get('passport_number', '')
            })
        
        return jsonify({
            'results': results,
            'total': convert_to_json_serializable(total),
            'search_term': search_term
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats_api():
    """API optimisée pour récupérer les statistiques avec cache"""
    try:
        from src.utils.cache_manager import cache_manager
        
        # Vérifier le cache d'abord
        cached_stats = cache_manager.get('dashboard_stats')
        if cached_stats is not None:
            return jsonify(cached_stats)
        
        # Calculer les statistiques si pas en cache
        all_clients, total_clients = client_controller.get_all_clients(1, 10000)  # Récupérer tous les clients
        
        stats = {
            'total_clients': convert_to_json_serializable(total_clients),  # Utiliser le total retourné par la base de données
            'by_status': {},
            'by_nationality': {},
            'by_employee': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculer les statistiques de manière optimisée
        status_counts = {}
        nationality_counts = {}
        employee_counts = {}
        
        for client in all_clients:
            # Compter par statut
            status = client.get('visa_status', '')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Compter par nationalité
            nationality = client.get('nationality', '')
            if nationality:
                nationality_counts[nationality] = nationality_counts.get(nationality, 0) + 1
            
            # Compter par employé
            employee = client.get('responsible_employee', '')
            if employee:
                employee_counts[employee] = employee_counts.get(employee, 0) + 1
        
        # Remplir les statistiques avec tous les statuts possibles
        for status in Client.VISA_STATUS_OPTIONS:
            stats['by_status'][status] = convert_to_json_serializable(status_counts.get(status, 0))
        
        for nationality in Client.NATIONALITY_OPTIONS:
            stats['by_nationality'][nationality] = convert_to_json_serializable(nationality_counts.get(nationality, 0))
        
        for employee in Client.EMPLOYEE_OPTIONS:
            stats['by_employee'][employee] = convert_to_json_serializable(employee_counts.get(employee, 0))
        
        # Mettre en cache pour 3 minutes
        cache_manager.set('dashboard_stats', stats, ttl=180)
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart-data')
def get_chart_data_api():
    """API optimisée pour récupérer les données du graphique avec cache"""
    try:
        from src.utils.cache_manager import cache_manager
        
        # Vérifier le cache d'abord
        cached_chart_data = cache_manager.get('chart_data')
        if cached_chart_data is not None:
            return jsonify(cached_chart_data)
        
        # Calculer les données si pas en cache
        all_clients, _ = client_controller.get_all_clients(1, 10000)  # Récupérer tous les clients
        
        # Calculer les données pour le graphique de manière optimisée
        chart_data = {
            'labels': [],
            'values': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Compter les clients par statut en une seule passe
        status_counts = {}
        for client in all_clients:
            status = client.get('visa_status', '')
            if status:
                status_counts[status] = status_counts.get(status, 0) + 1
        
        # Ne montrer que les statuts avec des clients (> 0)
        filtered_counts = {k: v for k, v in status_counts.items() if v > 0}
        
        # Préparer les données pour Chart.js
        chart_data['labels'] = list(filtered_counts.keys())
        chart_data['values'] = [convert_to_json_serializable(v) for v in filtered_counts.values()]
        
        # Mettre en cache pour 3 minutes
        cache_manager.set('chart_data', chart_data, ttl=180)
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/unrestricted-import', methods=['POST'])
def unrestricted_import_api():
    """API pour l'analyse et l'import sans restrictions"""
    try:
        # Importer les modules nécessaires
        from src.utils.advanced_excel_analyzer import AdvancedExcelAnalyzer
        from src.utils.unrestricted_importer import UnrestrictedImporter
        
        if 'excel_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'لم يتم اختيار ملف Excel'
            }), 400
        
        file = request.files['excel_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'لم يتم اختيار ملف صحيح'
            }), 400
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'error': 'يرجى اختيار ملف Excel صحيح (.xlsx أو .xls)'
            }), 400
        
        # Sauvegarder le fichier temporairement avec timestamp unique
        import time
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Créer l'importeur sans restrictions
            importer = UnrestrictedImporter(db_manager.db_path)
            
            # Effectuer l'import complet
            result = importer.perform_unrestricted_import(filepath)
            
            # Supprimer le fichier temporaire
            os.remove(filepath)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'analysis_report': result['analysis_report'],
                    'import_stats': result['import_stats'],
                    'final_report_html': result['final_report']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'خطأ غير محدد'),
                    'import_stats': result.get('import_stats', {})
                }), 500
                
        except Exception as e:
            # Supprimer le fichier en cas d'erreur
            if os.path.exists(filepath):
                os.remove(filepath)
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في المعالجة: {str(e)}'
        }), 500

@app.route('/unrestricted-import', endpoint='unrestricted_import_page')
def unrestricted_import_page():
    """صفحة الاستيراد الشامل بدون قيود"""
    return render_template('unrestricted_import.html')

@app.route('/delete-all-clients', methods=['GET', 'POST'])
def delete_all_clients():
    """Supprimer tous les clients avec confirmation"""
    if request.method == 'POST':
        try:
            # Vérifier la confirmation
            confirmation = request.form.get('confirmation', '').strip()
            if confirmation != 'DELETE_ALL_CLIENTS':
                flash('يرجى كتابة "DELETE_ALL_CLIENTS" للتأكيد', 'error')
                return render_template('delete_all_clients.html')
            
            # Compter les clients avant suppression
            clients_before_list, clients_before_total = client_controller.get_all_clients(page=1, per_page=5000)
            clients_before = clients_before_total
            
            # Supprimer tous les clients
            db_manager.delete_all_clients()
            
            flash(f'تم حذف جميع العملاء بنجاح! ({clients_before} عميل) ✅', 'success')
            return redirect(url_for('clients_list'))
            
        except Exception as e:
            flash(f'خطأ في حذف العملاء: {str(e)}', 'error')
    
    # GET request - afficher la page de confirmation
    clients_list, total_clients = client_controller.get_all_clients(page=1, per_page=5000)
    return render_template('delete_all_clients.html', total_clients=total_clients)

@app.route('/delete-all-clients-direct', methods=['POST'])
def delete_all_clients_direct():
    """Supprimer tous les clients sans confirmation - MODE DANGEREUX"""
    try:
        # Compter les clients avant suppression
        clients_before_list, clients_before_total = client_controller.get_all_clients(page=1, per_page=5000)
        clients_before = clients_before_total
        
        # Supprimer tous les clients immédiatement
        db_manager.delete_all_clients()
        
        flash(f'⚡ حذف مباشر: تم حذف جميع العملاء! ({clients_before} عميل) ✅', 'success')
        return redirect(url_for('clients_list'))
        
    except Exception as e:
        flash(f'خطأ في الحذف المباشر: {str(e)}', 'error')
        return redirect(url_for('clients_list'))

@app.route('/send_whatsapp/<client_id>')
def send_whatsapp(client_id):
    """Page d'envoi de message WhatsApp pour un client"""
    try:
        # Générer le message WhatsApp personnalisé
        message_data = client_controller.generate_whatsapp_message(client_id)
        
        if not message_data['success']:
            flash(f'خطأ: {message_data["error"]}', 'error')
            return redirect(url_for('clients_list'))
        
        # Encoder le message pour l'URL WhatsApp
        encoded_message = urllib.parse.quote(message_data['message'])
        
        # Générer le lien WhatsApp
        phone_number = message_data['phone_number']
        if phone_number:
            # Nettoyer le numéro de téléphone (supprimer espaces, tirets, etc.)
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_message}"
        else:
            # Si pas de numéro, utiliser WhatsApp Web général
            whatsapp_url = f"https://web.whatsapp.com/send?text={encoded_message}"
        
        return render_template('send_whatsapp.html', 
                             client=message_data,
                             whatsapp_url=whatsapp_url,
                             message=message_data['message'])
        
    except Exception as e:
        flash(f'خطأ في إنشاء رسالة WhatsApp: {str(e)}', 'error')
        return redirect(url_for('clients_list'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Page des paramètres"""
    if request.method == 'POST':
        try:
            # Mettre à jour les paramètres WhatsApp
            whatsapp_enabled = request.form.get('whatsapp_enabled') == 'on'
            facebook_link = request.form.get('facebook_link', '').strip()
            
            whatsapp_controller.enable_whatsapp(whatsapp_enabled)
            if facebook_link:
                whatsapp_controller.update_facebook_link(facebook_link)
            
            flash('تم حفظ الإعدادات بنجاح! ✅', 'success')
            
        except Exception as e:
            flash(f'خطأ في حفظ الإعدادات: {str(e)}', 'error')
    
    # Récupérer les paramètres actuels
    current_settings = {
        'whatsapp_enabled': whatsapp_controller.is_whatsapp_enabled(),
        'facebook_link': whatsapp_controller.facebook_link
    }
    
    return render_template('settings.html', settings=current_settings)

# Routes pour l'analyse avancée
@app.route('/analytics')
def analytics_dashboard():
    """Tableau de bord d'analyse avancée"""
    try:
        # Obtenir l'analyse complète
        analysis_data = analytics_controller.get_comprehensive_dashboard_data()
        
        return render_template('analytics.html', analysis=analysis_data)
        
    except Exception as e:
        flash(f'خطأ في تحميل التحليل المتقدم: {str(e)}', 'error')
        return render_template('analytics.html', analysis={})

@app.route('/api/analytics/comprehensive')
def get_comprehensive_analytics_api():
    """API pour obtenir l'analyse complète"""
    try:
        data = analytics_controller.get_comprehensive_dashboard_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/executive-report')
def get_executive_report_api():
    """API pour obtenir le rapport exécutif"""
    try:
        data = analytics_controller.get_executive_report()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/operational-dashboard')
def get_operational_dashboard_api():
    """API pour obtenir le tableau de bord opérationnel"""
    try:
        data = analytics_controller.get_operational_dashboard()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/real-time-stats')
def get_real_time_stats_api():
    """API pour obtenir les statistiques en temps réel"""
    try:
        data = analytics_controller.get_real_time_stats()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/chart-data/<chart_type>')
def get_analytics_chart_data_api(chart_type):
    """API pour obtenir les données des graphiques"""
    try:
        data = analytics_controller.get_chart_data(chart_type)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export/excel')
def export_clients_excel():
    """Exporter la liste des clients vers Excel"""
    try:
        print(f"🎯 EXPORT EXCEL: Début de l'export")
        
        # Récupérer les paramètres de filtrage
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        nationality = request.args.get('nationality', '')
        employee = request.args.get('employee', '')
        
        print(f"🎯 EXPORT EXCEL: Filtres - search: '{search}', status: '{status}', nationality: '{nationality}', employee: '{employee}'")
        
        # Obtenir tous les clients avec les filtres
        page = 1
        per_page = 10000  # Récupérer beaucoup de clients pour l'export
        
        # Construire les filtres
        filters = {}
        if search:
            filters['search'] = search
        if status:
            filters['status'] = status
        if nationality:
            filters['nationality'] = nationality
        if employee:
            filters['employee'] = employee
        
        print(f"🎯 EXPORT EXCEL: Appel du contrôleur avec filtres: {filters}")
        
        # Récupérer les clients filtrés
        clients_data, total_clients = client_controller.get_filtered_clients(
            filters=filters,
            page=page, 
            per_page=per_page
        )
        
        print(f"🎯 EXPORT EXCEL: Clients récupérés: {len(clients_data)}, Total: {total_clients}")
        
        if not clients_data:
            print("🎯 EXPORT EXCEL: Aucun client à exporter")
            return jsonify({'error': 'Aucun client à exporter'}), 404
        
        # Préparer les données pour l'export
        export_data = []
        for client in clients_data:
            export_data.append({
                'معرف العميل': client.get('client_id', ''),
                'الاسم الكامل': client.get('full_name', ''),
                'رقم الواتساب': client.get('whatsapp_number', ''),
                'تاريخ التقديم': client.get('application_date', ''),
                'تاريخ استلام للسفارة': client.get('transaction_date', ''),
                'رقم جواز السفر': client.get('passport_number', ''),
                'حالة جواز السفر': client.get('passport_status', ''),
                'الجنسية': client.get('nationality', ''),
                'حالة تتبع التأشيرة': client.get('visa_status', ''),
                'من طرف': client.get('processed_by', ''),
                'الخلاصة': client.get('summary', ''),
                'ملاحظة': client.get('notes', ''),
                'اختيار الموظف': client.get('responsible_employee', ''),
                'تاريخ الإنشاء': client.get('created_at', ''),
                'تاريخ التحديث': client.get('updated_at', '')
            })
        
        print(f"🎯 EXPORT EXCEL: Données préparées pour l'export: {len(export_data)} lignes")
        
        # Créer le fichier Excel
        excel_handler = ExcelHandler()
        
        # Générer un nom de fichier unique
        filename = f'clients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        filepath = os.path.join('uploads', filename)
        
        # S'assurer que le dossier uploads existe
        os.makedirs('uploads', exist_ok=True)
        
        print(f"🎯 EXPORT EXCEL: Export vers fichier: {filepath}")
        
        # Exporter vers Excel
        success = excel_handler.export_to_excel(export_data, filepath)
        
        print(f"🎯 EXPORT EXCEL: Succès de l'export: {success}")
        
        if success and os.path.exists(filepath):
            print(f"🎯 EXPORT EXCEL: Envoi du fichier à l'utilisateur")
            # Envoyer le fichier à l'utilisateur
            response = send_file(filepath, 
                               as_attachment=True, 
                               download_name=filename,
                               mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            print(f"🎯 EXPORT EXCEL: Fichier envoyé avec succès")
            return response
        else:
            print(f"🎯 EXPORT EXCEL: Erreur - fichier non créé")
            return jsonify({'error': 'Erreur lors de la création du fichier Excel'}), 500
            
    except Exception as e:
        print(f"🎯 EXPORT EXCEL: Exception capturée: {str(e)}")
        return jsonify({'error': f'Erreur lors de l\'export: {str(e)}'}), 500

@app.route('/api/analytics/export/<report_type>')
def export_analysis_report_api(report_type):
    """API pour exporter un rapport d'analyse"""
    try:
        data = analytics_controller.export_analysis_report(report_type)
        
        # Créer la réponse avec les en-têtes appropriés
        response = make_response(jsonify(data))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=analysis_report_{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🛂 نظام تتبع التأشيرات الذكي - TCA")
    print("شركة تونس للاستشارات والخدمات")
    print("\n🌐 Démarrage du serveur web...")
    print("📱 Interface web disponible sur: http://localhost:5005")
    print("\n⚡ Serveur en cours d'exécution...")
    
    app.run(debug=True, host='0.0.0.0', port=5005)
