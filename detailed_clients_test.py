#!/usr/bin/env python3

import requests
import re

def detailed_clients_test():
    """Test détaillé pour identifier le problème spécifique"""
    
    url = "http://127.0.0.1:5000/clients"
    params = {
        'page': 1,
        'per_page': 50,
        'search': '',
        'status': '',
        'nationality': '',
        'employee': ''
    }
    
    try:
        print("🔍 Analyse détaillée de la page clients...")
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            content = response.text
            
            # Analyser le contenu spécifique
            print(f"\n📊 Statistiques de la page:")
            print(f"   - Taille totale: {len(content)} caractères")
            print(f"   - Nombre de <tr>: {content.count('<tr')}")
            print(f"   - Nombre de <td>: {content.count('<td')}")
            
            # Vérifier les données clients
            client_rows = re.findall(r'<tr>.*?CLI\d+.*?</tr>', content, re.DOTALL)
            print(f"   - Lignes client détectées: {len(client_rows)}")
            
            # Vérifier les problèmes JavaScript
            js_errors = []
            if 'error' in content.lower():
                error_patterns = [
                    r'console\.error\([^)]*\)',
                    r'showError\([^)]*\)',
                    r'alert\([^)]*error[^)]*\)',
                    r'خطأ[^<]*<'  # Erreurs arabes
                ]
                
                for pattern in error_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        js_errors.extend(matches)
            
            if js_errors:
                print(f"\n⚠️  Erreurs JavaScript détectées: {len(js_errors)}")
                for error in js_errors[:3]:
                    print(f"   - {error}")
            
            # Vérifier les styles CSS
            print(f"\n🎨 Analyse CSS:")
            if 'display: none' in content:
                hidden_elements = re.findall(r'<[^>]*style="[^"]*display:\s*none[^"]*"[^>]*>', content)
                print(f"   - Éléments cachés: {len(hidden_elements)}")
                for element in hidden_elements[:3]:
                    print(f"     * {element[:100]}...")
            
            # Vérifier les données vides
            empty_fields = re.findall(r'<span[^>]*class="field-value"[^>]*>\s*</span>', content)
            print(f"   - Champs vides: {len(empty_fields)}")
            
            # Vérifier la pagination
            pagination_match = re.search(r'<div[^>]*pagination[^>]*>(.*?)</div>', content, re.DOTALL)
            if pagination_match:
                pagination_html = pagination_match.group(1)
                page_links = re.findall(r'<a[^>]*>\d+</a>', pagination_html)
                print(f"   - Liens de pagination: {len(page_links)}")
            
            # Vérifier les scripts bloquants
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            blocking_scripts = []
            for i, script in enumerate(scripts):
                if 'document.write' in script or 'window.onload' in script:
                    blocking_scripts.append(i)
            
            if blocking_scripts:
                print(f"   - Scripts bloquants trouvés aux indices: {blocking_scripts}")
            
            print(f"\n💡 Recommandations:")
            if len(client_rows) == 0:
                print("   ❌ Aucun client trouvé - Vérifier la récupération des données")
            elif len(client_rows) < 10:
                print("   ⚠️  Peu de clients affichés - Vérifier la pagination")
            else:
                print("   ✅ Nombre de clients semble correct")
                
            if empty_fields:
                print(f"   ⚠️  {len(empty_fields)} champs vides détectés")
                
            if 'display: none' in content and len(client_rows) > 0:
                print("   ⚠️  Table cachée mais données présentes - Problème CSS/JavaScript")
                
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Flask")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    detailed_clients_test()