"""
Simulated Annealing for TSP and CVRP.

This module implements the Simulated Annealing metaheuristic for solving
routing problems using probabilistic acceptance of moves.

Algorithm Classification:
    - Class: P-Data (Parallel Data)
    - Type: Single-trajectory metaheuristic
    - Approach: Probabilistic local search with temperature-based acceptance

Algorithm Overview:
    1. Initialize with greedy solution (nearest neighbor)
    2. Set temperature T = initial_temp
    3. While T > min_temp and iterations < max_iterations:
        a. Generate neighbor solution (2-opt, swap, or insertion)
        b. Calculate delta = new_cost - current_cost
        c. Accept if delta < 0 (improvement)
        d. Accept with probability exp(-delta/T) if delta >= 0
        e. Cool temperature: T = cooling_function(T, iteration)
    4. Return best solution found during search

Neighbor Generation Methods:
    - 2-opt: Reverse random segment of tour [i+1:j+1]
    - Swap: Exchange positions of two random cities
    - Insertion: Remove random city, insert at random position

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
    - initial_temp (float): Starting temperature (default: 1000.0)
    - cooling_rate (float): Geometric cooling factor (default: 0.95)
    - max_iterations (int): Maximum iterations (default: 1000)
    - min_temp (float): Stopping temperature (default: 0.01)
    - neighbor_method (str): '2-opt', 'swap', or 'insertion' (default: '2-opt')
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
    >>> from src.protocols.problem_context import ProblemContext
    >>>
    >>> # Create problem context
    >>> context = ProblemContext(problem, xp=np)
    >>> customers = list(range(1, problem.dimension))
    >>>
    >>> # Configure and run SA
    >>> sa = SimulatedAnnealing()
    >>> sa.set_params(initial_temp=2000, max_iterations=5000, neighbor_method='2-opt')
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
import math

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

    def __init__(self, callback: Optional["ProgressCallback"] = None):
        """
        Initialize Simulated Annealing with default hyperparameters.

        Args:
            callback: Optional callback for progress tracking (ProgressCallback protocol)

        Default configuration:
            - initial_temp: 1000.0
            - cooling_rate: 0.95 (for geometric schedule)
            - max_iterations: 1000
            - min_temp: 0.01
            - neighbor_method: '2-opt'
            - schedule: 'geometric'
        """
        self._callback = callback
        self._hyperparams = {
            "initial_temp": 1000.0,
            "cooling_rate": 0.95,
            "max_iterations": 1000,
            "min_temp": 0.01,
            "neighbor_method": "2-opt",  # '2-opt', 'swap', 'insertion'
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

        # Get backend and distances
        xp = context.xp
        distances = context.distances  # Uses backend from context (np or cp)

        # Extract hyperparameters
        initial_temp = self._hyperparams["initial_temp"]
        max_iterations = self._hyperparams["max_iterations"]
        min_temp = self._hyperparams["min_temp"]
        neighbor_method = self._hyperparams["neighbor_method"]
        schedule = self._hyperparams["schedule"]

        # Start timing
        start_time = time.time()

        # Generate initial solution (greedy nearest neighbor)
        current_tour = self._generate_initial_solution(customers, distances, xp)
        current_cost = self._compute_tour_cost(current_tour, distances, xp)

        # Track best solution
        best_tour = current_tour.copy()
        best_cost = current_cost

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
            # Generate neighbor
            neighbor_tour = self._generate_neighbor(current_tour, neighbor_method, xp)
            neighbor_cost = self._compute_tour_cost(neighbor_tour, distances, xp)

            # Calculate delta
            delta = neighbor_cost - current_cost

            # Acceptance decision
            if self._accept_move(delta, temperature, xp):
                current_tour = neighbor_tour
                current_cost = neighbor_cost
                accepted_moves += 1

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
        self, customers: List[int], distances, xp
    ) -> List[int]:
        """
        Generate initial solution using greedy nearest neighbor.

        Args:
            customers: List of customer indices
            distances: Distance matrix (backend-agnostic)
            xp: Backend module (numpy or cupy)

        Returns:
            Initial tour [depot, c1, c2, ..., ck, depot]
        """
        # Greedy nearest neighbor construction
        # Keep distances on backend (no forced conversion)
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

    def _generate_neighbor(self, tour: List[int], method: str, xp) -> List[int]:
        """
        Generate neighbor solution using specified method.

        Args:
            tour: Current tour [depot, c1, ..., ck, depot]
            method: Neighbor generation method ('2-opt', 'swap', 'insertion')
            xp: Backend module (NumPy or CuPy)

        Returns:
            Neighbor tour with same structure

        Raises:
            ValueError: If method is not recognized
        """
        n = len(tour) - 1  # Exclude depot at end

        if method == "2-opt":
            return self._neighbor_2opt(tour, n, xp)
        elif method == "swap":
            return self._neighbor_swap(tour, n, xp)
        elif method == "insertion":
            return self._neighbor_insertion(tour, n, xp)
        else:
            raise ValueError(f"Unknown neighbor method: {method}")

    def _neighbor_2opt(self, tour: List[int], n: int, xp) -> List[int]:
        """
        Generate neighbor by reversing a random tour segment (2-opt move).

        Args:
            tour: Current tour
            n: Tour length excluding final depot
            xp: Backend module (numpy or cupy)

        Returns:
            Neighbor tour with reversed segment
        """
        # Need at least 3 nodes for meaningful 2-opt (depot + 2 customers)
        if n < 3:
            return tour.copy()  # Cannot apply 2-opt, return copy

        # Select two random positions (i < j) using backend random
        i = int(xp.random.randint(0, n - 2))
        j = int(xp.random.randint(i + 2, n))

        # Create neighbor by reversing tour[i+1:j+1]
        neighbor = tour.copy()
        neighbor[i + 1 : j + 1] = neighbor[i + 1 : j + 1][::-1]

        return neighbor

    def _neighbor_swap(self, tour: List[int], n: int, xp) -> List[int]:
        """
        Generate neighbor by swapping two random cities.

        Args:
            tour: Current tour
            n: Tour length excluding final depot
            xp: Backend module (numpy or cupy)

        Returns:
            Neighbor tour with swapped cities
        """
        # Select two random positions (excluding depot) using backend random
        i = int(xp.random.randint(1, n))
        j = int(xp.random.randint(1, n))

        while i == j:
            j = int(xp.random.randint(1, n))

        # Create neighbor by swapping positions i and j
        neighbor = tour.copy()
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]

        return neighbor

    def _neighbor_insertion(self, tour: List[int], n: int, xp) -> List[int]:
        """
        Generate neighbor by removing a city and inserting it elsewhere.

        Args:
            tour: Current tour
            n: Tour length excluding final depot
            xp: Backend module (numpy or cupy)

        Returns:
            Neighbor tour with relocated city
        """
        # Select random city to remove (excluding depot) using backend random
        remove_pos = int(xp.random.randint(1, n))

        # Select random insertion position
        insert_pos = int(xp.random.randint(1, n))

        while insert_pos == remove_pos:
            insert_pos = int(xp.random.randint(1, n))

        # Create neighbor by removing and reinserting city
        neighbor = tour.copy()
        city = neighbor.pop(remove_pos)
        neighbor.insert(insert_pos, city)

        return neighbor

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

    def _accept_move(self, delta: float, temperature: float, xp) -> bool:
        """
        Determine whether to accept a move using Metropolis criterion.

        Args:
            delta: Cost change (new_cost - current_cost)
            temperature: Current temperature
            xp: Backend module (numpy or cupy)

        Returns:
            True if move should be accepted, False otherwise
        """
        if delta < 0:
            # Always accept improvements
            return True

        # Metropolis acceptance criterion using backend operations
        probability = float(xp.exp(-delta / temperature))
        return float(xp.random.random()) < probability

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
