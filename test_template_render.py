#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du rendu du template clients.html
"""

import sys
from pathlib import Path
from flask import Flask, render_template

# Ajouter le dossier src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_template_rendering():
    """Tester le rendu du template clients.html"""
    print("🎨 TEST DU RENDU DU TEMPLATE")
    print("=" * 60)
    
    try:
        from database.database_manager import DatabaseManager
        from controllers.client_controller import ClientController
        from models.client import Client
        
        # Créer une app Flask temporaire
        app = Flask(__name__)
        app.secret_key = 'test_key'
        
        # Configuration pour les templates RTL
        @app.context_processor
        def inject_rtl_support():
            from datetime import datetime
            return {
                'rtl_support': True,
                'app_title': '🛂 نظام تتبع التأشيرات الذكي - TCA',
                'company_name': 'شركة تونس للاستشارات والخدمات',
                'facebook_link': 'https://www.facebook.com/share/1D4dHp2z74/?mibextid=wwXIfr',
                'current_datetime': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        
        with app.app_context():
            # Initialiser les contrôleurs
            db_manager = DatabaseManager()
            client_controller = ClientController(db_manager)
            
            print("✅ App Flask et contrôleurs initialisés")
            
            # Récupérer les données comme dans la route
            page = 1
            per_page = 10  # Moins pour le test
            clients, total = client_controller.get_all_clients(page, per_page)
            
            print(f"\n📊 Données récupérées:")
            print(f"   - Clients: {len(clients)}")
            print(f"   - Total: {total}")
            
            if not clients:
                print("❌ Aucun client récupéré")
                return False
            
            # Préparer le contexte du template
            total_pages = (total + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < total_pages
            
            pagination = {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'prev_num': page - 1 if has_prev else None,
                'next_num': page + 1 if has_next else None
            }
            
            template_context = {
                'clients': clients,
                'pagination': pagination,
                'search_term': '',
                'status_filter': '',
                'nationality_filter': '',
                'employee_filter': '',
                'visa_statuses': Client.VISA_STATUS_OPTIONS,
                'nationalities': Client.NATIONALITY_OPTIONS,
                'employees': Client.EMPLOYEE_OPTIONS
            }
            
            print(f"\n🎨 Contexte du template préparé")
            
            # Tenter de rendre le template
            try:
                html_content = render_template('clients.html', **template_context)
                print(f"\n✅ Template rendu avec succès")
                print(f"   - Taille du HTML: {len(html_content)} caractères")
                
                # Vérifier la présence de données clients dans le HTML
                first_client = clients[0]
                client_id = first_client.get('client_id', '')
                full_name = first_client.get('full_name', '')
                
                print(f"\n🔍 Vérification du contenu HTML:")
                print(f"   - Client ID '{client_id}' présent: {'✅' if client_id in html_content else '❌'}")
                print(f"   - Nom '{full_name}' présent: {'✅' if full_name in html_content else '❌'}")
                print(f"   - Balise <tbody> présente: {'✅' if '<tbody>' in html_content else '❌'}")
                print(f"   - Balise <tr> présente: {'✅' if '<tr>' in html_content else '❌'}")
                
                # Extraire la section tbody pour analyse
                tbody_start = html_content.find('<tbody>')
                tbody_end = html_content.find('</tbody>')
                
                if tbody_start != -1 and tbody_end != -1:
                    tbody_content = html_content[tbody_start:tbody_end + 8]
                    print(f"\n📋 Contenu de <tbody>:")
                    print(f"   - Taille: {len(tbody_content)} caractères")
                    print(f"   - Nombre de <tr>: {tbody_content.count('<tr>')}")
                    
                    if len(tbody_content) < 100:
                        print(f"   - Contenu complet: {tbody_content}")
                    else:
                        print(f"   - Début: {tbody_content[:200]}...")
                else:
                    print(f"\n❌ Section <tbody> non trouvée")
                
                # Vérifier la condition {% if clients %}
                if_clients_present = '{% if clients %}' in open('templates/clients.html', 'r', encoding='utf-8').read()
                print(f"\n🔧 Condition template:")
                status_icon = '✅' if if_clients_present else '❌'
                print(f"   - 'if clients' dans le template: {status_icon}")
                print(f"   - len(clients) = {len(clients)} (doit être > 0)")
                
                return client_id in html_content and full_name in html_content
                
            except Exception as template_error:
                print(f"❌ Erreur de rendu du template: {template_error}")
                import traceback
                traceback.print_exc()
                return False
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_syntax():
    """Vérifier la syntaxe du template"""
    print(f"\n🔍 VÉRIFICATION DE LA SYNTAXE DU TEMPLATE")
    print("=" * 60)
    
    try:
        template_path = Path('templates/clients.html')
        if not template_path.exists():
            print(f"❌ Template non trouvé: {template_path}")
            return False
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Template lu: {len(content)} caractères")
        
        # Vérifier les éléments critiques
        critical_elements = [
            '{% if clients %}',
            '{% for client in clients %}',
            'client.get(',
            '</tbody>',
            '{% endfor %}',
            '{% endif %}'
        ]
        
        print(f"\n🔧 Éléments critiques:")
        for element in critical_elements:
            present = element in content
            status_icon = '✅' if present else '❌'
            print(f"   - '{element}': {status_icon}")
        
        # Compter les balises importantes
        print(f"\n📊 Statistiques du template:")
        print(f"   - Lignes: {content.count(chr(10)) + 1}")
        if_count = content.count('{% if')
        for_count = content.count('{% for')
        get_count = content.count('client.get(')
        print(f"   - if statements: {if_count}")
        print(f"   - for loops: {for_count}")
        print(f"   - client.get(): {get_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lecture template: {e}")
        return False

def main():
    """Fonction principale"""
    syntax_ok = test_template_syntax()
    render_ok = test_template_rendering()
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS:")
    syntax_status = '✅ OK' if syntax_ok else '❌ Erreur'
    render_status = '✅ OK' if render_ok else '❌ Erreur'
    print(f"   - Syntaxe du template: {syntax_status}")
    print(f"   - Rendu du template: {render_status}")
    
    if syntax_ok and render_ok:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ Le template devrait afficher les clients correctement")
    else:
        print("\n❌ PROBLÈMES DÉTECTÉS")
        print("🔧 Vérifiez les erreurs ci-dessus")

if __name__ == "__main__":
    main()