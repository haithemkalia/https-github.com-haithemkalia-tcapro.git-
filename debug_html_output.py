#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Débogage du HTML généré par la page /clients
"""

import requests
import time

def debug_html_output():
    """Déboguer le HTML généré"""
    print("🔍 DÉBOGAGE DU HTML GÉNÉRÉ")
    print("=" * 60)
    
    try:
        print("⏳ Attente du serveur...")
        time.sleep(2)
        
        # Récupérer la page clients
        response = requests.get("http://localhost:5000/clients", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
        
        html_content = response.text
        print(f"✅ Page récupérée: {len(html_content)} caractères")
        
        # Analyser le contenu HTML
        print("\n🔍 Analyse du contenu HTML:")
        
        # Vérifier les éléments de base
        checks = {
            'DOCTYPE': '<!DOCTYPE html>' in html_content,
            'HTML tag': '<html' in html_content,
            'Body tag': '<body' in html_content,
            'Container': 'container-fluid' in html_content,
            'Card': 'card-modern' in html_content,
            'Table': '<table' in html_content,
            'Table ID': 'clientsTable' in html_content,
            'Thead': '<thead>' in html_content,
            'Tbody': '<tbody>' in html_content,
            'Arabic text': 'إدارة العملاء' in html_content,
            'Client data': 'CLI' in html_content,
            'Arabic names': 'محمد' in html_content or 'عبد' in html_content
        }
        
        for check, result in checks.items():
            status = '✅' if result else '❌'
            print(f"   - {check}: {status}")
        
        # Chercher des erreurs ou messages spécifiques
        print("\n🚨 Recherche d'erreurs:")
        error_indicators = [
            'error',
            'Error',
            'خطأ',
            'لا توجد نتائج',
            'No results',
            'Exception',
            'Traceback'
        ]
        
        for indicator in error_indicators:
            if indicator in html_content:
                print(f"   ⚠️  Trouvé: '{indicator}'")
        
        # Extraire et afficher des sections spécifiques
        print("\n📋 Sections importantes:")
        
        # Section title
        if 'إدارة العملاء' in html_content:
            start = html_content.find('إدارة العملاء') - 50
            end = html_content.find('إدارة العملاء') + 100
            section = html_content[max(0, start):end]
            print(f"   - Titre: ...{section}...")
        
        # Section table
        table_start = html_content.find('<table')
        if table_start != -1:
            table_end = html_content.find('</table>', table_start) + 8
            if table_end > table_start:
                table_section = html_content[table_start:table_end]
                print(f"   - Table trouvée: {len(table_section)} caractères")
                
                # Analyser le contenu de la table
                tbody_start = table_section.find('<tbody>')
                tbody_end = table_section.find('</tbody>')
                
                if tbody_start != -1 and tbody_end != -1:
                    tbody_content = table_section[tbody_start:tbody_end + 8]
                    print(f"   - Tbody: {len(tbody_content)} caractères")
                    
                    if len(tbody_content) < 200:
                        print(f"   - Contenu tbody: {tbody_content}")
                    else:
                        print(f"   - Début tbody: {tbody_content[:200]}...")
                else:
                    print(f"   - ❌ Tbody non trouvé dans la table")
            else:
                print(f"   - ❌ Fin de table non trouvée")
        else:
            print(f"   - ❌ Aucune table trouvée")
        
        # Section "لا توجد نتائج" (No results)
        no_results_pos = html_content.find('لا توجد نتائج')
        if no_results_pos != -1:
            start = max(0, no_results_pos - 100)
            end = min(len(html_content), no_results_pos + 200)
            section = html_content[start:end]
            print(f"   - Message 'Aucun résultat': ...{section}...")
        
        # Sauvegarder le HTML pour inspection manuelle
        with open('debug_clients_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n💾 HTML sauvegardé dans: debug_clients_page.html")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    success = debug_html_output()
    
    if success:
        print("\n✅ Débogage terminé")
        print("📄 Consultez le fichier debug_clients_page.html pour plus de détails")
    else:
        print("\n❌ Échec du débogage")

if __name__ == "__main__":
    main()