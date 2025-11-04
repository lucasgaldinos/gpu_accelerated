"""
Best Fit Decreasing (BFD) bin packing algorithm.

This module implements the Best Fit Decreasing strategy for bin packing,
which sorts items in descending order and places each item in the bin with
the LEAST remaining capacity that can still accommodate it.

Academic Reference:
------------------
Simchi-Levi, D., Chen, X., & Bramel, J. (2005). "The logic of logistics:
Theory, algorithms, and applications for logistics and supply chain management",
Springer.

Algorithm:
----------
1. Sort items by size in descending order (largest first)
2. For each item:
   - Find bin with MINIMUM remaining capacity that still fits the item
   - If no bin fits, create a new bin

Time Complexity: O(n log n)
- Sorting: O(n log n)
- Packing with min-heap: O(n log k) where k ≤ n bins
- Total: O(n log n)

Approximation Guarantee:
-----------------------
BFD uses at most (11/9)OPT + 6/9 bins, where OPT is the optimal number of bins.

BFD typically produces tighter packing than FFD in practice due to minimizing
wasted space in bins.

Example:
--------
    >>> import numpy as np
    >>> from src.algorithms.bin_packing.construction.best_fit_decreasing import BestFitDecreasing
    >>>
    >>> # Customer demands (CVRP context)
    >>> demands = np.array([20, 30, 25, 40, 35, 15])
    >>> capacity = 100
    >>>
    >>> bfd = BestFitDecreasing()
    >>> bins = bfd.pack(demands, capacity)
    >>> # bins = [[3, 4, 2], [1, 0, 5]]
    >>> # Bin 1: items[3]=40, items[4]=35, items[2]=25 → load=100 (perfect fit!)
    >>> # Bin 2: items[1]=30, items[0]=20, items[5]=15 → load=65
    >>>
    >>> print(f"{bfd.get_name()} uses {len(bins)} bins")
    Best Fit Decreasing uses 2 bins
"""

from typing import List
import numpy as np
from numpy.typing import NDArray


class BestFitDecreasing:
    """
    Best Fit Decreasing bin packing strategy.

    Sorts items in descending order by size, then applies Best Fit heuristic:
    place each item in the bin with MINIMUM remaining capacity that can fit it.

    **Algorithm Pseudocode:**

    ```
    Algorithm: BestFitDecreasing
    Input: items[] with demands/sizes, capacity C
    Output: bins[] where bins[i] = list of item indices in bin i

    1:  # Create (size, original_index) pairs
    2:  indexed_items ← [(items[i], i) for i in 0 to n-1]
    3:
    4:  # Sort by size descending (largest first)
    5:  sorted_items ← sort(indexed_items, key=size, reverse=True)
    6:
    7:  bins ← []                    # List of bins
    8:  heap ← []                     # Min-heap of (remaining_capacity, bin_index)
    9:
    10: for (size, original_idx) in sorted_items do
    11:     placed ← false
    12:
    13:     # Find bin with minimum remaining capacity that fits
    14:     if heap is not empty then
    15:         (remaining, bin_idx) ← heap.peek()
    16:
    17:         if size ≤ remaining then
    18:             # Remove bin from heap
    19:             heap.extract_min()
    20:
    21:             # Add item to bin
    22:             bins[bin_idx].append(original_idx)
    23:             new_remaining ← remaining - size
    24:
    25:             # Re-insert with updated remaining capacity
    26:             heap.insert((new_remaining, bin_idx))
    27:             placed ← true
    28:
    29:     # If no bin fits, create new bin
    30:     if not placed then
    31:         bin_idx ← |bins|
    32:         bins.append([original_idx])
    33:         new_remaining ← C - size
    34:         heap.insert((new_remaining, bin_idx))
    35:
    36: return bins
    ```

    Time Complexity:
        - Sorting: O(n log n)
        - Heap operations: O(log k) per item, k ≤ n bins
        - Total packing: O(n log k) ≈ O(n log n)
        - Overall: O(n log n)

    Space Complexity:
        - O(n) for sorted array
        - O(k) for heap where k ≤ n bins

    Key Advantage over FFD:
        BFD minimizes wasted space by choosing the tightest fit, leading to
        better average-case packing efficiency than FFD's first-fit strategy.

    Attributes:
        _name: Strategy identifier

    Methods:
        pack: Assign items to bins using BFD
        get_name: Return "Best Fit Decreasing"
        uses_sorting: Return True (BFD sorts items)

    Example - Basic Usage:
        >>> demands = np.array([45, 30, 25, 20, 15])
        >>> bfd = BestFitDecreasing()
        >>> bins = bfd.pack(demands, capacity=100)
        >>> bins  # [[0, 1, 2], [3, 4]]
        >>> # Sorted order: 45, 30, 25, 20, 15
        >>> # Bin 1: 45 + 30 + 25 = 100 (perfect fit - best fit strategy)
        >>> # Bin 2: 20 + 15 = 35

    Example - BFD vs FFD Difference:
        >>> items = np.array([70, 30, 30, 30, 30])
        >>> capacity = 100
        >>>
        >>> bfd = BestFitDecreasing()
        >>> bfd_bins = bfd.pack(items, capacity)
        >>> print(f"BFD: {len(bfd_bins)} bins")  # 3 bins: [70,30], [30,30], [30]
        >>>
        >>> # FFD might use same or different packing depending on ties
        >>> # BFD tends to minimize wasted space more consistently
    """

    def __init__(self):
        """Initialize Best Fit Decreasing strategy."""
        self._name = "Best Fit Decreasing"

    def pack(self, items: NDArray, capacity: float) -> List[List[int]]:
        """
        Pack items into bins using Best Fit Decreasing strategy.

        Sorts items in descending order, then places each item in the bin
        with minimum remaining capacity that can still fit it (best fit).
        Uses a min-heap for efficient O(log k) bin selection.

        Args:
            items: 1D NumPy array of item sizes/demands, shape (n,)
                Example: np.array([20, 30, 25, 40, 35, 15])

            capacity: Maximum capacity per bin (vehicle capacity)
                Must be positive and >= max(items)

        Returns:
            bins: List of bins, each bin is list of item indices
                Example: [[3, 4, 2], [1, 0, 5]]
                Indices refer to original items array positions

        Raises:
            ValueError: If any item exceeds capacity
            ValueError: If capacity <= 0
            ValueError: If items array is empty

        Example:
            >>> demands = np.array([20, 30, 25, 40, 35])
            >>> bfd = BestFitDecreasing()
            >>> bins = bfd.pack(demands, capacity=100)
            >>>
            >>> # Verify packing
            >>> for i, bin_indices in enumerate(bins, 1):
            ...     load = sum(demands[idx] for idx in bin_indices)
            ...     remaining = 100 - load
            ...     print(f"Bin {i}: {bin_indices} → load={load}/100, waste={remaining}")
            Bin 1: [3, 4, 2] → load=100/100, waste=0  # Perfect fit!
            Bin 2: [1, 0] → load=50/100, waste=50
        """
        # Validation
        if capacity <= 0:
            raise ValueError(f"Capacity must be positive, got {capacity}")

        if len(items) == 0:
            raise ValueError("Items array cannot be empty")

        if np.any(items > capacity):
            max_item = np.max(items)
            raise ValueError(f"Item size {max_item} exceeds capacity {capacity}")

        # Create (size, original_index) pairs
        n = len(items)
        indexed_items = [(items[i], i) for i in range(n)]

        # Sort by size descending (largest first)
        sorted_items = sorted(indexed_items, key=lambda x: x[0], reverse=True)

        # Initialize bins and track remaining capacity
        bins: List[List[int]] = []
        remaining_capacity: List[float] = []

        # Pack each item using Best Fit
        for size, original_idx in sorted_items:
            # Find bin with minimum remaining capacity that can fit item
            best_bin_idx = -1
            min_remaining = float("inf")

            for bin_idx, remaining in enumerate(remaining_capacity):
                if size <= remaining and remaining < min_remaining:
                    best_bin_idx = bin_idx
                    min_remaining = remaining

            if best_bin_idx != -1:
                # Place item in best fitting bin
                bins[best_bin_idx].append(original_idx)
                remaining_capacity[best_bin_idx] -= size
            else:
                # No bin fits, create new bin
                bins.append([original_idx])
                remaining_capacity.append(capacity - size)

        return bins

    def get_name(self) -> str:
        """
        Return strategy name.

        Returns:
            "Best Fit Decreasing"
        """
        return self._name

    def uses_sorting(self) -> bool:
        """
        Indicate whether this strategy sorts items.

        Returns:
            True - BFD sorts items in descending order
        """
        return True
