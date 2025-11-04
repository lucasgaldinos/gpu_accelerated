"""
Bin packing protocol for capacity-constrained item assignment.

This module defines the protocol interface for bin packing strategies that
assign items (customers) to bins (vehicles) while respecting capacity constraints.

Academic Context:
-----------------
Bin packing is a foundational problem in combinatorial optimization with direct
applications to vehicle routing. In the CVRP context:

1. **Items** = Customers with demands
2. **Bins** = Vehicles with capacity
3. **Goal** = Minimize number of vehicles needed

This is a SIMPLIFIED first step before routing optimization:
- Step 1: Bin packing (assign customers to vehicles) ← THIS MODULE
- Step 2: Route construction (TSP within each vehicle's customers)
- Step 3: Route improvement (metaheuristics like SA)

Key Difference from Split Methods:
----------------------------------
**Bin Packing (Simple):**
- Input: Unordered items with demands
- Output: Assignment to bins
- Ignores: Routing cost, customer sequence
- Complexity: O(n log n) for FFD/BFD

**Split Methods (Complex - Future):**
- Input: Ordered customer sequence (giant tour)
- Output: Route boundaries considering distances
- Considers: Routing cost, sequence preservation
- Complexity: O(n²) for DP split

Academic References:
-------------------
- **Simchi-Levi et al. (2005)**: "The logic of logistics"
  Chapter on bin packing algorithms (FF, BF, FFD, BFD)

- **Johnson (1973)**: "Near-optimal bin packing algorithms"
  Original analysis of FFD approximation ratio

- **Garey & Johnson (1979)**: "Computers and Intractability"
  NP-hardness proof and approximation theory

Approximation Guarantees:
-------------------------
- **First Fit Decreasing (FFD)**: Uses at most (11/9)OPT + 6/9 bins
- **Best Fit Decreasing (BFD)**: Uses at most (11/9)OPT + 6/9 bins
- Both have same worst-case bound, differ in average-case performance

Protocol Design:
---------------
All bin packing strategies implement this protocol to enable swappable
implementations. Strategies differ in item ordering and bin selection criteria.

Example Usage:
-------------
    >>> from src.protocols.bin_packing_protocol import BinPackingStrategy
    >>> from src.algorithms.bin_packing.construction.best_fit_decreasing import BestFitDecreasing
    >>>
    >>> # CVRP customer demands (depot has 0 demand)
    >>> demands = np.array([0, 20, 30, 25, 40, 35, 15])  # 6 customers + depot
    >>> capacity = 100
    >>>
    >>> # Apply bin packing
    >>> packer = BestFitDecreasing()
    >>> bins = packer.pack(demands[1:], capacity)  # Exclude depot demand
    >>> # bins = [[40, 35, 25], [30, 20, 15]]
    >>> # Bin 1: customers with demands 40+35+25=100 (full)
    >>> # Bin 2: customers with demands 30+20+15=65
    >>>
    >>> print(f"Number of vehicles needed: {len(bins)}")
    >>> for i, bin_items in enumerate(bins, 1):
    ...     load = sum(bin_items)
    ...     print(f"Vehicle {i}: load={load}/{capacity}, items={bin_items}")
    Number of vehicles needed: 2
    Vehicle 1: load=100/100, items=[40, 35, 25]
    Vehicle 2: load=65/100, items=[30, 20, 15]

Integration with CVRP:
---------------------
    >>> # After bin packing, solve TSP for each bin's customers
    >>> for bin_customers in bins:
    ...     # Extract coordinates for these customers
    ...     # Solve TSP to find best route through them
    ...     # Result: complete CVRP solution (vehicles + routes)
"""

from typing import Protocol, List
from numpy.typing import NDArray


class BinPackingStrategy(Protocol):
    """
    Protocol for bin packing strategies that assign items to capacity-constrained bins.

    A bin packing strategy takes a list of item sizes (demands) and assigns them
    to bins (vehicles) while respecting capacity constraints. The goal is typically
    to minimize the number of bins used.

    **Conceptual Pseudocode Framework:**

    ```
    Algorithm: Generic-BinPacking-Framework
    Input: items[] with sizes/demands, bin capacity C
    Output: bins[] where bins[i] = list of items in bin i

    1: # Optional: Sort items (FFD/BFD do this, FF/BF don't)
    2: sorted_items ← sort(items, descending) OR items (no sort)
    3:
    4: bins ← []  # List of bins, each bin is list of items
    5:
    6: for each item in sorted_items do
    7:     # Strategy-specific bin selection
    8:     selected_bin ← find_bin_using_strategy_criteria(bins, item)
    9:
    10:    if selected_bin exists then
    11:        Add item to selected_bin
    12:    else
    13:        Create new bin with item
    14:        Add new bin to bins
    15:
    16: return bins
    ```

    **Strategy-Specific Variations:**

    - **First Fit (FF)**: Select first bin with enough space (no sorting)
    - **Best Fit (BF)**: Select bin with least remaining space (no sorting)
    - **First Fit Decreasing (FFD)**: Sort descending, then First Fit
    - **Best Fit Decreasing (BFD)**: Sort descending, then Best Fit

    See `documentation/developer_guides/cvrp_split_strategies.md` for detailed
    pseudocode of BFD and FFD implementations.

    Performance Characteristics:
        Strategy | Sort | Selection    | Time        | Approx Ratio
        ---------|------|--------------|-------------|---------------
        FF       | No   | First fit    | O(n²)       | Poor
        BF       | No   | Best fit     | O(n log n)  | Better
        FFD      | Yes  | First fit    | O(n log n)  | 11/9 OPT + 6/9
        BFD      | Yes  | Best fit     | O(n log n)  | 11/9 OPT + 6/9

    Attributes (via methods):
        name: Strategy identifier (e.g., "First Fit Decreasing")
        uses_sorting: Whether strategy sorts items before packing

    Methods:
        pack: Assign items to bins respecting capacity
        get_name: Return strategy name
        uses_sorting: Return whether items are sorted

    Invariants:
        - All bins must respect capacity: sum(bin) <= capacity
        - All items must be assigned exactly once
        - Bins are non-empty (no empty bins in result)

    Example - Comparing Strategies:
        >>> demands = np.array([45, 30, 25, 20, 15, 10])
        >>> capacity = 100
        >>>
        >>> strategies = [FirstFitDecreasing(), BestFitDecreasing()]
        >>> for strategy in strategies:
        ...     bins = strategy.pack(demands, capacity)
        ...     print(f"{strategy.get_name()}: {len(bins)} bins")
        First Fit Decreasing: 2 bins  # [[45, 30, 25], [20, 15, 10]]
        Best Fit Decreasing: 2 bins   # [[45, 30, 25], [20, 15, 10]]
        # Both achieve same result for this instance

    Example - Worst Case for FFD:
        >>> # Items that trigger worst-case behavior
        >>> # FFD can use up to (11/9)OPT + 6/9 bins
        >>> items = [50, 50, 50, 50, 33, 33, 33, 33, 33, 33]
        >>> capacity = 100
        >>>
        >>> ffd = FirstFitDecreasing()
        >>> bins = ffd.pack(items, capacity)
        >>> print(f"FFD uses {len(bins)} bins")
        >>> # Optimal: 5 bins (each [50, 33, 17] or similar)
        >>> # FFD might use 6 bins due to greedy choices

    Notes:
        - Items are typically customer demands in CVRP context
        - Bin capacity is vehicle capacity
        - This is packing only - routing within bins is separate step
        - Decreasing strategies (FFD/BFD) generally perform better
        - Best Fit uses min-heap for O(n log n) efficiency

    See Also:
        - documentation/developer_guides/cvrp_split_strategies.md (BFD/FFD details)
        - Simchi-Levi et al. (2005) "The logic of logistics"
        - Johnson (1973) "Near-optimal bin packing algorithms"
    """

    def pack(self, items: NDArray, capacity: float) -> List[List[int]]:
        """
        Assign items to bins while respecting capacity constraints.

        Takes an array of item sizes (demands) and partitions them into bins
        (vehicles) such that no bin exceeds the capacity constraint. The goal
        is typically to minimize the number of bins used.

        Args:
            items: 1D NumPy array of item sizes/demands, shape (n,)
                Example: np.array([20, 30, 25, 40, 35, 15])
                Values should be positive and <= capacity

            capacity: Maximum capacity of each bin (vehicle capacity)
                Must be positive
                All items should fit: max(items) <= capacity

        Returns:
            bins: List of bins, where each bin is a list of item indices
                Example: [[3, 4, 2], [1, 0, 5]] means:
                    Bin 1: items[3], items[4], items[2] (indices from input)
                    Bin 2: items[1], items[0], items[5]
                Note: Returns item INDICES, not sizes

        Raises:
            ValueError: If any item size exceeds capacity
            ValueError: If capacity <= 0
            ValueError: If items array is empty

        Complexity:
            - First Fit: O(n²) worst case
            - Best Fit: O(n log n) with min-heap
            - FFD/BFD: O(n log n) sorting + packing

        Example - Basic Usage:
            >>> demands = np.array([20, 30, 25, 40, 35])
            >>> capacity = 100
            >>>
            >>> packer = BestFitDecreasing()
            >>> bins = packer.pack(demands, capacity)
            >>> bins  # [[3, 4, 2], [1, 0]]
            >>> # Bin 1: demands[3]=40, demands[4]=35, demands[2]=25 → load=100
            >>> # Bin 2: demands[1]=30, demands[0]=20 → load=50

        Example - Verifying Capacity:
            >>> for i, bin_indices in enumerate(bins, 1):
            ...     load = sum(demands[idx] for idx in bin_indices)
            ...     assert load <= capacity, f"Bin {i} exceeds capacity!"
            ...     print(f"Bin {i}: {bin_indices} → load={load}/{capacity}")
            Bin 1: [3, 4, 2] → load=100/100
            Bin 2: [1, 0] → load=50/100

        Example - CVRP Integration:
            >>> # After bin packing, map to customers
            >>> customer_ids = np.array([5, 2, 8, 3, 7])  # Customer IDs
            >>> bins = packer.pack(demands, capacity)
            >>>
            >>> vehicles = []
            >>> for bin_indices in bins:
            ...     # Get actual customer IDs for this vehicle
            ...     vehicle_customers = [customer_ids[i] for i in bin_indices]
            ...     vehicles.append(vehicle_customers)
            >>> vehicles  # [[3, 7, 8], [2, 5]] - customer IDs per vehicle

        Notes:
            - Returns item INDICES (0 to n-1), not item sizes
            - Caller must map indices back to customer IDs if needed
            - No empty bins in output (all bins contain at least one item)
            - Order within bins may vary by strategy
            - Total items assigned = len(items) (all items covered)
        """
        ...

    def get_name(self) -> str:
        """
        Return strategy name for identification and logging.

        Returns:
            Human-readable strategy name

        Examples:
            - "First Fit"
            - "Best Fit"
            - "First Fit Decreasing"
            - "Best Fit Decreasing"
        """
        ...

    def uses_sorting(self) -> bool:
        """
        Indicate whether strategy sorts items before packing.

        Returns:
            True if items are sorted (FFD, BFD)
            False if items are processed in original order (FF, BF)

        Notes:
            - Decreasing strategies (FFD, BFD) sort items largest-first
            - Sorting improves approximation guarantees
            - Non-sorting strategies preserve input order
        """
        ...
