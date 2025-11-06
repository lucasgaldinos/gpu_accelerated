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
    >>> # Create GPU context (Class P algorithms - requires CuPy)
    >>> try:
    ...     import cupy as cp
    ...     gpu_context = ProblemContext(problem, xp=cp)
    ...     gpu_context.distances  # Computed once on GPU, stays in VRAM
    ... except ImportError:
    ...     print("CuPy not available - GPU acceleration unavailable")

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

# CuPy availability check
try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False


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
        Initialize ProblemContext with lazy computation strategy.

        Unlike the previous eager implementation, this version does NOT
        precompute distance matrices or transfer data in __init__. All
        computations are deferred until first access, eliminating the
        wasteful double-transfer pattern for Class S algorithms.

        Args:
            problem: Immutable Problem instance from database loader
            xp: Backend module (numpy or cupy) - preferred backend hint

        Raises:
            ImportError: If xp is CuPy but CuPy is not installed/available

        Note:
            The xp parameter indicates the PREFERRED backend but does not
            force eager computation on that backend. Actual computation
            happens lazily when get_cpu_*() or get_gpu_*() is called.

        Example:
            >>> # Create GPU context (no computation yet)
            >>> import cupy as cp
            >>> context = ProblemContext(problem, xp=cp)
            >>> # Class S algorithm calls get_cpu_distances()
            >>> # → Computes on CPU directly (no GPU transfer waste)
            >>> distances_cpu = context.get_cpu_distances()

            >>> # CuPy not available - clear error
            >>> context = ProblemContext(problem, xp=cp)  # Raises ImportError
        """
        # Validate GPU backend availability
        if xp != np and not CUPY_AVAILABLE:
            raise ImportError(
                "GPU backend requested but CuPy is not installed.\n"
                "To use GPU acceleration, install CuPy:\n"
                "  pip install cupy-cuda12x  # For CUDA 12.x\n"
                "  pip install cupy-cuda11x  # For CUDA 11.x\n"
                "Or use CPU backend with xp=np (NumPy)."
            )

        self.xp = xp
        self.problem = problem
        self.dimension = problem.dimension
        self.capacity = problem.capacity

        # Lazy computation cache (all None until first access)
        self._cpu_distances = None
        self._gpu_distances = None
        self._cpu_demands = None
        self._gpu_demands = None
        self._cpu_coordinates = None
        self._gpu_coordinates = None

        # Validate problem has data to compute from
        if problem.distances is None and problem.coordinates is None:
            raise ValueError(
                f"Problem '{problem.name}' has no distances or coordinates "
                "to compute distance matrix from."
            )

    def get_cpu_demands(self) -> Optional[np.ndarray]:
        """
        Get demands as NumPy array on CPU (lazy computation with caching).

        This method implements lazy computation: demands are only moved/
        computed on first access and then cached for subsequent calls.

        For Class S (sequential) algorithms requiring CPU data, this
        eliminates wasteful GPU transfers when context was created with
        xp=cupy but algorithm needs CPU data.

        Returns:
            Demands array as NumPy array on CPU, or None if no demands

        Example:
            >>> # GPU context (xp=cp) but Class S bin packing needs CPU
            >>> context = ProblemContext(problem, xp=cp)
            >>> # First call: computes on CPU directly (no GPU waste)
            >>> cpu_demands = context.get_cpu_demands()
            >>> # Subsequent calls: returns cached value
            >>> same_demands = context.get_cpu_demands()
        """
        if self._cpu_demands is None and self.problem.demands is not None:
            # Lazy computation: extract demands on CPU
            self._cpu_demands = self.problem.demands  # Already NumPy array
        return self._cpu_demands

    def get_cpu_distances(self) -> np.ndarray:
        """
        Get distance matrix as NumPy array on CPU (lazy computation with caching).

        This method implements lazy computation: the distance matrix is only
        computed on CPU when first requested, eliminating wasteful GPU
        computation and transfer for Class S algorithms.

        Returns:
            Distance matrix as NumPy array on CPU, shape (n, n)

        Raises:
            ValueError: If problem has no distances or coordinates

        Example:
            >>> # Context created with xp=cp (GPU hint)
            >>> context = ProblemContext(problem, xp=cp)
            >>> # Class S algorithm needs CPU distances
            >>> # First call: computes on CPU directly (no GPU waste!)
            >>> cpu_dist = context.get_cpu_distances()
            >>> # Subsequent calls: returns cached CPU matrix
            >>> same_dist = context.get_cpu_distances()
        """
        if self._cpu_distances is None:
            # Lazy computation on CPU
            if self.problem.distances is not None:
                # EXPLICIT edge type - use pre-computed matrix
                self._cpu_distances = self.problem.distances
            elif self.problem.coordinates is not None:
                # Compute from coordinates on CPU (using NumPy)
                self._cpu_distances = compute_distance_matrix(
                    self.problem.coordinates, self.problem.edge_type, np
                )
            else:
                raise ValueError(
                    f"Problem '{self.problem.name}' has no distances or "
                    "coordinates to compute distance matrix from."
                )
        return self._cpu_distances

    def get_cpu_coordinates(self) -> Optional[np.ndarray]:
        """
        Get coordinates as NumPy array on CPU (lazy with caching).

        Returns:
            Coordinates as NumPy array on CPU, or None if not available
        """
        if self._cpu_coordinates is None and self.problem.coordinates is not None:
            # Lazy extraction: coordinates already NumPy array
            self._cpu_coordinates = self.problem.coordinates
        return self._cpu_coordinates

    def get_gpu_demands(self):
        """
        Get demands on GPU (lazy computation with caching).

        Transfers from CPU cache if available, otherwise from problem data.
        Only valid when xp is CuPy.

        Returns:
            Demands as CuPy array on GPU, or None if no demands

        Raises:
            ValueError: If xp is NumPy (not CuPy)
        """
        if self.xp == np:
            raise ValueError("get_gpu_demands() requires xp to be CuPy, not NumPy")

        if self._gpu_demands is None and self.problem.demands is not None:
            if self._cpu_demands is not None:
                # Transfer from CPU cache
                self._gpu_demands = self.xp.asarray(self._cpu_demands)
            else:
                # Transfer from problem data
                self._gpu_demands = self.xp.asarray(self.problem.demands)
        return self._gpu_demands

    def get_gpu_distances(self):
        """
        Get distance matrix on GPU (lazy computation with caching).

        This method computes or transfers the distance matrix to GPU only
        when first requested. If CPU cache exists, transfers from there.
        Otherwise, computes directly on GPU or transfers from problem data.

        Returns:
            Distance matrix as CuPy array on GPU, shape (n, n)

        Raises:
            ValueError: If xp is NumPy (not CuPy) or no data to compute from

        Example:
            >>> # Context with GPU hint
            >>> context = ProblemContext(problem, xp=cp)
            >>> # Class P algorithm needs GPU distances
            >>> # First call: computes on GPU and caches
            >>> gpu_dist = context.get_gpu_distances()
            >>> # Subsequent calls: returns cached GPU matrix (stays in VRAM)
            >>> same_dist = context.get_gpu_distances()
        """
        if self.xp == np:
            raise ValueError("get_gpu_distances() requires xp to be CuPy, not NumPy")

        if self._gpu_distances is None:
            # Priority: CPU cache > problem.distances > compute from coordinates
            if self._cpu_distances is not None:
                # Transfer from CPU cache (most efficient if CPU was used first)
                self._gpu_distances = self.xp.asarray(self._cpu_distances)
            elif self.problem.distances is not None:
                # Transfer EXPLICIT matrix to GPU
                self._gpu_distances = self.xp.asarray(self.problem.distances)
            elif self.problem.coordinates is not None:
                # Compute from coordinates on GPU
                coords_gpu = self.xp.asarray(self.problem.coordinates)
                self._gpu_distances = compute_distance_matrix(
                    coords_gpu, self.problem.edge_type, self.xp
                )
            else:
                raise ValueError(
                    f"Problem '{self.problem.name}' has no distances or "
                    "coordinates to compute distance matrix from."
                )
        return self._gpu_distances

    def get_gpu_coordinates(self):
        """
        Get coordinates on GPU (lazy with caching).

        Returns:
            Coordinates as CuPy array on GPU, or None if not available

        Raises:
            ValueError: If xp is NumPy (not CuPy)
        """
        if self.xp == np:
            raise ValueError("get_gpu_coordinates() requires xp to be CuPy, not NumPy")

        if self._gpu_coordinates is None and self.problem.coordinates is not None:
            if self._cpu_coordinates is not None:
                # Transfer from CPU cache
                self._gpu_coordinates = self.xp.asarray(self._cpu_coordinates)
            else:
                # Transfer from problem data
                self._gpu_coordinates = self.xp.asarray(self.problem.coordinates)
        return self._gpu_coordinates

    # Backward compatibility properties
    @property
    def distances(self):
        """
        Distance matrix on preferred backend (backward compatibility property).

        This property maintains compatibility with existing code that accesses
        context.distances directly. It returns distances on the backend
        specified by self.xp (CPU for NumPy, GPU for CuPy).

        Returns:
            Distance matrix on backend specified by xp
        """
        if self.xp == np:
            return self.get_cpu_distances()
        else:
            return self.get_gpu_distances()

    @property
    def demands(self):
        """
        Demands on preferred backend (backward compatibility property).

        Returns:
            Demands on backend specified by xp, or None
        """
        if self.xp == np:
            return self.get_cpu_demands()
        else:
            return self.get_gpu_demands()

    @property
    def coordinates(self):
        """
        Coordinates on preferred backend (backward compatibility property).

        Returns:
            Coordinates on backend specified by xp, or None
        """
        if self.xp == np:
            return self.get_cpu_coordinates()
        else:
            return self.get_gpu_coordinates()

    def __repr__(self) -> str:
        """String representation showing problem and backend."""
        backend_name = "GPU (CuPy)" if hasattr(self.xp, "RawKernel") else "CPU (NumPy)"
        return (
            f"<ProblemContext: {self.problem.name} "
            f"({self.problem.problem_type}, N={self.dimension}) "
            f"on {backend_name}>"
        )
