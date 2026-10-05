#!/usr/bin/env python
"""
Simple Flask test server
"""
import os
import sys
from pathlib import Path

# Set environment
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['FLASK_ENV'] = 'development'

# Add to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Flask app
from src.app import app

if __name__ == '__main__':
    print("=" * 60)
    print("Medical Diagnosis System - Flask Server")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("Press CTRL+C to stop")
    print("=" * 60)
    
    # Run the app
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )
