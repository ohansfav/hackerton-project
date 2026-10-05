#!/usr/bin/env python
"""Test if app can start Waitress server"""
import os
import sys
import time

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

print("=" * 60)
print("Testing server startup...")
print("=" * 60)

try:
    print("\n1. Importing app...")
    from src.app import app
    print("   ✓ App imported")
    
    print("\n2. Importing Waitress...")
    from waitress import serve
    print("   ✓ Waitress imported")
    
    print("\n3. Starting server...")
    print("   NOTE: Server will block. Press CTRL+C to stop.")
    print("")
    serve(app, host='0.0.0.0', port=5000, threads=4, _quiet=False)
    
except KeyboardInterrupt:
    print("\n✓ Server stopped by user")
except Exception as e:
    import traceback
    print(f"\n✗ Error: {e}")
    traceback.print_exc()
