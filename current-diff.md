diff --git a/code/src/algorithms/compositional_cvrp_solver.py b/code/src/algorithms/compositional_cvrp_solver.py
index c325c70..7bc0e8a 100644
--- a/code/src/algorithms/compositional_cvrp_solver.py
+++ b/code/src/algorithms/compositional_cvrp_solver.py
@@ -62,9 +62,8 @@ See Also:
     - algorithms.strategies.clustering_strategies: K-Means, DBSCAN [Future]
 """

-from typing import List, Optional
+from typing import Any, List, Optional
 import numpy as np
-from ..protocols.backend import BackendModule
 from ..protocols.algorithm_strategies import (
     BinPackingStrategy,
     TspConstructionStrategy,
@@ -72,7 +71,7 @@ from ..protocols.algorithm_strategies import (
     ClusteringStrategy,
 )
 from ..data_models.problem import Problem
-from ..protocols.problem_context import ProblemContext
+from ..contexts.problem_context import ProblemContext

# ==============================================================================

@@ -88,7 +87,7 @@ def lego_cvrp_solver(
     tsp_strategy: Optional[TspConstructionStrategy] = None,
     clustering_strategy: Optional[ClusteringStrategy] = None,
     improvement_strategy: Optional["TspImprovementStrategy"] = None,

- xp: BackendModule = np,

+ xp: Any = np,
 ) -> List[List[int]]:
     """
     Solve TSP or CVRP via compositional "Lego Blocks" architecture.
diff --git a/code/src/algorithms/construction/christofides.py b/code/src/algorithms/construction/christofides.py
index 82353bd..d01eee4 100644
--- a/code/src/algorithms/construction/christofides.py
+++ b/code/src/algorithms/construction/christofides.py
@@ -17,11 +17,10 @@ import numpy as np
 from typing import Any, List, Set, Dict, Tuple

 from ...data_models.problem import Problem
-from ...protocols.backend import BackendModule
 from .minimum_spanning_tree import minimum_spanning_tree

-def christofides(problem: Problem, xp: BackendModule = np) -> Any:
+def christofides(problem: Problem, xp: Any = np) -> Any:
     """
     Construct TSP tour using Christofides approximation algorithm.

diff --git a/code/src/algorithms/construction/minimum_spanning_tree.py b/code/src/algorithms/construction/minimum_spanning_tree.py
index cf15df3..f606ce0 100644
--- a/code/src/algorithms/construction/minimum_spanning_tree.py
+++ b/code/src/algorithms/construction/minimum_spanning_tree.py
@@ -17,12 +17,11 @@ import heapq
 from typing import Any, List, Tuple

 from ...data_models.problem import Problem
-from ...protocols.backend import BackendModule

 def minimum_spanning_tree(

- problem: Problem, xp: BackendModule = np
-) -> Tuple[Any, float]:

+ problem: Problem, xp: Any = np
+) -> Tuple[List[Tuple[int, int]], float]:
     """
     Compute Minimum Spanning Tree using Prim's algorithm.

@@ -70,8 +69,8 @@ def minimum_spanning_tree(
     problem : Problem
         Problem instance with populated distance matrix.
         Must have problem.distances as (n, n) array.

- xp : BackendModule, optional
-        Array library (numpy or cupy) for backend abstraction.

+ xp : Any, optional
-        Array module (numpy or cupy) controlling where arrays are allocated.
         Default: numpy (CPU execution).
         Note: Priority queue operations remain in Python (heapq).

diff --git a/code/src/algorithms/construction/nearest_neighbor.py b/code/src/algorithms/construction/nearest_neighbor.py
index 6d5339d..7828d5e 100644
--- a/code/src/algorithms/construction/nearest_neighbor.py
+++ b/code/src/algorithms/construction/nearest_neighbor.py
@@ -17,14 +17,13 @@ import numpy as np
 from typing import Any, Optional

 from ...data_models.problem import Problem
-from ...protocols.backend import BackendModule

 def nearest_neighbor(
     problem: Problem,
     start_node: int = 0,
     seed: Optional[int] = None,

- xp: BackendModule = np,

+ xp: Any = np,
 ) -> Any:
     """
     Construct TSP tour using Nearest Neighbor greedy heuristic.
diff --git a/code/src/algorithms/fitness_calculators.py b/code/src/algorithms/fitness_calculators.py
deleted file mode 100644
index 59972bb..0000000
--- a/code/src/algorithms/fitness_calculators.py
+++ /dev/null
@@ -1,247 +0,0 @@
-"""
-Fitness calculation strategies for genetic algorithms.

-

-This module provides GPU-aware fitness calculators that eliminate
-premature GPU→CPU transfers, maintaining fitness arrays on GPU until
-final computation
-

-Classes:

- GACostCalculatorGPU: GPU-aware batch fitness calculator for TSP
-

-Phase 3.5 Bridge Pattern:
- - S-Task (CPU): Selection, Crossover, Mutation use NumPy internally
- - P-Task (GPU): Fitness calculation can use CuPy when context.use_cupy
- - Bridge: Calculator handles GPU→CPU transfer at the right time
-

-Performance Impact:
- - Before (Stage 3): Fitness transferred GPU→CPU twice per generation
-      - Initial population: compute fitness on GPU → transfer to CPU
-      - Offspring: compute fitness on GPU → transfer to CPU
-      - Result: 6.6× slowdown (1.184s vs 0.179s)
-
- - After (Stage 4): Fitness computed on GPU, transferred once at end
-      - Single transfer after all fitness computations complete
-      - Result: Expected 2-4× speedup (0.05-0.09s)
-

-Academic Context:

- TSP Cost Function: $$C(\\pi) = \\sum_{i=1}^{n-1} d(\\pi_i, \\pi_{i+1})$$
- Where:
-        - $\\pi$ is a permutation (tour)
-        - $d(i,j)$ is the distance between cities $i$ and $j$
-        - $n$ is the number of cities
-
- Batch Fitness: $$F(P) = [C(\\pi_1), C(\\pi_2), ..., C(\\pi_m)]$$
- Where:
-        - $P$ is a population of $m$ tours
-        - Computed in parallel on GPU (vectorized operations)
-

-Literature:
- - Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization
-      and Machine Learning. Addison-Wesley.
- - Whitley, D. (1994). A genetic algorithm tutorial. Statistics and
-      Computing, 4(2), 65-85.

-"""
-

-from typing import TYPE_CHECKING
-import numpy as np
-

-try:

- import cupy as cp
- CUPY_AVAILABLE = True
-except ImportError:
- cp = None
- CUPY_AVAILABLE = False
-

-if TYPE_CHECKING:

- from ..contexts.problem_context import ProblemContext
-
-

-class GACostCalculatorGPU:

- """
- GPU-aware fitness calculator for TSP in genetic algorithms.
-
- Phase 3.5 Bridge Pattern:
-        - Accepts Python lists (CPU-resident tours) from S-Task
-        - Converts to GPU arrays for parallel computation
-        - Keeps fitness arrays on GPU during computation
-        - Transfers to CPU only at the end (single transfer)
-
- Architecture:
-        - Designed for Phase 3.5 Hybrid Bridge (S-Task CPU, P-Task GPU)
-        - Eliminates premature GPU→CPU transfers (6.6× slowdown fix)
-        - Maintains compatibility with NumPy-only contexts
-
- Performance:
-        - Expected speedup: 2-4× (CuPy faster than NumPy)
-        - VRAM usage: population_size × tour_length × 8 bytes (float64)
-        - Example: n=100, pop=210 → 168KB (negligible)
-
- Example:
-        >>> context = ProblemContext(problem, xp=cp)
-        >>> calculator = GACostCalculatorGPU(context)
-        >>> population = [[0, 1, 2, 0], [0, 2, 1, 0]]
-        >>> fitness = calculator.compute_batch_fitness(population)
-        >>> # fitness is NumPy array (CPU), ready for S-Task selection
- """
-
- def __init__(self, context: "ProblemContext"):
-        """
-        Initialize GPU-aware fitness calculator.
-
-        Args:
-            context: ProblemContext with distance matrix and backend
-
-        Raises:
-            ValueError: If context lacks required attributes
-        """
-        if not hasattr(context, "xp"):
-            raise ValueError("ProblemContext must have 'xp' attribute (backend module)")
-
-        if not hasattr(context, "distances"):
-            raise ValueError("ProblemContext must have 'distances' attribute")
-
-        self.context = context
-        self.xp = context.xp
-        self._distances = context.distances
-
- def compute_batch_fitness(self, population: np.ndarray) -> np.ndarray:
-        """
-        Compute fitness for entire population on GPU via efficient bulk transfer.
-
-        Phase 3.5 Bridge Pattern (CORRECTED):
-            1. Receive NumPy array (high-performance C-contiguous array)
-            2. Single bulk transfer: NumPy → CuPy (if GPU backend)
-            3. Compute fitness on GPU (parallel edge cost summation)
-            4. Single bulk transfer: CuPy → NumPy (return to CPU)
-
-        Performance Fix (Stage 4):
-            - BEFORE: List[List[int]] → CuPy (slow object-by-object iteration)
-            - AFTER: np.ndarray → CuPy via cp.asarray() (fast bulk C-array transfer)
-            - Result: Eliminates 6.6× slowdown caused by Python list conversion
-
-        TSP Cost Calculation:
-            For each tour $\\pi = [c_0, c_1, ..., c_n, c_0]$:
-            $$
-            C(\\pi) = \\sum_{i=0}^{n} d(c_i, c_{i+1})
-            $$
-
-            Vectorized GPU implementation:
-                - Extract edges: `pop[:, :-1]` (start cities)
-                - Extract edges: `pop[:, 1:]` (end cities)
-                - Index distances: `distances[start, end]`
-                - Sum per tour: `sum(edge_costs, axis=1)`
-
-        Args:
-            population: NumPy array of tours (shape: [pop_size, tour_length])
-                Each row: [depot, c1, c2, ..., ck, depot]
-                Type: np.ndarray with dtype int32 or int64
-
-        Returns:
-            NumPy array of fitness values (CPU-resident, for S-Task)
-            Shape: (population_size,)
-            Dtype: float64
-
-        Raises:
-            ValueError: If population is empty
-            ValueError: If population is not 2D array
-
-        Performance:
-            - CuPy backend: ~0.1-0.5ms for pop=210, n=100
-            - NumPy backend: ~1-2ms for same problem
-            - Bulk transfer overhead: ~0.01-0.1ms (negligible)
-
-        Example:
-            >>> calculator = GACostCalculatorGPU(context)
-            >>> # Population is numpy array (from GA)
-            >>> population = np.array([[0, 1, 2, 0], [0, 2, 1, 0]])
-            >>> fitness = calculator.compute_batch_fitness(population)
-            >>> print(fitness)  # [total_cost_tour1, total_cost_tour2]
-            [12.5, 14.3]
-        """
-        # Validation: Population must be non-empty
-        if population.size == 0:
-            raise ValueError("Population cannot be empty")
-
-        # Validation: Population must be 2D array
-        if population.ndim != 2:
-            raise ValueError(
-                f"Population must be 2D array (pop_size, tour_length), "
-                f"got shape {population.shape}"
-            )
-
-        # Stage 4 Bridge: Efficient bulk transfer NumPy → CuPy
-        # cp.asarray() performs single, fast C-array copy (not object-by-object)
-        if CUPY_AVAILABLE and self.xp is cp:
-            pop_gpu = cp.asarray(population, dtype=cp.int32)
-        else:
-            # NumPy backend: No transfer needed
-            pop_gpu = population.astype(np.int32) if population.dtype != np.int32 else population
-
-        # Extract edges: start and end cities for each edge in all tours
-        # Shape: (population_size, n-1)
-        start_cities = pop_gpu[:, :-1]  # [depot, c1, c2, ..., ck]
-        end_cities = pop_gpu[:, 1:]  # [c1, c2, ..., ck, depot]
-
-        # Index distance matrix with all edges in parallel
-        # Shape: (population_size, n-1)
-        # Each element: d(start_cities[i,j], end_cities[i,j])
-        edge_costs = self._distances[start_cities, end_cities]
-
-        # Sum edge costs per tour (axis=1)
-        # Shape: (population_size,)
-        fitness_backend = self.xp.sum(edge_costs, axis=1)
-
-        # Stage 4 Bridge: Single bulk transfer CuPy → NumPy
-        # .get() performs fast C-array copy back to CPU
-        if hasattr(fitness_backend, "get"):
-            fitness_cpu = fitness_backend.get()
-            return fitness_cpu
-
-        # Already NumPy array
-        return fitness_backend
-
- def compute_single_fitness(self, tour: np.ndarray) -> float:
-        """
-        Compute fitness for a single tour (convenience wrapper).
-
-        This method wraps compute_batch_fitness() for single-tour evaluation.
-        Uses efficient batch interface internally.
-
-        Args:
-            tour: NumPy array representing single tour (1D array)
-                Shape: (tour_length,)
-                Example: np.array([0, 1, 2, 0])
-
-        Returns:
-            float: Total cost of the tour
-
-        Example:
-            >>> calculator = GACostCalculatorGPU(context)
-            >>> tour = np.array([0, 1, 2, 0])
-            >>> cost = calculator.compute_single_fitness(tour)
-            >>> print(cost)  # 12.5
-        """
-        # Ensure 1D array
-        if tour.ndim != 1:
-            raise ValueError(f"Tour must be 1D array, got shape {tour.shape}")
-
-        # Convert to 2D batch (single tour)
-        # np.newaxis creates shape (1, tour_length) efficiently
-        tour_batch = tour[np.newaxis, :]
-
-        # Use batch computation
-        fitness_array = self.compute_batch_fitness(tour_batch)
-
-        # Extract scalar from single-element array
-        return float(fitness_array[0])
-
- def __repr__(self) -> str:
-        """
-        String representation for debugging.
-
-        Returns:
-            String with backend type and problem size
-        """
-        backend_name = "CuPy (GPU)" if hasattr(self.xp, "cuda") else "NumPy (CPU)"
-        n_cities = len(self._distances)
-        return f"GACostCalculatorGPU(backend={backend_name}, n_cities={n_cities})"

diff --git a/code/src/algorithms/improvement/kernels/two_opt_single.cu b/code/src/algorithms/improvement/kernels/two_opt_single.cu
deleted file mode 100644
index cc6644a..0000000
--- a/code/src/algorithms/improvement/kernels/two_opt_single.cu
+++ /dev/null
@@ -1,146 +0,0 @@
-/**

- - GPU 2-opt Single Tour Kernel
- -
- - Performs one pass of 2-opt improvement for a single TSP tour.
- - Uses shared memory for efficient parallel evaluation of all possible swaps.
- -
- - Algorithm:
- - 1. Load tour into shared memory
- - 2. Each thread evaluates subset of (i,j) swap pairs
- - 3. Parallel reduction finds best improvement (minimum delta)
- - 4. Apply best swap in-place
- - 5. Write back improved tour
- -
- - Performance Notes:
- - Shared memory reduces global memory accesses
- - Parallel reduction minimizes synchronization
- - In-place reversal avoids temporary allocations
- -
- - References:
- - Fujimoto & Tsutsui (2011). "A Highly-Parallel TSP Solver for a GPU Computing Platform"
- - Croes (1958). "A Method for Solving Traveling Salesman Problems"
-
- - Author: GPU Debugging Session
- - Date: 2025-01-27
- - Updated: 2025-11-14 (Phase 3.5 - Kernel extraction)
- - >[!warning]
- - >- This references are out of place, please double check. Is this really the same method as fujimoto or is it based on tsplogo/rocki and suda.
- - >- change the variables to descriptive names
- */
-

-extern "C" __global__
-void two_opt_kernel(

- int *tour,
- const double *dist,
- int n,
- int tour_idx
-) {
- extern __shared__ double shared_mem[];
-
- // Partition shared memory
- double *s_deltas = shared_mem;
- int *s_swap_i = (int*)&s_deltas[blockDim.x];
- int *s_swap_j = (int*)&s_swap_i[blockDim.x];
- int *s_tour = (int*)&s_swap_j[blockDim.x];
-
- int tid = threadIdx.x;
- int block_size = blockDim.x;
-
- // FIX: Load tour using loop to handle n > block_size
- for (int i = tid; i < n; i += block_size) {
-        s_tour[i] = tour[i];
- }
- __syncthreads();
-
- // Initialize shared memory for this thread
- s_deltas[tid] = 0.0;
- s_swap_i[tid] = -1;
- s_swap_j[tid] = -1;
-
- // Each thread evaluates a subset of i positions
- for (int i = tid; i < n - 2; i += block_size) {
-        int node_i = s_tour[i];
-        int node_i1 = s_tour[i + 1];
-
-        // Serial inner loop over j
-        for (int j = i + 2; j < n; ++j) {
-            int node_j = s_tour[j];
-            int node_j1 = s_tour[(j + 1) % n];
-
-            // Calculate delta (new - old: negative = improvement)
-            double old_dist = dist[node_i * n + node_i1] + 
-                           dist[node_j * n + node_j1];
-            double new_dist = dist[node_i * n + node_j] + 
-                           dist[node_i1 * n + node_j1];
-            double delta = new_dist - old_dist;  // Negative = improvement
-
-            // Update best for this thread (delta < 0 means improvement)
-            if (delta < s_deltas[tid]) {
-                s_deltas[tid] = delta;
-                s_swap_i[tid] = i;
-                s_swap_j[tid] = j;
-            }
-        }
- }
- __syncthreads();
-
- // Parallel reduction to find minimum delta (most negative = best improvement)
- // Handle small block sizes correctly
- if (tid < 16 && tid + 16 < block_size && s_deltas[tid + 16] < s_deltas[tid]) {
-        s_deltas[tid] = s_deltas[tid + 16];
-        s_swap_i[tid] = s_swap_i[tid + 16];
-        s_swap_j[tid] = s_swap_j[tid + 16];
- }
- __syncthreads();
-
- if (tid < 8 && tid + 8 < block_size && s_deltas[tid + 8] < s_deltas[tid]) {
-        s_deltas[tid] = s_deltas[tid + 8];
-        s_swap_i[tid] = s_swap_i[tid + 8];
-        s_swap_j[tid] = s_swap_j[tid + 8];
- }
- __syncthreads();
-
- if (tid < 4 && tid + 4 < block_size && s_deltas[tid + 4] < s_deltas[tid]) {
-        s_deltas[tid] = s_deltas[tid + 4];
-        s_swap_i[tid] = s_swap_i[tid + 4];
-        s_swap_j[tid] = s_swap_j[tid + 4];
- }
- __syncthreads();
-
- if (tid < 2 && tid + 2 < block_size && s_deltas[tid + 2] < s_deltas[tid]) {
-        s_deltas[tid] = s_deltas[tid + 2];
-        s_swap_i[tid] = s_swap_i[tid + 2];
-        s_swap_j[tid] = s_swap_j[tid + 2];
- }
- __syncthreads();
-
- if (tid < 1 && tid + 1 < block_size && s_deltas[tid + 1] < s_deltas[tid]) {
-        s_deltas[0] = s_deltas[1];
-        s_swap_i[0] = s_swap_i[1];
-        s_swap_j[0] = s_swap_j[1];
- }
- __syncthreads();
-
- // Apply best swap (Thread 0 only)
- if (tid == 0 && s_deltas[0] < 0.0) {
-        int swap_i = s_swap_i[0];
-        int swap_j = s_swap_j[0];
-
-        // Reverse segment [i+1, j]
-        int left = swap_i + 1;
-        int right = swap_j;
-        while (left < right) {
-            int temp = s_tour[left];
-            s_tour[left] = s_tour[right];
-            s_tour[right] = temp;
-            left++;
-            right--;
-        }
- }
- __syncthreads();
-
- // FIX: Write back using loop to handle n > block_size
- for (int i = tid; i < n; i += block_size) {
-        tour[i] = s_tour[i];
- }
-}
diff --git a/code/src/algorithms/metaheuristics/genetic_algorithm.py b/code/src/algorithms/metaheuristics/genetic_algorithm.py
index fa74236..5a657ef 100644
--- a/code/src/algorithms/metaheuristics/genetic_algorithm.py
+++ b/code/src/algorithms/metaheuristics/genetic_algorithm.py
@@ -108,7 +108,7 @@ except ImportError:
     CUPY_AVAILABLE = False

 if TYPE_CHECKING:

- from src.protocols.problem_context import ProblemContext

+ from src.contexts.problem_context import ProblemContext
     from src.protocols.callback_protocol import ProgressCallback, ProgressEvent
     from src.protocols.strategy_protocols import (
         CrossoverStrategy,
diff --git a/code/src/algorithms/metaheuristics/multistart.py b/code/src/algorithms/metaheuristics/multistart.py
index a50f3b0..38a0298 100644
--- a/code/src/algorithms/metaheuristics/multistart.py
+++ b/code/src/algorithms/metaheuristics/multistart.py
@@ -58,7 +58,7 @@ import time
 import numpy as np

 if TYPE_CHECKING:

- from ...protocols.problem_context import ProblemContext

+ from ...contexts.problem_context import ProblemContext
     from ...data_models.problem import Problem
     from ..protocols.algorithm_strategies import TspMetaheuristicStrategy

@@ -91,7 +91,7 @@ def _worker_function(
     Uses seed=[worker_id, seed_base] to ensure independent RNG streams.
     This prevents the UNSAFE pattern: seed = seed_base + worker_id (collisions!)
     """

- from ...protocols.problem_context import ProblemContext

+ from ...contexts.problem_context import ProblemContext

     # args: (algorithm_config, problem, customers, worker_id, seed_base, stored_params)

     algorithm_config, problem, customers, worker_id, seed_base, stored_params = args
diff --git a/code/src/algorithms/metaheuristics/simulated_annealing.py b/code/src/algorithms/metaheuristics/simulated_annealing.py
index fcbc000..c5b4457 100644
--- a/code/src/algorithms/metaheuristics/simulated_annealing.py
+++ b/code/src/algorithms/metaheuristics/simulated_annealing.py
@@ -72,7 +72,7 @@ Statistics Dictionary:
 Example Usage:
     >>> from src.algorithms.metaheuristics import SimulatedAnnealing
     >>> from src.algorithms.strategies import RandomSwapStrategy
>>>
- >>> from src.protocols.problem_context import ProblemContext
>>>
+ >>> from src.contexts.problem_context import ProblemContext
     >>>
     >>> # Create problem context
>>>
     >>> context = ProblemContext(problem, xp=np)
@@ -108,7 +108,7 @@ except ImportError:
     CUPY_AVAILABLE = False

 if TYPE_CHECKING:

- from src.protocols.problem_context import ProblemContext

+ from src.contexts.problem_context import ProblemContext
     from src.protocols.callback_protocol import ProgressCallback, ProgressEvent

diff --git a/code/src/algorithms/objectives/tour_cost.py b/code/src/algorithms/objectives/tour_cost.py
index 1636757..3f5b869 100644
--- a/code/src/algorithms/objectives/tour_cost.py
+++ b/code/src/algorithms/objectives/tour_cost.py
@@ -9,10 +9,9 @@ import numpy as np
 from typing import Any

 from ...data_models.problem import Problem
-from ...protocols.backend import BackendModule

-def compute_tour_cost(problem: Problem, tour: Any, xp: BackendModule = np) -> float:
+def compute_tour_cost(problem: Problem, tour: Any, xp: Any = np) -> float:
     """
     Calculate total cost of a TSP/ATSP tour including return to start.

@@ -31,8 +30,8 @@ def compute_tour_cost(problem: Problem, tour: Any, xp: BackendModule = np) -> fl
     tour : array-like, shape (n,)
         Tour as array of node indices in visit order.
         Can be numpy.ndarray or cupy.ndarray depending on backend.

- xp : BackendModule, optional
-        Array library to use (numpy or cupy). Default: numpy.

+ xp : Any, optional
-        Array module (numpy or cupy) controlling where computations run. Default: numpy.

  Returns
     -------

diff --git a/code/src/algorithms/strategies/bin_packing_strategies.py b/code/src/algorithms/strategies/bin_packing_strategies.py
index 3a17eac..7c9a5eb 100644
--- a/code/src/algorithms/strategies/bin_packing_strategies.py
+++ b/code/src/algorithms/strategies/bin_packing_strategies.py
@@ -39,7 +39,7 @@ See Also:
 from typing import List, TYPE_CHECKING

 if TYPE_CHECKING:

- from ...protocols.problem_context import ProblemContext

+ from ...contexts.problem_context import ProblemContext

# ==============================================================================

diff --git a/code/src/algorithms/strategies/clustering_strategies.py b/code/src/algorithms/strategies/clustering_strategies.py
index 5b9a9cf..d98ba5e 100644
--- a/code/src/algorithms/strategies/clustering_strategies.py
+++ b/code/src/algorithms/strategies/clustering_strategies.py
@@ -51,9 +51,8 @@ See Also:
     - algorithms.compositional_cvrp_solver (clustering phase)
 """

-from typing import List
+from typing import Any, List
 import numpy as np
-from protocols.backend import BackendModule
 from protocols.algorithm_strategies import ClusteringStrategy

@@ -119,7 +118,7 @@ class KMeansStrategy:
         self.max_iterations = max_iterations

     def cluster(

-        self, locations: np.ndarray, demands: np.ndarray, xp: BackendModule = np

+        self, locations: np.ndarray, demands: np.ndarray, xp: Any = np
     ) -> List[Cluster]:
         """Partition customers via k-means (NOT IMPLEMENTED)."""
         raise NotImplementedError(
@@ -161,7 +160,7 @@ class DBSCANStrategy:
         self.min_samples = min_samples

     def cluster(

-        self, locations: np.ndarray, demands: np.ndarray, xp: BackendModule = np

+        self, locations: np.ndarray, demands: np.ndarray, xp: Any = np
     ) -> List[Cluster]:
         """Partition customers via DBSCAN (NOT IMPLEMENTED)."""
         raise NotImplementedError(
diff --git a/code/src/algorithms/strategies/construction_strategies.py b/code/src/algorithms/strategies/construction_strategies.py
index fce91f6..e798a35 100644
--- a/code/src/algorithms/strategies/construction_strategies.py
+++ b/code/src/algorithms/strategies/construction_strategies.py
@@ -42,7 +42,7 @@ import numpy as np
 from ...utils.strategy_registry import StrategyRegistry

 if TYPE_CHECKING:

- from ...protocols.problem_context import ProblemContext

+ from ...contexts.problem_context import ProblemContext

# ==============================================================================

diff --git a/code/src/algorithms/strategies/improvement_strategies.py b/code/src/algorithms/strategies/improvement_strategies.py
index 5e49f83..de184d2 100644
--- a/code/src/algorithms/strategies/improvement_strategies.py
+++ b/code/src/algorithms/strategies/improvement_strategies.py
@@ -47,7 +47,7 @@ import numpy as np
 from typing import List, Optional, TYPE_CHECKING, Any, Dict

 if TYPE_CHECKING:

- from ...protocols.problem_context import ProblemContext

+ from ...contexts.problem_context import ProblemContext

# ==============================================================================

diff --git a/code/src/distances/matrix.py b/code/src/distances/matrix.py
index 5535707..e70c623 100644
--- a/code/src/distances/matrix.py
+++ b/code/src/distances/matrix.py
@@ -15,14 +15,14 @@ Usage:
     5.0
 """

-import numpy as np
+from typing import Any

-from ..protocols.backend import BackendModule
+import numpy as np
 from .pairwise import get_distance_function

 def compute_distance_matrix(

- coordinates: np.ndarray, edge_weight_type: str, xp: BackendModule = np

+ coordinates: np.ndarray, edge_weight_type: str, xp: Any = np
 ) -> np.ndarray:
     """
     Compute full distance matrix from coordinates using specified edge type.
diff --git a/code/src/protocols/__init__.py b/code/src/protocols/__init__.py
index 187f67f..f5a33d4 100644
--- a/code/src/protocols/__init__.py
+++ b/code/src/protocols/__init__.py
@@ -1,11 +1,5 @@
-"""
-Backend protocols for type safety across NumPy/CuPy implementations.
+"""Exports for protocol-based strategy interfaces."""

-This package defines typing.Protocol interfaces that ensure type safety
-when switching between NumPy (CPU) and CuPy (GPU) backends.
-"""
-

-from .backend import BackendModule
 from .bin_packing_protocol import BinPackingStrategy

-__all__ = ["BackendModule", "BinPackingStrategy"]
+__all__ = ["BinPackingStrategy"]
diff --git a/code/src/protocols/algorithm_strategies.py b/code/src/protocols/algorithm_strategies.py
index 5a32945..93b3a3c 100644
--- a/code/src/protocols/algorithm_strategies.py
+++ b/code/src/protocols/algorithm_strategies.py
@@ -29,9 +29,8 @@ See Also:
     - code/src/algorithms/compositional_cvrp_solver.py
 """

-from typing import Protocol, List, TYPE_CHECKING
+from typing import Any, List, Protocol, TYPE_CHECKING
 import numpy as np
-from .backend import BackendModule

 if TYPE_CHECKING:
     from .problem_context import ProblemContext
@@ -547,7 +546,7 @@ class ClusteringStrategy(Protocol):
     """

     def cluster(

-        self, locations: np.ndarray, demands: np.ndarray, xp: BackendModule = np

+        self, locations: np.ndarray, demands: np.ndarray, xp: Any = np
     ) -> List["Cluster"]:
         """
         Partition customers into spatial clusters.
diff --git a/code/src/protocols/backend.py b/code/src/protocols/backend.py
deleted file mode 100644
index 417339d..0000000
--- a/code/src/protocols/backend.py
+++ /dev/null
@@ -1,521 +0,0 @@
-"""
-Backend module protocol for NumPy/CuPy interoperability.

-

-This module defines typing.Protocol interfaces that ensure type-safe
-backend switching between NumPy (CPU) and CuPy (GPU) implementations
-

-The protocol pattern allows type checkers to validate that code using
-backend modules (passed as `xp` parameter) only calls methods that exist
-in both NumPy and CuPy
-

-Example:
>>>
- >>> import numpy as np
- >>> def compute_distance(coords, xp: BackendModule):
- ...     # Type checker knows xp.sqrt and xp.sum are safe
- ...     diff = coords[:, None, :] - coords[None, :, :]
- ...     return xp.sqrt(xp.sum(diff**2, axis=2))
-

-> [!important] For later documentation
-"""
-

-from typing import Any, Optional, Protocol, Tuple, Union
-

-

-class BackendModule(Protocol):

- """
- Protocol defining required operations for backend modules (NumPy/CuPy).
-
- This protocol specifies the minimum set of operations required by
- distance calculation functions. Both NumPy and CuPy satisfy this protocol.
-
- The protocol ensures:
- - Type safety when switching backends
- - Clear documentation of backend requirements
- - Prevention of accidentally using backend-specific methods
-
- Attributes:
-        ndarray: Array type for the backend (numpy.ndarray or cupy.ndarray)
-
- Note:
-        Return types use `Any` because NumPy and CuPy have incompatible
-        array type hierarchies. Type checkers will still validate that
-        methods exist and are called correctly.
- """
-

- # Array creation and conversion

- def array(
-        self,
-        object: Any,
-        dtype: Optional[Any] = None,
-        *,
-        copy: Optional[bool] = None,
-        order: Optional[str] = None,
-        ndmin: int = 0,
- ) -> Any:
-        """
-        Create an array from an object.
-
-        Args:
-            object: Array-like object to convert
-            dtype: Desired data type
-            copy: If True, ensure array is copied
-            order: Memory layout ('C' or 'F')
-            ndmin: Minimum number of dimensions
-
-        Returns:
-            Array (numpy.ndarray or cupy.ndarray)
-        """
-        ...
-
- def zeros(
-        self, shape: Union[int, Tuple[int, ...]], dtype: Optional[Any] = None
- ) -> Any:
-        """Create array filled with zeros."""
-        ...
-
- def ones(
-        self, shape: Union[int, Tuple[int, ...]], dtype: Optional[Any] = None
- ) -> Any:
-        """Create array filled with ones."""
-        ...
-
- def empty(
-        self, shape: Union[int, Tuple[int, ...]], dtype: Optional[Any] = None
- ) -> Any:
-        """Create uninitialized array."""
-        ...
-

- # Mathematical operations

- def sqrt(self, x: Any) -> Any:
-        """Element-wise square root."""
-        ...
-
- def sum(
-        self,
-        a: Any,
-        axis: Optional[Union[int, Tuple[int, ...]]] = None,
-        keepdims: bool = False,
- ) -> Any:
-        """Sum array elements over given axis."""
-        ...
-
- def abs(self, x: Any) -> Any:
-        """Element-wise absolute value."""
-        ...
-
- def ceil(self, x: Any) -> Any:
-        """Element-wise ceiling (round up)."""
-        ...
-
- def floor(self, x: Any) -> Any:
-        """Element-wise floor (round down)."""
-        ...
-

- # Trigonometric functions (needed for GEO distance)

- def sin(self, x: Any) -> Any:
-        """Element-wise sine."""
-        ...
-
- def cos(self, x: Any) -> Any:
-        """Element-wise cosine."""
-        ...
-
- def arcsin(self, x: Any) -> Any:
-        """Element-wise inverse sine (arcsine)."""
-        ...
-
- def radians(self, x: Any) -> Any:
-        """Convert degrees to radians."""
-        ...
-

- # Array manipulation

- def asarray(self, a: Any, dtype: Optional[Any] = None) -> Any:
-        """
-        Convert input to array (avoid copy if possible).
-
-        Note: For axis expansion, use None instead of xp.newaxis:
-            coords[:, None, :]  # Correct - works with all backends
-            coords[:, xp.newaxis, :]  # Also correct, but None is simpler
-        """
-        ...
-
- def arccos(self, x: Any) -> Any:
-        """Element-wise inverse cosine (arccosine)."""
-        ...
-

- # Reduction operations

- def any(
-        self,
-        a: Any,
-        axis: Optional[Union[int, Tuple[int, ...]]] = None,
-        keepdims: bool = False,
- ) -> Any:
-        """
-        Test whether any array element evaluates to True.
-
-        Args:
-            a: Input array or condition
-            axis: Axis along which to perform reduction
-            keepdims: Keep reduced dimensions as size 1
-
-        Returns:
-            Boolean or array of booleans
-        """
-        ...
-
- def all(
-        self,
-        a: Any,
-        axis: Optional[Union[int, Tuple[int, ...]]] = None,
-        keepdims: bool = False,
- ) -> Any:
-        """
-        Test whether all array elements evaluate to True.
-
-        Args:
-            a: Input array or condition
-            axis: Axis along which to perform reduction
-            keepdims: Keep reduced dimensions as size 1
-
-        Returns:
-            Boolean or array of booleans
-        """
-        ...
-
- def max(
-        self,
-        a: Any,
-        axis: Optional[Union[int, Tuple[int, ...]]] = None,
-        keepdims: bool = False,
- ) -> Any:
-        """
-        Return maximum value along axis.
-
-        Args:
-            a: Input array
-            axis: Axis along which to find maximum
-            keepdims: Keep reduced dimensions as size 1
-
-        Returns:
-            Maximum value(s)
-        """
-        ...
-
- def min(
-        self,
-        a: Any,
-        axis: Optional[Union[int, Tuple[int, ...]]] = None,
-        keepdims: bool = False,
- ) -> Any:
-        """
-        Return minimum value along axis.
-
-        Args:
-            a: Input array
-            axis: Axis along which to find minimum
-            keepdims: Keep reduced dimensions as size 1
-
-        Returns:
-            Minimum value(s)
-        """
-        ...
-
- def argmax(
-        self,
-        a: Any,
-        axis: Optional[int] = None,
- ) -> Any:
-        """
-        Return indices of maximum values along axis.
-
-        Args:
-            a: Input array
-            axis: Axis along which to find argmax
-
-        Returns:
-            Index or array of indices
-        """
-        ...
-
- def argmin(
-        self,
-        a: Any,
-        axis: Optional[int] = None,
- ) -> Any:
-        """
-        Return indices of minimum values along axis.
-
-        Args:
-            a: Input array
-            axis: Axis along which to find argmin
-
-        Returns:
-            Index or array of indices
-        """
-        ...
-

- # Array creation (additional)

- def arange(
-        self,
-        start: Union[int, float],
-        stop: Optional[Union[int, float]] = None,
-        step: Union[int, float] = 1,
-        dtype: Optional[Any] = None,
- ) -> Any:
-        """
-        Return evenly spaced values within interval.
-
-        Args:
-            start: Start of interval (or stop if only one arg)
-            stop: End of interval
-            step: Spacing between values
-            dtype: Desired data type
-
-        Returns:
-            Array of evenly spaced values
-        """
-        ...
-
- def full(
-        self,
-        shape: Union[int, Tuple[int, ...]],
-        fill_value: Any,
-        dtype: Optional[Any] = None,
- ) -> Any:
-        """
-        Create array filled with specific value.
-
-        Args:
-            shape: Shape of array
-            fill_value: Value to fill array with
-            dtype: Desired data type
-
-        Returns:
-            Array filled with fill_value
-        """
-        ...
-

- # Advanced indexing

- def ix_(self, *args: Any) -> Tuple[Any, ...]:
-        """
-        Construct open mesh from multiple sequences.
-
-        Used for fancy indexing to extract submatrices.
-
-        Args:
-            *args: 1-D sequences (arrays or lists)
-
-        Returns:
-            Tuple of arrays for indexing
-
-        Example:
-            >>> subset_matrix = full_matrix[xp.ix_([0,2,3], [0,2,3])]
-        """
-        ...
-

- # Constants (attributes, not methods)

- @property
- def inf(self) -> float:
-        """Positive infinity constant."""
-        ...
-
- @property
- def newaxis(self) -> Any:
-        """
-        Constant for adding new axes to arrays.
-
-        Note: Using None is equivalent and more portable:
-            arr[:, None, :]  # Recommended
-            arr[:, xp.newaxis, :]  # Also works
-        """
-        ...
-
-

-# ==============================================================================
-# CuPy-Specific Methods (Not in Protocol)
-# ==============================================================================
-

-"""
-Some operations are specific to CuPy and not available in NumPy.
-Use hasattr() to check for these methods before calling
-

-__CuPy-only methods:__
-

-1. __xp.asnumpy(arr)__ - Transfer CuPy array to NumPy (GPU → CPU)
-

- Usage pattern:
- ```python
- if hasattr(xp, 'asnumpy'):
-       cpu_array = xp.asnumpy(gpu_array)  # CuPy → NumPy
- else:
-       cpu_array = np.asarray(gpu_array)  # NumPy (no-op)
- ```
-

-2. __xp.get_array_module(arr)__ - Get backend module from array
-

- Usage pattern:
- ```python
- import numpy as np
- try:
-       import cupy as cp
-       xp = cp.get_array_module(distances)  # Returns cp if CuPy array
- except ImportError:
-       xp = np
- ```
-

-__NumPy-only methods:__
-

-- Most NumPy-specific methods have CuPy equivalents
-- Check CuPy documentation for compatibility: <https://docs.cupy.dev/>
-

-__Type checking:__
-

-The protocol uses `Any` for return types because NumPy and CuPy have
-incompatible type hierarchies. To check array types at runtime
-

-```python
-import numpy as np
-try:

- import cupy as cp
- CUPY_AVAILABLE = True
-except ImportError:
- CUPY_AVAILABLE = False
-

-def is_gpu_array(arr):

- '''Check if array is CuPy array (on GPU).'''
- if CUPY_AVAILABLE:
-        return isinstance(arr, cp.ndarray)
- return False
-

-def is_cpu_array(arr):

- '''Check if array is NumPy array (on CPU).'''
- return isinstance(arr, np.ndarray)
-```
-

-__Backend detection:__
-

-```python
-def get_backend_name(xp):

- '''Get human-readable backend name.'''
- if xp.__name__ == 'cupy':
-        return 'CuPy (GPU)'
- elif xp.__name__ == 'numpy':
-        return 'NumPy (CPU)'
- else:
-        return f'Unknown ({xp.__name__})'

-```
-"""
-

-

-# ==============================================================================
-# Backend Utility Functions (Lego Bricks for Backend Configuration)
-# ==============================================================================
-

-import numpy as np
-

-try:

- import cupy as cp
-
- CUPY_AVAILABLE = True
-except ImportError:
- CUPY_AVAILABLE = False
-
-

-def get_backend(backend: str) -> Any:

- """
- Get backend module by name (lego brick for backend configuration).
-
- Enables explicit backend selection in algorithms instead of relying
- on implicit backend from ProblemContext.
-
- Args:
-        backend: Backend name string
-            - "numpy": NumPy (CPU) - safe default for all problem sizes
-            - "cupy": CuPy (GPU) - requires CUDA, best for large problems (n>1000)
-
- Returns:
-        Backend module (numpy or cupy)
-
- Raises:
-        ValueError: If backend name invalid
-        RuntimeError: If cupy requested but not installed
-
- Example:
-        >>> xp = get_backend("numpy")  # CPU
-        >>> xp = get_backend("cupy")   # GPU
-        >>> arr = xp.array([1, 2, 3])
-
- Note:
-        Numba JIT acceleration is NOT a backend option here because Numba
-        operates at the strategy/function level via @jit decorators, not
-        at the array module level. For Numba acceleration, implement
-        Numba-decorated strategy classes (e.g., Numba2OptStrategy).
-        > In fact, numba is not an option anywhere this repo, for now.
-
- Reference:
-        Backend Configuration Architecture (M14_M15_DETAILED_TASKS.md)
-        METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 2.1
- """
- if backend == "numpy":
-        return np
- elif backend == "cupy":
-        if not CUPY_AVAILABLE:
-            raise RuntimeError(
-                "Backend 'cupy' requested but CuPy not installed.\n"
-                "Install with: pip install cupy-cuda12x (for CUDA 12.x)\n"
-                "Or: pip install cupy-cuda11x (for CUDA 11.x)"
-            )
-        return cp
- else:
-        raise ValueError(f"Invalid backend '{backend}'. Valid options: 'numpy', 'cupy'")
-
-

-def get_backend_name(xp) -> str:

- """
- Get human-readable backend name.
-
- Args:
-        xp: Backend module (numpy or cupy)
-
- Returns:
-        Human-readable name: "NumPy (CPU)", "CuPy (GPU)", or "Unknown"
-
- Example:
-        >>> import numpy as np
-        >>> get_backend_name(np)
-        'NumPy (CPU)'
- """
- if xp.__name__ == "cupy":
-        return "CuPy (GPU)"
- elif xp.__name__ == "numpy":
-        return "NumPy (CPU)"
- else:
-        return f"Unknown ({xp.__name__})"
-
-

-def is_gpu_array(arr) -> bool:

- """
- Check if array is CuPy array (on GPU).
-
- Args:
-        arr: Array to check
-
- Returns:
-        True if CuPy array, False otherwise
- """
- if CUPY_AVAILABLE:
-        return isinstance(arr, cp.ndarray)
- return False
-
-

-def is_cpu_array(arr) -> bool:

- """
- Check if array is NumPy array (on CPU).
-
- Args:
-        arr: Array to check
-
- Returns:
-        True if NumPy array, False otherwise
- """
- return isinstance(arr, np.ndarray)
diff --git a/code/src/protocols/problem_context.py b/code/src/protocols/problem_context.py
deleted file mode 100644
index 17782a8..0000000
--- a/code/src/protocols/problem_context.py
+++ /dev/null
@@ -1,385 +0,0 @@
-"""
-ProblemContext: Backend-Specific Problem Data Holder with Lazy Distance Matrix Caching.
-

-⚠️ ARCHITECTURAL NOTE ⚠️
-This module is placed in `protocols/` for organizational consistency with other
-strategy protocols, but ProblemContext is NOT a Protocol (PEP 544) interface.
-It is a concrete class that wraps the immutable Problem dataclass and adds
-backend-specific lazy computation of distance matrices
-

-The ProblemContext solves a critical performance anti-pattern identified in
-flaws.md: sequential algorithms calling compute_distance_matrix() repeatedly
-inside Python loops, causing O(n³) complexity instead of O(n²)
-

-__CRITICAL: Fully Lazy Loading (Phase 5 Cleanup)__
-- `__init__` stores problem and xp but DOES NOT allocate matrices
-- All caches (_distances_cpu, _distances_gpu, etc.) start as None
-- No eager @property accessors - forces explicit method calls
-- Use `get_cpu_distances()` or `get_gpu_distances()` explicitly
-- This prevents 14.4GB allocation crashes on large problems (n=30,000)
-

-Design Philosophy:
-- Single Responsibility: Holds all backend-specific problem data
-- Immutability: Based on frozen Problem dataclass, computed data cached
-- Performance: Distance matrix computed ONCE on target backend
-- Lazy Loading: NO allocation until first explicit access
-- Hybrid Bridge Compatible: Supports both CPU-only (S-Task) and GPU (P-Task)
-

-Example:
>>>
- >>> from src.data_models.problem import Problem
- >>> from src.protocols.problem_context import ProblemContext
- >>> import numpy as np
- >>>
>>>
- >>> # Load problem
>>>
- >>> with DatabaseLoader() as loader:
- ...     problem = loader.load('berlin52')
- >>>
>>>
- >>> # Create context (NO allocation yet - fully lazy)
>>>
- >>> context = ProblemContext(problem, xp=np, seed=42)
- >>>
>>>
- >>> # S-Task algorithm: Use CPU distances explicitly
>>>
- >>> distances_cpu = context.get_cpu_distances()  # Allocated here
- >>>
>>>
- >>> # P-Task algorithm: Use GPU distances explicitly
>>>
- >>> if CUPY_AVAILABLE:
- ...     distances_gpu = context.get_gpu_distances()  # Transfers to GPU
-

-References:
- - flaws.md: Documents the distance matrix recomputation anti-pattern
- - flaw_analysis.md: Explains Class S (sequential) vs Class P (parallel)
- - architectural-decisions-and-questions.md: ProblemContext design rationale
- - Phase 5 Cleanup: Removed eager @property accessors (distances, demands, coordinates)
-"""
-

-import numpy as np
-from typing import Optional
-

-from ..data_models.problem import Problem
-from ..protocols.backend import BackendModule
-from ..distances.matrix import compute_distance_matrix
-

-# CuPy availability check
-try:

- import cupy as cp
-
- CUPY_AVAILABLE = True
-except ImportError:
- cp = None
- CUPY_AVAILABLE = False
-
-

-class ProblemContext:

- """
- Backend-specific problem data holder with cached distance matrix.
-
- This class wraps the immutable Problem dataclass and precomputes the
- distance matrix on the specified backend (NumPy or CuPy), caching it
- to avoid redundant O(n²) computations.
-
- __Key Performance Fix:__
- Before ProblemContext, TspConstructionStrategy.build_tour() was called
- k times (once per route), each time computing the distance matrix:
-        - Total: k × O(m²) redundant work
-        - For GPU: k × (CPU→GPU transfer + compute + GPU→CPU transfer)
-        - Example: eil51 with k=5 routes = 17-82x slowdown
-
- After ProblemContext:
-        - Distance matrix computed ONCE: O(N²) where N = total nodes
-        - Cached on target backend (CPU or GPU)
-        - All algorithms reuse the same cached matrix
-        - No redundant transfers
-
- Attributes:
-        xp: Backend module (NumPy or CuPy)
-        problem: Original immutable Problem instance
-        dimension: Number of nodes (problem.dimension)
-        capacity: Vehicle capacity (CVRP only, None for TSP/ATSP)
-        demands: Customer demands on target backend (xp.ndarray)
-        distances: Cached distance matrix on target backend (xp.ndarray)
-        coordinates: Coordinates on target backend (xp.ndarray or None)
-
- Example:
-        >>> # Class S (sequential CPU algorithm)
-        >>> context = ProblemContext(problem, xp=np)
-        >>> tour = nearest_neighbor_strategy.construct(context, customers)
-        >>> # No recomputation - uses context.distances
-
-        >>> # Class P (parallel GPU algorithm)
-        >>> context_gpu = ProblemContext(problem, xp=cp)
-        >>> improved_tours = two_opt_gpu.improve_tours(tours, context_gpu)
-        >>> # Distance matrix stays in VRAM, zero transfer overhead
- """
-
- def __init__(
-        self,
-        problem: Problem,
-        xp: BackendModule,
-        seed: Optional[int | list[int]] = None,
- ):
-        """
-        Initialize ProblemContext with lazy computation strategy.
-
-        Unlike the previous eager implementation, this version does NOT
-        precompute distance matrices or transfer data in __init__. All
-        computations are deferred until first access, eliminating the
-        wasteful double-transfer pattern for Class S algorithms.
-
-        Args:
-            problem: Immutable Problem instance from database loader
-            xp: Backend module (numpy or cupy) - preferred backend hint
-            seed: Random seed for RNG (int, list of ints, or None).
-                  If None, OS entropy is used. For parallel execution,
-                  use sequence of integers: [worker_id, root_seed].
-                  See NumPy docs on "Parallel random number generation".
-
-        Raises:
-            ImportError: If xp is CuPy but CuPy is not installed/available
-
-        Note:
-            The xp parameter indicates the PREFERRED backend but does not
-            force eager computation on that backend. Actual computation
-            happens lazily when get_cpu_*() or get_gpu_*() is called.
-
-            RNG Strategy: Uses NumPy's "Sequence of integer seeds" pattern
-            for parallel safety. RandomState accepts both single integers
-            and sequences, providing cross-backend compatibility (NumPy/CuPy).
-
-        Example:
-            >>> # Create GPU context (no computation yet)
-            >>> import cupy as cp
-            >>> context = ProblemContext(problem, xp=cp)
-            >>> # Class S algorithm calls get_cpu_distances()
-            >>> # → Computes on CPU directly (no GPU transfer waste)
-            >>> distances_cpu = context.get_cpu_distances()
-
-            >>> # Parallel execution with independent RNG (SAFE)
-            >>> context = ProblemContext(problem, xp=np, seed=[worker_id, root_seed])
-            >>> # Each worker gets independent RNG stream
-            >>> random_value = context.rng.random()
-
-            >>> # CuPy not available - clear error
-            >>> context = ProblemContext(problem, xp=cp)  # Raises ImportError
-        """
-        # Validate GPU backend availability
-        if xp != np and not CUPY_AVAILABLE:
-            raise ImportError(
-                "GPU backend requested but CuPy is not installed.\n"
-                "To use GPU acceleration, install CuPy:\n"
-                "  pip install cupy-cuda12x  # For CUDA 12.x\n"
-                "  pip install cupy-cuda11x  # For CUDA 11.x\n"
-                "Or use CPU backend with xp=np (NumPy)."
-            )
-
-        self.xp = xp
-        self.problem = problem
-        self.dimension = problem.dimension
-        self.capacity = problem.capacity
-
-        # Create independent RNG instance (NumPy "Sequence of integer seeds" pattern)
-        # RandomState works with both NumPy and CuPy for cross-backend compatibility
-        if seed is not None:
-            # Accepts both int and sequence of ints (e.g., [worker_id, root_seed])
-            self.rng = xp.random.RandomState(seed)
-        else:
-            # Use OS entropy (non-deterministic)
-            self.rng = xp.random.RandomState()
-
-        # Store seed for debugging/reproducibility
-        self.seed = seed
-
-        # Lazy computation cache (all None until first access)
-        self._cpu_distances = None
-        self._gpu_distances = None
-        self._cpu_demands = None
-        self._gpu_demands = None
-        self._cpu_coordinates = None
-        self._gpu_coordinates = None
-
-        # Validate problem has data to compute from
-        if problem.distances is None and problem.coordinates is None:
-            raise ValueError(
-                f"Problem '{problem.name}' has no distances or coordinates "
-                "to compute distance matrix from."
-            )
-
- def get_cpu_demands(self) -> Optional[np.ndarray]:
-        """
-        Get demands as NumPy array on CPU (lazy computation with caching).
-
-        This method implements lazy computation: demands are only moved/
-        computed on first access and then cached for subsequent calls.
-
-        For Class S (sequential) algorithms requiring CPU data, this
-        eliminates wasteful GPU transfers when context was created with
-        xp=cupy but algorithm needs CPU data.
-
-        Returns:
-            Demands array as NumPy array on CPU, or None if no demands
-
-        Example:
-            >>> # GPU context (xp=cp) but Class S bin packing needs CPU
-            >>> context = ProblemContext(problem, xp=cp)
-            >>> # First call: computes on CPU directly (no GPU waste)
-            >>> cpu_demands = context.get_cpu_demands()
-            >>> # Subsequent calls: returns cached value
-            >>> same_demands = context.get_cpu_demands()
-        """
-        if self._cpu_demands is None and self.problem.demands is not None:
-            # Lazy computation: extract demands on CPU
-            self._cpu_demands = self.problem.demands  # Already NumPy array
-        return self._cpu_demands
-
- def get_cpu_distances(self) -> np.ndarray:
-        """
-        Get distance matrix as NumPy array on CPU (lazy computation with caching).
-
-        This method implements lazy computation: the distance matrix is only
-        computed on CPU when first requested, eliminating wasteful GPU
-        computation and transfer for Class S algorithms.
-
-        Returns:
-            Distance matrix as NumPy array on CPU, shape (n, n)
-
-        Raises:
-            ValueError: If problem has no distances or coordinates
-
-        Example:
-            >>> # Context created with xp=cp (GPU hint)
-            >>> context = ProblemContext(problem, xp=cp)
-            >>> # Class S algorithm needs CPU distances
-            >>> # First call: computes on CPU directly (no GPU waste!)
-            >>> cpu_dist = context.get_cpu_distances()
-            >>> # Subsequent calls: returns cached CPU matrix
-            >>> same_dist = context.get_cpu_distances()
-        """
-        if self._cpu_distances is None:
-            # Lazy computation on CPU
-            if self.problem.distances is not None:
-                # EXPLICIT edge type - use pre-computed matrix
-                self._cpu_distances = self.problem.distances
-            elif self.problem.coordinates is not None:
-                # Compute from coordinates on CPU (using NumPy)
-                self._cpu_distances = compute_distance_matrix(
-                    self.problem.coordinates, self.problem.edge_type, np
-                )
-            else:
-                raise ValueError(
-                    f"Problem '{self.problem.name}' has no distances or "
-                    "coordinates to compute distance matrix from."
-                )
-        return self._cpu_distances
-
- def get_cpu_coordinates(self) -> Optional[np.ndarray]:
-        """
-        Get coordinates as NumPy array on CPU (lazy with caching).
-
-        Returns:
-            Coordinates as NumPy array on CPU, or None if not available
-        """
-        if self._cpu_coordinates is None and self.problem.coordinates is not None:
-            # Lazy extraction: coordinates already NumPy array
-            self._cpu_coordinates = self.problem.coordinates
-        return self._cpu_coordinates
-
- def get_gpu_demands(self):
-        """
-        Get demands on GPU (lazy computation with caching).
-
-        Transfers from CPU cache if available, otherwise from problem data.
-        Only valid when xp is CuPy.
-
-        Returns:
-            Demands as CuPy array on GPU, or None if no demands
-
-        Raises:
-            ValueError: If xp is NumPy (not CuPy)
-        """
-        if self.xp == np:
-            raise ValueError("get_gpu_demands() requires xp to be CuPy, not NumPy")
-
-        if self._gpu_demands is None and self.problem.demands is not None:
-            if self._cpu_demands is not None:
-                # Transfer from CPU cache
-                self._gpu_demands = self.xp.asarray(self._cpu_demands)
-            else:
-                # Transfer from problem data
-                self._gpu_demands = self.xp.asarray(self.problem.demands)
-        return self._gpu_demands
-
- def get_gpu_distances(self):
-        """
-        Get distance matrix on GPU (lazy computation with caching).
-
-        This method computes or transfers the distance matrix to GPU only
-        when first requested. If CPU cache exists, transfers from there.
-        Otherwise, computes directly on GPU or transfers from problem data.
-
-        Returns:
-            Distance matrix as CuPy array on GPU, shape (n, n)
-
-        Raises:
-            ValueError: If xp is NumPy (not CuPy) or no data to compute from
-
-        Example:
-            >>> # Context with GPU hint
-            >>> context = ProblemContext(problem, xp=cp)
-            >>> # Class P algorithm needs GPU distances
-            >>> # First call: computes on GPU and caches
-            >>> gpu_dist = context.get_gpu_distances()
-            >>> # Subsequent calls: returns cached GPU matrix (stays in VRAM)
-            >>> same_dist = context.get_gpu_distances()
-        """
-        if self.xp == np:
-            raise ValueError("get_gpu_distances() requires xp to be CuPy, not NumPy")
-
-        if self._gpu_distances is None:
-            # Priority: CPU cache > problem.distances > compute from coordinates
-            if self._cpu_distances is not None:
-                # Transfer from CPU cache (most efficient if CPU was used first)
-                self._gpu_distances = self.xp.asarray(self._cpu_distances)
-            elif self.problem.distances is not None:
-                # Transfer EXPLICIT matrix to GPU
-                self._gpu_distances = self.xp.asarray(self.problem.distances)
-            elif self.problem.coordinates is not None:
-                # Compute from coordinates on GPU
-                coords_gpu = self.xp.asarray(self.problem.coordinates)
-                self._gpu_distances = compute_distance_matrix(
-                    coords_gpu, self.problem.edge_type, self.xp
-                )
-            else:
-                raise ValueError(
-                    f"Problem '{self.problem.name}' has no distances or "
-                    "coordinates to compute distance matrix from."
-                )
-        return self._gpu_distances
-
- def get_gpu_coordinates(self):
-        """
-        Get coordinates on GPU (lazy with caching).
-
-        Returns:
-            Coordinates as CuPy array on GPU, or None if not available
-
-        Raises:
-            ValueError: If xp is NumPy (not CuPy)
-        """
-        if self.xp == np:
-            raise ValueError("get_gpu_coordinates() requires xp to be CuPy, not NumPy")
-
-        if self._gpu_coordinates is None and self.problem.coordinates is not None:
-            if self._cpu_coordinates is not None:
-                # Transfer from CPU cache
-                self._gpu_coordinates = self.xp.asarray(self._cpu_coordinates)
-            else:
-                # Transfer from problem data
-                self._gpu_coordinates = self.xp.asarray(self.problem.coordinates)
-        return self._gpu_coordinates
-
- def __repr__(self) -> str:
-        """String representation showing problem and backend."""
-        backend_name = "GPU (CuPy)" if hasattr(self.xp, "RawKernel") else "CPU (NumPy)"
-        return (
-            f"<ProblemContext: {self.problem.name} "
-            f"({self.problem.problem_type}, N={self.dimension}) "
-            f"on {backend_name}>"
-        )

diff --git a/code/src/protocols/strategy_protocols.py b/code/src/protocols/strategy_protocols.py
index 48c0a74..9583c7f 100644
--- a/code/src/protocols/strategy_protocols.py
+++ b/code/src/protocols/strategy_protocols.py
@@ -21,8 +21,8 @@ References:

 from typing import Protocol, List, Tuple, Any
 import numpy as np
+import numpy.typing as npt
 from ..data_models.problem import Problem
-from .backend import BackendModule

 class NeighborStrategy(Protocol):
@@ -136,7 +136,7 @@ class MutationOperator(Protocol):
         - Follow DRY principle: validate once in GeneticAlgorithm, not in every operator
     """

- def mutate(self, individual: np.ndarray) -> List[int]:

+ def mutate(self, individual: npt.NDArray[np.int64]) -> List[int]:
         """
         Mutate individual (introduce variation).

@@ -201,7 +201,7 @@ class CrossoverStrategy(Protocol):
     """

     def crossover(

-        self, parent1: np.ndarray, parent2: np.ndarray

+        self, parent1: npt.NDArray[np.int64], parent2: npt.NDArray[np.int64]
     ) -> Tuple[List[int], List[int]]:
         """
         Generate two offspring from two parents (or one offspring, depending on implementation).
@@ -270,7 +270,7 @@ class ImprovementOperator(Protocol):
         self,
         tour: List[int],
         problem: Problem,

-        xp: BackendModule,

+        xp: Any,
         max_iterations: int = 100,
     ) -> List[int]:
         """
@@ -350,8 +350,8 @@ class SelectionStrategy(Protocol):

     def select(
         self,

-        population: np.ndarray,
-        fitness: np.ndarray,

+        population: npt.NDArray[np.int64],
-        fitness: npt.NDArray[np.float64],
         n_select: int,
     ) -> List[int]:
         """
diff --git a/code/src/utils/algorithm_factory.py b/code/src/utils/algorithm_factory.py
deleted file mode 100644
index 0366905..0000000
--- a/code/src/utils/algorithm_factory.py
+++ /dev/null
@@ -1,432 +0,0 @@
-"""
-Algorithm Factory for dynamic algorithm instantiation from JSON configurations.

-

-This module provides a factory pattern for creating algorithm instances from
-JSON or dictionary configurations, enabling
-

-1. Dynamic strategy composition
-2. Configuration-driven experimentation
-3. Reproducible algorithm setups
-4. Higher-order metaheuristics support
-

-Example Usage:
>>>
- >>> # From JSON file
>>>
- >>> algorithm = AlgorithmFactory.from_json("config/ga_tournament.json")
- >>> solution = algorithm.solve(problem)
- >>>
>>>
- >>> # From dictionary
>>>
- >>> config = {
- >>>     "algorithm": "genetic_algorithm",
- >>>     "backend": "cupy",
- >>>     "strategies": {
- >>>         "selection": {"name": "tournament", "params": {"tournament_size": 3}},
- >>>         "crossover": {"name": "order_crossover", "params": {}},
- >>>         "mutation": {"name": "swap", "params": {}}
- >>>     },
- >>>     "hyperparameters": {
- >>>         "population_size": 100,
- >>>         "max_generations": 1000,
- >>>         "crossover_rate": 0.9,
- >>>         "mutation_rate": 0.1
- >>>     }
- >>> }
- >>> algorithm = AlgorithmFactory.from_dict(config)
-

-JSON Schema:

- {
-        "algorithm": str,  # "genetic_algorithm" | "simulated_annealing"
-        "backend": str,    # "numpy" | "cupy" (optional, default: "numpy")
-        "strategies": {
-            "<category>": {
-                "name": str,         # Strategy name in registry
-                "params": dict       # Strategy constructor parameters (optional)
-            }
-        },
-        "hyperparameters": dict  # Algorithm-specific hyperparameters (optional)
- }
-

-References:
- - Factory pattern: Gamma et al. (1994) - Design Patterns
- - Configuration-driven design: Fowler (2002) - Patterns of Enterprise Application Architecture
-"""
-

-from typing import Any, Dict, List
-import json
-from pathlib import Path
-

-from .strategy_registry import StrategyRegistry
-

-

-class AlgorithmFactory:

- """
- Factory for creating algorithm instances from JSON configurations.
-
- This class provides static methods for:
- 1. Loading configurations from JSON files or dictionaries
- 2. Validating configurations (algorithm types, strategies, backends)
- 3. Instantiating strategies from the registry
- 4. Creating algorithm instances with composed strategies
-
- All methods are static (no instance state needed).
- """
-
- @staticmethod
- def from_json(json_path: str) -> Any:
-        """
-        Create algorithm instance from JSON configuration file.
-
-        Parameters

-        ----------

-        json_path : str
-            Path to JSON configuration file.
-
-        Returns

-        -------

-        algorithm : Any
-            Instantiated algorithm (GeneticAlgorithm, SimulatedAnnealing, etc.)
-
-        Raises

-        ------

-        FileNotFoundError
-            If JSON file doesn't exist.
-        ValueError
-            If configuration is invalid (see validate_config for details).
-
-        Example

-        -------

-        >>> algorithm = AlgorithmFactory.from_json("configs/ga_tournament.json")
-        >>> solution = algorithm.solve(problem)
-        """
-        # Load JSON file
-        json_path = Path(json_path)
-        if not json_path.exists():
-            raise FileNotFoundError(f"Configuration file not found: {json_path}")
-
-        with open(json_path, "r") as f:
-            config = json.load(f)
-
-        # Use from_dict for actual instantiation
-        return AlgorithmFactory.from_dict(config)
-
- @staticmethod
- def from_dict(config: Dict[str, Any]) -> Any:
-        """
-        Create algorithm instance from configuration dictionary.
-
-        Parameters

-        ----------

-        config : Dict[str, Any]
-            Configuration dictionary with algorithm type, strategies, and hyperparameters.
-
-        Returns

-        -------

-        algorithm : Any
-            Instantiated algorithm with composed strategies.
-
-        Raises

-        ------

-        ValueError
-            If configuration is invalid. Error message lists all validation failures.
-
-        Example

-        -------

-        >>> config = {
-        >>>     "algorithm": "genetic_algorithm",
-        >>>     "backend": "numpy",
-        >>>     "strategies": {
-        >>>         "selection": {"name": "tournament", "params": {"tournament_size": 3}},
-        >>>         "crossover": {"name": "order_crossover"},
-        >>>         "mutation": {"name": "swap"}
-        >>>     },
-        >>>     "hyperparameters": {"population_size": 100}
-        >>> }
-        >>> algorithm = AlgorithmFactory.from_dict(config)
-        """
-        # Step 1: Validate configuration
-        errors = AlgorithmFactory.validate_config(config)
-        if errors:
-            error_msg = "Configuration validation failed:\n" + "\n".join(
-                f"  - {error}" for error in errors
-            )
-            raise ValueError(error_msg)
-
-        # Step 2: Extract configuration fields
-        algorithm_type = config["algorithm"]
-        backend = config.get("backend", "numpy")
-        strategies_config = config.get("strategies", {})
-        hyperparameters = config.get("hyperparameters", {})
-
-        # Step 3: Instantiate strategies
-        strategies = AlgorithmFactory._instantiate_strategies(
-            algorithm_type=algorithm_type,
-            strategies_config=strategies_config,
-            backend=backend,
-        )
-
-        # Step 4: Instantiate algorithm
-        algorithm = AlgorithmFactory._instantiate_algorithm(
-            algorithm_type=algorithm_type,
-            backend=backend,
-            strategies=strategies,
-            hyperparameters=hyperparameters,
-        )
-
-        return algorithm
-
- @staticmethod
- def validate_config(config: Dict[str, Any]) -> List[str]:
-        """
-        Validate configuration dictionary without instantiating.
-
-        Parameters

-        ----------

-        config : Dict[str, Any]
-            Configuration dictionary to validate.
-
-        Returns

-        -------

-        errors : List[str]
-            List of validation error messages. Empty list if valid.
-
-        Example

-        -------

-        >>> errors = AlgorithmFactory.validate_config(config)
-        >>> if errors:
-        >>>     print("Invalid configuration:")
-        >>>     for error in errors:
-        >>>         print(f"  - {error}")
-        """
-        errors = []
-
-        # Check required field: algorithm
-        if "algorithm" not in config:
-            errors.append("Missing required field 'algorithm'")
-            return errors  # Can't proceed without algorithm type
-
-        algorithm_type = config["algorithm"]
-
-        # Validate algorithm type
-        supported_algorithms = ["genetic_algorithm", "simulated_annealing"]
-        if algorithm_type not in supported_algorithms:
-            errors.append(
-                f"Unknown algorithm type '{algorithm_type}'. "
-                f"Supported: {', '.join(supported_algorithms)}"
-            )
-            return errors  # Can't proceed without valid algorithm type
-
-        # Validate backend
-        backend = config.get("backend", "numpy")
-        if backend not in ["numpy", "cupy"]:
-            errors.append(f"Unknown backend '{backend}'. Supported: 'numpy', 'cupy'")
-        elif backend == "cupy":
-            # Check if cupy is installed
-            try:
-                import cupy  # noqa: F401
-            except ImportError:
-                errors.append(
-                    "Backend 'cupy' selected but cupy is not installed. "
-                    "Install with: pip install cupy-cuda12x"
-                )
-
-        # Validate strategies field
-        strategies_config = config.get("strategies", {})
-        if not isinstance(strategies_config, dict):
-            errors.append("Field 'strategies' must be a dictionary")
-            return errors
-
-        # Check required strategies for each algorithm type
-        if algorithm_type == "genetic_algorithm":
-            required_strategies = ["selection", "crossover", "mutation"]
-            for strategy_type in required_strategies:
-                if strategy_type not in strategies_config:
-                    errors.append(
-                        f"Genetic Algorithm requires '{strategy_type}' strategy"
-                    )
-
-        elif algorithm_type == "simulated_annealing":
-            # SA requires neighborhood strategy
-            required_strategies = ["neighborhood"]
-            for strategy_type in required_strategies:
-                if strategy_type not in strategies_config:
-                    errors.append(
-                        f"Simulated Annealing requires '{strategy_type}' strategy"
-                    )
-
-        # Validate each strategy configuration
-        for category, strategy_config in strategies_config.items():
-            # Check strategy config structure
-            if not isinstance(strategy_config, dict):
-                errors.append(f"Strategy '{category}' config must be a dictionary")
-                continue
-
-            # Check required field: name
-            if "name" not in strategy_config:
-                errors.append(f"Strategy '{category}' missing required field 'name'")
-                continue
-
-            strategy_name = strategy_config["name"]
-
-            # Check if strategy exists in registry
-            try:
-                StrategyRegistry.get(category, strategy_name)
-            except ValueError as e:
-                # Registry provides helpful error message with available strategies
-                errors.append(str(e))
-
-            # Validate params field (if present)
-            if "params" in strategy_config:
-                params = strategy_config["params"]
-                if not isinstance(params, dict):
-                    errors.append(f"Strategy '{category}' params must be a dictionary")
-
-        return errors
-
- @staticmethod
- def _instantiate_strategies(
-        algorithm_type: str,
-        strategies_config: Dict[str, Dict[str, Any]],
-        backend: str,
- ) -> Dict[str, Any]:
-        """
-        Instantiate strategy objects from configuration.
-
-        Parameters

-        ----------

-        algorithm_type : str
-            Algorithm type ("genetic_algorithm", "simulated_annealing").
-        strategies_config : Dict[str, Dict[str, Any]]
-            Dictionary of strategy configurations by category.
-        backend : str
-            Backend to use ("numpy" or "cupy").
-
-        Returns

-        -------

-        strategies : Dict[str, Any]
-            Dictionary of instantiated strategy objects by category.
-
-        Raises

-        ------

-        TypeError
-            If strategy instantiation fails due to invalid parameters.
-        """
-        strategies = {}
-
-        for category, strategy_config in strategies_config.items():
-            strategy_name = strategy_config["name"]
-            strategy_params = strategy_config.get("params", {})
-
-            # Get strategy class from registry
-            strategy_class = StrategyRegistry.get(category, strategy_name)
-
-            # Instantiate with parameters
-            try:
-                strategy_instance = strategy_class(**strategy_params)
-            except TypeError as e:
-                raise TypeError(
-                    f"Failed to instantiate {category} strategy '{strategy_name}': {e}"
-                )
-
-            strategies[category] = strategy_instance
-
-        return strategies
-
- @staticmethod
- def _instantiate_algorithm(
-        algorithm_type: str,
-        backend: str,
-        strategies: Dict[str, Any],
-        hyperparameters: Dict[str, Any],
- ) -> Any:
-        """
-        Instantiate algorithm with composed strategies.
-
-        Parameters

-        ----------

-        algorithm_type : str
-            Algorithm type ("genetic_algorithm", "simulated_annealing").
-        backend : str
-            Backend to use ("numpy" or "cupy").
-        strategies : Dict[str, Any]
-            Dictionary of instantiated strategy objects.
-        hyperparameters : Dict[str, Any]
-            Algorithm-specific hyperparameters.
-
-        Returns

-        -------

-        algorithm : Any
-            Instantiated algorithm instance.
-
-        Raises

-        ------

-        NotImplementedError
-            If algorithm type not yet supported (e.g., SA in PHASE 7).
-        TypeError
-            If algorithm instantiation fails due to invalid parameters.
-        """
-        if algorithm_type == "genetic_algorithm":
-            # Import GeneticAlgorithm (lazy import to avoid circular dependencies)
-            from ..algorithms.metaheuristics.genetic_algorithm import (
-                GeneticAlgorithm,
-            )
-
-            # Get improvement strategy (optional, defaults to None)
-            improvement_strategy = strategies.get("improvement", None)
-
-            # Get construction strategy (optional, defaults to None → Random)
-            construction_strategy = strategies.get("construction", None)
-
-            # Map strategies to GA constructor parameters
-            try:
-                algorithm = GeneticAlgorithm(
-                    selection_strategy=strategies["selection"],
-                    crossover_strategy=strategies["crossover"],
-                    mutation_strategy=strategies["mutation"],
-                    improvement_strategy=improvement_strategy,  # Optional
-                    construction_strategy=construction_strategy,  # Optional (NEW)
-                    backend=backend,
-                )
-
-                # Set hyperparameters via set_params()
-                if hyperparameters:
-                    algorithm.set_params(**hyperparameters)
-
-            except TypeError as e:
-                raise TypeError(f"Failed to instantiate GeneticAlgorithm: {e}")
-
-            return algorithm
-
-        elif algorithm_type == "simulated_annealing":
-            # Import SimulatedAnnealing
-            from ..algorithms.metaheuristics.simulated_annealing import (
-                SimulatedAnnealing,
-            )
-
-            # SA requires neighborhood_strategy
-            if "neighborhood" not in strategies:
-                raise ValueError(
-                    "Simulated Annealing requires 'neighborhood' strategy in configuration"
-                )
-
-            # Get improvement strategy (optional, defaults to None)
-            improvement_strategy = strategies.get("improvement", None)
-
-            # Instantiate SA with neighborhood strategy
-            try:
-                algorithm = SimulatedAnnealing(
-                    neighbor_strategy=strategies["neighborhood"],
-                    improvement_strategy=improvement_strategy,  # Optional
-                    backend=backend,
-                )
-
-                # Set hyperparameters via set_params()
-                if hyperparameters:
-                    algorithm.set_params(**hyperparameters)
-
-            except TypeError as e:
-                raise TypeError(f"Failed to instantiate SimulatedAnnealing: {e}")
-
-            return algorithm
-
-        else:
-            # Should not reach here if validate_config passed
-            raise ValueError(f"Unsupported algorithm type '{algorithm_type}'")

diff --git a/code/tests/unit/test_backend_protocol.py b/code/tests/unit/test_backend_protocol.py
deleted file mode 100644
index 6cf274f..0000000
--- a/code/tests/unit/test_backend_protocol.py
+++ /dev/null
@@ -1,145 +0,0 @@
-"""
-Tests for backend protocol compatibility
-

-Validates that NumPy and CuPy satisfy the BackendModule protocol
-and that common operations work correctly with both backends.
-"""
-

-import numpy as np
-import pytest
-

-from src.protocols.backend import BackendModule
-

-

-def test_numpy_satisfies_protocol():

- """Verify NumPy satisfies the BackendModule protocol."""

- # This will pass type checking if NumPy satisfies the protocol

- backend: BackendModule = np
-

- # Test basic operations

- arr = backend.array([1, 2, 3, 4])
- assert arr.shape == (4,)
-

- # Test mathematical operations

- result = backend.sqrt(backend.sum(arr**2))
- expected = np.sqrt(1 + 4 + 9 + 16)
- assert abs(result - expected) < 1e-10
-
-

-def test_cupy_satisfies_protocol():

- """Verify CuPy satisfies the BackendModule protocol (if available)."""
- try:
-        import cupy as cp
- except ImportError:
-        pytest.skip("CuPy not available")
-

- # This will pass type checking if CuPy satisfies the protocol

- backend: BackendModule = cp
-

- # Test basic operations

- arr = backend.array([1, 2, 3, 4])
- assert arr.shape == (4,)
-

- # Test mathematical operations

- result = backend.sqrt(backend.sum(arr**2))
- expected = np.sqrt(1 + 4 + 9 + 16)

- # Convert CuPy result to Python float for comparison

- result_scalar = float(cp.asnumpy(result))
- assert abs(result_scalar - expected) < 1e-10
-
-

-def test_backend_array_creation():

- """Test array creation methods work with both backends."""
- backends = [np]
- try:
-        import cupy as cp
-
-        backends.append(cp)
- except ImportError:
-        pass
-
- for xp in backends:
-        # Test zeros
-        zeros = xp.zeros((3, 2))
-        assert zeros.shape == (3, 2)
-        assert xp.sum(zeros) == 0
-
-        # Test ones
-        ones = xp.ones(5)
-        assert ones.shape == (5,)
-        assert xp.sum(ones) == 5
-
-        # Test empty (just check shape)
-        empty = xp.empty((2, 2))
-        assert empty.shape == (2, 2)
-
-

-def test_backend_trigonometric_functions():

- """Test trigonometric functions needed for GEO distance."""
- backends = [np]
- try:
-        import cupy as cp
-
-        backends.append(cp)
- except ImportError:
-        pass
-
- for xp in backends:
-        # Test radians conversion
-        degrees = xp.array([0, 90, 180, 360])
-        radians = xp.radians(degrees)
-
-        # Test sin
-        sin_vals = xp.sin(radians)
-        assert abs(sin_vals[0]) < 1e-10  # sin(0) = 0
-        assert abs(sin_vals[1] - 1.0) < 1e-10  # sin(90°) = 1
-
-        # Test cos
-        cos_vals = xp.cos(radians)
-        assert abs(cos_vals[0] - 1.0) < 1e-10  # cos(0) = 1
-        assert abs(cos_vals[1]) < 1e-10  # cos(90°) = 0
-
-

-def test_backend_equivalence():

- """Verify NumPy and CuPy produce identical results for same operations."""
- try:
-        import cupy as cp
- except ImportError:
-        pytest.skip("CuPy not available for equivalence test")
-

- # Test data

- coords = np.random.rand(5, 2)
-

- # Compute with NumPy

- diff_np = coords[:, None, :] - coords[None, :, :]
- dist_np = np.sqrt(np.sum(diff_np**2, axis=2))
-

- # Compute with CuPy

- coords_cp = cp.array(coords)
- diff_cp = coords_cp[:, None, :] - coords_cp[None, :, :]
- dist_cp = cp.sqrt(cp.sum(diff_cp**2, axis=2))
-

- # Results should be identical (within floating point precision)

- np.testing.assert_allclose(dist_np, cp.asnumpy(dist_cp), rtol=1e-6)
-
-

-def test_newaxis_usage():

- """Verify None works for axis expansion (newaxis equivalent)."""
- backends = [np]
- try:
-        import cupy as cp
-
-        backends.append(cp)
- except ImportError:
-        pass
-
- for xp in backends:
-        arr = xp.array([[1, 2], [3, 4]])
-
-        # Using None for newaxis (protocol-compatible)
-        expanded = arr[:, None, :]
-        assert expanded.shape == (2, 1, 2)
-
-        # Both None and xp.newaxis should work
-        expanded2 = arr[:, xp.newaxis, :]
-        assert expanded2.shape == (2, 1, 2)

diff --git a/example_usage.py b/example_usage.py
deleted file mode 100644
index 8441106..0000000
--- a/example_usage.py
+++ /dev/null
@@ -1,243 +0,0 @@
-#!/usr/bin/env python3
-"""
-Example usage of the refactored ProblemContext-based architecture
-

-This script demonstrates:
-1. Loading a problem from the database
-2. Creating ProblemContext (precomputes distance matrix ONCE)
-3. Using different strategies with the same cached context
-4. Composing algorithms via lego_cvrp_solver
-5. GPU memory cleanup
-

-Run with: python3 example_usage.py
-"""
-

-import sys
-import numpy as np
-

-# Add code/src to path
-sys.path.insert(0, "/home/runner/work/gpu_accelerated/gpu_accelerated/code")
-

-from src.loaders.database_loader import DatabaseLoader
-from src.protocols.problem_context import ProblemContext
-from src.algorithms.strategies.tsp_strategies import NearestNeighborStrategy, ChristofidesStrategy
-from src.algorithms.strategies.bin_packing_strategies import FFDStrategy, BFDStrategy
-from src.algorithms.compositional_cvrp_solver import lego_cvrp_solver
-from src.algorithms.improvement.two_opt_cpu import TwoOptCPU
-

-

-def example_1_basic_context():

- """Example 1: Basic ProblemContext usage."""
- print("\n" + "=" * 70)
- print("EXAMPLE 1: Basic ProblemContext Usage")
- print("=" * 70)
-

- # Load a TSP problem

- with DatabaseLoader() as loader:
-        problem = loader.load('berlin52')
-
- print(f"Loaded problem: {problem.name}")
- print(f"  Dimension: {problem.dimension}")
- print(f"  Type: {problem.problem_type}")
- print(f"  Edge type: {problem.edge_type}")
-

- # Create context - distance matrix computed ONCE

- print("\nCreating ProblemContext (distance matrix computed once)...")
- context = ProblemContext(problem, xp=np)
- print(f"  {context}")
- print(f"  Distance matrix shape: {context.distances.shape}")
- print(f"  Distance matrix type: {type(context.distances)}")
-

- # Verify distance matrix is symmetric

- is_symmetric = np.allclose(context.distances, context.distances.T)
- print(f"  Distance matrix is symmetric: {is_symmetric}")
-
- return context
-
-

-def example_2_tsp_strategies(context):

- """Example 2: Using TSP strategies with shared context."""
- print("\n" + "=" * 70)
- print("EXAMPLE 2: TSP Strategies with Shared Context")
- print("=" * 70)
-

- # Select a few customers to test

- customers = [1, 2, 3, 4, 5]
- print(f"Building tours for customers: {customers}")
-

- # Strategy 1: Nearest Neighbor

- print("\n1. Nearest Neighbor Strategy:")
- nn_strategy = NearestNeighborStrategy()
- nn_tour = nn_strategy.build_tour(context, customers)
- print(f"   Tour: {nn_tour}")
- print(f"   Length: {len(nn_tour)} nodes")
-

- # Calculate tour cost

- tour_cost = 0.0
- for i in range(len(nn_tour) - 1):
-        tour_cost += context.distances[nn_tour[i], nn_tour[i+1]]
- print(f"   Cost: {tour_cost:.2f}")
-

- # Strategy 2: Christofides (if small enough)

- if len(customers) <= 10:  # Christofides is O(n³)
-        print("\n2. Christofides Strategy:")
-        ch_strategy = ChristofidesStrategy()
-        ch_tour = ch_strategy.build_tour(context, customers)
-        print(f"   Tour: {ch_tour}")
-
-        # Calculate tour cost
-        ch_cost = 0.0
-        for i in range(len(ch_tour) - 1):
-            ch_cost += context.distances[ch_tour[i], ch_tour[i+1]]
-        print(f"   Cost: {ch_cost:.2f}")
-        print(f"   Improvement over NN: {((tour_cost - ch_cost) / tour_cost * 100):.1f}%")
-
-

-def example_3_improvement():

- """Example 3: Tour improvement with 2-opt."""
- print("\n" + "=" * 70)
- print("EXAMPLE 3: Tour Improvement with 2-Opt")
- print("=" * 70)
-

- # Load a small problem

- with DatabaseLoader() as loader:
-        problem = loader.load('burma14')  # Small TSP
-
- print(f"Problem: {problem.name} ({problem.dimension} nodes)")
-

- # Create context

- context = ProblemContext(problem, xp=np)
-

- # Build initial tour with Nearest Neighbor

- customers = list(range(1, problem.dimension))
- nn_strategy = NearestNeighborStrategy()
- initial_tour = nn_strategy.build_tour(context, customers)
-

- # Calculate initial cost

- initial_cost = 0.0
- for i in range(len(initial_tour) - 1):
-        initial_cost += context.distances[initial_tour[i], initial_tour[i+1]]
-
- print(f"\nInitial tour (Nearest Neighbor):")
- print(f"  Cost: {initial_cost:.2f}")
-

- # Improve with 2-opt

- print("\nApplying 2-Opt improvement...")
- two_opt = TwoOptCPU(max_iterations=1000)
- improved_tour = two_opt.improve_tour(context, initial_tour)
-

- # Calculate improved cost

- improved_cost = 0.0
- for i in range(len(improved_tour) - 1):
-        improved_cost += context.distances[improved_tour[i], improved_tour[i+1]]
-
- print(f"Improved tour (2-Opt):")
- print(f"  Cost: {improved_cost:.2f}")
- print(f"  Improvement: {((initial_cost - improved_cost) / initial_cost * 100):.1f}%")
-
-

-def example_4_cvrp_solver():

- """Example 4: Full CVRP solving with compositional architecture."""
- print("\n" + "=" * 70)
- print("EXAMPLE 4: CVRP Solving with Lego Blocks Architecture")
- print("=" * 70)
-

- # Load a CVRP problem

- with DatabaseLoader() as loader:
-        # Try to load a CVRP instance
-        try:
-            problem = loader.load('eil22')  # Should be CVRP
-        except:
-            print("Could not load CVRP instance, using TSP instead")
-            # Create a synthetic CVRP from TSP
-            tsp_problem = loader.load('burma14')
-            from src.data_models.problem import Problem
-
-            # Add synthetic demands
-            demands = np.array([0] + [10 + i % 20 for i in range(tsp_problem.dimension - 1)])
-
-            problem = Problem(
-                name=f"{tsp_problem.name}_cvrp",
-                dimension=tsp_problem.dimension,
-                problem_type="CVRP",
-                edge_type=tsp_problem.edge_type,
-                coordinates=tsp_problem.coordinates,
-                distances=tsp_problem.distances,
-                capacity=50,
-                demands=demands,
-            )
-
- print(f"Problem: {problem.name}")
- print(f"  Dimension: {problem.dimension}")
- print(f"  Capacity: {problem.capacity}")
- print(f"  Demands: {problem.demands}")
-

- # Solve with different strategy combinations

- print("\n1. FFD + Nearest Neighbor:")
- routes_1 = lego_cvrp_solver(
-        problem,
-        bin_packing_strategy=FFDStrategy(),
-        tsp_strategy=NearestNeighborStrategy(),
-        xp=np
- )
- print(f"   Number of routes: {len(routes_1)}")
- for i, route in enumerate(routes_1):
-        print(f"   Route {i+1}: {route}")
-
- print("\n2. BFD + Nearest Neighbor + 2-Opt:")
- routes_2 = lego_cvrp_solver(
-        problem,
-        bin_packing_strategy=BFDStrategy(),
-        tsp_strategy=NearestNeighborStrategy(),
-        improvement_strategy=TwoOptCPU(max_iterations=500),
-        xp=np
- )
- print(f"   Number of routes: {len(routes_2)}")
- for i, route in enumerate(routes_2):
-        print(f"   Route {i+1}: {route}")
-
-

-def main():

- """Run all examples."""
- print("\n" + "=" * 70)
- print("GPU-ACCELERATED CVRP SOLVER - ARCHITECTURE EXAMPLES")
- print("=" * 70)
- print("\nDemonstrating ProblemContext-based architecture:")
- print("- Distance matrix computed ONCE and cached")
- print("- Strategies reuse cached data (no redundant computation)")
- print("- Clean separation of Class S (CPU) and Class P (GPU) algorithms")
-
- try:
-        # Example 1: Basic context
-        context = example_1_basic_context()
-
-        # Example 2: TSP strategies
-        example_2_tsp_strategies(context)
-
-        # Example 3: Improvement
-        example_3_improvement()
-
-        # Example 4: Full CVRP
-        example_4_cvrp_solver()
-
-        print("\n" + "=" * 70)
-        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
-        print("=" * 70)
-        print("\nKey Achievements:")
-        print("✅ Distance matrix computed once per ProblemContext")
-        print("✅ Multiple strategies reused cached distance matrix")
-        print("✅ No redundant O(n²) computations")
-        print("✅ GPU memory cleanup (when using CuPy)")
-        print("✅ Class S/P separation enforced at type level")
-
- except Exception as e:
-        print(f"\n❌ ERROR: {e}")
-        import traceback
-        traceback.print_exc()
-        return 1
-
- return 0
-
-

-if __name__ == "__main__":

- sys.exit(main())

diff --git a/scripts/validate_backend_protocol.py b/scripts/validate_backend_protocol.py
deleted file mode 100644
index 162bb66..0000000
--- a/scripts/validate_backend_protocol.py
+++ /dev/null
@@ -1,250 +0,0 @@
-#!/usr/bin/env python3
-"""
-Validate BackendModule Protocol Implementation
-

-Tests that NumPy and CuPy (if available) satisfy the BackendModule protocol
-defined in code/src/protocols/backend.py
-

-Usage:

- python scripts/validate_backend_protocol.py
-

- # Or with uv

- uv run python scripts/validate_backend_protocol.py
-"""
-

-import sys
-from typing import List, Tuple
-

-

-def test_backend_protocol(xp, backend_name: str) -> Tuple[bool, List[str]]:

- """
- Test if backend module satisfies BackendModule protocol.
-
- Args:
-        xp: Backend module (numpy or cupy)
-        backend_name: Human-readable name for reporting
-
- Returns:
-        Tuple of (success: bool, errors: List[str])
- """
- errors = []
-

- # Test array creation methods

- creation_methods = ["array", "zeros", "ones", "empty", "asarray", "arange", "full"]
-

- # Test mathematical operations

- math_methods = ["sqrt", "sum", "abs", "ceil", "floor"]
-

- # Test trigonometric functions

- trig_methods = ["sin", "cos", "arcsin", "arccos", "radians"]
-

- # Test reduction operations

- reduction_methods = ["any", "all", "max", "min", "argmax", "argmin"]
-

- # Test advanced indexing

- indexing_methods = ["ix_"]
-

- # Test constants

- constants = ["inf", "newaxis"]
-
- all_methods = (
-        creation_methods
-        + math_methods
-        + trig_methods
-        + reduction_methods
-        + indexing_methods
- )
-

- # Check methods exist

- print(f"\n{'=' * 60}")
- print(f"Testing {backend_name}")
- print(f"{'=' * 60}\n")
-
- print("Checking methods...")
- for method in all_methods:
-        if not hasattr(xp, method):
-            errors.append(f"Missing method: {method}()")
-            print(f"  ❌ {method}()")
-        else:
-            print(f"  ✅ {method}()")
-
- print("\nChecking constants...")
- for const in constants:
-        if not hasattr(xp, const):
-            errors.append(f"Missing constant: {const}")
-            print(f"  ❌ {const}")
-        else:
-            print(f"  ✅ {const}")
-

- # Functional tests

- print("\nFunctional tests...")
-
- try:
-        # Test array creation
-        arr = xp.array([1, 2, 3, 4, 5])
-        assert arr.shape == (5,), "array() failed"
-        print("  ✅ Array creation")
-
-        # Test zeros/ones
-        zeros = xp.zeros((3, 3))
-        ones = xp.ones((2, 2))
-        assert zeros.shape == (3, 3), "zeros() failed"
-        assert ones.shape == (2, 2), "ones() failed"
-        print("  ✅ zeros() and ones()")
-
-        # Test arange
-        range_arr = xp.arange(0, 10, 2)
-        assert len(range_arr) == 5, "arange() failed"
-        print("  ✅ arange()")
-
-        # Test full
-        filled = xp.full((2, 3), 7.5)
-        assert filled.shape == (2, 3), "full() failed"
-        print("  ✅ full()")
-
-        # Test math operations
-        arr_float = xp.array([1.0, 4.0, 9.0, 16.0])
-        sqrt_arr = xp.sqrt(arr_float)
-        sum_val = xp.sum(arr_float)
-        print("  ✅ sqrt() and sum()")
-
-        # Test trigonometric
-        angles = xp.array([0.0, 0.5, 1.0])
-        sin_vals = xp.sin(angles)
-        cos_vals = xp.cos(angles)
-        arccos_vals = xp.arccos(xp.array([1.0, 0.5, -1.0]))
-        print("  ✅ Trigonometric functions (sin, cos, arccos)")
-
-        # Test reductions
-        bool_arr = xp.array([True, False, True])
-        any_result = xp.any(bool_arr)
-        all_result = xp.all(bool_arr)
-        assert any_result == True, "any() failed"
-        assert all_result == False, "all() failed"
-        print("  ✅ any() and all()")
-
-        max_val = xp.max(arr)
-        min_val = xp.min(arr)
-        assert max_val == 5, "max() failed"
-        assert min_val == 1, "min() failed"
-        print("  ✅ max() and min()")
-
-        argmax_idx = xp.argmax(arr)
-        argmin_idx = xp.argmin(arr)
-        assert argmax_idx == 4, "argmax() failed"
-        assert argmin_idx == 0, "argmin() failed"
-        print("  ✅ argmax() and argmin()")
-
-        # Test fancy indexing
-        matrix = xp.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
-        subset = matrix[xp.ix_([0, 2], [0, 2])]
-        assert subset.shape == (2, 2), "ix_() failed"
-        print("  ✅ ix_() fancy indexing")
-
-        # Test constants
-        inf_val = xp.inf
-        assert inf_val > 1e100, "inf constant failed"
-        print("  ✅ inf constant")
-
-        # Test newaxis
-        expanded = arr[:, xp.newaxis]
-        assert expanded.shape == (5, 1), "newaxis failed"
-        print("  ✅ newaxis constant")
-
- except Exception as e:
-        errors.append(f"Functional test failed: {e}")
-        print(f"  ❌ Functional test error: {e}")
-

- # Backend-specific tests

- print("\nBackend-specific features...")
-
- if hasattr(xp, "asnumpy"):
-        print("  ✅ asnumpy() available (CuPy-specific)")
-        try:
-            test_arr = xp.array([1, 2, 3])
-            cpu_arr = xp.asnumpy(test_arr)
-            print(f"     Transfer test: {type(cpu_arr).__name__}")
-        except Exception as e:
-            print(f"     ⚠️  asnumpy() exists but failed: {e}")
- else:
-        print("  ℹ️  asnumpy() not available (NumPy doesn't need it)")
-
- if hasattr(xp, "get_array_module"):
-        print("  ✅ get_array_module() available (CuPy-specific)")
- else:
-        print("  ℹ️  get_array_module() not available (NumPy-only)")
-

- # Summary

- print(f"\n{'=' * 60}")
- if errors:
-        print(f"❌ {backend_name} FAILED with {len(errors)} error(s):")
-        for error in errors:
-            print(f"   - {error}")
-        return False, errors
- else:
-        print(f"✅ {backend_name} PASSED all tests")
-        print(f"{'=' * 60}\n")
-        return True, []
-
-

-def main():

- """Main validation script."""
- print("=" * 60)
- print("BackendModule Protocol Validation")
- print("=" * 60)
-
- results = {}
-

- # Test NumPy (always available)

- print("\n[1/2] Testing NumPy...")
- try:
-        import numpy as np
-
-        success, errors = test_backend_protocol(np, "NumPy (CPU)")
-        results["NumPy"] = success
- except ImportError as e:
-        print(f"❌ NumPy not available: {e}")
-        results["NumPy"] = False
-        return 1
-

- # Test CuPy (optional)

- print("\n[2/2] Testing CuPy...")
- try:
-        import cupy as cp
-
-        success, errors = test_backend_protocol(cp, "CuPy (GPU)")
-        results["CuPy"] = success
- except ImportError:
-        print("\nℹ️  CuPy not installed (optional)")
-        print("   To install: pip install cupy-cuda12x")
-        results["CuPy"] = None
- except Exception as e:
-        print(f"❌ CuPy test failed: {e}")
-        results["CuPy"] = False
-

- # Final summary

- print("\n" + "=" * 60)
- print("FINAL SUMMARY")
- print("=" * 60)
-
- for backend, status in results.items():
-        if status is True:
-            print(f"✅ {backend}: PASSED")
-        elif status is False:
-            print(f"❌ {backend}: FAILED")
-        else:
-            print(f"ℹ️  {backend}: SKIPPED (not installed)")
-
- print("=" * 60)
-

- # Exit code

- if results["NumPy"] and (results["CuPy"] in [True, None]):
-        print("\n🎉 Protocol validation successful!")
-        return 0
- else:
-        print("\n💥 Protocol validation failed!")
-        return 1
-
-

-if __name__ == "__main__":

- sys.exit(main())
diff --git a/simple_example.py b/simple_example.py
deleted file mode 100644
index 35aa32f..0000000
--- a/simple_example.py
+++ /dev/null
@@ -1,242 +0,0 @@
-#!/usr/bin/env python3
-"""
-Simple example demonstrating ProblemContext architecture without database dependency.
-

-This script creates synthetic problems and demonstrates the refactored architecture.
-"""
-

-import sys
-import numpy as np
-

-# Add code/src to path
-sys.path.insert(0, "/home/runner/work/gpu_accelerated/gpu_accelerated/code")
-

-from src.data_models.problem import Problem
-from src.protocols.problem_context import ProblemContext
-from src.algorithms.strategies.tsp_strategies import NearestNeighborStrategy
-from src.algorithms.strategies.bin_packing_strategies import FFDStrategy
-from src.algorithms.compositional_cvrp_solver import lego_cvrp_solver
-from src.algorithms.improvement.two_opt_cpu import TwoOptCPU
-

-

-def create_synthetic_problem(n=20, seed=42):

- """Create a synthetic TSP/CVRP problem for testing."""
- np.random.seed(seed)
-

- # Generate random coordinates

- coordinates = np.random.rand(n, 2) * 100  # 100x100 grid
-

- # Generate demands for CVRP

- demands = np.array([0] + list(10 + np.random.randint(0, 20, n-1)))
-
- problem = Problem(
-        name=f"synthetic_{n}",
-        dimension=n,
-        problem_type="CVRP",
-        edge_type="EUC_2D",
-        coordinates=coordinates,
-        distances=None,  # Will be computed from coordinates
-        capacity=50,
-        demands=demands,
- )
-
- return problem
-
-

-def example_1_context_caching():

- """Demonstrate distance matrix caching."""
- print("\n" + "=" * 70)
- print("EXAMPLE 1: Distance Matrix Caching in ProblemContext")
- print("=" * 70)
-
- problem = create_synthetic_problem(n=15)
- print(f"Created synthetic problem: {problem.name}")
- print(f"  Dimension: {problem.dimension} nodes")
- print(f"  Type: {problem.problem_type}")
- print(f"  Capacity: {problem.capacity}")
-

- # Create context - distance matrix computed ONCE

- print("\nCreating ProblemContext...")
- context = ProblemContext(problem, xp=np)
- print(f"  {context}")
- print(f"  Distance matrix shape: {context.distances.shape}")
- print(f"  Distance matrix type: {type(context.distances)}")
-

- # Verify it's cached (same object on repeated access)

- print(f"\nDistance matrix is cached: {context.distances is context.distances}")
-

- # Show sample distances

- print(f"\nSample distances:")
- print(f"  Distance [0→1]: {context.distances[0, 1]:.2f}")
- print(f"  Distance [1→0]: {context.distances[1, 0]:.2f} (should be same)")
- print(f"  Symmetric: {np.allclose(context.distances, context.distances.T)}")
-
-

-def example_2_tsp_strategies():

- """Demonstrate TSP strategies reusing cached context."""
- print("\n" + "=" * 70)
- print("EXAMPLE 2: Multiple Strategies Reuse Cached Distance Matrix")
- print("=" * 70)
-
- problem = create_synthetic_problem(n=10)
- print(f"Problem: {problem.name} ({problem.dimension} nodes)")
-

- # Create context ONCE

- context = ProblemContext(problem, xp=np)
- print(f"ProblemContext created (distance matrix computed once)")
-

- # Use strategy multiple times - all reuse same cached distance matrix

- customers_list = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
- strategy = NearestNeighborStrategy()
-
- print(f"\nBuilding {len(customers_list)} tours using SAME cached context:")
- for i, customers in enumerate(customers_list):
-        tour = strategy.build_tour(context, customers)
-        print(f"  Tour {i+1} (customers {customers}): {tour}")
-
- print(f"\n✅ All {len(customers_list)} tours used the SAME distance matrix (cached)")
- print(f"   No redundant O(n²) computations!")
-
-

-def example_3_improvement():

- """Demonstrate tour improvement with 2-opt."""
- print("\n" + "=" * 70)
- print("EXAMPLE 3: Tour Improvement with 2-Opt")
- print("=" * 70)
-
- problem = create_synthetic_problem(n=12, seed=123)
- context = ProblemContext(problem, xp=np)
-

- # Build initial tour

- customers = list(range(1, problem.dimension))
- nn_strategy = NearestNeighborStrategy()
- initial_tour = nn_strategy.build_tour(context, customers)
-

- # Calculate initial cost

- initial_cost = sum(
-        context.distances[initial_tour[i], initial_tour[i+1]]
-        for i in range(len(initial_tour) - 1)
- )
-
- print(f"Initial tour (Nearest Neighbor): cost = {initial_cost:.2f}")
-

- # Improve with 2-opt

- two_opt = TwoOptCPU(max_iterations=500)
- improved_tour = two_opt.improve_tour(context, initial_tour)
-

- # Calculate improved cost

- improved_cost = sum(
-        context.distances[improved_tour[i], improved_tour[i+1]]
-        for i in range(len(improved_tour) - 1)
- )
-
- print(f"Improved tour (2-Opt):         cost = {improved_cost:.2f}")
- print(f"Improvement: {((initial_cost - improved_cost) / initial_cost * 100):.1f}%")
-
-

-def example_4_cvrp_solver():

- """Demonstrate full CVRP solving."""
- print("\n" + "=" * 70)
- print("EXAMPLE 4: Full CVRP Solving with Compositional Architecture")
- print("=" * 70)
-
- problem = create_synthetic_problem(n=15, seed=789)
- print(f"Problem: {problem.name}")
- print(f"  Nodes: {problem.dimension}")
- print(f"  Capacity: {problem.capacity}")
- print(f"  Total demand: {problem.demands[1:].sum()}")
-

- # Solve with FFD + Nearest Neighbor

- print("\nSolving with FFD + Nearest Neighbor...")
- routes = lego_cvrp_solver(
-        problem,
-        bin_packing_strategy=FFDStrategy(),
-        tsp_strategy=NearestNeighborStrategy(),
-        xp=np
- )
-
- print(f"Solution: {len(routes)} routes")
- total_cost = 0.0
- for i, route in enumerate(routes):
-        # Calculate route cost
-        route_cost = 0.0
-        context = ProblemContext(problem, xp=np)  # Temporary for cost calc
-        for j in range(len(route) - 1):
-            route_cost += context.distances[route[j], route[j+1]]
-        total_cost += route_cost
-
-        # Calculate route demand
-        route_demand = sum(problem.demands[node] for node in route if node != 0)
-
-        print(f"  Route {i+1}: {len(route)-2} customers, "
-              f"demand={route_demand:.0f}/{problem.capacity}, "
-              f"cost={route_cost:.2f}")
-
- print(f"\nTotal solution cost: {total_cost:.2f}")
-

- # Solve with improvement

- print("\nSolving with FFD + Nearest Neighbor + 2-Opt...")
- routes_improved = lego_cvrp_solver(
-        problem,
-        bin_packing_strategy=FFDStrategy(),
-        tsp_strategy=NearestNeighborStrategy(),
-        improvement_strategy=TwoOptCPU(max_iterations=300),
-        xp=np
- )
-
- print(f"Solution: {len(routes_improved)} routes")
- total_cost_improved = 0.0
- for i, route in enumerate(routes_improved):
-        route_cost = 0.0
-        context = ProblemContext(problem, xp=np)
-        for j in range(len(route) - 1):
-            route_cost += context.distances[route[j], route[j+1]]
-        total_cost_improved += route_cost
-
-        route_demand = sum(problem.demands[node] for node in route if node != 0)
-        print(f"  Route {i+1}: {len(route)-2} customers, "
-              f"demand={route_demand:.0f}/{problem.capacity}, "
-              f"cost={route_cost:.2f}")
-
- print(f"\nTotal solution cost: {total_cost_improved:.2f}")
- print(f"Improvement from 2-Opt: {((total_cost - total_cost_improved) / total_cost * 100):.1f}%")
-
-

-def main():

- """Run all examples."""
- print("\n" + "=" * 70)
- print("PROBLEMCONTEXT ARCHITECTURE - SIMPLE EXAMPLES")
- print("=" * 70)
- print("\nDemonstrating the refactored architecture:")
- print("✅ Distance matrix computed ONCE and cached in ProblemContext")
- print("✅ Multiple strategies reuse the same cached matrix")
- print("✅ No redundant O(n²) distance computations")
- print("✅ GPU memory cleanup (when using CuPy)")
-
- try:
-        example_1_context_caching()
-        example_2_tsp_strategies()
-        example_3_improvement()
-        example_4_cvrp_solver()
-
-        print("\n" + "=" * 70)
-        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
-        print("=" * 70)
-        print("\nKey Achievements Demonstrated:")
-        print("  ✅ ProblemContext caches distance matrix")
-        print("  ✅ Strategies reuse cached data (no recomputation)")
-        print("  ✅ Class S (CPU) and Class P (GPU-capable) separation")
-        print("  ✅ Compositional architecture working correctly")
-        print("  ✅ GPU memory cleanup integrated")
-
-        return 0
-
- except Exception as e:
-        print(f"\n❌ ERROR: {e}")
-        import traceback
-        traceback.print_exc()
-        return 1
-
-

-if __name__ == "__main__":

- sys.exit(main())
