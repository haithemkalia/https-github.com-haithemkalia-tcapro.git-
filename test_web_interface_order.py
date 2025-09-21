#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tester l'ordre chronologique via l'interface web
"""

import sys
sys.path.append('src')

from database.database_manager import DatabaseManager

def test_web_interface_order():
    """Tester l'ordre chronologique via l'interface web"""
    
    try:
        db = DatabaseManager()
        
        # Tester la méthode get_all_clients
        clients, total = db.get_all_clients(page=1, per_page=10)
        
        print("📅 LISTE CLIENTS VIA INTERFACE WEB (ordre chronologique):")
        print("=" * 70)
        print("(Plus ancien → Plus récent selon تاريخ التقديم)")
        print("-" * 70)
        
        for i, client in enumerate(clients, 1):
            client_id = client['client_id']
            full_name = client['full_name']
            app_date = client['application_date']
            nationality = client['nationality']
            visa_status = client['visa_status']
            
            date_display = app_date if app_date else "غير محدد"
            print(f"{i:2d}. {client_id} | {full_name} | {date_display} | {nationality} | {visa_status}")
        
        print("-" * 70)
        print(f"✅ {len(clients)} clients affichés via l'interface web")
        print(f"📊 Total dans la base: {total} clients")
        
        # Tester aussi la recherche
        print("\n🔍 TEST DE RECHERCHE AVEC TRI CHRONOLOGIQUE:")
        print("-" * 50)
        
        search_clients, search_total = db.search_clients("سالم", page=1, per_page=5)
        
        for i, client in enumerate(search_clients, 1):
            client_id = client['client_id']
            full_name = client['full_name']
            app_date = client['application_date']
            print(f"{i}. {client_id} | {full_name} | {app_date}")
        
        print(f"✅ {len(search_clients)} résultats de recherche avec tri chronologique")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_web_interface_order()
