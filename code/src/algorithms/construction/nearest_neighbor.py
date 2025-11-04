"""
Nearest Neighbor construction heuristic for TSP.

This module implements the classic greedy Nearest Neighbor algorithm,
which constructs a tour by iteratively visiting the closest unvisited node.

Algorithm Complexity: O(n²)
Solution Quality: Typically 20-30% above optimal for random Euclidean instances

References:
    - Rosenkrantz, Stearns, Lewis (1977): "An Analysis of Several Heuristics
      for the Traveling Salesman Problem"
    - Gutin, Punnen (2007): "The Traveling Salesman Problem and Its Variations"
"""

import numpy as np
from typing import Any, Optional

from ...data_models.problem import Problem
from ...protocols.backend import BackendModule


def nearest_neighbor(
    problem: Problem,
    start_node: int = 0,
    seed: Optional[int] = None,
    xp: BackendModule = np,
) -> Any:
    """
    Construct TSP tour using Nearest Neighbor greedy heuristic.

    Starting from a depot node, iteratively moves to the nearest unvisited
    node until all nodes are visited. Returns a permutation representing
    the tour order (does NOT include return to depot).

    Algorithm (Cormen et al. Style Pseudocode)
    -------------------------------------------
    NEAREST-NEIGHBOR(D, s)
    ────────────────────────────────────────────
    Input:  D - distance matrix (n × n)
            s - start node index
    Output: τ - tour permutation [τ₀, τ₁, ..., τₙ₋₁]

    1:  τ ← empty array of length n
    2:  τ[0] ← s
    3:  U ← {0, 1, ..., n-1} \ {s}        ▷ Unvisited nodes
    4:  current ← s
    5:  for i ← 1 to n-1 do
    6:      nearest ← argmin{D[current, u] : u ∈ U}
    7:      τ[i] ← nearest
    8:      U ← U \ {nearest}
    9:      current ← nearest
    10: end for
    11: return τ
    ────────────────────────────────────────────

    Time Complexity: O(n²) where n = problem.dimension
        - For each of n nodes, scans remaining unvisited nodes (average n/2)
        - Total: n * (n/2) = O(n²) distance lookups

    Space Complexity: O(n) for tour array and unvisited set

    Parameters
    ----------
    problem : Problem
        Problem instance with populated distance matrix.
        Must have problem.distances as (n, n) array.
    start_node : int, optional
        Index of starting node (0-indexed). Default is 0 (depot).
        Must satisfy 0 <= start_node < problem.dimension.
    seed : int, optional
        DEPRECATED: Random seed for tie-breaking is not supported in vectorized
        implementation. Included for API compatibility but has no effect.
        argmin always returns first occurrence for deterministic behavior.
    xp : BackendModule, optional
        Array library (numpy or cupy) for backend abstraction.
        Default: numpy (CPU execution).

    Returns
    -------
    tour : xp.ndarray, shape (n,), dtype=int32
        Tour as array of node indices in visit order.
        tour[0] = start_node
        tour[-1] = last node before returning to start
        Does NOT include return edge (start_node is implicit)

    Raises
    ------
    ValueError
        If problem.distances is None
    ValueError
        If start_node is out of bounds
    TypeError
        If problem is not a Problem instance

    Notes
    -----
    Solution Quality:
        - For random Euclidean instances: typically 20-30% above optimal
        - For structured instances: can be much worse (e.g., worst-case: O(log n) approximation)
        - Quality depends heavily on start_node choice

    Backend Support:
        This function uses vectorized operations for GPU compatibility.
        The distance matrix is transferred to the specified backend (GPU if CuPy),
        and all operations (masking, argmin) run on that device.

        Performance characteristics:
        - CPU (NumPy): Efficient for all problem sizes
        - GPU (CuPy): Overhead may dominate for small problems (n < 5000)
                       due to inherently sequential algorithm structure

        The algorithm remains O(n) in sequential steps, with O(1) vectorized
        operations per step, resulting in ~3n kernel launches total instead of
        O(n²) scalar accesses.

    Examples
    --------
    >>> from src.loaders.database_loader import DatabaseLoader
    >>> from src.algorithms.TSP.utils import compute_tour_cost
    >>>
    >>> with DatabaseLoader() as loader:
    ...     problem = loader.load('berlin52')
    >>>
    >>> # NumPy backend (CPU)
    >>> tour = nearest_neighbor(problem, start_node=0)
    >>> tour.shape
    (52,)
    >>> len(set(tour))  # All nodes visited exactly once
    52
    >>> tour[0]  # Starts at depot
    0

    >>> # Compute tour cost using utility function
    >>> cost = compute_tour_cost(problem, tour)
    >>> cost > 0
    True

    >>> # CuPy backend (GPU) - if available
    >>> try:
    ...     import cupy as cp
    ...     tour_gpu = nearest_neighbor(problem, start_node=0, xp=cp)
    ...     isinstance(tour_gpu, cp.ndarray)
    ... except ImportError:
    ...     True  # Skip if CuPy not available
    True

    See Also
    --------
    compute_tour_cost : Calculate total tour distance (in utils/tour_evaluation.py)
    """
    # Validation
    if not isinstance(problem, Problem):
        raise TypeError(
            f"problem must be Problem instance, got {type(problem).__name__}"
        )

    if problem.distances is None:
        raise ValueError(
            f"Problem '{problem.name}' has no distance matrix. "
            f"Cannot construct tour without distances."
        )

    n = problem.dimension

    if not (0 <= start_node < n):
        raise ValueError(
            f"start_node={start_node} out of bounds for problem with {n} nodes. "
            f"Must satisfy 0 <= start_node < {n}."
        )

    # Transfer distances to backend (GPU if using CuPy)
    # This ensures vectorized operations run on the same device as the backend
    distances = xp.asarray(problem.distances)

    # Initialize tour array using backend
    tour = xp.zeros(n, dtype=xp.int32)
    tour[0] = start_node

    # Use boolean mask for visited nodes (more efficient than set for vectorization)
    visited = xp.zeros(n, dtype=bool)
    visited[start_node] = True

    current_node = start_node

    # Greedy construction with vectorized operations
    for step in range(1, n):
        # Vectorized: Get all distances from current node (one kernel launch)
        dist_from_current = distances[current_node, :]

        # Mask visited nodes with infinity (one kernel launch)
        dist_from_current = xp.where(visited, xp.inf, dist_from_current)

        # Find nearest unvisited node (one kernel launch for reduction)
        nearest_node = int(xp.argmin(dist_from_current))

        # Note: Tie-breaking with seed parameter is not supported in vectorized version
        # as it would require transferring data to CPU. For deterministic behavior,
        # argmin consistently returns the first occurrence of the minimum value.

        # Update state
        tour[step] = nearest_node
        visited[nearest_node] = True
        current_node = nearest_node

    return tour
