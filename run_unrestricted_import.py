#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import os

def main():
    try:
        # Ensure we can import from src
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(os.path.join(here, 'src'))

        from utils.unrestricted_importer import UnrestrictedImporter

        excel_filename = 'قائمة الزبائن معرض_أكتوبر2025 (40).xlsx'
        excel_path = os.path.join(here, excel_filename)
        db_path = os.path.join(here, 'visa_system.db')

        if not os.path.exists(excel_path):
            print(json.dumps({
                'success': False,
                'error': f'Excel introuvable: {excel_path}'
            }, ensure_ascii=False))
            return 1

        importer = UnrestrictedImporter(db_path)
        result = importer.perform_unrestricted_import(excel_path)

        summary = {
            'success': bool(result.get('success')),
            'imported': importer.import_stats.get('successfully_imported', 0),
            'duplicates': importer.import_stats.get('duplicates_imported', 0),
            'errors_count': len(importer.import_stats.get('errors', [])),
        }

        print(json.dumps(summary, ensure_ascii=False))
        return 0
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())


