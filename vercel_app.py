"""
Application Vercel avec gestion d'erreurs améliorée
"""
import sys
import os

# Ajouter le répertoire courant au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Forcer l'environnement Vercel
os.environ['VERCEL'] = 'true'

# Essayer d'importer Flask avec gestion d'erreur
try:
    from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response
    print("✅ Flask importé avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import Flask: {e}")
    print("📦 Installation de Flask...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask==2.3.3"])
    from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response
    print("✅ Flask installé et importé")

# Importer l'application principale
try:
    from app import app as flask_app
    print("✅ Application principale importée")
except Exception as e:
    print(f"❌ Erreur import application: {e}")
    # Créer une application minimale si l'import échoue
    flask_app = Flask(__name__)
    flask_app.config['SECRET_KEY'] = 'vercel-emergency-key'
    
    @flask_app.route('/')
    def emergency_index():
        return "Application en mode d'urgence - Erreur lors du chargement"
    
    @flask_app.route('/health')
    def emergency_health():
        return jsonify({"status": "emergency", "error": str(e)})

# Exporter l'application pour Vercel
app = flask_app

if __name__ == "__main__":
    app.run(debug=True)