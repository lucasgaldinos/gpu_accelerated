"""
Strategy protocols for algorithm composition (Lego Brick Architecture).

Enables pluggable operators for metaheuristics:
- SimulatedAnnealing accepts NeighborStrategy
- GeneticAlgorithm accepts CrossoverStrategy, MutationOperator, ImprovementOperator

Design Philosophy:
- Protocols over inheritance (duck typing + type safety)
- Single Responsibility (each protocol does ONE thing)
- Semantic clarity (Neighbor vs Mutation vs Improvement)

Type Safety:
- Runtime: Python's structural subtyping (duck typing)
- Compile-time: mypy validates protocol compliance

References:
- PEP 544: Protocols (Structural Subtyping)
- Gang of Four: Strategy Pattern
"""

from typing import Protocol, List, Tuple, Any
import numpy as np
from ..data_models.problem import Problem
from .backend import BackendModule


class NeighborStrategy(Protocol):
    """
    Generate neighbor solution for local search metaheuristics.

    Semantic Context:
        Used by: Simulated Annealing, Tabu Search, Iterated Local Search
        Purpose: Explore solution space via single-move modifications
        Frequency: Called O(iterations) times per solve()

    Key Characteristics:
        - Single neighbor generation (not exhaustive search)
        - Stochastic (uses CPU-native NumPy RNG for determinism)
        - May use problem context (distances for move evaluation)

    Examples:
        - RandomSwapStrategy: Swap two random cities
        - RandomInsertionStrategy: Remove city, reinsert elsewhere
        - Random2OptStrategy: Reverse random tour segment
        - TwoOptMoveStrategy: Best single 2-opt move (uses distances)

    Comparison with ImprovementOperator:
        - Neighbor: Single move generation (SA's job to accept/reject)
        - Improvement: Iterative search until local optimum

    Validation Responsibilities:
        - Metaheuristic validates inputs ONCE (tour dimensions, depot positions)
        - Strategies ASSUME valid inputs (no duplicate validation)
        - Strategies MAY add domain-specific validation (e.g., CVRP capacity constraints)
        - Follow DRY principle: validate once at entry point, not in every strategy
    
    Hybrid Bridge Compliance (S-Task):
        - NeighborStrategy is S-Task (sequential, CPU-only)
        - Must use explicit NumPy Generator (rng parameter) for determinism
        - Cannot use backend-agnostic xp parameter (removed in Stage 5)
        - This ensures consistent random sequences across NumPy/CuPy contexts
    """

    def generate_neighbor(
        self, current_tour: List[int], problem: Problem, rng: Any
    ) -> List[int]:
        """
        Generate neighbor from current tour using CPU-native RNG.

        Args:
            current_tour: Current solution [depot, c1, c2, ..., ck, depot]
                - First and last elements are depot (typically 0)
                - Length: n+1 for n-city TSP
            problem: Problem instance
                - problem.distances: (n, n) distance matrix
            rng: NumPy Generator for deterministic random number generation
                - CPU-native (S-Task requirement)
                - Modern API: np.random.default_rng(seed)
                - Use rng.integers() instead of legacy randint()
                - problem.dimension: Number of nodes (n)
            xp: Backend module (numpy or cupy)
                - Use xp.random for randomness
                - Use xp operations for vectorization

        Returns:
            Neighbor tour: List[int] with single modification
                - Must maintain depot at first/last positions
                - Must be valid permutation (all cities visited once)

        Example:
            >>> # Random swap strategy
            >>> import numpy as np
            >>> tour = [0, 5, 3, 7, 2, 0]  # 4-city TSP
            >>> neighbor = strategy.generate_neighbor(tour, problem, np)
            >>> neighbor  # e.g., [0, 3, 5, 7, 2, 0] (swapped 5 ↔ 3)
        """
        ...


class MutationOperator(Protocol):
    """
    Introduce variation into genetic algorithm individual.

    Phase 3.5 Hybrid Bridge Architecture:
        - Mutation operations ALWAYS run on CPU (NumPy)
        - No xp parameter - uses numpy internally
        - Part of S-Task (sequential CPU operations)

    Semantic Context:
        Used by: Genetic Algorithm
        Purpose: Maintain population diversity, prevent premature convergence
        Frequency: Called O(population_size × generations) times

    Key Characteristics:
        - Stochastic variation (not improvement-focused)
        - No fitness evaluation during mutation
        - Independent of problem context (blind variation)
        - CPU-only execution (small operations, kernel overhead > speedup)

    Examples:
        - SwapMutation: Random city swap
        - InversionMutation: Reverse random segment
        - InsertionMutation: Remove and reinsert city
        - TwoOptMutation: Apply single 2-opt move (for intensification)

    Comparison with NeighborStrategy:
        - Mutation: Genetic variation (no problem context)
        - Neighbor: SA exploration (may use distances)
        - Both: Single-move operations (not exhaustive)

    Validation Responsibilities:
        - Metaheuristic validates inputs ONCE (tour dimensions, depot positions)
        - Operators ASSUME valid inputs (no duplicate validation)
        - Operators MAY add domain-specific validation if needed
        - Follow DRY principle: validate once in GeneticAlgorithm, not in every operator
    """

    def mutate(self, individual: np.ndarray) -> List[int]:
        """
        Mutate individual (introduce variation).

        Phase 3.5: CPU-only execution using NumPy internally.
        Stage 4: Updated to accept np.ndarray directly (individual extracted from population array).

        Args:
            individual: Tour to mutate as 1D NumPy array [depot, c1, ..., ck, depot]
                - Shape: (tour_length,)
                - dtype: typically int32 or int64

        Returns:
            Mutated tour as Python list
                - Should be structurally valid (depot preserved)
                - May be worse than original (fitness evaluated later)
                - Returned as list for compatibility with offspring collection

        Example:
            >>> # Swap mutation (CPU-only)
            >>> import numpy as np
            >>> individual = np.array([0, 1, 2, 3, 4, 0])
            >>> mutated = operator.mutate(individual)
            >>> mutated  # e.g., [0, 1, 4, 3, 2, 0] (swapped 2 ↔ 4)
        """
        ...


class CrossoverStrategy(Protocol):
    """
    Combine two parents to produce offspring (genetic recombination).

    Phase 3.5 Hybrid Bridge Architecture:
        - Crossover operations ALWAYS run on CPU (NumPy)
        - No xp parameter - uses numpy internally
        - Part of S-Task (sequential CPU operations)

    Semantic Context:
        Used by: Genetic Algorithm
        Purpose: Combine good traits from multiple parents
        Frequency: Called O(population_size × generations) times

    Key Characteristics:
        - Deterministic or stochastic (depends on implementation)
        - Must preserve tour validity (all cities visited once)
        - Typically produces 2 offspring from 2 parents (or 1 in some implementations)
        - CPU-only execution (small permutation operations)

    Examples:
        - OrderCrossover (OX): Davis (1985) - preserve relative order
        - PartiallyMappedCrossover (PMX): Goldberg (1985) - preserve positions
        - CycleCrossover (CX): Oliver et al. (1987) - preserve absolute positions

    Complexity Note:
        - OX is O(n) in Python (for-loops)
        - Parallel OX (Fujimoto) is O(log n) with CUDA (future work - P-Task)

    Validation Responsibilities:
        - Metaheuristic validates parent tours ONCE (dimensions, depot positions)
        - Crossover strategies ASSUME valid parent tours (no duplicate validation)
        - Strategies MUST ensure offspring validity (all cities visited once)
        - Follow DRY principle: validate inputs once in GeneticAlgorithm, validate outputs in crossover
    """

    def crossover(
        self, parent1: np.ndarray, parent2: np.ndarray
    ) -> Tuple[List[int], List[int]]:
        """
        Generate two offspring from two parents (or one offspring, depending on implementation).

        Phase 3.5: CPU-only execution using NumPy internally.
        Stage 4: Updated to accept np.ndarray directly (parents extracted from population array).

        Args:
            parent1, parent2: Parent tours as 1D NumPy arrays [depot, ..., depot]
                - Shape: (tour_length,) for each parent
                - dtype: typically int32 or int64

        Returns:
            (child1, child2): Two offspring tours as Python lists
                - Both must be valid permutations
                - Should inherit traits from both parents
                - Returned as lists for compatibility with offspring collection

        Example:
            >>> # Order Crossover (OX) - CPU-only
            >>> import numpy as np
            >>> parent1 = np.array([0, 1, 2, 3, 4, 5, 0])
            >>> parent2 = np.array([0, 3, 5, 1, 4, 2, 0])
            >>> child1, child2 = strategy.crossover(parent1, parent2)
            >>> # Children have segments from both parents
        """
        ...


class ImprovementOperator(Protocol):
    """
    Improve solution quality via local search (intensification).

    Semantic Context:
        Used by: Post-processing, hybrid algorithms, memetic algorithms
        Purpose: Refine solutions to local optima
        Frequency: Called O(1) per solution (or per generation in GA)

    Key Characteristics:
        - Exhaustive local search (evaluates multiple moves)
        - Iterative improvement (until no improvement found)
        - Uses problem context (distances for move evaluation)

    Examples:
        - TwoOptImprovement: Iterative 2-opt until convergence
        - ThreeOptImprovement: 3-opt local search
        - VNDImprovement: Variable Neighborhood Descent

    Comparison with NeighborStrategy:
        - Improvement: Exhaustive search (O(N²) per iteration)
        - Neighbor: Single move generation (O(1) or O(N) for best move)

    Use Cases:
        - SA → TwoOpt pipeline: SA explores, TwoOpt refines
        - GA post-processing: Improve best individual after each generation
        - Memetic algorithms: Local search after crossover/mutation

    Validation Responsibilities:
        - Metaheuristic validates inputs ONCE (tour dimensions, depot positions, problem validity)
        - Improvement operators ASSUME valid inputs (tour structure pre-validated)
        - Operators MUST ensure output validity (preserved tour structure)
        - Follow DRY principle: validate once at entry point, not in every iteration of improve()
    """

    def improve(
        self,
        tour: List[int],
        problem: Problem,
        xp: BackendModule,
        max_iterations: int = 100,
    ) -> List[int]:
        """
        Improve tour via local search.

        Args:
            tour: Initial tour [depot, ..., depot]
            problem: Problem instance (for distances)
            xp: Backend module (numpy or cupy)
            max_iterations: Maximum improvement iterations
                - Default: 100 (enough for convergence on most instances)
                - For TwoOptMove in SA: use max_iterations=1 (single best move)

        Returns:
            Improved tour: Local optimum (or best found within max_iterations)
                - Cost should be ≤ initial tour cost
                - May be same as input if already at local optimum

        Example:
            >>> # 2-opt improvement
            >>> tour = [0, 5, 3, 7, 2, 0]  # Cost: 150
            >>> improved = operator.improve(tour, problem, np, max_iterations=50)
            >>> # improved cost: 120 (local optimum found in 15 iterations)
        """
        ...


class SelectionStrategy(Protocol):
    """
    Select individuals from population for reproduction (Genetic Algorithms).

    Phase 3.5 Hybrid Bridge Architecture:
        - Selection operations ALWAYS run on CPU (NumPy)
        - No xp parameter - uses numpy internally
        - Part of S-Task (sequential CPU operations)

    Semantic Context:
        Used by: Genetic Algorithm, Evolutionary Strategies
        Purpose: Determine which individuals reproduce based on fitness
        Frequency: Called O(generations) times per solve()

    Key Characteristics:
        - Selection with replacement (same individual can be selected multiple times)
        - Vectorized interface (single call for all selections)
        - Fitness-based (lower cost = better fitness for minimization)
        - Returns indices (not tours) for memory efficiency
        - CPU-only execution (small array operations, efficient on CPU)

    Selection Pressure:
        - Tournament (k=2): Weak pressure, good exploration
        - Tournament (k=5-7): Strong pressure, fast convergence
        - Roulette Wheel: Proportional to fitness (weak for similar fitness)
        - Crowding: Deterministic (maintains diversity)

    Examples:
        - TournamentSelection: k-tournament (sample k, select best)
        - RouletteWheelSelection: Fitness-proportional sampling
        - RankSelection: Based on rank, not absolute fitness
        - CrowdingSelection: Deterministic (for steady-state GA)

    Comparison with Other Operators:
        - Selection: Choose who reproduces (fitness-based)
        - Crossover: Create offspring from parents (structure combination)
        - Mutation: Modify offspring (exploration)

    Design Note:
        Returns indices instead of tours for:
        - Memory efficiency: Avoid copying O(n_select × n) tour data
        - Flexibility: Caller decides whether to copy or reference
        - Simplicity: Indexing is straightforward CPU operation

    Validation Responsibilities:
        - GA validates population/fitness shapes ONCE at entry
        - Selection strategies ASSUME valid inputs (shapes pre-validated)
        - Strategies MUST return valid indices [0, pop_size)
    """

    def select(
        self,
        population: np.ndarray,
        fitness: np.ndarray,
        n_select: int,
    ) -> List[int]:
        """
        Select n_select individuals from population based on fitness.

        Phase 3.5: CPU-only execution using NumPy internally.
        Stage 4: Updated to accept np.ndarray directly (efficient bulk operations).

        Args:
            population: NumPy array of tours, shape (pop_size, tour_length)
                - Each row: [depot, city1, ..., cityN, depot]
                - dtype: typically int32 or int64
            fitness: NumPy array of costs, shape (pop_size,)
                - Minimization problem: fitness[i] = tour_cost(population[i])
                - Must be positive for some selection methods (e.g., roulette wheel)
                - dtype: typically float64
            n_select: Number of individuals to select
                - Typically equal to pop_size (select entire next generation)
                - Can be different for offspring generation strategies

        Returns:
            List of indices into population (length n_select)
                - Values in [0, pop_size)
                - With replacement: same index can appear multiple times
                - Usage: selected_tours = population[indices]

        Example:
            >>> # Tournament selection (k=3) - CPU-only
            >>> import numpy as np
            >>> strategy = TournamentSelection(tournament_size=3)
            >>> population = np.array([[0,1,2,3,0], [0,2,1,3,0], ...])  # (100, 5)
            >>> fitness = np.array([150.0, 120.0, ...])  # (100,)
            >>> indices = strategy.select(population, fitness, n_select=100)
            >>> # indices: [5, 23, 5, 67, ...]  # Best individuals selected multiple times
            >>>
            >>> # Use indices to get selected tours
            >>> parents = population[indices]  # (100, 5)

        Notes:
            - With replacement: Allows multiple selection of same individual
            - Lower fitness is better (TSP minimization)
            - Implementations use NumPy internally (CPU-only)
        """
        ...
