#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os

def check_excel_columns():
    """Vérifier les colonnes du fichier Excel"""
    
    excel_file = 'قائمة الزبائن معرض_أكتوبر2025 (21).xlsx'
    
    if not os.path.exists(excel_file):
        print(f"❌ Fichier Excel non trouvé: {excel_file}")
        return
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(excel_file)
        
        print(f"📊 ANALYSE DU FICHIER EXCEL: {excel_file}")
        print("=" * 60)
        
        print(f"\n📋 COLONNES TROUVÉES ({len(df.columns)} au total):")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. '{col}'")
        
        print(f"\n📈 NOMBRE DE LIGNES: {len(df)}")
        
        # Chercher les colonnes qui correspondent à nos champs
        target_fields = {
            'الموظف المسؤول': ['الموظف المسؤول', 'اختيار الموظف', 'الموظف', 'المسؤول'],
            'تاريخ التقديم': ['تاريخ التقديم', 'تاريخ الطلب', 'تاريخ التسجيل', 'التاريخ']
        }
        
        print(f"\n🔍 البحث عن الأعمدة المطلوبة:")
        
        found_columns = {}
        
        for field_name, possible_names in target_fields.items():
            found = False
            for col in df.columns:
                col_clean = str(col).strip()
                for possible in possible_names:
                    if possible in col_clean or col_clean in possible:
                        print(f"   ✅ {field_name}: العمود '{col}' موجود")
                        found_columns[field_name] = col
                        found = True
                        break
                if found:
                    break
            
            if not found:
                print(f"   ❌ {field_name}: غير موجود")
        
        # Afficher un échantillon des données pour les colonnes trouvées
        if found_columns:
            print(f"\n📋 عينة من البيانات (أول 10 صفوف):")
            print("-" * 60)
            
            for field_name, col_name in found_columns.items():
                print(f"\n🔸 {field_name} (العمود: '{col_name}'):")
                sample_data = df[col_name].head(10)
                
                filled_count = sample_data.notna().sum()
                empty_count = sample_data.isna().sum()
                
                print(f"   📊 في العينة: {filled_count} مملوء، {empty_count} فارغ")
                
                for i, value in enumerate(sample_data, 1):
                    if pd.notna(value) and str(value).strip():
                        print(f"   {i:2d}. '{value}'")
                    else:
                        print(f"   {i:2d}. [فارغ]")
        
        # Statistiques générales pour toutes les colonnes
        print(f"\n📊 إحصائيات عامة لجميع الأعمدة:")
        print("-" * 60)
        
        for col in df.columns:
            filled = df[col].notna().sum()
            empty = df[col].isna().sum()
            percentage = (filled / len(df)) * 100
            print(f"   '{col}': {filled} مملوء ({percentage:.1f}%), {empty} فارغ")
        
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف: {e}")

if __name__ == "__main__":
    check_excel_columns()