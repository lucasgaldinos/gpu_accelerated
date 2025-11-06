"""
Bin packing strategy implementations (FFD, BFD).

This module provides wrapper classes that adapt existing bin packing algorithms
to the BinPackingStrategy protocol, enabling "Lego Blocks" composition.

Strategies:
    - FFDStrategy: First Fit Decreasing (sorts demands, greedy bin assignment)
    - BFDStrategy: Best Fit Decreasing (sorts demands, minimizes waste)

Design Pattern:
    These classes are ADAPTERS that wrap existing implementations in
    `algorithms.bin_packing.first_fit_decreasing` and `algorithms.bin_packing.best_fit_decreasing`.
    They conform to the BinPackingStrategy protocol for dependency injection.

Example Usage:
    >>> from algorithms.strategies.bin_packing_strategies import FFDStrategy
    >>> from algorithms.compositional_cvrp_solver import lego_cvrp_solver
    >>>
    >>> # Swap strategies at runtime
    >>> routes_ffd = lego_cvrp_solver(..., bin_packing_strategy=FFDStrategy())
    >>> routes_bfd = lego_cvrp_solver(..., bin_packing_strategy=BFDStrategy())

Performance Characteristics:
    - FFD: O(n log n) sorting + O(n²) bin assignment
    - BFD: O(n log n) sorting + O(n² log n) bin selection
    - Both are 11/9-approximations for offline bin packing

References:
    - Johnson (1973): "Near-optimal bin packing algorithms"
    - Garey & Johnson (1979): "Computers and Intractability"

See Also:
    - protocols.algorithm_strategies.BinPackingStrategy
    - algorithms.bin_packing.first_fit_decreasing
    - algorithms.bin_packing.best_fit_decreasing
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...protocols.problem_context import ProblemContext


# ==============================================================================
# FFD STRATEGY (First Fit Decreasing)
# ==============================================================================


class FFDStrategy:
    """
    First Fit Decreasing bin packing strategy (Class S - CPU only).

    **Architectural Classification: Class S (Sequential)**
    Bin packing is inherently sequential with greedy bin assignment. Runs
    on CPU regardless of ProblemContext backend.

    Sorts items by demand (descending), then assigns each item to the first
    bin with sufficient remaining capacity. Creates new bin if none found.

    Time Complexity: O(n log n) sort + O(n²) assignments
    Approximation Ratio: 11/9 OPT + 6/9 (Johnson, 1973)

    Attributes:
        _algorithm: FirstFitDecreasing instance (existing implementation)

    Methods:
        pack: Group customers into capacity-constrained bins

    Example:
        >>> from src.protocols import ProblemContext
        >>> import numpy as np
        >>>
        >>> context = ProblemContext(problem, xp=np)
        >>> strategy = FFDStrategy()
        >>> bins = strategy.pack(context)
        >>> # bins = [[1, 4], [2, 3]]  (customer indices)
        >>>
        >>> # Even with GPU context, bin packing runs on CPU
        >>> import cupy as cp
        >>> gpu_context = ProblemContext(problem, xp=cp)
        >>> bins = strategy.pack(gpu_context)
        >>> # Internally calls gpu_context.get_cpu_demands()

    Implementation Note:
        This is an ADAPTER that wraps the existing FirstFitDecreasing class
        from algorithms.bin_packing.construction.first_fit_decreasing.

        The wrapped algorithm is CPU-only (uses vanilla NumPy), which is
        acceptable since bin packing is O(n log n) and typically fast even
        on CPU for CVRP problem sizes (n < 3000).
    """

    def __init__(self):
        """Initialize FFD strategy by wrapping existing algorithm."""
        from ..bin_packing.construction.first_fit_decreasing import (
            FirstFitDecreasing,
        )

        self._algorithm = FirstFitDecreasing()

    def pack(
        self, context: "ProblemContext", customer_indices: List[int]
    ) -> List[List[int]]:
        """
        Group customers into bins using First Fit Decreasing.

        Args:
            context: ProblemContext with demands and capacity
            customer_indices: Indices of customers to pack (excludes depots)

        Returns:
            List of bins (each bin contains customer indices from customer_indices)

        Raises:
            ValueError: If any demand exceeds capacity
            ValueError: If capacity <= 0
            IndexError: If customer_indices contains invalid indices

        Implementation Note:
            Uses context.get_cpu_demands() to extract demands from context
            (which may be on GPU). Bin packing always runs on CPU since it's
            inherently sequential. The one-time GPU→CPU transfer is cheaper
            than the anti-pattern of running sequential code with GPU kernels.

        Example:
            >>> # Pack customers [1, 3, 5] from a problem with 6 nodes
            >>> bins = strategy.pack(context, [1, 3, 5])
            >>> # bins might be: [[5, 1], [3]]  (global indices)
        """
        # Get full CPU demands array from context (handles GPU→CPU if needed)
        demands_full = context.get_cpu_demands()

        # Extract demands for specified customers only
        # This supports arbitrary subsets: single cluster, depot subset, etc.
        customer_demands = demands_full[customer_indices]

        # Call existing CPU algorithm
        # Returns bins with LOCAL indices [0, len(customer_indices)-1]
        bins_local = self._algorithm.pack(customer_demands, context.capacity)

        # Map local indices back to global problem space
        # Example: customer_indices=[5,1,3], bins_local=[[0,2],[1]]
        #          → bins_global=[[5,3],[1]]
        bins_global = [
            [customer_indices[local_idx] for local_idx in bin_local]
            for bin_local in bins_local
        ]

        return bins_global


# ==============================================================================
# BFD STRATEGY (Best Fit Decreasing)
# ==============================================================================


class BFDStrategy:
    """
    Best Fit Decreasing bin packing strategy (Class S - CPU only).

    **Architectural Classification: Class S (Sequential)**
    Bin packing is inherently sequential with greedy bin assignment. Runs
    on CPU regardless of ProblemContext backend.

    Sorts items by demand (descending), then assigns each item to the bin
    with least remaining capacity that can still fit it. Creates new bin if none found.

    Time Complexity: O(n log n) sort + O(n² log n) assignments (with heap)
    Approximation Ratio: 11/9 OPT + 6/9 (same as FFD)

    Practical Advantage:
        BFD typically produces tighter packing (fewer wasted bins) than FFD,
        though worst-case guarantee is identical.

    Attributes:
        _algorithm: BestFitDecreasing instance (existing implementation)

    Methods:
        pack: Group customers into capacity-constrained bins

    Example:
        >>> from src.protocols import ProblemContext
        >>> import numpy as np
        >>>
        >>> context = ProblemContext(problem, xp=np)
        >>> strategy = BFDStrategy()
        >>> bins = strategy.pack(context)
        >>> # bins = [[1, 4], [2, 3]]  (customer indices)
        >>>
        >>> # Even with GPU context, bin packing runs on CPU
        >>> import cupy as cp
        >>> gpu_context = ProblemContext(problem, xp=cp)
        >>> bins = strategy.pack(gpu_context)
        >>> # Internally calls gpu_context.get_cpu_demands()

    Implementation Note:
        This is an ADAPTER that wraps the existing BestFitDecreasing class
        from algorithms.bin_packing.construction.best_fit_decreasing.

        The wrapped algorithm is CPU-only (uses vanilla NumPy), which is
        acceptable since bin packing is O(n log n) and typically fast even
        on CPU for CVRP problem sizes (n < 3000).
    """

    def __init__(self):
        """Initialize BFD strategy by wrapping existing algorithm."""
        from ..bin_packing.construction.best_fit_decreasing import (
            BestFitDecreasing,
        )

        self._algorithm = BestFitDecreasing()

    def pack(
        self, context: "ProblemContext", customer_indices: List[int]
    ) -> List[List[int]]:
        """
        Group customers into bins using Best Fit Decreasing.

        Args:
            context: ProblemContext with demands and capacity
            customer_indices: Indices of customers to pack (excludes depots)

        Returns:
            List of bins (each bin contains customer indices from customer_indices)

        Raises:
            ValueError: If any demand exceeds capacity
            ValueError: If capacity <= 0
            IndexError: If customer_indices contains invalid indices

        Implementation Note:
            Uses context.get_cpu_demands() to extract demands from context
            (which may be on GPU). Bin packing always runs on CPU since it's
            inherently sequential. The one-time GPU→CPU transfer is cheaper
            than the anti-pattern of running sequential code with GPU kernels.

        Example:
            >>> # Pack customers [1, 3, 5] from a problem with 6 nodes
            >>> bins = strategy.pack(context, [1, 3, 5])
            >>> # bins might be: [[5, 1], [3]]  (global indices)
        """
        # Get full CPU demands array from context (handles GPU→CPU if needed)
        demands_full = context.get_cpu_demands()

        # Extract demands for specified customers only
        # This supports arbitrary subsets: single cluster, depot subset, etc.
        customer_demands = demands_full[customer_indices]

        # Call existing CPU algorithm
        # Returns bins with LOCAL indices [0, len(customer_indices)-1]
        bins_local = self._algorithm.pack(customer_demands, context.capacity)

        # Map local indices back to global problem space
        # Example: customer_indices=[5,1,3], bins_local=[[0,2],[1]]
        #          → bins_global=[[5,3],[1]]
        bins_global = [
            [customer_indices[local_idx] for local_idx in bin_local]
            for bin_local in bins_local
        ]

        return bins_global


# ==============================================================================
# FUTURE STRATEGIES (Placeholder)
# ==============================================================================

# class OnlineBinPackingStrategy:
#     """Online bin packing for dynamic CVRP variants."""
#     pass

# class CustomBinPackingStrategy:
#     """User-defined bin packing logic via lambda."""
#     def __init__(self, pack_fn):
#         self.pack_fn = pack_fn
#
#     def pack(self, demands, capacity, xp=np):
#         return self.pack_fn(demands, capacity, xp)
