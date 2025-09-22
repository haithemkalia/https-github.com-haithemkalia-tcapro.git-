# Instructions de déploiement Render

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
