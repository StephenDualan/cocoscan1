#!/usr/bin/env python3
"""
Add Test Data to CocoScan Database
This script adds sample data to demonstrate the database functionality
"""

from database.db import (
    init_db, create_user, save_scan, get_user_scans, 
    get_scan_statistics, get_leaf_types, get_health_statuses
)
from database.auth import create_simple_hash

def add_test_data():
    print("🧪 Adding Test Data to CocoScan Database")
    print("=" * 50)
    
    # Initialize database
    print("1. Initializing database...")
    init_db()
    print("   ✅ Database initialized")
    
    # Create test users
    print("\n2. Creating test users...")
    users_data = [
        ("farmer1", "password123", "farmer1@example.com"),
        ("farmer2", "password456", "farmer2@example.com"),
        ("researcher", "research789", "researcher@example.com")
    ]
    
    user_ids = []
    for username, password, email in users_data:
        password_hash = create_simple_hash(password)
        user_id = create_user(username, password_hash, email)
        if user_id:
            user_ids.append(user_id)
            print(f"   ✅ Created user: {username} (ID: {user_id})")
        else:
            print(f"   ❌ Failed to create user: {username}")
    
    # Add test scans
    print("\n3. Adding test scans...")
    scan_data = [
        (user_ids[0], "Coconut", "Healthy", 0.98, "coconut_healthy.jpg", "No disease detected", "Farm A", "Sunny"),
        (user_ids[0], "Coconut", "Mild Disease", 0.85, "coconut_mild.jpg", "Minor yellowing observed", "Farm A", "Cloudy"),
        (user_ids[1], "Banana", "Healthy", 0.92, "banana_healthy.jpg", "Healthy banana leaves", "Farm B", "Sunny"),
        (user_ids[1], "Banana", "Moderate Disease", 0.78, "banana_disease.jpg", "Black sigatoka detected", "Farm B", "Rainy"),
        (user_ids[2], "Mango", "Healthy", 0.95, "mango_healthy.jpg", "Excellent condition", "Research Farm", "Sunny"),
        (user_ids[2], "Mango", "Severe Disease", 0.65, "mango_severe.jpg", "Anthracnose infection", "Research Farm", "Humid")
    ]
    
    for scan_info in scan_data:
        scan_id = save_scan(*scan_info)
        if scan_id:
            print(f"   ✅ Added scan {scan_id}: {scan_info[1]} - {scan_info[2]}")
        else:
            print(f"   ❌ Failed to add scan: {scan_info[1]}")
    
    print("\n" + "=" * 50)
    print("📊 Database Summary:")
    
    # Show statistics for each user
    for i, user_id in enumerate(user_ids):
        stats = get_scan_statistics(user_id)
        if stats:
            print(f"\nUser {i+1} Statistics:")
            print(f"   - Total scans: {stats['total_scans']}")
            print(f"   - Average confidence: {stats['avg_confidence']}%")
            print(f"   - Healthy leaves: {stats['healthy_count']}")
            print(f"   - Diseased leaves: {stats['diseased_count']}")
    
    # Show overall statistics
    overall_stats = get_scan_statistics()
    if overall_stats:
        print(f"\nOverall Statistics:")
        print(f"   - Total scans: {overall_stats['total_scans']}")
        print(f"   - Average confidence: {overall_stats['avg_confidence']}%")
        print(f"   - Healthy leaves: {overall_stats['healthy_count']}")
        print(f"   - Diseased leaves: {overall_stats['diseased_count']}")
    
    print("\n✅ Test data added successfully!")
    print("🔍 Run 'python view_database.py' to see the updated database")

if __name__ == "__main__":
    add_test_data() 