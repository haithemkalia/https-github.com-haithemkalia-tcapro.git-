#!/bin/bash
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

# Installer gunicorn si nécessaire
echo "📦 Installation de Gunicorn..."
pip install gunicorn

# Démarrer l'application avec Gunicorn
echo "🌐 Démarrage du serveur avec Gunicorn..."
gunicorn app:app -c gunicorn_config.py
