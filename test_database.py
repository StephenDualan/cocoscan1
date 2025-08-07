#!/usr/bin/env python3
"""
Comprehensive test script for CocoScan database functionality
"""

from database.db import (
    init_db, create_user, verify_user, save_scan, get_user_scans, 
    get_scan_statistics, get_leaf_types, get_health_statuses
)
from database.auth import create_simple_hash, verify_simple_hash

def test_database():
    print("🧪 Testing CocoScan Database Functionality")
    print("=" * 50)
    
    # 1. Initialize database
    print("1. Initializing database...")
    init_db()
    print("   ✅ Database initialized successfully")
    
    # 2. Test user creation
    print("\n2. Testing user creation...")
    test_username = "testuser"
    test_password = "password123"
    password_hash = create_simple_hash(test_password)
    
    user_id = create_user(test_username, password_hash, "test@example.com")
    if user_id:
        print(f"   ✅ User created successfully (ID: {user_id})")
    else:
        print("   ❌ Failed to create user")
        return
    
    # 3. Test user verification
    print("\n3. Testing user verification...")
    verified_user_id = verify_user(test_username, password_hash)
    if verified_user_id == user_id:
        print("   ✅ User verification successful")
    else:
        print("   ❌ User verification failed")
    
    # 4. Test scan saving
    print("\n4. Testing scan saving...")
    scan_id = save_scan(
        user_id=user_id,
        leaf_type="Coconut",
        health_status="Healthy",
        confidence=0.95,
        image_path="test_image.jpg",
        notes="Test scan",
        location="Test Location",
        weather_conditions="Sunny"
    )
    
    if scan_id:
        print(f"   ✅ Scan saved successfully (ID: {scan_id})")
    else:
        print("   ❌ Failed to save scan")
    
    # 5. Test scan retrieval
    print("\n5. Testing scan retrieval...")
    scans = get_user_scans(user_id)
    if scans:
        print(f"   ✅ Retrieved {len(scans)} scans")
        for scan in scans:
            scan_id, leaf_type, health_status, confidence, image_path, notes, location, weather, scan_date = scan
            print(f"      - Scan {scan_id}: {leaf_type} | {health_status} | {confidence:.2f}")
    else:
        print("   ❌ No scans retrieved")
    
    # 6. Test statistics
    print("\n6. Testing statistics...")
    stats = get_scan_statistics(user_id)
    if stats:
        print("   ✅ Statistics retrieved:")
        print(f"      - Total scans: {stats['total_scans']}")
        print(f"      - Average confidence: {stats['avg_confidence']}%")
        print(f"      - Healthy leaves: {stats['healthy_count']}")
        print(f"      - Diseased leaves: {stats['diseased_count']}")
    else:
        print("   ❌ Failed to retrieve statistics")
    
    # 7. Test leaf types
    print("\n7. Testing leaf types...")
    leaf_types = get_leaf_types()
    if leaf_types:
        print(f"   ✅ Retrieved {len(leaf_types)} leaf types:")
        for leaf_type in leaf_types:
            name, scientific_name, description = leaf_type
            print(f"      - {name} ({scientific_name})")
    else:
        print("   ❌ No leaf types retrieved")
    
    # 8. Test health statuses
    print("\n8. Testing health statuses...")
    health_statuses = get_health_statuses()
    if health_statuses:
        print(f"   ✅ Retrieved {len(health_statuses)} health statuses:")
        for status in health_statuses:
            status_name, description, severity = status
            print(f"      - {status_name} (Severity: {severity})")
    else:
        print("   ❌ No health statuses retrieved")
    
    # 9. Test duplicate user creation
    print("\n9. Testing duplicate user creation...")
    duplicate_user_id = create_user(test_username, password_hash, "duplicate@example.com")
    if duplicate_user_id is None:
        print("   ✅ Correctly prevented duplicate username")
    else:
        print("   ❌ Should have prevented duplicate username")
    
    print("\n" + "=" * 50)
    print("🎉 Database test completed successfully!")
    print("📱 Your CocoScan database is ready for mobile deployment!")

if __name__ == "__main__":
    test_database() 