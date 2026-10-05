"""
Trainer Module
Training pipeline for medical image diagnosis models
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np
import os
import logging
from typing import Dict, Tuple, Optional
from pathlib import Path
from src.image_processor import ImageProcessor
from src.model_builder import ModelFactory, DataAugmentation, create_callbacks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalImageTrainer:
    """Trainer class for medical image diagnosis models"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize trainer"""
        self.config = config or {}
        self.image_processor = ImageProcessor()
        self.model = None
        self.history = None
        
    def load_data_from_directory(self, 
                                 train_dir: str,
                                 val_dir: str,
                                 test_dir: Optional[str] = None,
                                 batch_size: int = 32,
                                 target_size: Tuple[int, int] = (224, 224),
                                 disease_type: str = 'malaria') -> Tuple:
        """Load data from directory structure"""
        aug_gen = DataAugmentation.get_augmentation_generator()
        prep_gen = DataAugmentation.get_preprocessing_generator()
        
        train_generator = keras.preprocessing.image.ImageDataGenerator(
            **aug_gen.__dict__
        ).flow_from_directory(
            train_dir,
            target_size=target_size,
            batch_size=batch_size,
            class_mode='categorical'
        )
        
        val_generator = prep_gen.flow_from_directory(
            val_dir,
            target_size=target_size,
            batch_size=batch_size,
            class_mode='categorical'
        )
        
        test_generator = None
        if test_dir and os.path.exists(test_dir):
            test_generator = prep_gen.flow_from_directory(
                test_dir,
                target_size=target_size,
                batch_size=batch_size,
                class_mode='categorical',
                shuffle=False
            )
        
        logger.info(f"Training samples: {train_generator.samples}")
        logger.info(f"Validation samples: {val_generator.samples}")
        if test_generator:
            logger.info(f"Test samples: {test_generator.samples}")
        
        return train_generator, val_generator, test_generator
    
    def build_model(self, 
                   architecture: str = 'custom_cnn',
                   input_shape: Tuple[int, int, int] = (224, 224, 3),
                   num_classes: int = 2,
                   learning_rate: float = 0.001) -> keras.Model:
        """Build and compile model"""
        self.model = ModelFactory.create_model(
            architecture=architecture,
            input_shape=input_shape,
            num_classes=num_classes
        )
        
        self.model = ModelFactory.compile_model(
            self.model,
            learning_rate=learning_rate
        )
        
        logger.info(f"Model built with architecture: {architecture}")
        self.model.summary()
        
        return self.model
    
    def train(self,
             train_generator,
             val_generator,
             epochs: int = 100,
             steps_per_epoch: Optional[int] = None,
             validation_steps: Optional[int] = None,
             model_name: str = 'medical_model') -> Dict:
        """Train the model"""
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        os.makedirs('models', exist_ok=True)
        callbacks = create_callbacks(model_name, patience=15)
        
        logger.info("Starting training...")
        self.history = self.model.fit(
            train_generator,
            epochs=epochs,
            steps_per_epoch=steps_per_epoch,
            validation_data=val_generator,
            validation_steps=validation_steps,
            callbacks=callbacks,
            verbose=1
        )
        
        model_path = f'models/{model_name}_final.h5'
        self.model.save(model_path)
        logger.info(f"Model saved to {model_path}")
        
        return self.history
    
    def evaluate(self, test_generator) -> Dict:
        """Evaluate model on test data"""
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        logger.info("Evaluating model...")
        results = self.model.evaluate(test_generator, verbose=1)
        
        metrics = {
            'loss': results[0],
            'accuracy': results[1],
            'precision': results[2] if len(results) > 2 else None,
            'recall': results[3] if len(results) > 3 else None
        }
        
        logger.info(f"Test Accuracy: {metrics['accuracy']:.4f}")
        
        return metrics
    
    def save_model(self, path: str) -> None:
        """Save model to file"""
        if self.model is None:
            raise ValueError("Model not built")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str) -> keras.Model:
        """Load model from file"""
        self.model = keras.models.load_model(path)
        logger.info(f"Model loaded from {path}")
        return self.model


def train_malaria_model(train_dir: str,
                       val_dir: str,
                       test_dir: Optional[str] = None,
                       architecture: str = 'custom_cnn',
                       epochs: int = 100) -> Dict:
    """Train malaria detection model"""
    trainer = MedicalImageTrainer()
    
    train_gen, val_gen, test_gen = trainer.load_data_from_directory(
        train_dir, val_dir, test_dir, disease_type='malaria'
    )
    
    trainer.build_model(
        architecture=architecture,
        input_shape=(224, 224, 3),
        num_classes=2,
        learning_rate=0.001
    )
    
    history = trainer.train(
        train_gen, val_gen, epochs=epochs, model_name='malaria_model'
    )
    
    metrics = {}
    if test_gen:
        metrics = trainer.evaluate(test_gen)
    
    return {'history': history, 'metrics': metrics}


def train_tb_model(train_dir: str,
                   val_dir: str,
                   test_dir: Optional[str] = None,
                   architecture: str = 'custom_cnn',
                   epochs: int = 100) -> Dict:
    """Train TB detection model"""
    trainer = MedicalImageTrainer()
    
    train_gen, val_gen, test_gen = trainer.load_data_from_directory(
        train_dir, val_dir, test_dir, disease_type='tb'
    )
    
    trainer.build_model(
        architecture=architecture,
        input_shape=(224, 224, 3),
        num_classes=2,
        learning_rate=0.001
    )
    
    history = trainer.train(
        train_gen, val_gen, epochs=epochs, model_name='tb_model'
    )
    
    metrics = {}
    if test_gen:
        metrics = trainer.evaluate(test_gen)
    
    return {'history': history, 'metrics': metrics}
