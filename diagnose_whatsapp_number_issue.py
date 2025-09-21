#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic du problème WhatsApp pour le numéro +216 218913810603
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.whatsapp_service import whatsapp_service

def diagnose_whatsapp_number_issue():
    """Diagnostiquer le problème WhatsApp pour le numéro spécifique"""
    
    print('🔍 DIAGNOSTIC PROBLÈME WHATSAPP NUMÉRO +216 218913810603')
    print('=' * 60)

    try:
        # Le numéro problématique
        problematic_number = '+216 218913810603'
        print(f'📱 Numéro problématique: {problematic_number}')
        
        # Test 1: Nettoyage du numéro
        print('\n1️⃣ Test nettoyage du numéro...')
        clean_number = whatsapp_service._clean_phone_number(problematic_number)
        print(f'📱 Numéro nettoyé: {clean_number}')
        
        # Test 2: Vérifier si le numéro est valide
        print('\n2️⃣ Vérification validité du numéro...')
        if clean_number:
            print(f'✅ Numéro valide: {clean_number}')
            print(f'📏 Longueur: {len(clean_number)} chiffres')
        else:
            print('❌ Numéro invalide')
            return
        
        # Test 3: Analyser le format du numéro
        print('\n3️⃣ Analyse du format...')
        print(f'📱 Numéro original: {problematic_number}')
        print(f'📱 Numéro nettoyé: {clean_number}')
        
        # Le problème pourrait être que le numéro n'existe pas sur WhatsApp
        # ou que le format n'est pas correct pour WhatsApp
        
        # Test 4: Essayer différents formats
        print('\n4️⃣ Test avec différents formats...')
        
        test_formats = [
            '218913810603',      # Sans espaces ni +
            '216218913810603',   # Avec 216
            '2168913810603',     # Format corrigé
            '216913810603',      # Format alternatif
            '216891381060',      # Format court
        ]
        
        for fmt in test_formats:
            print(f'📱 Test format: {fmt}')
            clean_fmt = whatsapp_service._clean_phone_number(fmt)
            print(f'   → {clean_fmt}')
        
        # Test 5: Générer le message
        print('\n5️⃣ Test génération du message...')
        message = whatsapp_service.get_visa_status_message(
            'تمت الموافقة على التأشيرة', 
            'ابوبكر بادي'
        )
        print(f'📝 Message généré: {len(message)} caractères')
        print(f'📝 Aperçu: {message[:100]}...')
        
        # Test 6: Test d'ouverture WhatsApp
        print('\n6️⃣ Test ouverture WhatsApp...')
        print('⚠️  Ce test va essayer d\'ouvrir WhatsApp avec le numéro!')
        
        confirm = input('❓ Voulez-vous tester l\'ouverture WhatsApp ? (o/n): ')
        
        if confirm.lower() in ['o', 'oui', 'y', 'yes']:
            result = whatsapp_service.send_message(clean_number, message)
            
            if result.get('success'):
                print('✅ WhatsApp ouvert avec succès!')
                print(f'📱 Numéro utilisé: {result.get("phone_number", "N/A")}')
                print(f'📱 Méthode: {result.get("method", "N/A")}')
                print('🆕 Nouvelle conversation créée!')
            else:
                print(f'❌ Échec: {result.get("error", "Erreur inconnue")}')
        else:
            print('⏭️ Test annulé')
        
        # Test 7: Solutions possibles
        print('\n7️⃣ Solutions possibles...')
        print('🔧 Solutions pour le problème "Le numéro n\'est pas sur WhatsApp":')
        print('   1. ✅ Le numéro n\'existe pas sur WhatsApp')
        print('   2. ✅ Le numéro n\'est pas encore activé sur WhatsApp')
        print('   3. ✅ Le format du numéro n\'est pas correct')
        print('   4. ✅ Le numéro a été supprimé de WhatsApp')
        print('   5. ✅ Le numéro est bloqué ou restreint')
        
        print('\n💡 Solutions recommandées:')
        print('   • Vérifier que le numéro existe vraiment')
        print('   • Essayer d\'envoyer un message manuellement')
        print('   • Vérifier le format du numéro')
        print('   • Contacter le client pour confirmer le numéro')
        
    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_whatsapp_number_issue()
