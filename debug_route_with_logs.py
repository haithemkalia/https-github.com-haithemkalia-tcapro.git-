#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour ajouter des logs de debug dans la route /clients
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_debug_logs_to_route():
    """Ajouter des logs de debug dans la route /clients"""
    
    print("🔧 Ajout de logs de debug dans la route /clients")
    print("="*50)
    
    try:
        # Lire le fichier app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Trouver la fonction clients_list
        start_marker = '@app.route(\'/clients\')\ndef clients_list():'
        end_marker = 'except Exception as e:'
        
        if start_marker in content and end_marker in content:
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker, start_idx)
            
            if start_idx != -1 and end_idx != -1:
                # Extraire la fonction
                before_function = content[:start_idx]
                function_content = content[start_idx:end_idx]
                after_function = content[end_idx:]
                
                # Ajouter des logs de debug
                debug_function = function_content.replace(
                    '"""Page de liste des clients avec pagination"""',
                    '"""Page de liste des clients avec pagination"""\n        print("🔍 DEBUG: Début de clients_list()")'
                ).replace(
                    '# Récupérer les clients avec pagination',
                    'print(f"🔍 DEBUG: Filtres construits: {filters}")\n        print(f"🔍 DEBUG: Paramètres: page={page}, per_page={per_page}")\n        \n        # Récupérer les clients avec pagination'
                ).replace(
                    'clients, total = client_controller.get_all_clients(page, per_page)',
                    'clients, total = client_controller.get_all_clients(page, per_page)\n            print(f"🔍 DEBUG: get_all_clients retourne: {len(clients)} clients, total={total}")\n            if clients:\n                print(f"🔍 DEBUG: Premier client: {clients[0].get(\'client_id\')}")'
                ).replace(
                    'clients, total = client_controller.get_filtered_clients(filters, page, per_page)',
                    'clients, total = client_controller.get_filtered_clients(filters, page, per_page)\n            print(f"🔍 DEBUG: get_filtered_clients retourne: {len(clients)} clients, total={total}")\n            if clients:\n                print(f"🔍 DEBUG: Premier client filtré: {clients[0].get(\'client_id\')}")'
                ).replace(
                    'return render_template(\'clients.html\',',
                    'print(f"🔍 DEBUG: Avant render_template - clients: {len(clients)}, total: {total}")\n        print(f"🔍 DEBUG: Pagination: {pagination}")\n        \n        return render_template(\'clients.html\','
                )
                
                # Reconstituer le fichier
                new_content = before_function + debug_function + after_function
                
                # Sauvegarder le fichier modifié
                with open('app_debug.py', 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("✅ Fichier app_debug.py créé avec les logs de debug")
                print("\n📋 Instructions:")
                print("   1. Arrêter le serveur actuel (Ctrl+C)")
                print("   2. Lancer: python app_debug.py")
                print("   3. Accéder à http://localhost:5000/clients")
                print("   4. Observer les logs dans la console")
                
            else:
                print("❌ Impossible de localiser la fonction clients_list")
        else:
            print("❌ Marqueurs de fonction non trouvés")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_debug_logs_to_route()