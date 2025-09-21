#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôleur pour l'analyse avancée du tableau de bord
"""

from typing import Dict, Any, List
import json
from datetime import datetime

from src.services.analytics_service import AnalyticsService

class AnalyticsController:
    """Contrôleur pour gérer les analyses avancées"""
    
    def __init__(self, db_manager):
        self.analytics_service = AnalyticsService(db_manager)
        self.db_manager = db_manager
    
    def get_comprehensive_dashboard_data(self) -> Dict[str, Any]:
        """Obtenir toutes les données pour le tableau de bord avancé"""
        
        try:
            # Obtenir l'analyse complète
            analysis = self.analytics_service.get_comprehensive_analysis()
            
            # Ajouter des métadonnées
            analysis['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'data_source': 'visa_system.db',
                'version': '1.0',
                'total_records_analyzed': analysis['overview']['total_clients']
            }
            
            return analysis
            
        except Exception as e:
            print(f"Erreur lors de la génération de l'analyse: {e}")
            return self._get_error_response(str(e))
    
    def get_executive_report(self) -> Dict[str, Any]:
        """Obtenir le rapport exécutif"""
        
        try:
            analysis = self.analytics_service.get_comprehensive_analysis()
            
            executive_report = {
                'summary': analysis['detailed_reports']['executive_summary'],
                'key_metrics': analysis['overview'],
                'performance': analysis['performance_metrics'],
                'trends': analysis['trends'],
                'recommendations': analysis['detailed_reports']['recommendations']
            }
            
            return executive_report
            
        except Exception as e:
            return self._get_error_response(str(e))
    
    def get_operational_dashboard(self) -> Dict[str, Any]:
        """Obtenir les données du tableau de bord opérationnel"""
        
        try:
            analysis = self.analytics_service.get_comprehensive_analysis()
            
            operational_data = {
                'overview': analysis['overview'],
                'visa_status': analysis['visa_status_analysis'],
                'employee_performance': analysis['employee_analysis'],
                'quality_metrics': analysis['quality_metrics'],
                'operational_report': analysis['detailed_reports']['operational_report']
            }
            
            return operational_data
            
        except Exception as e:
            return self._get_error_response(str(e))
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques en temps réel"""
        
        try:
            # Récupérer les données récentes
            all_clients, total_count = self.db_manager.get_all_clients(page=1, per_page=10000)
            
            # Convertir les Row objects en dictionnaires
            all_clients = [dict(client) for client in all_clients]
            
            # Calculer les stats en temps réel
            real_time_stats = {
                'total_clients': total_count,
                'active_today': self._count_active_today(all_clients),
                'completed_today': self._count_completed_today(all_clients),
                'pending_reviews': self._count_pending_reviews(all_clients),
                'system_status': 'operational',
                'last_update': datetime.now().isoformat()
            }
            
            return real_time_stats
            
        except Exception as e:
            return self._get_error_response(str(e))
    
    def export_analysis_report(self, report_type: str = 'comprehensive') -> Dict[str, Any]:
        """Exporter un rapport d'analyse"""
        
        try:
            if report_type == 'comprehensive':
                data = self.get_comprehensive_dashboard_data()
            elif report_type == 'executive':
                data = self.get_executive_report()
            elif report_type == 'operational':
                data = self.get_operational_dashboard()
            else:
                data = self.get_real_time_stats()
            
            # Préparer les données pour l'export
            export_data = {
                'report_type': report_type,
                'generated_at': datetime.now().isoformat(),
                'data': data,
                'export_format': 'json'
            }
            
            return export_data
            
        except Exception as e:
            return self._get_error_response(str(e))
    
    def get_chart_data(self, chart_type: str) -> Dict[str, Any]:
        """Obtenir les données pour les graphiques"""
        
        try:
            analysis = self.analytics_service.get_comprehensive_analysis()
            
            chart_data = {}
            
            if chart_type == 'visa_status_pie':
                chart_data = self._prepare_pie_chart_data(analysis['visa_status_analysis']['status_distribution'])
            
            elif chart_type == 'nationality_bar':
                chart_data = self._prepare_bar_chart_data(analysis['nationality_analysis']['nationality_distribution'])
            
            elif chart_type == 'employee_performance':
                chart_data = self._prepare_performance_chart_data(analysis['employee_analysis']['employee_performance'])
            
            elif chart_type == 'temporal_trend':
                chart_data = self._prepare_temporal_chart_data(analysis['temporal_analysis']['monthly_distribution'])
            
            elif chart_type == 'conversion_funnel':
                chart_data = self._prepare_funnel_chart_data(analysis['performance_metrics']['phase_conversion_rates'])
            
            return chart_data
            
        except Exception as e:
            return self._get_error_response(str(e))
    
    def _prepare_pie_chart_data(self, status_distribution: Dict[str, int]) -> Dict[str, Any]:
        """Préparer les données pour le graphique en secteurs"""
        
        colors = ['#28a745', '#ffc107', '#dc3545', '#17a2b8', '#6f42c1', '#6c757d']
        
        data = {
            'labels': list(status_distribution.keys()),
            'datasets': [{
                'data': list(status_distribution.values()),
                'backgroundColor': colors[:len(status_distribution)],
                'borderWidth': 2,
                'borderColor': '#ffffff'
            }]
        }
        
        return data
    
    def _prepare_bar_chart_data(self, nationality_distribution: Dict[str, int]) -> Dict[str, Any]:
        """Préparer les données pour le graphique en barres"""
        
        # Trier par nombre décroissant et prendre les top 10
        sorted_data = sorted(nationality_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
        
        data = {
            'labels': [item[0] for item in sorted_data],
            'datasets': [{
                'label': 'عدد العملاء',
                'data': [item[1] for item in sorted_data],
                'backgroundColor': 'rgba(54, 162, 235, 0.8)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }]
        }
        
        return data
    
    def _prepare_performance_chart_data(self, employee_performance: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Préparer les données pour le graphique de performance"""
        
        labels = list(employee_performance.keys())
        success_rates = [data['success_rate'] for data in employee_performance.values()]
        total_clients = [data['total_clients'] for data in employee_performance.values()]
        
        data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'معدل النجاح (%)',
                    'data': success_rates,
                    'type': 'line',
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'yAxisID': 'y'
                },
                {
                    'label': 'عدد العملاء',
                    'data': total_clients,
                    'type': 'bar',
                    'backgroundColor': 'rgba(54, 162, 235, 0.8)',
                    'yAxisID': 'y1'
                }
            ]
        }
        
        return data
    
    def _prepare_temporal_chart_data(self, monthly_distribution: Dict[str, int]) -> Dict[str, Any]:
        """Préparer les données pour le graphique temporel"""
        
        sorted_data = sorted(monthly_distribution.items())
        
        data = {
            'labels': [item[0] for item in sorted_data],
            'datasets': [{
                'label': 'العملاء الجدد',
                'data': [item[1] for item in sorted_data],
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.4,
                'fill': True
            }]
        }
        
        return data
    
    def _prepare_funnel_chart_data(self, conversion_rates: Dict[str, float]) -> Dict[str, Any]:
        """Préparer les données pour le graphique en entonnoir"""
        
        data = {
            'labels': list(conversion_rates.keys()),
            'datasets': [{
                'data': list(conversion_rates.values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)'
                ]
            }]
        }
        
        return data
    
    def _count_active_today(self, clients: List[Dict]) -> int:
        """Compter les clients actifs aujourd'hui"""
        today = datetime.now().date()
        active_count = 0
        
        for client in clients:
            created_at = client.get('created_at')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        date_obj = datetime.fromisoformat(created_at.replace('T', ' ').split('.')[0])
                    else:
                        date_obj = created_at
                    
                    if date_obj.date() == today:
                        active_count += 1
                except:
                    continue
        
        return active_count
    
    def _count_completed_today(self, clients: List[Dict]) -> int:
        """Compter les clients terminés aujourd'hui"""
        # Implémentation simplifiée - à améliorer selon les besoins
        return len([c for c in clients if c.get('visa_status') == 'اكتملت العملية'])
    
    def _count_pending_reviews(self, clients: List[Dict]) -> int:
        """Compter les clients en attente de révision"""
        return len([c for c in clients if c.get('visa_status') in ['تم التقديم إلى السفارة', 'تمت الموافقة على التأشيرة']])
    
    def _get_error_response(self, error_message: str) -> Dict[str, Any]:
        """Obtenir une réponse d'erreur standardisée"""
        return {
            'error': True,
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }
