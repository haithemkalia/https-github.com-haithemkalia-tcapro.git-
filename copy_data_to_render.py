#!/usr/bin/env python3
"""
Script pour copier les données de la base locale vers Render
"""

import sqlite3
import os
import tempfile
import shutil

def copy_database_to_render():
    """Copier la base de données locale vers le format Render"""
    
    # Chemins des bases de données
    source_db = 'data/visa_tracking.db'
    target_db = os.path.join(tempfile.gettempdir(), 'visa_system_render.db')
    
    print(f"📁 Source: {source_db}")
    print(f"📁 Cible: {target_db}")
    
    # Vérifier si la source existe
    if not os.path.exists(source_db):
        print("❌ Base de données source non trouvée!")
        return False
    
    try:
        # Copier la base de données
        shutil.copy2(source_db, target_db)
        print("✅ Base de données copiée avec succès!")
        
        # Vérifier la copie
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM clients')
        count = cursor.fetchone()[0]
        print(f"👥 Nombre de clients copiés: {count}")
        
        # Afficher quelques clients
        if count > 0:
            cursor.execute('SELECT client_id, full_name, visa_status FROM clients LIMIT 3')
            clients = cursor.fetchall()
            print("📋 Exemples de clients:")
            for client in clients:
                print(f"  - {client[0]}: {client[1]} | {client[2]}")
        
        conn.close()
        
        # Créer un fichier d'instruction pour Render
        instruction_file = 'RENDER_DEPLOY_INSTRUCTIONS.md'
        with open(instruction_file, 'w', encoding='utf-8') as f:
            f.write("""# Instructions de déploiement Render

## Base de données

La base de données a été préparée pour Render avec {count} clients.

### Configuration requise sur Render :

1. **Variables d'environnement** :
   ```
   RENDER=true
   PYTHONPATH=src
   ```

2. **Fichier de runtime** :
   Le fichier `runtime.txt` spécifie Python 3.9

3. **Build Command** :
   ```bash
   pip install --upgrade pip && pip install -r requirements.txt
   ```

4. **Start Command** :
   ```bash
   python vercel_app.py
   ```

### Structure de la base de données :

- **Emplacement** : `/tmp/visa_system_render.db`
- **Nombre de clients** : {count}
- **Langue** : Arabe et Français

### Vérification :

Après le déploiement, testez :
- `/health` - Health check
- `/` - Page d'accueil avec statistiques
- `/clients` - Liste des clients

### Données de test :

Si la base de données est vide sur Render, exécutez :
```bash
python populate_render_data.py
```
""")
        
        print(f"📝 Instructions créées dans: {instruction_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la copie: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Copie de la base de données pour Render...")
    success = copy_database_to_render()
    
    if success:
        print("\n✅ Préparation terminée!")
        print("💡 Les données sont maintenant prêtes pour Render.")
    else:
        print("\n❌ Échec de la préparation.")