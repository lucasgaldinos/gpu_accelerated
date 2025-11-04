"""
Minimum Spanning Tree (MST) construction for TSP.

This module implements Prim's algorithm for computing a Minimum Spanning Tree,
which serves as a component in approximation algorithms like Christofides.

Algorithm Complexity: O(n² log n) with simple implementation
                      O(n²) with optimized version

References:
    - Prim, R. C. (1957): "Shortest Connection Networks"
    - Cormen et al. (2009): "Introduction to Algorithms" (3rd ed.), Ch. 23
"""

import numpy as np
import heapq
from typing import Any, List, Tuple

from ...data_models.problem import Problem
from ...protocols.backend import BackendModule


def minimum_spanning_tree(
    problem: Problem, xp: BackendModule = np
) -> Tuple[Any, float]:
    """
    Compute Minimum Spanning Tree using Prim's algorithm.

    Constructs an MST of the complete graph defined by the distance matrix.
    Returns the MST as an edge list and its total weight.

    Algorithm (Cormen et al. Style Pseudocode)
    -------------------------------------------
    MST-PRIM(G, w, r)
    ────────────────────────────────────────────
    Input:  G - complete graph on n vertices
            w - edge weight function (distance matrix)
            r - root vertex
    Output: T - MST as list of edges [(u,v), ...]

    1:  T ← ∅
    2:  key[v] ← ∞ for all v ∈ V
    3:  key[r] ← 0
    4:  parent[r] ← NIL
    5:  Q ← V                          ▷ Priority queue
    6:  while Q ≠ ∅ do
    7:      u ← EXTRACT-MIN(Q)
    8:      if parent[u] ≠ NIL then
    9:          T ← T ∪ {(parent[u], u)}
    10:     end if
    11:     for each v ∈ Adj[u] do
    12:         if v ∈ Q and w(u,v) < key[v] then
    13:             parent[v] ← u
    14:             key[v] ← w(u,v)
    15:         end if
    16:     end for
    17: end while
    18: return T
    ────────────────────────────────────────────

    Time Complexity: O(n²) where n = problem.dimension
        - For each of n vertices: extract-min from heap (O(log n))
        - Update keys for adjacent vertices: O(n) per vertex
        - Total: O(n² log n) with binary heap, O(n²) with array

    Space Complexity: O(n) for key, parent arrays and priority queue

    Parameters
    ----------
    problem : Problem
        Problem instance with populated distance matrix.
        Must have problem.distances as (n, n) array.
    xp : BackendModule, optional
        Array library (numpy or cupy) for backend abstraction.
        Default: numpy (CPU execution).
        Note: Priority queue operations remain in Python (heapq).

    Returns
    -------
    edges : list of tuple[(int, int)]
        MST edges as list of (u, v) pairs where u < v.
        Length: n-1 edges
    total_weight : float
        Total weight (sum of edge weights) of the MST.

    Raises
    ------
    ValueError
        If problem.distances is None
    TypeError
        If problem is not a Problem instance

    Notes
    -----
    MST Properties:
        - An MST of a complete graph on n vertices has exactly n-1 edges
        - Total weight is minimum among all spanning trees
        - For metric TSP, MST weight ≤ optimal tour length

    Use in TSP Approximation:
        - MST provides a lower bound on optimal tour cost
        - Christofides algorithm uses MST as first step
        - 2-approximation: tour from MST (via DFS) costs ≤ 2 * OPT

    Backend Support:
        The algorithm uses Python's heapq for priority queue operations,
        which remain on CPU regardless of backend. Array operations use
        the specified backend for consistency.

    Examples
    --------
    >>> from src.loaders.database_loader import DatabaseLoader
    >>>
    >>> with DatabaseLoader() as loader:
    ...     problem = loader.load('burma14')
    >>>
    >>> # Compute MST
    >>> edges, weight = minimum_spanning_tree(problem)
    >>> len(edges)  # Should be n-1
    13
    >>> weight > 0
    True

    >>> # MST weight is lower bound on tour cost
    >>> from src.algorithms.TSP.utils import compute_tour_cost
    >>> from src.algorithms.TSP.construction_heuristics import nearest_neighbor
    >>> tour = nearest_neighbor(problem)
    >>> tour_cost = compute_tour_cost(problem, tour)
    >>> weight <= tour_cost  # MST weight ≤ tour cost
    True

    See Also
    --------
    christofides : Uses MST as component in 3/2-approximation algorithm
    """
    # Validation
    if not isinstance(problem, Problem):
        raise TypeError(
            f"problem must be Problem instance, got {type(problem).__name__}"
        )

    if problem.distances is None:
        raise ValueError(
            f"Problem '{problem.name}' has no distance matrix. "
            f"Cannot compute MST without distances."
        )

    n = problem.dimension

    # Transfer distances to backend
    distances_array = xp.asarray(problem.distances)

    # Initialize Prim's algorithm
    # Note: key, parent, in_mst remain as Python lists/arrays on CPU
    # because heapq operations require CPU. Only distance lookups are vectorized.
    key = xp.full(n, xp.inf, dtype=xp.float32)
    parent = xp.full(n, -1, dtype=xp.int32)
    in_mst = xp.zeros(n, dtype=bool)

    # Start from vertex 0
    key[0] = 0.0
    parent[0] = -1

    # Priority queue: (key[v], v)
    # Note: heapq is CPU-only, so we maintain it in NumPy
    pq: List[Tuple[float, int]] = [(0.0, 0)]

    edges: List[Tuple[int, int]] = []
    total_weight = 0.0

    # Prim's main loop
    while pq:
        # Extract vertex with minimum key
        current_key, u = heapq.heappop(pq)

        # Skip if already processed (duplicate in heap)
        if bool(in_mst[u]):
            continue

        in_mst[u] = True

        # Add edge to MST (except for root)
        if int(parent[u]) != -1:
            edge = (min(int(parent[u]), u), max(int(parent[u]), u))  # Canonical form
            edges.append(edge)
            total_weight += current_key

        # Vectorized key update: Check all vertices not in MST
        dist_from_u = distances_array[u, :]  # Get all distances from u

        # Create update mask: nodes not in MST and with better distance
        update_mask = ~in_mst & (dist_from_u < key)

        # Update keys and parents where mask is True
        key = xp.where(update_mask, dist_from_u, key)
        parent = xp.where(update_mask, u, parent)

        # Add updated vertices to priority queue
        # Convert to CPU for heapq operations
        if xp != np:
            update_mask_cpu = xp.asnumpy(update_mask)
            key_cpu = xp.asnumpy(key)
        else:
            update_mask_cpu = update_mask
            key_cpu = key

        for v in range(n):
            if update_mask_cpu[v]:
                heapq.heappush(pq, (float(key_cpu[v]), v))

    return edges, total_weight
