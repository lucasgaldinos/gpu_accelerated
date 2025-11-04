"""
ProblemContext: Backend-Specific Problem Data Holder with Distance Matrix Caching.

⚠️ ARCHITECTURAL NOTE ⚠️
This module is placed in `protocols/` for organizational consistency with other
strategy protocols, but ProblemContext is NOT a Protocol (PEP 544) interface.
It is a concrete class that wraps the immutable Problem dataclass and adds
backend-specific cached computation of distance matrices.

The ProblemContext solves a critical performance anti-pattern identified in
flaws.md: sequential algorithms calling compute_distance_matrix() repeatedly
inside Python loops, causing O(n³) complexity instead of O(n²).

Design Philosophy:
- Single Responsibility: Holds all backend-specific problem data
- Immutability: Based on frozen Problem dataclass, computed data cached
- Performance: Distance matrix computed ONCE on target backend
- Class S vs Class P Separation: Provides helpers for both CPU-only and
  parallelizable algorithms

Example:
    >>> from src.data_models.problem import Problem
    >>> from src.protocols.problem_context import ProblemContext
    >>> import numpy as np
    >>> 
    >>> # Load problem
    >>> with DatabaseLoader() as loader:
    ...     problem = loader.load('berlin52')
    >>> 
    >>> # Create CPU context (Class S algorithms)
    >>> cpu_context = ProblemContext(problem, xp=np)
    >>> cpu_context.distances  # Computed once, cached
    >>> 
    >>> # Create GPU context (Class P algorithms)
    >>> import cupy as cp
    >>> gpu_context = ProblemContext(problem, xp=cp)
    >>> gpu_context.distances  # Computed once on GPU, stays in VRAM

References:
    - flaws.md: Documents the distance matrix recomputation anti-pattern
    - flaw_analysis.md: Explains Class S (sequential) vs Class P (parallel)
    - architectural-decisions-and-questions.md: ProblemContext design rationale
"""

import numpy as np
from typing import Optional

from ..data_models.problem import Problem
from ..protocols.backend import BackendModule
from ..distances.matrix import compute_distance_matrix


class ProblemContext:
    """
    Backend-specific problem data holder with cached distance matrix.

    This class wraps the immutable Problem dataclass and precomputes the
    distance matrix on the specified backend (NumPy or CuPy), caching it
    to avoid redundant O(n²) computations.

    **Key Performance Fix:**
    Before ProblemContext, TspConstructionStrategy.build_tour() was called
    k times (once per route), each time computing the distance matrix:
        - Total: k × O(m²) redundant work
        - For GPU: k × (CPU→GPU transfer + compute + GPU→CPU transfer)
        - Example: eil51 with k=5 routes = 17-82x slowdown

    After ProblemContext:
        - Distance matrix computed ONCE: O(N²) where N = total nodes
        - Cached on target backend (CPU or GPU)
        - All algorithms reuse the same cached matrix
        - No redundant transfers

    Attributes:
        xp: Backend module (NumPy or CuPy)
        problem: Original immutable Problem instance
        dimension: Number of nodes (problem.dimension)
        capacity: Vehicle capacity (CVRP only, None for TSP/ATSP)
        demands: Customer demands on target backend (xp.ndarray)
        distances: Cached distance matrix on target backend (xp.ndarray)
        coordinates: Coordinates on target backend (xp.ndarray or None)

    Example:
        >>> # Class S (sequential CPU algorithm)
        >>> context = ProblemContext(problem, xp=np)
        >>> tour = nearest_neighbor_strategy.construct(context, customers)
        >>> # No recomputation - uses context.distances

        >>> # Class P (parallel GPU algorithm)
        >>> context_gpu = ProblemContext(problem, xp=cp)
        >>> improved_tours = two_opt_gpu.improve_tours(tours, context_gpu)
        >>> # Distance matrix stays in VRAM, zero transfer overhead
    """

    def __init__(self, problem: Problem, xp: BackendModule):
        """
        Initialize ProblemContext and precompute distance matrix.

        Args:
            problem: Immutable Problem instance from database loader
            xp: Backend module (numpy or cupy) to use for computation

        Raises:
            ValueError: If problem has no coordinates or distances to
                compute distance matrix from
        """
        self.xp = xp
        self.problem = problem
        self.dimension = problem.dimension
        self.capacity = problem.capacity

        # Move demands to target backend
        if problem.demands is not None:
            self.demands = xp.asarray(problem.demands)
        else:
            self.demands = None

        # Compute or move distance matrix ONCE
        if problem.distances is not None:
            # EXPLICIT edge type - matrix already exists
            self.distances = xp.asarray(problem.distances)
            self.coordinates = (
                xp.asarray(problem.coordinates)
                if problem.coordinates is not None
                else None
            )
        elif problem.coordinates is not None:
            # Compute from coordinates on the target backend
            self.coordinates = xp.asarray(problem.coordinates)
            self.distances = compute_distance_matrix(
                self.coordinates, problem.edge_type, xp
            )
        else:
            raise ValueError(
                f"Problem '{problem.name}' has no distances or coordinates "
                "to compute distance matrix from."
            )

    def get_cpu_demands(self) -> Optional[np.ndarray]:
        """
        Helper for Class S (sequential) algorithms requiring CPU data.

        Performs explicit data transfer if context is on GPU. This is
        acknowledged and acceptable for Class S algorithms which are
        CPU-bound by design.

        Returns:
            Demands array as NumPy array on CPU, or None

        Example:
            >>> # GPU context used by Class P algorithm
            >>> gpu_context = ProblemContext(problem, xp=cp)
            >>> # But Class S bin packing needs CPU data
            >>> cpu_demands = gpu_context.get_cpu_demands()  # Explicit transfer
            >>> bins = ffd_strategy.pack(cpu_demands, capacity)
        """
        if self.demands is None:
            return None
        if self.xp == np:
            return self.demands
        # CuPy → NumPy transfer
        return self.demands.get()

    def get_cpu_distances(self) -> np.ndarray:
        """
        Helper for Class S algorithms requiring CPU distance matrix.

        Returns:
            Distance matrix as NumPy array on CPU

        Example:
            >>> context_gpu = ProblemContext(problem, xp=cp)
            >>> # Class S algorithm needs CPU distances
            >>> cpu_distances = context_gpu.get_cpu_distances()
        """
        if self.xp == np:
            return self.distances
        return self.distances.get()

    def get_cpu_coordinates(self) -> Optional[np.ndarray]:
        """
        Helper for algorithms requiring CPU coordinates.

        Returns:
            Coordinates as NumPy array on CPU, or None
        """
        if self.coordinates is None:
            return None
        if self.xp == np:
            return self.coordinates
        return self.coordinates.get()

    def __repr__(self) -> str:
        """String representation showing problem and backend."""
        backend_name = "GPU (CuPy)" if hasattr(self.xp, "RawKernel") else "CPU (NumPy)"
        return (
            f"<ProblemContext: {self.problem.name} "
            f"({self.problem.problem_type}, N={self.dimension}) "
            f"on {backend_name}>"
        )
