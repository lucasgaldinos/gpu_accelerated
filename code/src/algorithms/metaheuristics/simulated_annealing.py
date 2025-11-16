"""
Simulated Annealing for TSP and CVRP.

This module implements the Simulated Annealing metaheuristic for solving
routing problems using probabilistic acceptance of moves.

Algorithm Classification:
    - Class: S-Task (Sequential Task)
    - Type: Single-trajectory metaheuristic
    - Approach: Probabilistic local search with temperature-based acceptance
    - Note: P-Data multistart variant planned for M18 (Streaming Architecture)

Future Extensions:
    - P-Data Variant (M18): Parallel multistart with stream compaction
      * Launch N independent S-Task trajectories on GPU using CUDA streams
      * Each stream executes one S-Task SA instance
      * Collect best solution across all trajectories
      * Reference: METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 4 (Streaming)
      * Hardware Requirements: CUDA streams + unified memory
      * Benefit: Process multiple independent searches simultaneously

Algorithm Overview:
    1. Initialize with greedy solution (nearest neighbor)
    2. Set temperature T = initial_temp
    3. While T > min_temp and iterations < max_iterations:
        a. Generate neighbor solution via neighbor_strategy
        b. Calculate delta = new_cost - current_cost
        c. Accept if delta < 0 (improvement)
        d. Accept with probability exp(-delta/T) if delta >= 0
        e. Cool temperature: T = cooling_function(T, iteration)
    4. Return best solution found during search

Neighbor Generation (Lego Brick Architecture):
    - Accepts NeighborStrategy instance (RandomSwapStrategy, Random2OptStrategy, etc.)
    - Strategies are composable and testable independently
    - Examples:
        * RandomSwapStrategy: Swap two random cities
        * RandomInsertionStrategy: Remove city, reinsert elsewhere
        * Random2OptStrategy: Reverse random tour segment

Cooling Schedules:
    - Geometric: T_new = alpha * T_old (default alpha=0.95)
    - Linear: T_new = T_old - beta (beta = (T_init - T_min) / max_iter)
    - Adaptive: Adjust cooling based on acceptance rate

Performance Characteristics:
    - Time: O(N * iterations) for neighbor evaluation
    - Space: O(N) for current and best tours
    - Typical iterations: 1000-10000 depending on problem size
    - GPU acceleration: Future enhancement for batch neighbor evaluation

Hyperparameters:
    - neighbor_strategy (NeighborStrategy): Strategy for neighbor generation (REQUIRED)
    - initial_temp (float): Starting temperature (default: 1000.0)
    - cooling_rate (float): Geometric cooling factor (default: 0.95)
    - max_iterations (int): Maximum iterations (default: 1000)
    - min_temp (float): Stopping temperature (default: 0.01)
    - schedule (str): 'geometric', 'linear', or 'adaptive' (default: 'geometric')

Statistics Dictionary:
    Required keys:
        - best_fitness: Best tour cost found during search
        - final_fitness: Final tour cost at end of search
        - iterations: Total iterations performed
        - convergence_history: List of best costs per iteration
        - runtime_seconds: Execution time in seconds
        - hyperparameters: Dictionary of configuration used
    Optional keys:
        - temperature_schedule: List of temperature values
        - acceptance_rate: Proportion of moves accepted

Example Usage:
    >>> from src.algorithms.metaheuristics import SimulatedAnnealing
    >>> from src.algorithms.strategies import RandomSwapStrategy
    >>> from src.protocols.problem_context import ProblemContext
    >>>
    >>> # Create problem context
    >>> context = ProblemContext(problem, xp=np)
    >>> customers = list(range(1, problem.dimension))
    >>>
    >>> # Configure and run SA with strategy
    >>> sa = SimulatedAnnealing(neighbor_strategy=RandomSwapStrategy())
    >>> sa.set_params(initial_temp=2000, max_iterations=5000)
    >>> tour, stats = sa.build_tour_with_stats(context, customers)
    >>>
    >>> print(f"Best cost: {stats['best_fitness']:.2f}")
    >>> print(f"Acceptance rate: {stats['acceptance_rate']:.2%}")
    >>> print(f"Runtime: {stats['runtime_seconds']:.2f}s")

See Also:
    - protocols.algorithm_strategies.TspMetaheuristicStrategy
    - algorithms.construction.nearest_neighbor for initial solution
    - algorithms.improvement.two_opt for local search comparison
"""

from typing import List, Dict, Any, Tuple, TYPE_CHECKING, Optional
import time
import numpy as np

from ...protocols.strategy_protocols import NeighborStrategy

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False

if TYPE_CHECKING:
    from src.protocols.problem_context import ProblemContext
    from src.protocols.callback_protocol import ProgressCallback, ProgressEvent


class SimulatedAnnealing:
    """
    Simulated Annealing metaheuristic for TSP and CVRP.

    This implementation satisfies the TspMetaheuristicStrategy protocol
    with support for multiple neighbor generation methods and cooling schedules.

    Attributes:
        _hyperparams (dict): Algorithm configuration
        _stats (dict): Optimization statistics from last run

    Example:
        >>> sa = SimulatedAnnealing()
        >>> sa.set_params(initial_temp=1500, max_iterations=3000)
        >>> tour, stats = sa.build_tour_with_stats(context, customers)
    """

    def __init__(
        self,
        neighbor_strategy: NeighborStrategy,
        improvement_strategy: Optional["TspImprovementStrategy"] = None,
        callback: Optional["ProgressCallback"] = None,
    ):
        """
        Initialize Simulated Annealing with strategy-based neighbor generation.

        Args:
            neighbor_strategy: NeighborStrategy instance (REQUIRED)
                Examples: RandomSwapStrategy(), Random2OptStrategy(), RandomInsertionStrategy()
            improvement_strategy: Local search operator (e.g., TwoOptSimpleStrategy, NoImprovementStrategy)
                Optional - defaults to NoImprovementStrategy() if None
                Applied to accepted moves AFTER acceptance (Option B from literature)
                Note: Applying to EVERY neighbor would be too expensive (Option A)
            callback: Optional callback for progress tracking (ProgressCallback protocol)

        Default configuration:
            - initial_temp: 1000.0
            - cooling_rate: 0.95 (for geometric schedule)
            - max_iterations: 1000
            - min_temp: 0.01
            - schedule: 'geometric'

        Lego Brick Architecture:
            SA = Neighbor Generation + Acceptance Criterion + [Improvement]
            - Each component is independently testable
            - Components are swappable at runtime
            - Improvement is optional (use NoImprovementStrategy for pure SA)

        Literature Basis (Improvement Timing):
            - Hoos & Stützle (2005): Hybrid metaheuristics apply local search to accepted solutions
            - This implementation uses Option B: improve AFTER acceptance
            - Alternative approaches:
                * Option A: Improve every neighbor (too expensive)
                * Option C: Improve only at end (separate post-processing stage)

        Example:
            >>> from code.src.algorithms.strategies import RandomSwapStrategy
            >>> from code.src.algorithms.strategies.improvement_strategies import TwoOptSimpleStrategy
            >>>
            >>> # Hybrid SA with local search
            >>> sa = SimulatedAnnealing(
            ...     neighbor_strategy=RandomSwapStrategy(),
            ...     improvement_strategy=TwoOptSimpleStrategy(max_iterations=5),
            ...     backend="numpy"
            ... )
            >>>
            >>> # Pure SA without improvement
            >>> sa_pure = SimulatedAnnealing(
            ...     neighbor_strategy=RandomSwapStrategy(),
            ...     improvement_strategy=None,  # Defaults to NoImprovementStrategy
            ...     backend="numpy"
            ... )

        Backend Configuration:
            See: Backend Configuration Architecture in M14_M15_DETAILED_TASKS.md
            Pattern: Hierarchical backend (SA backend != strategy backend is valid)

        BREAKING CHANGE (M14.3.4):
            OLD: SimulatedAnnealing(callback=...) with neighbor_method in set_params
            NEW: SimulatedAnnealing(neighbor_strategy=RandomSwapStrategy())

        Migration Guide:
            OLD: sa = SimulatedAnnealing()
                 sa.set_params(neighbor_method='swap')
            NEW: sa = SimulatedAnnealing(neighbor_strategy=RandomSwapStrategy())

        P-Data Compatibility (Future M18):
            The backend="numpy" default is FORWARD-COMPATIBLE with P-Data multistart.
            When P-Data is implemented, it will instantiate multiple S-Task (SA) objects,
            each with its own backend parameter:

            Example (M18 future):
                >>> # P-Data orchestrator creates N parallel S-Tasks
                >>> class ParallelMultistartSA:
                ...     def __init__(self, n_starts=10, backend="cupy"):
                ...         self.workers = [
                ...             SimulatedAnnealing(strategy=..., backend=backend)
                ...             for _ in range(n_starts)
                ...         ]

            No changes to S-Task backend parameter needed when M18 is implemented.
        """
        self.neighbor_strategy = neighbor_strategy

        # Improvement strategy (with default)
        if improvement_strategy is None:
            from ..strategies.improvement_strategies import NoImprovementStrategy

            self.improvement_strategy = NoImprovementStrategy()
        else:
            self.improvement_strategy = improvement_strategy

        self._callback = callback
        self._hyperparams = {
            "initial_temp": 1000.0,
            "cooling_rate": 0.95,
            "max_iterations": 1000,
            "min_temp": 0.01,
            "schedule": "geometric",  # 'geometric', 'linear', 'adaptive'
        }
        self._stats = {}

    def set_params(self, **hyperparameters) -> None:
        """
        Configure Simulated Annealing hyperparameters.

        Args:
            **hyperparameters: Keyword arguments for configuration.
                Valid keys: initial_temp, cooling_rate, max_iterations,
                min_temp, neighbor_method, schedule

        Example:
            >>> sa.set_params(initial_temp=2000, max_iterations=5000)
            >>> sa.set_params(neighbor_method='swap', schedule='adaptive')
        """
        self._hyperparams.update(hyperparameters)

    def build_tour_with_stats(
        self, context: "ProblemContext", customers: List[int]
    ) -> Tuple[List[int], Dict[str, Any]]:
        """
        Solve TSP/CVRP using Simulated Annealing.

        Args:
            context: ProblemContext with distances and backend
            customers: List of customer indices (excluding depot 0)

        Returns:
            Tuple of (tour, statistics) where:
                - tour: [depot, c1, c2, ..., ck, depot]
                - statistics: Dictionary with convergence and performance metrics

        Raises:
            ValueError: If context backend is invalid
            ValueError: If customers list is empty

        Example:
            >>> tour, stats = sa.build_tour_with_stats(context, [1, 2, 3, 4, 5])
            >>> print(f"Best cost: {stats['best_fitness']:.2f}")
        """
        # Validation
        if len(customers) == 0:
            raise ValueError("customers list cannot be empty")

        # Get CPU-native distance matrix (S-Task: CPU-only operations)
        # Use context.get_cpu_distances() for efficient access - returns CPU array
        # without copy if already on CPU, avoiding unnecessary GPU→CPU transfer
        distances_np = context.get_cpu_distances()

        # Create CPU-native RNG for S-Task operations (modern Generator API)
        # This ensures all random operations (neighbor, acceptance) are deterministic
        rng_cpu = np.random.default_rng(context.seed)

        # Extract hyperparameters
        initial_temp = self._hyperparams["initial_temp"]
        max_iterations = self._hyperparams["max_iterations"]
        min_temp = self._hyperparams["min_temp"]
        schedule = self._hyperparams["schedule"]

        # Start timing
        start_time = time.time()

        # Generate initial solution (greedy nearest neighbor)
        current_tour = self._generate_initial_solution(customers, distances_np)
        current_cost = self._compute_tour_cost(current_tour, distances_np)

        # Track best solution
        best_tour = current_tour.copy()
        best_cost = current_cost

        # Buffer Reuse Pattern (M14.3.4.4): Pre-allocate neighbor buffer
        # Reduces allocation overhead from O(iterations) to O(1)
        # Reference: METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 2.2
        neighbor_buffer = (
            current_tour.copy()
        )  # Reusable buffer for strategies that support it
        supports_inplace = hasattr(self.neighbor_strategy, "generate_neighbor_inplace")

        # Statistics tracking
        convergence_history = [best_cost]
        temperature_schedule = [initial_temp]
        accepted_moves = 0
        total_moves = 0

        # Lifecycle: START
        if self._callback:
            from src.protocols.callback_protocol import ProgressEvent

            event: ProgressEvent = {
                "iteration": 0,
                "best_cost": best_cost,
                "current_cost": current_cost,
                "elapsed_time": time.time() - start_time,
                "temperature": initial_temp,
                "acceptance_rate": 0.0,
            }
            self._callback.on_start(event)

        # Simulated Annealing main loop
        temperature = initial_temp
        iteration = 0

        while temperature > min_temp and iteration < max_iterations:
            # Generate neighbor using strategy (Lego Brick architecture)
            # Buffer Reuse Pattern: Check if strategy supports in-place generation
            # Backward compatible: falls back to allocation if not supported
            if supports_inplace:
                self.neighbor_strategy.generate_neighbor_inplace(
                    current_tour, neighbor_buffer, context.problem, rng_cpu
                )
                neighbor_tour = neighbor_buffer
            else:
                # Fallback: allocate new tour (current behavior)
                # Pass CPU-native RNG for deterministic neighbor generation (S-Task)
                neighbor_tour = self.neighbor_strategy.generate_neighbor(
                    current_tour, context.problem, rng_cpu
                )

            neighbor_cost = self._compute_tour_cost(neighbor_tour, distances_np)

            # Calculate delta
            delta = neighbor_cost - current_cost

            # Acceptance decision (using CPU RNG for S-Task)
            if self._accept_move(delta, temperature, rng_cpu):
                # Accept the move
                current_tour = neighbor_tour
                current_cost = neighbor_cost
                accepted_moves += 1

                # Apply improvement strategy to accepted moves (Option B from literature)
                # This is the "Lego Brick" composition: SA + Local Search
                # NOTE: Improvement is applied AFTER acceptance, not to every neighbor
                current_tour = self.improvement_strategy.improve_tour(
                    context, current_tour
                )
                # Recompute cost after improvement
                current_cost = self._compute_tour_cost(current_tour, distances_np)

                # Update best if improved
                if current_cost < best_cost:
                    best_tour = current_tour.copy()
                    best_cost = current_cost

            total_moves += 1

            # Cool temperature
            temperature = self._cool_temperature(
                temperature, iteration, schedule, initial_temp, min_temp, max_iterations
            )

            # Track statistics
            convergence_history.append(best_cost)
            temperature_schedule.append(temperature)

            # Lifecycle: ITERATION (call every iteration, tracker throttles internally)
            if self._callback:
                from src.protocols.callback_protocol import ProgressEvent

                acceptance_rate = (
                    accepted_moves / total_moves if total_moves > 0 else 0.0
                )
                event: ProgressEvent = {
                    "iteration": iteration,
                    "best_cost": best_cost,
                    "current_cost": current_cost,
                    "elapsed_time": time.time() - start_time,
                    "temperature": temperature,
                    "acceptance_rate": acceptance_rate,
                }
                self._callback.on_iteration(event)

            iteration += 1

        # End timing
        runtime = time.time() - start_time

        # Lifecycle: COMPLETE
        if self._callback:
            from src.protocols.callback_protocol import ProgressEvent

            final_acceptance_rate = (
                accepted_moves / total_moves if total_moves > 0 else 0.0
            )
            event: ProgressEvent = {
                "iteration": iteration,
                "best_cost": best_cost,
                "current_cost": current_cost,
                "elapsed_time": runtime,
                "temperature": temperature,
                "acceptance_rate": final_acceptance_rate,
            }
            self._callback.on_complete(event)

        # Calculate acceptance rate
        acceptance_rate = accepted_moves / total_moves if total_moves > 0 else 0.0

        # Compile statistics
        self._stats = {
            "best_fitness": float(best_cost),
            "final_fitness": float(current_cost),
            "iterations": iteration,
            "convergence_history": convergence_history,
            "runtime_seconds": runtime,
            "hyperparameters": self._hyperparams.copy(),
            "temperature_schedule": temperature_schedule,
            "acceptance_rate": acceptance_rate,
        }

        return best_tour, self._stats

    def get_stats(self) -> Dict[str, Any]:
        """
        Retrieve statistics from most recent optimization run.

        Returns:
            Copy of statistics dictionary with keys:
                - best_fitness: Best tour cost found
                - final_fitness: Final tour cost
                - iterations: Total iterations performed
                - convergence_history: Cost progression
                - runtime_seconds: Execution time
                - hyperparameters: Configuration used
                - temperature_schedule: Temperature values
                - acceptance_rate: Proportion of accepted moves

        Example:
            >>> stats = sa.get_stats()
            >>> print(f"Final acceptance rate: {stats['acceptance_rate']:.2%}")
        """
        return self._stats.copy()

    # ========== Private Helper Methods ==========

    def _generate_initial_solution(
        self, customers: List[int], distances
    ) -> List[int]:
        """
        Generate initial solution using greedy nearest neighbor.

        Args:
            customers: List of customer indices
            distances: Distance matrix (numpy or cupy array)

        Returns:
            Initial tour [depot, c1, c2, ..., ck, depot]
        """
        # Greedy nearest neighbor construction
        # Pure Python loop (S-Task) - works with any array backend
        unvisited = set(customers)
        tour = [0]  # Start at depot
        current = 0

        while unvisited:
            # Find nearest unvisited customer
            # Note: This is sequential by design (greedy construction)
            # Could vectorize with masks, but adds complexity for minimal gain
            nearest = min(unvisited, key=lambda c: float(distances[current, c]))
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        tour.append(0)  # Return to depot
        return tour

    def _compute_tour_cost(self, tour: List[int], distances) -> float:
        """
        Compute total cost of tour using CPU-native NumPy operations.

        Args:
            tour: Tour [depot, c1, ..., ck, depot]
            distances: Distance matrix (NumPy array on CPU)

        Returns:
            Total tour cost (sum of edge weights)
        """
        # Convert tour to numpy array (CPU S-Task operation)
        tour_array = np.array(tour)

        # Vectorized edge cost computation (NumPy indexing)
        edge_costs = distances[tour_array[:-1], tour_array[1:]]

        # Use np.sum() for 100% NumPy operation (no potential GPU kernel launch)
        return float(np.sum(edge_costs))

    def _accept_move(self, delta: float, temperature: float, rng_cpu) -> bool:
        """
        Determine whether to accept a move using Metropolis criterion.

        Args:
            delta: Cost change (new_cost - current_cost)
            temperature: Current temperature
            rng_cpu: NumPy Generator for CPU-native random numbers (S-Task)

        Returns:
            True if move should be accepted, False otherwise
        """
        if delta < 0:
            # Always accept improvements
            return True

        # Metropolis acceptance criterion (S-Task CPU operation)
        # Use CPU RNG to avoid GPU overhead (Hybrid Bridge pattern)
        probability = float(np.exp(-delta / temperature))
        return float(rng_cpu.random()) < probability

    def _cool_temperature(
        self,
        temperature: float,
        iteration: int,
        schedule: str,
        initial_temp: float,
        min_temp: float,
        max_iterations: int,
    ) -> float:
        """
        Cool temperature according to specified schedule.

        Args:
            temperature: Current temperature
            iteration: Current iteration number
            schedule: Cooling schedule type
            initial_temp: Starting temperature
            min_temp: Minimum temperature
            max_iterations: Maximum iterations

        Returns:
            New temperature value
        """
        if schedule == "geometric":
            # Geometric cooling: T_new = alpha * T_old
            return temperature * self._hyperparams["cooling_rate"]

        elif schedule == "linear":
            # Linear cooling: T_new = T_old - beta
            beta = (initial_temp - min_temp) / max_iterations
            return max(temperature - beta, min_temp)

        elif schedule == "adaptive":
            # Adaptive cooling based on acceptance rate
            # (Simplified version - could be enhanced)
            # Cool faster if accepting too many moves, slower if rejecting too many
            acceptance_rate = self._stats.get("acceptance_rate", 0.5)
            if acceptance_rate > 0.8:
                # Accepting too many - cool faster
                return temperature * 0.90
            elif acceptance_rate < 0.2:
                # Rejecting too many - cool slower
                return temperature * 0.98
            else:
                # Normal cooling
                return temperature * self._hyperparams["cooling_rate"]

        else:
            # Default to geometric
            return temperature * self._hyperparams["cooling_rate"]
