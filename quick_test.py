#!/usr/bin/env python
"""Quick test of diagnosis endpoint"""
import requests
import time

time.sleep(1)

print("Testing /api/status...")
r = requests.get('http://localhost:5000/api/status')
status = r.json()
print(f"✓ Status: {r.status_code}")
print(f"  Models loaded: {status['models_loaded']}")

print("\nTesting /api/diagnose with malaria image...")
with open('uploads/malaria_1763701024.085242_May_22_2025_03_29_17_PM.png', 'rb') as f:
    files = {'file': f}
    data = {'disease_type': 'malaria'}
    r = requests.post('http://localhost:5000/api/diagnose', files=files, data=data)

if r.status_code == 200:
    result = r.json()
    print(f"✓ Status: {r.status_code}")
    print(f"  Prediction: {result.get('prediction')}")
    print(f"  Confidence: {result.get('confidence', 'N/A')}")
else:
    print(f"✗ Error {r.status_code}: {r.json()}")
