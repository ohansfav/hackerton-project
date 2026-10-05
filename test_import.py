#!/usr/bin/env python
"""Test if app imports without crashing"""
import os
import sys

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("Attempting to import app...")
try:
    from src.app import app
    print("✓ App imported successfully")
    print(f"✓ App has {len(app.url_map)} routes")
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            print(f"  - {rule.rule} [{','.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
except Exception as e:
    import traceback
    print(f"✗ Error importing app: {e}")
    traceback.print_exc()
