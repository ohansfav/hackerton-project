"""
Utility functions for the medical diagnosis system
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, List
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config.yaml') -> Dict:
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        logger.warning(f"Config file not found: {config_path}")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return {}


def save_config(config: Dict, config_path: str = 'config.yaml') -> None:
    """Save configuration to YAML file"""
    try:
        os.makedirs(os.path.dirname(config_path) or '.', exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")


def save_results(results: Dict, output_path: str) -> None:
    """Save results to JSON file"""
    try:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)
        logger.info(f"Results saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")


def load_results(input_path: str) -> Dict:
    """Load results from JSON file"""
    try:
        with open(input_path, 'r') as f:
            results = json.load(f)
        return results
    except Exception as e:
        logger.error(f"Error loading results: {str(e)}")
        return {}


def get_supported_image_formats() -> List[str]:
    """Get list of supported image formats"""
    return ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif']


def validate_image_format(file_path: str) -> bool:
    """Validate if file has supported image format"""
    ext = os.path.splitext(file_path)[1].lower().lstrip('.')
    return ext in get_supported_image_formats()


def format_results_for_display(result: Dict) -> str:
    """Format prediction results for user display"""
    output = f"\n{'='*60}\n"
    output += f"Disease: {result.get('disease', 'Unknown')}\n"
    output += f"Prediction: {result.get('prediction', 'Unknown')}\n"
    output += f"Confidence: {result.get('confidence', 0):.2%}\n"
    output += f"\nProbabilities:\n"
    
    for class_name, prob in result.get('probabilities', {}).items():
        output += f"  {class_name}: {prob:.2%}\n"
    
    output += f"\nRecommendation:\n"
    output += f"{result.get('recommendation', 'N/A')}\n"
    output += f"{'='*60}\n"
    
    return output


def setup_logging(log_file: str = 'logs/app.log') -> None:
    """Setup logging configuration"""
    os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Logging initialized")
