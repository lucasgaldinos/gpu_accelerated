"""
Tour evaluation utilities for TSP and ATSP.

This module provides backend-aware functions for computing tour costs
and other tour quality metrics.
"""

import numpy as np
from typing import Any

from ...data_models.problem import Problem
from ...protocols.backend import BackendModule


def compute_tour_cost(problem: Problem, tour: Any, xp: BackendModule = np) -> float:
    """
    Calculate total cost of a TSP/ATSP tour including return to start.

    Computes the sum of all edge costs in the tour:
        cost = Σ D[tour[i], tour[i+1]] for i ∈ {0, ..., n-2}
             + D[tour[n-1], tour[0]]  (return edge)

    This function is backend-aware and works with both NumPy (CPU) and
    CuPy (GPU) arrays.

    Parameters
    ----------
    problem : Problem
        Problem instance with distance matrix.
        Must have problem.distances as (n, n) array.
    tour : array-like, shape (n,)
        Tour as array of node indices in visit order.
        Can be numpy.ndarray or cupy.ndarray depending on backend.
    xp : BackendModule, optional
        Array library to use (numpy or cupy). Default: numpy.

    Returns
    -------
    cost : float
        Total tour distance (sum of all edges including return to start).
        Returned as Python float for consistency across backends.

    Raises
    ------
    ValueError
        If problem.distances is None
    ValueError
        If tour length doesn't match problem dimension

    Notes
    -----
    Tour Cost Formula:
        For a tour τ = [τ₀, τ₁, ..., τₙ₋₁]:

        cost(τ) = Σᵢ₌₀ⁿ⁻² D[τᵢ, τᵢ₊₁] + D[τₙ₋₁, τ₀]

        where D is the distance matrix and n = |τ|.

    For ATSP (Asymmetric TSP), the distance matrix is not symmetric,
    so D[i,j] ≠ D[j,i]. This function handles both TSP and ATSP correctly.

    Examples
    --------
    >>> from src.loaders.database_loader import DatabaseLoader
    >>> from src.algorithms.TSP.construction_heuristics.nearest_neighbor import nearest_neighbor
    >>>
    >>> with DatabaseLoader() as loader:
    ...     problem = loader.load('burma14')
    >>>
    >>> # NumPy backend (CPU)
    >>> tour = nearest_neighbor(problem, start_node=0)
    >>> cost = compute_tour_cost(problem, tour)
    >>> cost > 0
    True

    >>> # CuPy backend (GPU) - if available
    >>> try:
    ...     import cupy as cp
    ...     tour_gpu = nearest_neighbor(problem, start_node=0, xp=cp)
    ...     cost_gpu = compute_tour_cost(problem, tour_gpu, xp=cp)
    ...     abs(cost - cost_gpu) < 1e-6  # Should be equal
    ... except ImportError:
    ...     True  # Skip if CuPy not available
    True

    See Also
    --------
    nearest_neighbor : Construct tour using greedy heuristic
    """
    # Validation
    if problem.distances is None:
        raise ValueError(
            f"Problem '{problem.name}' has no distance matrix. "
            f"Cannot compute tour cost without distances."
        )

    n = problem.dimension

    # Convert tour to backend array if needed
    tour_array = xp.asarray(tour) if hasattr(xp, "asarray") else xp.array(tour)

    if len(tour_array) != n:
        raise ValueError(
            f"Tour length {len(tour_array)} doesn't match problem dimension {n}"
        )

    # Convert distances to backend array for consistent operations
    distances = (
        xp.asarray(problem.distances)
        if hasattr(xp, "asarray")
        else xp.array(problem.distances)
    )

    # Compute edge costs: tour[i] -> tour[i+1] for i in 0..n-2
    # Using advanced indexing: distances[tour[:-1], tour[1:]]
    edge_costs = distances[tour_array[:-1], tour_array[1:]]

    # Add return edge: tour[n-1] -> tour[0]
    return_cost = distances[tour_array[-1], tour_array[0]]

    # Sum all costs and convert to Python float
    total_cost = xp.sum(edge_costs) + return_cost

    # Convert to Python float for consistent return type across backends
    if hasattr(total_cost, "get"):  # CuPy array
        return float(total_cost.get())
    else:  # NumPy scalar
        return float(total_cost)
