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

from typing import List
import numpy as np
from ...protocols.backend import BackendModule


# ==============================================================================
# FFD STRATEGY (First Fit Decreasing)
# ==============================================================================


class FFDStrategy:
    """
    First Fit Decreasing bin packing strategy.

    Sorts items by demand (descending), then assigns each item to the first
    bin with sufficient remaining capacity. Creates new bin if none found.

    Time Complexity: O(n log n) sort + O(n²) assignments
    Approximation Ratio: 11/9 OPT + 6/9 (Johnson, 1973)

    Attributes:
        _algorithm: FirstFitDecreasing instance (existing implementation)

    Methods:
        pack: Group items into capacity-constrained bins

    Example:
        >>> strategy = FFDStrategy()
        >>> bins = strategy.pack(
        ...     demands=np.array([0.6, 0.4, 0.5, 0.3]),
        ...     capacity=1.0,
        ...     xp=np
        ... )
        >>> # bins = [[0, 3], [1, 2]]  (0.6+0.3=0.9, 0.5+0.4=0.9)

    Implementation Note:
        This is an ADAPTER that wraps the existing FirstFitDecreasing class
        from algorithms.bin_packing.construction.first_fit_decreasing.

        **Backend Limitation (Temporary):**
        The wrapped algorithm is CPU-only (uses vanilla NumPy). The `xp`
        parameter is accepted for protocol compliance, but CuPy arrays are
        converted to NumPy before processing.

        Future: Vectorize bin packing for GPU acceleration.
    """

    def __init__(self):
        """Initialize FFD strategy by wrapping existing algorithm."""
        from ..bin_packing.construction.first_fit_decreasing import (
            FirstFitDecreasing,
        )

        self._algorithm = FirstFitDecreasing()

    def pack(
        self, demands: np.ndarray, capacity: float, xp: BackendModule = np
    ) -> List[List[int]]:
        """
        Group items into bins using First Fit Decreasing.

        Args:
            demands: (n,) array of item demands
            capacity: Maximum bin capacity
            xp: Backend module (NumPy or CuPy) - currently only NumPy supported

        Returns:
            List of bins (each bin is list of item indices)

        Raises:
            ValueError: If any demand exceeds capacity
            ValueError: If capacity <= 0

        Implementation Note:
            CuPy arrays are converted to NumPy (CPU processing) because the
            underlying bin packing algorithm is not yet vectorized for GPU.
            This is acceptable since bin packing is O(n log n) and typically
            fast even on CPU for CVRP problem sizes (n < 3000).
        """
        # Convert backend arrays to NumPy (bin packing is CPU-only for now)
        if hasattr(demands, "get"):  # CuPy array
            demands_np = demands.get()  # Explicit GPU->CPU transfer
        else:  # NumPy array
            demands_np = np.asarray(demands)  # Zero-copy

        # Call existing algorithm (validates inputs internally)
        bins = self._algorithm.pack(demands_np, capacity)

        return bins


# ==============================================================================
# BFD STRATEGY (Best Fit Decreasing)
# ==============================================================================


class BFDStrategy:
    """
    Best Fit Decreasing bin packing strategy.

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
        pack: Group items into capacity-constrained bins

    Example:
        >>> strategy = BFDStrategy()
        >>> bins = strategy.pack(
        ...     demands=np.array([0.7, 0.5, 0.3, 0.2]),
        ...     capacity=1.0,
        ...     xp=np
        ... )
        >>> # bins = [[0, 2], [1, 3]]  (0.7+0.2=0.9, 0.5+0.3=0.8)

    Implementation Note:
        This is an ADAPTER that wraps the existing BestFitDecreasing class
        from algorithms.bin_packing.construction.best_fit_decreasing.

        **Backend Limitation (Temporary):**
        The wrapped algorithm is CPU-only (uses vanilla NumPy). The `xp`
        parameter is accepted for protocol compliance, but CuPy arrays are
        converted to NumPy before processing.

        Future: Vectorize bin packing for GPU acceleration.
    """

    def __init__(self):
        """Initialize BFD strategy by wrapping existing algorithm."""
        from ..bin_packing.construction.best_fit_decreasing import (
            BestFitDecreasing,
        )

        self._algorithm = BestFitDecreasing()

    def pack(
        self, demands: np.ndarray, capacity: float, xp: BackendModule = np
    ) -> List[List[int]]:
        """
        Group items into bins using Best Fit Decreasing.

        Args:
            demands: (n,) array of item demands
            capacity: Maximum bin capacity
            xp: Backend module (NumPy or CuPy) - currently only NumPy supported

        Returns:
            List of bins (each bin is list of item indices)

        Raises:
            ValueError: If any demand exceeds capacity
            ValueError: If capacity <= 0

        Implementation Note:
            CuPy arrays are converted to NumPy (CPU processing) because the
            underlying bin packing algorithm is not yet vectorized for GPU.
            This is acceptable since bin packing is O(n log n) and typically
            fast even on CPU for CVRP problem sizes (n < 3000).
        """
        # Convert backend arrays to NumPy (bin packing is CPU-only for now)
        if hasattr(demands, "get"):  # CuPy array
            demands_np = demands.get()  # Explicit GPU->CPU transfer
        else:  # NumPy array
            demands_np = np.asarray(demands)  # Zero-copy

        # Call existing algorithm (validates inputs internally)
        bins = self._algorithm.pack(demands_np, capacity)

        return bins


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
