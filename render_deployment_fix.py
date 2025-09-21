#!/usr/bin/env python3
"""
Script de résolution pour le déploiement Render
Gère les problèmes de base de données SQLite et d'affichage des clients
"""

import sqlite3
import os
import shutil
import json
from datetime import datetime

def check_database_integrity():
    """Vérifie l'intégrité de la base de données et le nombre de clients"""
    print("🔍 Vérification de la base de données...")
    
    try:
        conn = sqlite3.connect('visa_system.db')
        cursor = conn.cursor()
        
        # Compter les clients
        cursor.execute('SELECT COUNT(*) FROM clients')
        count = cursor.fetchone()[0]
        print(f"✅ Nombre total de clients dans la base: {count}")
        
        # Vérifier la structure
        cursor.execute('PRAGMA table_info(clients)')
        columns = [col[1] for col in cursor.fetchall()]
        print(f"✅ Colonnes disponibles: {len(columns)} colonnes")
        
        # Exemple de données
        if count > 0:
            cursor.execute('SELECT id, client_id, full_name, whatsapp_number FROM clients LIMIT 3')
            samples = cursor.fetchall()
            print("\n📋 Exemples de clients:")
            for client in samples:
                print(f"  - ID: {client[1]}, Nom: {client[2]}, WhatsApp: {client[3]}")
        
        conn.close()
        return count
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return 0

def create_render_startup_script():
    """Crée un script de démarrage adapté pour Render"""
    print("\n📄 Création du script de démarrage Render...")
    
    startup_content = '''#!/bin/bash
# Script de démarrage pour Render

echo "🚀 Démarrage de l'application TCA VISA PRO2 sur Render..."

# Vérifier que la base de données existe
if [ ! -f "visa_system.db" ]; then
    echo "⚠️  Base de données non trouvée, création d'une nouvelle base..."
    python -c "
import sqlite3
conn = sqlite3.connect('visa_system.db')
conn.close()
print('✅ Base de données créée')
"
fi

# Lancer l'application
echo "🌐 Lancement du serveur Flask..."
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
'''
    
    with open('render_start.sh', 'w', encoding='utf-8') as f:
        f.write(startup_content)
    
    print("✅ Script de démarrage Render créé: render_start.sh")

def create_render_config():
    """Crée une configuration Render adaptée"""
    print("\n⚙️ Création de la configuration Render...")
    
    render_yaml = '''services:
  - type: web
    name: tca-visa-pro2
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "chmod +x render_start.sh && ./render_start.sh"
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      - key: FLASK_ENV
        value: "production"
      - key: PORT
        value: "10000"
    disk:
      name: sqlite-data
      mountPath: /data
      sizeGB: 1
'''
    
    with open('render.yaml', 'w', encoding='utf-8') as f:
        f.write(render_yaml)
    
    print("✅ Configuration Render créée: render.yaml")

def update_requirements():
    """Met à jour le requirements.txt pour Render"""
    print("\n📦 Mise à jour des dépendances...")
    
    requirements = '''Flask==2.3.3
sqlite3
requests
pandas
openpyxl
python-dotenv
gunicorn==21.2.0
'''
    
    with open('requirements_render.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print("✅ Requirements Render créés: requirements_render.txt")

def create_deployment_guide():
    """Crée un guide de déploiement détaillé"""
    print("\n📚 Création du guide de déploiement...")
    
    guide = '''# Guide de Déploiement Render - TCA VISA PRO2

## 🎯 Objectif
Résoudre les problèmes d'affichage des clients après déploiement sur Render

## 📊 État actuel
- Base de données: visa_system.db
- Nombre de clients: 975
- Format des IDs: CLI001, CLI002, etc.

## 🔧 Configuration Render

### 1. Variables d'environnement requises:
```
PYTHON_VERSION=3.11
FLASK_ENV=production
PORT=10000
```

### 2. Fichiers nécessaires:
- ✅ requirements.txt
- ✅ app.py
- ✅ visa_system.db (avec données)
- ✅ render_start.sh (script de démarrage)
- ✅ render.yaml (configuration)

### 3. Structure des données:
```sql
-- Table clients principale
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    client_id TEXT UNIQUE,
    full_name TEXT,
    whatsapp_number TEXT,
    passport_number TEXT,
    visa_status TEXT,
    -- ... autres colonnes
);
```

## 🚀 Procédure de déploiement:

### Étape 1: Préparation
1. S'assurer que visa_system.db contient les données
2. Vérifier que le script render_start.sh est exécutable
3. Configurer les variables d'environnement dans Render

### Étape 2: Déploiement
1. Connecter le repository GitHub à Render
2. Sélectionner la branche principale
3. Configurer le plan (Web Service)
4. Définir les variables d'environnement
5. Activer le stockage persistant (Disk)

### Étape 3: Vérification
1. Accéder à l'URL Render fournie
2. Vérifier /clients affiche les données
3. Confirmer que les 975 clients sont visibles

## 🔍 Dépannage

### Problème: Aucun client affiché
**Solution:** Vérifier que:
- La base de données est bien transférée
- Le chemin de la base est correct
- Les permissions sont accordées

### Problème: Erreur 500
**Solution:** Vérifier les logs Render pour:
- Erreurs de connexion DB
- Problèmes d'import
- Erreurs de template

## 📞 Support
En cas de problème, vérifier:
- Les logs Render
- La connexion à la base de données
- L'intégrité des fichiers
'''
    
    with open('RENDER_DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Guide de déploiement créé: RENDER_DEPLOYMENT_GUIDE.md")

def main():
    """Fonction principale"""
    print("🚀 Script de résolution pour Render - TCA VISA PRO2")
    print("=" * 60)
    
    # Vérifier la base de données
    client_count = check_database_integrity()
    
    if client_count == 0:
        print("❌ Aucun client trouvé dans la base de données!")
        return
    
    print(f"\n✅ Base de données prête avec {client_count} clients")
    
    # Créer les fichiers nécessaires
    create_render_startup_script()
    create_render_config()
    update_requirements()
    create_deployment_guide()
    
    print("\n🎉 Configuration Render complétée!")
    print("\nProchaines étapes:")
    print("1. Transférer visa_system.db sur Render")
    print("2. Configurer les variables d'environnement")
    print("3. Utiliser render_start.sh comme commande de démarrage")
    print("4. Activer le stockage persistant pour la DB")

if __name__ == "__main__":
    main()