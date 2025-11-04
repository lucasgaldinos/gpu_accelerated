"""
2-opt improvement algorithm implementation for GPU.

This is a local search improvement heuristic that improves an existing tour
by removing two edges and reconnecting the path in a different way.
This implementation is optimized for GPU execution using CuPy.
"""

import numpy as np
from ..protocols import ProblemContext, GPUStrategy, ImprovementStrategy

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False


class TwoOptGPU:
    """
    GPU-based 2-opt improvement heuristic for TSP.
    
    This implementation uses CuPy for GPU-accelerated computation.
    It improves an existing tour by finding beneficial 2-opt swaps.
    
    The 2-opt move:
    - Takes two edges (i, i+1) and (j, j+1)
    - Removes them and reconnects as (i, j) and (i+1, j+1)
    - This reverses the tour segment between i+1 and j
    
    Note: This is a simplified implementation for demonstration.
    A production version would use custom CUDA kernels to evaluate
    all swaps in parallel, avoiding the CPU-GPU transfer overhead
    in the current nested loop structure.
    
    Implements: ImprovementStrategy protocol
    """
    
    def __init__(self, max_iterations: int = 100):
        """
        Initialize the 2-opt GPU strategy.
        
        Args:
            max_iterations: Maximum number of improvement iterations
        """
        if not CUPY_AVAILABLE:
            raise RuntimeError("CuPy is not available. Cannot use GPU-based 2-opt.")
        
        self.max_iterations = max_iterations
    
    def solve(self, context: ProblemContext, initial_solution: np.ndarray = None):
        """
        Improve a tour using 2-opt on GPU.
        
        Args:
            context: ProblemContext with problem data
            initial_solution: Initial tour to improve (if None, creates greedy tour)
            
        Returns:
            Improved tour as numpy array
        """
        if initial_solution is None:
            # Create a simple greedy tour as starting point
            initial_solution = np.arange(context.n_nodes + 1, dtype=np.int32)
            initial_solution[-1] = 0  # Close the tour
        
        return self.improve(context, initial_solution)
    
    def improve(self, context: ProblemContext, initial_solution: np.ndarray) -> np.ndarray:
        """
        Improve a tour using 2-opt on GPU.
        
        Args:
            context: ProblemContext with problem data
            initial_solution: Initial tour to improve
            
        Returns:
            Improved tour as numpy array
            
        Note: The current implementation uses a nested loop with CPU control
        flow for demonstration. A production implementation would use custom
        CUDA kernels to evaluate all swap candidates in parallel, eliminating
        the CPU-GPU transfer overhead.
        """
        # Get GPU distance matrix (will be computed and cached if not already)
        distances_gpu = context.compute_distance_matrix_gpu()
        
        # Transfer tour to GPU
        tour = cp.asarray(initial_solution, dtype=cp.int32)
        n = len(tour) - 1  # Number of nodes (excluding duplicate start/end)
        
        improved = True
        iteration = 0
        
        while improved and iteration < self.max_iterations:
            improved = False
            iteration += 1
            
            # NOTE: The following nested loop structure is a simplified implementation
            # for demonstration purposes. It performs CPU-GPU transfers in each iteration
            # which negates GPU acceleration benefits.
            # 
            # Production implementation should use a custom CUDA kernel that:
            # 1. Evaluates all O(n²) swap candidates in parallel on GPU
            # 2. Reduces to find the best swap entirely on GPU
            # 3. Only transfers the best swap indices back to CPU
            # This would eliminate O(n²) memory transfers and leverage GPU parallelism.
            
            # Try all possible 2-opt swaps
            best_delta = 0
            best_i = -1
            best_j = -1
            
            # Convert to CPU for loop control (in production, this should be a GPU kernel)
            tour_cpu = cp.asnumpy(tour)
            
            for i in range(n - 1):
                for j in range(i + 2, n):
                    # Calculate change in tour length for this swap
                    # Current edges: (tour[i], tour[i+1]) and (tour[j], tour[j+1])
                    # New edges: (tour[i], tour[j]) and (tour[i+1], tour[j+1])
                    
                    # Get indices
                    a, b = tour_cpu[i], tour_cpu[i + 1]
                    c, d = tour_cpu[j], tour_cpu[j + 1]
                    
                    # Calculate on GPU
                    current_dist = (
                        float(distances_gpu[a, b]) + float(distances_gpu[c, d])
                    )
                    new_dist = (
                        float(distances_gpu[a, c]) + float(distances_gpu[b, d])
                    )
                    
                    delta = new_dist - current_dist
                    
                    if delta < best_delta:
                        best_delta = delta
                        best_i = i
                        best_j = j
                        improved = True
            
            # Apply best improvement if found
            if improved:
                tour_cpu = cp.asnumpy(tour)
                # Reverse the segment between i+1 and j
                tour_cpu[best_i + 1:best_j + 1] = tour_cpu[best_i + 1:best_j + 1][::-1]
                tour = cp.asarray(tour_cpu)
        
        # Return improved tour as numpy array
        return cp.asnumpy(tour)
    
    def get_solution_cost(self, context: ProblemContext, solution) -> float:
        """
        Calculate the total cost of a tour using GPU.
        
        Args:
            context: ProblemContext with problem data
            solution: Tour as array (numpy or CuPy)
            
        Returns:
            Total tour distance
        """
        distances_gpu = context.compute_distance_matrix_gpu()
        
        # Ensure solution is on GPU
        if isinstance(solution, np.ndarray):
            solution_gpu = cp.asarray(solution)
        else:
            solution_gpu = solution
        
        # Calculate sum of distances between consecutive nodes
        total_cost = 0.0
        for i in range(len(solution_gpu) - 1):
            idx1 = int(solution_gpu[i])
            idx2 = int(solution_gpu[i + 1])
            total_cost += float(distances_gpu[idx1, idx2])
        
        return total_cost
    
    def __repr__(self) -> str:
        return f"TwoOptGPU(max_iterations={self.max_iterations})"


# Note: This is a simplified implementation for demonstration.
# A production GPU 2-opt would use custom CUDA kernels for parallel evaluation
# of all swap candidates, significantly improving performance.


if __name__ == "__main__":
    if CUPY_AVAILABLE:
        # Simple test
        coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            [0.5, 0.5],
        ])
        
        context = ProblemContext(coordinates=coords)
        
        # Start with a simple tour
        initial_tour = np.array([0, 1, 2, 3, 4, 0])
        
        optimizer = TwoOptGPU(max_iterations=10)
        improved_tour = optimizer.improve(context, initial_tour)
        cost = optimizer.get_solution_cost(context, improved_tour)
        
        print(f"Initial tour: {initial_tour}")
        print(f"Improved tour: {improved_tour}")
        print(f"Cost: {cost:.2f}")
    else:
        print("CuPy not available. Cannot run GPU 2-opt test.")
