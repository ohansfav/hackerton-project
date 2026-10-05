"""
Image Processor Module
Handles image preprocessing, enhancement, and normalization for medical image analysis
"""

import cv2
import numpy as np
from PIL import Image
import os
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Image preprocessing and enhancement for medical images
    """
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
        
    def load_image(self, image_path: str, color_mode: str = 'rgb') -> np.ndarray:
        """Load image from file path"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
            
        if color_mode == 'grayscale':
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        else:
            image = cv2.imread(image_path, cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
            
        return image
    
    def resize_image(self, image: np.ndarray, 
                     target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """Resize image to target size"""
        if target_size is None:
            target_size = self.target_size
            
        return cv2.resize(image, (target_size[1], target_size[0]))
    
    def normalize_image(self, image: np.ndarray, 
                       method: str = 'minmax') -> np.ndarray:
        """Normalize image to [0, 1] range"""
        if method == 'minmax':
            return image.astype(np.float32) / 255.0
        elif method == 'zscore':
            mean = np.mean(image)
            std = np.std(image)
            return (image.astype(np.float32) - mean) / (std + 1e-7)
        else:
            raise ValueError(f"Unknown normalization method: {method}")
    
    def apply_clahe(self, image: np.ndarray, clip_limit: float = 2.0, 
                    tile_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
        """Apply Contrast Limited Adaptive Histogram Equalization"""
        if len(image.shape) == 3:
            lab = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
            l = clahe.apply(l)
            
            lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            return enhanced.astype(np.float32) / 255.0
        else:
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
            enhanced = clahe.apply((image * 255).astype(np.uint8))
            return enhanced.astype(np.float32) / 255.0
    
    def apply_gaussian_blur(self, image: np.ndarray, 
                           kernel_size: int = 5) -> np.ndarray:
        """Apply Gaussian blur for noise reduction"""
        if kernel_size % 2 == 0:
            kernel_size += 1
            
        blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        return blurred
    
    def preprocess_malaria_image(self, image_path: str) -> np.ndarray:
        """Preprocess blood slide image for malaria detection"""
        image = self.load_image(image_path, color_mode='rgb')
        image = self.resize_image(image, self.target_size)
        image = self.apply_clahe(image, clip_limit=2.0)
        image = self.normalize_image(image)
        return image
    
    def preprocess_tb_image(self, image_path: str) -> np.ndarray:
        """Preprocess chest X-ray image for TB detection"""
        image = self.load_image(image_path, color_mode='grayscale')
        image = self.resize_image(image, self.target_size)
        
        # Convert grayscale to 3-channel (RGB equivalent)
        if len(image.shape) == 2:
            image = np.repeat(np.expand_dims(image, axis=-1), 3, axis=-1)
        
        image = self.apply_clahe(image, clip_limit=3.0)
        image = self.apply_gaussian_blur(image, kernel_size=5)
        image = self.normalize_image(image)
        
        return image
    
    def preprocess_batch(self, image_paths: list, 
                        disease_type: str = 'malaria') -> np.ndarray:
        """Preprocess a batch of images"""
        preprocessor = self.preprocess_malaria_image if disease_type == 'malaria' \
                       else self.preprocess_tb_image
        
        batch = []
        for path in image_paths:
            try:
                img = preprocessor(path)
                batch.append(img)
            except Exception as e:
                logger.error(f"Error processing {path}: {str(e)}")
                continue
        
        return np.array(batch)
    
    @staticmethod
    def validate_image(image_path: str) -> bool:
        """Validate if image file is valid"""
        try:
            if not os.path.exists(image_path):
                return False
            
            img = Image.open(image_path)
            img.verify()
            return True
        except Exception as e:
            logger.error(f"Image validation failed: {str(e)}")
            return False
