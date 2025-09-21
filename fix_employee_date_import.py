#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction de l'importation des champs 'الموظف المسؤول' et 'تاريخ التقديم'
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime

def fix_employee_date_import():
    """Corriger l'importation des champs employé et date"""
    
    excel_file = 'قائمة الزبائن معرض_أكتوبر2025 (21).xlsx'
    db_file = 'visa_system.db'
    
    if not os.path.exists(excel_file):
        print(f"❌ Fichier Excel non trouvé: {excel_file}")
        return
    
    if not os.path.exists(db_file):
        print(f"❌ Base de données non trouvée: {db_file}")
        return
    
    try:
        print("🔧 CORRECTION DE L'IMPORTATION DES CHAMPS")
        print("=" * 50)
        
        # Lire le fichier Excel
        print("📖 Lecture du fichier Excel...")
        df = pd.read_excel(excel_file)
        
        # Mapping des colonnes correctes
        column_mapping = {
            'responsible_employee': 'اختيار الموظف مسؤول',
            'application_date': 'تاريخ التقديم        '  # Avec espaces
        }
        
        print(f"📊 Données Excel trouvées: {len(df)} lignes")
        
        # Connexion à la base de données
        print("🔗 Connexion à la base de données...")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Vérifier le nombre de clients dans la DB
        cursor.execute("SELECT COUNT(*) FROM clients")
        db_count = cursor.fetchone()[0]
        print(f"📊 Clients dans la DB: {db_count}")
        
        if db_count != len(df):
            print(f"⚠️ Attention: Nombre différent entre Excel ({len(df)}) et DB ({db_count})")
        
        # Récupérer tous les clients ordonnés par ID
        cursor.execute("SELECT id, client_id FROM clients ORDER BY id")
        db_clients = cursor.fetchall()
        
        print("\n🔄 Mise à jour des champs...")
        
        updated_employees = 0
        updated_dates = 0
        errors = 0
        
        for i, (db_id, client_id) in enumerate(db_clients):
            if i >= len(df):
                break
                
            try:
                # Récupérer les données Excel pour cette ligne
                excel_row = df.iloc[i]
                
                # Extraire les valeurs
                employee = excel_row.get(column_mapping['responsible_employee'])
                app_date = excel_row.get(column_mapping['application_date'])
                
                # Nettoyer les valeurs
                employee_clean = str(employee).strip() if pd.notna(employee) and str(employee).strip() != 'nan' else None
                date_clean = None
                
                if pd.notna(app_date) and str(app_date).strip() != 'nan':
                    date_str = str(app_date).strip()
                    # Convertir la date si nécessaire
                    try:
                        if isinstance(app_date, pd.Timestamp):
                            date_clean = app_date.strftime('%Y-%m-%d')
                        elif '-' in date_str:
                            # Vérifier le format YYYY-MM-DD
                            datetime.strptime(date_str, '%Y-%m-%d')
                            date_clean = date_str
                        else:
                            date_clean = date_str
                    except:
                        date_clean = date_str  # Garder tel quel si conversion échoue
                
                # Mettre à jour la base de données
                cursor.execute("""
                    UPDATE clients 
                    SET responsible_employee = ?, application_date = ?
                    WHERE id = ?
                """, (employee_clean, date_clean, db_id))
                
                if employee_clean:
                    updated_employees += 1
                if date_clean:
                    updated_dates += 1
                    
            except Exception as e:
                print(f"❌ Erreur ligne {i+1}: {e}")
                errors += 1
        
        # Valider les changements
        conn.commit()
        
        print(f"\n✅ MISE À JOUR TERMINÉE:")
        print(f"   • Employés mis à jour: {updated_employees}")
        print(f"   • Dates mises à jour: {updated_dates}")
        print(f"   • Erreurs: {errors}")
        
        # Vérification finale
        print("\n🔍 VÉRIFICATION FINALE:")
        
        cursor.execute("SELECT COUNT(*) FROM clients WHERE responsible_employee IS NOT NULL AND responsible_employee != ''")
        final_employees = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM clients WHERE application_date IS NOT NULL AND application_date != ''")
        final_dates = cursor.fetchone()[0]
        
        print(f"   • Employés remplis: {final_employees}/{db_count} ({final_employees/db_count*100:.1f}%)")
        print(f"   • Dates remplies: {final_dates}/{db_count} ({final_dates/db_count*100:.1f}%)")
        
        # Échantillon des données mises à jour
        print("\n📋 ÉCHANTILLON DES DONNÉES MISES À JOUR:")
        cursor.execute("""
            SELECT client_id, full_name, responsible_employee, application_date 
            FROM clients 
            WHERE (responsible_employee IS NOT NULL AND responsible_employee != '') 
               OR (application_date IS NOT NULL AND application_date != '')
            LIMIT 10
        """)
        
        samples = cursor.fetchall()
        print(f"{'ID':<8} {'Nom':<20} {'Employé':<15} {'Date':<12}")
        print("-" * 60)
        
        for sample in samples:
            client_id = sample[0] or 'N/A'
            name = (sample[1] or 'N/A')[:18]
            employee = (sample[2] or 'Vide')[:13]
            app_date = (sample[3] or 'Vide')[:10]
            
            print(f"{client_id:<8} {name:<20} {employee:<15} {app_date:<12}")
        
        conn.close()
        
        print(f"\n🎯 CORRECTION TERMINÉE AVEC SUCCÈS!")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    fix_employee_date_import()