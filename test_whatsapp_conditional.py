#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la fonctionnalité WhatsApp conditionnelle
Vérifier que le texte de demande de passeport n'apparaît que pour l'état "تم القبول"
"""

import sys
from pathlib import Path

# Ajouter le chemin pour les imports
sys.path.append(str(Path(__file__).parent / 'src'))

from controllers.client_controller import ClientController
from database.database_manager import DatabaseManager

def test_whatsapp_conditional_message():
    """Tester la génération conditionnelle des messages WhatsApp"""
    print("=== Test de la génération conditionnelle des messages WhatsApp ===")
    
    try:
        # Initialiser le contrôleur
        db_manager = DatabaseManager()
        controller = ClientController(db_manager)
        
        # Récupérer quelques clients pour les tests
        all_clients = controller.get_all_clients()
        if not all_clients:
            print("❌ Aucun client trouvé dans la base de données")
            return
        
        # Tester avec différents états
        test_states = ["تم القبول", "التقديم", "قيد المراجعة", "تم الرفض"]
        
        # Prendre le premier client pour les tests
        test_client = all_clients[0]
        client_id = test_client['client_id']
        original_status = test_client['visa_status']
        
        print(f"\n🧪 Test avec le client: {client_id} ({test_client['full_name']})")
        print(f"État original: {original_status}")
        
        for state in test_states:
            print(f"\n--- Test avec l'état: {state} ---")
            
            # Temporairement changer l'état du client
            controller.update_client_status(client_id, state)
            
            # Générer le message WhatsApp
            result = controller.generate_whatsapp_message(client_id)
            
            if result['success']:
                message = result['message']
                passport_text = "نأمل من سيادتكم تسليمنا جواز السفر في اقرب وقت ممكن"
                
                if state == "تم القبول":
                    if passport_text in message:
                        print(f"✅ CORRECT: Texte de passeport INCLUS pour '{state}'")
                    else:
                        print(f"❌ ERREUR: Texte de passeport MANQUANT pour '{state}'")
                else:
                    if passport_text not in message:
                        print(f"✅ CORRECT: Texte de passeport EXCLU pour '{state}'")
                    else:
                        print(f"❌ ERREUR: Texte de passeport PRÉSENT pour '{state}' (ne devrait pas l'être)")
                
                # Afficher un extrait du message
                print(f"Message généré: {message[:100]}...")
            else:
                print(f"❌ Erreur lors de la génération: {result['error']}")
        
        # Restaurer l'état original
        controller.update_client_status(client_id, original_status)
        print(f"\n🔄 État du client restauré à: {original_status}")
        
        print("\n=== Test terminé ===")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_whatsapp_conditional_message()