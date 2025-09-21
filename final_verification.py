#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérification finale du tri par معرف العميل
"""

import sqlite3

def final_verification():
    """Vérification finale du tri par client_id"""
    
    conn = sqlite3.connect('visa_system.db')
    cursor = conn.cursor()
    
    try:
        # Vérifier le tri par client_id
        cursor.execute("""
            SELECT client_id, full_name, application_date 
            FROM clients 
            ORDER BY 
                CASE WHEN client_id IS NULL OR client_id = '' THEN 1 ELSE 0 END ASC, 
                client_id ASC 
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        
        print("✅ VÉRIFICATION FINALE - TRI PAR معرف العميل:")
        print("=" * 60)
        print("(Ordre chronologique: CLI001 → CLI002 → CLI003 → ...)")
        print("-" * 60)
        
        for i, row in enumerate(rows, 1):
            client_id, full_name, app_date = row
            date_display = app_date if app_date else "غير محدد"
            print(f"{i:2d}. {client_id} - {full_name} - {date_display}")
        
        print("-" * 60)
        print(f"✅ {len(rows)} clients triés par معرف العميل")
        
        # Vérifier que l'ordre est correct
        client_ids = [row[0] for row in rows]
        is_ordered = all(client_ids[i] <= client_ids[i+1] for i in range(len(client_ids)-1))
        
        if is_ordered:
            print("✅ L'ordre chronologique par معرف العميل est correct !")
        else:
            print("❌ L'ordre n'est pas correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    final_verification()
