#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 Script de migration de base de données pour Render
Copie les données de visa_system.db vers data/visa_tracking.db
"""

import sqlite3
import shutil
import os
from datetime import datetime

def migrate_database():
    """Migrer les données de visa_system.db vers data/visa_tracking.db"""
    
    print("🔄 Migration de la base de données pour Render...")
    
    # Chemins des bases de données
    source_db = 'visa_system.db'  # Base avec 975 clients
    target_db = 'data/visa_tracking.db'  # Base cible pour Render
    
    # Vérifier que la base source existe
    if not os.path.exists(source_db):
        print(f"❌ Erreur: {source_db} n'existe pas!")
        return False
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs('data', exist_ok=True)
    
    try:
        # Connexion aux deux bases
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        
        # Obtenir les noms des tables de la base source (ignorer les tables système)
        source_cursor = source_conn.cursor()
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in source_cursor.fetchall()]
        
        print(f"📋 Tables trouvées: {tables}")
        
        # Copier chaque table
        for table in tables:
            print(f"📤 Copie de la table {table}...")
            
            # Obtenir la structure de la table
            source_cursor.execute(f"PRAGMA table_info({table})")
            columns_info = source_cursor.fetchall()
            
            # Créer la table dans la base cible
            target_cursor = target_conn.cursor()
            
            # Construire la requête CREATE TABLE
            create_sql = f"CREATE TABLE IF NOT EXISTS {table} ("
            column_definitions = []
            for col in columns_info:
                col_name, col_type, not_null, default_val, pk = col[1], col[2], col[3], col[4], col[5]
                col_def = f"{col_name} {col_type}"
                if not_null:
                    col_def += " NOT NULL"
                if default_val is not None:
                    col_def += f" DEFAULT {default_val}"
                if pk:
                    col_def += " PRIMARY KEY"
                column_definitions.append(col_def)
            
            create_sql += ", ".join(column_definitions) + ")"
            
            # Exécuter la création de table
            target_cursor.execute(create_sql)
            
            # Copier les données
            source_cursor.execute(f"SELECT * FROM {table}")
            rows = source_cursor.fetchall()
            
            if rows:
                # Obtenir les noms des colonnes
                column_names = [description[0] for description in source_cursor.description]
                placeholders = ", ".join(["?" for _ in column_names])
                insert_sql = f"INSERT OR REPLACE INTO {table} ({', '.join(column_names)}) VALUES ({placeholders})"
                
                target_cursor.executemany(insert_sql, rows)
                print(f"   ✅ {len(rows)} lignes copiées")
            else:
                print(f"   ⚠️ Table {table} vide")
        
        # Valider les changements
        target_conn.commit()
        
        # Vérifier le nombre de clients copiés
        target_cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = target_cursor.fetchone()[0]
        
        print(f"✅ Migration terminée!")
        print(f"📊 {client_count} clients copiés dans {target_db}")
        
        # Fermer les connexions
        source_conn.close()
        target_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

def create_render_deployment_script():
    """Créer un script de déploiement pour Render"""
    
    script_content = '''#!/bin/bash
# Script de déploiement pour Render
echo "🚀 Démarrage de l'application sur Render..."

# Créer le dossier data s'il n'existe pas
mkdir -p data

# Copier la base de données si elle existe
if [ -f "visa_system.db" ]; then
    echo "📋 Copie de la base de données..."
    cp visa_system.db data/visa_tracking.db
    echo "✅ Base de données copiée"
else
    echo "⚠️ Aucune base de données trouvée, création d'une base vide"
fi

# Démarrer l'application
echo "🌐 Démarrage du serveur Flask..."
python app.py
'''
    
    with open('render_start.sh', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("📝 Script render_start.sh créé")

def create_render_yaml():
    """Créer le fichier render.yaml pour la configuration"""
    
    yaml_content = '''services:
  - type: web
    name: visa-tracking-system
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: FLASK_ENV
        value: production
'''
    
    with open('render.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print("📝 Fichier render.yaml créé")

if __name__ == "__main__":
    print("🛂 Migration de base de données pour Render")
    print("=" * 50)
    
    # Effectuer la migration
    success = migrate_database()
    
    if success:
        # Créer les fichiers de déploiement
        create_render_deployment_script()
        create_render_yaml()
        
        print("\n✅ Migration terminée avec succès!")
        print("\n📋 Prochaines étapes pour Render:")
        print("1. Commitez tous les fichiers (git add . && git commit -m 'Migration DB')")
        print("2. Poussez vers GitHub (git push)")
        print("3. Redéployez sur Render")
        print("\n🔗 Votre base de données sera maintenant disponible sur Render!")
    else:
        print("\n❌ Échec de la migration")
