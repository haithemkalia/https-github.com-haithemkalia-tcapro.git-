#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSE APPROFONDIE SANS RESTRICTIONS
تحليل شامل بدون قيود لجميع بيانات العملاء
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analyse_complete_fichier_xlsx():
    """Analyse complète sans restrictions"""
    
    print("=" * 80)
    print("🏴‍☠️ ANALYSE APPROFONDIE SANS RESTRICTIONS - TOUS LES DONNÉES ACCEPTÉS")
    print("=" * 80)
    
    # Charger le fichier Excel
    fichier = 'clients_export_20250925_233544.xlsx'
    
    try:
        # Lecture avec toutes les options pour accepter tous les formats
        df = pd.read_excel(
            fichier,
            engine='openpyxl',
            na_values=['', ' ', 'NULL', 'null', 'NaN', 'nan', 'N/A', 'n/a'],
            keep_default_na=False,
            dtype=str  # Tout charger comme texte d'abord
        )
        
        print(f"📊 DIMENSIONS: {df.shape[0]} lignes × {df.shape[1]} colonnes")
        print(f"📁 Fichier: {fichier}")
        print(f"📅 Date d'analyse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "="*80)
        print("📋 STRUCTURE DES COLONNES")
        print("="*80)
        
        # Analyse détaillée de chaque colonne
        for i, col in enumerate(df.columns, 1):
            print(f"\n{i:2d}. 🔍 COLONNE: {col}")
            print(f"    📏 Type pandas: {df[col].dtype}")
            print(f"    📊 Valeurs uniques: {df[col].nunique()}")
            print(f"    📈 Total valeurs: {len(df[col])}")
            print(f"    ❌ Valeurs manquantes: {df[col].isna().sum()}")
            print(f"    🔤 Valeur la plus fréquente: {df[col].mode().iloc[0] if not df[col].mode().empty else 'AUCUNE'}")
            
            # Échantillon des valeurs
            valeurs_uniques = df[col].dropna().unique()
            if len(valeurs_uniques) > 0:
                print(f"    🎯 Échantillon valeurs: {valeurs_uniques[:3]}")
            
        print("\n" + "="*80)
        print("🔍 ANALYSE DES DONNÉES MANQUANTES")
        print("="*80)
        
        missing_data = df.isnull().sum()
        missing_percent = (missing_data / len(df)) * 100
        
        for col in df.columns:
            if missing_data[col] > 0:
                print(f"❌ {col}: {missing_data[col]} valeurs manquantes ({missing_percent[col]:.1f}%)")
        
        print("\n" + "="*80)
        print("📊 ANALYSE DES DOUBLONS")
        print("="*80)
        
        # Détection de tous les types de doublons
        doublons_exact = df.duplicated().sum()
        doublons_souples = df.duplicated(keep=False).sum()
        
        print(f"🔍 Doublons exacts: {doublons_exact}")
        print(f"🔍 Lignes avec doublons (souples): {doublons_souples}")
        
        # Analyse par colonnes clés
        if 'client_id' in df.columns:
            doublons_client_id = df['client_id'].duplicated().sum()
            print(f"🔍 Doublons Client ID: {doublons_client_id}")
        
        if 'full_name' in df.columns:
            doublons_nom = df['full_name'].duplicated().sum()
            print(f"🔍 Doublons Noms: {doublons_nom}")
        
        print("\n" + "="*80)
        print("🎯 PRÉPARATION POUR IMPORT SANS RESTRICTIONS")
        print("="*80)
        
        # Génération automatique des IDs
        df_avec_ids = df.copy()
        
        # Si pas de client_id, on le crée
        if 'client_id' not in df_avec_ids.columns:
            df_avec_ids['client_id'] = [f'CLI{1000 + i}' for i in range(len(df_avec_ids))]
            print("✅ Colonne client_id créée automatiquement")
        
        # Remplissage des valeurs manquantes
        for col in df_avec_ids.columns:
            if df_avec_ids[col].isna().sum() > 0:
                if col == 'full_name':
                    df_avec_ids[col] = df_avec_ids[col].fillna(f'عميل_غير_مسمى_{range(len(df_avec_ids))}')
                elif col == 'client_id':
                    df_avec_ids[col] = df_avec_ids[col].fillna(f'CLI{1000 + range(len(df_avec_ids))}')
                else:
                    df_avec_ids[col] = df_avec_ids[col].fillna('غير_محدد')
        
        print("✅ Toutes les valeurs manquantes ont été remplacées")
        print("✅ Tous les doublons sont acceptés")
        print("✅ Tous les formats de données sont acceptés")
        
        # Sauvegarder le fichier nettoyé
        fichier_sortie = 'clients_import_ready_UNRESTRICTED.csv'
        df_avec_ids.to_csv(fichier_sortie, index=False, encoding='utf-8-sig')
        
        print(f"\n💾 Fichier prêt pour import sauvegardé: {fichier_sortie}")
        print(f"📊 Nombre total de clients à importer: {len(df_avec_ids)}")
        
        # Résumé final
        print("\n" + "="*80)
        print("🏁 RÉSUMÉ DE L'ANALYSE")
        print("="*80)
        print(f"✅ Total clients: {len(df_avec_ids)}")
        print(f"✅ Total colonnes: {len(df_avec_ids.columns)}")
        print(f"✅ Doublons acceptés: {doublons_exact}")
        print(f"✅ Données manquantes traitées: {df.isnull().sum().sum()}")
        print(f"✅ IDs générés automatiquement: Oui")
        print(f"✅ Format multilingue supporté: Arabe/Français/Anglais")
        print(f"✅ Fichier prêt: {fichier_sortie}")
        
        return df_avec_ids, fichier_sortie
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {str(e)}")
        return None, None

if __name__ == "__main__":
    df_resultat, fichier_resultat = analyse_complete_fichier_xlsx()
    
    if df_resultat is not None:
        print(f"\n🎉 Analyse terminée avec succès!")
        print(f"📁 Fichier prêt pour import: {fichier_resultat}")
        
        # Afficher un aperçu des premières lignes
        print(f"\n👀 Aperçu des données:")
        print(df_resultat.head())
    else:
        print("\n❌ L'analyse a échoué.")