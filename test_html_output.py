#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test direct de la route Flask pour capturer le HTML généré
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_html_output():
    """Tester le HTML généré par la route /clients"""
    
    print("🌐 Test du HTML généré par la route /clients...")
    print("="*60)
    
    try:
        with app.test_client() as client:
            # Faire une requête GET sur /clients
            response = client.get('/clients')
            
            print(f"\n📊 Réponse HTTP:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Content-Type: {response.content_type}")
            print(f"   Content-Length: {len(response.data)} bytes")
            
            if response.status_code == 200:
                # Décoder le contenu HTML
                html_content = response.data.decode('utf-8')
                
                # Rechercher des éléments clés
                print(f"\n🔍 Analyse du contenu HTML:")
                
                # Vérifier la présence de clients
                if 'CLI0' in html_content:
                    print(f"   ✅ IDs clients (CLI0xxx) trouvés dans le HTML")
                    
                    # Compter les occurrences
                    cli_count = html_content.count('CLI0')
                    print(f"   📊 Nombre d'occurrences 'CLI0': {cli_count}")
                    
                    # Extraire quelques IDs
                    import re
                    cli_ids = re.findall(r'CLI0\d+', html_content)
                    unique_ids = list(set(cli_ids))
                    print(f"   📋 IDs uniques trouvés: {len(unique_ids)}")
                    print(f"   📋 Premiers IDs: {unique_ids[:5]}")
                    
                else:
                    print(f"   ❌ Aucun ID client (CLI0xxx) trouvé dans le HTML")
                
                # Vérifier les messages d'erreur
                if 'لا توجد نتائج' in html_content:
                    print(f"   ⚠️  Message 'لا توجد نتائج' trouvé")
                elif 'لا توجد عملاء' in html_content:
                    print(f"   ⚠️  Message 'لا توجد عملاء' trouvé")
                else:
                    print(f"   ✅ Aucun message d'erreur 'pas de clients' trouvé")
                
                # Vérifier la structure du tableau
                if '<table' in html_content and 'clientsTable' in html_content:
                    print(f"   ✅ Tableau des clients trouvé")
                    
                    # Compter les lignes de données
                    tbody_count = html_content.count('<tbody>')
                    tr_count = html_content.count('<tr>') - 1  # -1 pour l'en-tête
                    print(f"   📊 Nombre de <tbody>: {tbody_count}")
                    print(f"   📊 Nombre de lignes de données: {tr_count}")
                else:
                    print(f"   ❌ Tableau des clients non trouvé")
                
                # Vérifier la pagination
                if 'pagination' in html_content:
                    print(f"   ✅ Pagination trouvée")
                    
                    # Extraire le total
                    import re
                    total_match = re.search(r'من (\d+) عميل', html_content)
                    if total_match:
                        total = total_match.group(1)
                        print(f"   📊 Total affiché dans la pagination: {total}")
                else:
                    print(f"   ❌ Pagination non trouvée")
                
                # Sauvegarder un échantillon du HTML pour inspection
                print(f"\n💾 Sauvegarde d'un échantillon du HTML...")
                with open('html_sample.html', 'w', encoding='utf-8') as f:
                    # Sauvegarder les 5000 premiers caractères
                    f.write(html_content[:5000])
                print(f"   ✅ Échantillon sauvegardé dans 'html_sample.html'")
                
                # Rechercher des patterns spécifiques
                print(f"\n🔍 Recherche de patterns spécifiques:")
                patterns = [
                    ('معرف العميل', 'En-tête ID client'),
                    ('الاسم الكامل', 'En-tête nom complet'),
                    ('حالة التأشيرة', 'En-tête statut visa'),
                    ('text-primary', 'Style ID client'),
                    ('client.get', 'Appels template'),
                    ('{% for client in clients %}', 'Boucle template')
                ]
                
                for pattern, description in patterns:
                    if pattern in html_content:
                        print(f"   ✅ {description}: trouvé")
                    else:
                        print(f"   ❌ {description}: non trouvé")
                
            else:
                print(f"   ❌ Erreur HTTP: {response.status_code}")
        
        print("\n" + "="*60)
        print("🏁 Test terminé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_html_output()