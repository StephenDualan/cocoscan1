#!/usr/bin/env python3
"""
Database Viewer for CocoScan
This script helps you view and explore the database contents
"""

import sqlite3
import os

def view_database():
    db_path = 'database/cocoscan.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 CocoScan Database Explorer")
        print("=" * 50)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ No tables found in database!")
            return
        
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n" + "=" * 50)
        
        # Show table contents
        for table in tables:
            table_name = table[0]
            print(f"\n📊 Table: {table_name}")
            print("-" * 30)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"   - {col_name} ({col_type})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Total rows: {count}")
            
            # Show sample data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                
                print("Sample data:")
                for i, row in enumerate(rows, 1):
                    print(f"   Row {i}: {row}")
                
                if count > 5:
                    print(f"   ... and {count - 5} more rows")
            
            print()
        
        conn.close()
        print("✅ Database exploration completed!")
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

def show_specific_table(table_name):
    """Show detailed information about a specific table"""
    db_path = 'database/cocoscan.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n📋 Detailed view of table: {table_name}")
        print("=" * 50)
        
        # Get all data from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Columns: {', '.join(column_names)}")
        print(f"Total rows: {len(rows)}")
        print("-" * 50)
        
        for i, row in enumerate(rows, 1):
            print(f"Row {i}:")
            for j, value in enumerate(row):
                print(f"   {column_names[j]}: {value}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    view_database()
    
    # Ask user if they want to see specific table details
    print("\n" + "=" * 50)
    print("Options:")
    print("1. View specific table (enter table name)")
    print("2. Exit")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        table_name = input("Enter table name: ").strip()
        show_specific_table(table_name)
    elif choice == "2":
        print("Goodbye!")
    else:
        print("Invalid choice!") 