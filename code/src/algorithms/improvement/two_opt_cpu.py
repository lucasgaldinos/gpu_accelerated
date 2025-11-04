"""
CPU-based 2-opt local search for TSP.

This module provides a baseline CPU implementation of 2-opt local search
for performance comparison with GPU implementations.

Algorithm Overview:
    - Sequential 2-opt improvement (Class P - but CPU implementation)
    - Evaluates all O(N²) possible 2-opt moves
    - Applies best improving move iteratively
    - Continues until local optimum (no improvement found)

Performance Characteristics:
    - Time: O(N²) per iteration × number of iterations
    - Space: O(N) for tour storage
    - Typical iterations: 10-50 for random instances

Example Usage:
    >>> import numpy as np
    >>> from src.protocols import ProblemContext
    >>> from src.algorithms.improvement.two_opt_cpu import TwoOptCPU
    >>>
    >>> # Create context with precomputed distance matrix
    >>> context = ProblemContext(problem, xp=np)
    >>>
    >>> # Initial tour from construction heuristic
    >>> tour = [0, 5, 3, 7, 2, 0]
    >>>
    >>> # Improve tour on CPU
    >>> strategy = TwoOptCPU(max_iterations=1000)
    >>> improved_tour = strategy.improve_tour(context, tour)

See Also:
    - protocols.algorithm_strategies.TspImprovementStrategy
    - algorithms.improvement.two_opt_gpu (GPU acceleration)
"""

from typing import List, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from ...protocols.problem_context import ProblemContext


class TwoOptCPU:
    """
    CPU-based 2-opt local search for TSP (Class P - parallelizable).

    **Architectural Classification: Class P (Parallel)**
    While this is the CPU implementation, 2-opt is classified as Class P because
    it has parallelizable components (evaluating all O(n²) swaps). This CPU
    version serves as the baseline for comparing GPU acceleration.

    This implementation provides a baseline for comparing GPU performance.
    It uses standard Python loops with NumPy for distance lookups.

    Attributes:
        max_iterations: Maximum number of improvement iterations
        convergence_threshold: Stop if improvement < threshold

    Performance Notes:
        - Suitable for all problem sizes
        - Typical time: 10-100ms for N=100, 1-10s for N=1000
        - Memory: O(N) tour + O(N²) distance matrix (from context)

    Example:
        >>> from src.protocols import ProblemContext
        >>> context = ProblemContext(problem, xp=np)
        >>> strategy = TwoOptCPU(max_iterations=1000)
        >>> improved = strategy.improve_tour(context, tour)
    """

    def __init__(self, max_iterations: int = 1000, convergence_threshold: float = 1e-6):
        """
        Initialize CPU 2-opt strategy.

        Args:
            max_iterations: Maximum improvement iterations
            convergence_threshold: Stop if improvement < threshold
        """
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold

    def improve_tour(self, context: "ProblemContext", tour: List[int]) -> List[int]:
        """
        Improve TSP tour using CPU 2-opt.

        Args:
            context: ProblemContext with precomputed distance matrix
            tour: Current tour [depot, c1, c2, ..., ck, depot]

        Returns:
            Improved tour with same structure (same customers, better cost)

        Returns:
            Improved tour with same structure

        Raises:
            ValueError: If tour is invalid

        Example:
            >>> tour = [0, 5, 3, 7, 2, 0]
            >>> distances = np.array([[...]])
            >>> improved = strategy.improve_tour(tour, distances, xp=np)
        """
        # Validation
        if len(tour) < 4:
            # Need at least 4 nodes for meaningful 2-opt
            return tour

        if tour[0] != 0 or tour[-1] != 0:
            raise ValueError(
                "Tour must start and end at depot (0). "
                f"Got: tour[0]={tour[0]}, tour[-1]={tour[-1]}"
            )

        # Get CPU distances from context (handles GPU→CPU transfer if needed)
        distances_np = context.get_cpu_distances()

        # Remove duplicate depot at end for processing
        current_tour = list(tour[:-1])
        n = len(current_tour)

        # Run iterative improvement
        improved = True
        iterations = 0

        while improved and iterations < self.max_iterations:
            improved = False
            best_improvement = 0.0
            best_i, best_j = -1, -1

            # Evaluate all possible 2-opt moves
            for i in range(n - 2):
                for j in range(i + 2, n):
                    # Evaluate 2-opt move: reverse tour[i+1:j+1]
                    # Old edges: (tour[i], tour[i+1]) and (tour[j], tour[j+1])
                    # New edges: (tour[i], tour[j]) and (tour[i+1], tour[j+1])

                    node_i = current_tour[i]
                    node_i1 = current_tour[i + 1]
                    node_j = current_tour[j]
                    node_j1 = current_tour[(j + 1) % n]  # Wrap around to depot

                    # Compute improvement (old cost - new cost)
                    old_cost = (
                        distances_np[node_i, node_i1] + distances_np[node_j, node_j1]
                    )
                    new_cost = (
                        distances_np[node_i, node_j] + distances_np[node_i1, node_j1]
                    )
                    improvement = old_cost - new_cost

                    # Track best improvement
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_i, best_j = i, j

            # Apply best improvement if found
            if best_improvement > self.convergence_threshold:
                # Reverse tour segment [i+1:j+1]
                current_tour[best_i + 1 : best_j + 1] = reversed(
                    current_tour[best_i + 1 : best_j + 1]
                )
                improved = True

            iterations += 1

        # Add depot return
        current_tour.append(0)

        return current_tour
