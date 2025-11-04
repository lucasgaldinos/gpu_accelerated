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


# ==============================================================================
# MAIN COMPOSITIONAL SOLVER
# ==============================================================================


def lego_cvrp_solver(
    locations: np.ndarray,
    demands: np.ndarray,
    capacity: float,
    bin_packing_strategy: BinPackingStrategy,
    tsp_strategy: TspConstructionStrategy,
    clustering_strategy: Optional[ClusteringStrategy] = None,
    improvement_strategy: Optional["TspImprovementStrategy"] = None,
    xp: BackendModule = np,
) -> List[List[int]]:
    """
    Solve CVRP via compositional "Lego Blocks" architecture.

    Enables runtime algorithm selection by accepting strategy objects.
    Single backend (xp) propagates through all strategies for GPU/CPU consistency.

    Algorithm Pipeline:
        1. [If clustering_strategy provided] Partition customers into clusters
        2. For each cluster (or all customers if no clustering):
            a. Group customers into bins via bin_packing_strategy
            b. Build tour for each bin via tsp_strategy
        3. Return list of routes

    Args:
        locations: (n, 2) array of customer coordinates (depot at index 0)
        demands: (n,) array of customer demands (depot demand = 0)
        capacity: Vehicle capacity constraint
        bin_packing_strategy: Strategy for capacity grouping (e.g., FFDStrategy())
        tsp_strategy: Strategy for tour construction (e.g., ChristofidesStrategy())
        clustering_strategy: Optional spatial clustering (e.g., KMeansStrategy(k=5))
        improvement_strategy: Optional tour improvement (e.g., TwoOptCPU(), TwoOptGPU())
        xp: Backend module (NumPy for CPU, CuPy for GPU)

    Returns:
        List of routes, where each route is a list of customer indices
        including depot (e.g., [[0, 1, 3, 0], [0, 2, 4, 0]])

    Raises:
        ValueError: If demands exceed capacity or locations/demands shape mismatch

    Time Complexity:
        - Without clustering: O(n log n + n²)
        - With clustering: O(k·n log n + k·n²) where k = number of clusters

    Approximation Ratio:
        Depends on strategy choices:
        - FFD + Nearest Neighbor: No theoretical guarantee
        - BFD + Christofides: ≤ (11/9) * 1.5 ≈ 1.83 (heuristic bound)

    Example:
        >>> # CPU with FFD + Christofides
        >>> routes = lego_cvrp_solver(
        ...     locations, demands, capacity=100,
        ...     bin_packing_strategy=FFDStrategy(),
        ...     tsp_strategy=ChristofidesStrategy(),
        ...     xp=np
        ... )
        >>>
        >>> # GPU with BFD + Nearest Neighbor + Clustering
        >>> routes = lego_cvrp_solver(
        ...     locations, demands, capacity=100,
        ...     bin_packing_strategy=BFDStrategy(),
        ...     tsp_strategy=NearestNeighborStrategy(),
        ...     clustering_strategy=KMeansStrategy(k=5),
        ...     xp=cp
        ... )

    Implementation Notes:
        - This is a SCAFFOLD with signature only (pass statement)
        - Actual implementation will:
          1. Validate inputs (locations shape, demands ≤ capacity)
          2. Call clustering_strategy.cluster() if provided
          3. For each cluster, call bin_packing_strategy.pack()
          4. For each bin, call tsp_strategy.build_tour()
          5. Combine tours into routes with depot returns
        - Backend (xp) must flow through all strategy method calls
        - Distance matrix computation reused across TSP calls (cache optimization)
    """
    # Step 1: Validate inputs
    if len(locations.shape) != 2 or locations.shape[1] != 2:
        raise ValueError(
            f"locations must be 2D array with shape (n, 2), got shape {locations.shape}"
        )

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

    # Step 2: Extract customers (exclude depot at index 0)
    n_total = len(locations)
    all_customers = list(range(1, n_total))  # [1, 2, 3, ..., n-1]
    customer_demands = demands[1:]  # Exclude depot demand (should be 0)

    # Step 2: Compute distance matrix ONCE (critical performance fix)
    # This eliminates k × O(m²) redundant distance computations
    # where k = number of routes, m = average route size
    #
    # For GPU: This keeps data on device, avoiding repeated CPU↔GPU transfers
    # For CPU: This exploits cache locality and SIMD vectorization
    #
    # Shape: (n, n) where n = total number of nodes (depot + customers)
    distances = _compute_distance_matrix(locations, xp)

    # Step 3: [OPTIONAL] Clustering - partition customers spatially
    if clustering_strategy is not None:
        # Cluster customers into spatial groups
        # clustering_strategy.cluster() returns List[List[int]] (customer indices per cluster)
        customer_clusters = clustering_strategy.cluster(
            customer_indices=all_customers, locations=locations, xp=xp
        )
    else:
        # No clustering: treat all customers as a single cluster
        customer_clusters = [all_customers]

    # Step 4: Process each cluster
    all_routes = []

    for cluster_customers in customer_clusters:
        if len(cluster_customers) == 0:
            # Skip empty clusters (shouldn't happen, but defensive)
            continue

        # Step 4a: Extract demands for this cluster
        # cluster_customers contains indices in [1, n-1] range
        # We need to map to demands array indices (which are also [1, n-1])
        cluster_demands_list = [
            demands[customer_idx] for customer_idx in cluster_customers
        ]
        cluster_demands = xp.array(cluster_demands_list)

        # Step 4b: Bin Packing - group customers into capacity-constrained bins
        # bin_packing_strategy.pack() returns List[List[int]]
        # Each bin is a list of indices into cluster_demands (NOT original customer indices)
        bins = bin_packing_strategy.pack(
            demands=cluster_demands, capacity=capacity, xp=xp
        )

        # Step 4c: Build TSP tour for each bin
        for bin_indices in bins:
            # bin_indices are indices into cluster_customers
            # Example: bin_indices = [0, 2] means cluster_customers[0] and cluster_customers[2]

            # Map bin indices to original customer indices
            customers_in_bin = [cluster_customers[i] for i in bin_indices]

            # Step 4d: Call TSP strategy to build tour
            # Pass precomputed distance matrix instead of locations
            # tsp_strategy.build_tour() returns List[int] with depot at start and end
            # Example: [0, 5, 3, 7, 0] for customers [5, 3, 7]
            tour = tsp_strategy.build_tour(
                customers=customers_in_bin, distances=distances, xp=xp
            )

            # Step 4e: [OPTIONAL] Improve tour with local search
            # If improvement_strategy provided, apply 2-opt or other improvement
            if improvement_strategy is not None:
                tour = improvement_strategy.improve_tour(tour, distances, xp)

            # Step 4f: Add tour to routes
            all_routes.append(tour)

    # Step 5: Return all routes
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
