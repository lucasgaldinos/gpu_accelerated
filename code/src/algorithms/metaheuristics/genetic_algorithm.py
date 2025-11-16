"""
Genetic Algorithm for TSP and CVRP.

This module implements a Genetic Algorithm (GA) metaheuristic based on
Fujimoto & Tsutsui (2011) with OX crossover and optional 2-opt local search.

Algorithm Classification:
    - Class: P-Data (Parallel Data)
    - Type: Population-based evolutionary algorithm
    - Approach: Selection, crossover, mutation with optional local search

Algorithm Overview:
    1. Initialize population with random tours
    2. For each generation:
        a. For each individual i:
            - Select random parent j
            - Create offspring via OX(parent_i, parent_j)
            - Optionally apply 2-opt local search
            - Deterministic crowding: keep better of (parent_i, offspring)
        b. Track best solution and statistics
    3. Return best solution found

Reference:
    Fujimoto, N., & Tsutsui, S. (2011). A Highly-Parallel TSP Solver for
    a GPU Computing Platform. In Proceedings of NMA 2010, LNCS 6046,
    pp. 264-271. Springer-Verlag Berlin Heidelberg.

OX (Order Crossover) Operator:
    - Select two random cut points [cut1, cut2)
    - Copy segment parent2[cut1:cut2] to offspring
    - Fill remaining positions with cities from parent1 in order
    - Preserves relative ordering while introducing new subsequences

Selection Methods:
    - Deterministic Crowding: Compare offspring with same-index parent
    - Tournament Selection: Select best from k random individuals
    - Roulette Wheel: Fitness-proportionate selection

Mutation Operators:
    - Swap: Exchange two random cities
    - Inversion: Reverse random tour segment
    - Insertion: Remove city and reinsert elsewhere

Performance Characteristics:
    - Time: O(pop_size * generations * N²) with 2-opt
    - Time: O(pop_size * generations * N) without 2-opt
    - Space: O(pop_size * N) for population
    - GPU acceleration: Future enhancement for fitness evaluation

Hyperparameters:
    - population_size (int): Number of individuals (default: 60)
    - max_generations (int): Maximum generations (default: 1000)
    - crossover_rate (float): Probability of crossover (default: 0.9)
    - mutation_rate (float): Probability of mutation (default: 0.1)
    - use_2opt (bool): Apply 2-opt after crossover (default: True)
    - elitism_count (int): Number of elite solutions to preserve (default: 1)

Note:
    Selection, crossover, and mutation strategies are now injected via __init__ (Task 4.5).
    String-based configuration ("selection_method", "mutation_method") has been removed.

Statistics Dictionary:
    Required keys:
        - best_fitness: Best tour cost in final generation
        - final_fitness: Average fitness of final population
        - iterations: Total generations performed
        - convergence_history: Best cost per generation
        - runtime_seconds: Execution time
        - hyperparameters: Configuration used
    Optional keys:
        - population_diversity: Unique tours per generation
        - crossover_count: Total crossovers performed
        - mutation_count: Total mutations performed

Example Usage:
    >>> from src.algorithms.metaheuristics import GeneticAlgorithm
    >>> from src.protocols.problem_context import ProblemContext
    >>>
    >>> # Create problem context
    >>> context = ProblemContext(problem, xp=np)
    >>> customers = list(range(1, problem.dimension))
    >>>
    >>> # Configure and run GA
    >>> ga = GeneticAlgorithm()
    >>> ga.set_params(population_size=100, max_generations=500, use_2opt=True)
    >>> tour, stats = ga.build_tour_with_stats(context, customers)
    >>>
    >>> print(f"Best cost: {stats['best_fitness']:.2f}")
    >>> print(f"Population diversity: {stats['population_diversity'][-1]}")
    >>> print(f"Runtime: {stats['runtime_seconds']:.2f}s")

See Also:
    - protocols.algorithm_strategies.TspMetaheuristicStrategy
    - algorithms.improvement.two_opt_cpu for local search
    - Fujimoto & Tsutsui (2011) for algorithm details
"""

from typing import List, Dict, Any, Tuple, TYPE_CHECKING, Optional
import time
import numpy as np

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False

if TYPE_CHECKING:
    from src.protocols.problem_context import ProblemContext
    from src.protocols.callback_protocol import ProgressCallback, ProgressEvent
    from src.protocols.strategy_protocols import (
        CrossoverStrategy,
        MutationOperator,
        SelectionStrategy,
    )

# Phase 3.5: GA is CPU-only (NumPy), improvement strategies bridge to GPU
# Removed get_backend import - no longer needed


class GeneticAlgorithm:
    """
    Genetic Algorithm for TSP and CVRP using OX crossover.

    This implementation follows Fujimoto & Tsutsui (2011) with:
    - OX (Order Crossover) operator
    - Optional 2-opt local search on offspring
    - Deterministic crowding selection
    - Configurable mutation operators

    Attributes:
        _hyperparams (dict): Algorithm configuration
        _stats (dict): Optimization statistics from last run

    Example:
        >>> ga = GeneticAlgorithm()
        >>> ga.set_params(population_size=100, use_2opt=True)
        >>> tour, stats = ga.build_tour_with_stats(context, customers)
    """

    def __init__(
        self,
        crossover_strategy: "CrossoverStrategy",
        mutation_strategy: "MutationOperator",
        selection_strategy: "SelectionStrategy",
        improvement_strategy: Optional["TspImprovementStrategy"] = None,
        construction_strategy: Optional["TspConstructionStrategy"] = None,
        callback: Optional["ProgressCallback"] = None,
    ):
        """
        Initialize Genetic Algorithm with pluggable strategies.

        Phase 3.5 Hybrid Bridge Architecture:
            - S-Task operations (selection, crossover, mutation) ALWAYS run on CPU (NumPy)
            - P-Task operations (improvement strategies) handle their own GPU transfers
            - No backend parameter - GA is CPU-only by design

        Args:
            crossover_strategy: Crossover operator (e.g., OrderCrossover, PMXCrossover)
            mutation_strategy: Mutation operator (e.g., SwapMutation, InversionMutation)
            selection_strategy: Selection operator (e.g., TournamentSelection, RouletteWheelSelection)
            improvement_strategy: Local search operator (e.g., TwoOptSimpleStrategy, TwoOptGPUStrategy)
                Optional - defaults to NoImprovementStrategy() if None
                Applied to offspring AFTER crossover and mutation
                GPU improvement strategies (e.g., TwoOptGPUStrategy) handle GPU transfers internally
            construction_strategy: Initial tour construction (e.g., NearestNeighborStrategy, ChristofidesStrategy)
                Optional - defaults to RandomConstructionStrategy() if None
                Applied during population initialization for better starting quality
            callback: Optional callback for progress tracking (ProgressCallback protocol)

        Design Pattern:
            Strategy Pattern with Dependency Injection
            - Strategies passed as objects (not string configuration)
            - Type-safe (mypy validates protocol conformance)
            - Composable (any valid strategy combination works)
            - S-Task strategies (selection, crossover, mutation) use NumPy internally
            - P-Task strategies (improvement) handle their own backend internally

        Lego Brick Architecture:
            GA = Construction + Selection + Crossover + Mutation + [Improvement]
            - Each component is independently testable
            - Components are swappable at runtime
            - Improvement is optional (use NoImprovementStrategy for pure GA)
            - Construction provides better initial population (vs random)

        Example (CPU-only GA):
            >>> from code.src.algorithms.strategies.crossover_strategies import OrderCrossover
            >>> from code.src.algorithms.strategies.mutation_strategies import SwapMutation
            >>> from code.src.algorithms.strategies.selection_strategies import TournamentSelection
            >>> from code.src.algorithms.strategies.improvement_strategies import TwoOptSimpleStrategy
            >>> from code.src.algorithms.strategies.construction_strategies import NearestNeighborStrategy
            >>>
            >>> # Hybrid GA with NN initialization and CPU 2-opt
            >>> ga = GeneticAlgorithm(
            ...     crossover_strategy=OrderCrossover(),
            ...     mutation_strategy=SwapMutation(),
            ...     selection_strategy=TournamentSelection(tournament_size=3),
            ...     construction_strategy=NearestNeighborStrategy(),
            ...     improvement_strategy=TwoOptSimpleStrategy(max_iterations=10)
            ... )
            >>> ga.set_params(population_size=100, max_generations=500)
            >>> tour, stats = ga.build_tour_with_stats(context, customers)

        Example (GPU improvement via bridge):
            >>> from code.src.algorithms.strategies.improvement_strategies import TwoOptGPUStrategy
            >>>
            >>> # GA with GPU 2-opt improvement (bridge pattern)
            >>> ga = GeneticAlgorithm(
            ...     crossover_strategy=OrderCrossover(),
            ...     mutation_strategy=SwapMutation(),
            ...     selection_strategy=TournamentSelection(tournament_size=3),
            ...     improvement_strategy=TwoOptGPUStrategy(max_iterations=10)  # GPU bridge
            ... )
            >>> # S-Task operations on CPU, P-Task improvement bridges to GPU

        Breaking Change (Phase 3.5):
            Removed backend parameter - GA is now CPU-only for S-Task operations.
            Old: GeneticAlgorithm(..., backend="cupy")
            New: GeneticAlgorithm(..., improvement_strategy=TwoOptGPUStrategy())

            GPU acceleration now via improvement strategies, not global backend parameter.

        Deprecation:
            The `use_2opt` hyperparameter is DEPRECATED. Use improvement_strategy instead:
            - Old: ga.set_params(use_2opt=True)
            - New: ga = GeneticAlgorithm(..., improvement_strategy=TwoOptSimpleStrategy())
        """
        # Store strategies
        self.crossover_strategy = crossover_strategy
        self.mutation_strategy = mutation_strategy
        self.selection_strategy = selection_strategy

        # Improvement strategy (with default)
        if improvement_strategy is None:
            from ..strategies.improvement_strategies import NoImprovementStrategy

            self.improvement_strategy = NoImprovementStrategy()
        else:
            self.improvement_strategy = improvement_strategy

        # Construction strategy (with default)
        if construction_strategy is None:
            from ..strategies.construction_strategies import RandomConstructionStrategy

            self.construction_strategy = RandomConstructionStrategy()
        else:
            self.construction_strategy = construction_strategy

        # Callback for progress tracking
        self._callback = callback

        # Hyperparameters (default values)
        # NOTE: Removed string-based config: "selection_method", "mutation_method", "crossover_method"
        # NOTE: Removed "use_2opt" - now controlled via improvement_strategy
        # NOTE: Removed "backend" - S-Task operations always use NumPy (Phase 3.5)
        self._hyperparams = {
            "population_size": 60,  # Fujimoto's recommendation
            "max_generations": 1000,
            "crossover_rate": 0.9,
            "mutation_rate": 0.1,
            "elitism_count": 1,  # Number of elite solutions to preserve
        }
        self._stats = {}

    def set_params(self, **hyperparameters) -> None:
        """
        Configure Genetic Algorithm hyperparameters.

        Args:
            **hyperparameters: Keyword arguments for configuration.
                Valid keys: population_size, max_generations, crossover_rate,
                mutation_rate, tournament_size, elitism_count

        Deprecated Parameters:
            use_2opt (bool): DEPRECATED - Use improvement_strategy in __init__ instead
                If provided, will issue warning and auto-configure improvement strategy

        Example:
            >>> ga = GeneticAlgorithm(...)
            >>> ga.set_params(population_size=100, max_generations=500)
        """
        # Handle deprecated use_2opt parameter
        if "use_2opt" in hyperparameters:
            import warnings

            use_2opt = hyperparameters.pop("use_2opt")
            warnings.warn(
                "Parameter 'use_2opt' is deprecated. "
                "Use improvement_strategy in GeneticAlgorithm.__init__() instead:\n"
                "  Old: ga.set_params(use_2opt=True)\n"
                "  New: ga = GeneticAlgorithm(..., improvement_strategy=TwoOptSimpleStrategy())",
                DeprecationWarning,
                stacklevel=2,
            )

            # Auto-configure improvement strategy for backward compatibility
            if use_2opt:
                from ..strategies.improvement_strategies import TwoOptSimpleStrategy

                self.improvement_strategy = TwoOptSimpleStrategy(max_iterations=10)
            else:
                from ..strategies.improvement_strategies import NoImprovementStrategy

                self.improvement_strategy = NoImprovementStrategy()

        self._hyperparams.update(hyperparameters)

    def build_tour_with_stats(
        self, context: "ProblemContext", customers: List[int]
    ) -> Tuple[List[int], Dict[str, Any]]:
        """
        Solve TSP/CVRP using Genetic Algorithm (CPU-only for S-Task operations).

        Phase 3.5 Hybrid Bridge Architecture:
            - S-Task operations (selection, crossover, mutation) run on CPU with NumPy
            - P-Task operations (improvement strategies) may bridge to GPU internally
            - No GPU VRAM check needed - GA is CPU-only by design

        Args:
            context: ProblemContext with distances (may be NumPy or CuPy)
            customers: List of customer indices (excluding depot 0)

        Returns:
            Tuple of (tour, statistics) where:
                - tour: [depot, c1, c2, ..., ck, depot]
                - statistics: Dictionary with convergence and performance metrics

        Raises:
            ValueError: If customers list is empty

        Example:
            >>> tour, stats = ga.build_tour_with_stats(context, [1, 2, 3, 4, 5])
            >>> print(f"Best cost: {stats['best_fitness']:.2f}")
        """
        # Validation
        if len(customers) == 0:
            raise ValueError("customers list cannot be empty")

        # Phase 3.5: S-Task operations ALWAYS use NumPy (CPU-only)
        pop_size = self._hyperparams["population_size"]
        max_gen = self._hyperparams["max_generations"]
        crossover_rate = self._hyperparams["crossover_rate"]
        mutation_rate = self._hyperparams["mutation_rate"]

        # Stage 4: Create GPU-aware fitness calculator
        # Eliminates premature GPU→CPU transfers (6.6× slowdown fix)
        from ..fitness_calculators import GACostCalculatorGPU

        fitness_calculator = GACostCalculatorGPU(context)

        # Start timing
        start_time = time.time()

        # Initialize population (using construction strategy)
        # Stage 4: Returns NumPy array directly (efficient initialization)
        population = self._initialize_population(context, customers, pop_size)

        # Stage 4: Use GPU-aware fitness calculator
        # Calculator performs efficient bulk transfer if CuPy backend
        # Returns NumPy array (CPU) regardless of backend
        fitness = fitness_calculator.compute_batch_fitness(population)

        # Track statistics (all CPU operations - fitness is NumPy array)
        best_idx = int(np.argmin(fitness))
        best_tour = population[best_idx].copy()
        best_cost = float(fitness[best_idx])

        convergence_history = [best_cost]
        # Diversity: Convert numpy array rows to tuples for set uniqueness check
        diversity_history = [len(set(map(tuple, population.tolist())))]
        crossover_count = 0
        mutation_count = 0

        # Lifecycle: START
        if self._callback:
            from src.protocols.callback_protocol import ProgressEvent

            event: ProgressEvent = {
                "iteration": 0,
                "best_cost": best_cost,
                "current_cost": best_cost,
                "elapsed_time": time.time() - start_time,
            }
            self._callback.on_start(event)

        # Main GA loop
        for generation in range(max_gen):
            # Vectorized parent selection (Task 4.5: Strategy pattern)
            # Select pop_size parent indices using strategy
            # Phase 3.5: Strategies use NumPy internally (no xp parameter)
            # Stage 4: Pass numpy arrays directly (protocol uses Any types, converts internally)
            parent_indices = self.selection_strategy.select(
                population=population, fitness=fitness, n_select=pop_size
            )

            # Generate offspring
            offspring = []

            for i in range(pop_size):
                # Get parents using strategy-based selection
                parent1 = population[i]
                parent2 = population[parent_indices[i]]

                # Crossover using strategy (Task 4.5: Strategy pattern)
                # Phase 3.5: Strategies use NumPy internally (no xp parameter)
                if float(context.rng.rand()) < crossover_rate:
                    child = self.crossover_strategy.crossover(
                        parent1=parent1, parent2=parent2, problem=None
                    )
                    crossover_count += 1
                else:
                    child = parent1.copy()

                # Apply mutation strategy (Phase 3.5: NumPy internally)
                if float(context.rng.rand()) < mutation_rate:
                    child = self.mutation_strategy.mutate(tour=child, problem=None)
                    mutation_count += 1

                offspring.append(child)

            # Apply improvement strategy (e.g., 2-opt local search)
            # Phase 3: Use batch API if available (GPU parallel processing)
            # Otherwise fallback to sequential (CPU or strategies without batch API)
            if hasattr(self.improvement_strategy, "improve_batch"):
                # Batch improvement: Process all offspring in parallel (Class P-Data)
                offspring = self.improvement_strategy.improve_batch(context, offspring)
            else:
                # Sequential improvement: Process one at a time (fallback)
                for i in range(len(offspring)):
                    offspring[i] = self.improvement_strategy.improve_tour(
                        context, offspring[i]
                    )

            # Stage 4 Fix: Convert offspring to NumPy array for efficient GPU transfer
            # Enables bulk transfer (NumPy → CuPy) instead of slow List → CuPy
            offspring_array = np.array(offspring, dtype=np.int32)

            # Stage 4: Use GPU-aware fitness calculator for offspring
            # Calculator performs efficient bulk transfer if CuPy backend
            # Returns NumPy array (CPU) regardless of backend
            offspring_fitness = fitness_calculator.compute_batch_fitness(offspring_array)

            # Survival selection: Combine populations and select best
            # Stage 4 Fix: Work with numpy arrays throughout
            combined_pop = np.vstack([population, offspring_array])
            combined_fit = np.concatenate([fitness, offspring_fitness])
            
            # Select best pop_size individuals
            indices = np.argsort(combined_fit)[:pop_size]
            population = combined_pop[indices]
            fitness = combined_fit[indices]

            # Update best solution
            gen_best_idx = int(np.argmin(fitness))
            if fitness[gen_best_idx] < best_cost:
                best_tour = population[gen_best_idx].copy()
                best_cost = float(fitness[gen_best_idx])

            # Track statistics
            convergence_history.append(best_cost)
            # Diversity: Convert numpy array rows to tuples for set uniqueness check
            diversity_history.append(len(set(map(tuple, population.tolist()))))

            # Lifecycle: ITERATION
            if self._callback:
                from src.protocols.callback_protocol import ProgressEvent

                event: ProgressEvent = {
                    "iteration": generation + 1,  # 1-indexed for user clarity
                    "best_cost": best_cost,
                    "current_cost": float(np.mean(fitness)),
                    "elapsed_time": time.time() - start_time,
                }
                self._callback.on_iteration(event)

        # End timing
        runtime = time.time() - start_time

        # Lifecycle: COMPLETE
        if self._callback:
            from src.protocols.callback_protocol import ProgressEvent

            event: ProgressEvent = {
                "iteration": max_gen,
                "best_cost": best_cost,
                "current_cost": float(np.mean(fitness)),
                "elapsed_time": runtime,
            }
            self._callback.on_complete(event)

        # Compile statistics
        self._stats = {
            "best_fitness": float(best_cost),
            "final_fitness": float(np.mean(fitness)),
            "iterations": max_gen,
            "convergence_history": convergence_history,
            "runtime_seconds": runtime,
            "hyperparameters": self._hyperparams.copy(),
            "population_diversity": diversity_history,
            "crossover_count": crossover_count,
            "mutation_count": mutation_count,
        }

        return best_tour, self._stats

    def get_stats(self) -> Dict[str, Any]:
        """
        Retrieve statistics from most recent optimization run.

        Returns:
            Copy of statistics dictionary with keys:
                - best_fitness: Best tour cost found
                - final_fitness: Average fitness of final population
                - iterations: Total generations performed
                - convergence_history: Best cost per generation
                - runtime_seconds: Execution time
                - hyperparameters: Configuration used
                - population_diversity: Unique tours per generation
                - crossover_count: Total crossovers performed
                - mutation_count: Total mutations performed

        Example:
            >>> stats = ga.get_stats()
            >>> print(f"Final diversity: {stats['population_diversity'][-1]}")
        """
        return self._stats.copy()

    # ========== Private Helper Methods ==========

    def _initialize_population(
        self, context: "ProblemContext", customers: List[int], pop_size: int
    ) -> np.ndarray:
        """
        Initialize population using construction strategy.

        Stage 4 Update: Returns NumPy array directly for efficiency.

        Args:
            context: ProblemContext with distance matrix and backend
            customers: List of customer indices
            pop_size: Population size

        Returns:
            NumPy array of tours, shape (pop_size, tour_length)
                - Each row: [depot, c1, ..., ck, depot]
                - dtype: int32

        Notes:
            Uses injected construction_strategy (RandomConstructionStrategy by default,
            or NearestNeighborStrategy/Christofides for better quality).

            For diversity, each tour is constructed independently (strategy may use
            randomness internally, e.g., random nearest-neighbor tie-breaking).
        """
        population_list = []
        for _ in range(pop_size):
            # Use construction strategy to build each tour
            tour = self.construction_strategy.build_tour(context, customers)
            population_list.append(tour)
        
        # Convert to numpy array once (efficient bulk conversion)
        return np.array(population_list, dtype=np.int32)


