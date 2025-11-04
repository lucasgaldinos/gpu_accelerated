"""
Nearest Neighbor algorithm implementation for CPU.

This is a greedy constructive heuristic for TSP that builds a tour by
repeatedly selecting the nearest unvisited node. This implementation
is optimized for CPU execution using NumPy.
"""

import numpy as np
from ..protocols import ProblemContext, CPUStrategy


class NearestNeighborCPU:
    """
    CPU-based Nearest Neighbor heuristic for TSP.
    
    This implementation uses NumPy for all computations and operates
    exclusively on CPU. It avoids the anti-pattern of calling GPU
    kernels within Python loops by working entirely with CPU arrays.
    
    The algorithm:
    1. Start at a given node (default: 0)
    2. Find the nearest unvisited node
    3. Add it to the tour
    4. Repeat until all nodes are visited
    5. Return to the starting node
    """
    
    def __init__(self, start_node: int = 0):
        """
        Initialize the Nearest Neighbor strategy.
        
        Args:
            start_node: Index of the starting node (default: 0)
        """
        self.start_node = start_node
    
    def solve(self, context: ProblemContext) -> np.ndarray:
        """
        Solve TSP using Nearest Neighbor heuristic on CPU.
        
        Args:
            context: ProblemContext with problem data
            
        Returns:
            Tour as numpy array of node indices
        """
        # Get CPU distance matrix (will be computed and cached if not already)
        distances = context.compute_distance_matrix_cpu()
        n_nodes = context.n_nodes
        
        # Validate start node
        if self.start_node >= n_nodes:
            raise ValueError(f"Start node {self.start_node} >= number of nodes {n_nodes}")
        
        # Initialize tour and visited tracking
        tour = np.zeros(n_nodes + 1, dtype=np.int32)
        visited = np.zeros(n_nodes, dtype=bool)
        
        # Start at the specified node
        current = self.start_node
        tour[0] = current
        visited[current] = True
        
        # Build tour by selecting nearest unvisited node
        for i in range(1, n_nodes):
            # Get distances from current node to all others
            dist_from_current = distances[current].copy()
            
            # Set distance to visited nodes to infinity
            dist_from_current[visited] = np.inf
            
            # Find nearest unvisited node
            nearest = np.argmin(dist_from_current)
            
            # Add to tour
            tour[i] = nearest
            visited[nearest] = True
            current = nearest
        
        # Close the tour by returning to start
        tour[n_nodes] = self.start_node
        
        return tour
    
    def get_solution_cost(self, context: ProblemContext, solution: np.ndarray) -> float:
        """
        Calculate the total cost of a tour.
        
        Args:
            context: ProblemContext with problem data
            solution: Tour as array of node indices
            
        Returns:
            Total tour distance
        """
        distances = context.compute_distance_matrix_cpu()
        
        # Calculate sum of distances between consecutive nodes
        total_cost = 0.0
        for i in range(len(solution) - 1):
            total_cost += distances[solution[i], solution[i + 1]]
        
        return total_cost
    
    def __repr__(self) -> str:
        return f"NearestNeighborCPU(start_node={self.start_node})"


# Type checking: Verify that NearestNeighborCPU implements CPUStrategy
def _check_protocol_compliance():
    """Compile-time check that NearestNeighborCPU implements CPUStrategy."""
    instance: CPUStrategy = NearestNeighborCPU()
    return instance


if __name__ == "__main__":
    # Simple test
    coords = np.array([
        [0, 0],
        [1, 0],
        [1, 1],
        [0, 1],
    ])
    
    context = ProblemContext(coordinates=coords)
    solver = NearestNeighborCPU()
    
    tour = solver.solve(context)
    cost = solver.get_solution_cost(context, tour)
    
    print(f"Tour: {tour}")
    print(f"Cost: {cost:.2f}")
