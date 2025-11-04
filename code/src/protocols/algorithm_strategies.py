"""
Algorithm strategy protocols for "Lego Blocks" compositional architecture.

This module defines protocol interfaces for interchangeable algorithm strategies:
- BinPackingStrategy: Capacity-based customer grouping algorithms (Class S - CPU only)
- TspConstructionStrategy: Tour construction heuristics (Class S - CPU only)
- TspImprovementStrategy: Tour improvement algorithms (Class P - CPU/GPU parallelizable)
- ClusteringStrategy: Spatial clustering algorithms

These protocols enable runtime algorithm selection via dependency injection,
supporting the compositional "Lego Blocks" design pattern.

**Class S vs Class P Separation (see flaws.md):**
- Class S (Sequential): CPU-only algorithms with inherent sequential dependencies
  Examples: Bin packing, nearest neighbor, Christofides
- Class P (Parallel): Algorithms with parallelizable components, benchmark-worthy
  Examples: Distance matrix computation, 2-opt improvement, clustering

Design Pattern References:
    - Strategy Pattern (GoF Design Patterns)
    - Dependency Injection (Fowler, 2004)
    - Protocol-Based Programming (PEP 544)

Example Usage:
    >>> # Mix and match algorithms
    >>> from src.protocols import ProblemContext
    >>> context = ProblemContext(problem, xp=cp)  # GPU context
    >>> 
    >>> solver = lego_cvrp_solver(
    ...     context,
    ...     bin_packing_strategy=FFDStrategy(),  # Class S - always CPU
    ...     tsp_strategy=NearestNeighborStrategy(),  # Class S - uses context.get_cpu_distances()
    ...     improvement_strategy=TwoOptGPU(),  # Class P - uses context.distances (GPU)
    ... )

See Also:
    - code/src/algorithms/strategies/bin_packing_strategies.py
    - code/src/algorithms/strategies/tsp_strategies.py
    - code/src/algorithms/compositional_cvrp_solver.py
    - code/src/protocols/problem_context.py
"""

from typing import Protocol, List, TYPE_CHECKING
import numpy as np
from .backend import BackendModule

if TYPE_CHECKING:
    from .problem_context import ProblemContext


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
    Protocol for TSP tour construction heuristics (Class S - CPU only).

    **Architectural Classification: Class S (Sequential)**
    These algorithms are inherently sequential with step k+1 depending on step k.
    They run on CPU regardless of ProblemContext backend. When context is on GPU,
    strategies use context.get_cpu_distances() for explicit data transfer.

    This is acceptable because:
    1. Sequential algorithms cannot leverage GPU parallelism
    2. Forcing them to run with GPU kernel calls creates massive overhead
    3. The single transfer is cheaper than k × (compute + transfer) anti-pattern

    Protocol Requirements:
        - Accept ProblemContext and customer indices
        - Return tour as ordered list of customer indices
        - Tour must visit each customer exactly once
        - Tour implicitly returns to start (depot)
        - Use context.get_cpu_distances() for CPU-based computation

    Design Rationale:
        ProblemContext eliminates k × O(m²) redundant distance computations
        (where k = number of routes, m = avg route size). Distance matrix is
        computed ONCE during context creation, then cached.

    Implementations:
        - NearestNeighborStrategy: O(n²) greedy construction
        - ChristofidesStrategy: 1.5-approximation for metric TSP
        - RandomStrategy: Random permutation (baseline)
        - SweepStrategy: Angular sorting from depot

    Example:
        >>> from src.protocols import ProblemContext
        >>> import numpy as np
        >>> 
        >>> context = ProblemContext(problem, xp=np)
        >>> strategy = NearestNeighborStrategy()
        >>> tour = strategy.build_tour(context, [1, 2, 3])
        >>> # tour = [0, 1, 3, 2, 0]  (includes depot return)
        >>> 
        >>> # Even with GPU context, strategy uses CPU
        >>> import cupy as cp
        >>> gpu_context = ProblemContext(problem, xp=cp)
        >>> tour = strategy.build_tour(gpu_context, [1, 2, 3])
        >>> # Internally calls gpu_context.get_cpu_distances()
    """

    def build_tour(
        self, context: "ProblemContext", customers: List[int]
    ) -> List[int]:
        """
        Construct TSP tour for given customers using context's cached distances.

        Args:
            context: ProblemContext with precomputed distance matrix
            customers: List of customer indices to visit (NOT including depot)

        Returns:
            Tour as ordered list of node indices [depot, c1, c2, ..., depot]

        Raises:
            ValueError: If customers list is empty
            ValueError: If depot (0) is in customers list

        Note:
            Implementations should use context.get_cpu_distances() to obtain
            the distance matrix as a NumPy array for CPU-based computation.
            This handles the backend transfer transparently.
        """
        ...


# ==============================================================================
# TSP IMPROVEMENT STRATEGY PROTOCOL
# ==============================================================================


class TspImprovementStrategy(Protocol):
    """
    Protocol for TSP tour improvement (local search) algorithms (Class P - Parallelizable).

    **Architectural Classification: Class P (Parallel)**
    These algorithms have parallelizable components that can benefit from GPU acceleration.
    They are the primary target for CPU vs GPU benchmarking.

    Unlike Class S (construction), improvement algorithms evaluate many candidate moves
    in parallel (e.g., all O(n²) 2-opt swaps), making them suitable for GPU acceleration.

    Protocol Requirements:
        - Accept ProblemContext and existing tour
        - Return improved tour with same structure (depot at start/end)
        - Tour must remain valid (visits each customer exactly once)
        - Should reduce or maintain tour cost (no worsening)
        - Use context.distances directly (respects backend)

    Design Rationale:
        Separating improvement from construction enables:
        - Fast construction + intensive improvement pipeline
        - GPU acceleration of improvement phase (parallel neighborhood search)
        - Iterative improvement (apply multiple times)
        - Benchmarking improvement impact

    Implementations:
        - TwoOptCPU: CPU-based 2-opt local search (sequential evaluation)
        - TwoOptGPU: GPU-accelerated 2-opt (Fujimoto 2011, parallel evaluation)
        - ThreeOpt: 3-opt local search (more expensive, better solutions)
        - LinKernighan: Variable-depth search (state-of-the-art)
        - SimulatedAnnealing: Metaheuristic with probabilistic acceptance

    Example:
        >>> from src.protocols import ProblemContext
        >>> import numpy as np
        >>> 
        >>> # Construct initial tour
        >>> context = ProblemContext(problem, xp=np)
        >>> construction = NearestNeighborStrategy()
        >>> tour = construction.build_tour(context, [1, 2, 3, 4, 5])
        >>>
        >>> # Improve with CPU 2-opt
        >>> improvement = TwoOptCPU()
        >>> improved_tour = improvement.improve_tour(context, tour)
        >>>
        >>> # Or use GPU for larger problems
        >>> import cupy as cp
        >>> gpu_context = ProblemContext(problem, xp=cp)
        >>> gpu_improvement = TwoOptGPU()
        >>> gpu_improved = gpu_improvement.improve_tour(gpu_context, tour)

    GPU Acceleration Note:
        GPU implementations (e.g., TwoOptGPU) should:
        - Use CuPy RawKernel for custom CUDA code
        - Exploit parallelism in neighborhood evaluation
        - Keep data on device (context.distances stays in VRAM)
        - Handle synchronization correctly
    """

    def improve_tour(
        self, context: "ProblemContext", tour: List[int]
    ) -> List[int]:
        """
        Improve TSP tour using local search with context's cached distances.

        Args:
            context: ProblemContext with precomputed distance matrix on target backend
            tour: Current tour [depot, c1, c2, ..., ck, depot]

        Returns:
            Improved tour with same structure (same customers, better or equal cost)

        Raises:
            ValueError: If tour is invalid (missing depot, duplicate customers)
            ValueError: If tour is empty or has fewer than 3 nodes

        Note:
            Implementations access context.distances directly, which is on the
            backend specified during context creation (NumPy for CPU, CuPy for GPU).
            This eliminates redundant transfers.
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
