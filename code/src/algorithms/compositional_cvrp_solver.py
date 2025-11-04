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
from ..protocols.problem_context import ProblemContext
from ..protocols.algorithm_strategies import (
    BinPackingStrategy,
    TspConstructionStrategy,
    TspImprovementStrategy,
    ClusteringStrategy,
)
from ..data_models.problem import Problem


# ==============================================================================
# MAIN COMPOSITIONAL SOLVER
# ==============================================================================


def lego_cvrp_solver(
    problem: Problem,
    bin_packing_strategy: BinPackingStrategy,
    tsp_strategy: TspConstructionStrategy,
    clustering_strategy: Optional[ClusteringStrategy] = None,
    improvement_strategy: Optional["TspImprovementStrategy"] = None,
    xp: BackendModule = np,
) -> List[List[int]]:
    """
    Solve CVRP via compositional "Lego Blocks" architecture with ProblemContext.

    **Key Performance Fix:**
    Creates ProblemContext ONCE at the start, precomputing the distance matrix.
    All strategies reuse this cached matrix, eliminating k × O(m²) redundant
    distance computations (where k = number of routes).

    Enables runtime algorithm selection by accepting strategy objects.
    Single backend (xp) propagates through all strategies for GPU/CPU consistency.

    Algorithm Pipeline:
        0. Create ProblemContext (precompute distance matrix ONCE)
        1. [If clustering_strategy provided] Partition customers into clusters
        2. For each cluster (or all customers if no clustering):
            a. Group customers into bins via bin_packing_strategy
            b. Build tour for each bin via tsp_strategy
            c. [If improvement_strategy] Improve tour
        3. Return list of routes

    Args:
        problem: Problem instance with coordinates/distances and demands
        bin_packing_strategy: Strategy for capacity grouping (e.g., FFDStrategy())
        tsp_strategy: Strategy for tour construction (e.g., ChristofidesStrategy())
        clustering_strategy: Optional spatial clustering (e.g., KMeansStrategy(k=5))
        improvement_strategy: Optional tour improvement (e.g., TwoOptCPU(), TwoOptGPU())
        xp: Backend module (NumPy for CPU, CuPy for GPU)

    Returns:
        List of routes, where each route is a list of customer indices
        including depot (e.g., [[0, 1, 3, 0], [0, 2, 4, 0]])

    Raises:
        ValueError: If demands exceed capacity or problem structure is invalid

    Time Complexity:
        - Without clustering: O(n²) distance matrix + O(n log n + k·m²)
        - With clustering: O(n²) + O(c·n log n + c·k·m²) where c = clusters

    Approximation Ratio:
        Depends on strategy choices:
        - FFD + Nearest Neighbor: No theoretical guarantee
        - BFD + Christofides: ≤ (11/9) * 1.5 ≈ 1.83 (heuristic bound)

    Example:
        >>> from src.loaders import DatabaseLoader
        >>> from src.algorithms.strategies import FFDStrategy, NearestNeighborStrategy
        >>> from src.algorithms.compositional_cvrp_solver import lego_cvrp_solver
        >>> 
        >>> # Load problem
        >>> with DatabaseLoader() as loader:
        ...     problem = loader.load('eil22')
        >>> 
        >>> # CPU with FFD + Nearest Neighbor
        >>> routes = lego_cvrp_solver(
        ...     problem,
        ...     bin_packing_strategy=FFDStrategy(),
        ...     tsp_strategy=NearestNeighborStrategy(),
        ...     xp=np
        ... )
        >>>
        >>> # GPU with BFD + Nearest Neighbor + 2-opt improvement
        >>> import cupy as cp
        >>> from src.algorithms.improvement import TwoOptGPU
        >>> routes = lego_cvrp_solver(
        ...     problem,
        ...     bin_packing_strategy=BFDStrategy(),
        ...     tsp_strategy=NearestNeighborStrategy(),
        ...     improvement_strategy=TwoOptGPU(),
        ...     xp=cp
        ... )

    Implementation Notes:
        - Distance matrix computed ONCE in ProblemContext creation
        - Backend (xp) must flow through all strategy method calls
        - Strategies access context.distances (no redundant computation)
        - GPU memory cleaned up automatically when context goes out of scope
    """
    # Step 0: Create ProblemContext (critical performance fix!)
    # This precomputes the distance matrix ONCE on the target backend,
    # eliminating k × O(m²) redundant computations where k = number of routes
    context = ProblemContext(problem, xp=xp)

    # Step 1: Validate inputs
    if problem.capacity is None or problem.demands is None:
        raise ValueError(
            f"Problem '{problem.name}' must have capacity and demands for CVRP"
        )

    capacity = problem.capacity
    demands = context.get_cpu_demands()  # Class S bin packing needs CPU data

    if np.any(demands > capacity):
        raise ValueError(
            f"Some demands exceed capacity: max demand = {np.max(demands)}, capacity = {capacity}"
        )

    # Step 2: Extract customers (exclude depot at index 0)
    n_total = problem.dimension
    all_customers = list(range(1, n_total))  # [1, 2, 3, ..., n-1]
    customer_demands = demands[1:]  # Exclude depot demand (should be 0)

    # Step 3: [OPTIONAL] Clustering - partition customers spatially
    if clustering_strategy is not None:
        # Get CPU coordinates for clustering (Class S algorithm)
        coordinates_cpu = context.get_cpu_coordinates()
        if coordinates_cpu is None:
            raise ValueError(
                "Clustering requires coordinates, but problem has EXPLICIT distances only"
            )
        
        # Cluster customers into spatial groups
        # clustering_strategy.cluster() returns List[List[int]] (customer indices per cluster)
        customer_clusters = clustering_strategy.cluster(
            customer_indices=all_customers, locations=coordinates_cpu, xp=np
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
        cluster_demands_list = [
            demands[customer_idx] for customer_idx in cluster_customers
        ]
        cluster_demands = np.array(cluster_demands_list)

        # Step 4b: Bin Packing - group customers into capacity-constrained bins
        # bin_packing_strategy.pack() returns List[List[int]]
        # Each bin is a list of indices into cluster_demands (NOT original customer indices)
        bins = bin_packing_strategy.pack(
            demands=cluster_demands, capacity=capacity, xp=np  # Class S - always CPU
        )

        # Step 4c: Build TSP tour for each bin
        for bin_indices in bins:
            # bin_indices are indices into cluster_customers
            # Example: bin_indices = [0, 2] means cluster_customers[0] and cluster_customers[2]

            # Map bin indices to original customer indices
            customers_in_bin = [cluster_customers[i] for i in bin_indices]

            # Step 4d: Call TSP strategy to build tour
            # Pass ProblemContext instead of distances and xp
            # tsp_strategy.build_tour() returns List[int] with depot at start and end
            # Example: [0, 5, 3, 7, 0] for customers [5, 3, 7]
            tour = tsp_strategy.build_tour(context, customers_in_bin)

            # Step 4e: [OPTIONAL] Improve tour with local search
            # If improvement_strategy provided, apply 2-opt or other improvement
            if improvement_strategy is not None:
                tour = improvement_strategy.improve_tour(context, tour)

            # Step 4f: Add tour to routes
            all_routes.append(tour)

    # Step 5: Clean up GPU memory if using CuPy
    if hasattr(xp, "get_default_memory_pool"):
        # CuPy cleanup
        xp.get_default_memory_pool().free_all_blocks()
    if hasattr(xp, "get_default_pinned_memory_pool"):
        xp.get_default_pinned_memory_pool().free_all_blocks()

    # Step 6: Return all routes
    return all_routes


# ==============================================================================
# NOTE: Distance matrix computation is now handled by ProblemContext
# ==============================================================================
# The _compute_distance_matrix() helper function has been removed because
# ProblemContext now handles distance matrix precomputation in a more robust way:
# 1. Supports multiple edge types (EUC_2D, GEO, ATT, EXPLICIT, etc.)
# 2. Uses the proper distance functions from distances/pairwise.py
# 3. Caches the result to avoid redundant computation
# 4. Handles backend-specific memory management
#
# Old anti-pattern: compute distance matrix k times (once per route)
# New pattern: compute once in ProblemContext, reuse via context.distances
