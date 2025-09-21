#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug spécifique de la route /clients pour comprendre pourquoi aucun client ne s'affiche
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers.client_controller import ClientController
from src.database.database_manager import DatabaseManager
from src.models.client import Client
from flask import Flask, request

def debug_clients_route():
    """Déboguer la route /clients étape par étape"""
    
    print("🔍 Debug de la route /clients...")
    print("="*60)
    
    try:
        # Simuler les paramètres de la route
        page = 1
        per_page = 50
        search_term = ''
        status_filter = ''
        nationality_filter = ''
        employee_filter = ''
        
        print(f"\n📋 Paramètres de la route:")
        print(f"   - page: {page}")
        print(f"   - per_page: {per_page}")
        print(f"   - search_term: '{search_term}'")
        print(f"   - status_filter: '{status_filter}'")
        print(f"   - nationality_filter: '{nationality_filter}'")
        print(f"   - employee_filter: '{employee_filter}'")
        
        # Initialiser le contrôleur
        print(f"\n🔧 Initialisation du contrôleur...")
        db_manager = DatabaseManager()
        client_controller = ClientController(db_manager)
        print(f"   ✅ ClientController initialisé")
        
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
        
        print(f"\n🔍 Filtres construits: {filters}")
        
        # Récupérer les clients
        print(f"\n📊 Récupération des clients...")
        if filters:
            print(f"   🔍 Utilisation de get_filtered_clients()")
            clients, total = client_controller.get_filtered_clients(filters, page, per_page)
        else:
            print(f"   📋 Utilisation de get_all_clients()")
            clients, total = client_controller.get_all_clients(page, per_page)
        
        print(f"   ✅ Clients récupérés: {len(clients)}")
        print(f"   ✅ Total: {total}")
        
        # Afficher quelques exemples
        if clients:
            print(f"\n📋 Exemples de clients récupérés:")
            for i, client in enumerate(clients[:5]):
                print(f"      {i+1}. Type: {type(client)}")
                print(f"         ID: {client.get('client_id', 'N/A')}")
                print(f"         Nom: {client.get('full_name', 'N/A')}")
                print(f"         Clés: {list(client.keys())[:10]}...")
        else:
            print(f"   ❌ Aucun client dans la liste")
        
        # Calculer les informations de pagination
        print(f"\n📄 Calcul de la pagination...")
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
        
        # Simuler le rendu du template
        print(f"\n🎨 Simulation du rendu du template...")
        template_vars = {
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
        
        print(f"   📋 Variables du template:")
        print(f"      - clients: {len(template_vars['clients'])} éléments")
        print(f"      - pagination.total: {template_vars['pagination']['total']}")
        print(f"      - visa_statuses: {len(template_vars['visa_statuses'])} options")
        
        # Test de la condition du template
        print(f"\n🧪 Test de la condition du template...")
        if template_vars['clients']:
            print(f"   ✅ Condition 'if clients' = True")
            print(f"   ✅ Le tableau devrait s'afficher")
            
            # Test d'une boucle comme dans le template
            print(f"   🔄 Test de la boucle 'for client in clients':")
            for i, client in enumerate(template_vars['clients'][:3]):
                client_id = client.get('client_id', '')
                full_name = client.get('full_name', '')
                print(f"      {i+1}. ID: '{client_id}', Nom: '{full_name}'")
        else:
            print(f"   ❌ Condition 'if clients' = False")
            print(f"   ❌ Le message 'لا توجد نتائج' devrait s'afficher")
        
        print("\n" + "="*60)
        print("🏁 Debug terminé")
        
        # Résumé
        if clients and len(clients) > 0:
            print(f"✅ RÉSULTAT: {len(clients)} clients devraient s'afficher dans l'interface")
        else:
            print(f"❌ PROBLÈME: Aucun client ne devrait s'afficher")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_clients_route()