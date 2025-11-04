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

from typing import List, TYPE_CHECKING
import numpy as np
from ...protocols.backend import BackendModule

if TYPE_CHECKING:
    from ...protocols.problem_context import ProblemContext


# ==============================================================================
# NEAREST NEIGHBOR STRATEGY
# ==============================================================================


class NearestNeighborStrategy:
    """
    Nearest Neighbor TSP construction strategy (Class S - CPU only).

    Starts at depot (customer 0), iteratively selects the nearest unvisited
    customer, returns to depot at the end.

    **Architectural Classification: Class S (Sequential)**
    This algorithm is inherently sequential - each step depends on the previous.
    It always runs on CPU, even when ProblemContext is on GPU. Uses
    context.get_cpu_distances() for explicit data transfer when needed.

    Time Complexity: O(n²) - n iterations, each O(n) distance comparisons
    Approximation Ratio: No worst-case guarantee (can be arbitrarily bad)

    Practical Advantages:
        - Very fast (CPU-friendly sequential algorithm)
        - Produces reasonable tours in practice
        - Baseline for local search improvement

    Attributes:
        None (stateless wrapper)

    Methods:
        build_tour: Construct TSP tour via nearest neighbor heuristic

    Example:
        >>> from src.protocols import ProblemContext
        >>> from src.loaders import DatabaseLoader
        >>> import numpy as np
        >>> 
        >>> with DatabaseLoader() as loader:
        ...     problem = loader.load('berlin52')
        >>> context = ProblemContext(problem, xp=np)
        >>> strategy = NearestNeighborStrategy()
        >>> tour = strategy.build_tour(context, customers=[1, 2, 3])
        >>> # tour = [0, 1, 3, 2, 0]  (depot → 1 → 3 → 2 → depot)

    Implementation Note:
        This is an ADAPTER that wraps the existing nearest_neighbor() function
        from algorithms.construction.nearest_neighbor.

        The wrapper:
        1. Extracts CPU distance submatrix from context for given customers
        2. Creates temporary Problem instance
        3. Calls nearest_neighbor(problem, xp=np) on CPU
        4. Maps tour indices back to original customer indices
        5. Prepends depot (0) and appends depot return
    """

    def build_tour(
        self, context: "ProblemContext", customers: List[int]
    ) -> List[int]:
        """
        Build nearest neighbor tour for subset of customers.

        Args:
            context: ProblemContext with precomputed distance matrix
            customers: List of customer indices (excluding depot)

        Returns:
            Tour visiting depot and customers: [0, c1, c2, ..., ck, 0]

        Example:
            >>> context = ProblemContext(problem, xp=np)
            >>> strategy = NearestNeighborStrategy()
            >>> tour = strategy.build_tour(context, [1, 2, 3])
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

        # Get CPU distances from context (handles GPU→CPU transfer if needed)
        distances_cpu = context.get_cpu_distances()

        # Create subset indices: [depot, customer1, customer2, ...]
        subset_indices = [0] + customers  # Depot always first
        n_subset = len(subset_indices)

        # Extract distance submatrix for this subset
        # Use NumPy for indexing since we're on CPU
        distances_subset = distances_cpu[np.ix_(subset_indices, subset_indices)]

        # Create temporary Problem instance for subset
        temp_problem = Problem(
            name="temp_subset",
            dimension=n_subset,
            problem_type="TSP",
            edge_type="EXPLICIT",  # Use explicit distances, not coordinates
            coordinates=None,  # Not needed when using explicit distances
            distances=distances_subset,
            capacity=None,
            demands=None,
        )

        # Call nearest_neighbor on CPU (Class S algorithm)
        tour_subset = nearest_neighbor(temp_problem, start_node=0, xp=np)

        # Convert to Python list and map back to original indices
        tour_subset_list = [int(idx) for idx in tour_subset]
        tour_original = [subset_indices[idx] for idx in tour_subset_list]

        # Add depot return (nearest_neighbor doesn't include return edge)
        tour_original.append(0)

        return tour_original


# ==============================================================================
# CHRISTOFIDES STRATEGY
# ==============================================================================


class ChristofidesStrategy:
    """
    Christofides approximation for TSP subset construction (Class S - CPU only).

    Wrapper for the Christofides-Serdyukov algorithm that constructs a tour
    for a subset of customers extracted from a larger problem instance. This
    strategy provides a 3/2-approximation guarantee for metric TSP.

    **Architectural Classification: Class S (Sequential)**
    This algorithm uses sequential matching and MST computations that are
    CPU-bound. Always runs on CPU via context.get_cpu_distances().

    The wrapper:
    1. Extracts a subproblem with depot + selected customers
    2. Gets CPU distances from context
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
        self, context: "ProblemContext", customers: List[int]
    ) -> List[int]:
        """
        Build a TSP tour for a subset of customers using Christofides.

        Parameters
        ----------
        context : ProblemContext
            Problem context with precomputed distance matrix
        customers : List[int]
            Indices of customers to visit (excluding depot 0).
            Must be non-empty and not contain depot.

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
        >>> from src.protocols import ProblemContext
        >>> context = ProblemContext(problem, xp=np)
        >>> strategy = ChristofidesStrategy()
        >>> customers = [1, 2, 3]  # Customers to visit
        >>> tour = strategy.build_tour(context, customers)
        >>> tour[0] == 0 and tour[-1] == 0  # Starts and ends at depot
        True
        >>> set(tour[1:-1]) == {1, 2, 3}  # Visits all customers
        True

        Notes
        -----
        - Uses precomputed distances from context (no recomputation)
        - Always runs on CPU (Class S algorithm)
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

        # Get CPU distances from context (handles GPU→CPU transfer if needed)
        distances_cpu = context.get_cpu_distances()

        # Step 1: Create subset indices (depot + customers)
        subset_indices = [0] + customers

        # Step 2: Extract distance submatrix for this subset
        # Use NumPy for indexing since we're on CPU (Class S)
        distances_subset = distances_cpu[np.ix_(subset_indices, subset_indices)]

        # Step 3: Create temporary Problem instance for subset
        from ...data_models.problem import Problem

        temp_problem = Problem(
            name=f"Subset-{len(customers)}",
            dimension=len(subset_indices),
            problem_type="TSP",
            edge_type="EXPLICIT",  # Use explicit distances, not coordinates
            coordinates=None,  # Not needed when using explicit distances
            distances=distances_subset,
            capacity=None,
            demands=None,
        )

        # Step 4: Call Christofides algorithm on CPU (Class S)
        # Returns: array of indices in subset space [0, i1, i2, ..., ik]
        # Does NOT include return to depot
        tour_subset = self._algorithm(temp_problem, xp=np)

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
