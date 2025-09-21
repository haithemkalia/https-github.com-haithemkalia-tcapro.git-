#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôleur WhatsApp pour le système de suivi des visas TCA
"""

from typing import Dict, Any, Optional
from datetime import datetime

class WhatsAppController:
    """Contrôleur pour les fonctionnalités WhatsApp"""
    
    def __init__(self, db_manager):
        """Initialiser le contrôleur WhatsApp"""
        self.db_manager = db_manager
        self.whatsapp_enabled = False  # Désactivé par défaut
    
    def is_whatsapp_enabled(self) -> bool:
        """Vérifier si WhatsApp est activé"""
        return self.whatsapp_enabled
    
    def enable_whatsapp(self):
        """Activer WhatsApp"""
        self.whatsapp_enabled = True
    
    def disable_whatsapp(self):
        """Désactiver WhatsApp"""
        self.whatsapp_enabled = False
    
    def send_welcome_notification(self, client_id: str) -> bool:
        """Envoyer une notification de bienvenue"""
        try:
            if not self.whatsapp_enabled:
                return False
            
            # Récupérer les informations du client
            client = self.db_manager.get_client_by_id(client_id)
            if not client:
                return False
            
            # Simuler l'envoi du message
            print(f"📱 Message WhatsApp envoyé à {client.get('full_name', '')} ({client.get('whatsapp_number', '')})")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi WhatsApp: {e}")
            return False
    
    def send_status_update(self, client_id: str, new_status: str) -> bool:
        """Envoyer une mise à jour de statut"""
        try:
            if not self.whatsapp_enabled:
                return False
            
            # Récupérer les informations du client
            client = self.db_manager.get_client_by_id(client_id)
            if not client:
                return False
            
            # Simuler l'envoi du message
            print(f"📱 Mise à jour de statut envoyée à {client.get('full_name', '')}: {new_status}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de mise à jour: {e}")
            return False
    
    def send_custom_message(self, client_id: str, message: str) -> bool:
        """Envoyer un message personnalisé"""
        try:
            if not self.whatsapp_enabled:
                return False
            
            # Récupérer les informations du client
            client = self.db_manager.get_client_by_id(client_id)
            if not client:
                return False
            
            # Simuler l'envoi du message
            print(f"📱 Message personnalisé envoyé à {client.get('full_name', '')}: {message}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi du message: {e}")
            return False
    
    def validate_whatsapp_number(self, number: str) -> bool:
        """Valider un numéro WhatsApp"""
        if not number:
            return False
        
        # Nettoyer le numéro
        clean_number = ''.join(filter(str.isdigit, number))
        
        # Vérifier la longueur
        return 8 <= len(clean_number) <= 15
    
    def format_whatsapp_number(self, number: str) -> str:
        """Formater un numéro WhatsApp"""
        if not number:
            return ''
        
        # Nettoyer le numéro
        clean_number = ''.join(filter(str.isdigit, number))
        
        # Ajouter le préfixe international si nécessaire
        if not clean_number.startswith('218') and len(clean_number) == 9:
            clean_number = '218' + clean_number
        
        return clean_number