#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 Migration simple pour Render - Copie directe de la base de données
"""

import shutil
import os
from datetime import datetime

def simple_migrate():
    """Migration simple en copiant directement le fichier de base de données"""
    
    print("🔄 Migration simple pour Render...")
    
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
        # Copier directement le fichier
        print(f"📤 Copie de {source_db} vers {target_db}...")
        shutil.copy2(source_db, target_db)
        
        # Vérifier que la copie a réussi
        if os.path.exists(target_db):
            # Vérifier le nombre de clients
            import sqlite3
            conn = sqlite3.connect(target_db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients")
            client_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"✅ Migration terminée!")
            print(f"📊 {client_count} clients copiés dans {target_db}")
            
            # Créer une sauvegarde avec timestamp
            backup_name = f"visa_system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(source_db, backup_name)
            print(f"💾 Sauvegarde créée: {backup_name}")
            
            return True
        else:
            print("❌ Échec de la copie")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

def create_render_files():
    """Créer les fichiers nécessaires pour Render"""
    
    # 1. Script de démarrage pour Render
    start_script = '''#!/bin/bash
echo "🚀 Démarrage de l'application sur Render..."

# Créer le dossier data s'il n'existe pas
mkdir -p data

# Vérifier si la base de données existe
if [ -f "visa_system.db" ]; then
    echo "📋 Copie de la base de données..."
    cp visa_system.db data/visa_tracking.db
    echo "✅ Base de données copiée"
elif [ -f "data/visa_tracking.db" ]; then
    echo "✅ Base de données déjà présente"
else
    echo "⚠️ Aucune base de données trouvée"
fi

# Démarrer l'application
echo "🌐 Démarrage du serveur Flask..."
python app.py
'''
    
    with open('render_start.sh', 'w', encoding='utf-8') as f:
        f.write(start_script)
    
    # 2. Fichier render.yaml
    render_yaml = '''services:
  - type: web
    name: visa-tracking-system
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: bash render_start.sh
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: FLASK_ENV
        value: production
'''
    
    with open('render.yaml', 'w', encoding='utf-8') as f:
        f.write(render_yaml)
    
    # 3. Requirements pour Render
    requirements_render = '''# Web Application Dependencies
Flask==2.3.3
Werkzeug==2.3.7
Jinja2==3.1.2

# Data Processing
pandas>=2.0.0
openpyxl>=3.0.0

# HTTP Requests
requests>=2.30.0

# Database
# sqlite3 is included with Python

# Utilities
gunicorn>=21.0.0
'''
    
    with open('requirements_render.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_render)
    
    print("📝 Fichiers Render créés:")
    print("   - render_start.sh")
    print("   - render.yaml") 
    print("   - requirements_render.txt")

def create_gitignore():
    """Créer un .gitignore approprié"""
    
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Application specific
uploads/
*.log
*.db-journal

# Keep important databases
!visa_system.db
!data/visa_tracking.db
'''
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("📝 .gitignore créé")

if __name__ == "__main__":
    print("🛂 Migration simple pour Render")
    print("=" * 50)
    
    # Effectuer la migration
    success = simple_migrate()
    
    if success:
        # Créer les fichiers de déploiement
        create_render_files()
        create_gitignore()
        
        print("\n✅ Migration terminée avec succès!")
        print("\n📋 Prochaines étapes pour Render:")
        print("1. git add .")
        print("2. git commit -m 'Migration DB pour Render'")
        print("3. git push")
        print("4. Redéployer sur Render")
        print("\n🔗 Votre base de données sera maintenant disponible sur Render!")
        print(f"\n📊 Base de données: {target_db}")
    else:
        print("\n❌ Échec de la migration")
