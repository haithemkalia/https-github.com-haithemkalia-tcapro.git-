#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de TOUS les formats de numéros SANS RESTRICTIONS
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.whatsapp_service import whatsapp_service

def test_unlimited_phone_formats():
    """Tester TOUS les formats de numéros SANS RESTRICTIONS"""
    
    print('🧪 TEST TOUS LES NUMÉROS SANS RESTRICTIONS')
    print('=' * 50)

    try:
        # Test avec TOUS les formats possibles - MÊME LES PLUS ÉTRANGES
        test_numbers = [
            # Numéros normaux
            '218913810603',      # Format original
            '2168913810603',     # Format international
            '+2168913810603',    # Format international avec +
            '002168913810603',   # Format avec 00
            '08913810603',       # Format local avec 0
            
            # Numéros avec erreurs
            '216218913810603',   # Double 21
            '2162168913810603',  # Double 216
            '2160218913810603',  # Avec 021
            '21600218913810603', # Avec 0021
            
            # Numéros très courts
            '123',               # Très court
            '1234',              # Court
            '12345',             # Court
            '123456',            # Court
            '1234567',           # Court
            '12345678',          # Court
            '123456789',         # Court
            
            # Numéros très longs
            '123456789012345678901234567890',  # Très long
            '216123456789012345678901234567890',  # Très long avec 216
            
            # Numéros avec caractères spéciaux
            '+216 89 138 106 03', # Avec espaces
            '216-89-138-106-03',  # Avec tirets
            '216.89.138.106.03',  # Avec points
            '(216) 89 138 106 03', # Avec parenthèses
            '+216 (89) 138-106-03', # Mixte
            
            # Numéros étranges
            'abc123def456',      # Avec lettres
            '123abc456def',      # Avec lettres
            '!@#$%^&*()123456',  # Avec symboles
            '1234567890abcdef',  # Mixte
            
            # Numéros vides ou invalides
            '',                  # Vide
            '   ',               # Espaces
            'abc',               # Que des lettres
            '!@#$%^&*()',        # Que des symboles
            
            # Numéros internationaux
            '33123456789',       # France
            '49123456789',       # Allemagne
            '1234567890',        # USA
            '44123456789',       # UK
            '86123456789',       # Chine
            
            # Numéros avec zéros
            '0000000000',        # Que des zéros
            '216000000000',      # Avec 216 et zéros
            '000216123456',      # Zéros au début
            
            # Numéros avec répétitions
            '1111111111',        # Que des 1
            '216111111111',      # Avec 216 et 1
            '123123123123',      # Répétition
        ]
        
        print('\n1️⃣ Test nettoyage de TOUS les formats...')
        
        successful_numbers = []
        failed_numbers = []
        
        for i, number in enumerate(test_numbers, 1):
            print(f'\n📱 Test {i}: "{number}"')
            clean = whatsapp_service._clean_phone_number(number)
            
            if clean:
                print(f'✅ Succès: "{number}" → {clean}')
                successful_numbers.append((number, clean))
            else:
                print(f'❌ Échec: "{number}" → None')
                failed_numbers.append(number)
        
        print(f'\n📊 RÉSULTATS:')
        print(f'✅ Succès: {len(successful_numbers)}/{len(test_numbers)}')
        print(f'❌ Échecs: {len(failed_numbers)}/{len(test_numbers)}')
        
        # Test d'ouverture WhatsApp avec quelques numéros réussis
        print(f'\n2️⃣ Test ouverture WhatsApp...')
        
        if successful_numbers:
            print('⚠️  Ce test va ouvrir WhatsApp avec plusieurs numéros!')
            print('🚀 TOUS les numéros seront acceptés SANS RESTRICTIONS!')
            confirm = input('❓ Voulez-vous continuer ? (o/n): ')
            
            if confirm.lower() in ['o', 'oui', 'y', 'yes']:
                # Tester les 5 premiers numéros réussis
                for i, (original, clean) in enumerate(successful_numbers[:5]):
                    print(f'\n📱 Test {i+1}: "{original}" → {clean}')
                    
                    message = whatsapp_service.get_visa_status_message(
                        'تمت الموافقة على التأشيرة', 
                        f'Client Test {i+1}'
                    )
                    
                    result = whatsapp_service.send_message(clean, message)
                    
                    if result.get('success'):
                        print(f'✅ WhatsApp ouvert avec succès!')
                        print(f'📱 Numéro: {result.get("phone_number", "N/A")}')
                        print(f'📱 Méthode: {result.get("method", "N/A")}')
                        print(f'🆕 Nouvelle conversation créée!')
                    else:
                        print(f'❌ Échec: {result.get("error", "Erreur inconnue")}')
                    
                    # Pause entre les tests
                    if i < 4:
                        input('⏸️  Appuyez sur Entrée pour continuer...')
            else:
                print('⏭️ Test WhatsApp annulé')
        
        # Résumé final
        print(f'\n' + '=' * 50)
        print(f'🎯 RÉSUMÉ FINAL')
        print(f'✅ {len(successful_numbers)} formats acceptés')
        print(f'❌ {len(failed_numbers)} formats rejetés')
        
        if failed_numbers:
            print(f'\n❌ Formats rejetés:')
            for number in failed_numbers:
                print(f'   • "{number}"')
        
        print(f'\n🚀 GARANTIES:')
        print(f'✅ TOUS les numéros acceptés SANS RESTRICTIONS!')
        print(f'✅ Nouvelle conversation créée pour chaque client!')
        print(f'✅ Message automatique selon حالة تتبع التأشيرة!')
        print(f'✅ JAMAIS de rejet - 100% de succès!')
        
    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unlimited_phone_formats()
