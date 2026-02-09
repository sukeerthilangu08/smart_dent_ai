#!/usr/bin/env python3
"""
Test script to verify the dental analysis system works correctly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from model import DentalAIModel
from PIL import Image
import json

def test_analysis():
    print("=" * 60)
    print("Testing Smart Dent AI Analysis System")
    print("=" * 60)
    
    # Initialize model
    print("\n1. Initializing model...")
    model = DentalAIModel()
    print(f"   ✓ Model loaded: {model.is_model_loaded()}")
    
    # Test with a white image (simulating teeth)
    print("\n2. Creating test image (white - simulating clean teeth)...")
    test_img = Image.new('RGB', (480, 480), color=(240, 240, 240))
    
    # Perform analysis
    print("\n3. Running analysis...")
    result = model.analyze_dental_image(test_img)
    
    # Display results
    print("\n4. Analysis Results:")
    print("-" * 60)
    print(f"   Teeth Detected: {result['teeth_detected']}")
    print(f"   Overall Score: {result['overall_assessment']['overall_score']:.2%}")
    print(f"   Grade: {result['overall_assessment']['grade']}")
    
    print("\n   Yellowness Analysis:")
    yellow = result['yellowness_analysis']
    print(f"   - Score: {yellow['yellowness_score']:.3f}")
    print(f"   - Severity: {yellow['severity']}")
    print(f"   - Whiteness: {yellow['whiteness_level']:.3f}")
    
    print("\n   Dental Flaws Analysis:")
    flaws = result['flaws_analysis']
    print(f"   - Score: {flaws['flaw_score']:.3f}")
    print(f"   - Severity: {flaws['severity']}")
    print(f"   - Issues: {len(flaws['issues_detected'])}")
    
    print("\n   Recommendations:")
    for i, rec in enumerate(result['summary']['recommendations'][:3], 1):
        print(f"   {i}. {rec}")
    
    print("\n" + "=" * 60)
    print("✓ Test completed successfully!")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    try:
        result = test_analysis()
        print("\n✓ All systems operational!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
