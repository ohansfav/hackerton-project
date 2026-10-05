"""
Binary Water Wave Optimization (BWWO) Algorithm
Implementation for medical image feature selection and model optimization
References: Zheng et al., 2016 - "A Novel Water Wave Optimization Algorithm"
Adapted for binary optimization in healthcare ML applications
"""

import numpy as np
import logging
from typing import Callable, Tuple, Dict, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class BWWOConfig:
    """Configuration for Binary Water Wave Optimization"""
    population_size: int = 30  # Number of water particles (solutions)
    n_iterations: int = 50     # Number of iterations
    wavelength_min: float = 0.1
    wavelength_max: float = 2.0
    amplitude_min: float = 0.1
    amplitude_max: float = 2.0
    initial_frequency: float = 0.5
    reduction_factor: float = 0.99
    refraction_intensity: float = 0.1
    reflection_intensity: float = 0.1
    seed: int = None


class BinaryWaterWaveOptimizer:
    """
    Binary Water Wave Optimization Algorithm
    
    Mimics physical water wave propagation for optimization:
    - Propagation: Waves move through space
    - Refraction: Waves bend when encountering shallow water (local optima)
    - Breaking: Waves break and create turbulence (exploration)
    - Reflection: Waves reflect from boundaries (solution constraints)
    
    Perfect for feature selection and hyperparameter tuning!
    """
    
    def __init__(self, objective_fn: Callable, dimensions: int, config: BWWOConfig = None):
        """
        Initialize BWWO optimizer
        
        Args:
            objective_fn: Function to minimize/maximize
            dimensions: Number of decision variables (features)
            config: BWWOConfig object with algorithm parameters
        """
        self.objective_fn = objective_fn
        self.dimensions = dimensions
        self.config = config or BWWOConfig()
        
        if self.config.seed is not None:
            np.random.seed(self.config.seed)
        
        self.population = None
        self.fitness_values = None
        self.best_solution = None
        self.best_fitness = None
        self.fitness_history = []
        self.iteration_log = []
        
        logger.info(f"BWWO Optimizer initialized for {dimensions}-dimensional problem")
        logger.info(f"Population: {self.config.population_size}, Iterations: {self.config.n_iterations}")
    
    def _initialize_population(self) -> np.ndarray:
        """Initialize binary population (0s and 1s)"""
        # For binary problems, randomly initialize with 0s and 1s
        population = np.random.randint(0, 2, size=(self.config.population_size, self.dimensions))
        return population
    
    def _evaluate_fitness(self, population: np.ndarray) -> np.ndarray:
        """Evaluate fitness for entire population"""
        fitness = np.zeros(self.config.population_size)
        for i in range(self.config.population_size):
            try:
                fitness[i] = self.objective_fn(population[i])
            except Exception as e:
                logger.warning(f"Error evaluating fitness for particle {i}: {str(e)}")
                fitness[i] = float('inf')
        return fitness
    
    def _propagation(self, iteration: int) -> None:
        """
        Wave Propagation Phase
        Waves move towards the best solution found so far
        """
        # Decrease wavelength over iterations (exploitation over exploration)
        wavelength = self.config.wavelength_max - (
            (self.config.wavelength_max - self.config.wavelength_min) * 
            (iteration / self.config.n_iterations)
        )
        
        # Find best solution
        best_idx = np.argmin(self.fitness_values)
        best_particle = self.population[best_idx]
        
        # Update each particle
        for i in range(self.config.population_size):
            if i != best_idx:
                # Calculate distance to best solution
                distance = np.sum(np.abs(self.population[i] - best_particle))
                
                # For binary space, use probability-based updates
                # Particles closer to best solution update more conservatively
                if distance > 0:
                    # Move towards best solution with probability
                    update_prob = 1.0 / (1.0 + np.exp(distance / (wavelength + 1e-6)))
                    
                    for d in range(self.dimensions):
                        if np.random.random() < update_prob:
                            self.population[i, d] = best_particle[d]
    
    def _refraction(self, iteration: int) -> None:
        """
        Wave Refraction Phase
        Particles refract when they encounter shallower areas (local optima)
        Helps escape local optima
        """
        amplitude = self.config.amplitude_max * (self.config.reduction_factor ** iteration)
        
        for i in range(self.config.population_size):
            # Evaluate if current solution is in a "shallow" area (local optimum)
            # by checking if fitness improvements are stalling
            
            if len(self.fitness_history) > 5:
                recent_improvement = self.fitness_history[-1] - self.fitness_history[-5]
                
                # If improvement is small, apply refraction
                if abs(recent_improvement) < (self.config.refraction_intensity * 
                                             abs(self.fitness_history[-5])):
                    # Perform random bit flips (refraction)
                    num_flips = max(1, int(amplitude * self.dimensions))
                    flip_indices = np.random.choice(
                        self.dimensions, 
                        size=min(num_flips, self.dimensions), 
                        replace=False
                    )
                    self.population[i, flip_indices] = 1 - self.population[i, flip_indices]
    
    def _breaking(self) -> None:
        """
        Wave Breaking Phase
        Creates turbulent particles to enhance exploration
        Prevents premature convergence
        """
        # Create 1-2 new particles with random features
        num_breaking_waves = max(1, int(0.1 * self.config.population_size))
        
        for _ in range(num_breaking_waves):
            random_idx = np.random.randint(0, self.config.population_size)
            # Break wave by creating random perturbation
            new_solution = np.random.randint(0, 2, size=self.dimensions)
            
            # Evaluate and replace if better
            new_fitness = self.objective_fn(new_solution)
            if new_fitness < self.fitness_values[random_idx]:
                self.population[random_idx] = new_solution
                self.fitness_values[random_idx] = new_fitness
    
    def _reflection(self) -> None:
        """
        Wave Reflection Phase
        Reflects particles that violate constraints
        Ensures solutions stay within valid bounds
        """
        # For binary solutions, reflection means ensuring valid bit patterns
        # This can enforce domain-specific constraints
        
        for i in range(self.config.population_size):
            # Ensure at least one feature is selected (reflection constraint)
            if np.sum(self.population[i]) == 0:
                # If all zeros, randomly set one to 1
                random_idx = np.random.randint(0, self.dimensions)
                self.population[i, random_idx] = 1
    
    def optimize(self) -> Tuple[np.ndarray, float, Dict]:
        """
        Main optimization loop
        
        Returns:
            best_solution: Binary vector of selected features
            best_fitness: Best fitness value achieved
            history: Dictionary containing optimization history
        """
        logger.info("=" * 60)
        logger.info("Starting Binary Water Wave Optimization")
        logger.info("=" * 60)
        
        # Initialize population
        self.population = self._initialize_population()
        self.fitness_values = self._evaluate_fitness(self.population)
        
        # Find initial best
        best_idx = np.argmin(self.fitness_values)
        self.best_solution = self.population[best_idx].copy()
        self.best_fitness = self.fitness_values[best_idx]
        
        logger.info(f"Initial best fitness: {self.best_fitness:.6f}")
        
        # Main iteration loop
        for iteration in range(self.config.n_iterations):
            # Water wave operations
            self._propagation(iteration)
            self._refraction(iteration)
            self._breaking()
            self._reflection()
            
            # Evaluate new population
            self.fitness_values = self._evaluate_fitness(self.population)
            
            # Update best solution
            current_best_idx = np.argmin(self.fitness_values)
            current_best_fitness = self.fitness_values[current_best_idx]
            
            if current_best_fitness < self.best_fitness:
                self.best_solution = self.population[current_best_idx].copy()
                self.best_fitness = current_best_fitness
                improvement = "↓ NEW BEST"
            else:
                improvement = ""
            
            self.fitness_history.append(self.best_fitness)
            
            # Log progress every 10 iterations
            if (iteration + 1) % 10 == 0 or iteration == 0:
                avg_fitness = np.mean(self.fitness_values)
                std_fitness = np.std(self.fitness_values)
                num_selected = int(np.sum(self.best_solution))
                
                log_msg = (f"Iteration {iteration+1:3d}/{self.config.n_iterations} | "
                          f"Best: {self.best_fitness:8.6f} | "
                          f"Avg: {avg_fitness:8.6f} ± {std_fitness:6.4f} | "
                          f"Selected Features: {num_selected} {improvement}")
                logger.info(log_msg)
                self.iteration_log.append(log_msg)
        
        logger.info("=" * 60)
        logger.info(f"Optimization Complete!")
        logger.info(f"Final Best Fitness: {self.best_fitness:.6f}")
        logger.info(f"Features Selected: {int(np.sum(self.best_solution))}/{self.dimensions}")
        logger.info("=" * 60)
        
        return self.best_solution, self.best_fitness, self._get_history()
    
    def _get_history(self) -> Dict:
        """Return optimization history and statistics"""
        return {
            'best_fitness': self.best_fitness,
            'best_solution': self.best_solution,
            'fitness_history': self.fitness_history,
            'initial_fitness': self.fitness_history[0] if self.fitness_history else None,
            'improvement': self.fitness_history[0] - self.best_fitness if self.fitness_history else 0,
            'num_features_selected': int(np.sum(self.best_solution)),
            'selected_indices': np.where(self.best_solution == 1)[0].tolist(),
            'iteration_log': self.iteration_log,
            'completion_time': datetime.now().isoformat()
        }
    
    def get_selected_features(self) -> np.ndarray:
        """Get indices of selected features"""
        if self.best_solution is None:
            return np.array([])
        return np.where(self.best_solution == 1)[0]
    
    def print_summary(self) -> str:
        """Print and return optimization summary"""
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║     BINARY WATER WAVE OPTIMIZATION - RESULTS SUMMARY          ║
╚══════════════════════════════════════════════════════════════╝

📊 OPTIMIZATION METRICS:
  • Best Fitness Value: {self.best_fitness:.6f}
  • Initial Fitness: {self.fitness_history[0]:.6f}
  • Total Improvement: {self.fitness_history[0] - self.best_fitness:.6f}
  • Iterations Completed: {len(self.fitness_history)}
  
🧬 FEATURE SELECTION:
  • Total Features: {self.dimensions}
  • Selected Features: {int(np.sum(self.best_solution))}
  • Selection Rate: {100 * np.sum(self.best_solution) / self.dimensions:.1f}%
  • Selected Indices: {self.get_selected_features().tolist()}

⚙️ ALGORITHM PARAMETERS:
  • Population Size: {self.config.population_size}
  • Iterations: {self.config.n_iterations}
  • Wavelength Range: [{self.config.wavelength_min}, {self.config.wavelength_max}]
  • Amplitude Range: [{self.config.amplitude_min}, {self.config.amplitude_max}]

🌊 WATER WAVE DYNAMICS:
  • Propagation: Guides particles towards global optimum
  • Refraction: Escapes local optima when stagnating
  • Breaking: Creates new solutions for exploration
  • Reflection: Maintains constraint satisfaction
  
════════════════════════════════════════════════════════════════
"""
        logger.info(summary)
        return summary
