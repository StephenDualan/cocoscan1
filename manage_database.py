#!/usr/bin/env python3
"""
Database Management for CocoScan
This script provides common database operations
"""

import sqlite3
import os
from database.db import init_db, get_user_scans, get_scan_statistics
from database.auth import create_simple_hash

def backup_database():
    """Create a backup of the database"""
    import shutil
    from datetime import datetime
    
    db_path = 'database/cocoscan.db'
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'database/cocoscan_backup_{timestamp}.db'
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

def reset_database():
    """Reset the database (delete and recreate)"""
    db_path = 'database/cocoscan.db'
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("✅ Old database deleted")
        except Exception as e:
            print(f"❌ Failed to delete database: {e}")
            return
    
    try:
        init_db()
        print("✅ Database reset successfully")
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")

def show_user_details():
    """Show detailed information about users and their scans"""
    db_path = 'database/cocoscan.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("👥 User Details")
        print("=" * 50)
        
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.created_at, u.last_login,
                   COUNT(s.id) as scan_count
            FROM users u
            LEFT JOIN scans s ON u.id = s.user_id
            GROUP BY u.id
            ORDER BY u.id
        """)
        
        users = cursor.fetchall()
        
        for user in users:
            user_id, username, email, created_at, last_login, scan_count = user
            print(f"\nUser ID: {user_id}")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Created: {created_at}")
            print(f"Last Login: {last_login or 'Never'}")
            print(f"Total Scans: {scan_count}")
            
            # Show recent scans for this user
            if scan_count > 0:
                cursor.execute("""
                    SELECT leaf_type, health_status, confidence, scan_date
                    FROM scans
                    WHERE user_id = ?
                    ORDER BY scan_date DESC
                    LIMIT 3
                """, (user_id,))
                
                recent_scans = cursor.fetchall()
                print("Recent Scans:")
                for scan in recent_scans:
                    leaf_type, health_status, confidence, scan_date = scan
                    print(f"  - {leaf_type}: {health_status} ({confidence:.2f}) - {scan_date}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def show_database_info():
    """Show general database information"""
    db_path = 'database/cocoscan.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📊 Database Information")
        print("=" * 50)
        
        # File size
        file_size = os.path.getsize(db_path)
        print(f"Database file size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Table counts
        tables = ['users', 'scans', 'leaf_types', 'health_statuses']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table.capitalize()}: {count} records")
        
        # Overall statistics
        stats = get_scan_statistics()
        if stats:
            print(f"\nOverall Scan Statistics:")
            print(f"  - Total scans: {stats['total_scans']}")
            print(f"  - Average confidence: {stats['avg_confidence']}%")
            print(f"  - Healthy leaves: {stats['healthy_count']}")
            print(f"  - Diseased leaves: {stats['diseased_count']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main_menu():
    """Main menu for database management"""
    while True:
        print("\n" + "=" * 50)
        print("🗄️  CocoScan Database Management")
        print("=" * 50)
        print("1. Show database information")
        print("2. Show user details")
        print("3. Backup database")
        print("4. Reset database (WARNING: This will delete all data!)")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            show_database_info()
        elif choice == "2":
            show_user_details()
        elif choice == "3":
            backup_database()
        elif choice == "4":
            confirm = input("⚠️  Are you sure you want to reset the database? (yes/no): ").strip().lower()
            if confirm == "yes":
                reset_database()
            else:
                print("Database reset cancelled.")
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please enter 1-5.")

if __name__ == "__main__":
    main_menu() 