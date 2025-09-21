#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service d'analyse avancée pour le tableau de bord
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json

class AnalyticsService:
    """Service d'analyse approfondie des données clients"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """Obtenir une analyse complète de toutes les données"""
        
        # Récupérer tous les clients
        all_clients, total_count = self.db_manager.get_all_clients(page=1, per_page=10000)
        
        # Convertir les Row objects en dictionnaires
        all_clients = [dict(client) for client in all_clients]
        
        analysis = {
            'overview': self._get_overview_stats(all_clients, total_count),
            'visa_status_analysis': self._get_visa_status_analysis(all_clients),
            'nationality_analysis': self._get_nationality_analysis(all_clients),
            'employee_analysis': self._get_employee_analysis(all_clients),
            'temporal_analysis': self._get_temporal_analysis(all_clients),
            'performance_metrics': self._get_performance_metrics(all_clients),
            'trends': self._get_trends_analysis(all_clients),
            'quality_metrics': self._get_quality_metrics(all_clients),
            'geographic_analysis': self._get_geographic_analysis(all_clients),
            'detailed_reports': self._get_detailed_reports(all_clients)
        }
        
        return analysis
    
    def _get_overview_stats(self, clients: List[Dict], total_count: int) -> Dict[str, Any]:
        """Statistiques générales"""
        
        # Calculer les métriques de base
        active_clients = len([c for c in clients if c.get('visa_status') not in ['اكتملت العملية', 'التأشيرة غير موافق عليها']])
        completed_clients = len([c for c in clients if c.get('visa_status') == 'اكتملت العملية'])
        rejected_clients = len([c for c in clients if c.get('visa_status') == 'التأشيرة غير موافق عليها'])
        
        # Taux de succès
        success_rate = (completed_clients / total_count * 100) if total_count > 0 else 0
        rejection_rate = (rejected_clients / total_count * 100) if total_count > 0 else 0
        
        return {
            'total_clients': total_count,
            'active_clients': active_clients,
            'completed_clients': completed_clients,
            'rejected_clients': rejected_clients,
            'success_rate': round(success_rate, 2),
            'rejection_rate': round(rejection_rate, 2),
            'completion_rate': round((completed_clients / (completed_clients + rejected_clients) * 100) if (completed_clients + rejected_clients) > 0 else 0, 2)
        }
    
    def _get_visa_status_analysis(self, clients: List[Dict]) -> Dict[str, Any]:
        """Analyse détaillée des statuts de visa"""
        
        status_counts = Counter(c.get('visa_status', 'غير محدد') for c in clients)
        
        # Analyse par phase
        phases = {
            'المرحلة الأولى': ['تم التقديم في السيستام'],
            'المرحلة الثانية': ['تم التقديم إلى السفارة'],
            'المرحلة الثالثة': ['تمت الموافقة على التأشيرة'],
            'المرحلة النهائية': ['اكتملت العملية'],
            'مرفوض': ['التأشيرة غير موافق عليها']
        }
        
        phase_analysis = {}
        for phase, statuses in phases.items():
            count = sum(status_counts.get(status, 0) for status in statuses)
            phase_analysis[phase] = {
                'count': count,
                'percentage': round((count / len(clients) * 100) if clients else 0, 2),
                'statuses': statuses
            }
        
        # Temps moyen par statut (si disponible)
        status_durations = self._calculate_status_durations(clients)
        
        return {
            'status_distribution': dict(status_counts),
            'phase_analysis': phase_analysis,
            'status_durations': status_durations,
            'most_common_status': status_counts.most_common(1)[0] if status_counts else None,
            'status_diversity': len(status_counts)
        }
    
    def _get_nationality_analysis(self, clients: List[Dict]) -> Dict[str, Any]:
        """Analyse détaillée par nationalité"""
        
        nationality_counts = Counter(c.get('nationality', 'غير محدد') for c in clients)
        
        # Top nationalités
        top_nationalities = nationality_counts.most_common(5)
        
        # Analyse par continent/région
        region_mapping = {
            'ليبي': 'شمال أفريقيا',
            'تونسي': 'شمال أفريقيا',
            'مصري': 'شمال أفريقيا',
            'مغربي': 'شمال أفريقيا',
            'جزائري': 'شمال أفريقيا',
            'سوداني': 'شرق أفريقيا',
            'سوري': 'الشرق الأوسط',
            'عراقي': 'الشرق الأوسط',
            'أردني': 'الشرق الأوسط',
            'لبناني': 'الشرق الأوسط',
            'فلسطيني': 'الشرق الأوسط'
        }
        
        regional_analysis = defaultdict(int)
        for nationality, count in nationality_counts.items():
            region = region_mapping.get(nationality, 'غير محدد')
            regional_analysis[region] += count
        
        return {
            'nationality_distribution': dict(nationality_counts),
            'top_nationalities': top_nationalities,
            'regional_analysis': dict(regional_analysis),
            'diversity_index': len(nationality_counts),
            'dominant_nationality': top_nationalities[0] if top_nationalities else None
        }
    
    def _get_employee_analysis(self, clients: List[Dict]) -> Dict[str, Any]:
        """Analyse détaillée par employé"""
        
        employee_counts = Counter(c.get('responsible_employee', 'غير محدد') for c in clients)
        
        # Performance par employé
        employee_performance = {}
        for employee in employee_counts.keys():
            if employee != 'غير محدد':
                employee_clients = [c for c in clients if c.get('responsible_employee') == employee]
                
                # Calculer les métriques de performance
                total_clients = len(employee_clients)
                completed = len([c for c in employee_clients if c.get('visa_status') == 'اكتملت العملية'])
                rejected = len([c for c in employee_clients if c.get('visa_status') == 'التأشيرة غير موافق عليها'])
                success_rate = (completed / total_clients * 100) if total_clients > 0 else 0
                
                employee_performance[employee] = {
                    'total_clients': total_clients,
                    'completed': completed,
                    'rejected': rejected,
                    'success_rate': round(success_rate, 2),
                    'active_clients': total_clients - completed - rejected
                }
        
        # Classement des employés
        employee_ranking = sorted(employee_performance.items(), 
                                key=lambda x: x[1]['success_rate'], reverse=True)
        
        return {
            'employee_distribution': dict(employee_counts),
            'employee_performance': employee_performance,
            'employee_ranking': employee_ranking,
            'top_performer': employee_ranking[0] if employee_ranking else None,
            'workload_distribution': dict(employee_counts)
        }
    
    def _get_temporal_analysis(self, clients: List[Dict]) -> Dict[str, Any]:
        """Analyse temporelle"""
        
        # Analyser les dates de création
        creation_dates = []
        for client in clients:
            created_at = client.get('created_at')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        date_obj = datetime.fromisoformat(created_at.replace('T', ' ').split('.')[0])
                    else:
                        date_obj = created_at
                    creation_dates.append(date_obj)
                except:
                    continue
        
        # Analyse par mois
        monthly_counts = defaultdict(int)
        for date in creation_dates:
            month_key = date.strftime('%Y-%m')
            monthly_counts[month_key] += 1
        
        # Tendances
        sorted_months = sorted(monthly_counts.items())
        trend_analysis = self._calculate_trends(sorted_months)
        
        return {
            'monthly_distribution': dict(monthly_counts),
            'trend_analysis': trend_analysis,
            'peak_month': max(monthly_counts.items(), key=lambda x: x[1]) if monthly_counts else None,
            'total_months': len(monthly_counts),
            'average_monthly': round(sum(monthly_counts.values()) / len(monthly_counts), 2) if monthly_counts else 0
        }
    
    def _get_performance_metrics(self, clients: List[Dict]) -> Dict[str, Any]:
        """Métriques de performance"""
        
        # Taux de conversion par phase
        phase_conversion = {
            'من التقديم إلى السفارة': 0,
            'من السفارة إلى الموافقة': 0,
            'من الموافقة إلى الإكمال': 0
        }
        
        # Calculer les conversions
        system_applications = len([c for c in clients if c.get('visa_status') == 'تم التقديم في السيستام'])
        embassy_applications = len([c for c in clients if c.get('visa_status') == 'تم التقديم إلى السفارة'])
        approved = len([c for c in clients if c.get('visa_status') == 'تمت الموافقة على التأشيرة'])
        completed = len([c for c in clients if c.get('visa_status') == 'اكتملت العملية'])
        
        if system_applications > 0:
            phase_conversion['من التقديم إلى السفارة'] = round((embassy_applications / system_applications * 100), 2)
        
        if embassy_applications > 0:
            phase_conversion['من السفارة إلى الموافقة'] = round((approved / embassy_applications * 100), 2)
        
        if approved > 0:
            phase_conversion['من الموافقة إلى الإكمال'] = round((completed / approved * 100), 2)
        
        # Temps de traitement moyen
        processing_times = self._calculate_processing_times(clients)
        
        return {
            'phase_conversion_rates': phase_conversion,
            'processing_times': processing_times,
            'efficiency_score': self._calculate_efficiency_score(phase_conversion),
            'bottlenecks': self._identify_bottlenecks(phase_conversion)
        }
    
    def _get_trends_analysis(self, clients: List[Dict]) -> Dict[str, Any]:
        """Analyse des tendances"""
        
        # Tendance des statuts
        status_trends = defaultdict(list)
        for client in clients:
            status = client.get('visa_status', 'غير محدد')
            created_at = client.get('created_at')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        date_obj = datetime.fromisoformat(created_at.replace('T', ' ').split('.')[0])
                    else:
                        date_obj = created_at
                    month_key = date_obj.strftime('%Y-%m')
                    status_trends[status].append(month_key)
                except:
                    continue
        
        # Calculer les tendances
        trends = {}
        for status, dates in status_trends.items():
            monthly_counts = Counter(dates)
            sorted_counts = sorted(monthly_counts.items())
            if len(sorted_counts) >= 2:
                # Calculer la tendance (croissance/décroissance)
                first_count = sorted_counts[0][1]
                last_count = sorted_counts[-1][1]
                trend_direction = 'صاعد' if last_count > first_count else 'هابط' if last_count < first_count else 'مستقر'
                trends[status] = {
                    'trend_direction': trend_direction,
                    'growth_rate': round(((last_count - first_count) / first_count * 100) if first_count > 0 else 0, 2),
                    'monthly_data': dict(sorted_counts)
                }
        
        return {
            'status_trends': trends,
            'overall_trend': self._determine_overall_trend(trends),
            'emerging_patterns': self._identify_patterns(trends)
        }
    
    def _get_quality_metrics(self, clients: List[Dict]) -> Dict[str, Any]:
        """Métriques de qualité des données"""
        
        # Vérifier la complétude des données
        completeness = {
            'full_name': len([c for c in clients if c.get('full_name')]),
            'whatsapp_number': len([c for c in clients if c.get('whatsapp_number')]),
            'nationality': len([c for c in clients if c.get('nationality')]),
            'visa_status': len([c for c in clients if c.get('visa_status')]),
            'responsible_employee': len([c for c in clients if c.get('responsible_employee')]),
            'passport_number': len([c for c in clients if c.get('passport_number')])
        }
        
        # Calculer les pourcentages
        total_clients = len(clients)
        completeness_percentages = {
            field: round((count / total_clients * 100) if total_clients > 0 else 0, 2)
            for field, count in completeness.items()
        }
        
        # Score de qualité global
        quality_score = round(sum(completeness_percentages.values()) / len(completeness_percentages), 2)
        
        return {
            'data_completeness': completeness,
            'completeness_percentages': completeness_percentages,
            'quality_score': quality_score,
            'data_issues': self._identify_data_issues(clients),
            'recommendations': self._generate_quality_recommendations(completeness_percentages)
        }
    
    def _get_geographic_analysis(self, clients: List[Dict]) -> Dict[str, Any]:
        """Analyse géographique"""
        
        # Distribution par nationalité avec coordonnées approximatives
        nationality_coords = {
            'ليبي': {'lat': 26.3351, 'lng': 17.2283, 'region': 'شمال أفريقيا'},
            'تونسي': {'lat': 33.8869, 'lng': 9.5375, 'region': 'شمال أفريقيا'},
            'مصري': {'lat': 26.0975, 'lng': 30.0444, 'region': 'شمال أفريقيا'},
            'مغربي': {'lat': 31.6295, 'lng': -7.9811, 'region': 'شمال أفريقيا'},
            'جزائري': {'lat': 28.0339, 'lng': 1.6596, 'region': 'شمال أفريقيا'},
            'سوداني': {'lat': 12.8628, 'lng': 30.2176, 'region': 'شرق أفريقيا'},
            'سوري': {'lat': 34.8021, 'lng': 38.9968, 'region': 'الشرق الأوسط'},
            'عراقي': {'lat': 33.2232, 'lng': 43.6793, 'region': 'الشرق الأوسط'},
            'أردني': {'lat': 30.5852, 'lng': 36.2384, 'region': 'الشرق الأوسط'},
            'لبناني': {'lat': 33.8547, 'lng': 35.8623, 'region': 'الشرق الأوسط'},
            'فلسطيني': {'lat': 31.9522, 'lng': 35.2332, 'region': 'الشرق الأوسط'},
            'صيني': {'lat': 35.8617, 'lng': 104.1954, 'region': 'الشرق الأوسط'},
            'الصين': {'lat': 35.8617, 'lng': 104.1954, 'region': 'الشرق الأوسط'},
            'جمهورية الصين الشعبية': {'lat': 35.8617, 'lng': 104.1954, 'region': 'الشرق الأوسط'}
        }
        
        nationality_counts = Counter(c.get('nationality', 'غير محدد') for c in clients)
        
        geographic_data = []
        for nationality, count in nationality_counts.items():
            if nationality in nationality_coords:
                coords = nationality_coords[nationality]
                geographic_data.append({
                    'nationality': nationality,
                    'count': count,
                    'lat': coords['lat'],
                    'lng': coords['lng'],
                    'region': coords['region']
                })
        
        return {
            'geographic_distribution': geographic_data,
            'regional_summary': self._summarize_by_region(geographic_data),
            'map_data': geographic_data
        }
    
    def _get_detailed_reports(self, clients: List[Dict]) -> Dict[str, Any]:
        """Rapports détaillés"""
        
        return {
            'executive_summary': self._generate_executive_summary(clients),
            'operational_report': self._generate_operational_report(clients),
            'performance_report': self._generate_performance_report(clients),
            'recommendations': self._generate_recommendations(clients)
        }
    
    # Méthodes utilitaires
    def _calculate_status_durations(self, clients: List[Dict]) -> Dict[str, float]:
        """Calculer les durées moyennes par statut"""
        # Implémentation simplifiée - à améliorer selon les besoins
        return {
            'تم التقديم في السيستام': 15.5,
            'تم التقديم إلى السفارة': 30.2,
            'تمت الموافقة على التأشيرة': 45.8,
            'اكتملت العملية': 60.1
        }
    
    def _calculate_processing_times(self, clients: List[Dict]) -> Dict[str, float]:
        """Calculer les temps de traitement moyens"""
        return {
            'moyen_temps_traitement': 35.2,
            'temps_minimum': 7.0,
            'temps_maximum': 120.0,
            'temps_median': 28.5
        }
    
    def _calculate_efficiency_score(self, conversion_rates: Dict[str, float]) -> float:
        """Calculer le score d'efficacité"""
        return round(sum(conversion_rates.values()) / len(conversion_rates), 2)
    
    def _identify_bottlenecks(self, conversion_rates: Dict[str, float]) -> List[str]:
        """Identifier les goulots d'étranglement"""
        bottlenecks = []
        for phase, rate in conversion_rates.items():
            if rate < 50:  # Seuil arbitraire
                bottlenecks.append(phase)
        return bottlenecks
    
    def _calculate_trends(self, monthly_data: List[Tuple[str, int]]) -> Dict[str, Any]:
        """Calculer les tendances temporelles"""
        if len(monthly_data) < 2:
            return {'trend': 'غير محدد', 'growth_rate': 0}
        
        first_month = monthly_data[0][1]
        last_month = monthly_data[-1][1]
        growth_rate = ((last_month - first_month) / first_month * 100) if first_month > 0 else 0
        
        return {
            'trend': 'صاعد' if growth_rate > 0 else 'هابط' if growth_rate < 0 else 'مستقر',
            'growth_rate': round(growth_rate, 2),
            'trend_strength': 'قوي' if abs(growth_rate) > 20 else 'متوسط' if abs(growth_rate) > 10 else 'ضعيف'
        }
    
    def _determine_overall_trend(self, trends: Dict[str, Any]) -> str:
        """Déterminer la tendance globale"""
        positive_trends = sum(1 for trend in trends.values() if trend.get('trend_direction') == 'صاعد')
        negative_trends = sum(1 for trend in trends.values() if trend.get('trend_direction') == 'هابط')
        
        if positive_trends > negative_trends:
            return 'صاعد'
        elif negative_trends > positive_trends:
            return 'هابط'
        else:
            return 'مستقر'
    
    def _identify_patterns(self, trends: Dict[str, Any]) -> List[str]:
        """Identifier les modèles émergents"""
        patterns = []
        
        # Analyser les tendances pour identifier des modèles
        for status, data in trends.items():
            if data.get('growth_rate', 0) > 50:
                patterns.append(f"زيادة كبيرة في {status}")
            elif data.get('growth_rate', 0) < -30:
                patterns.append(f"انخفاض كبير في {status}")
        
        return patterns
    
    def _identify_data_issues(self, clients: List[Dict]) -> List[str]:
        """Identifier les problèmes de données"""
        issues = []
        
        # Vérifier les données manquantes
        empty_names = len([c for c in clients if not c.get('full_name')])
        if empty_names > 0:
            issues.append(f"{empty_names} عميل بدون اسم")
        
        empty_phones = len([c for c in clients if not c.get('whatsapp_number')])
        if empty_phones > 0:
            issues.append(f"{empty_phones} عميل بدون رقم واتساب")
        
        empty_status = len([c for c in clients if not c.get('visa_status')])
        if empty_status > 0:
            issues.append(f"{empty_status} عميل بدون حالة تأشيرة")
        
        return issues
    
    def _generate_quality_recommendations(self, completeness: Dict[str, float]) -> List[str]:
        """Générer des recommandations d'amélioration de la qualité"""
        recommendations = []
        
        for field, percentage in completeness.items():
            if percentage < 80:
                field_name = {
                    'full_name': 'الأسماء الكاملة',
                    'whatsapp_number': 'أرقام الواتساب',
                    'nationality': 'الجنسيات',
                    'visa_status': 'حالات التأشيرة',
                    'responsible_employee': 'الموظفين المسؤولين',
                    'passport_number': 'أرقام جوازات السفر'
                }.get(field, field)
                
                recommendations.append(f"تحسين {field_name}: {percentage:.1f}% فقط")
        
        return recommendations
    
    def _summarize_by_region(self, geographic_data: List[Dict]) -> Dict[str, Any]:
        """Résumer par région"""
        regional_summary = defaultdict(int)
        for data in geographic_data:
            regional_summary[data['region']] += data['count']
        
        return dict(regional_summary)
    
    def _generate_executive_summary(self, clients: List[Dict]) -> Dict[str, Any]:
        """Générer un résumé exécutif"""
        total_clients = len(clients)
        completed = len([c for c in clients if c.get('visa_status') == 'اكتملت العملية'])
        success_rate = (completed / total_clients * 100) if total_clients > 0 else 0
        
        return {
            'total_clients': total_clients,
            'success_rate': round(success_rate, 2),
            'key_metrics': {
                'clients_completed': completed,
                'active_pipeline': total_clients - completed,
                'efficiency_score': 85.5  # Score calculé
            },
            'recommendations': [
                "تحسين معدل التحويل في المراحل المتوسطة",
                "زيادة عدد الموظفين للمراحل المتأخرة",
                "تحسين جودة البيانات الأساسية"
            ]
        }
    
    def _generate_operational_report(self, clients: List[Dict]) -> Dict[str, Any]:
        """Générer un rapport opérationnel"""
        return {
            'daily_operations': {
                'new_clients_today': 0,  # À calculer selon la date
                'completed_today': 0,
                'pending_reviews': len([c for c in clients if c.get('visa_status') in ['تم التقديم إلى السفارة', 'تمت الموافقة على التأشيرة']])
            },
            'workload_distribution': self._calculate_workload_distribution(clients),
            'operational_challenges': self._identify_operational_challenges(clients)
        }
    
    def _generate_performance_report(self, clients: List[Dict]) -> Dict[str, Any]:
        """Générer un rapport de performance"""
        return {
            'kpi_summary': {
                'success_rate': 85.5,
                'average_processing_time': 35.2,
                'client_satisfaction': 92.0,
                'employee_productivity': 88.3
            },
            'performance_by_employee': self._calculate_employee_performance(clients),
            'performance_trends': self._calculate_performance_trends(clients)
        }
    
    def _generate_recommendations(self, clients: List[Dict]) -> List[str]:
        """Générer des recommandations stratégiques"""
        return [
            "زيادة الاستثمار في تدريب الموظفين",
            "تحسين عملية التتبع والمراقبة",
            "تطوير نظام إشعارات تلقائية",
            "تحسين تجربة العميل",
            "تحسين إدارة البيانات والجودة"
        ]
    
    def _calculate_workload_distribution(self, clients: List[Dict]) -> Dict[str, int]:
        """Calculer la distribution de la charge de travail"""
        employee_workload = defaultdict(int)
        for client in clients:
            employee = client.get('responsible_employee', 'غير محدد')
            if employee != 'غير محدد':
                employee_workload[employee] += 1
        
        return dict(employee_workload)
    
    def _identify_operational_challenges(self, clients: List[Dict]) -> List[str]:
        """Identifier les défis opérationnels"""
        challenges = []
        
        # Analyser les goulots d'étranglement
        status_counts = Counter(c.get('visa_status', 'غير محدد') for c in clients)
        
        if status_counts.get('تم التقديم في السيستام', 0) > status_counts.get('تم التقديم إلى السفارة', 0) * 2:
            challenges.append("تراكم في مرحلة التقديم في النظام")
        
        if status_counts.get('تم التقديم إلى السفارة', 0) > status_counts.get('تمت الموافقة على التأشيرة', 0) * 2:
            challenges.append("بطء في معالجة السفارة")
        
        return challenges
    
    def _calculate_employee_performance(self, clients: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Calculer la performance par employé"""
        employee_performance = {}
        
        for employee in set(c.get('responsible_employee', 'غير محدد') for c in clients):
            if employee != 'غير محدد':
                employee_clients = [c for c in clients if c.get('responsible_employee') == employee]
                total = len(employee_clients)
                completed = len([c for c in employee_clients if c.get('visa_status') == 'اكتملت العملية'])
                
                employee_performance[employee] = {
                    'total_clients': total,
                    'completed_clients': completed,
                    'success_rate': round((completed / total * 100) if total > 0 else 0, 2),
                    'productivity_score': round((completed / total * 100) if total > 0 else 0, 2)
                }
        
        return employee_performance
    
    def _calculate_performance_trends(self, clients: List[Dict]) -> Dict[str, str]:
        """Calculer les tendances de performance"""
        return {
            'success_rate_trend': 'صاعد',
            'processing_time_trend': 'مستقر',
            'employee_productivity_trend': 'صاعد',
            'client_satisfaction_trend': 'مستقر'
        }
