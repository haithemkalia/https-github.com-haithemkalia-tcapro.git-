#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple pour capturer le HTML de la route /clients
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_clients_html():
    """Tester le HTML généré par /clients"""
    
    print("🌐 Test HTML de la route /clients")
    print("="*50)
    
    try:
        with app.test_client() as client:
            # Faire une requête GET sur /clients
            response = client.get('/clients')
            
            print(f"Status Code: {response.status_code}")
            print(f"Content-Length: {len(response.data)} bytes")
            
            if response.status_code == 200:
                html_content = response.data.decode('utf-8')
                
                # Sauvegarder le HTML complet
                with open('clients_page_full.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print("✅ HTML sauvegardé dans 'clients_page_full.html'")
                
                # Rechercher des patterns critiques
                patterns = [
                    'CLI0',
                    'لا توجد نتائج',
                    'لا توجد عملاء',
                    '<tbody>',
                    'clientsTable',
                    'pagination'
                ]
                
                print("\n🔍 Analyse des patterns:")
                for pattern in patterns:
                    count = html_content.count(pattern)
                    print(f"   {pattern}: {count} occurrence(s)")
                
                # Extraire la section du tableau
                if '<table' in html_content:
                    table_start = html_content.find('<table')
                    table_end = html_content.find('</table>') + 8
                    if table_end > 7:
                        table_section = html_content[table_start:table_end]
                        with open('table_section.html', 'w', encoding='utf-8') as f:
                            f.write(table_section)
                        print("✅ Section tableau sauvegardée dans 'table_section.html'")
                
                # Rechercher la condition if clients
                if_clients_patterns = [
                    '{% if clients %}',
                    '{% if not clients %}',
                    'if clients',
                    'if not clients'
                ]
                
                print("\n🔍 Conditions template:")
                for pattern in if_clients_patterns:
                    if pattern in html_content:
                        print(f"   ✅ Trouvé: {pattern}")
                    else:
                        print(f"   ❌ Non trouvé: {pattern}")
                
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
        
        print("\n🏁 Test terminé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clients_html()