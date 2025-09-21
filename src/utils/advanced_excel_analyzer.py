import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import hashlib
import json
from datetime import datetime
import os


class AdvancedExcelAnalyzer:
    """Analyseur avancé de fichiers Excel pour détecter les problèmes et optimiser l'import"""
    
    def __init__(self):
        self.analysis_results = {}
        self.errors = []
        self.warnings = []
        
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyse complète d'un fichier Excel"""
        try:
            # Charger le fichier Excel
            df = pd.read_excel(file_path)
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
            
            # Analyse de base
            basic_analysis = self._analyze_basic_structure(df)
            
            # Analyse des colonnes
            columns_analysis = self._analyze_columns(df)
            
            # Analyse des données
            data_analysis = self._analyze_data_quality(df)
            
            # Analyse des doublons
            duplicates_analysis = self._analyze_duplicates(df)
            
            # Analyse de la mémoire
            memory_analysis = self._analyze_memory_usage(df)
            
            # Générer le rapport complet
            self.analysis_results = {
                'success': True,
                'file_info': {
                    'filename': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path),
                    'file_size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2),
                    'analysis_date': datetime.now().isoformat()
                },
                'basic_structure': basic_analysis,
                'columns_analysis': columns_analysis,
                'data_quality': data_analysis,
                'duplicates_analysis': duplicates_analysis,
                'memory_usage': memory_analysis,
                'statistics': {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'data_density': ((df.size - df.isnull().sum().sum()) / df.size * 100),
                    'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
                },
                'recommendations': self._generate_recommendations(df),
                'errors': self.errors,
                'warnings': self.warnings
            }
            
            return self.analysis_results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_info': {
                    'filename': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                    'analysis_date': datetime.now().isoformat()
                }
            }
    
    def _analyze_basic_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse la structure de base du DataFrame"""
        return {
            'shape': df.shape,
            'total_cells': df.size,
            'column_names': list(df.columns),
            'column_count': len(df.columns),
            'row_count': len(df),
            'index_type': str(type(df.index)),
            'has_multiindex': isinstance(df.index, pd.MultiIndex)
        }
    
    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse détaillée des colonnes"""
        column_details = {}
        
        for col in df.columns:
            col_data = df[col]
            col_info = {
                'name': col,
                'dtype': str(col_data.dtype),
                'null_count': col_data.isnull().sum(),
                'non_null_count': col_data.notnull().sum(),
                'null_percentage': round((col_data.isnull().sum() / len(df)) * 100, 2),
                'unique_count': col_data.nunique(),
                'unique_percentage': round((col_data.nunique() / len(df)) * 100, 2),
                'is_numeric': pd.api.types.is_numeric_dtype(col_data),
                'is_datetime': pd.api.types.is_datetime64_any_dtype(col_data),
                'is_string': pd.api.types.is_string_dtype(col_data),
                'memory_usage': round(col_data.memory_usage(deep=True) / 1024, 2)  # KB
            }
            
            # Analyse selon le type de données
            if pd.api.types.is_numeric_dtype(col_data):
                col_info.update(self._analyze_numeric_column(col_data))
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                col_info.update(self._analyze_datetime_column(col_data))
            elif pd.api.types.is_string_dtype(col_data):
                col_info.update(self._analyze_string_column(col_data))
            
            column_details[col] = col_info
        
        return {
            'total_columns': len(df.columns),
            'column_details': column_details,
            'numeric_columns': [col for col, info in column_details.items() if info['is_numeric']],
            'datetime_columns': [col for col, info in column_details.items() if info['is_datetime']],
            'string_columns': [col for col, info in column_details.items() if info['is_string']],
            'high_null_columns': [col for col, info in column_details.items() if info['null_percentage'] > 50],
            'unique_columns': [col for col, info in column_details.items() if info['unique_count'] == len(df)]
        }
    
    def _analyze_numeric_column(self, col_data: pd.Series) -> Dict[str, Any]:
        """Analyse d'une colonne numérique"""
        return {
            'min': col_data.min(),
            'max': col_data.max(),
            'mean': col_data.mean(),
            'median': col_data.median(),
            'std': col_data.std(),
            'zeros_count': (col_data == 0).sum(),
            'negative_count': (col_data < 0).sum(),
            'outliers_count': self._count_outliers(col_data)
        }
    
    def _analyze_datetime_column(self, col_data: pd.Series) -> Dict[str, Any]:
        """Analyse d'une colonne de dates"""
        return {
            'min_date': col_data.min(),
            'max_date': col_data.max(),
            'date_range_days': (col_data.max() - col_data.min()).days if col_data.notnull().sum() > 1 else 0,
            'future_dates_count': (col_data > datetime.now()).sum(),
            'very_old_dates_count': (col_data < datetime.now() - pd.DateOffset(years=10)).sum()
        }
    
    def _analyze_string_column(self, col_data: pd.Series) -> Dict[str, Any]:
        """Analyse d'une colonne de texte"""
        non_null_data = col_data.dropna()
        return {
            'avg_length': non_null_data.str.len().mean() if len(non_null_data) > 0 else 0,
            'max_length': non_null_data.str.len().max() if len(non_null_data) > 0 else 0,
            'min_length': non_null_data.str.len().min() if len(non_null_data) > 0 else 0,
            'empty_strings': (non_null_data == '').sum(),
            'whitespace_only': non_null_data.str.strip().eq('').sum(),
            'most_common': non_null_data.value_counts().head(5).to_dict() if len(non_null_data) > 0 else {}
        }
    
    def _analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse de la qualité des données"""
        total_cells = df.size
        null_cells = df.isnull().sum().sum()
        
        return {
            'null_cells': null_cells,
            'null_percentage': round((null_cells / total_cells) * 100, 2),
            'complete_rows': df.dropna().shape[0],
            'complete_rows_percentage': round((df.dropna().shape[0] / len(df)) * 100, 2),
            'data_consistency_score': self._calculate_consistency_score(df),
            'potential_issues': self._detect_data_issues(df)
        }
    
    def _analyze_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse des doublons"""
        complete_duplicates = df.duplicated().sum()
        
        # Chercher des doublons partiels (basés sur les colonnes clés)
        key_columns = [col for col in df.columns if any(keyword in col.lower() 
                      for keyword in ['id', 'name', 'client', 'phone', 'email'])]
        
        partial_duplicates = 0
        if key_columns:
            partial_duplicates = df.duplicated(subset=key_columns).sum()
        
        return {
            'complete_duplicates': complete_duplicates,
            'complete_duplicates_percentage': round((complete_duplicates / len(df)) * 100, 2),
            'partial_duplicates': partial_duplicates,
            'partial_duplicates_percentage': round((partial_duplicates / len(df)) * 100, 2) if key_columns else 0,
            'unique_rows': len(df) - complete_duplicates,
            'key_columns_used': key_columns
        }
    
    def _analyze_memory_usage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse de l'utilisation mémoire"""
        memory_usage = df.memory_usage(deep=True)
        total_memory = memory_usage.sum()
        
        return {
            'total_memory_bytes': total_memory,
            'total_memory_mb': round(total_memory / (1024 * 1024), 2),
            'memory_per_column': {col: round(usage / 1024, 2) for col, usage in memory_usage.items()},
            'estimated_processing_time': self._estimate_processing_time(len(df), len(df.columns))
        }
    
    def _count_outliers(self, col_data: pd.Series) -> int:
        """Compte les valeurs aberrantes dans une colonne numérique"""
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return ((col_data < lower_bound) | (col_data > upper_bound)).sum()
    
    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calcule un score de cohérence des données"""
        # Score basé sur le pourcentage de données non nulles et la cohérence des types
        null_score = 100 - ((df.isnull().sum().sum() / df.size) * 100)
        type_consistency = 0
        
        # Vérifier la cohérence des types dans chaque colonne
        for col in df.columns:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                # Compter les types uniques
                unique_types = col_data.apply(type).nunique()
                if unique_types == 1:
                    type_consistency += 100
                else:
                    type_consistency += max(0, 100 - (unique_types * 20))
        
        type_consistency_score = type_consistency / len(df.columns) if len(df.columns) > 0 else 0
        
        return round((null_score + type_consistency_score) / 2, 2)
    
    def _detect_data_issues(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Détecte les problèmes potentiels dans les données"""
        issues = []
        
        for col in df.columns:
            col_data = df[col].dropna()
            
            if len(col_data) == 0:
                issues.append({
                    'type': 'empty_column',
                    'column': col,
                    'severity': 'high',
                    'message': f'La colonne "{col}" est complètement vide'
                })
                continue
            
            # Vérifier les incohérences de type
            unique_types = col_data.apply(type).nunique()
            if unique_types > 1:
                issues.append({
                    'type': 'type_inconsistency',
                    'column': col,
                    'severity': 'medium',
                    'message': f'La colonne "{col}" contient {unique_types} types de données différents'
                })
            
            # Vérifier les valeurs extrêmes pour les colonnes numériques
            if pd.api.types.is_numeric_dtype(col_data):
                outliers_count = self._count_outliers(col_data)
                if outliers_count > len(col_data) * 0.1:  # Plus de 10% de valeurs aberrantes
                    issues.append({
                        'type': 'too_many_outliers',
                        'column': col,
                        'severity': 'medium',
                        'message': f'La colonne "{col}" contient beaucoup de valeurs aberrantes ({outliers_count})'
                    })
        
        return issues
    
    def _estimate_processing_time(self, rows: int, columns: int) -> str:
        """Estime le temps de traitement en fonction de la taille des données"""
        # Estimation basée sur des tests empiriques
        base_time = (rows * columns) / 10000  # Temps de base en secondes
        
        if rows < 1000:
            estimated_time = base_time * 0.5
        elif rows < 10000:
            estimated_time = base_time * 1.0
        elif rows < 50000:
            estimated_time = base_time * 1.5
        else:
            estimated_time = base_time * 2.0
        
        if estimated_time < 60:
            return f"{round(estimated_time, 1)}s"
        else:
            minutes = estimated_time / 60
            return f"{round(minutes, 1)}min"
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Génère des recommandations basées sur l'analyse"""
        recommendations = []
        
        # Recommandations basées sur la taille
        if len(df) > 50000:
            recommendations.append("Fichier volumineux : envisagez un traitement par lots")
        
        # Recommandations basées sur les valeurs manquantes
        null_percentage = (df.isnull().sum().sum() / df.size) * 100
        if null_percentage > 30:
            recommendations.append("Beaucoup de valeurs manquantes : nettoyez les données avant l'import")
        
        # Recommandations basées sur les doublons
        duplicates = df.duplicated().sum()
        if duplicates > len(df) * 0.1:
            recommendations.append("Nombreux doublons : nettoyez les données avant l'import")
        
        # Recommandations basées sur la mémoire
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        if memory_mb > 100:
            recommendations.append("Utilisation mémoire élevée : surveillez les ressources système")
        
        return recommendations