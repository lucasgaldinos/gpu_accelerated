"""
TSP improvement strategy implementations (2-opt CPU/GPU).

This module provides wrapper classes that adapt existing TSP improvement algorithms
to the TspImprovementStrategy protocol, enabling "Lego Blocks" composition.

Strategies:
    - TwoOptGPU: GPU-accelerated 2-opt using CUDA RawKernel (Class P-Task)

Design Pattern:
    These classes are ADAPTERS that wrap existing implementations from
    `algorithms.improvement.two_opt_gpu`. They conform to the TspImprovementStrategy
    protocol for dependency injection.

Architectural Classification:
    **Class P-Task (Task-Parallel)**: TwoOptGPU uses custom CUDA kernels for
    parallelizable neighborhood evaluation. This is the primary target for
    CPU vs GPU benchmarking.

Example Usage:
    >>> from algorithms.strategies.improvement_strategies import TwoOptGPU
    >>> from algorithms.compositional_cvrp_solver import lego_cvrp_solver
    >>> import cupy as cp
    >>>
    >>> # Apply GPU 2-opt improvement after construction
    >>> routes = lego_cvrp_solver(
    ...     locations, demands, capacity,
    ...     bin_packing_strategy=FFDStrategy(),
    ...     tsp_strategy=NearestNeighborStrategy(),
    ...     improvement_strategy=TwoOptGPU(),  # GPU improvement
    ...     xp=cp
    ... )

Performance Characteristics:
    - TwoOptGPU: O(n²) per iteration with GPU parallelization

References:
    - Fujimoto & Nakamura (2011): "GPU-accelerated 2-opt local search"
    - Croes (1958): "A method for solving traveling-salesman problems"

See Also:
    - protocols.algorithm_strategies.TspImprovementStrategy
    - algorithms.improvement.two_opt_gpu
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...protocols.problem_context import ProblemContext


# ==============================================================================
# TWO-OPT GPU STRATEGY (Class P-Task)
# ==============================================================================


class TwoOptGPUStrategy:
    """
    GPU-accelerated 2-opt improvement strategy (Class P-Task).

    **Architectural Classification: Class P-Task (Task-Parallel)**
    Uses custom CUDA RawKernel for parallel neighborhood evaluation.
    REQUIRES GPU backend - will raise ValueError if context.xp is NumPy.

    Wraps the existing TwoOptGPU implementation from algorithms.improvement.two_opt_gpu
    to conform to the TspImprovementStrategy protocol with ProblemContext.

    Time Complexity: O(n²) per iteration with GPU parallelization
    Space Complexity: O(n) on device + O(n²) for shared memory

    Attributes:
        max_iterations: Maximum number of 2-opt iterations (default: 100)
        threads_per_block: CUDA block size (default: 256)
        _wrapped_algorithm: Underlying TwoOptGPU instance

    Methods:
        improve_tour: Apply GPU 2-opt improvement to a tour

    Example:
        >>> from src.protocols import ProblemContext
        >>> from src.data_models import Problem
        >>> import cupy as cp
        >>>
        >>> # Create GPU context
        >>> problem = Problem(...)
        >>> context = ProblemContext(problem, xp=cp)
        >>>
        >>> # Construct initial tour
        >>> construction = NearestNeighborStrategy()
        >>> tour = construction.build_tour(context, [1, 2, 3, 4, 5])
        >>>
        >>> # Improve with GPU 2-opt
        >>> improvement = TwoOptGPUStrategy(max_iterations=50)
        >>> improved_tour = improvement.improve_tour(context, tour)
        >>> # improved_tour has lower cost

    Backend Requirements:
        - context.xp MUST be CuPy (has RawKernel attribute)
        - context.distances MUST be CuPy array in device memory
        - Raises ValueError if NumPy backend detected

    Implementation Note:
        This is an ADAPTER that wraps the existing TwoOptGPU class.

        The wrapper:
        1. Validates backend is GPU (checks for RawKernel)
        2. Calls underlying two_opt_gpu.improve_tour()
        3. Returns improved tour in same format
    """

    def __init__(self, max_iterations: int = 100, threads_per_block: int = 256):
        """
        Initialize GPU 2-opt strategy.

        Args:
            max_iterations: Maximum number of 2-opt passes
            threads_per_block: CUDA threads per block (tune for GPU)

        Note:
            The underlying TwoOptGPU kernel will be compiled lazily on first use.
        """
        self.max_iterations = max_iterations
        self.threads_per_block = threads_per_block
        self._wrapped_algorithm = None  # Lazy initialization

    def improve_tour(self, context: "ProblemContext", tour: List[int]) -> List[int]:
        """
        Improve TSP tour using GPU-accelerated 2-opt.

        Args:
            context: ProblemContext with distance matrix on GPU (CuPy)
            tour: Current tour [depot, c1, c2, ..., ck, depot]

        Returns:
            Improved tour with same structure (same customers, lower cost)

        Raises:
            ValueError: If context.xp is not CuPy (GPU required)
            ValueError: If tour is invalid (wrong structure)
            ImportError: If CuPy is not available

        Example:
            >>> context = ProblemContext(problem, xp=cp)
            >>> tour = [0, 5, 3, 7, 2, 0]
            >>> strategy = TwoOptGPUStrategy()
            >>> improved = strategy.improve_tour(context, tour)
            >>> # improved cost <= original cost
        """
        # GUARD: Validate GPU backend
        if not hasattr(context.xp, "RawKernel"):
            raise ValueError(
                "TwoOptGPUStrategy requires GPU backend (CuPy). "
                f"Got: {type(context.xp).__name__}. "
                "Use CPU context with TwoOptCPU instead, or create context with xp=cp."
            )

        # Lazy initialization of wrapped algorithm
        if self._wrapped_algorithm is None:
            from ..improvement.two_opt_gpu import TwoOptGPU

            self._wrapped_algorithm = TwoOptGPU(
                max_iterations=self.max_iterations,
                threads_per_block=self.threads_per_block,
            )

        # Validate tour structure
        if len(tour) < 3:
            raise ValueError(
                f"Tour must have at least 3 nodes (depot + 1 customer + depot return), "
                f"got {len(tour)} nodes"
            )

        if tour[0] != 0 or tour[-1] != 0:
            raise ValueError(
                f"Tour must start and end at depot (0), got start={tour[0]}, end={tour[-1]}"
            )

        # Call underlying GPU algorithm
        # NOTE: context.distances is already on GPU (CuPy array)
        improved_tour = self._wrapped_algorithm.improve_tour(
            tour=tour, distances=context.distances, xp=context.xp
        )

        return improved_tour


# ==============================================================================
# FUTURE STRATEGIES (Placeholder)
# ==============================================================================

# class TwoOptCPUStrategy:
#     """CPU-based 2-opt for comparison (Class S)."""
#     pass

# class ThreeOptStrategy:
#     """3-opt improvement (more expensive, better solutions)."""
#     pass
