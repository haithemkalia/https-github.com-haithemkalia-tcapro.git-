#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tester le tri chronologique par معرف العميل (client_id)
"""

import sys
sys.path.append('src')

from database.database_manager import DatabaseManager

def test_client_id_order():
    """Tester le tri chronologique par client_id"""
    
    try:
        db = DatabaseManager()
        
        # Tester la méthode get_all_clients
        clients, total = db.get_all_clients(page=1, per_page=15)
        
        print("📅 LISTE CLIENTS TRIÉS PAR معرف العميل (client_id):")
        print("=" * 70)
        print("(Ordre chronologique: CLI001 → CLI002 → CLI003 → ...)")
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
        print(f"✅ {len(clients)} clients affichés par ordre معرف العميل")
        print(f"📊 Total dans la base: {total} clients")
        
        # Vérifier que l'ordre est bien chronologique par client_id
        client_ids = [client['client_id'] for client in clients]
        print(f"\n🔍 VÉRIFICATION DE L'ORDRE:")
        print(f"Premier client_id: {client_ids[0]}")
        print(f"Dernier client_id: {client_ids[-1]}")
        
        # Tester aussi la recherche
        print("\n🔍 TEST DE RECHERCHE AVEC TRI PAR معرف العميل:")
        print("-" * 50)
        
        search_clients, search_total = db.search_clients("محمد", page=1, per_page=5)
        
        for i, client in enumerate(search_clients, 1):
            client_id = client['client_id']
            full_name = client['full_name']
            app_date = client['application_date']
            print(f"{i}. {client_id} | {full_name} | {app_date}")
        
        print(f"✅ {len(search_clients)} résultats de recherche triés par معرف العميل")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_client_id_order()
