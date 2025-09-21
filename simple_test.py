#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple pour vérifier l'état actuel
"""

import requests
import time

def simple_test():
    """Test simple de l'interface"""
    print("🔍 TEST SIMPLE")
    print("=" * 40)
    
    try:
        time.sleep(2)
        
        # Test de la page clients
        response = requests.get("http://localhost:5000/clients", timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            
            # Vérifications simples
            checks = {
                'Titre page': 'إدارة العملاء' in html,
                'Table HTML': '<table' in html,
                'Table ID': 'clientsTable' in html,
                'Tbody': '<tbody>' in html,
                'Message vide': 'لا توجد نتائج' in html,
                'Données clients': 'CLI' in html,
                'Noms arabes': 'محمد' in html or 'عبد' in html,
                'Résultats count': 'النتائج:' in html
            }
            
            for check, result in checks.items():
                status = '✅' if result else '❌'
                print(f"{check}: {status}")
            
            # Extraire le nombre de résultats
            if 'النتائج:' in html:
                start = html.find('النتائج:')
                end = html.find('عميل', start)
                if start != -1 and end != -1:
                    result_text = html[start:end+4]
                    print(f"\nTexte résultats: {result_text}")
            
            # Sauvegarder pour inspection
            with open('simple_test_output.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"\nHTML sauvegardé: simple_test_output.html")
            
            return 'CLI' in html
        else:
            print(f"Erreur HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    success = simple_test()
    print(f"\nRésultat: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")