#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérification de l'importation des champs 'الموظف المسؤول' et 'تاريخ التقديم'
"""

import sqlite3
import os
from collections import Counter
from datetime import datetime

def analyze_employee_date_fields():
    """Analyser les champs employé responsable et date de soumission"""
    
    # Vérifier les bases de données disponibles
    db_paths = ['visa_system.db', 'data/visa_tracking.db']
    db_path = None
    
    for path in db_paths:
        if os.path.exists(path):
            # Vérifier si la base contient des données
            try:
                test_conn = sqlite3.connect(path)
                test_cursor = test_conn.cursor()
                test_cursor.execute("SELECT COUNT(*) FROM clients")
                count = test_cursor.fetchone()[0]
                test_conn.close()
                
                if count > 0:
                    db_path = path
                    break
            except:
                continue
    
    if not db_path:
        print("❌ Erreur: Aucune base de données trouvée")
        return
    
    print(f"📂 Base de données utilisée: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Vérifier la structure de la table
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        
        print("🔍 VÉRIFICATION DES CHAMPS 'الموظف المسؤول' ET 'تاريخ التقديم'")
        print("=" * 70)
        
        # Vérifier les colonnes pertinentes
        relevant_columns = []
        for col in columns:
            if col[1] in ['responsible_employee', 'application_date']:
                relevant_columns.append(col[1])
        
        print(f"\n📋 COLONNES TROUVÉES:")
        for col in relevant_columns:
            if col == 'responsible_employee':
                print(f"   ✅ {col} (الموظف المسؤول)")
            elif col == 'application_date':
                print(f"   ✅ {col} (تاريخ التقديم)")
        
        # Récupérer tous les clients
        cursor.execute("SELECT * FROM clients ORDER BY id")
        clients = cursor.fetchall()
        
        total_clients = len(clients)
        print(f"\n📊 NOMBRE TOTAL DE CLIENTS: {total_clients}")
        
        if total_clients == 0:
            print("❌ Aucun client trouvé dans la base de données")
            return
        
        # Analyser le champ 'responsible_employee' (الموظف المسؤول)
        print("\n" + "=" * 50)
        print("📋 ANALYSE DU CHAMP 'الموظف المسؤول' (responsible_employee)")
        print("=" * 50)
        
        responsible_employees = []
        empty_responsible = 0
        filled_responsible = 0
        
        for client in clients:
            emp = client['responsible_employee']
            if emp and emp.strip():
                responsible_employees.append(emp.strip())
                filled_responsible += 1
            else:
                empty_responsible += 1
        
        print(f"\n📈 STATISTIQUES:")
        print(f"   • Champs remplis: {filled_responsible} ({filled_responsible/total_clients*100:.1f}%)")
        print(f"   • Champs vides: {empty_responsible} ({empty_responsible/total_clients*100:.1f}%)")
        
        if responsible_employees:
            employee_counts = Counter(responsible_employees)
            print(f"\n👥 EMPLOYÉS RESPONSABLES IDENTIFIÉS ({len(employee_counts)} uniques):")
            for emp, count in employee_counts.most_common():
                print(f"   • {emp}: {count} clients ({count/total_clients*100:.1f}%)")
        
        # Analyser le champ 'application_date' (تاريخ التقديم)
        print("\n" + "=" * 50)
        print("📅 ANALYSE DU CHAMP 'تاريخ التقديم' (application_date)")
        print("=" * 50)
        
        application_dates = []
        empty_dates = 0
        filled_dates = 0
        valid_dates = 0
        invalid_dates = 0
        
        for client in clients:
            app_date = client['application_date']
            if app_date and app_date.strip():
                application_dates.append(app_date.strip())
                filled_dates += 1
                
                # Vérifier le format de la date
                try:
                    # Essayer différents formats de date
                    if '-' in app_date:
                        datetime.strptime(app_date.strip(), '%Y-%m-%d')
                    elif '/' in app_date:
                        datetime.strptime(app_date.strip(), '%d/%m/%Y')
                    valid_dates += 1
                except:
                    invalid_dates += 1
            else:
                empty_dates += 1
        
        print(f"\n📈 STATISTIQUES:")
        print(f"   • Champs remplis: {filled_dates} ({filled_dates/total_clients*100:.1f}%)")
        print(f"   • Champs vides: {empty_dates} ({empty_dates/total_clients*100:.1f}%)")
        print(f"   • Dates valides: {valid_dates} ({valid_dates/total_clients*100:.1f}%)")
        print(f"   • Dates invalides: {invalid_dates} ({invalid_dates/total_clients*100:.1f}%)")
        
        if application_dates:
            # Analyser les formats de dates
            date_formats = Counter()
            for date_str in application_dates[:10]:  # Échantillon
                if '-' in date_str:
                    date_formats['YYYY-MM-DD'] += 1
                elif '/' in date_str:
                    date_formats['DD/MM/YYYY'] += 1
                else:
                    date_formats['Autre'] += 1
            
            print(f"\n📅 FORMATS DE DATES DÉTECTÉS:")
            for fmt, count in date_formats.items():
                print(f"   • {fmt}: {count} occurrences")
        
        # Afficher un échantillon des données
        print("\n" + "=" * 50)
        print("📋 ÉCHANTILLON DES DONNÉES (10 premiers clients)")
        print("=" * 50)
        
        print(f"{'ID':<8} {'Nom':<20} {'Employé':<15} {'Date App.':<12}")
        print("-" * 60)
        
        for i, client in enumerate(clients[:10]):
            client_id = client['client_id'] or f"#{client['id']}"
            name = (client['full_name'] or 'N/A')[:18]
            employee = (client['responsible_employee'] or 'Vide')[:13]
            app_date = (client['application_date'] or 'Vide')[:10]
            
            print(f"{client_id:<8} {name:<20} {employee:<15} {app_date:<12}")
        
        # Résumé final
        print("\n" + "=" * 50)
        print("🎯 RÉSUMÉ DE LA VÉRIFICATION")
        print("=" * 50)
        
        print(f"\n✅ CHAMP 'الموظف المسؤول' (responsible_employee):")
        print(f"   • Présent dans la base de données: OUI")
        print(f"   • Données importées: {filled_responsible}/{total_clients} ({filled_responsible/total_clients*100:.1f}%)")
        print(f"   • Champs vides préservés: {empty_responsible} (comme demandé)")
        
        print(f"\n✅ CHAMP 'تاريخ التقديم' (application_date):")
        print(f"   • Présent dans la base de données: OUI")
        print(f"   • Données importées: {filled_dates}/{total_clients} ({filled_dates/total_clients*100:.1f}%)")
        print(f"   • Champs vides préservés: {empty_dates} (comme demandé)")
        print(f"   • Dates valides: {valid_dates}/{filled_dates} ({valid_dates/filled_dates*100 if filled_dates > 0 else 0:.1f}%)")
        
        success_rate = ((filled_responsible + filled_dates) / (total_clients * 2)) * 100
        print(f"\n🎯 TAUX DE SUCCÈS GLOBAL: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ IMPORTATION RÉUSSIE - Les champs sont correctement importés")
        elif success_rate >= 50:
            print("⚠️ IMPORTATION PARTIELLE - Certaines données manquent")
        else:
            print("❌ PROBLÈME D'IMPORTATION - Beaucoup de données manquantes")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_employee_date_fields()