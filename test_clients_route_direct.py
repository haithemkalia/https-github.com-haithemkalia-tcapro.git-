#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test direct de la route /clients pour identifier le problème exact
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from src.controllers.client_controller import ClientController
from src.database.database_manager import DatabaseManager
from src.models.client import Client

def test_clients_route_step_by_step():
    """Tester la route /clients étape par étape"""
    
    print("🔍 TEST DIRECT DE LA ROUTE /clients")
    print("="*60)
    
    try:
        with app.test_client() as test_client:
            with app.app_context():
                print("\n1️⃣ Initialisation des contrôleurs...")
                
                # Initialiser les contrôleurs comme dans app.py
                db_manager = DatabaseManager()
                controller = ClientController(db_manager)
                
                print("   ✅ Contrôleurs initialisés")
                
                print("\n2️⃣ Test des paramètres de requête...")
                
                # Simuler les paramètres par défaut
                page = 1
                per_page = 50
                search_term = ''
                status_filter = ''
                nationality_filter = ''
                employee_filter = ''
                
                print(f"   📊 Paramètres: page={page}, per_page={per_page}")
                print(f"   🔍 Filtres: search='{search_term}', status='{status_filter}'")
                print(f"   🔍 Filtres: nationality='{nationality_filter}', employee='{employee_filter}'")
                
                print("\n3️⃣ Construction des filtres...")
                
                # Construire les filtres comme dans la route
                filters = {}
                if search_term:
                    filters['search'] = search_term
                if status_filter and status_filter in Client.VISA_STATUS_OPTIONS:
                    filters['visa_status'] = status_filter
                if nationality_filter and nationality_filter in Client.NATIONALITY_OPTIONS:
                    filters['nationality'] = nationality_filter
                if employee_filter and employee_filter in Client.EMPLOYEE_OPTIONS:
                    filters['responsible_employee'] = employee_filter
                
                print(f"   🔧 Filtres construits: {filters}")
                
                print("\n4️⃣ Récupération des clients...")
                
                # Récupérer les clients comme dans la route
                if filters:
                    print("   🔍 Utilisation de get_filtered_clients...")
                    clients, total = controller.get_filtered_clients(filters, page, per_page)
                else:
                    print("   📋 Utilisation de get_all_clients...")
                    clients, total = controller.get_all_clients(page, per_page)
                
                print(f"   ✅ Résultat: {len(clients)} clients récupérés, total: {total}")
                
                if clients:
                    print(f"   📋 Premier client: ID={clients[0].get('client_id')}, Nom={clients[0].get('full_name')}")
                    print(f"   📋 Type des clients: {type(clients)}")
                    print(f"   📋 Type du premier élément: {type(clients[0])}")
                else:
                    print("   ❌ Aucun client récupéré")
                
                print("\n5️⃣ Calcul de la pagination...")
                
                # Calculer la pagination comme dans la route
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
                
                print(f"   ✅ Pagination: {pagination}")
                
                print("\n6️⃣ Vérification des options...")
                
                # Vérifier les options comme dans la route
                try:
                    visa_statuses = Client.VISA_STATUS_OPTIONS
                    nationalities = Client.NATIONALITY_OPTIONS
                    employees = Client.EMPLOYEE_OPTIONS
                    
                    print(f"   ✅ Visa statuses: {len(visa_statuses)} options")
                    print(f"   ✅ Nationalities: {len(nationalities)} options")
                    print(f"   ✅ Employees: {len(employees)} options")
                except Exception as e:
                    print(f"   ❌ Erreur options: {e}")
                
                print("\n7️⃣ Test de la requête HTTP réelle...")
                
                # Faire une vraie requête HTTP
                response = test_client.get('/clients')
                
                print(f"   📊 Status Code: {response.status_code}")
                print(f"   📊 Content-Type: {response.content_type}")
                print(f"   📊 Content-Length: {len(response.data)} bytes")
                
                if response.status_code == 200:
                    html_content = response.data.decode('utf-8')
                    
                    # Vérifier les patterns critiques
                    patterns = [
                        ('CLI0', 'IDs clients'),
                        ('النتائج: 0 عميل', 'Résultats zéro'),
                        (f'النتائج: {total} عميل', 'Résultats corrects'),
                        ('لا توجد نتائج', 'Message aucun résultat'),
                        ('لا توجد عملاء', 'Message aucun client')
                    ]
                    
                    print(f"\n   🔍 Analyse du HTML:")
                    for pattern, description in patterns:
                        if pattern in html_content:
                            print(f"   ✅ {description}: trouvé")
                        else:
                            print(f"   ❌ {description}: non trouvé")
                    
                    # Extraire la ligne des résultats
                    import re
                    results_match = re.search(r'النتائج: (\d+) عميل', html_content)
                    if results_match:
                        displayed_count = results_match.group(1)
                        print(f"   📊 Nombre affiché dans l'interface: {displayed_count}")
                        print(f"   📊 Nombre réel récupéré: {total}")
                        
                        if displayed_count != str(total):
                            print(f"   ⚠️  PROBLÈME: Incohérence entre les données !")
                        else:
                            print(f"   ✅ Cohérence des données")
                    
                else:
                    print(f"   ❌ Erreur HTTP: {response.status_code}")
                
                print("\n8️⃣ Test avec des paramètres spécifiques...")
                
                # Tester avec des paramètres de requête
                response_with_params = test_client.get('/clients?page=1&per_page=10')
                print(f"   📊 Status avec paramètres: {response_with_params.status_code}")
                
                if response_with_params.status_code == 200:
                    html_with_params = response_with_params.data.decode('utf-8')
                    results_match_params = re.search(r'النتائج: (\d+) عميل', html_with_params)
                    if results_match_params:
                        displayed_count_params = results_match_params.group(1)
                        print(f"   📊 Nombre affiché avec paramètres: {displayed_count_params}")
        
        print("\n" + "="*60)
        print("🏁 TEST TERMINÉ")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clients_route_step_by_step()