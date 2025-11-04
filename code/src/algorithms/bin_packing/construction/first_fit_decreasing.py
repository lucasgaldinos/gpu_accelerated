"""
First Fit Decreasing (FFD) bin packing algorithm.

This module implements the First Fit Decreasing strategy for bin packing,
which sorts items in descending order and places each item in the first bin
that has sufficient remaining capacity.

Academic Reference:
------------------
Simchi-Levi, D., Chen, X., & Bramel, J. (2005). "The logic of logistics:
Theory, algorithms, and applications for logistics and supply chain management",
Springer.

Algorithm:
----------
1. Sort items by size in descending order (largest first)
2. For each item:
   - Try to place in first bin with enough remaining space
   - If no bin fits, create a new bin

Time Complexity: O(n log n)
- Sorting: O(n log n)
- Packing: O(n × k) where k = number of bins ≤ n
- Total: O(n log n) dominates

Approximation Guarantee:
-----------------------
FFD uses at most (11/9)OPT + 6/9 bins, where OPT is the optimal number of bins.

For most practical instances, FFD performs much better than this worst-case bound.

Example:
--------
    >>> import numpy as np
    >>> from src.algorithms.bin_packing.construction.first_fit_decreasing import FirstFitDecreasing
    >>>
    >>> # Customer demands (CVRP context)
    >>> demands = np.array([20, 30, 25, 40, 35, 15])
    >>> capacity = 100
    >>>
    >>> ffd = FirstFitDecreasing()
    >>> bins = ffd.pack(demands, capacity)
    >>> # bins = [[3, 4, 2], [1, 0, 5]]
    >>> # Bin 1: items[3]=40, items[4]=35, items[2]=25 → load=100
    >>> # Bin 2: items[1]=30, items[0]=20, items[5]=15 → load=65
    >>>
    >>> print(f"{ffd.get_name()} uses {len(bins)} bins")
    First Fit Decreasing uses 2 bins
"""

from typing import List
import numpy as np
from numpy.typing import NDArray


class FirstFitDecreasing:
    """
    First Fit Decreasing bin packing strategy.

    Sorts items in descending order by size, then applies First Fit heuristic:
    place each item in the first bin with sufficient remaining capacity.

    **Algorithm Pseudocode:**

    ```
    Algorithm: FirstFitDecreasing
    Input: items[] with demands/sizes, capacity C
    Output: bins[] where bins[i] = list of item indices in bin i

    1:  # Create (size, original_index) pairs
    2:  indexed_items ← [(items[i], i) for i in 0 to n-1]
    3:
    4:  # Sort by size descending (largest first)
    5:  sorted_items ← sort(indexed_items, key=size, reverse=True)
    6:
    7:  bins ← []              # List of bins
    8:  bin_loads ← []         # Remaining capacity for each bin
    9:
    10: for (size, original_idx) in sorted_items do
    11:     placed ← false
    12:
    13:     # Try to place in first bin with enough space
    14:     for i ← 0 to |bins|-1 do
    15:         if size ≤ bin_loads[i] then
    16:             bins[i].append(original_idx)
    17:             bin_loads[i] ← bin_loads[i] - size
    18:             placed ← true
    19:             break  # First fit: take first available
    20:
    21:     # If no bin fits, create new bin
    22:     if not placed then
    23:         bins.append([original_idx])
    24:         bin_loads.append(C - size)
    25:
    26: return bins
    ```

    Time Complexity:
        - Sorting: O(n log n)
        - Packing loop: O(n × k) where k ≤ n bins
        - Total: O(n log n) for sort + O(n²) worst case for packing
        - Typical: O(n log n) when k << n (few bins needed)

    Space Complexity:
        - O(n) for sorted array
        - O(k) for bin tracking where k ≤ n

    Attributes:
        _name: Strategy identifier

    Methods:
        pack: Assign items to bins using FFD
        get_name: Return "First Fit Decreasing"
        uses_sorting: Return True (FFD sorts items)

    Example - Basic Usage:
        >>> demands = np.array([45, 30, 25, 20, 15])
        >>> ffd = FirstFitDecreasing()
        >>> bins = ffd.pack(demands, capacity=100)
        >>> bins  # [[0, 1, 2], [3, 4]]
        >>> # Sorted order: 45, 30, 25, 20, 15
        >>> # Bin 1: 45 + 30 + 25 = 100 (full)
        >>> # Bin 2: 20 + 15 = 35

    Example - Comparison with Optimal:
        >>> # Worst-case instance for FFD
        >>> items = np.array([50, 50, 50, 33, 33, 33, 33, 33, 33])
        >>> ffd = FirstFitDecreasing()
        >>> bins = ffd.pack(items, capacity=100)
        >>> print(f"FFD: {len(bins)} bins")
        >>> # FFD might use 6 bins while optimal is 5
        >>> # Still within (11/9)OPT + 6/9 guarantee
    """

    def __init__(self):
        """Initialize First Fit Decreasing strategy."""
        self._name = "First Fit Decreasing"

    def pack(self, items: NDArray, capacity: float) -> List[List[int]]:
        """
        Pack items into bins using First Fit Decreasing strategy.

        Sorts items in descending order, then places each item in the first
        bin with sufficient remaining capacity.

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
            >>> ffd = FirstFitDecreasing()
            >>> bins = ffd.pack(demands, capacity=100)
            >>>
            >>> # Verify packing
            >>> for i, bin_indices in enumerate(bins, 1):
            ...     load = sum(demands[idx] for idx in bin_indices)
            ...     print(f"Bin {i}: {bin_indices} → load={load}/100")
            Bin 1: [3, 4, 2] → load=100/100
            Bin 2: [1, 0] → load=50/100
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

        # Initialize bins and remaining capacities
        bins: List[List[int]] = []
        bin_remaining: List[float] = []

        # Pack each item using First Fit
        for size, original_idx in sorted_items:
            placed = False

            # Try to place in first bin with enough space
            for i in range(len(bins)):
                if size <= bin_remaining[i]:
                    bins[i].append(original_idx)
                    bin_remaining[i] -= size
                    placed = True
                    break  # First fit: take first available

            # If no bin fits, create new bin
            if not placed:
                bins.append([original_idx])
                bin_remaining.append(capacity - size)

        return bins

    def get_name(self) -> str:
        """
        Return strategy name.

        Returns:
            "First Fit Decreasing"
        """
        return self._name

    def uses_sorting(self) -> bool:
        """
        Indicate whether this strategy sorts items.

        Returns:
            True - FFD sorts items in descending order
        """
        return True
