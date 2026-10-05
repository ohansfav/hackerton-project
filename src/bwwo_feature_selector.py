"""
BWWO-based Feature Selector for Medical Diagnosis
Uses Binary Water Wave Optimization to select optimal features from medical images
"""

import numpy as np
import logging
from typing import Callable, Tuple, Dict, List
import cv2
from src.bwwo import BinaryWaterWaveOptimizer, BWWOConfig

logger = logging.getLogger(__name__)


class ImageFeatureExtractor:
    """Extract features from medical images for BWWO optimization"""
    
    @staticmethod
    def extract_color_features(image: np.ndarray) -> np.ndarray:
        """Extract color-based features"""
        features = []
        
        # Convert to different color spaces
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Mean and std of each channel
            for c in range(3):
                features.append(np.mean(image[:, :, c]))
                features.append(np.std(image[:, :, c]))
        
        # Histogram features
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        features.extend([np.mean(hist), np.std(hist), np.max(hist)])
        
        return np.array(features)
    
    @staticmethod
    def extract_texture_features(image: np.ndarray) -> np.ndarray:
        """Extract texture-based features using Gabor filters"""
        features = []
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Gabor filter bank
        kernels = []
        for theta in [0, np.pi/4, np.pi/2, 3*np.pi/4]:
            for lambda_val in [3, 5, 7]:
                kernel = cv2.getGaborKernel((21, 21), 3, theta, lambda_val, 0.5, 0)
                kernels.append(kernel)
        
        # Apply filters and extract statistics
        for kernel in kernels[:8]:  # Use first 8 for efficiency
            filtered = cv2.filter2D(gray, cv2.CV_32F, kernel)
            features.append(np.mean(filtered))
            features.append(np.std(filtered))
        
        return np.array(features)
    
    @staticmethod
    def extract_edge_features(image: np.ndarray) -> np.ndarray:
        """Extract edge-based features using Canny edge detection"""
        features = []
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        features.append(np.sum(edges) / 255)  # Edge density
        features.append(np.mean(gray[edges == 255]) if np.sum(edges) > 0 else 0)  # Mean edge intensity
        
        # Hough line detection
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=10, maxLineGap=10)
        features.append(len(lines) if lines is not None else 0)  # Number of lines
        
        return np.array(features)
    
    @staticmethod
    def extract_shape_features(image: np.ndarray) -> np.ndarray:
        """Extract shape-based features using contours"""
        features = []
        
        # Convert to grayscale and binary
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            # Contour count
            features.append(len(contours))
            
            # Largest contour area
            areas = [cv2.contourArea(c) for c in contours]
            features.append(max(areas))
            features.append(np.mean(areas))
            
            # Circularity (4π * area / perimeter²)
            for contour in contours[:3]:  # First 3 contours
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter ** 2)
                    features.append(circularity)
        else:
            features.extend([0] * 6)
        
        return np.array(features)
    
    @staticmethod
    def extract_all_features(image: np.ndarray) -> Tuple[np.ndarray, List[str]]:
        """Extract all features and return feature names"""
        color_feat = ImageFeatureExtractor.extract_color_features(image)
        texture_feat = ImageFeatureExtractor.extract_texture_features(image)
        edge_feat = ImageFeatureExtractor.extract_edge_features(image)
        shape_feat = ImageFeatureExtractor.extract_shape_features(image)
        
        all_features = np.concatenate([color_feat, texture_feat, edge_feat, shape_feat])
        
        feature_names = (
            ['color_ch0_mean', 'color_ch0_std', 'color_ch1_mean', 'color_ch1_std', 
             'color_ch2_mean', 'color_ch2_std', 'hist_mean', 'hist_std', 'hist_max'] +
            [f'texture_gabor_{i}_mean' for i in range(8)] +
            [f'texture_gabor_{i}_std' for i in range(8)] +
            ['edge_density', 'edge_intensity', 'num_lines'] +
            ['contour_count', 'max_contour_area', 'mean_contour_area', 
             'circularity_1', 'circularity_2', 'circularity_3']
        )
        
        return all_features, feature_names


class BWWOFeatureSelector:
    """Feature selection using Binary Water Wave Optimization"""
    
    def __init__(self, image_samples: List[np.ndarray], labels: np.ndarray, config: BWWOConfig = None):
        """
        Initialize feature selector
        
        Args:
            image_samples: List of image arrays for feature extraction
            labels: Class labels for images (0 or 1)
            config: BWWO configuration
        """
        self.image_samples = image_samples
        self.labels = labels
        self.config = config or BWWOConfig(population_size=20, n_iterations=30)
        
        # Extract features from all images
        logger.info(f"Extracting features from {len(image_samples)} images...")
        self.feature_matrix = []
        self.feature_names = None
        
        for i, img in enumerate(image_samples):
            features, feature_names = ImageFeatureExtractor.extract_all_features(img)
            self.feature_matrix.append(features)
            if self.feature_names is None:
                self.feature_names = feature_names
            
            if (i + 1) % 5 == 0:
                logger.info(f"  Processed {i + 1}/{len(image_samples)} images")
        
        self.feature_matrix = np.array(self.feature_matrix)
        self.n_features = self.feature_matrix.shape[1]
        logger.info(f"Total features extracted: {self.n_features}")
    
    def _objective_function(self, feature_mask: np.ndarray) -> float:
        """
        Objective function for BWWO
        Minimize: (1 - classification_accuracy) + 0.1 * (n_selected_features / total_features)
        """
        # At least one feature must be selected
        if np.sum(feature_mask) == 0:
            return float('inf')
        
        # Select features
        selected_features = self.feature_matrix[:, feature_mask == 1]
        n_selected = np.sum(feature_mask)
        
        try:
            # Simple classification accuracy using distance
            # For each sample, find nearest neighbor in opposite class
            correct = 0
            for i in range(len(self.labels)):
                distances = np.linalg.norm(selected_features[i] - selected_features, axis=1)
                # Find nearest sample with different label (excluding self)
                distances[i] = float('inf')
                nearest_idx = np.argmin(distances)
                
                if self.labels[i] != self.labels[nearest_idx]:
                    correct += 1
            
            accuracy = correct / len(self.labels)
            
            # Objective: maximize accuracy while minimizing features
            # (Lower is better)
            objective = (1 - accuracy) + 0.1 * (n_selected / self.n_features)
            
        except Exception as e:
            logger.warning(f"Error in objective function: {str(e)}")
            objective = 1.0
        
        return objective
    
    def optimize(self) -> Dict:
        """
        Run BWWO feature selection
        
        Returns:
            Dictionary with optimization results
        """
        logger.info("=" * 60)
        logger.info("Starting BWWO-based Feature Selection")
        logger.info("=" * 60)
        
        optimizer = BinaryWaterWaveOptimizer(
            objective_fn=self._objective_function,
            dimensions=self.n_features,
            config=self.config
        )
        
        best_mask, best_fitness, history = optimizer.optimize()
        
        # Get selected feature names
        selected_indices = np.where(best_mask == 1)[0]
        selected_names = [self.feature_names[i] for i in selected_indices]
        
        result = {
            'best_mask': best_mask,
            'best_fitness': best_fitness,
            'selected_features': selected_names,
            'selected_indices': selected_indices.tolist(),
            'n_selected': len(selected_names),
            'n_total': self.n_features,
            'selection_rate': len(selected_names) / self.n_features,
            'history': history,
            'feature_names': self.feature_names
        }
        
        self._print_results(result)
        
        return result
    
    def _print_results(self, result: Dict) -> str:
        """Print feature selection results"""
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║    BWWO FEATURE SELECTION RESULTS FOR MEDICAL DIAGNOSIS      ║
╚══════════════════════════════════════════════════════════════╝

📊 SELECTION STATISTICS:
  • Total Features Extracted: {result['n_total']}
  • Features Selected: {result['n_selected']}
  • Selection Rate: {100 * result['selection_rate']:.1f}%
  • Classification Fitness: {result['best_fitness']:.6f}

🎯 SELECTED FEATURES ({result['n_selected']} features):
"""
        for i, name in enumerate(result['selected_features'][:15], 1):
            summary += f"  {i:2d}. {name}\n"
        
        if result['n_selected'] > 15:
            summary += f"  ... and {result['n_selected'] - 15} more features\n"
        
        summary += f"""
📈 OPTIMIZATION HISTORY:
  • Initial Fitness: {result['history']['initial_fitness']:.6f}
  • Final Fitness: {result['history']['best_fitness']:.6f}
  • Total Improvement: {result['history']['improvement']:.6f}
  
💾 USAGE:
  To use selected features in your model:
  >>> from src.bwwo_feature_selector import BWWOFeatureSelector
  >>> selected_indices = {result['selected_indices'][:5]}{'...' if len(result['selected_indices']) > 5 else ''}
  >>> optimized_features = all_features[:, selected_indices]

════════════════════════════════════════════════════════════════
"""
        logger.info(summary)
        return summary
