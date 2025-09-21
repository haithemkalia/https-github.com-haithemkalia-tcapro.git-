#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug complet de la route /clients
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from src.controllers.client_controller import ClientController
from src.database.database_manager import DatabaseManager
from flask import request

def debug_clients_route_complete():
    """Debug complet de la route /clients"""
    
    print("🔍 DEBUG COMPLET DE LA ROUTE /clients")
    print("="*70)
    
    try:
        # Test 1: Vérifier le contrôleur directement
        print("\n1️⃣ Test du contrôleur ClientController...")
        db_manager = DatabaseManager()
        controller = ClientController(db_manager)
        
        # Test get_all_clients
        clients, total = controller.get_all_clients(page=1, per_page=50)
        print(f"   ✅ get_all_clients() retourne: {len(clients)} clients, total: {total}")
        
        if clients:
            print(f"   📋 Premier client: ID={clients[0].get('client_id')}, Nom={clients[0].get('full_name')}")
        
        # Test 2: Simuler la route Flask avec tous les paramètres
        print("\n2️⃣ Simulation complète de la route Flask...")
        
        with app.test_client() as client:
            with app.app_context():
                # Simuler les paramètres de requête
                page = 1
                per_page = 50
                search_query = ''
                nationality_filter = ''
                visa_status_filter = ''
                employee_filter = ''
                
                print(f"   📊 Paramètres: page={page}, per_page={per_page}")
                print(f"   🔍 Filtres: search='{search_query}', nationality='{nationality_filter}'")
                print(f"   🔍 Filtres: visa_status='{visa_status_filter}', employee='{employee_filter}'")
                
                # Recréer la logique de la route
                db_manager = DatabaseManager()
                controller = ClientController(db_manager)
                
                # Construire les filtres
                filters = {}
                if search_query:
                    filters['search'] = search_query
                if nationality_filter:
                    filters['nationality'] = nationality_filter
                if visa_status_filter:
                    filters['visa_status'] = visa_status_filter
                if employee_filter:
                    filters['employee'] = employee_filter
                
                print(f"   🔧 Filtres construits: {filters}")
                
                # Appeler get_filtered_clients
                if filters:
                    print("   🔍 Utilisation de get_filtered_clients...")
                    clients, total_count = controller.get_filtered_clients(filters, page, per_page)
                else:
                    print("   📋 Utilisation de get_all_clients...")
                    clients, total_count = controller.get_all_clients(page, per_page)
                
                print(f"   ✅ Résultat: {len(clients)} clients récupérés, total: {total_count}")
                
                # Vérifier le type et le contenu des clients
                print(f"\n3️⃣ Analyse des données clients...")
                print(f"   📊 Type de 'clients': {type(clients)}")
                print(f"   📊 Longueur: {len(clients)}")
                
                if clients:
                    print(f"   📋 Type du premier élément: {type(clients[0])}")
                    print(f"   📋 Clés du premier client: {list(clients[0].keys()) if isinstance(clients[0], dict) else 'N/A'}")
                    print(f"   📋 Premier client: {clients[0]}")
                    
                    # Vérifier si les clients ont les bonnes clés
                    required_keys = ['client_id', 'full_name', 'whatsapp_number']
                    for key in required_keys:
                        if key in clients[0]:
                            print(f"   ✅ Clé '{key}': présente")
                        else:
                            print(f"   ❌ Clé '{key}': MANQUANTE")
                else:
                    print(f"   ❌ Aucun client dans la liste")
                
                # Test 4: Calculer la pagination
                print(f"\n4️⃣ Calcul de la pagination...")
                total_pages = (total_count + per_page - 1) // per_page
                has_prev = page > 1
                has_next = page < total_pages
                prev_num = page - 1 if has_prev else None
                next_num = page + 1 if has_next else None
                
                pagination = {
                    'page': page,
                    'per_page': per_page,
                    'total': total_count,
                    'total_pages': total_pages,
                    'has_prev': has_prev,
                    'has_next': has_next,
                    'prev_num': prev_num,
                    'next_num': next_num
                }
                
                print(f"   ✅ Pagination: {pagination}")
                
                # Test 5: Vérifier les statuts de visa
                print(f"\n5️⃣ Récupération des statuts de visa...")
                visa_statuses = controller.get_visa_statuses()
                print(f"   ✅ Statuts de visa: {len(visa_statuses)} éléments")
                print(f"   📋 Statuts: {visa_statuses}")
                
                # Test 6: Faire une vraie requête HTTP
                print(f"\n6️⃣ Test de la requête HTTP réelle...")
                response = client.get('/clients')
                print(f"   📊 Status Code: {response.status_code}")
                print(f"   📊 Content-Type: {response.content_type}")
                print(f"   📊 Content-Length: {len(response.data)} bytes")
                
                if response.status_code == 200:
                    html_content = response.data.decode('utf-8')
                    
                    # Rechercher des patterns critiques
                    patterns_to_check = [
                        ('CLI0', 'IDs clients'),
                        ('لا توجد نتائج', 'Message aucun résultat'),
                        ('لا توجد عملاء', 'Message aucun client'),
                        ('{% if clients %}', 'Condition template brute'),
                        ('if clients', 'Condition template rendue'),
                        ('<tbody>', 'Corps du tableau'),
                        ('clientsTable', 'ID du tableau'),
                        ('pagination', 'Section pagination')
                    ]
                    
                    print(f"\n   🔍 Analyse du HTML généré:")
                    for pattern, description in patterns_to_check:
                        count = html_content.count(pattern)
                        if count > 0:
                            print(f"   ✅ {description}: {count} occurrence(s)")
                        else:
                            print(f"   ❌ {description}: non trouvé")
                    
                    # Sauvegarder le HTML complet
                    with open('full_html_debug.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"   💾 HTML complet sauvegardé dans 'full_html_debug.html'")
                    
                    # Extraire la section critique
                    start_marker = '<!-- Results Section -->'
                    end_marker = '<!-- End Results Section -->'
                    
                    if start_marker in html_content and end_marker in html_content:
                        start_idx = html_content.find(start_marker)
                        end_idx = html_content.find(end_marker) + len(end_marker)
                        results_section = html_content[start_idx:end_idx]
                        
                        with open('results_section_debug.html', 'w', encoding='utf-8') as f:
                            f.write(results_section)
                        print(f"   💾 Section résultats sauvegardée dans 'results_section_debug.html'")
                    else:
                        print(f"   ⚠️  Marqueurs de section résultats non trouvés")
                
        print("\n" + "="*70)
        print("🏁 DEBUG TERMINÉ")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_clients_route_complete()