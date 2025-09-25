#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Préparer l'import des données pour Render
"""

import json
import pandas as pd
import sqlite3

def prepare_render_import():
    print("🔄 PRÉPARATION DE L'IMPORT POUR RENDER")
    print("=" * 40)
    
    # Lire le fichier JSON exporté
    try:
        with open('clients_complete_20250925_020530.json', 'r', encoding='utf-8') as f:
            clients_data = json.load(f)
        
        print(f"📊 Nombre de clients à importer: {len(clients_data)}")
        
        # Créer un format Excel optimisé pour l'import
        df = pd.DataFrame(clients_data)
        
        # Sélectionner les colonnes essentielles pour l'import
        essential_columns = [
            'client_id', 'full_name', 'whatsapp_number', 'passport_number',
            'nationality', 'visa_status', 'application_date', 'transaction_date',
            'processed_by', 'responsible_employee', 'passport_status'
        ]
        
        # Filtrer les colonnes existantes
        available_columns = [col for col in essential_columns if col in df.columns]
        import_df = df[available_columns].copy()
        
        # Créer le fichier d'import
        import_filename = 'render_import_ready.xlsx'
        import_df.to_excel(import_filename, index=False, engine='openpyxl')
        print(f"💾 Fichier d'import créé: {import_filename}")
        
        # Créer un résumé pour vérification
        print(f"\n📋 Aperçu des données à importer:")
        print(f"  - Total: {len(import_df)} clients")
        print(f"  - Colonnes: {', '.join(available_columns)}")
        
        # Afficher les 5 premiers clients
        print(f"\n📝 5 premiers clients:")
        for i in range(min(5, len(import_df))):
            client = import_df.iloc[i]
            print(f"  {client['client_id']}: {client['full_name']}")
        
        # Afficher les 5 derniers clients
        print(f"\n📝 5 derniers clients:")
        for i in range(max(0, len(import_df)-5), len(import_df)):
            client = import_df.iloc[i]
            print(f"  {client['client_id']}: {client['full_name']}")
        
        # Vérifier CLI100N et CLI1000
        cli100n = import_df[import_df['client_id'] == 'CLI100N']
        if not cli100n.empty:
            print(f"\n✅ CLI100N trouvé dans l'import:")
            print(f"  - Nom: {cli100n.iloc[0]['full_name']}")
        
        cli1000 = import_df[import_df['client_id'] == 'CLI1000']
        if not cli1000.empty:
            print(f"\n✅ CLI1000 trouvé dans l'import:")
            print(f"  - Nom: {cli1000.iloc[0]['full_name']}")
        
        # Créer aussi un fichier CSV pour backup
        csv_filename = 'render_import_backup.csv'
        import_df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"💾 Fichier CSV backup créé: {csv_filename}")
        
        print(f"\n🎯 INSTRUCTIONS POUR RENDER:")
        print(f"1. Téléchargez le fichier: {import_filename}")
        print(f"2. Allez sur votre site Render: https://https-github-com-haithemkalia-tcapro-git.onrender.com")
        print(f"3. Trouvez l'option d'import Excel/données")
        print(f"4. Téléversez le fichier {import_filename}")
        print(f"5. Vérifiez que les 1001 clients sont importés")
        
        return import_filename
        
    except FileNotFoundError:
        print("❌ Fichier clients_complete_20250925_020530.json non trouvé")
        print("💡 Assurez-vous d'avoir exécuté export_complete_clients.py d'abord")
        return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def create_step_by_step_guide():
    """Créer un guide détaillé pour l'import"""
    guide_content = """
# GUIDE D'IMPORT POUR RENDER - 1001 CLIENTS

## ÉTAPES DÉTAILLÉES:

### 1. PRÉPARATION
- Fichier créé: render_import_ready.xlsx
- Nombre de clients: 1001
- Inclut CLI100N et CLI1000

### 2. ACCÈS AU SITE RENDER
- URL: https://https-github-com-haithemkalia-tcapro-git.onrender.com
- Attendre que le site soit complètement chargé

### 3. IMPORT DES DONNÉES
- Chercher une option "Importer" ou "Import Excel" dans le menu
- Si pas d'option directe, chercher dans:
  * Paramètres / Settings
  * Administration / Admin
  * Outils / Tools
  * Gestion des données / Data Management

### 4. VÉRIFICATION APRÈS IMPORT
- Vérifier le nombre total: 1001 clients
- Chercher CLI100N: نور الدين بن علي
- Chercher CLI1000: عمر الإدريسي
- Vérifier CLI001: سالم علي (premier client)
- Vérifier CLI976: مراد الجويني (dernier client)

### 5. PROBLÈMES POSSIBLES
- Si le site est lent: attendre 2-3 minutes
- Si pas d'option d'import: contacter l'administrateur
- Si erreur lors de l'import: vérifier le format du fichier

### 6. DONNÉES CLÉS À VÉRIFIER
✅ CLI100N: نور الدين بن علي (nouveau client créé)
✅ CLI1000: عمر الإدريسي (existe déjà)
✅ CLI001: سالم علي (premier client)
✅ CLI976: مراد الجويني (dernier client)
📊 Total: 1001 clients

"""
    
    with open('RENDER_IMPORT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("💾 Guide d'import créé: RENDER_IMPORT_GUIDE.md")

if __name__ == "__main__":
    import_file = prepare_render_import()
    if import_file:
        create_step_by_step_guide()
        print("\n🎉 Préparation terminée! Suivez le guide RENDER_IMPORT_GUIDE.md")