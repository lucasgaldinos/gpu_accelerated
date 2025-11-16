"""
Neighbor generation strategies for local search metaheuristics.

Used by: SimulatedAnnealing, TabuSearch, IteratedLocalSearch

Strategies implement NeighborStrategy protocol:
- RandomSwapStrategy: Swap two random cities
- RandomInsertionStrategy: Remove and reinsert city
- Random2OptStrategy: Reverse random tour segment
- TwoOptMoveStrategy: Best single 2-opt move (uses distances)

Design Notes:
- All strategies MUST have explicit __init__(self, **kwargs) -> None
- Stateless strategies accept **kwargs for registry compatibility
- Use tour_operators utilities (swap_cities, insert_city, invert_segment)

References:
- M14.3: SA Strategy Extraction
- Layer 3 Architecture: protocols → tour_operators → strategies
"""

from typing import Any, List
from ...data_models.problem import Problem
from ..tour_operators import swap_cities, insert_city, invert_segment
from ...utils.strategy_registry import StrategyRegistry


@StrategyRegistry.register("neighborhood", "random_swap")
class RandomSwapStrategy:
    """
    Generate neighbor by swapping two random cities.

    Used By: Simulated Annealing (exploration phase)

    Algorithm:
        1. Select two random positions i, j (exclude depot)
        2. Ensure i ≠ j
        3. Return swap_cities(tour, i, j)

    Complexity: O(1) for move generation
    Search Space: n(n-1)/2 possible swaps for n-city TSP

    Characteristics:
        - High diversity (large neighborhood)
        - No problem knowledge (blind search)
        - Fast generation (constant time)

    Best For:
        - Early SA iterations (exploration)
        - Small/medium problem sizes (<500 cities)
        - Diversification in multi-start methods

    Example:
        >>> strategy = RandomSwapStrategy()
        >>> tour = [0, 5, 3, 7, 2, 0]
        >>> neighbor = strategy.generate_neighbor(tour, problem, np)
        >>> neighbor  # e.g., [0, 3, 5, 7, 2, 0] (swapped positions 1 and 2)
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize RandomSwapStrategy.

        Args:
            **kwargs: Ignored (for registry compatibility)

        Note:
            This strategy is STATELESS (no configuration parameters).
            Accepts **kwargs to enable:
            1. Registry pattern (all strategies accept config)
            2. Uniform factory interface
            3. Future extension without breaking changes
        """
        pass

    def generate_neighbor(
        self,
        current_tour: List[int],
        problem: Problem,
        rng: Any,  # NumPy Generator instance
    ) -> List[int]:
        """
        Generate neighbor via random swap using CPU-native RNG.

        Args:
            current_tour: Current solution [depot, c1, c2, ..., ck, depot]
            problem: Problem instance (unused for random swap)
            rng: NumPy Generator for deterministic random number generation (S-Task)

        Returns:
            Neighbor tour with two cities swapped

        Example:
            >>> rng = np.random.default_rng(42)
            >>> tour = [0, 1, 2, 3, 0]
            >>> neighbor = strategy.generate_neighbor(tour, problem, rng)
            >>> # Possible result: [0, 3, 2, 1, 0] (swapped cities at pos 1 and 3)
        """
        n = len(current_tour) - 1  # Exclude final depot

        # Select random positions (exclude depot at position 0 and n)
        # Use modern Generator API (integers) for determinism
        i = int(rng.integers(1, n))
        j = int(rng.integers(1, n))

        # Ensure i != j (swap needs two different positions)
        while i == j:
            j = int(rng.integers(1, n))

        return swap_cities(current_tour, i, j)


@StrategyRegistry.register("neighborhood", "random_insertion")
class RandomInsertionStrategy:
    """
    Generate neighbor by removing a city and reinserting it elsewhere.

    Used By: Simulated Annealing (mid-range temperatures)

    Algorithm:
        1. Select random position from_pos to remove city
        2. Select random position to_pos to insert city
        3. Ensure from_pos ≠ to_pos
        4. Return insert_city(tour, from_pos, to_pos)

    Complexity: O(n) for list operations (pop + insert)
    Search Space: n(n-1) possible insertions for n-city TSP

    Characteristics:
        - Moderate diversity (medium neighborhood)
        - Can produce larger changes than swap
        - Slower than swap due to list operations

    Best For:
        - Mid-range SA temperatures (balanced exploration/exploitation)
        - Route structure optimization
        - Avoiding local minima from swap-only search

    Example:
        >>> strategy = RandomInsertionStrategy()
        >>> tour = [0, 5, 3, 7, 2, 0]
        >>> neighbor = strategy.generate_neighbor(tour, problem, np)
        >>> neighbor  # e.g., [0, 3, 7, 5, 2, 0] (moved city 5 to position 3)
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize RandomInsertionStrategy.

        Args:
            **kwargs: Ignored (for registry compatibility)

        Note:
            This strategy is STATELESS (no configuration parameters).
            Accepts **kwargs to enable:
            1. Registry pattern (all strategies accept config)
            2. Uniform factory interface
            3. Future extension without breaking changes
        """
        pass

    def generate_neighbor(
        self,
        current_tour: List[int],
        problem: Problem,
        rng: Any,  # NumPy Generator instance
    ) -> List[int]:
        """
        Generate neighbor via random insertion using CPU-native RNG.

        Args:
            current_tour: Current solution [depot, c1, c2, ..., ck, depot]
            problem: Problem instance (unused for random insertion)
            rng: NumPy Generator for deterministic random number generation (S-Task)

        Returns:
            Neighbor tour with one city relocated

        Example:
            >>> rng = np.random.default_rng(42)
            >>> tour = [0, 1, 2, 3, 0]
            >>> neighbor = strategy.generate_neighbor(tour, problem, rng)
            >>> # Possible result: [0, 2, 1, 3, 0] (moved city at pos 1 to pos 2)
        """
        n = len(current_tour) - 1  # Exclude final depot

        # Select random position to remove city from (exclude depot)
        # Use modern Generator API (integers) for determinism
        from_pos = int(rng.integers(1, n))

        # Select random position to insert city at (exclude depot)
        to_pos = int(rng.integers(1, n))

        # Ensure from_pos != to_pos (insertion needs different positions)
        while from_pos == to_pos:
            to_pos = int(rng.integers(1, n))

        return insert_city(current_tour, from_pos, to_pos)


@StrategyRegistry.register("neighborhood", "random_2opt")
class Random2OptStrategy:
    """
    Generate neighbor by reversing a random tour segment (2-opt move).

    Used By: Simulated Annealing (later iterations, intensification)

    Algorithm:
        1. Select random position i (exclude depot and last customer)
        2. Select random position j where j > i (exclude depot)
        3. Return invert_segment(tour, i, j) - reverses tour[i:j+1]

    Complexity: O(k) where k = j - i (segment length)
    Search Space: n(n-1)/2 possible reversals for n-city TSP

    Characteristics:
        - Classic 2-opt neighborhood (Lin & Kernighan, 1973)
        - Can untangle crossed edges in geometric TSP
        - Variable impact (small segments = minor change, large = major)

    Best For:
        - Later SA iterations (intensification phase)
        - TSP instances with geometric/Euclidean structure
        - Hybrid methods (combine with improvement operators)

    Note:
        This generates ONE random 2-opt move.
        For exhaustive 2-opt search, use ImprovementOperator.

    Example:
        >>> strategy = Random2OptStrategy()
        >>> tour = [0, 1, 2, 3, 4, 0]
        >>> neighbor = strategy.generate_neighbor(tour, problem, np)
        >>> neighbor  # e.g., [0, 1, 4, 3, 2, 0] (reversed segment [2,3,4])
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize Random2OptStrategy.

        Args:
            **kwargs: Ignored (for registry compatibility)

        Note:
            This strategy is STATELESS (no configuration parameters).
            Accepts **kwargs to enable:
            1. Registry pattern (all strategies accept config)
            2. Uniform factory interface
            3. Future extension without breaking changes
        """
        pass

    def generate_neighbor(
        self,
        current_tour: List[int],
        problem: Problem,
        rng: Any,  # NumPy Generator instance
    ) -> List[int]:
        """
        Generate neighbor via random 2-opt move using CPU-native RNG.

        Args:
            current_tour: Current solution [depot, c1, c2, ..., ck, depot]
            problem: Problem instance (unused for random 2-opt)
            rng: NumPy Generator for deterministic random number generation (S-Task)
                - Modern API: np.random.default_rng(seed)
                - Use integers() instead of legacy randint()

        Returns:
            Neighbor tour with one segment reversed

        Example:
            >>> rng = np.random.default_rng(42)
            >>> tour = [0, 1, 2, 3, 4, 0]
            >>> neighbor = strategy.generate_neighbor(tour, problem, rng)
            >>> # Possible result: [0, 1, 3, 2, 4, 0] (reversed [2,3])
        """
        n = len(current_tour) - 1  # Exclude final depot

        # Select first position i (must leave room for j > i)
        # Range: [1, n-2] to ensure at least one position for j
        # Use modern Generator API (integers) for determinism (S-Task requirement)
        i = int(rng.integers(1, n - 1))

        # Select second position j where j > i
        # Range: [i+1, n-1] (automatically ensures j > i)
        j = int(rng.integers(i + 1, n))

        return invert_segment(current_tour, i, j)
