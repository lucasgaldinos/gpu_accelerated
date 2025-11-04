"""
2-Opt Local Search Improvement Heuristic.

This strategy improves an existing tour by iteratively removing two edges
and reconnecting the tour in a different way.
"""

import numpy as np
from numpy.typing import NDArray


class TwoOptStrategy:
    """
    2-Opt improvement heuristic for TSP.
    
    This is a local search method that removes crossing edges and
    reconnects the tour to reduce total distance.
    """
    
    def __init__(self, backend: str = "cpu"):
        """
        Initialize the strategy.
        
        Args:
            backend: Computational backend ("cpu" or "numpy")
        """
        self._backend = backend
    
    @property
    def name(self) -> str:
        return "TwoOpt"
    
    @property
    def backend(self) -> str:
        return self._backend
    
    def improve(
        self,
        solution: NDArray[np.int_],
        distance_matrix: NDArray[np.float64],
        max_iterations: int = 1000,
        **kwargs
    ) -> tuple[NDArray[np.int_], float]:
        """
        Improve a tour using 2-opt local search.
        
        Args:
            solution: Current tour
            distance_matrix: Precomputed distance matrix
            max_iterations: Maximum number of iterations
            **kwargs: Additional parameters (unused)
            
        Returns:
            Tuple of (improved_tour, cost)
        """
        tour = solution.copy()
        n = len(tour)
        improved = True
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            # Try all possible 2-opt swaps
            for i in range(n - 1):
                for j in range(i + 2, n):
                    # Calculate change in tour length
                    # Current edges: (tour[i], tour[i+1]) and (tour[j], tour[(j+1)%n])
                    # New edges: (tour[i], tour[j]) and (tour[i+1], tour[(j+1)%n])
                    
                    current_dist = (
                        distance_matrix[tour[i], tour[i + 1]] +
                        distance_matrix[tour[j], tour[(j + 1) % n]]
                    )
                    
                    new_dist = (
                        distance_matrix[tour[i], tour[j]] +
                        distance_matrix[tour[i + 1], tour[(j + 1) % n]]
                    )
                    
                    # If improvement found, apply 2-opt swap
                    if new_dist < current_dist:
                        # Reverse the segment between i+1 and j
                        tour[i + 1:j + 1] = tour[i + 1:j + 1][::-1]
                        improved = True
                        break
                
                if improved:
                    break
        
        # Calculate final cost
        cost = self._calculate_cost(tour, distance_matrix)
        
        return tour, cost
    
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
