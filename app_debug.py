# Import des modules Flask
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import urllib.parse
from flask.json.provider import DefaultJSONProvider
import numpy as np

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.database_manager import DatabaseManager
from controllers.client_controller import ClientController
from controllers.whatsapp_controller import WhatsAppController
from utils.excel_handler import ExcelHandler
from models.client import Client

# Configuration Flask pour debug
def convert_to_json_serializable(obj):
    """Convertit les types numpy/pandas en types Python natifs pour la sérialisation JSON"""
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8,
                        np.uint64, np.uint32, np.uint16, np.uint8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_json_serializable(item) for item in obj)
    else:
        return obj

class NumpyJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        return convert_to_json_serializable(obj)

# Configuration de base
app = Flask(__name__)
app.secret_key = 'tca_visa_tracking_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Activer le JSON provider global pour numpy/pandas
app.json = NumpyJSONProvider(app)

# Créer le dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialiser les contrôleurs
db_manager = DatabaseManager()
client_controller = ClientController(db_manager)
whatsapp_controller = WhatsAppController(db_manager)
excel_handler = ExcelHandler()

@app.context_processor
def inject_rtl_support():
    """Injecter le support RTL dans tous les templates"""
    return {
        'rtl_languages': ['ar', 'fa', 'he', 'ur'],
        'current_language': 'ar',  # Ou déterminer dynamiquement
        'is_rtl': True  # Pour l'arabe
    }

@app.route('/')
def debug_home():
    return 'TCA Debug app is running'

@app.route('/api/test-serialization')
def test_serialization():
    import numpy as np
    import pandas as pd
    data = {
        'numpy_int64': np.int64(42),
        'numpy_float64': np.float64(3.14),
        'numpy_bool': True,
        'numpy_array': np.array([1, 2, 3]),
        'pandas_timestamp': pd.Timestamp('2025-09-26 12:34:56'),
        'pandas_series': pd.Series([1, 2, 3], name='vals'),
        'pandas_dataframe': pd.DataFrame({'a': [1, 2], 'b': [np.int64(5), np.float64(2.5)]}),
    }
    return jsonify(data)

@app.route('/health')
def health_check():
    """Endpoint de santé pour vérifier le serveur et la DB"""
    try:
        # Tester la connexion DB
        db_manager.get_connection()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'environment': 'development'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/stats')
def get_stats_api():
    """API pour récupérer les statistiques (debug)"""
    try:
        all_clients, total_clients = client_controller.get_all_clients(1, 10000)
        stats = {
            'total_clients': int(total_clients),
            'by_status': {},
            'by_nationality': {},
            'by_employee': {},
            'timestamp': datetime.now().isoformat()
        }

        status_counts = {}
        nationality_counts = {}
        employee_counts = {}

        for client in all_clients:
            status = client.get('visa_status', '')
            status_counts[status] = status_counts.get(status, 0) + 1

            nationality = client.get('nationality', '')
            if nationality:
                nationality_counts[nationality] = nationality_counts.get(nationality, 0) + 1

            employee = client.get('responsible_employee', '')
            if employee:
                employee_counts[employee] = employee_counts.get(employee, 0) + 1

        for status in Client.VISA_STATUS_OPTIONS:
            stats['by_status'][status] = int(status_counts.get(status, 0))
        for nationality in Client.NATIONALITY_OPTIONS:
            stats['by_nationality'][nationality] = int(nationality_counts.get(nationality, 0))
        for employee in Client.EMPLOYEE_OPTIONS:
            stats['by_employee'][employee] = int(employee_counts.get(employee, 0))

        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart-data')
def get_chart_data_api():
    """API pour récupérer les données du graphique (debug)"""
    try:
        all_clients, _ = client_controller.get_all_clients(1, 10000)
        status_counts = {}
        for client in all_clients:
            status = client.get('visa_status', '')
            if status:
                status_counts[status] = status_counts.get(status, 0) + 1

        labels = [s for s, count in status_counts.items() if count > 0]
        values = [status_counts[s] for s in labels]

        chart_data = {
            'labels': labels,
            'values': values,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🛂 نظام تتبع التأشيرات الذكي - TCA (Debug Mode)")
    print("شركة تونس للاستشارات والخدمات")
    print("\n🌐 Démarrage du serveur web...")
    print("📱 Interface web disponible sur: http://localhost:5000")
    print("\n⚡ Serveur en cours d'exécution...")
    print("⚠️  Mode Debug activé")
    
    app.run(debug=True, host='0.0.0.0', port=5000)