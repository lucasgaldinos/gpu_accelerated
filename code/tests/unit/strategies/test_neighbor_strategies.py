"""
Tests for neighbor generation strategies.

Test Coverage:
- RandomSwapStrategy: Validity, modification, immutability
- RandomInsertionStrategy: (to be added in M14.3.2)
- Random2OptStrategy: (to be added in M14.3.3)

Design:
- Use small 4-city TSP for fast, deterministic testing
- Test protocol compliance (valid permutation)
- Test actual modification (not identity function)
- Test immutability (no side effects on input)
"""

import pytest
import numpy as np
from src.algorithms.strategies.neighbor_strategies import RandomSwapStrategy
from src.data_models.problem import Problem


@pytest.fixture
def problem_4city():
    """
    4-city TSP problem for testing.

    Returns:
        Problem instance with:
        - 4 cities (indices 0-3, 0 is depot)
        - Symmetric distances
        - EUC_2D edge type
    """
    distances = np.array(
        [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
    )
    coordinates = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
    return Problem(
        name="test",
        dimension=4,
        problem_type="TSP",
        edge_type="EUC_2D",
        coordinates=coordinates,
        distances=distances,
    )


# ===== RandomSwapStrategy Tests =====


def test_random_swap_returns_valid_tour(problem_4city):
    """
    Neighbor should be valid permutation.

    Validates:
    - Same tour length
    - Depot preserved at first position
    - Depot preserved at last position
    - All cities present (valid permutation)
    """
    strategy = RandomSwapStrategy()
    tour = [0, 1, 2, 3, 0]

    neighbor = strategy.generate_neighbor(tour, problem_4city, np)

    assert len(neighbor) == len(tour), "Tour length changed"
    assert neighbor[0] == 0, "Depot not preserved at start"
    assert neighbor[-1] == 0, "Depot not preserved at end"
    assert set(neighbor) == set(tour), "Cities changed (not a permutation)"


def test_random_swap_modifies_tour(problem_4city):
    """
    Neighbor should be different from current tour.

    Strategy:
    - Run 10 times to avoid false negatives from randomness
    - At least one result should differ from input
    - Probability of all identical: (1/6)^10 ≈ 0 (negligible)

    Note:
    - For 4-city tour, 3 interior positions → 3 choose 2 = 3 possible swaps
    - Each swap produces different tour
    - Probability any single call returns same tour: 0
    """
    strategy = RandomSwapStrategy()
    tour = [0, 1, 2, 3, 0]

    # Run multiple times to ensure randomness works
    neighbors = [strategy.generate_neighbor(tour, problem_4city, np) for _ in range(10)]

    # At least one should be different (should be ALL different actually)
    assert any(n != tour for n in neighbors), "All neighbors identical to input"


def test_random_swap_does_not_modify_original(problem_4city):
    """
    Should return new tour, not modify original.

    Validates:
    - No side effects on input tour
    - swap_cities creates NEW list (not in-place modification)
    - Functional programming principle (immutability)
    """
    strategy = RandomSwapStrategy()
    tour = [0, 1, 2, 3, 0]
    original = tour.copy()

    neighbor = strategy.generate_neighbor(tour, problem_4city, np)

    assert tour == original, "Original tour was modified (side effect)"
    assert neighbor is not tour, "Returned same list object (should be new list)"


# ===== RandomInsertionStrategy Tests =====


def test_random_insertion_returns_valid_tour(problem_4city):
    """
    Insertion neighbor should be valid permutation.

    Validates:
    - Same tour length
    - Depot preserved at first position
    - Depot preserved at last position
    - All cities present (valid permutation)
    """
    from src.algorithms.strategies.neighbor_strategies import RandomInsertionStrategy

    strategy = RandomInsertionStrategy()
    tour = [0, 1, 2, 3, 0]

    neighbor = strategy.generate_neighbor(tour, problem_4city, np)

    assert len(neighbor) == len(tour), "Tour length changed"
    assert neighbor[0] == 0, "Depot not preserved at start"
    assert neighbor[-1] == 0, "Depot not preserved at end"
    assert set(neighbor) == set(tour), "Cities changed (not a permutation)"


def test_random_insertion_modifies_tour(problem_4city):
    """
    Insertion neighbor should be different from current tour.

    Strategy:
    - Run 10 times to avoid false negatives from randomness
    - At least one result should differ from input
    - Probability of all identical: very low (insertion almost always changes order)

    Note:
    - For 4-city tour, 3 interior positions
    - Each insertion (except same position) produces different tour
    - We ensure from_pos != to_pos, so result should differ
    """
    from src.algorithms.strategies.neighbor_strategies import RandomInsertionStrategy

    strategy = RandomInsertionStrategy()
    tour = [0, 1, 2, 3, 0]

    # Run multiple times to ensure randomness works
    neighbors = [strategy.generate_neighbor(tour, problem_4city, np) for _ in range(10)]

    # At least one should be different
    assert any(n != tour for n in neighbors), "All neighbors identical to input"


def test_random_insertion_does_not_modify_original(problem_4city):
    """
    Should return new tour, not modify original.

    Validates:
    - No side effects on input tour
    - insert_city creates NEW list (not in-place modification)
    - Functional programming principle (immutability)
    """
    from src.algorithms.strategies.neighbor_strategies import RandomInsertionStrategy

    strategy = RandomInsertionStrategy()
    tour = [0, 1, 2, 3, 0]
    original = tour.copy()

    neighbor = strategy.generate_neighbor(tour, problem_4city, np)

    assert tour == original, "Original tour was modified (side effect)"
    assert neighbor is not tour, "Returned same list object (should be new list)"


# ===== Random2OptStrategy Tests =====


def test_random_2opt_returns_valid_tour(problem_4city):
    """
    2-opt neighbor should be valid permutation.

    Validates:
    - Same tour length
    - Depot preserved at first position
    - Depot preserved at last position
    - All cities present (valid permutation)
    """
    from src.algorithms.strategies.neighbor_strategies import Random2OptStrategy

    strategy = Random2OptStrategy()
    tour = [0, 1, 2, 3, 0]

    neighbor = strategy.generate_neighbor(tour, problem_4city, np)

    assert len(neighbor) == len(tour), "Tour length changed"
    assert neighbor[0] == 0, "Depot not preserved at start"
    assert neighbor[-1] == 0, "Depot not preserved at end"
    assert set(neighbor) == set(tour), "Cities changed (not a permutation)"


def test_random_2opt_modifies_tour(problem_4city):
    """
    2-opt neighbor should be different from current tour.

    Strategy:
    - Run 10 times to avoid false negatives from randomness
    - At least one result should differ from input
    - 2-opt reverses segment, so result should differ unless segment length = 1

    Note:
    - For 4-city tour, segment reversals almost always change order
    - Only exception: segment of length 1 (no change)
    - With 10 runs, very high probability of seeing modification
    """
    from src.algorithms.strategies.neighbor_strategies import Random2OptStrategy

    strategy = Random2OptStrategy()
    tour = [0, 1, 2, 3, 0]

    # Run multiple times to ensure randomness works
    neighbors = [strategy.generate_neighbor(tour, problem_4city, np) for _ in range(10)]

    # At least one should be different
    assert any(n != tour for n in neighbors), "All neighbors identical to input"


def test_random_2opt_does_not_modify_original(problem_4city):
    """
    Should return new tour, not modify original.

    Validates:
    - No side effects on input tour
    - invert_segment creates NEW list (not in-place modification)
    - Functional programming principle (immutability)
    """
    from src.algorithms.strategies.neighbor_strategies import Random2OptStrategy

    strategy = Random2OptStrategy()
    tour = [0, 1, 2, 3, 0]
    original = tour.copy()

    neighbor = strategy.generate_neighbor(tour, problem_4city, np)

    assert tour == original, "Original tour was modified (side effect)"
    assert neighbor is not tour, "Returned same list object (should be new list)"
