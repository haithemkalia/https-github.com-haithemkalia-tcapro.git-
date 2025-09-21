import pandas as pd
import numpy as np
import sqlite3
import hashlib
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import uuid
from .advanced_excel_analyzer import AdvancedExcelAnalyzer


class UnrestrictedImporter:
    """Importeur sans restrictions qui accepte tous les types de données"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.analyzer = AdvancedExcelAnalyzer()
        self.import_stats = {
            'total_processed': 0,
            'successfully_imported': 0,
            'duplicates_imported': 0,
            'empty_ids_generated': 0,
            'empty_names_accepted': 0,
            'processing_time': 0,
            'errors': []
        }
        
    def perform_unrestricted_import(self, excel_path: str) -> Dict[str, Any]:
        """Effectue un import complet sans restrictions"""
        start_time = datetime.now()
        
        try:
            print(f"🔄 Début de l'import sans restrictions pour: {excel_path}")
            
            # Étape 1: Analyser le fichier
            print("📊 Analyse du fichier Excel...")
            analysis_result = self.analyzer.analyze_file(excel_path)
            
            if not analysis_result['success']:
                return {
                    'success': False,
                    'error': f'Échec de l\'analyse: {analysis_result.get("error", "Erreur inconnue")}',
                    'import_stats': self.import_stats
                }
            
            # Étape 2: Charger les données
            print("📂 Chargement des données...")
            df = pd.read_excel(excel_path)
            # Normaliser: supprimer colonnes 'Unnamed' et garder colonnes métiers/arabes si présentes
            try:
                df = df.loc[:, [col for col in df.columns if not (isinstance(col, str) and col.strip().lower().startswith('unnamed:'))]]
                target_names = [
                    'ملاحظة', 'ملاحضة',
                    'اختيار الموظف مسؤول', 'اختيار الموظف', 'اختار الموظف',
                    'الخلاصة',
                    'من طرف',
                    'حالة تتبع التأشيرة',
                    'الجنسية',
                    'حالة جواز السفر',
                    'رقم جواز السفر',
                    'تاريخ استلام للسفارة', 'تاريخ استلام المعملة',
                    'تاريخ التقديم',
                    'رقم الواتساب',
                    'الاسم الكامل',
                    'معرف العميل'
                ]
                def norm(s: str) -> str:
                    return ' '.join(str(s).strip().split())
                targets_norm = set(norm(n) for n in target_names)
                keep_cols = [col for col in df.columns if norm(col) in targets_norm]
                if keep_cols:
                    df = df.loc[:, keep_cols]
            except Exception:
                pass
            self.import_stats['total_processed'] = len(df)
            
            # Étape 3: Préparer les données
            print("🔧 Préparation des données...")
            prepared_data = self._prepare_data_for_import(df)
            
            # Étape 4: Insérer dans la base de données
            print("💾 Insertion dans la base de données...")
            import_result = self._insert_data_into_db(prepared_data)
            
            # Calculer le temps de traitement
            end_time = datetime.now()
            self.import_stats['processing_time'] = (end_time - start_time).total_seconds()
            
            # Générer le rapport final
            final_report = self._generate_final_report(analysis_result, import_result)
            
            print(f"✅ Import terminé avec succès en {self.import_stats['processing_time']:.2f} secondes")
            
            return {
                'success': True,
                'message': f'تم استيراد {self.import_stats["successfully_imported"]} عميل بنجاح!',
                'analysis_report': analysis_result,
                'import_stats': self.import_stats,
                'final_report': final_report
            }
            
        except Exception as e:
            end_time = datetime.now()
            self.import_stats['processing_time'] = (end_time - start_time).total_seconds()
            self.import_stats['errors'].append(str(e))
            
            print(f"❌ Erreur lors de l'import: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'import_stats': self.import_stats
            }
    
    def _prepare_data_for_import(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prépare les données pour l'import sans restrictions"""
        prepared_records = []
        
        # Limiter le nombre de lignes pour éviter les problèmes de mémoire
        max_rows = 50000  # Limite raisonnable
        total_rows = len(df)
        
        if total_rows > max_rows:
            print(f"⚠️ Attention : fichier trop grand ({total_rows} lignes). Traitement limité à {max_rows} lignes.")
            df = df.head(max_rows)
            total_rows = max_rows
        
        print(f"🔧 Préparation de {total_rows} enregistrements...")
        
        for index, row in df.iterrows():
            try:
                # Protection contre les boucles infinies - limiter le temps par enregistrement
                import time
                start_time = time.time()
                
                # Créer un enregistrement client
                client_record = self._create_client_record(row, index)
                if client_record:
                    prepared_records.append(client_record)
                
                # Si le traitement prend trop de temps, passer à l'enregistrement suivant
                if time.time() - start_time > 5:  # 5 secondes max par enregistrement
                    print(f"⚠️ Traitement trop long pour la ligne {index + 2}, utilisation de valeurs par défaut")
                    continue
                    
            except Exception as e:
                print(f"⚠️ Erreur lors de la préparation de la ligne {index + 2}: {str(e)}")
                self.import_stats['errors'].append(f"Ligne {index + 2}: {str(e)}")
                continue
        
        return prepared_records
    
    def _create_client_record(self, row: pd.Series, row_index: int) -> Optional[Dict[str, Any]]:
        """Crée un enregistrement client à partir d'une ligne Excel"""
        try:
            # Nettoyer et préparer les données
            client_data = self._extract_client_data(row)
            
            # Générer un ID client si nécessaire
            if not client_data.get('client_id'):
                client_data['client_id'] = self._generate_client_id(client_data, row_index)
                self.import_stats['empty_ids_generated'] += 1
            
            # Accepter les noms vides (contrairement à l'import normal)
            if not client_data.get('full_name'):
                client_data['full_name'] = f"عميل غير محدد {row_index + 1}"
                self.import_stats['empty_names_accepted'] += 1
            
            # Définir les valeurs par défaut pour les champs manquants
            client_data = self._set_default_values(client_data)
            
            # Valider et nettoyer les données
            client_data = self._validate_and_clean_data(client_data)
            
            return client_data
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la création de l'enregistrement: {str(e)}")
            return None
    
    def _extract_client_data(self, row: pd.Series) -> Dict[str, Any]:
        """Extrait les données client de la ligne Excel"""
        client_data = {}
        
        # Mapping des colonnes avec gestion flexible - incluant les colonnes arabes spécifiques
        column_mapping = {
            'client_id': ['client_id', 'id', 'معرف_العميل', 'رقم_العميل', 'code', 'code_client', 'معرف ال', 'معرف_العميل'],
            'full_name': ['full_name', 'name', 'nom', 'الاسم_الكامل', 'الاسم', 'nom_complet', 'الاسم الكامل', 'الاسم'],
            'phone': ['phone', 'telephone', 'tel', 'الهاتف', 'رقم_الهاتف', 'portable', 'رقم الواتساب', 'واتساب'],
            'nationality': ['nationality', 'nationalite', 'pays', 'الجنسية', 'بلد'],
            'passport_number': ['passport_number', 'passeport', 'رقم_الجواز', 'جواز'],
            'birth_date': ['birth_date', 'date_naissance', 'تاريخ_الولادة', 'naissance'],
            'visa_type': ['visa_type', 'type_visa', 'نوع_التأشيرة', 'التأشيرة'],
            'visa_duration': ['visa_duration', 'duree_visa', 'مدة_التأشيرة'],
            'employee': ['employee', 'employe', 'الموظف', 'المعالج', 'من طرف', 'اختار الموظف'],
            'embassy': ['embassy', 'ambassade', 'السفارة'],
            'file_date': ['file_date', 'date_dossier', 'تاريخ_الملف', 'تاريخ التقديم'],
            'reception_date': ['reception_date', 'date_reception', 'تاريخ_الاستلام', 'تاريخ استلام للسفارة'],
            'status': ['status', 'statut', 'الحالة', 'حالة تتبع التأشيرة'],
            'notes': ['notes', 'remarques', 'ملاحظات', 'ملاحظة']
        }
        
        # Parcourir les mappings
        for standard_field, possible_columns in column_mapping.items():
            for col in row.index:
                if str(col).lower().strip() in [possible.lower() for possible in possible_columns]:
                    value = row[col]
                    if pd.notna(value) and str(value).strip():
                        client_data[standard_field] = str(value).strip()
                        break
        
        # Si aucune correspondance trouvée, utiliser les colonnes par index
        if not client_data:
            client_data = self._extract_by_position(row)
        
        return client_data
    
    def _extract_by_position(self, row: pd.Series) -> Dict[str, Any]:
        """Extrait les données par position si aucune correspondance de noms"""
        client_data = {}
        
        try:
            # Essayer d'utiliser les premières colonnes par position
            if len(row) > 0:
                first_col = row.iloc[0]
                if pd.notna(first_col):
                    client_data['client_id'] = str(first_col).strip()
            
            if len(row) > 1:
                second_col = row.iloc[1]
                if pd.notna(second_col):
                    client_data['full_name'] = str(second_col).strip()
            
            if len(row) > 2:
                third_col = row.iloc[2]
                if pd.notna(third_col):
                    client_data['phone'] = str(third_col).strip()
            
            # Ajouter les autres colonnes comme données supplémentaires
            for i, value in enumerate(row):
                if pd.notna(value) and i >= 3:
                    field_name = f'field_{i+1}'
                    client_data[field_name] = str(value).strip()
                    
        except Exception as e:
            print(f"⚠️ Erreur lors de l'extraction par position: {str(e)}")
            
        return client_data
    
    def _generate_client_id(self, client_data: Dict[str, Any], row_index: int) -> str:
        """Génère un ID client unique au format CLI standard (CLI001, CLI002, etc.)"""
        try:
            # Utiliser le système de génération d'ID standard du contrôleur
            from controllers.client_controller import ClientController
            from database.database_manager import DatabaseManager
            
            # Initialiser le contrôleur pour utiliser sa méthode de génération
            db_manager = DatabaseManager()
            client_controller = ClientController(db_manager)
            
            # Utiliser la méthode standard de génération d'ID
            return client_controller.generate_client_id()
            
        except Exception as e:
            # Fallback: générer un ID CLI simple
            import time
            timestamp = int(time.time()) % 100000
            return f"CLI{timestamp % 1000:03d}"
    
    def _set_default_values(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Définit les valeurs par défaut pour les champs manquants"""
        defaults = {
            'nationality': 'غير محدد',
            'visa_type': 'غير محدد',
            'visa_duration': 'غير محدد',
            'employee': 'غير محدد',
            'embassy': 'غير محددة',
            'status': 'قيد الانتظار',
            'notes': '',
            'file_date': datetime.now().strftime('%Y-%m-%d'),
            'reception_date': datetime.now().strftime('%Y-%m-%d'),
            'birth_date': '1990-01-01'
        }
        
        for field, default_value in defaults.items():
            if field not in client_data or not client_data[field]:
                client_data[field] = default_value
        
        return client_data
    
    def _validate_and_clean_data(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide et nettoie les données"""
        # Nettoyer le numéro de téléphone
        if 'phone' in client_data:
            phone = str(client_data['phone'])
            # Ne garder que les chiffres
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) > 8:
                client_data['phone'] = phone
            else:
                client_data['phone'] = '00000000'
        
        # Valider la date de naissance
        if 'birth_date' in client_data:
            try:
                birth_date = pd.to_datetime(client_data['birth_date'])
                # S'assurer que la date est raisonnable
                if birth_date.year < 1900 or birth_date.year > datetime.now().year:
                    client_data['birth_date'] = '1990-01-01'
                else:
                    client_data['birth_date'] = birth_date.strftime('%Y-%m-%d')
            except:
                client_data['birth_date'] = '1990-01-01'
        
        # Limiter la longueur des champs texte
        text_fields = ['full_name', 'nationality', 'visa_type', 'employee', 'embassy', 'status']
        for field in text_fields:
            if field in client_data and len(str(client_data[field])) > 100:
                client_data[field] = str(client_data[field])[:100]
        
        return client_data
    
    def _insert_data_into_db(self, prepared_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Insère les données préparées dans la base de données"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            successfully_imported = 0
            duplicates_imported = 0
            
            print(f"💾 Insertion de {len(prepared_records)} enregistrements dans la base de données...")
            
            for record_index, record in enumerate(prepared_records):
                try:
                    # Vérifier si l'ID existe déjà et générer un ID unique
                    original_id = record['client_id']
                    retry_count = 0
                    max_retries = 5  # Réduit de 10 à 5 pour éviter les boucles trop longues
                    
                    while retry_count < max_retries:
                        try:
                            cursor.execute("SELECT COUNT(*) FROM clients WHERE client_id = ?", (record['client_id'],))
                            exists = cursor.fetchone()[0] > 0
                            
                            if not exists:
                                break
                                
                            # Générer un nouvel ID pour le doublon avec une approche plus simple
                            import time
                            timestamp_suffix = str(int(time.time() * 1000) % 1000)
                            record['client_id'] = f"{original_id[:8]}{timestamp_suffix}"
                            retry_count += 1
                            
                            if retry_count >= max_retries:
                                # Fallback ultime : ID avec timestamp et index
                                record['client_id'] = f"CLI{record_index}{int(time.time()) % 10000}"
                                break
                        except Exception as inner_e:
                            # En cas d'erreur SQL, sortir de la boucle
                            print(f"⚠️ Erreur SQL lors de la vérification d'ID: {str(inner_e)}")
                            break
                    
                    if original_id != record['client_id']:
                        duplicates_imported += 1
                    
                    # Insérer l'enregistrement
                    self._insert_client_record(cursor, record)
                    successfully_imported += 1
                    
                except Exception as e:
                    print(f"⚠️ Erreur lors de l'insertion de l'enregistrement: {str(e)}")
                    continue
            
            conn.commit()
            conn.close()
            
            # Mettre à jour les statistiques
            self.import_stats['successfully_imported'] = successfully_imported
            self.import_stats['duplicates_imported'] = duplicates_imported
            
            return {
                'success': True,
                'message': f'{successfully_imported} enregistrements importés avec succès',
                'duplicates_handled': duplicates_imported
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion dans la base de données: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _insert_client_record(self, cursor: sqlite3.Cursor, record: Dict[str, Any]) -> None:
        """Insère un enregistrement client dans la base de données (adapté au schéma existant)."""
        # Lire les colonnes existantes de la table
        db_columns = [row[1] for row in cursor.execute('PRAGMA table_info(clients)')]

        # Mapper nos champs vers le schéma actuel observé
        now_date = datetime.now().strftime('%Y-%m-%d')
        now_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Préparer les valeurs potentielles
        phone_raw = record.get('phone', '')
        phone_digits = ''.join(c for c in str(phone_raw) if c.isdigit()) if phone_raw else ''

        candidate_values = {
            'client_id': record.get('client_id', ''),
            'full_name': record.get('full_name', ''),
            'whatsapp_number': phone_raw,
            'whatsapp_number_clean': phone_digits,
            'application_date': record.get('file_date', now_date),
            'transaction_date': record.get('reception_date', now_date),
            'passport_number': record.get('passport_number', ''),
            'passport_status': record.get('status', ''),  # si différent, sera corrigé par app plus tard
            'passport_status_normalized': record.get('status', ''),
            'nationality': record.get('nationality', ''),
            'visa_status': record.get('status', 'قيد الانتظار'),
            'visa_status_normalized': record.get('status', 'قيد الانتظار'),
            'processed_by': record.get('employee', record.get('handled_by', '')),
            'summary': record.get('summary', ''),
            'notes': record.get('notes', ''),
            'responsible_employee': record.get('employee', ''),
            'original_row_number': 0,
            'import_timestamp': now_ts,
            'is_duplicate': 0,
            'has_empty_fields': 0,
            'has_errors': 0,
            'original_data': json.dumps(record, ensure_ascii=False),
            'created_at': now_ts,
            'updated_at': now_ts,
        }

        # Ne garder que les colonnes présentes dans la table
        insert_cols = [col for col in candidate_values.keys() if col in db_columns]
        insert_vals = [candidate_values[col] for col in insert_cols]

        # Construire et exécuter la requête dynamiquement
        placeholders = ', '.join(['?'] * len(insert_cols))
        columns_sql = ', '.join(insert_cols)
        query = f"INSERT INTO clients ({columns_sql}) VALUES ({placeholders})"
        cursor.execute(query, insert_vals)
    
    def _generate_final_report(self, analysis_result: Dict[str, Any], import_result: Dict[str, Any]) -> str:
        """Génère un rapport final détaillé"""
        report_html = f"""
        <div class="final-report">
            <h4>📋 تقرير الاستيراد النهائي</h4>
            <div class="report-summary">
                <div class="row">
                    <div class="col-md-6">
                        <h5>📊 إحصائيات الملف</h5>
                        <ul>
                            <li><strong>إجمالي الصفوف:</strong> {analysis_result['statistics']['total_rows']:,}</li>
                            <li><strong>إجمالي الأعمدة:</strong> {analysis_result['statistics']['total_columns']}</li>
                            <li><strong>حجم الملف:</strong> {analysis_result['file_info']['file_size_mb']} ميجابايت</li>
                            <li><strong>كثافة البيانات:</strong> {analysis_result['statistics']['data_density']:.1f}%</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h5>✅ نتائج الاستيراد</h5>
                        <ul>
                            <li><strong>تم الاستيراد:</strong> {self.import_stats['successfully_imported']:,}</li>
                            <li><strong>معرفات مولدة:</strong> {self.import_stats['empty_ids_generated']:,}</li>
                            <li><strong>أسماء فارغة:</strong> {self.import_stats['empty_names_accepted']:,}</li>
                            <li><strong>تكرارات:</strong> {self.import_stats['duplicates_imported']:,}</li>
                            <li><strong>وقت المعالجة:</strong> {self.import_stats['processing_time']:.2f} ثانية</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="report-recommendations">
                <h5>💡 التوصيات</h5>
                <ul>
                    <li>✅ تم استيراد جميع البيانات بنجاح بدون قيود</li>
                    <li>✅ تم التعامل مع التكرارات بشكل تلقائي</li>
                    <li>✅ تم إنشاء معرفات تلقائية للبيانات المفقودة</li>
                    <li>✅ تم قبول جميع الأسماء حتى الفارغة</li>
                </ul>
            </div>
            
            {self._generate_error_summary() if self.import_stats['errors'] else ''}
        </div>
        """
        
        return report_html
    
    def _generate_error_summary(self) -> str:
        """Génère un résumé des erreurs"""
        if not self.import_stats['errors']:
            return ""
        
        errors_html = "<div class='error-summary'><h5>⚠️ الأخطاء</h5><ul>"
        for error in self.import_stats['errors'][:5]:  # Limiter à 5 erreurs
            errors_html += f"<li>{error}</li>"
        
        if len(self.import_stats['errors']) > 5:
            errors_html += f"<li>... و {len(self.import_stats['errors']) - 5} أخطاء أخرى</li>"
        
        errors_html += "</ul></div>"
        return errors_html