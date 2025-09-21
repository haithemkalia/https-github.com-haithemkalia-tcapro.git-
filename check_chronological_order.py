#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérifier l'ordre chronologique des clients
"""

import sqlite3
from datetime import datetime

def check_chronological_order():
    """Vérifier que les clients sont triés chronologiquement"""
    
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    
    try:
        # Récupérer les clients triés chronologiquement
        cursor.execute("""
            SELECT client_id, full_name, application_date, nationality, visa_status 
            FROM clients 
            ORDER BY 
                CASE WHEN application_date IS NULL OR application_date = '' THEN 1 ELSE 0 END ASC,
                substr(application_date, 7, 4) || '-' || substr(application_date, 4, 2) || '-' || substr(application_date, 1, 2) ASC,
                client_id ASC 
            LIMIT 15
        """)
        
        rows = cursor.fetchall()
        
        print("📅 LISTE DES CLIENTS EN ORDRE CHRONOLOGIQUE")
        print("=" * 80)
        print("(Plus ancien → Plus récent selon تاريخ التقديم)")
        print("-" * 80)
        
        for i, row in enumerate(rows, 1):
            client_id, full_name, app_date, nationality, visa_status = row
            date_display = app_date if app_date else "غير محدد"
            print(f"{i:2d}. {client_id} | {full_name} | {date_display} | {nationality} | {visa_status}")
        
        print("-" * 80)
        print(f"✅ {len(rows)} premiers clients affichés en ordre chronologique")
        
        # Vérifier aussi les dates les plus récentes
        cursor.execute("""
            SELECT client_id, full_name, application_date 
            FROM clients 
            WHERE application_date IS NOT NULL AND application_date != ''
            ORDER BY 
                substr(application_date, 7, 4) || '-' || substr(application_date, 4, 2) || '-' || substr(application_date, 1, 2) DESC
            LIMIT 5
        """)
        
        recent_rows = cursor.fetchall()
        
        print("\n📅 CLIENTS LES PLUS RÉCENTS:")
        print("-" * 50)
        for i, row in enumerate(recent_rows, 1):
            client_id, full_name, app_date = row
            print(f"{i}. {client_id} | {full_name} | {app_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_chronological_order()
