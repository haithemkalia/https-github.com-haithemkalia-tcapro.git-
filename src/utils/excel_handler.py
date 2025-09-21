#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire Excel pour le système de suivi des visas TCA
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

class ExcelHandler:
    """Gestionnaire pour les opérations Excel"""
    
    def __init__(self):
        """Initialiser le gestionnaire Excel"""
        pass
    
    def read_excel_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Lire un fichier Excel"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
            
            # Lire le fichier Excel
            df = pd.read_excel(file_path)
            # Nettoyage colonnes: supprimer 'Unnamed:*' et garder uniquement les colonnes métiers demandées si présentes
            try:
                # Supprimer les colonnes Unnamed si présentes
                df = df.loc[:, [col for col in df.columns if not (isinstance(col, str) and col.strip().lower().startswith('unnamed:'))]]
                # Définir les colonnes à garder (avec variantes possibles)
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
                keep_cols = []
                for col in df.columns:
                    col_s = str(col)
                    if norm(col_s) in targets_norm:
                        keep_cols.append(col)
                if keep_cols:
                    df = df.loc[:, keep_cols]
            except Exception:
                pass
            return df
            
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier Excel: {e}")
            return None
    
    def analyze_excel_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyser la structure d'un fichier Excel"""
        try:
            df = self.read_excel_file(file_path)
            if df is None:
                return {}
            
            analysis = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'column_types': {col: str(df[col].dtype) for col in df.columns},
                'null_counts': {col: df[col].isnull().sum() for col in df.columns},
                'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
            }
            
            return analysis
            
        except Exception as e:
            print(f"Erreur lors de l'analyse: {e}")
            return {}
    
    def extract_client_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Extraire les données clients d'un fichier Excel"""
        try:
            df = self.read_excel_file(file_path)
            if df is None:
                return []
            
            clients_data = []
            
            for index, row in df.iterrows():
                client_data = {
                    'client_id': self._safe_str(row.get('معرف العميل', '')),
                    'full_name': self._safe_str(row.get('الاسم الكامل', '')),
                    'whatsapp_number': self._safe_str(row.get('رقم الواتساب', '')),
                    'application_date': self._safe_str(row.get('تاريخ التقديم', '')),
                    'transaction_date': self._safe_str(row.get('تاريخ استلام للسفارة', '')),
                    'passport_number': self._safe_str(row.get('رقم جواز السفر', '')),
                    'passport_status': self._safe_str(row.get('حالة جواز السفر', '')),
                    'nationality': self._safe_str(row.get('الجنسية', '')),
                    'visa_status': self._safe_str(row.get('حالة تتبع التأشيرة', 'التقديم')),
                    'processed_by': self._safe_str(row.get('من طرف', '')),
                    'summary': self._safe_str(row.get('الخلاصة', '')),
                    'notes': self._safe_str(row.get('ملاحضة', '')),
                    'responsible_employee': self._safe_str(row.get('اختيار الموظف', '')),
                    'original_row_number': index + 1
                }
                
                clients_data.append(client_data)
            
            return clients_data
            
        except Exception as e:
            print(f"Erreur lors de l'extraction des données: {e}")
            return []
    
    def export_to_excel(self, data: List[Dict[str, Any]], output_path: str) -> bool:
        """Exporter des données vers Excel"""
        try:
            if not data:
                return False
            
            df = pd.DataFrame(data)
            df.to_excel(output_path, index=False, engine='openpyxl')
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export Excel: {e}")
            return False
    
    def _safe_str(self, value: Any) -> str:
        """Convertir une valeur en string de manière sécurisée"""
        if pd.isna(value) or value is None:
            return ''
        return str(value).strip()
    
    def validate_excel_format(self, file_path: str) -> Dict[str, Any]:
        """Valider le format d'un fichier Excel"""
        try:
            analysis = self.analyze_excel_structure(file_path)
            
            validation = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'analysis': analysis
            }
            
            # Vérifications basiques
            if analysis.get('total_rows', 0) == 0:
                validation['errors'].append('Le fichier est vide')
                validation['is_valid'] = False
            
            if analysis.get('total_columns', 0) == 0:
                validation['errors'].append('Aucune colonne trouvée')
                validation['is_valid'] = False
            
            # Vérifier les colonnes importantes
            required_columns = ['الاسم الكامل', 'معرف العميل']
            missing_columns = []
            
            for col in required_columns:
                if col not in analysis.get('columns', []):
                    missing_columns.append(col)
            
            if missing_columns:
                validation['warnings'].append(f'Colonnes manquantes: {", ".join(missing_columns)}')
            
            return validation
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f'Erreur lors de la validation: {str(e)}'],
                'warnings': [],
                'analysis': {}
            }