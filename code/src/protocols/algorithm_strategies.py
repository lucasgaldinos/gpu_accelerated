"""
Algorithm strategy protocols for "Lego Blocks" compositional architecture.

This module defines protocol interfaces for interchangeable algorithm strategies:
- BinPackingStrategy: Capacity-based customer grouping algorithms
- TspConstructionStrategy: Tour construction heuristics
- ClusteringStrategy: Spatial clustering algorithms

These protocols enable runtime algorithm selection via dependency injection,
supporting the compositional "Lego Blocks" design pattern.

Design Pattern References:
    - Strategy Pattern (GoF Design Patterns)
    - Dependency Injection (Fowler, 2004)
    - Protocol-Based Programming (PEP 544)

Example Usage:
    >>> # Mix and match algorithms
    >>> solver = lego_cvrp_solver(
    ...     locations, demands, capacity,
    ...     bin_packing_strategy=FFDStrategy(),  # Swap with BFDStrategy()
    ...     tsp_strategy=NearestNeighborStrategy(),  # Swap with ChristofidesStrategy()
    ...     xp=cp  # Backend flows through
    ... )

See Also:
    - code/src/algorithms/strategies/bin_packing_strategies.py
    - code/src/algorithms/strategies/tsp_strategies.py
    - code/src/algorithms/compositional_cvrp_solver.py
"""

from typing import Protocol, List
import numpy as np
from .backend import BackendModule


# ==============================================================================
# BIN PACKING STRATEGY PROTOCOL
# ==============================================================================


class BinPackingStrategy(Protocol):
    """
    Protocol for bin packing (capacity grouping) algorithms.

    Implementations must group items into capacity-constrained bins.
    This is Phase 1 of cluster-first, route-second CVRP approaches.

    Protocol Requirements:
        - Accept demands array, capacity constraint, and backend module
        - Return list of bins (each bin is list of item indices)
        - Respect capacity constraint: sum(demands[bin]) <= capacity
        - No assumptions about item ordering (unless documented)

    Implementations:
        - FFDStrategy: First Fit Decreasing (sorts by demand)
        - BFDStrategy: Best Fit Decreasing (sorts by demand)
        - CustomStrategy: User-defined bin packing logic

    Example:
        >>> strategy = FFDStrategy()
        >>> bins = strategy.pack(demands, capacity=100, xp=np)
        >>> # bins = [[0, 3, 5], [1, 4], [2]]  (customer indices per bin)
    """

    def pack(
        self, demands: np.ndarray, capacity: float, xp: BackendModule = np
    ) -> List[List[int]]:
        """
        Group items into capacity-constrained bins.

        Args:
            demands: (n,) array of item demands/weights
            capacity: Maximum bin capacity
            xp: Backend module (NumPy or CuPy)

        Returns:
            List of bins, where each bin is a list of item indices

        Raises:
            ValueError: If any demand exceeds capacity
        """
        ...


# ==============================================================================
# TSP CONSTRUCTION STRATEGY PROTOCOL
# ==============================================================================


class TspConstructionStrategy(Protocol):
    """
    Protocol for TSP tour construction heuristics.

    Implementations must build a valid TSP tour (Hamiltonian cycle) for
    a given set of customers using a precomputed distance matrix.

    Protocol Requirements:
        - Accept customer indices, distance matrix, backend module
        - Return tour as ordered list of customer indices
        - Tour must visit each customer exactly once
        - Tour implicitly returns to start (depot)
        - Distance matrix is precomputed ONCE by solver (avoids redundant work)

    Design Rationale:
        Passing a precomputed distance matrix eliminates k × O(m²) redundant
        distance computations (where k = number of routes, m = avg route size).
        This is critical for GPU performance to avoid CPU↔GPU transfers.

    Implementations:
        - NearestNeighborStrategy: O(n²) greedy construction
        - ChristofidesStrategy: 1.5-approximation for metric TSP
        - RandomStrategy: Random permutation (baseline)
        - SweepStrategy: Angular sorting from depot

    Example:
        >>> strategy = NearestNeighborStrategy()
        >>> # distances is precomputed n×n matrix
        >>> tour = strategy.build_tour([1, 2, 3], distances, xp=cp)
        >>> # tour = [0, 1, 3, 2, 0]  (includes depot return)
    """

    def build_tour(
        self, customers: List[int], distances: np.ndarray, xp: BackendModule = np
    ) -> List[int]:
        """
        Construct TSP tour for given customers using precomputed distances.

        Args:
            customers: List of customer indices to visit (NOT including depot)
            distances: (n, n) precomputed distance matrix for ALL nodes
            xp: Backend module (NumPy or CuPy)

        Returns:
            Tour as ordered list of node indices [depot, c1, c2, ..., depot]

        Raises:
            ValueError: If customers list is empty
            ValueError: If depot (0) is in customers list

        Note:
            The distance matrix should cover ALL nodes (depot + customers).
            Strategies extract submatrix using: distances[np.ix_(subset, subset)]
        """
        ...


# ==============================================================================
# TSP IMPROVEMENT STRATEGY PROTOCOL
# ==============================================================================


class TspImprovementStrategy(Protocol):
    """
    Protocol for TSP tour improvement (local search) algorithms.

    Implementations must improve an existing TSP tour using local search
    heuristics. These are applied AFTER construction to refine solution quality.

    Protocol Requirements:
        - Accept existing tour, distance matrix, backend module
        - Return improved tour with same structure (depot at start/end)
        - Tour must remain valid (visits each customer exactly once)
        - Distance matrix is precomputed (same as construction)
        - Should reduce or maintain tour cost (no worsening)

    Design Rationale:
        Separating improvement from construction enables:
        - Fast construction + intensive improvement pipeline
        - GPU acceleration of improvement phase (parallel neighborhood search)
        - Iterative improvement (apply multiple times)
        - Benchmarking improvement impact

    Implementations:
        - TwoOptCPU: CPU-based 2-opt local search (sequential)
        - TwoOptGPU: GPU-accelerated 2-opt (Fujimoto 2011)
        - ThreeOpt: 3-opt local search (more expensive, better solutions)
        - LinKernighan: Variable-depth search (state-of-the-art)
        - SimulatedAnnealing: Metaheuristic with probabilistic acceptance

    Example:
        >>> # Construct initial tour
        >>> construction = NearestNeighborStrategy()
        >>> tour = construction.build_tour([1, 2, 3, 4, 5], distances, xp=np)
        >>>
        >>> # Improve with 2-opt
        >>> improvement = TwoOptCPU()
        >>> improved_tour = improvement.improve_tour(tour, distances, xp=np)
        >>>
        >>> # Optionally chain improvements
        >>> improved_tour = TwoOptGPU().improve_tour(improved_tour, distances, xp=cp)

    GPU Acceleration Note:
        GPU implementations (e.g., TwoOptGPU) should:
        - Use CuPy RawKernel for custom CUDA code
        - Exploit parallelism in neighborhood evaluation
        - Keep data on device (avoid CPU↔GPU transfers)
        - Handle synchronization correctly
    """

    def improve_tour(
        self, tour: List[int], distances: np.ndarray, xp: BackendModule = np
    ) -> List[int]:
        """
        Improve TSP tour using local search.

        Args:
            tour: Current tour [depot, c1, c2, ..., ck, depot]
            distances: (n, n) precomputed distance matrix for ALL nodes
            xp: Backend module (NumPy or CuPy)

        Returns:
            Improved tour with same structure (same customers, better cost)

        Raises:
            ValueError: If tour is invalid (missing depot, duplicate customers)
            ValueError: If tour is empty or has fewer than 3 nodes

        Note:
            Implementations should:
            - Validate tour structure before improving
            - Preserve depot at start and end
            - Only return improvements (never worsen)
            - Support both NumPy and CuPy backends
            - Document time complexity and iteration limit

        Performance:
            Typical complexities:
            - 2-opt: O(n²) per iteration, O(n³) worst case
            - 3-opt: O(n³) per iteration
            - Lin-Kernighan: O(n²·⁵) average case

        Example:
            >>> tour = [0, 5, 3, 7, 2, 0]  # 5 customers
            >>> improved = strategy.improve_tour(tour, distances, xp=np)
            >>> cost(improved) <= cost(tour)  # Monotonic improvement
            True
        """
        ...


# ==============================================================================
# CLUSTERING STRATEGY PROTOCOL
# ==============================================================================


class ClusteringStrategy(Protocol):
    """
    Protocol for spatial clustering algorithms.

    Implementations must partition customers into spatial clusters based on
    geographic proximity. This is Phase 0 of spatial-aware CVRP approaches,
    applied before bin packing and routing.

    Protocol Requirements:
        - Accept location coordinates, demands, backend module
        - Return list of Cluster objects (customer indices + metadata)
        - Clusters should be spatially coherent (minimize inter-cluster distance)
        - May consider demand distribution for load balancing

    Implementations:
        - KMeansStrategy: k-means clustering (requires k parameter)
        - DBSCANStrategy: Density-based clustering (finds k automatically)
        - SweepStrategy: Angular partitioning from depot
        - GridStrategy: Spatial grid decomposition

    Example:
        >>> strategy = KMeansStrategy(k=5)
        >>> clusters = strategy.cluster(locations, demands, xp=np)
        >>> # clusters[0].customer_indices = [1, 3, 7, 9]
        >>> # clusters[0].centroid = array([10.5, 20.3])

    Note:
        This protocol is OPTIONAL in compositional solver. If not provided,
        all customers treated as single cluster.
    """

    def cluster(
        self, locations: np.ndarray, demands: np.ndarray, xp: BackendModule = np
    ) -> List["Cluster"]:
        """
        Partition customers into spatial clusters.

        Args:
            locations: (n, 2) array of customer coordinates
            demands: (n,) array of customer demands
            xp: Backend module (NumPy or CuPy)

        Returns:
            List of Cluster objects with customer indices and metadata

        Raises:
            ValueError: If locations and demands have different lengths
        """
        ...
