"""
Compositional CVRP solver with "Lego Blocks" architecture.

This module implements the main composition function that enables runtime
algorithm selection via Strategy Pattern and Dependency Injection.

Key Features:
    - Mix and match algorithms: swap FFD ↔ BFD, NN ↔ Christofides
    - Backend propagation: single xp parameter flows through all strategies
    - Optional clustering: spatial decomposition before routing
    - Protocol-based: accepts any strategy conforming to protocols

Design Pattern:
    - Strategy Pattern: Algorithms as interchangeable objects
    - Dependency Injection: Strategies passed as parameters
    - Composition over Inheritance: Flexible algorithm combinations

Example Usage:
    >>> from algorithms.strategies.bin_packing_strategies import FFDStrategy
    >>> from algorithms.strategies.tsp_strategies import ChristofidesStrategy
    >>> from algorithms.compositional_cvrp_solver import lego_cvrp_solver
    >>>
    >>> # Mix and match algorithms
    >>> routes = lego_cvrp_solver(
    ...     locations=np.array([[0, 0], [1, 2], [3, 4], ...]),
    ...     demands=np.array([0, 10, 20, 15, ...]),
    ...     capacity=100,
    ...     bin_packing_strategy=FFDStrategy(),  # Swap with BFDStrategy()
    ...     tsp_strategy=ChristofidesStrategy(),  # Swap with NearestNeighborStrategy()
    ...     xp=cp  # GPU backend
    ... )
    >>>
    >>> # With optional clustering
    >>> routes = lego_cvrp_solver(
    ...     locations, demands, capacity,
    ...     clustering_strategy=KMeansStrategy(k=5),  # Spatial decomposition
    ...     bin_packing_strategy=BFDStrategy(),
    ...     tsp_strategy=NearestNeighborStrategy(),
    ...     xp=np  # CPU backend
    ... )

Algorithm Pipeline:
    1. [OPTIONAL] Clustering: Partition customers into spatial clusters
    2. Bin Packing: Group customers into capacity-constrained bins
    3. TSP Construction: Build tour for each bin
    4. Return: List of routes (each route is a tour)

Performance Characteristics:
    - Time: O(k·n log n + k·n²) where k = number of clusters
    - Space: O(n²) for distance matrices (GPU-friendly)
    - Approximation: Depends on strategy choices (e.g., FFD+Christofides ≈ 1.65 OPT)

References:
    - Gamma et al. (1994): "Design Patterns: Strategy Pattern"
    - Fowler (2004): "Inversion of Control Containers and Dependency Injection"
    - Toth & Vigo (2014): "Vehicle Routing: Cluster-first, Route-second"

See Also:
    - protocols.algorithm_strategies: Protocol definitions
    - algorithms.strategies.bin_packing_strategies: FFD, BFD
    - algorithms.strategies.tsp_strategies: Nearest Neighbor, Christofides
    - algorithms.strategies.clustering_strategies: K-Means, DBSCAN [Future]
"""

from typing import List, Optional
import numpy as np
from ..protocols.backend import BackendModule
from ..protocols.algorithm_strategies import (
    BinPackingStrategy,
    TspConstructionStrategy,
    TspImprovementStrategy,
    ClusteringStrategy,
)
from ..data_models.problem import Problem
from ..protocols.problem_context import ProblemContext


# ==============================================================================
# MAIN COMPOSITIONAL SOLVER
# ==============================================================================


def lego_cvrp_solver(
    locations: np.ndarray,
    demands: Optional[np.ndarray] = None,
    capacity: Optional[float] = None,
    bin_packing_strategy: Optional[BinPackingStrategy] = None,
    tsp_strategy: Optional[TspConstructionStrategy] = None,
    clustering_strategy: Optional[ClusteringStrategy] = None,
    improvement_strategy: Optional["TspImprovementStrategy"] = None,
    xp: BackendModule = np,
) -> List[List[int]]:
    """
    Solve TSP or CVRP via compositional "Lego Blocks" architecture.

    Enables runtime algorithm selection by accepting strategy objects.
    Single backend (xp) propagates through all strategies for GPU/CPU consistency.

    Problem Type Auto-Detection:
        - TSP Mode: If demands=None and capacity=None
        - CVRP Mode: If demands and capacity are provided

    Algorithm Pipeline:
        TSP Mode:
            1. Build single tour via tsp_strategy (default: NearestNeighbor)
            2. [Optional] Improve tour via improvement_strategy
            3. Return single-route solution

        CVRP Mode:
            1. [Optional] Cluster customers via clustering_strategy
            2. Group customers into bins via bin_packing_strategy (default: FFD)
            3. Build tour for each bin via tsp_strategy (default: NearestNeighbor)
            4. [Optional] Improve each tour via improvement_strategy
            5. Return multi-route solution

    Args:
        locations: (n, 2) array of customer coordinates (depot at index 0)
        demands: Optional (n,) array of customer demands. If None, TSP mode.
        capacity: Optional vehicle capacity. Required for CVRP mode.
        bin_packing_strategy: Optional strategy for capacity grouping.
            If None and CVRP mode, defaults to FFDStrategy().
            Ignored in TSP mode.
        tsp_strategy: Optional strategy for tour construction.
            If None, defaults to NearestNeighborStrategy().
        clustering_strategy: Optional spatial clustering (e.g., KMeansStrategy(k=5))
        improvement_strategy: Optional tour improvement (e.g., TwoOptGPU())
        xp: Backend module (NumPy for CPU, CuPy for GPU)

    Returns:
        List of routes, where each route is a list of customer indices
        including depot (e.g., [[0, 1, 3, 0], [0, 2, 4, 0]])

        TSP mode: Single route [[0, 1, 2, ..., n, 0]]
        CVRP mode: Multiple routes, one per vehicle

    Raises:
        ValueError: If CVRP mode but demands or capacity missing
        ValueError: If demands exceed capacity or locations/demands shape mismatch

    Time Complexity:
        - TSP mode: O(n²) with default NearestNeighbor
        - CVRP mode: O(n log n + k·n²) where k = number of bins

    Example:
        >>> # TSP with defaults (Nearest Neighbor on CPU)
        >>> routes = lego_cvrp_solver(locations)
        >>>
        >>> # TSP with custom strategy
        >>> routes = lego_cvrp_solver(
        ...     locations,
        ...     tsp_strategy=ChristofidesStrategy(),
        ...     xp=np
        ... )
        >>>
        >>> # CVRP with defaults (FFD + Nearest Neighbor)
        >>> routes = lego_cvrp_solver(
        ...     locations, demands, capacity=100
        ... )
        >>>
        >>> # CVRP with custom strategies (GPU-accelerated)
        >>> routes = lego_cvrp_solver(
        ...     locations, demands, capacity=100,
        ...     bin_packing_strategy=BFDStrategy(),
        ...     tsp_strategy=ChristofidesStrategy(),
        ...     improvement_strategy=TwoOptGPUStrategy(),
        ...     xp=cp  # GPU backend
        ... )
        >>>
        >>> # Pure improvement on existing tour
        >>> routes = lego_cvrp_solver(
        ...     locations,
        ...     improvement_strategy=GeneticAlgorithmStrategy(),
        ...     xp=cp
        ... )

    Implementation Notes:
        - Preset defaults applied automatically based on problem type
        - Backend (xp) flows through all strategy method calls
        - Distance matrix cached in ProblemContext (lazy computation)
        - Bin packing only used if CVRP mode (demands + capacity provided)
    """
    # Step 1: Auto-detect problem type and apply preset defaults
    is_cvrp = demands is not None and capacity is not None

    if is_cvrp:
        # CVRP mode: Apply preset bin packing if not provided
        if bin_packing_strategy is None:
            from .strategies.bin_packing_strategies import FFDStrategy

            bin_packing_strategy = FFDStrategy()
    else:
        # TSP mode: Bin packing not needed
        if bin_packing_strategy is not None:
            raise ValueError(
                "bin_packing_strategy provided but demands/capacity are None. "
                "For TSP mode, use: solver(locations, tsp_strategy=...). "
                "For CVRP mode, use: solver(locations, demands, capacity, ...)"
            )

    # Apply preset TSP strategy if not provided
    if tsp_strategy is None:
        from .strategies.tsp_strategies import NearestNeighborStrategy

        tsp_strategy = NearestNeighborStrategy()

    # Step 2: Convert inputs to target backend (if needed)
    # This allows passing NumPy arrays to GPU solver or vice versa
    if hasattr(locations, "__array_interface__"):  # NumPy array
        locations = xp.asarray(locations)
    if demands is not None and hasattr(demands, "__array_interface__"):
        demands = xp.asarray(demands)

    # Step 3: Validate inputs
    if len(locations.shape) != 2 or locations.shape[1] != 2:
        raise ValueError(
            f"locations must be 2D array with shape (n, 2), got shape {locations.shape}"
        )

    if is_cvrp:
        if len(demands.shape) != 1:
            raise ValueError(f"demands must be 1D array, got shape {demands.shape}")

        if locations.shape[0] != demands.shape[0]:
            raise ValueError(
                f"locations and demands length mismatch: {locations.shape[0]} vs {demands.shape[0]}"
            )

        if xp.any(demands > capacity):
            raise ValueError(
                f"Some demands exceed capacity: max demand = {xp.max(demands)}, capacity = {capacity}"
            )

    # Step 4: Create Problem and ProblemContext (Option B Architecture)
    # ProblemContext computes distance matrix ONCE and provides get_cpu_*() helpers
    # This eliminates the anti-pattern of repeated distance matrix computation
    # and explicit GPU→CPU conversions scattered across strategy implementations
    problem = Problem(
        name="synthetic",
        dimension=len(locations),
        problem_type="CVRP" if is_cvrp else "TSP",
        edge_type="EUC_2D",
        coordinates=locations,
        distances=None,
        capacity=int(capacity) if is_cvrp else None,
        demands=demands if is_cvrp else None,
    )
    context = ProblemContext(problem, xp)

    # Step 5: Extract customers (exclude depot at index 0)
    n_total = len(locations)
    all_customers = list(range(1, n_total))  # [1, 2, 3, ..., n-1]

    # Step 6: [OPTIONAL] Clustering - partition customers spatially
    if clustering_strategy is not None:
        # Cluster customers into spatial groups
        # clustering_strategy.cluster() returns List[List[int]] (customer indices per cluster)
        customer_clusters = clustering_strategy.cluster(
            customer_indices=all_customers, locations=locations, xp=xp
        )
    else:
        # No clustering: treat all customers as a single cluster
        customer_clusters = [all_customers]

    # Step 7: Process each cluster
    all_routes = []

    for cluster_customers in customer_clusters:
        if len(cluster_customers) == 0:
            # Skip empty clusters (shouldn't happen, but defensive)
            continue

        if is_cvrp:
            # CVRP Mode: Bin packing → TSP per bin
            # bin_packing_strategy.pack() uses context.get_cpu_demands() and context.capacity
            # Pass customer_indices for this cluster to enable flexible composition
            # Returns List[List[int]] where each bin contains customer indices
            bins = bin_packing_strategy.pack(context, cluster_customers)
        else:
            # TSP Mode: Single tour for all customers (no bin packing)
            bins = [cluster_customers]

        # Step 8: Build TSP tour for each bin
        for bin_customer_indices in bins:
            # bin_customer_indices are already in original problem space [1, n-1]
            # Example: [1, 5, 3] means customers 1, 5, 3 from the original problem

            # Step 8a: Call TSP strategy to build tour
            # tsp_strategy.build_tour(context, customers) uses context.get_cpu_distances()
            # Returns List[int] with depot at start and end
            # Example: [0, 1, 5, 3, 0] for customers [1, 5, 3]
            tour = tsp_strategy.build_tour(context, bin_customer_indices)

            # Step 8b: [OPTIONAL] Improve tour with local search
            # If improvement_strategy provided, apply 2-opt or other improvement
            if improvement_strategy is not None:
                # Improvement strategies accept (context, tour) for Class P operations
                tour = improvement_strategy.improve_tour(context, tour)

            # Step 8c: Add tour to routes
            all_routes.append(tour)

    # Step 9: Return all routes
    return all_routes


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def _compute_distance_matrix(locations: np.ndarray, xp) -> np.ndarray:
    """
    Compute pairwise Euclidean distance matrix.

    This function computes the distance matrix ONCE at the start of solving,
    eliminating redundant distance computations in TSP strategies.

    Args:
        locations: (n, 2) array of node coordinates
        xp: Backend module (NumPy or CuPy)

    Returns:
        (n, n) symmetric distance matrix

    Performance:
        - O(n²) computation, done once
        - Fully vectorized (SIMD on CPU, parallel on GPU)
        - Result stays on device (no transfers for CuPy)

    Example:
        >>> locations = np.array([[0, 0], [1, 0], [0, 1]])
        >>> distances = _compute_distance_matrix(locations, np)
        >>> distances[0, 1]  # Distance from node 0 to node 1
        1.0
    """
    # Broadcasting: (n, 1, 2) - (1, n, 2) → (n, n, 2)
    diff = locations[:, None, :] - locations[None, :, :]

    # Euclidean distance: sqrt(dx² + dy²)
    # Shape: (n, n)
    distances = xp.sqrt(xp.sum(diff**2, axis=2))

    return distances


# ==============================================================================
# DEPRECATED HELPER FUNCTIONS
# ==============================================================================

# def _validate_inputs(locations, demands, capacity):
#     """Validate input arrays and constraints."""
#     pass

# def _combine_routes(bins, tours):
#     """Combine bin assignments and tours into final routes."""
#     pass
