#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse approfondie pourquoi CLI100N devrait exister mais n'est pas trouvé
"""

import sqlite3
import pandas as pd
import re

def deep_search_analysis():
    try:
        conn = sqlite3.connect('visa_system.db')
        
        print("🔍 ANALYSE APPROFONDIE DE CLI100N")
        print("=" * 50)
        
        # 1. Vérifier tous les IDs qui commencent par CLI100
        print("\n1️⃣ TOUS LES IDs COMMENÇANT PAR 'CLI100':")
        query_cli100 = """
        SELECT client_id, full_name, passport_number, nationality, visa_status 
        FROM clients 
        WHERE client_id LIKE 'CLI100%' 
        ORDER BY client_id;
        """
        
        df_cli100 = pd.read_sql_query(query_cli100, conn)
        if not df_cli100.empty:
            print(df_cli100.to_string(index=False))
            print(f"📊 Nombre total CLI100*: {len(df_cli100)}")
        else:
            print("❌ Aucun ID CLI100* trouvé")
        
        # 2. Vérifier la séquence des CLI
        print("\n2️⃣ SÉQUENCE DES CLI - Vérifier s'il manque des numéros:")
        query_sequence = """
        SELECT client_id 
        FROM clients 
        WHERE client_id BETWEEN 'CLI099' AND 'CLI110'
        ORDER BY client_id;
        """
        
        df_sequence = pd.read_sql_query(query_sequence, conn)
        if not df_sequence.empty:
            print("Séquence trouvée:")
            for idx, row in df_sequence.iterrows():
                print(f"  {row['client_id']}")
                
            # Vérifier s'il manque CLI100N
            all_ids = df_sequence['client_id'].tolist()
            expected_cli100n = 'CLI100N'
            if expected_cli100n not in all_ids:
                print(f"\n⚠️  CLI100N MANQUANT dans la séquence!")
                print(f"IDs trouvés: {len(all_ids)}")
                print(f"IDs attendus: CLI099 à CLI110")
        
        # 3. Recherche dans les noms complets avec '100' ou 'N'
        print("\n3️⃣ RECHERCHE DANS LES NOMS ET PASSPORTS:")
        query_names = """
        SELECT client_id, full_name, passport_number, nationality, visa_status 
        FROM clients 
        WHERE full_name LIKE '%100%' 
           OR full_name LIKE '%N%'
           OR passport_number LIKE '%100%'
           OR passport_number LIKE '%N%'
        LIMIT 10;
        """
        
        df_names = pd.read_sql_query(query_names, conn)
        if not df_names.empty:
            print("Résultats trouvés:")
            print(df_names.to_string(index=False))
        
        # 4. Vérifier s'il y a des clients avec des IDs non standards
        print("\n4️⃣ VÉRIFICATION DES FORMATS D'ID:")
        query_formats = """
        SELECT DISTINCT 
            CASE 
                WHEN client_id GLOB 'CLI[0-9][0-9][0-9]' THEN 'Format CLI###'
                WHEN client_id GLOB 'CLI[0-9][0-9][0-9][0-9]' THEN 'Format CLI####'
                WHEN client_id GLOB 'CLI[0-9][0-9][0-9][A-Z]' THEN 'Format CLI###A'
                ELSE 'Autre format'
            END as format_id,
            COUNT(*) as nombre
        FROM clients
        GROUP BY format_id
        ORDER BY nombre DESC;
        """
        
        df_formats = pd.read_sql_query(query_formats, conn)
        print("Formats d'ID trouvés:")
        print(df_formats.to_string(index=False))
        
        # 5. Recherche spécifique pour CLI100N avec des variantes
        print("\n5️⃣ RECHERCHE DE VARIANTES DE CLI100N:")
        variants = ['CLI100N', 'CLI100', 'CLI1000', 'CLI100A', 'CLI100B', 'CLI100C']
        
        for variant in variants:
            query = f"""
            SELECT COUNT(*) as count 
            FROM clients 
            WHERE client_id = '{variant}';
            """
            result = pd.read_sql_query(query, conn)
            count = result.iloc[0]['count']
            status = "✅ EXISTE" if count > 0 else "❌ N'EXISTE PAS"
            print(f"  {variant}: {status}")
        
        # 6. Vérifier les données d'import
        print("\n6️⃣ ANALYSE DES DONNÉES D'IMPORT:")
        query_import = """
        SELECT 
            MIN(created_at) as premiere_date,
            MAX(created_at) as derniere_date,
            COUNT(DISTINCT client_id) as total_clients
        FROM clients;
        """
        
        df_import = pd.read_sql_query(query_import, conn)
        print("Informations d'import:")
        print(df_import.to_string(index=False))
        
        conn.close()
        
        # 7. Recommandations
        print("\n🎯 RECOMMANDATIONS:")
        print("1. CLI100N n'existe pas actuellement dans la base de données")
        print("2. CLI100 (Hussein Musa) existe - c'est peut-être une confusion")
        print("3. CLI1000 (Omar Al-Idrissi) existe aussi")
        print("4. Pour avoir CLI100N, vous devez:")
        print("   - Soit le créer manuellement via le formulaire d'ajout")
        print("   - Soit l'importer via Excel")
        print("   - Soit vérifier si le fichier source contient CLI100N")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    deep_search_analysis()