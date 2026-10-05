"""
Medical Diagnosis System Package
"""

__version__ = "1.0.0"
__author__ = "Healthcare AI Team"
__description__ = "AI-powered Malaria and TB diagnosis system"

# Lazy imports to avoid loading heavy dependencies on module import
def __getattr__(name):
    if name == 'ImageProcessor':
        from src.image_processor import ImageProcessor
        return ImageProcessor
    elif name == 'ModelFactory':
        from src.model_builder import ModelFactory
        return ModelFactory
    elif name == 'CustomCNNModel':
        from src.model_builder import CustomCNNModel
        return CustomCNNModel
    elif name == 'TransferLearningModel':
        from src.model_builder import TransferLearningModel
        return TransferLearningModel
    elif name == 'MedicalDiagnosisPredictor':
        from src.predictor import MedicalDiagnosisPredictor
        return MedicalDiagnosisPredictor
    elif name == 'MedicalImageTrainer':
        from src.trainer import MedicalImageTrainer
        return MedicalImageTrainer
    elif name == 'load_config' or name == 'save_config':
        from src import utils
        return getattr(utils, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'ImageProcessor',
    'ModelFactory',
    'CustomCNNModel',
    'TransferLearningModel',
    'MedicalDiagnosisPredictor',
    'MedicalImageTrainer',
    'load_config',
    'save_config',
]
