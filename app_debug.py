#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛂 نظام تتبع التأشيرات الذكي - TCA
شركة تونس للاستشارات والخدمات

Application Web Flask pour la gestion des visas
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import urllib.parse

# Ajouter le dossier src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.database_manager import DatabaseManager
from controllers.client_controller import ClientController
from controllers.whatsapp_controller import WhatsAppController
from utils.excel_handler import ExcelHandler
from models.client import Client

# Configuration de l'application Flask
app = Flask(__name__)
app.secret_key = 'tca_visa_tracking_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Créer le dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialiser les contrôleurs
db_manager = DatabaseManager()
client_controller = ClientController(db_manager)
whatsapp_controller = WhatsAppController(db_manager)
excel_handler = ExcelHandler()

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

# Routes principales
@app.route('/')
def index():
    """Page d'accueil avec tableau de bord"""
    try:
        # Récupérer les statistiques
        all_clients, total_count = client_controller.get_all_clients(page=1, per_page=1000)
        
        stats = {
            'total_clients': total_count,
            'by_status': {},
            'by_nationality': {},
            'by_employee': {},
            'recent_clients': all_clients[:5] if all_clients else []
        }
        
        # Calculer les statistiques par statut
        for status in Client.VISA_STATUS_OPTIONS:
            count = len([c for c in all_clients if c.get('visa_status') == status])
            stats['by_status'][status] = count
        
        # Calculer les statistiques par nationalité
        for nationality in Client.NATIONALITY_OPTIONS:
            count = len([c for c in all_clients if c.get('nationality') == nationality])
            stats['by_nationality'][nationality] = count
        
        # Calculer les statistiques par employé
        for employee in Client.EMPLOYEE_OPTIONS:
            count = len([c for c in all_clients if c.get('responsible_employee') == employee])
            stats['by_employee'][employee] = count
        
        return render_template('index.html', stats=stats, clients=all_clients)
        
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

@app.route('/clients')
def clients_list():
    """Page de liste des clients avec pagination"""
        print("🔍 DEBUG: Début de clients_list()")
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
        
        print(f"🔍 DEBUG: Filtres construits: {filters}")
        print(f"🔍 DEBUG: Paramètres: page={page}, per_page={per_page}")
        
        # Récupérer les clients avec pagination
        if filters:
            clients, total = client_controller.get_filtered_clients(filters, page, per_page)
            print(f"🔍 DEBUG: get_filtered_clients retourne: {len(clients)} clients, total={total}")
            if clients:
                print(f"🔍 DEBUG: Premier client filtré: {clients[0].get('client_id')}")
        else:
            clients, total = client_controller.get_all_clients(page, per_page)
            print(f"🔍 DEBUG: get_all_clients retourne: {len(clients)} clients, total={total}")
            if clients:
                print(f"🔍 DEBUG: Premier client: {clients[0].get('client_id')}")
        
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
        
        print(f"🔍 DEBUG: Avant render_template - clients: {len(clients)}, total: {total}")
        print(f"🔍 DEBUG: Pagination: {pagination}")
        
        return render_template('clients.html', 
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
        flash(f'خطأ في تحميل قائمة العملاء: {str(e)}', 'error')
        return render_template('clients.html', clients=[], pagination={'page': 1, 'total': 0, 'total_pages': 0})

@app.route('/client/add', methods=['GET', 'POST'])
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
                'receipt_date': request.form.get('receipt_date', '').strip(),
                'passport_number': request.form.get('passport_number', '').strip(),
                'passport_status': request.form.get('passport_status', '').strip(),
                'nationality': request.form.get('nationality', '').strip(),
                'visa_status': request.form.get('visa_status', 'التقديم').strip(),
                'processed_by': request.form.get('processed_by', '').strip(),
                'summary': request.form.get('summary', '').strip(),
                'notes': request.form.get('notes', '').strip(),
                'responsible_employee': request.form.get('responsible_employee', '').strip()
            }
            
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
                'receipt_date': request.form.get('receipt_date', '').strip(),
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
    """Supprimer un client"""
    try:
        success = client_controller.delete_client(client_id)
        if success:
            flash('تم حذف العميل بنجاح! ✅', 'success')
        else:
            flash('فشل في حذف العميل', 'error')
    except Exception as e:
        flash(f'خطأ في حذف العميل: {str(e)}', 'error')
    
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
                    'application_date': safe_str(row_data.get('application_date')),
                    'receipt_date': safe_str(row_data.get('receipt_date')),
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
        all_clients, _ = client_controller.get_all_clients(1, 10000)  # Récupérer tous les clients
        
        stats = {
            'total_clients': len(all_clients),
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
            stats['by_status'][status] = status_counts.get(status, 0)
        
        for nationality in Client.NATIONALITY_OPTIONS:
            stats['by_nationality'][nationality] = nationality_counts.get(nationality, 0)
        
        for employee in Client.EMPLOYEE_OPTIONS:
            stats['by_employee'][employee] = employee_counts.get(employee, 0)
        
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
        chart_data['values'] = list(filtered_counts.values())
        
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
            clients_before_list, clients_before_total = client_controller.get_all_clients(page=1, per_page=10000)
            clients_before = clients_before_total
            
            # Supprimer tous les clients
            db_manager.delete_all_clients()
            
            flash(f'تم حذف جميع العملاء بنجاح! ({clients_before} عميل) ✅', 'success')
            return redirect(url_for('clients_list'))
            
        except Exception as e:
            flash(f'خطأ في حذف العملاء: {str(e)}', 'error')
    
    # GET request - afficher la page de confirmation
    clients_list, total_clients = client_controller.get_all_clients(page=1, per_page=10000)
    return render_template('delete_all_clients.html', total_clients=total_clients)

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

if __name__ == '__main__':
    print("🛂 نظام تتبع التأشيرات الذكي - TCA")
    print("شركة تونس للاستشارات والخدمات")
    print("\n🌐 Démarrage du serveur web...")
    print("📱 Interface web disponible sur: http://localhost:5000")
    print("\n⚡ Serveur en cours d'exécution...")
    
    app.run(debug=True, host='0.0.0.0', port=5000)