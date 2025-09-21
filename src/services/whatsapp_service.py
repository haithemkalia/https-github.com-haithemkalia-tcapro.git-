#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service WhatsApp pour l'envoi de notifications automatiques
"""

import requests
import json
import subprocess
import webbrowser
from typing import Optional, Dict, Any

class WhatsAppService:
    """Service pour l'envoi de messages WhatsApp"""
    
    def __init__(self):
        self.base_url = "https://api.whatsapp.com"  # URL de base WhatsApp Business API
        self.access_token = None  # Token d'accès (à configurer)
        
    def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Ouvrir WhatsApp Desktop avec le message pré-rempli
        
        Args:
            phone_number: Numéro de téléphone du destinataire
            message: Message à envoyer
            
        Returns:
            Dict avec le statut de l'envoi
        """
        try:
            # Nettoyer le numéro de téléphone
            clean_number = self._clean_phone_number(phone_number)
            if not clean_number:
                return {"success": False, "error": "Numéro de téléphone invalide"}
            
            # Ouvrir WhatsApp Desktop
            success = self._open_whatsapp_desktop(clean_number, message)
            
            if success:
                return {
                    "success": True,
                    "message_id": f"whatsapp_{clean_number}_{hash(message)}",
                    "phone_number": clean_number,
                    "message": message,
                    "method": "desktop_app"
                }
            else:
                return {"success": False, "error": "Impossible d'ouvrir WhatsApp Desktop"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _open_whatsapp_desktop(self, phone_number: str, message: str) -> bool:
        """
        Ouvrir WhatsApp Web directement avec le numéro et le message
        SOLUTION POUR LES NUMÉROS NON ENREGISTRÉS DANS LES CONTACTS
        
        Args:
            phone_number: Numéro de téléphone
            message: Message à envoyer
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Encoder le message pour l'URL
            import urllib.parse
            encoded_message = urllib.parse.quote(message)
            
            print(f"📱 Ouverture WhatsApp pour {phone_number}")
            print(f"📝 Message: {message[:50]}...")
            print(f"🆕 NOUVELLE FENÊTRE - Numéro non enregistré dans contacts")
            
            # SOLUTION: Utiliser WhatsApp Web directement
            # WhatsApp Web permet d'envoyer à n'importe quel numéro sans l'avoir dans les contacts
            
            try:
                # URL WhatsApp Web pour nouvelle conversation
                web_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
                print(f"🌐 URL WhatsApp Web: {web_url}")
                
                # Ouvrir dans une nouvelle fenêtre du navigateur
                webbrowser.open_new(web_url)
                print(f"✅ WhatsApp Web ouvert dans NOUVELLE FENÊTRE pour {phone_number}")
                print(f"🆕 Nouvelle conversation créée automatiquement")
                print(f"📝 Message pré-rempli: {message[:30]}...")
                print(f"🚀 SOLUTION: Numéro non enregistré dans contacts - OK!")
                return True
                
            except Exception as e:
                print(f"⚠️ Méthode Web échouée: {e}")
            
            # Fallback: Essayer WhatsApp Desktop si Web échoue
            try:
                desktop_url = f"whatsapp://send?phone={phone_number}&text={encoded_message}"
                print(f"🔗 Fallback Desktop: {desktop_url}")
                
                subprocess.Popen(['start', desktop_url], shell=True)
                print(f"✅ WhatsApp Desktop ouvert (fallback) pour {phone_number}")
                return True
            except Exception as e:
                print(f"⚠️ Méthode Desktop fallback échouée: {e}")
            
            return False
            
        except Exception as e:
            print(f"❌ Erreur ouverture WhatsApp: {e}")
            return False
    
    def _is_whatsapp_desktop_installed(self) -> bool:
        """
        Vérifier si WhatsApp Desktop est installé
        
        Returns:
            True si WhatsApp Desktop est trouvé, False sinon
        """
        try:
            import os
            
            # Chemins possibles pour WhatsApp Desktop
            possible_paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe"),
                os.path.expandvars(r"%PROGRAMFILES%\WhatsApp\WhatsApp.exe"),
                os.path.expandvars(r"%PROGRAMFILES(X86)%\WhatsApp\WhatsApp.exe"),
                os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\WhatsApp.lnk")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"✅ WhatsApp Desktop trouvé: {path}")
                    return True
            
            print("⚠️ WhatsApp Desktop non trouvé, utilisation de WhatsApp Web")
            return False
            
        except Exception as e:
            print(f"⚠️ Erreur vérification WhatsApp Desktop: {e}")
            return False
    
    def _clean_phone_number(self, phone_number: str) -> Optional[str]:
        """
        SOLUTION UNIVERSELLE: Nettoyer le numéro pour WhatsApp
        Supporte tous les formats internationaux avec préfixe +
        
        Args:
            phone_number: Numéro de téléphone brut
            
        Returns:
            Numéro au format WhatsApp avec préfixe +
        """
        if not phone_number:
            return None
        
        # Supprimer les espaces et caractères spéciaux sauf +
        clean_number = phone_number.strip()
        
        # Supprimer TOUS les caractères non numériques sauf +
        digits_only = ''.join(c for c in clean_number if c.isdigit() or c == '+')
        
        if not digits_only:
            return None
        
        print(f"🔍 Nettoyage: {phone_number} → {digits_only}")
        
        # Si le numéro commence par +, le garder tel quel
        if digits_only.startswith('+'):
            final_number = digits_only
            print(f"✅ Numéro avec préfixe +: {final_number}")
            return final_number
        
        # Si pas de préfixe +, l'ajouter
        final_number = '+' + digits_only
        print(f"✅ Numéro avec préfixe + ajouté: {final_number}")
        return final_number
    
    def get_visa_status_message(self, status: str, client_name: str) -> str:
        """
        Générer le message WhatsApp selon le statut de visa
        
        Args:
            status: Statut de visa
            client_name: Nom du client
            
        Returns:
            Message formaté
        """
        messages = {
            'تم التقديم في السيستام': f"""
🛂 *تحديث حالة التأشيرة*

مرحباً {client_name}،

تم تسجيل طلب التأشيرة الخاص بك في النظام بنجاح.

📋 *الحالة الحالية:* تم التقديم في السيستام
📅 *التاريخ:* {self._get_current_date()}

سيتم متابعة طلبك وإعلامك بأي تحديثات.

شكراً لثقتكم بنا.

---
شركة تونس للاستشارات والخدمات
📱 Facebook: https://www.facebook.com/share/1D4dHp2z74/?mibextid=wwXIfr
            """,
            
            'تم التقديم إلى السفارة': f"""
🛂 *تحديث حالة التأشيرة*

مرحباً {client_name}،

تم تقديم جواز سفرك إلى السفارة.

📋 *الحالة الحالية:* تم التقديم إلى السفارة
📅 *التاريخ:* {self._get_current_date()}

سنقوم باعلامكم فورا استلام جوازكم.

شكراً لصبركم.

---
شركة تونس للاستشارات والخدمات
📱 Facebook: https://www.facebook.com/share/1D4dHp2z74/?mibextid=wwXIfr
            """,
            
            'تمت الموافقة على التأشيرة': f"""
🎉 *تهانينا!*

مرحباً {client_name}،

🎊 *تمت الموافقة على طلب التأشيرة الخاص بك!*

📋 *الحالة الحالية:* تمت الموافقة على التأشيرة
📅 *التاريخ:* {self._get_current_date()}

يمكنكم الآن تسليم جواز السفر اذا لم يكون متوفر لنا

شكراً لثقتكم بنا.

---
شركة تونس للاستشارات والخدمات
📱 Facebook: https://www.facebook.com/share/1D4dHp2z74/?mibextid=wwXIfr
            """,
            
            'التأشيرة غير موافق عليها': f"""
😔 *تحديث حالة التأشيرة*

مرحباً {client_name}،

للأسف، لم يتم قبول طلب التأشيرة.

📋 *الحالة الحالية:* التأشيرة غير موافق عليها
📅 *التاريخ:* {self._get_current_date()}

يمكنكم مراجعة الأسباب معنا أو إعادة التقديم.

نحن هنا لمساعدتكم.

---
شركة تونس للاستشارات والخدمات
📱 Facebook: https://www.facebook.com/share/1D4dHp2z74/?mibextid=wwXIfr
            """,
            
            'اكتملت العملية': f"""
✅ *اكتملت العملية*

مرحباً {client_name}،

تم اصدار التاشيرة وسوف يتصل بك مندوب الشركة فورا وصول جواز سفركم للاستلام.

📋 *الحالة الحالية:* اكتملت العملية
📅 *التاريخ:* {self._get_current_date()}

شكراً لثقتكم بنا.

---
شركة تونس للاستشارات والخدمات
📱 Facebook: https://www.facebook.com/share/1D4dHp2z74/?mibextid=wwXIfr
            """
        }
        
        return messages.get(status, f"""
🛂 *تحديث حالة التأشيرة*

مرحباً {client_name}،

تم تحديث حالة التأشيرة الخاصة بك.

📋 *الحالة الحالية:* {status}
📅 *التاريخ:* {self._get_current_date()}

شكراً لثقتكم بنا.

---
شركة تونس للاستشارات والخدمات
        """)
    
    def _get_current_date(self) -> str:
        """Obtenir la date actuelle formatée"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def send_visa_status_notification(self, client_data: Dict[str, Any], old_status: str, new_status: str) -> Dict[str, Any]:
        """
        Envoyer une notification de changement de statut de visa
        
        Args:
            client_data: Données du client
            old_status: Ancien statut
            new_status: Nouveau statut
            
        Returns:
            Résultat de l'envoi
        """
        try:
            # Vérifier si le statut a vraiment changé
            if old_status == new_status:
                return {"success": True, "message": "Aucun changement de statut"}
            
            # Récupérer les informations du client
            client_name = client_data.get('full_name', 'عميلنا العزيز')
            phone_number = client_data.get('whatsapp_number', '')
            
            if not phone_number:
                return {"success": False, "error": "Numéro WhatsApp non fourni"}
            
            # Générer le message
            message = self.get_visa_status_message(new_status, client_name)
            
            # Envoyer le message
            result = self.send_message(phone_number, message)
            
            if result["success"]:
                print(f"✅ Notification WhatsApp envoyée à {client_name} ({phone_number})")
                print(f"📋 Statut: {old_status} → {new_status}")
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Instance globale du service
whatsapp_service = WhatsAppService()
