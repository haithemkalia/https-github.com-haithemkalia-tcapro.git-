#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test direct de la route Flask avec logs de débogage
"""

import sys
from pathlib import Path
from flask import Flask, render_template, request

# Ajouter le dossier src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_route_direct():
    """Tester directement la route Flask avec logs"""
    print("🔧 TEST DIRECT DE LA ROUTE FLASK")
    print("=" * 60)
    
    try:
        from database.database_manager import DatabaseManager
        from controllers.client_controller import ClientController
        from models.client import Client
        
        # Créer une app Flask temporaire
        app = Flask(__name__)
        app.secret_key = 'test_key'
        
        # Configuration pour les templates RTL
        @app.context_processor
        def inject_rtl_support():
            from datetime import datetime
            return {
                'rtl_support': True,
                'app_title': '🛂 نظام تتبع التأشيرات الذكي - TCA',
                'company_name': 'شركة تونس للاستشارات والخدمات',
                'facebook_link': 'https://www.facebook.com/share/1D4dHp2z74/?mibextid=wwXIfr',
                'current_datetime': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        
        # Initialiser les contrôleurs
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        
        print("✅ App Flask et contrôleurs initialisés")
        
        # Créer une route de test qui reproduit exactement la logique de app.py
        @app.route('/test_clients')
        def test_clients_list():
            """Route de test qui reproduit clients_list"""
            print("\n🔍 DÉBUT DE LA ROUTE /test_clients")
            
            try:
                # Paramètres de pagination
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 50))
                
                print(f"📋 Paramètres: page={page}, per_page={per_page}")
                
                # Paramètres de filtrage
                search_term = request.args.get('search', '')
                status_filter = request.args.get('status', '')
                nationality_filter = request.args.get('nationality', '')
                employee_filter = request.args.get('employee', '')
                
                print(f"🔍 Filtres: search='{search_term}', status='{status_filter}', nationality='{nationality_filter}', employee='{employee_filter}'")
                
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
                
                print(f"🔧 Filtres construits: {filters}")
                
                # Récupérer les clients avec pagination
                print("📊 Récupération des clients...")
                if filters:
                    print("   Utilisation de get_filtered_clients")
                    clients, total = client_controller.get_filtered_clients(filters, page, per_page)
                else:
                    print("   Utilisation de get_all_clients")
                    clients, total = client_controller.get_all_clients(page, per_page)
                
                print(f"📈 Résultats: {len(clients)} clients récupérés, total: {total}")
                print(f"📈 Type de clients: {type(clients)}")
                
                if clients:
                    print(f"👤 Premier client: {clients[0]}")
                else:
                    print("❌ Liste de clients vide")
                
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
                
                print(f"📄 Pagination: {pagination}")
                
                # Préparer le contexte du template
                template_context = {
                    'clients': clients,
                    'pagination': pagination,
                    'search_term': search_term,
                    'status_filter': status_filter,
                    'nationality_filter': nationality_filter,
                    'employee_filter': employee_filter,
                    'visa_statuses': Client.VISA_STATUS_OPTIONS,
                    'nationalities': Client.NATIONALITY_OPTIONS,
                    'employees': Client.EMPLOYEE_OPTIONS
                }
                
                print(f"🎨 Contexte du template:")
                print(f"   - clients: {len(template_context['clients'])} éléments")
                print(f"   - pagination total: {template_context['pagination']['total']}")
                print(f"   - visa_statuses: {len(template_context['visa_statuses'])} options")
                print(f"   - nationalities: {len(template_context['nationalities'])} options")
                print(f"   - employees: {len(template_context['employees'])} options")
                
                # Vérifier que les options ne sont pas vides
                if not template_context['visa_statuses']:
                    print("⚠️  ATTENTION: visa_statuses est vide!")
                if not template_context['nationalities']:
                    print("⚠️  ATTENTION: nationalities est vide!")
                if not template_context['employees']:
                    print("⚠️  ATTENTION: employees est vide!")
                
                print("🎨 Rendu du template...")
                
                # Rendre le template
                html_result = render_template('clients.html', **template_context)
                
                print(f"✅ Template rendu avec succès: {len(html_result)} caractères")
                
                # Vérifier le contenu du HTML
                if clients and len(clients) > 0:
                    first_client = clients[0]
                    client_id = first_client.get('client_id', '')
                    if client_id in html_result:
                        print(f"✅ Client ID '{client_id}' trouvé dans le HTML")
                    else:
                        print(f"❌ Client ID '{client_id}' NON trouvé dans le HTML")
                
                return html_result
                
            except Exception as route_error:
                print(f"❌ Erreur dans la route: {route_error}")
                import traceback
                traceback.print_exc()
                return f"Erreur: {route_error}", 500
        
        # Tester la route avec un contexte de requête
        with app.test_request_context('/test_clients'):
            result = test_clients_list()
            
            if isinstance(result, tuple):
                print(f"❌ Erreur retournée: {result}")
                return False
            else:
                print(f"✅ Route exécutée avec succès")
                return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    success = test_route_direct()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST RÉUSSI")
        print("🎯 La route Flask fonctionne correctement")
    else:
        print("❌ TEST ÉCHOUÉ")
        print("🔧 Il y a un problème dans la route Flask")

if __name__ == "__main__":
    main()