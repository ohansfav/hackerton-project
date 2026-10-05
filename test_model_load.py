#!/usr/bin/env python
"""Test model loading directly"""
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print('=' * 60)
print('MODEL LOADING TEST')
print('=' * 60)

try:
    print('\n1. Importing predictor...')
    from src.predictor import MedicalDiagnosisPredictor
    print('   ✓ Predictor imported')
    
    print('\n2. Creating predictor instance...')
    predictor = MedicalDiagnosisPredictor()
    print('   ✓ Predictor instance created')
    
    print('\n3. Loading malaria model...')
    predictor.load_malaria_model('models/malaria_model.h5')
    print('   ✓ Malaria model loaded successfully')
    print(f'   Model type: {type(predictor.malaria_model)}')
    
    print('\n4. Loading TB model...')
    predictor.load_tb_model('models/tb_model.h5')
    print('   ✓ TB model loaded successfully')
    print(f'   Model type: {type(predictor.tb_model)}')
    
    print('\n' + '=' * 60)
    print('SUCCESS: Both models loaded!')
    print('=' * 60)
    
except Exception as e:
    import traceback
    print(f'\n✗ ERROR: {e}')
    print('\nFull traceback:')
    traceback.print_exc()
