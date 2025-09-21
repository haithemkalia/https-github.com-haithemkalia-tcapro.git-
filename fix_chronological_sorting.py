#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corriger le tri chronologique en normalisant les dates
"""

import sqlite3
from datetime import datetime

def fix_chronological_sorting():
    """Corriger le tri chronologique en normalisant les dates"""
    
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    
    try:
        print("🔧 CORRECTION DU TRI CHRONOLOGIQUE")
        print("=" * 50)
        
        # 1. Analyser les formats de dates existants
        cursor.execute("SELECT DISTINCT application_date FROM clients WHERE application_date IS NOT NULL AND application_date != '' LIMIT 10")
        date_samples = cursor.fetchall()
        
        print("📅 ÉCHANTILLONS DE DATES DÉTECTÉS:")
        for date_sample in date_samples:
            print(f"   '{date_sample[0]}'")
        
        # 2. Créer une fonction SQL pour normaliser les dates
        # Cette fonction convertit DD/MM/YYYY en YYYY-MM-DD pour un tri correct
        cursor.execute("""
            SELECT 
                client_id, 
                full_name, 
                application_date,
                CASE 
                    WHEN application_date LIKE '__/__/____' THEN
                        substr(application_date, 7, 4) || '-' || 
                        substr(application_date, 4, 2) || '-' || 
                        substr(application_date, 1, 2)
                    WHEN application_date LIKE '____-__-__' THEN application_date
                    ELSE '9999-12-31'
                END as normalized_date
            FROM clients 
            ORDER BY 
                CASE WHEN application_date IS NULL OR application_date = '' THEN 1 ELSE 0 END ASC,
                CASE 
                    WHEN application_date LIKE '__/__/____' THEN
                        substr(application_date, 7, 4) || '-' || 
                        substr(application_date, 4, 2) || '-' || 
                        substr(application_date, 1, 2)
                    WHEN application_date LIKE '____-__-__' THEN application_date
                    ELSE '9999-12-31'
                END ASC,
                client_id ASC
            LIMIT 15
        """)
        
        rows = cursor.fetchall()
        
        print("\n📅 LISTE CORRIGÉE EN ORDRE CHRONOLOGIQUE:")
        print("=" * 80)
        print("(Plus ancien → Plus récent avec dates normalisées)")
        print("-" * 80)
        
        for i, row in enumerate(rows, 1):
            client_id, full_name, app_date, normalized_date = row
            date_display = app_date if app_date else "غير محدد"
            print(f"{i:2d}. {client_id} | {full_name} | {date_display} | Normalisé: {normalized_date}")
        
        print("-" * 80)
        print(f"✅ {len(rows)} premiers clients avec tri chronologique corrigé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_chronological_sorting()
