"""
Christofides algorithm for TSP.

This module implements the Christofides-Serdyukov approximation algorithm,
which guarantees a solution within 3/2 of optimal for metric TSP instances.

Algorithm Complexity: O(n³) due to minimum weight matching
Solution Quality: ≤ 1.5 * OPT for metric TSP

References:
    - Christofides, N. (1976): "Worst-Case Analysis of a New Heuristic for the TSP"
    - Serdyukov, A. I. (1978): Independent discovery
    - Williamson, D. P. (2019): "Network Flow Algorithms"
"""

import numpy as np
from typing import Any, List, Set, Dict, Tuple

from ...data_models.problem import Problem
from ...protocols.backend import BackendModule
from .minimum_spanning_tree import minimum_spanning_tree


def christofides(problem: Problem, xp: BackendModule = np) -> Any:
    """
    Construct TSP tour using Christofides approximation algorithm.

    Christofides algorithm is a 3/2-approximation for metric TSP. It combines
    a Minimum Spanning Tree with a minimum-weight perfect matching on odd-degree
    vertices to create an Eulerian graph, then extracts a Hamiltonian tour.

    Algorithm (Cormen et al. Style Pseudocode)
    -------------------------------------------
    CHRISTOFIDES(G, w)
    ────────────────────────────────────────────
    Input:  G - complete graph on n vertices
            w - metric edge weight function
    Output: τ - Hamiltonian tour

    1:  T ← MST-PRIM(G, w, 0)           ▷ Minimum spanning tree
    2:  O ← {v : degree(v) in T is odd} ▷ Odd-degree vertices
    3:  M ← MIN-WEIGHT-MATCHING(O, w)   ▷ Perfect matching on O
    4:  H ← T ∪ M                       ▷ Eulerian multigraph
    5:  C ← EULERIAN-CIRCUIT(H, 0)      ▷ Eulerian circuit
    6:  τ ← SHORTCUT(C)                 ▷ Remove duplicates
    7:  return τ
    ────────────────────────────────────────────

    Time Complexity: O(n³) where n = problem.dimension
        - MST computation: O(n²)
        - Find odd-degree vertices: O(n)
        - Minimum weight matching: O(n³) (dominating term)
        - Eulerian circuit: O(n)
        - Shortcutting: O(n)

    Space Complexity: O(n²) for matching computation

    Parameters
    ----------
    problem : Problem
        Problem instance with populated distance matrix.
        Must satisfy triangle inequality for approximation guarantee.
    xp : BackendModule, optional
        Array library (numpy or cupy) for backend abstraction.
        Default: numpy (CPU execution).
        Note: Matching computation currently CPU-only.

    Returns
    -------
    tour : xp.ndarray, shape (n,), dtype=int32
        Tour as array of node indices in visit order.
        Does NOT include return edge (start node is implicit).

    Raises
    ------
    ValueError
        If problem.distances is None
    TypeError
        If problem is not a Problem instance

    Warnings
    --------
    The approximation guarantee (cost ≤ 1.5 * OPT) only holds if the
    distance matrix satisfies the triangle inequality:
        d(i,k) ≤ d(i,j) + d(j,k) for all i,j,k

    Most TSPLIB instances satisfy this (EUC_2D, GEO, etc.), but ATSP
    instances may not.

    Notes
    -----
    Algorithm Steps:
        1. Compute MST of the graph (lower bound on OPT)
        2. Find vertices with odd degree in MST
        3. Find minimum-weight perfect matching on odd vertices
        4. Combine MST + matching = Eulerian graph
        5. Find Eulerian circuit (visits all edges exactly once)
        6. Shortcut to create Hamiltonian tour (visits each vertex once)

    Approximation Analysis:
        - MST weight ≤ OPT (removing one edge from tour gives spanning tree)
        - Matching weight ≤ OPT/2 (odd vertices can be paired via tour)
        - Total: MST + Matching ≤ OPT + OPT/2 = 3/2 * OPT
        - Shortcutting doesn't increase cost (triangle inequality)

    Implementation Status:
        **SIMPLIFIED VERSION**: This implementation uses a greedy matching
        heuristic instead of optimal minimum-weight perfect matching.
        - Greedy matching: O(n²) time
        - Approximation guarantee: Not strictly 3/2 (but close in practice)
        - Full optimal matching would require Edmond's blossom algorithm

    Examples
    --------
    >>> from src.loaders.database_loader import DatabaseLoader
    >>> from src.algorithms.TSP.utils import compute_tour_cost
    >>>
    >>> with DatabaseLoader() as loader:
    ...     problem = loader.load('berlin52')
    >>>
    >>> # Compute Christofides tour
    >>> tour = christofides(problem)
    >>> tour.shape
    (52,)
    >>>
    >>> # Compare with nearest neighbor
    >>> from src.algorithms.TSP.construction_heuristics import nearest_neighbor
    >>> nn_tour = nearest_neighbor(problem)
    >>>
    >>> chris_cost = compute_tour_cost(problem, tour)
    >>> nn_cost = compute_tour_cost(problem, nn_tour)
    >>> chris_cost <= nn_cost  # Christofides often better
    True

    See Also
    --------
    minimum_spanning_tree : First step of Christofides algorithm
    nearest_neighbor : Simpler O(n²) construction heuristic
    """
    # Validation
    if not isinstance(problem, Problem):
        raise TypeError(
            f"problem must be Problem instance, got {type(problem).__name__}"
        )

    if problem.distances is None:
        raise ValueError(
            f"Problem '{problem.name}' has no distance matrix. "
            f"Cannot run Christofides without distances."
        )

    n = problem.dimension
    distances = xp.asarray(problem.distances)

    # Step 1: Compute Minimum Spanning Tree
    mst_edges, mst_weight = minimum_spanning_tree(problem, xp)

    # Step 2: Find odd-degree vertices in MST
    degree = [0] * n
    for u, v in mst_edges:
        degree[u] += 1
        degree[v] += 1

    odd_vertices = [v for v in range(n) if degree[v] % 2 == 1]

    # Step 3: Minimum-weight perfect matching on odd vertices
    # SIMPLIFIED: Greedy matching (not optimal, but fast)
    matching_edges = _greedy_matching(odd_vertices, distances, xp)

    # Step 4: Combine MST and matching to form Eulerian multigraph
    all_edges = mst_edges + matching_edges

    # Step 5: Find Eulerian circuit
    eulerian_circuit = _find_eulerian_circuit(n, all_edges, start=0)

    # Step 6: Shortcut to create Hamiltonian tour
    tour_list = _shortcut_to_tour(eulerian_circuit)

    # Convert to backend array
    tour = xp.array(tour_list, dtype=xp.int32)

    return tour


def _greedy_matching(vertices: List[int], distances, xp) -> List[Tuple[int, int]]:
    """
    Greedy minimum-weight matching heuristic with vectorized distance lookups.

    This is NOT the optimal minimum-weight perfect matching, but a fast
    greedy approximation. Repeatedly pairs the two closest unmatched vertices.

    Parameters
    ----------
    vertices : list of int
        Vertices to match (must have even length)
    distances : array
        Distance matrix (NumPy or CuPy array)
    xp : BackendModule
        Array library (numpy or cupy)

    Returns
    -------
    edges : list of tuple[(int, int)]
        Matching edges
    """
    unmatched = set(vertices)
    edges = []

    while unmatched:
        # Convert to list for indexing
        unmatched_list = list(unmatched)
        k = len(unmatched_list)

        if k == 0:
            break

        # Vectorized: Extract distance submatrix for unmatched vertices
        idx = xp.array(unmatched_list)
        # Create meshgrid for all pairs
        i_idx = idx[:, None]  # Shape: (k, 1)
        j_idx = idx[None, :]  # Shape: (1, k)

        # Get all pairwise distances
        dist_sub = distances[i_idx, j_idx]  # Shape: (k, k)

        # Mask diagonal and lower triangle (only consider upper triangle)
        mask = xp.triu(xp.ones((k, k), dtype=bool), k=1)
        dist_sub = xp.where(mask, dist_sub, xp.inf)

        # Find minimum distance pair
        if xp == np:
            min_idx = dist_sub.argmin()
            i_min, j_min = divmod(int(min_idx), k)
        else:
            min_idx = int(xp.argmin(dist_sub))
            i_min, j_min = divmod(min_idx, k)

        # Get actual vertex indices
        u, v = unmatched_list[i_min], unmatched_list[j_min]

        # Add edge in canonical form
        edges.append((min(u, v), max(u, v)))

        # Remove matched vertices
        unmatched.remove(u)
        unmatched.remove(v)

    return edges


def _find_eulerian_circuit(
    n: int, edges: List[Tuple[int, int]], start: int = 0
) -> List[int]:
    """
    Find Eulerian circuit in multigraph using Hierholzer's algorithm.

    Parameters
    ----------
    n : int
        Number of vertices
    edges : list of tuple[(int, int)]
        Edge list (may contain duplicates for multigraph)
    start : int
        Starting vertex

    Returns
    -------
    circuit : list of int
        Eulerian circuit as sequence of vertices
    """
    # Build adjacency list
    adj: Dict[int, List[int]] = {v: [] for v in range(n)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # Hierholzer's algorithm
    circuit = []
    stack = [start]

    while stack:
        v = stack[-1]
        if adj[v]:
            u = adj[v].pop()
            adj[u].remove(v)  # Remove reverse edge
            stack.append(u)
        else:
            circuit.append(stack.pop())

    return circuit[::-1]  # Reverse to get correct order


def _shortcut_to_tour(circuit: List[int]) -> List[int]:
    """
    Convert Eulerian circuit to Hamiltonian tour by shortcutting.

    Removes duplicate vertices, keeping only first occurrence.

    Parameters
    ----------
    circuit : list of int
        Eulerian circuit (may have repeated vertices)

    Returns
    -------
    tour : list of int
        Hamiltonian tour (each vertex appears exactly once)
    """
    seen: Set[int] = set()
    tour = []

    for v in circuit:
        if v not in seen:
            tour.append(v)
            seen.add(v)

    return tour
