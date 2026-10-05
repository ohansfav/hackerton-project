#!/usr/bin/env python
"""Diagnostic script to analyze malaria model predictions"""
import os
import sys
sys.path.insert(0, '.')

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = ''

from src.predictor import MedicalDiagnosisPredictor
from src.image_processor import ImageProcessor
import numpy as np
from pathlib import Path

# Initialize
predictor = MedicalDiagnosisPredictor()
predictor.load_malaria_model('models/malaria_model.h5')

# Find malaria test images
uploads_dir = Path('uploads')
malaria_images = sorted(uploads_dir.glob('malaria_*.png'))

print("=" * 80)
print("MALARIA MODEL PREDICTION ANALYSIS")
print("=" * 80)
print(f"\nFound {len(malaria_images)} malaria images\n")

if malaria_images:
    for img_path in malaria_images[:5]:  # Test first 5
        try:
            result = predictor.diagnose_malaria(str(img_path))
            print(f"Image: {img_path.name}")
            print(f"  Prediction: {result['prediction']}")
            print(f"  Confidence: {result['confidence']:.4f}")
            print(f"  Probabilities:")
            for class_name, prob in result['probabilities'].items():
                print(f"    - {class_name}: {prob:.4f}")
            print()
        except Exception as e:
            print(f"  ERROR: {e}\n")
else:
    print("No malaria images found in uploads/")

# Check model info
print("=" * 80)
print("MODEL INFORMATION")
print("=" * 80)
print(f"Model architecture: {predictor.malaria_model.summary()}")
