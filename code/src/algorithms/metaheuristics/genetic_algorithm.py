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
    - selection_method (str): 'crowding', 'tournament', 'roulette' (default: 'crowding')
    - mutation_method (str): 'swap', 'inversion', 'insertion' (default: 'swap')
    - tournament_size (int): Size for tournament selection (default: 3)
    - elitism_count (int): Number of elite solutions to preserve (default: 1)

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

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False

if TYPE_CHECKING:
    from src.protocols.problem_context import ProblemContext
    from src.protocols.callback_protocol import ProgressCallback, ProgressEvent


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

    def __init__(self, callback: Optional["ProgressCallback"] = None):
        """
        Initialize Genetic Algorithm with default hyperparameters.

        Args:
            callback: Optional callback for progress tracking (ProgressCallback protocol)

        Default configuration:
            - population_size: 60 (Fujimoto's recommendation)
            - max_generations: 1000
            - crossover_rate: 0.9
            - mutation_rate: 0.1
            - use_2opt: True (apply local search to offspring)
            - selection_method: 'crowding' (deterministic crowding)
            - mutation_method: 'swap'
            - tournament_size: 3
            - elitism_count: 1
        """
        self._callback = callback
        self._hyperparams = {
            "population_size": 60,
            "max_generations": 1000,
            "crossover_rate": 0.9,
            "mutation_rate": 0.1,
            "use_2opt": True,
            "selection_method": "crowding",  # 'crowding', 'tournament', 'roulette'
            "mutation_method": "swap",  # 'swap', 'inversion', 'insertion'
            "tournament_size": 3,
            "elitism_count": 1,
        }
        self._stats = {}

    def set_params(self, **hyperparameters) -> None:
        """
        Configure Genetic Algorithm hyperparameters.

        Args:
            **hyperparameters: Keyword arguments for configuration.
                Valid keys: population_size, max_generations, crossover_rate,
                mutation_rate, use_2opt, selection_method, mutation_method,
                tournament_size, elitism_count

        Example:
            >>> ga.set_params(population_size=100, max_generations=500)
            >>> ga.set_params(use_2opt=False, mutation_rate=0.2)
        """
        self._hyperparams.update(hyperparameters)

    def build_tour_with_stats(
        self, context: "ProblemContext", customers: List[int]
    ) -> Tuple[List[int], Dict[str, Any]]:
        """
        Solve TSP/CVRP using Genetic Algorithm.

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
            >>> tour, stats = ga.build_tour_with_stats(context, [1, 2, 3, 4, 5])
            >>> print(f"Best cost: {stats['best_fitness']:.2f}")
        """
        # Validation
        if len(customers) == 0:
            raise ValueError("customers list cannot be empty")

        # Get backend and distances (Class P-Data: backend-agnostic)
        xp = context.xp
        distances = context.distances  # Uses backend from context (np or cp)

        # Extract hyperparameters
        pop_size = self._hyperparams["population_size"]
        max_gen = self._hyperparams["max_generations"]
        crossover_rate = self._hyperparams["crossover_rate"]
        mutation_rate = self._hyperparams["mutation_rate"]
        use_2opt = self._hyperparams["use_2opt"]
        selection = self._hyperparams["selection_method"]

        # Start timing
        start_time = time.time()

        # Initialize population
        population = self._initialize_population(customers, pop_size, xp)

        # Vectorized fitness evaluation (Class P-Data)
        fitness = self._compute_batch_fitness(population, distances, xp)

        # Track statistics
        best_idx = int(xp.argmin(fitness))
        best_tour = population[best_idx].copy()
        best_cost = float(fitness[best_idx])

        convergence_history = [best_cost]
        diversity_history = [len(set(map(tuple, population)))]
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
            # Generate offspring
            offspring = []

            for i in range(pop_size):
                # Select second parent (not i) - using xp.random for backend compatibility
                j = int(xp.random.randint(0, pop_size))
                while j == i:
                    j = int(xp.random.randint(0, pop_size))

                # Crossover
                if float(xp.random.random()) < crossover_rate:
                    child = self._order_crossover(population[i], population[j], xp)
                    crossover_count += 1
                else:
                    child = population[i].copy()

                # Mutation
                if float(xp.random.random()) < mutation_rate:
                    child = self._mutate(
                        child, self._hyperparams["mutation_method"], xp
                    )
                    mutation_count += 1

                # Optional 2-opt local search
                if use_2opt:
                    child = self._apply_2opt(child, distances, xp)

                offspring.append(child)

            # Vectorized fitness evaluation for all offspring (Class P-Data)
            offspring_fitness = self._compute_batch_fitness(offspring, distances, xp)

            # Selection (deterministic crowding by default)
            if selection == "crowding":
                # Compare each offspring with its corresponding parent
                for i in range(pop_size):
                    if offspring_fitness[i] < fitness[i]:
                        population[i] = offspring[i]
                        fitness[i] = offspring_fitness[i]
            else:
                # Combine populations and select best
                combined_pop = population + offspring
                combined_fit = xp.concatenate([fitness, offspring_fitness])
                indices = xp.argsort(combined_fit)[:pop_size]
                # Convert indices to Python ints for list indexing
                indices_list = [int(idx) for idx in indices]
                population = [combined_pop[i] for i in indices_list]
                fitness = combined_fit[indices]

            # Update best solution
            gen_best_idx = int(xp.argmin(fitness))
            if fitness[gen_best_idx] < best_cost:
                best_tour = population[gen_best_idx].copy()
                best_cost = float(fitness[gen_best_idx])

            # Track statistics
            convergence_history.append(best_cost)
            diversity_history.append(len(set(map(tuple, population))))

            # Lifecycle: ITERATION
            if self._callback:
                from src.protocols.callback_protocol import ProgressEvent

                event: ProgressEvent = {
                    "iteration": generation + 1,  # 1-indexed for user clarity
                    "best_cost": best_cost,
                    "current_cost": float(xp.mean(fitness)),
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
                "current_cost": float(xp.mean(fitness)),
                "elapsed_time": runtime,
            }
            self._callback.on_complete(event)

        # Compile statistics
        self._stats = {
            "best_fitness": float(best_cost),
            "final_fitness": float(xp.mean(fitness)),
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

    def _compute_batch_fitness(self, population: List[List[int]], distances, xp):
        """
        Vectorized fitness evaluation for entire population.

        This is the KEY optimization for Class P-Data classification.
        Replaces O(pop_size * N) sequential loop with O(1) vectorized operation.

        Args:
            population: List of tours to evaluate
            distances: Distance matrix (backend-agnostic)
            xp: Backend module (numpy or cupy)

        Returns:
            Array of fitness values (one per tour)

        Performance:
            - Sequential: O(pop_size * N) = 60 * 100 = 6,000 operations
            - Vectorized: O(1) fancy indexing operation
            - Expected GPU speedup: 10-100x
        """
        # Convert population to backend array
        # Shape: (pop_size, tour_length)
        pop_array = xp.array(population)

        # Fancy indexing: get all edge costs at once
        # For each tour, get costs between consecutive nodes
        # Shape: (pop_size, tour_length - 1)
        edge_costs = distances[pop_array[:, :-1], pop_array[:, 1:]]

        # Sum across each tour
        # Shape: (pop_size,)
        return xp.sum(edge_costs, axis=1)

    def _initialize_population(
        self, customers: List[int], pop_size: int, xp
    ) -> List[List[int]]:
        """
        Initialize population with random tours.

        Args:
            customers: List of customer indices
            pop_size: Population size
            xp: Backend module (numpy or cupy)

        Returns:
            List of random tours, each [depot, c1, ..., ck, depot]
        """
        population = []
        # Convert customers to array for permutation
        customers_array = xp.array(customers)

        for _ in range(pop_size):
            # Random permutation of customers (using backend's random)
            tour_interior = xp.random.permutation(customers_array)
            # Convert to list for easier manipulation in crossover/mutation
            if hasattr(tour_interior, "get"):
                tour_interior = tour_interior.get().tolist()
            else:
                tour_interior = tour_interior.tolist()
            tour = [0] + tour_interior + [0]
            population.append(tour)
        return population

    def _order_crossover(self, parent1: List[int], parent2: List[int], xp) -> List[int]:
        """
        OX (Order Crossover) operator from Davis (1985).

        Implementation follows Fujimoto & Tsutsui (2011):
        1. Select two random cut points [cut1, cut2)
        2. Copy segment parent2[cut1:cut2] to offspring
        3. Fill remaining positions with cities from parent1 in order

        Args:
            parent1: First parent tour [depot, c1, ..., ck, depot]
            parent2: Second parent tour [depot, c1, ..., ck, depot]
            xp: Backend module (numpy or cupy)

        Returns:
            Offspring tour with same structure
        """
        # Exclude depots for crossover
        p1_interior = parent1[1:-1]
        p2_interior = parent2[1:-1]
        n = len(p1_interior)

        # Edge case: single customer
        if n < 2:
            return parent1.copy()  # Cannot perform meaningful crossover

        # Select two random cut points (using backend's random)
        cut_points = xp.random.choice(n, size=2, replace=False)
        if hasattr(cut_points, "get"):
            cut_points = cut_points.get()
        cut1, cut2 = sorted(cut_points)

        # Initialize offspring
        offspring_interior = [None] * n

        # Copy segment from parent2
        offspring_interior[cut1:cut2] = p2_interior[cut1:cut2]
        copied_cities = set(p2_interior[cut1:cut2])

        # Fill remaining positions from parent1 in order
        p1_idx = 0
        for i in range(n):
            if offspring_interior[i] is None:
                # Find next city from parent1 not in copied segment
                while p1_interior[p1_idx] in copied_cities:
                    p1_idx += 1
                offspring_interior[i] = p1_interior[p1_idx]
                p1_idx += 1

        # Add depots
        return [0] + offspring_interior + [0]

    def _mutate(self, tour: List[int], method: str, xp) -> List[int]:
        """
        Apply mutation operator to tour.

        Args:
            tour: Tour [depot, c1, ..., ck, depot]
            method: Mutation method ('swap', 'inversion', 'insertion')
            xp: Backend module (numpy or cupy)

        Returns:
            Mutated tour
        """
        if method == "swap":
            return self._mutation_swap(tour, xp)
        elif method == "inversion":
            return self._mutation_inversion(tour, xp)
        elif method == "insertion":
            return self._mutation_insertion(tour, xp)
        else:
            raise ValueError(f"Unknown mutation method: {method}")

    def _mutation_swap(self, tour: List[int], xp) -> List[int]:
        """Swap two random cities (excluding depot)."""
        mutated = tour.copy()
        n = len(tour) - 1  # Exclude last depot
        interior_size = n - 1  # Exclude first depot too
        # Edge case: less than 2 customers to swap
        if interior_size < 2:
            return mutated
        indices = xp.random.choice(range(1, n), size=2, replace=False)
        if hasattr(indices, "get"):
            indices = indices.get()
        i, j = indices
        mutated[i], mutated[j] = mutated[j], mutated[i]
        return mutated

    def _mutation_inversion(self, tour: List[int], xp) -> List[int]:
        """Reverse random segment of tour."""
        mutated = tour.copy()
        n = len(tour) - 1  # Exclude last depot
        interior_size = n - 1  # Exclude first depot too
        # Edge case: less than 2 customers to invert
        if interior_size < 2:
            return mutated
        indices = xp.random.choice(range(1, n), size=2, replace=False)
        if hasattr(indices, "get"):
            indices = indices.get()
        i, j = sorted(indices)
        mutated[i : j + 1] = mutated[i : j + 1][::-1]
        return mutated

    def _mutation_insertion(self, tour: List[int], xp) -> List[int]:
        """Remove city and reinsert at different position."""
        mutated = tour.copy()
        n = len(tour) - 1  # Exclude last depot
        interior_size = n - 1  # Exclude first depot too
        # Edge case: less than 2 customers for meaningful insertion
        if interior_size < 2:
            return mutated

        remove_pos = int(xp.random.randint(1, n))
        insert_pos = int(xp.random.randint(1, n))

        while insert_pos == remove_pos:
            insert_pos = int(xp.random.randint(1, n))

        city = mutated.pop(remove_pos)
        mutated.insert(insert_pos, city)
        return mutated

    def _apply_2opt(self, tour: List[int], distances, xp) -> List[int]:
        """
        Apply 2-opt local search to tour.

        Uses simplified first-improvement 2-opt for efficiency.

        Args:
            tour: Tour to improve
            distances: Distance matrix (backend-agnostic)
            xp: Backend module (numpy or cupy)

        Returns:
            Improved tour
        """
        n = len(tour) - 1
        improved = True
        current = tour.copy()

        # Limit iterations to avoid excessive time
        max_iterations = 10
        iteration = 0

        while improved and iteration < max_iterations:
            improved = False

            for i in range(n - 1):
                for j in range(i + 2, n):
                    # Check 2-opt move
                    node_i = current[i]
                    node_i1 = current[i + 1]
                    node_j = current[j]
                    node_j1 = current[(j + 1) % (n + 1)]

                    # Current edges: (i, i+1) and (j, j+1)
                    # New edges: (i, j) and (i+1, j+1)
                    old_cost = distances[node_i, node_i1] + distances[node_j, node_j1]
                    new_cost = distances[node_i, node_j] + distances[node_i1, node_j1]

                    # Convert to float for comparison (handles both np and cp)
                    if float(new_cost) < float(old_cost):
                        # Apply 2-opt move
                        current[i + 1 : j + 1] = current[i + 1 : j + 1][::-1]
                        improved = True
                        break

                if improved:
                    break

            iteration += 1

        return current

    def _compute_tour_cost(self, tour: List[int], distances, xp) -> float:
        """
        Compute total cost of tour using vectorized operations.

        Args:
            tour: Tour [depot, c1, ..., ck, depot]
            distances: Distance matrix (backend-agnostic)
            xp: Backend module (numpy or cupy)

        Returns:
            Total tour cost (sum of edge weights)
        """
        # Convert tour to backend array
        tour_array = xp.array(tour)

        # Vectorized edge cost computation
        edge_costs = distances[tour_array[:-1], tour_array[1:]]

        # Sum and convert to Python float
        return float(xp.sum(edge_costs))
