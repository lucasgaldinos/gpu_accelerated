"""
TSP construction strategy implementations (Nearest Neighbor, Christofides).

This module provides wrapper classes that adapt existing TSP algorithms
to the TspConstructionStrategy protocol, enabling "Lego Blocks" composition.

Strategies:
    - NearestNeighborStrategy: O(n²) greedy tour construction
    - ChristofidesStrategy: 1.5-approximation for metric TSP

Design Pattern:
    These classes are ADAPTERS that wrap existing implementations in
    `algorithms.construction.nearest_neighbor` and `algorithms.construction.christofides`.
    They conform to the TspConstructionStrategy protocol for dependency injection.

Example Usage:
    >>> from algorithms.strategies.tsp_strategies import NearestNeighborStrategy
    >>> from algorithms.compositional_cvrp_solver import lego_cvrp_solver
    >>>
    >>> # Swap strategies at runtime
    >>> routes_nn = lego_cvrp_solver(..., tsp_strategy=NearestNeighborStrategy())
    >>> routes_ch = lego_cvrp_solver(..., tsp_strategy=ChristofidesStrategy())

Performance Characteristics:
    - Nearest Neighbor: O(n²) time, no approximation guarantee
    - Christofides: O(n³) time, 1.5-approximation for metric TSP

References:
    - Rosenkrantz et al. (1977): "Nearest Neighbor algorithm analysis"
    - Christofides (1976): "Worst-case analysis of TSP heuristic"

See Also:
    - protocols.algorithm_strategies.TspConstructionStrategy
    - algorithms.construction.nearest_neighbor
    - algorithms.construction.christofides
"""

from typing import List
import numpy as np
from ...protocols.backend import BackendModule


# ==============================================================================
# NEAREST NEIGHBOR STRATEGY
# ==============================================================================


class NearestNeighborStrategy:
    """
    Nearest Neighbor TSP construction strategy.

    Starts at depot (customer 0), iteratively selects the nearest unvisited
    customer, returns to depot at the end.

    Time Complexity: O(n²) - n iterations, each O(n) distance comparisons
    Approximation Ratio: No worst-case guarantee (can be arbitrarily bad)

    Practical Advantages:
        - Very fast (GPU-friendly with distance matrix)
        - Produces reasonable tours in practice
        - Baseline for local search improvement

    Attributes:
        None (stateless wrapper)

    Methods:
        build_tour: Construct TSP tour via nearest neighbor heuristic

    Example:
        >>> strategy = NearestNeighborStrategy()
        >>> tour = strategy.build_tour(
        ...     customers=[1, 2, 3],
        ...     locations=np.array([[0, 0], [1, 0], [0, 1], [1, 1]]),
        ...     xp=np
        ... )
        >>> # tour = [0, 1, 3, 2, 0]  (depot → 1 → 3 → 2 → depot)

    Implementation Note:
        This is an ADAPTER that wraps the existing nearest_neighbor() function
        from algorithms.construction.nearest_neighbor.

        The wrapper:
        1. Extracts distance submatrix for given customers
        2. Creates temporary Problem instance
        3. Calls nearest_neighbor(problem, xp=xp)
        4. Maps tour indices back to original customer indices
        5. Prepends depot (0) and appends depot return
    """

    def build_tour(
        self, customers: List[int], distances: np.ndarray, xp=np
    ) -> List[int]:
        """
        Build nearest neighbor tour for subset of customers.

        Args:
            customers: List of customer indices (excluding depot)
            distances: Precomputed distance matrix for ALL nodes
            xp: Backend module (NumPy or CuPy)

        Returns:
            Tour visiting depot and customers: [0, c1, c2, ..., ck, 0]

        Example:
            >>> distances = np.array([[...]])  # Full distance matrix
            >>> strategy = NearestNeighborStrategy()
            >>> tour = strategy.build_tour([1, 2, 3], distances)
            >>> tour
            [0, 1, 2, 3, 0]
        """
        from ..construction import nearest_neighbor
        from ...data_models.problem import Problem

        # Validation
        if len(customers) == 0:
            raise ValueError("Customers list cannot be empty")

        if 0 in customers:
            raise ValueError("Depot (index 0) should not be in customers list")

        # Create subset indices: [depot, customer1, customer2, ...]
        subset_indices = [0] + customers  # Depot always first
        n_subset = len(subset_indices)

        # Extract distance submatrix for this subset using ix_ (works with NumPy and CuPy)
        # This is the key optimization: reuse precomputed distances instead of recomputing
        distances_subset = distances[xp.ix_(subset_indices, subset_indices)]

        # Extract corresponding locations for Problem (if needed)
        # For now, we'll construct a minimal Problem with just distances
        # nearest_neighbor can work with distance matrix only

        # Create temporary Problem instance for subset
        temp_problem = Problem(
            name="temp_subset",
            dimension=n_subset,
            problem_type="TSP",
            edge_type="EXPLICIT",  # Use explicit distances, not coordinates
            coordinates=None,  # Not needed when using explicit distances
            distances=xp.asnumpy(distances_subset)
            if hasattr(xp, "asnumpy")
            else np.asarray(distances_subset),
        )

        # Call nearest_neighbor (returns tour of subset indices)
        tour_subset = nearest_neighbor(temp_problem, start_node=0, xp=xp)

        # Convert to Python list and map back to original indices
        tour_subset_list = (
            [int(idx) for idx in xp.asnumpy(tour_subset)]
            if hasattr(xp, "asnumpy")
            else [int(idx) for idx in tour_subset]
        )
        tour_original = [subset_indices[idx] for idx in tour_subset_list]

        # Add depot return (nearest_neighbor doesn't include return edge)
        tour_original.append(0)

        return tour_original


# ==============================================================================
# CHRISTOFIDES STRATEGY
# ==============================================================================


class ChristofidesStrategy:
    """
    Christofides approximation for TSP subset construction.

    Wrapper for the Christofides-Serdyukov algorithm that constructs a tour
    for a subset of customers extracted from a larger problem instance. This
    strategy provides a 3/2-approximation guarantee for metric TSP.

    The wrapper:
    1. Extracts a subproblem with depot + selected customers
    2. Computes distances for the subproblem
    3. Calls the Christofides algorithm
    4. Maps the resulting tour back to original customer indices

    Complexity
    ----------
    - Time: O(k³) where k = |customers| + 1 (includes depot)
    - Space: O(k²) for distance matrix and matching computation

    Algorithm
    ---------
    Christofides combines:
    - Minimum Spanning Tree (MST)
    - Minimum weight perfect matching on odd-degree vertices
    - Eulerian circuit extraction
    - Tour shortcutting (remove duplicates)

    See Also
    --------
    construction.christofides : The underlying algorithm implementation
    NearestNeighborStrategy : Alternative greedy construction heuristic
    """

    def __init__(self):
        """Initialize Christofides strategy wrapper."""
        from ..construction.christofides import christofides

        self._algorithm = christofides

    def build_tour(
        self, customers: List[int], distances: np.ndarray, xp: BackendModule = np
    ) -> List[int]:
        """
        Build a TSP tour for a subset of customers using Christofides.

        Parameters
        ----------
        customers : List[int]
            Indices of customers to visit (excluding depot 0).
            Must be non-empty and not contain depot.
        distances : np.ndarray, shape (n, n)
            Precomputed distance matrix for ALL nodes (depot + customers).
            Used to extract subset distances efficiently.
        xp : BackendModule, optional
            Array library (numpy or cupy) for computation.
            Default: numpy

        Returns
        -------
        tour : List[int]
            Tour as list of node indices [0, c1, c2, ..., ck, 0].
            Starts and ends at depot, visits all customers exactly once.

        Raises
        ------
        ValueError
            If customers list is empty or contains depot (0)

        Examples
        --------
        >>> strategy = ChristofidesStrategy()
        >>> distances = np.array([[...]])  # Full distance matrix
        >>> customers = [1, 2, 3]  # Customers to visit
        >>> tour = strategy.build_tour(customers, distances)
        >>> tour[0] == 0 and tour[-1] == 0  # Starts and ends at depot
        True
        >>> set(tour[1:-1]) == {1, 2, 3}  # Visits all customers
        True

        Notes
        -----
        - Uses precomputed distances (no recomputation)
        - Backend parameter `xp` flows to underlying algorithm
        - Matching computation is CPU-only (uses NumPy internally)
        - Returns depot at start AND end (full closed tour)
        """
        # Validation: ensure customers list is non-empty and doesn't contain depot
        if len(customers) == 0:
            raise ValueError("Customers list cannot be empty")
        if 0 in customers:
            raise ValueError(
                "Depot (node 0) should not be in customers list. "
                "Only customer indices should be provided."
            )

        # Step 1: Create subset indices (depot + customers)
        subset_indices = [0] + customers

        # Step 2: Extract distance submatrix for this subset
        # This is the key optimization: reuse precomputed distances
        distances_subset = distances[xp.ix_(subset_indices, subset_indices)]

        # Step 3: Create temporary Problem instance for subset
        from ...data_models.problem import Problem

        temp_problem = Problem(
            name=f"Subset-{len(customers)}",
            dimension=len(subset_indices),
            problem_type="TSP",
            edge_type="EXPLICIT",  # Use explicit distances, not coordinates
            coordinates=None,  # Not needed when using explicit distances
            distances=xp.asnumpy(distances_subset)
            if hasattr(xp, "asnumpy")
            else np.asarray(distances_subset),
        )

        # Step 4: Call Christofides algorithm on subset problem
        # Returns: array of indices in subset space [0, i1, i2, ..., ik]
        # Does NOT include return to depot
        tour_subset = self._algorithm(temp_problem, xp=xp)

        # Step 5: Map subset tour indices back to original customer indices
        # christofides returns ndarray, convert to list for indexing
        tour_subset_list = (
            tour_subset.tolist()
            if hasattr(tour_subset, "tolist")
            else list(tour_subset)
        )

        # Map: subset index → original customer index
        # subset_indices[0] = 0 (depot)
        # subset_indices[1] = customers[0], etc.
        tour_original = [subset_indices[idx] for idx in tour_subset_list]

        # Step 6: Add depot return (Christofides doesn't include return edge)
        tour_original.append(0)

        return tour_original


# ==============================================================================
# FUTURE STRATEGIES (Placeholder)
# ==============================================================================

# class SweepStrategy:
#     """Angular sweep TSP construction (polar sorting)."""
#     pass

# class RandomStrategy:
#     """Random permutation (baseline for benchmarks)."""
#     pass

# class SavingsStrategy:
#     """Clarke-Wright savings heuristic (integrates with CVRP)."""
#     pass
