#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôleur pour la gestion des clients dans le système de suivi des visas TCA
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from models.client import Client, ClientValidator
from database.database_manager import DatabaseManager
from utils.cache_manager import cache_client_data, cache_statistics, invalidate_client_cache

class ClientController:
    """Contrôleur pour la gestion des clients"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialiser le contrôleur"""
        self.db_manager = db_manager
        
    def add_client_raw(self, client_data: Dict[str, Any]) -> Optional[int]:
        """Ajouter un nouveau client SANS validation (pour import raw)"""
        try:
            # Générer automatiquement l'ID client s'il n'est pas fourni ou est vide
            # OU s'il existe déjà dans la base de données
            client_id = client_data.get('client_id', '').strip()
            
            if not client_id or self.db_manager.get_client_by_id(client_id):
                # Générer un ID au format CLI standard
                client_data['client_id'] = self.generate_client_id()
                print(f"ID généré automatiquement: {client_data['client_id']}")
            
            # Ajouter le client à la base de données SANS validation
            client_id = self.db_manager.add_client(client_data)
            
            return client_id
            
        except Exception as e:
            print(f"Erreur lors de l'ajout du client raw: {e}")
            raise
    
    def add_client(self, client_data: Dict[str, Any]) -> Optional[str]:
        """Ajouter un nouveau client avec génération automatique d'ID"""
        try:
            # Générer automatiquement l'ID client si non fourni
            if not client_data.get('client_id', '').strip():
                client_data['client_id'] = self.generate_client_id()
            
            # Créer un objet Client pour validation
            client = Client.from_dict(client_data)
            
            # Valider les données
            validation_errors = client.validate()
            if validation_errors:
                raise ValueError(f"Erreurs de validation: {validation_errors}")
            
            # Vérifier si l'ID client existe déjà
            existing_client = self.db_manager.get_client_by_id(client.client_id)
            if existing_client:
                raise ValueError(f"Un client avec l'ID '{client.client_id}' existe déjà")
            
            # Ajouter le client à la base de données
            client_id = self.db_manager.add_client(client.to_dict())
            
            # Invalider le cache après ajout
            invalidate_client_cache()
            
            return client_id
            
        except Exception as e:
            print(f"Erreur lors de l'ajout du client: {e}")
            raise
            
    def update_client(self, client_id: str, client_data: Dict[str, Any]) -> bool:
        """Mettre à jour un client existant"""
        try:
            # Vérifier que le client existe
            existing_client = self.db_manager.get_client_by_id(client_id)
            if not existing_client:
                raise ValueError(f"Client avec l'ID '{client_id}' non trouvé")
            
            # Créer un objet Client pour validation
            client = Client.from_dict(client_data)
            
            # Valider les données
            validation_errors = client.validate()
            if validation_errors:
                raise ValueError(f"Erreurs de validation: {validation_errors}")
            
            # Si l'ID client a changé, vérifier qu'il n'existe pas déjà
            if client.client_id != client_id:
                existing_new_id = self.db_manager.get_client_by_id(client.client_id)
                if existing_new_id:
                    raise ValueError(f"Un client avec l'ID '{client.client_id}' existe déjà")
            
            # Mettre à jour le client
            success = self.db_manager.update_client(client_id, client.to_dict())
            
            # Invalider le cache après mise à jour
            if success:
                invalidate_client_cache()
            
            return success
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour du client: {e}")
            raise
            
    def update_client_status(self, client_id: str, new_status: str) -> bool:
        """Mettre à jour uniquement le statut d'un client"""
        try:
            # Vérifier que le client existe
            existing_client = self.db_manager.get_client_by_id(client_id)
            if not existing_client:
                raise ValueError(f"Client avec l'ID '{client_id}' non trouvé")
            
            # Vérifier que le statut est valide
            if new_status not in Client.VISA_STATUS_OPTIONS:
                raise ValueError(f"Statut invalide: {new_status}")
            
            # Préparer les données de mise à jour
            update_data = dict(existing_client)
            update_data['visa_status'] = new_status
            
            # Mettre à jour le client
            success = self.db_manager.update_client(client_id, update_data)
            
            return success
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour du statut: {e}")
            raise
            
    def delete_client(self, client_id: str) -> bool:
        """Supprimer un client"""
        try:
            # Vérifier que le client existe
            existing_client = self.db_manager.get_client_by_id(client_id)
            if not existing_client:
                raise ValueError(f"Client avec l'ID '{client_id}' non trouvé")
            
            # Supprimer le client
            success = self.db_manager.delete_client(client_id)
            
            # Invalider le cache après suppression
            if success:
                invalidate_client_cache()
            
            return success
            
        except Exception as e:
            print(f"Erreur lors de la suppression du client: {e}")
            raise
            
    def get_client_by_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer un client par son ID"""
        try:
            client = self.db_manager.get_client_by_id(client_id)
            return dict(client) if client else None
            
        except Exception as e:
            print(f"Erreur lors de la récupération du client: {e}")
            return None
            
    def get_all_clients(self, page: int = 1, per_page: int = 50) -> tuple[List[Dict[str, Any]], int]:
        """Récupérer tous les clients avec pagination"""
        try:
            clients, total = self.db_manager.get_all_clients(page, per_page)
            return [dict(client) for client in clients], total
            
        except Exception as e:
            print(f"Erreur lors de la récupération des clients: {e}")
            return [], 0
            
    def search_clients(self, search_term: str, page: int = 1, per_page: int = 50) -> tuple[List[Dict[str, Any]], int]:
        """Rechercher des clients avec pagination"""
        try:
            if not search_term or not search_term.strip():
                return self.get_all_clients(page, per_page)
                
            clients, total = self.db_manager.search_clients(search_term.strip(), page, per_page)
            return [dict(client) for client in clients], total
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return [], 0
    
    def get_filtered_clients(self, filters: Dict[str, str] = None, page: int = 1, per_page: int = 50) -> tuple[List[Dict[str, Any]], int]:
        """Récupérer les clients avec filtres et pagination"""
        try:
            clients, total = self.db_manager.get_filtered_clients(filters, page, per_page)
            return [dict(client) for client in clients], total
            
        except Exception as e:
            print(f"Erreur lors de la récupération filtrée: {e}")
            return [], 0
            
    def get_clients_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Récupérer les clients par statut"""
        try:
            if status not in Client.VISA_STATUS_OPTIONS:
                raise ValueError(f"Statut invalide: {status}")
                
            clients = self.db_manager.get_clients_by_status(status)
            return [dict(client) for client in clients]
            
        except Exception as e:
            print(f"Erreur lors de la récupération par statut: {e}")
            return []
            
    def get_clients_by_nationality(self, nationality: str) -> List[Dict[str, Any]]:
        """Récupérer les clients par nationalité"""
        try:
            if nationality not in Client.NATIONALITY_OPTIONS:
                raise ValueError(f"Nationalité invalide: {nationality}")
                
            all_clients, _ = self.get_all_clients()
            filtered_clients = [c for c in all_clients if c.get('nationality') == nationality]
            
            return filtered_clients
            
        except Exception as e:
            print(f"Erreur lors de la récupération par nationalité: {e}")
            return []
            
    def get_clients_by_employee(self, employee: str) -> List[Dict[str, Any]]:
        """Récupérer les clients par employé responsable"""
        try:
            if employee not in Client.EMPLOYEE_OPTIONS:
                raise ValueError(f"Employé invalide: {employee}")
                
            all_clients, _ = self.get_all_clients()
            filtered_clients = [c for c in all_clients if c.get('responsible_employee') == employee]
            
            return filtered_clients
            
        except Exception as e:
            print(f"Erreur lors de la récupération par employé: {e}")
            return []
            
    def update_client_field(self, client_id: str, field: str, value: str) -> bool:
        """Mettre à jour un champ spécifique d'un client"""
        try:
            # Vérifier que le client existe
            client = self.get_client_by_id(client_id)
            if not client:
                return False
            
            # Valider le champ et la valeur
            if field == 'visa_status' and value not in Client.VISA_STATUS_OPTIONS:
                return False
            elif field == 'responsible_employee' and value not in Client.EMPLOYEE_OPTIONS:
                return False
            elif field in ['application_date', 'transaction_date']:
                # Validation basique pour les dates
                if not value or len(value) < 8:
                    return False
            
            # Sauvegarder l'ancien statut pour les notifications WhatsApp
            old_status = None
            if field == 'visa_status':
                old_status = client.get('visa_status', '')
            
            # Mettre à jour le champ
            success = self.db_manager.update_client_field(client_id, field, value)
            
            if success:
                # Invalider le cache si nécessaire
                try:
                    from utils.cache_manager import invalidate_client_cache
                    invalidate_client_cache()
                except ImportError:
                    pass  # Cache non disponible, continuer sans
                
                # Envoyer notification WhatsApp si le statut de visa a changé
                if field == 'visa_status' and old_status != value:
                    try:
                        from services.whatsapp_service import whatsapp_service
                        whatsapp_result = whatsapp_service.send_visa_status_notification(
                            client, old_status, value
                        )
                        if whatsapp_result.get('success'):
                            print(f"✅ Notification WhatsApp envoyée pour {client.get('full_name', 'Client')}")
                        else:
                            print(f"⚠️ Échec envoi WhatsApp: {whatsapp_result.get('error', 'Erreur inconnue')}")
                    except Exception as whatsapp_error:
                        print(f"⚠️ Erreur notification WhatsApp: {whatsapp_error}")
                        # Ne pas faire échouer la mise à jour à cause de WhatsApp
            
            return success
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour du champ {field}: {e}")
            return False

    def get_status_history(self, client_id: str) -> List[Dict[str, Any]]:
        """Récupérer l'historique des statuts d'un client"""
        try:
            history = self.db_manager.get_status_history(client_id)
            return [dict(record) for record in history]
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'historique: {e}")
            return []
            
    def import_clients_bulk(self, clients_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Importer plusieurs clients en lot"""
        try:
            # Valider les données en lot
            validation_result = ClientValidator.validate_bulk_data(clients_data)
            
            # Compter les résultats
            valid_count = len(validation_result['valid_clients'])
            invalid_count = len(validation_result['invalid_clients'])
            
            # Ajouter les clients valides
            added_count = 0
            errors = []
            
            for client in validation_result['valid_clients']:
                try:
                    # Vérifier si l'ID existe déjà
                    existing = self.db_manager.get_client_by_id(client.client_id)
                    if existing:
                        errors.append(f"Client '{client.client_id}' existe déjà")
                        continue
                        
                    # Ajouter le client
                    client_id = self.db_manager.add_client(client.to_dict())
                    if client_id:
                        added_count += 1
                    else:
                        errors.append(f"Échec de l'ajout du client '{client.client_id}'")
                        
                except Exception as e:
                    errors.append(f"Erreur pour le client '{client.client_id}': {str(e)}")
            
            return {
                'success': True,
                'total_processed': len(clients_data),
                'valid_clients': valid_count,
                'invalid_clients': invalid_count,
                'added_clients': added_count,
                'errors': errors + validation_result['errors'],
                'invalid_details': validation_result['invalid_clients']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Erreur lors de l'import en lot: {str(e)}",
                'total_processed': 0,
                'added_clients': 0
            }
            
    def get_statistics(self) -> Dict[str, Any]:
        """Récupérer les statistiques des clients"""
        try:
            return self.db_manager.get_statistics()
            
        except Exception as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            return {
                'total_clients': 0,
                'by_status': {},
                'by_nationality': {},
                'by_employee': {}
            }
            
    def validate_client_data(self, client_data: Dict[str, Any]) -> Dict[str, str]:
        """Valider les données d'un client"""
        try:
            client = Client.from_dict(client_data)
            return client.validate()
            
        except Exception as e:
            return {'general': f"Erreur de validation: {str(e)}"}
            
    def generate_client_id(self, prefix: str = "CLI") -> str:
        """Générer un ID client unique avec format officiel CLI001, CLI002, etc. (3 chiffres)"""
        try:
            # Requête directe à la base de données pour obtenir tous les client_id
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT client_id FROM clients WHERE client_id LIKE ?", (f"{prefix}%",))
            all_client_ids = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            # Extraire les numéros existants
            existing_numbers = []
            for client_id in all_client_ids:
                if client_id.startswith(prefix):
                    try:
                        # Extraire le numéro après le préfixe (format CLI001, CLI002, etc.)
                        number_str = client_id[len(prefix):]
                        number = int(number_str)
                        existing_numbers.append(number)
                    except ValueError:
                        continue
            
            # Trouver le prochain numéro disponible
            if existing_numbers:
                next_number = max(existing_numbers) + 1
            else:
                next_number = 1  # Commencer à CLI001
            
            # Vérifier que cet ID n'existe pas déjà (sécurité supplémentaire)
            while f"{prefix}{next_number:03d}" in all_client_ids:
                next_number += 1
            
            # Format officiel: CLI + 3 chiffres (CLI001, CLI002, ..., CLI999)
            return f"{prefix}{next_number:03d}"
            
        except Exception as e:
            print(f"Erreur lors de la génération de l'ID: {e}")
            # Fallback: commencer à CLI001
            return "CLI001"
            
    def generate_whatsapp_message(self, client_id: str) -> Dict[str, Any]:
        """Générer un message WhatsApp personnalisé pour un client"""
        try:
            # Récupérer les données du client
            client = self.get_client_by_id(client_id)
            if not client:
                raise ValueError(f"Client avec l'ID '{client_id}' non trouvé")
            
            # Récupérer le nom et l'état du visa
            client_name = client.get('full_name', 'Client')
            visa_status = client.get('visa_status', 'En cours de traitement')
            
            # Message de base (toujours inclus)
            base_message = (
                "نشكركم عزيز {client_name} اختياركم لشركة تونس للاستشارات والخدمات، تهانينا! "
                "{visa_status} "
            )
            
            # Texte de demande de passeport (seulement si état = "تم القبول")
            passport_request = "نأمل من سيادتكم تسليمنا جواز السفر في اقرب وقت ممكن. "
            
            # Message de fin (toujours inclus)
            end_message = (
                "للمزيد من المعلومات و تتبع ما هو جديد الرجاء التواصل معنا عبر صفحة الفيسبوك وشكرا. "
                "رابط الصفحة: https://www.facebook.com/share/1D4dHp2z74/?mibextid=wwXIfr"
            )
            
            # Construire le message selon l'état
            if visa_status == "تم القبول":
                # Inclure la demande de passeport
                message_template = base_message + passport_request + end_message
            else:
                # Exclure la demande de passeport
                message_template = base_message + end_message
            
            # Remplacer les placeholders
            personalized_message = message_template.format(
                client_name=client_name,
                visa_status=visa_status
            )
            
            return {
                'success': True,
                'client_id': client_id,
                'client_name': client_name,
                'visa_status': visa_status,
                'message': personalized_message,
                'phone_number': client.get('phone_number', '')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Erreur lors de la génération du message: {str(e)}"
            }