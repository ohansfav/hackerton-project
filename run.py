#!/usr/bin/env python
"""
Run the Flask Medical Diagnosis application
This script starts the Flask development server
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Flask environment variables
os.environ['FLASK_APP'] = 'src.app'
os.environ['FLASK_ENV'] = 'development'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Suppress TensorFlow warnings

# Import and run the app
from src.app import app, logger

if __name__ == '__main__':
    logger.info("Starting Medical Diagnosis System...")
    logger.info("Flask app is running at http://localhost:5000")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )
