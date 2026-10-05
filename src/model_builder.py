"""
Model Builder Module
Constructs neural network architectures for medical image diagnosis
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import ResNet50, MobileNetV2, InceptionV3
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import logging
from typing import Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomCNNModel:
    """Custom Convolutional Neural Network for medical image classification"""
    
    @staticmethod
    def build(input_shape: Tuple[int, int, int] = (224, 224, 3), 
              num_classes: int = 2) -> keras.Model:
        """Build custom CNN model"""
        model = models.Sequential([
            # Block 1
            layers.Conv2D(32, (3, 3), activation='relu', padding='same', 
                         input_shape=input_shape),
            layers.BatchNormalization(),
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Block 2
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Block 3
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Block 4
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Global Average Pooling
            layers.GlobalAveragePooling2D(),
            
            # Fully Connected Layers
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            # Output Layer
            layers.Dense(num_classes, activation='softmax')
        ])
        
        return model


class TransferLearningModel:
    """Transfer learning models using pretrained architectures"""
    
    @staticmethod
    def build_resnet50(input_shape: Tuple[int, int, int] = (224, 224, 3),
                       num_classes: int = 2) -> keras.Model:
        """Build ResNet50 transfer learning model"""
        base_model = ResNet50(weights='imagenet', input_shape=input_shape,
                             include_top=False)
        
        for layer in base_model.layers[:-50]:
            layer.trainable = False
        
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        return model
    
    @staticmethod
    def build_mobilenetv2(input_shape: Tuple[int, int, int] = (224, 224, 3),
                         num_classes: int = 2) -> keras.Model:
        """Build MobileNetV2 transfer learning model"""
        base_model = MobileNetV2(weights='imagenet', input_shape=input_shape,
                                include_top=False)
        
        base_model.trainable = False
        
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        return model
    
    @staticmethod
    def build_inceptionv3(input_shape: Tuple[int, int, int] = (224, 224, 3),
                         num_classes: int = 2) -> keras.Model:
        """Build InceptionV3 transfer learning model"""
        base_model = InceptionV3(weights='imagenet', input_shape=input_shape,
                                include_top=False)
        
        base_model.trainable = False
        
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        return model


class ModelFactory:
    """Factory class to create models based on configuration"""
    
    @staticmethod
    def create_model(architecture: str = 'custom_cnn',
                    input_shape: Tuple[int, int, int] = (224, 224, 3),
                    num_classes: int = 2) -> keras.Model:
        """Create model based on architecture name"""
        if architecture == 'custom_cnn':
            return CustomCNNModel.build(input_shape, num_classes)
        elif architecture == 'resnet50':
            return TransferLearningModel.build_resnet50(input_shape, num_classes)
        elif architecture == 'mobilenetv2':
            return TransferLearningModel.build_mobilenetv2(input_shape, num_classes)
        elif architecture == 'inception':
            return TransferLearningModel.build_inceptionv3(input_shape, num_classes)
        else:
            logger.warning(f"Unknown architecture {architecture}, using custom_cnn")
            return CustomCNNModel.build(input_shape, num_classes)
    
    @staticmethod
    def compile_model(model: keras.Model,
                     learning_rate: float = 0.001,
                     loss_function: str = 'categorical_crossentropy') -> keras.Model:
        """Compile model with optimizer and loss"""
        optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        
        model.compile(
            optimizer=optimizer,
            loss=loss_function,
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        return model


class DataAugmentation:
    """Data augmentation utilities for training"""
    
    @staticmethod
    def get_augmentation_generator(rotation_range: float = 20,
                                   width_shift_range: float = 0.2,
                                   height_shift_range: float = 0.2,
                                   horizontal_flip: bool = True,
                                   zoom_range: float = 0.2) -> ImageDataGenerator:
        """Create data augmentation generator"""
        return ImageDataGenerator(
            rotation_range=rotation_range,
            width_shift_range=width_shift_range,
            height_shift_range=height_shift_range,
            horizontal_flip=horizontal_flip,
            zoom_range=zoom_range,
            fill_mode='nearest'
        )
    
    @staticmethod
    def get_preprocessing_generator() -> ImageDataGenerator:
        """Create preprocessing-only generator for validation/test"""
        return ImageDataGenerator(rescale=1.0/255.0)


def create_callbacks(model_name: str, patience: int = 15) -> list:
    """Create training callbacks"""
    return [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=patience,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7
        ),
        keras.callbacks.ModelCheckpoint(
            f'models/{model_name}_best.h5',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max'
        ),
        keras.callbacks.TensorBoard(
            log_dir=f'logs/{model_name}'
        )
    ]
