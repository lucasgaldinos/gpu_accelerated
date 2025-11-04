"""
ProblemContext - Centralized data management for optimization problems.

This class addresses the anti-pattern of recomputing distance matrices
by providing a centralized place to store and reuse problem data.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from numpy.typing import NDArray


@dataclass
class ProblemContext:
    """
    Centralized context for TSP/VRP problem data.
    
    This class ensures that expensive computations like distance matrices
    are computed once and reused across all strategies.
    """
    
    coordinates: NDArray[np.float64]
    """Node coordinates as (n_nodes, 2) array"""
    
    _distance_matrix: Optional[NDArray[np.float64]] = None
    """Cached distance matrix"""
    
    @property
    def n_nodes(self) -> int:
        """Number of nodes in the problem."""
        return len(self.coordinates)
    
    @property
    def distance_matrix(self) -> NDArray[np.float64]:
        """
        Get or compute the distance matrix.
        
        The distance matrix is computed once and cached for reuse.
        This prevents the anti-pattern of recomputing distances in each strategy.
        """
        if self._distance_matrix is None:
            self._distance_matrix = self._compute_distance_matrix()
        return self._distance_matrix
    
    def _compute_distance_matrix(self) -> NDArray[np.float64]:
        """
        Compute Euclidean distance matrix from coordinates.
        
        Returns:
            Symmetric distance matrix of shape (n_nodes, n_nodes)
        """
        n = self.n_nodes
        coords = self.coordinates
        
        # Vectorized distance computation
        # Using broadcasting: (n, 1, 2) - (1, n, 2) -> (n, n, 2)
        diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
        distances = np.sqrt(np.sum(diff ** 2, axis=2))
        
        return distances
    
    def compute_tour_cost(self, tour: NDArray[np.int_]) -> float:
        """
        Compute the total cost of a tour.
        
        Args:
            tour: Array of node indices representing the tour
            
        Returns:
            Total tour distance
        """
        dist_matrix = self.distance_matrix
        
        # Cost is sum of distances between consecutive nodes
        cost = 0.0
        for i in range(len(tour)):
            from_node = tour[i]
            to_node = tour[(i + 1) % len(tour)]
            cost += dist_matrix[from_node, to_node]
        
        return cost
    
    def validate_tour(self, tour: NDArray[np.int_]) -> bool:
        """
        Validate that a tour is valid.
        
        Args:
            tour: Array of node indices
            
        Returns:
            True if tour is valid
        """
        # Check all nodes are visited exactly once
        if len(tour) != self.n_nodes:
            return False
        
        if len(set(tour)) != self.n_nodes:
            return False
        
        # Check indices are in valid range
        if np.any(tour < 0) or np.any(tour >= self.n_nodes):
            return False
        
        return True
    
    @classmethod
    def from_random(cls, n_nodes: int, seed: Optional[int] = None) -> 'ProblemContext':
        """
        Create a random problem instance.
        
        Args:
            n_nodes: Number of nodes
            seed: Random seed for reproducibility
            
        Returns:
            New ProblemContext with random coordinates
        """
        rng = np.random.default_rng(seed)
        coordinates = rng.random((n_nodes, 2)) * 100.0  # Scale to 0-100 range
        return cls(coordinates=coordinates)
