#!/usr/bin/env python
"""
Medical Diagnosis Server - Simplified for Windows
Uses Waitress WSGI server for reliable operation
"""
import os
import sys
from pathlib import Path

# Set environment
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Use CPU only
os.environ['FLASK_ENV'] = 'production'

# Add to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == '__main__':
    # Import app after environment setup
    from src.app import app
    
    print("=" * 70)
    print("MEDICAL DIAGNOSIS SYSTEM WITH BWWO FEATURE SELECTION")
    print("=" * 70)
    print("")
    print("🌐 Web Interface: http://localhost:5000")
    print("")
    print("📊 API Endpoints:")
    print("   • GET   http://localhost:5000/                  (Web interface)")
    print("   • POST  http://localhost:5000/api/diagnose      (Make diagnosis)")
    print("   • GET   http://localhost:5000/api/status        (System status)")
    print("   • POST  http://localhost:5000/api/bwwo/optimize (Feature selection)")
    print("   • GET   http://localhost:5000/api/bwwo/info     (Algorithm info)")
    print("")
    print("⏹️  Press CTRL+C to stop the server")
    print("=" * 70)
    print("")
    
    # Try Flask with threaded mode first
    try:
        print("⚙️  Starting Flask server...")
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True, use_reloader=False)
    except Exception as e:
        print(f"Flask failed: {e}")
        print("Falling back to Waitress...")
        try:
            from waitress import serve
            serve(app, host='127.0.0.1', port=5000, threads=4)
        except Exception as e2:
            print(f"Waitress failed: {e2}")
            sys.exit(1)
