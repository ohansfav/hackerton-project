"""
Flask Web Application for Medical Image Diagnosis
Malaria and TB Detection System
"""

import os
import sys

# Set TensorFlow env vars BEFORE importing anything else
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = ''

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
from werkzeug.utils import secure_filename
from pathlib import Path
import json
from datetime import datetime
import sys
import numpy as np
import cv2

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import utilities first (lightweight)
try:
    from src.utils import load_config, validate_image_format, format_results_for_display, setup_logging
except ImportError:
    from utils import load_config, validate_image_format, format_results_for_display, setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Flask app with templates folder at project root
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)
CORS(app)

# Disable caching for all responses
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'}

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('results', exist_ok=True)

# Load configuration
config = load_config('config.yaml')

# Initialize modules directly
logger.info("Initializing medical diagnosis system...")

try:
    from src.predictor import MedicalDiagnosisPredictor
except ImportError:
    from predictor import MedicalDiagnosisPredictor

try:
    from src.image_processor import ImageProcessor
except ImportError:
    from image_processor import ImageProcessor

# Create instances
predictor = MedicalDiagnosisPredictor(config)
image_processor = ImageProcessor()

# Load models immediately
models_loaded = {'malaria': False, 'tb': False}
malaria_path = 'models/malaria_model.h5'
tb_path = 'models/tb_model.h5'

logger.info("Loading Malaria model...")
if os.path.exists(malaria_path):
    try:
        predictor.load_malaria_model(malaria_path)
        models_loaded['malaria'] = True
        logger.info("✓ Malaria model loaded")
    except Exception as e:
        logger.error(f"✗ Failed to load Malaria model: {e}")
else:
    logger.warning(f"Malaria model not found: {malaria_path}")

logger.info("Loading TB model...")
if os.path.exists(tb_path):
    try:
        predictor.load_tb_model(tb_path)
        models_loaded['tb'] = True
        logger.info("✓ TB model loaded")
    except Exception as e:
        logger.error(f"✗ Failed to load TB model: {e}")
else:
    logger.warning(f"TB model not found: {tb_path}")

logger.info(f"System initialized. Models: {models_loaded}")


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page - serve the HTML frontend"""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def status():
    """Get system status and model information"""
    return jsonify({
        'status': 'running',
        'models': predictor.get_model_info() if predictor else {},
        'models_loaded': models_loaded,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Main diagnosis endpoint"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        if 'disease_type' not in request.form:
            return jsonify({'error': 'Disease type not specified'}), 400
        
        file = request.files['file']
        disease_type = request.form['disease_type'].lower()
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format'}), 400
        
        if disease_type not in ['malaria', 'tb']:
            return jsonify({'error': 'Invalid disease type'}), 400
        
        # Save file
        filename = secure_filename(f"{disease_type}_{datetime.now().timestamp()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {filepath}")
        
        # Make diagnosis
        if disease_type == 'malaria':
            if not models_loaded['malaria']:
                return jsonify({'error': 'Malaria model not loaded'}), 500
            result = predictor.diagnose_malaria(filepath)
        else:
            if not models_loaded['tb']:
                return jsonify({'error': 'TB model not loaded'}), 500
            result = predictor.diagnose_tb(filepath)
        
        result['timestamp'] = datetime.now().isoformat()
        result['filename'] = filename
        
        # Save result
        result_path = f"results/{disease_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('results', exist_ok=True)
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=4)
        
        logger.info(f"Diagnosis complete: {result['prediction']}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error during diagnosis: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/load_models', methods=['POST'])
def load_models():
    """Load pretrained models"""
    try:
        data = request.get_json()
        
        malaria_model_path = data.get('malaria_model_path', 'models/malaria_model.h5')
        tb_model_path = data.get('tb_model_path', 'models/tb_model.h5')
        
        if os.path.exists(malaria_model_path):
            predictor.load_malaria_model(malaria_model_path)
            models_loaded['malaria'] = True
            logger.info("Malaria model loaded successfully")
        
        if os.path.exists(tb_model_path):
            predictor.load_tb_model(tb_model_path)
            models_loaded['tb'] = True
            logger.info("TB model loaded successfully")
        
        return jsonify({
            'status': 'success',
            'models_loaded': models_loaded
        }), 200
    
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/model_info', methods=['GET'])
def model_info():
    """Get detailed model information"""
    return jsonify(predictor.get_model_info() if predictor else {}), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/api/bwwo/optimize', methods=['POST'])
def bwwo_optimize():
    """Run BWWO feature selection on uploaded images"""
    try:
        from src.bwwo_feature_selector import BWWOFeatureSelector, ImageFeatureExtractor
        from src.bwwo import BWWOConfig
        
        # Get uploaded files and labels
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        labels = request.form.get('labels', '')
        
        if not labels:
            return jsonify({'error': 'Labels required (comma-separated)'}), 400
        
        try:
            labels = np.array([int(x) for x in labels.split(',')])
        except:
            return jsonify({'error': 'Invalid label format'}), 400
        
        if len(files) != len(labels):
            return jsonify({'error': 'Number of files must match number of labels'}), 400
        
        logger.info(f"BWWO: Processing {len(files)} images for feature optimization...")
        
        # Load images
        images = []
        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"bwwo_{filename}")
            file.save(filepath)
            
            img = cv2.imread(filepath)
            if img is None:
                return jsonify({'error': f'Failed to load image: {filename}'}), 400
            
            img = cv2.resize(img, (224, 224))
            images.append(img)
        
        # Configure BWWO
        bwwo_config = BWWOConfig(
            population_size=int(request.form.get('population_size', 20)),
            n_iterations=int(request.form.get('n_iterations', 30)),
            seed=42
        )
        
        # Run feature selection
        selector = BWWOFeatureSelector(images, labels, bwwo_config)
        result = selector.optimize()
        
        logger.info(f"BWWO completed. Selected {result['n_selected']}/{result['n_total']} features")
        
        return jsonify({
            'status': 'success',
            'selected_features': result['selected_features'][:20],  # Top 20 for display
            'selected_indices': result['selected_indices'],
            'n_selected': result['n_selected'],
            'n_total': result['n_total'],
            'selection_rate': result['selection_rate'],
            'fitness': result['best_fitness'],
            'improvement': result['history']['improvement'],
            'message': f"Optimized from {result['n_total']} to {result['n_selected']} features"
        }), 200
    
    except Exception as e:
        logger.error(f"BWWO Error: {str(e)}")
        return jsonify({'error': f'BWWO optimization failed: {str(e)}'}), 500


@app.route('/api/bwwo/info', methods=['GET'])
def bwwo_info():
    """Get information about BWWO algorithm"""
    info = {
        'algorithm': 'Binary Water Wave Optimization (BWWO)',
        'purpose': 'Feature selection and hyperparameter optimization',
        'description': 'Mimics physical water wave propagation for binary optimization',
        'mechanics': {
            'propagation': 'Waves move towards best solution',
            'refraction': 'Escape local optima when stagnating',
            'breaking': 'Create new solutions for exploration',
            'reflection': 'Maintain constraint satisfaction'
        },
        'advantages': [
            'Efficient feature selection',
            'Balances exploration and exploitation',
            'No gradient requirement',
            'Good for discrete optimization problems'
        ],
        'use_cases': [
            'Medical image feature selection',
            'Hyperparameter tuning',
            'Feature subset selection',
            'Model optimization'
        ],
        'parameters': {
            'population_size': 'Number of water particles (solutions)',
            'n_iterations': 'Number of optimization iterations',
            'wavelength_min/max': 'Controls wave propagation',
            'amplitude_min/max': 'Controls perturbation magnitude'
        }
    }
    return jsonify(info), 200


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size: 10MB'}), 413


@app.route('/api/test-tb', methods=['GET'])
def test_tb_diagnosis():
    """Test TB diagnosis with h0186.png from Downloads"""
    try:
        test_image_path = r'C:\Users\ohanu\Downloads\h0186.png'
        
        # Check if file exists
        if not os.path.exists(test_image_path):
            return jsonify({
                'error': 'Test image not found',
                'expected_path': test_image_path
            }), 404
        
        logger.info(f"Testing TB diagnosis with: {test_image_path}")
        
        # Perform diagnosis
        result = predictor.diagnose_tb(test_image_path)
        result['test_mode'] = True
        result['test_image'] = test_image_path
        result['timestamp'] = datetime.now().isoformat()
        
        # Save test result
        result_path = f"results/test_tb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('results', exist_ok=True)
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=4)
        
        logger.info(f"Test TB diagnosis complete: {result['prediction']}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in test TB diagnosis: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("Starting Medical Diagnosis System...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )
