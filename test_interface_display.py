#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier l'affichage de "إشراف" dans l'interface
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.client import Client

def test_interface_display():
    """Tester l'affichage dans l'interface"""
    
    print('🧪 TEST D'AFFICHAGE DE "إشراف" DANS L'INTERFACE')
    print('=' * 60)
    
    # Afficher la liste des employés
    print('\n📋 Liste des employés disponibles:')
    for i, employee in enumerate(Client.EMPLOYEE_OPTIONS, 1):
        if employee == 'إشراف':
            print(f'   {i}. {employee} ⭐ (NOUVEAU)')
        else:
            print(f'   {i}. {employee}')
    
    # Vérifier que "إشراف" est présent
    if 'إشراف' in Client.EMPLOYEE_OPTIONS:
        print('\n✅ "إشراف" est disponible dans la liste des employés')
        print('✅ Les utilisateurs peuvent maintenant sélectionner "إشراف"')
    else:
        print('\n❌ "إشراف" n'est pas disponible dans la liste des employés')
    
    # Générer du HTML de test
    print('\n🌐 Génération de HTML de test:')
    print('<select name="responsible_employee">')
    for employee in Client.EMPLOYEE_OPTIONS:
        if employee == 'إشراف':
            print(f'    <option value="{employee}" selected>⭐ {employee}</option>')
        else:
            print(f'    <option value="{employee}">{employee}</option>')
    print('</select>')

if __name__ == "__main__":
    test_interface_display()
