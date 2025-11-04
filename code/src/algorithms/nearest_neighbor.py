"""
Nearest Neighbor Constructive Heuristic.

This is a CPU-optimized implementation that avoids the anti-pattern
of excessive GPU kernel launches in sequential algorithms.
"""

import numpy as np
from numpy.typing import NDArray
from typing import Optional


class NearestNeighborStrategy:
    """
    Nearest Neighbor constructive heuristic for TSP.
    
    This implementation uses vectorized NumPy operations where possible
    to avoid the performance anti-pattern of Python loops with individual
    operations.
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
        return "NearestNeighbor"
    
    @property
    def backend(self) -> str:
        return self._backend
    
    def construct(
        self,
        distance_matrix: NDArray[np.float64],
        start_node: int = 0,
        **kwargs
    ) -> tuple[NDArray[np.int_], float]:
        """
        Construct a tour using the nearest neighbor heuristic.
        
        Args:
            distance_matrix: Precomputed distance matrix
            start_node: Starting node index
            **kwargs: Additional parameters (unused)
            
        Returns:
            Tuple of (tour, cost)
        """
        n_nodes = len(distance_matrix)
        
        # Initialize tour and tracking
        tour = np.zeros(n_nodes, dtype=np.int_)
        visited = np.zeros(n_nodes, dtype=bool)
        
        # Start at the specified node
        current_node = start_node
        tour[0] = current_node
        visited[current_node] = True
        total_cost = 0.0
        
        # Build tour by always selecting nearest unvisited neighbor
        for i in range(1, n_nodes):
            # Get distances to all nodes
            distances = distance_matrix[current_node].copy()
            
            # Mask visited nodes with infinity
            distances[visited] = np.inf
            
            # Select nearest unvisited neighbor
            next_node = np.argmin(distances)
            
            # Update tour
            tour[i] = next_node
            visited[next_node] = True
            total_cost += distance_matrix[current_node, next_node]
            current_node = next_node
        
        # Add cost to return to start
        total_cost += distance_matrix[current_node, start_node]
        
        return tour, total_cost
