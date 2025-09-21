#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
import os

def main():
    db_path = os.path.join(os.path.dirname(__file__), 'visa_system.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        total = c.execute('SELECT COUNT(*) FROM clients').fetchone()[0]
        with_full_name = c.execute("SELECT COUNT(*) FROM clients WHERE IFNULL(trim(full_name),'')<>''").fetchone()[0]
        with_whatsapp = c.execute("SELECT COUNT(*) FROM clients WHERE IFNULL(trim(whatsapp_number),'')<>''").fetchone()[0]
        rows = c.execute(
            "SELECT client_id, full_name, whatsapp_number, nationality, visa_status, processed_by FROM clients LIMIT 10"
        ).fetchall()
        print(json.dumps({
            'total': total,
            'with_full_name': with_full_name,
            'with_whatsapp': with_whatsapp,
            'samples': rows
        }, ensure_ascii=False))
    finally:
        conn.close()

if __name__ == '__main__':
    main()


