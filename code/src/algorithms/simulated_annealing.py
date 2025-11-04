"""
Simulated Annealing Metaheuristic.

This strategy uses a probabilistic approach to escape local optima
by accepting worse solutions with decreasing probability over time.
"""

import numpy as np
from numpy.typing import NDArray
from typing import Optional


class SimulatedAnnealingStrategy:
    """
    Simulated Annealing metaheuristic for TSP.
    
    Uses temperature-based acceptance probability to explore the solution space
    and escape local optima.
    """
    
    def __init__(
        self,
        initial_temperature: float = 100.0,
        cooling_rate: float = 0.995,
        backend: str = "cpu",
        seed: Optional[int] = None
    ):
        """
        Initialize the strategy.
        
        Args:
            initial_temperature: Starting temperature
            cooling_rate: Rate at which temperature decreases (0 < rate < 1)
            backend: Computational backend
            seed: Random seed for reproducibility
        """
        self._backend = backend
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.rng = np.random.default_rng(seed)
    
    @property
    def name(self) -> str:
        return "SimulatedAnnealing"
    
    @property
    def backend(self) -> str:
        return self._backend
    
    def search(
        self,
        initial_solution: NDArray[np.int_],
        distance_matrix: NDArray[np.float64],
        max_iterations: int = 10000,
        **kwargs
    ) -> tuple[NDArray[np.int_], float]:
        """
        Perform simulated annealing search.
        
        Args:
            initial_solution: Starting tour
            distance_matrix: Precomputed distance matrix
            max_iterations: Maximum number of iterations
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (best_solution, best_cost)
        """
        current_solution = initial_solution.copy()
        current_cost = self._calculate_cost(current_solution, distance_matrix)
        
        best_solution = current_solution.copy()
        best_cost = current_cost
        
        temperature = self.initial_temperature
        
        for iteration in range(max_iterations):
            # Generate neighbor solution using 2-opt move
            neighbor = self._generate_neighbor(current_solution)
            neighbor_cost = self._calculate_cost(neighbor, distance_matrix)
            
            # Calculate change in cost
            delta = neighbor_cost - current_cost
            
            # Accept or reject the neighbor
            if delta < 0:
                # Always accept improvements
                current_solution = neighbor
                current_cost = neighbor_cost
                
                # Update best solution if better
                if current_cost < best_cost:
                    best_solution = current_solution.copy()
                    best_cost = current_cost
            else:
                # Accept worse solutions with probability based on temperature
                acceptance_prob = np.exp(-delta / temperature)
                if self.rng.random() < acceptance_prob:
                    current_solution = neighbor
                    current_cost = neighbor_cost
            
            # Cool down temperature
            temperature *= self.cooling_rate
            
            # Stop if temperature is too low
            if temperature < 1e-8:
                break
        
        return best_solution, best_cost
    
    def _generate_neighbor(self, solution: NDArray[np.int_]) -> NDArray[np.int_]:
        """
        Generate a neighbor solution using 2-opt move.
        
        Args:
            solution: Current solution
            
        Returns:
            Neighbor solution
        """
        neighbor = solution.copy()
        n = len(neighbor)
        
        # Random 2-opt swap - ensure i+2 < n
        i = self.rng.integers(0, n - 2)  # Changed from n-1 to n-2
        j = self.rng.integers(i + 2, n)
        
        # Reverse segment between i+1 and j
        neighbor[i + 1:j + 1] = neighbor[i + 1:j + 1][::-1]
        
        return neighbor
    
    def _calculate_cost(
        self,
        tour: NDArray[np.int_],
        distance_matrix: NDArray[np.float64]
    ) -> float:
        """Calculate the total cost of a tour."""
        cost = 0.0
        n = len(tour)
        for i in range(n):
            cost += distance_matrix[tour[i], tour[(i + 1) % n]]
        return cost
