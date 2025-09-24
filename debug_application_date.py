#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to check what's happening with application_date field
"""

import sqlite3
import os
import sys

def check_database():
    """Check the database directly to see what's being saved"""
    print("Checking database directly...")
    
    # Get the database path
    db_path = os.path.join(os.getcwd(), 'data', 'clients.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check the table structure
        print("\nTable structure:")
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col['name']}: {col['type']}")
        
        # Check recent clients
        print("\nRecent clients (last 5):")
        cursor.execute("SELECT client_id, full_name, application_date, file_date FROM clients ORDER BY created_at DESC LIMIT 5")
        recent_clients = cursor.fetchall()
        
        for client in recent_clients:
            print(f"  ID: {client['client_id']}")
            print(f"  Name: {client['full_name']}")
            print(f"  application_date: {client['application_date']}")
            print(f"  file_date: {client.get('file_date', 'N/A')}")
            print()
        
        # Check if TEST_001 exists
        print("Checking TEST_001 client:")
        cursor.execute("SELECT client_id, full_name, application_date, file_date, created_at FROM clients WHERE client_id = ?", ('TEST_001',))
        test_client = cursor.fetchone()
        
        if test_client:
            print(f"  Found TEST_001:")
            print(f"    Name: {test_client['full_name']}")
            print(f"    application_date: {test_client['application_date']}")
            print(f"    file_date: {test_client.get('file_date', 'N/A')}")
            print(f"    created_at: {test_client['created_at']}")
            
            # Check if there's a file_date column
            try:
                file_date_value = test_client['file_date']
                print(f"    file_date exists: {file_date_value}")
            except:
                print("    file_date column does not exist")
                
        else:
            print("  TEST_001 not found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def test_direct_insert():
    """Test direct database insert to see if application_date works"""
    print("\nTesting direct database insert...")
    
    db_path = os.path.join(os.getcwd(), 'data', 'clients.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert test data directly
        test_data = {
            'client_id': 'DEBUG_TEST',
            'full_name': 'Debug Test Client',
            'whatsapp_number': '+218911111111',
            'application_date': '2024-03-15',
            'transaction_date': '2024-03-20',
            'passport_number': 'DEBUG_PASS_001',
            'passport_status': 'موجود',
            'nationality': 'ليبي',
            'visa_status': 'تم التقديم في السيستام',
            'responsible_employee': 'اميرة',
            'notes': 'Direct database insert test'
        }
        
        # Get current data to see what fields are available
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        column_names = [col['name'] for col in columns]
        
        print(f"Available columns: {column_names}")
        
        # Build insert query based on available columns
        available_fields = []
        values = []
        
        for field, value in test_data.items():
            if field in column_names:
                available_fields.append(field)
                values.append(value)
        
        # Add missing required fields
        if 'processed_by' not in test_data:
            available_fields.append('processed_by')
            values.append('')
        
        if 'summary' not in test_data:
            available_fields.append('summary')
            values.append('')
            
        if 'created_at' not in test_data:
            available_fields.append('created_at')
            values.append('2024-03-15T10:00:00')
        
        # Build and execute query
        placeholders = ', '.join(['?' for _ in available_fields])
        fields_str = ', '.join(available_fields)
        
        query = f"INSERT INTO clients ({fields_str}) VALUES ({placeholders})"
        print(f"Query: {query}")
        print(f"Values: {values}")
        
        cursor.execute(query, values)
        conn.commit()
        
        # Check if insert worked
        cursor.execute("SELECT client_id, full_name, application_date FROM clients WHERE client_id = ?", ('DEBUG_TEST',))
        inserted = cursor.fetchone()
        
        if inserted:
            print(f"✅ Direct insert successful:")
            print(f"  application_date: {inserted['application_date']}")
        else:
            print("❌ Direct insert failed")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error with direct insert: {e}")
        return False

def main():
    """Main debug function"""
    print("=" * 60)
    print("Debugging application_date field issue")
    print("=" * 60)
    
    # Check database directly
    db_check = check_database()
    
    # Test direct insert
    direct_test = test_direct_insert()
    
    print("\n" + "=" * 60)
    print("Debug Summary:")
    print(f"Database check: {'✅ PASSED' if db_check else '❌ FAILED'}")
    print(f"Direct insert test: {'✅ PASSED' if direct_test else '❌ FAILED'}")
    print("=" * 60)

if __name__ == "__main__":
    main()