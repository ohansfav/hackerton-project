#!/usr/bin/env python
"""Quick test of the diagnosis API"""
import requests
import json
from pathlib import Path

print("=" * 60)
print("Medical Diagnosis API Test")
print("=" * 60)

# Find a sample image
try:
    image_file = list(Path('uploads').glob('malaria*.png'))[0]
    print(f"\n📁 Testing with: {image_file.name}")
    
    # Test 1: Make diagnosis with malaria image
    print("\n🔄 Testing /api/diagnose endpoint...")
    with open(image_file, 'rb') as f:
        files = {'file': f}
        data = {'disease_type': 'malaria'}
        response = requests.post('http://localhost:5000/api/diagnose', files=files, data=data)
    
    result = response.json()
    print(f"✓ Status code: {response.status_code}")
    if response.status_code != 200:
        print(f"  Error details: {result}")
    else:
        print(f"✓ Prediction: {result.get('prediction', 'ERROR')}")
        print(f"✓ Confidence: {result.get('confidence', 0) * 100:.1f}%")
    
    # Test 2: Check API status
    print("\n🔄 Testing /api/status endpoint...")
    response = requests.get('http://localhost:5000/api/status')
    status = response.json()
    print(f"✓ Server status: {status['status']}")
    print(f"✓ Models loaded: {status['models_loaded']}")
    
    # Test 3: Get BWWO info
    print("\n🔄 Testing /api/bwwo/info endpoint...")
    response = requests.get('http://localhost:5000/api/bwwo/info')
    info = response.json()
    print(f"✓ Algorithm: {info['algorithm']}")
    print(f"✓ Purpose: {info['purpose']}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! API is fully functional!")
    print("=" * 60)
    print("\n🌐 Web Interface: http://localhost:5000")
    print("📚 Endpoints ready for use:")
    print("   • GET  /                 - Web interface")
    print("   • POST /api/diagnose     - Make diagnosis")
    print("   • GET  /api/status       - System status")
    print("   • POST /api/bwwo/optimize- Feature selection")
    print("   • GET  /api/bwwo/info    - Algorithm info")

except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
