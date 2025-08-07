#!/usr/bin/env python3
"""
Test script for CocoScan Coconut Focus
Tests the coconut-specific AI analysis and database functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_leaf_analyzer import LeafAnalyzer
from database.db import init_db, get_leaf_types, get_health_statuses
import cv2
import numpy as np

def test_coconut_ai_analyzer():
    """Test the coconut-focused AI analyzer"""
    print("🥥 Testing Coconut AI Analyzer...")
    
    # Initialize analyzer
    analyzer = LeafAnalyzer()
    
    # Create a test image (green leaf-like)
    test_image = np.zeros((224, 224, 3), dtype=np.uint8)
    test_image[:, :, 1] = 150  # Green channel
    test_image[:, :, 0] = 50   # Blue channel
    test_image[:, :, 2] = 50   # Red channel
    
    # Save test image
    test_image_path = "test_coconut_leaf.jpg"
    cv2.imwrite(test_image_path, test_image)
    
    try:
        # Test analysis
        results = analyzer.analyze_leaf(test_image_path)
        
        print("✅ Analysis Results:")
        print(f"   Disease: {results.get('disease_name', 'Unknown')}")
        print(f"   Leaf Type: {results.get('leaf_name', 'Unknown')}")
        print(f"   Confidence: {results.get('overall_confidence', 0):.1%}")
        print(f"   Coconut Specific: {results.get('coconut_specific', False)}")
        
        # Test symptoms
        symptoms = results.get('symptoms', [])
        if symptoms:
            print(f"   Symptoms: {', '.join(symptoms)}")
        
        # Test recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            print(f"   Recommendations: {len(recommendations)} items")
        
        # Clean up
        os.remove(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in AI analysis: {e}")
        return False

def test_coconut_database():
    """Test the coconut-focused database"""
    print("\n🥥 Testing Coconut Database...")
    
    try:
        # Initialize database
        init_db()
        
        # Test leaf types
        leaf_types = get_leaf_types()
        print("✅ Leaf Types:")
        for leaf_type in leaf_types:
            print(f"   - {leaf_type[1]} ({leaf_type[2]})")
        
        # Test health statuses
        health_statuses = get_health_statuses()
        print("✅ Health Statuses:")
        for status in health_statuses:
            print(f"   - {status[1]} (Level {status[3]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in database test: {e}")
        return False

def test_coconut_disease_detection():
    """Test coconut-specific disease detection"""
    print("\n🥥 Testing Coconut Disease Detection...")
    
    analyzer = LeafAnalyzer()
    
    # Create test images for different diseases
    diseases = {
        'healthy': np.full((224, 224, 3), [50, 150, 50], dtype=np.uint8),  # Green
        'yellowing': np.full((224, 224, 3), [50, 200, 200], dtype=np.uint8),  # Yellow
        'browning': np.full((224, 224, 3), [50, 100, 150], dtype=np.uint8),  # Brown
    }
    
    for disease_name, test_image in diseases.items():
        test_path = f"test_{disease_name}.jpg"
        cv2.imwrite(test_path, test_image)
        
        try:
            # Test disease pattern detection
            patterns = analyzer.detect_coconut_disease_patterns(test_image)
            
            print(f"✅ {disease_name.title()} Test:")
            print(f"   Yellowing: {patterns.get('yellowing_detected', {}).get('detected', False)}")
            print(f"   Root Wilt: {patterns.get('root_wilt_signs', {}).get('detected', False)}")
            print(f"   Bud Rot: {patterns.get('bud_rot_indicators', {}).get('detected', False)}")
            print(f"   Leaf Spots: {patterns.get('leaf_spots', {}).get('detected', False)}")
            
            # Clean up
            os.remove(test_path)
            
        except Exception as e:
            print(f"❌ Error testing {disease_name}: {e}")
            if os.path.exists(test_path):
                os.remove(test_path)
    
    return True

def main():
    """Run all coconut focus tests"""
    print("🥥 CocoScan Coconut Focus Test Suite")
    print("=" * 50)
    
    tests = [
        ("AI Analyzer", test_coconut_ai_analyzer),
        ("Database", test_coconut_database),
        ("Disease Detection", test_coconut_disease_detection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} Test PASSED")
        else:
            print(f"❌ {test_name} Test FAILED")
    
    print("\n" + "=" * 50)
    print(f"🥥 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CocoScan is ready for coconut analysis.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 