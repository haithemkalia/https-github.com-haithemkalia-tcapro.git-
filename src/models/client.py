#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modèle Client pour le système de suivi des visas TCA
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re

class Client:
    """Modèle représentant un client dans le système de suivi des visas"""
    
    # Options prédéfinies
    PASSPORT_STATUS_OPTIONS = [
        'موجود', 'غير موجود', 'منتهي الصلاحية', 'قيد التجديد', 'مفقود'
    ]
    
    NATIONALITY_OPTIONS = [
        'ليبي', 'تونسي', 'مصري', 'مغربي', 'جزائري', 'سوداني', 'سوري', 'عراقي', 'أردني', 'لبناني', 'فلسطيني', 'صيني'
    ]
    
    VISA_STATUS_OPTIONS = [
        'تم التقديم في السيستام', 'تم التقديم إلى السفارة', 'تمت الموافقة على التأشيرة', 'التأشيرة غير موافق عليها', 'اكتملت العملية'
    ]
    
    EMPLOYEE_OPTIONS = [
        'اميرة', 'محمد', 'سفيان', 'اميمة', 'ايلاف', 'انيس', 'وليد', 'إشراف'
    ]
    
    def __init__(self, **kwargs):
        """Initialiser un client"""
        self.id = kwargs.get('id')
        self.client_id = kwargs.get('client_id', '')
        self.full_name = kwargs.get('full_name', '')
        self.whatsapp_number = kwargs.get('whatsapp_number', '')
        self.whatsapp_number_clean = kwargs.get('whatsapp_number_clean', '')
        self.application_date = kwargs.get('application_date', '')
        self.transaction_date = kwargs.get('transaction_date', '')
        self.passport_number = kwargs.get('passport_number', '')
        self.passport_status = kwargs.get('passport_status', '')
        self.passport_status_normalized = kwargs.get('passport_status_normalized', '')
        self.nationality = kwargs.get('nationality', '')
        self.visa_status = kwargs.get('visa_status', 'التقديم')
        self.visa_status_normalized = kwargs.get('visa_status_normalized', '')
        self.processed_by = kwargs.get('processed_by', '')
        self.summary = kwargs.get('summary', '')
        self.notes = kwargs.get('notes', '')
        self.responsible_employee = kwargs.get('responsible_employee', '')
        self.original_row_number = kwargs.get('original_row_number')
        self.import_timestamp = kwargs.get('import_timestamp')
        self.is_duplicate = kwargs.get('is_duplicate', False)
        self.auto_generated_id = kwargs.get('auto_generated_id', False)
        self.empty_name_accepted = kwargs.get('empty_name_accepted', False)
        self.extra_data = kwargs.get('extra_data', '')
        self.created_at = kwargs.get('created_at')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Client':
        """Créer un client à partir d'un dictionnaire"""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir le client en dictionnaire"""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'full_name': self.full_name,
            'whatsapp_number': self.whatsapp_number,
            'whatsapp_number_clean': self.whatsapp_number_clean,
            'application_date': self.application_date,
            'transaction_date': self.transaction_date,
            'passport_number': self.passport_number,
            'passport_status': self.passport_status,
            'passport_status_normalized': self.passport_status_normalized,
            'nationality': self.nationality,
            'visa_status': self.visa_status,
            'visa_status_normalized': self.visa_status_normalized,
            'processed_by': self.processed_by,
            'summary': self.summary,
            'notes': self.notes,
            'responsible_employee': self.responsible_employee,
            'original_row_number': self.original_row_number,
            'import_timestamp': self.import_timestamp,
            'is_duplicate': self.is_duplicate,
            'auto_generated_id': self.auto_generated_id,
            'empty_name_accepted': self.empty_name_accepted,
            'extra_data': self.extra_data,
            'created_at': self.created_at
        }
    
    def validate(self) -> List[str]:
        """Valider les données du client"""
        errors = []
        
        # Validation basique (optionnelle pour import sans restriction)
        if not self.client_id and not self.auto_generated_id:
            errors.append('معرف العميل مطلوب')
        
        if not self.full_name and not self.empty_name_accepted:
            errors.append('الاسم الكامل مطلوب')
        
        # Validation du numéro WhatsApp (optionnelle)
        if self.whatsapp_number and not self._is_valid_whatsapp(self.whatsapp_number):
            # Ne pas considérer comme erreur pour import sans restriction
            pass
        
        return errors
    
    def _is_valid_whatsapp(self, number: str) -> bool:
        """Valider le format du numéro WhatsApp"""
        if not number:
            return True  # Optionnel
        
        # Nettoyer le numéro
        clean_number = re.sub(r'[^0-9+]', '', number)
        
        # Vérifier la longueur (entre 8 et 15 chiffres)
        if len(clean_number) < 8 or len(clean_number) > 15:
            return False
        
        return True
    
    def __str__(self) -> str:
        """Représentation string du client"""
        return f"Client({self.client_id}: {self.full_name})"
    
    def __repr__(self) -> str:
        """Représentation pour debug"""
        return self.__str__()

class ClientValidator:
    """Validateur pour les données client"""
    
    @staticmethod
    def validate_client_data(data: Dict[str, Any], strict: bool = True) -> List[str]:
        """Valider les données d'un client"""
        errors = []
        
        if strict:
            # Validation stricte
            if not data.get('client_id', '').strip():
                errors.append('معرف العميل مطلوب')
            
            if not data.get('full_name', '').strip():
                errors.append('الاسم الكامل مطلوب')
        
        # Validation du numéro WhatsApp
        whatsapp = data.get('whatsapp_number', '')
        if whatsapp and not ClientValidator._is_valid_whatsapp(whatsapp):
            if strict:
                errors.append('رقم الواتساب غير صحيح')
        
        return errors
    
    @staticmethod
    def _is_valid_whatsapp(number: str) -> bool:
        """Valider le format du numéro WhatsApp"""
        if not number:
            return True
        
        clean_number = re.sub(r'[^0-9+]', '', number)
        return 8 <= len(clean_number) <= 15
    
    @staticmethod
    def normalize_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliser les données client"""
        normalized = data.copy()
        
        # Nettoyer les espaces
        for key, value in normalized.items():
            if isinstance(value, str):
                normalized[key] = value.strip()
        
        # Normaliser le numéro WhatsApp
        if normalized.get('whatsapp_number'):
            clean_whatsapp = re.sub(r'[^0-9+]', '', normalized['whatsapp_number'])
            normalized['whatsapp_number_clean'] = clean_whatsapp
        
        # Normaliser les statuts
        if normalized.get('passport_status'):
            normalized['passport_status_normalized'] = ClientValidator._normalize_status(
                normalized['passport_status'], Client.PASSPORT_STATUS_OPTIONS
            )
        
        if normalized.get('visa_status'):
            normalized['visa_status_normalized'] = ClientValidator._normalize_status(
                normalized['visa_status'], Client.VISA_STATUS_OPTIONS
            )
        
        return normalized
    
    @staticmethod
    def _normalize_status(status: str, options: List[str]) -> str:
        """Normaliser un statut selon les options disponibles"""
        if not status:
            return ''
        
        status_clean = status.strip()
        
        # Recherche exacte
        if status_clean in options:
            return status_clean
        
        # Recherche approximative
        for option in options:
            if status_clean in option or option in status_clean:
                return option
        
        # Retourner tel quel si pas de correspondance
        return status_clean