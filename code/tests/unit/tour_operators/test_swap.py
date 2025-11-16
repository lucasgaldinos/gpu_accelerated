"""Tests for swap_cities utility."""

from src.algorithms.tour_operators.swap import swap_cities


def test_swap_cities_basic():
    """Test basic swap functionality."""
    tour = [0, 1, 2, 3, 4, 0]
    result = swap_cities(tour, 1, 3)
    assert result == [0, 3, 2, 1, 4, 0]


def test_swap_cities_preserves_depot():
    """Depot positions should not change."""
    tour = [0, 5, 3, 7, 2, 0]
    result = swap_cities(tour, 1, 3)
    assert result[0] == 0  # First depot preserved
    assert result[-1] == 0  # Last depot preserved


def test_swap_cities_does_not_modify_original():
    """Should return new list, not modify original."""
    tour = [0, 1, 2, 3, 0]
    original = tour.copy()
    result = swap_cities(tour, 1, 2)
    assert tour == original  # Original unchanged


def test_swap_same_positions():
    """Swapping same position should return unchanged tour."""
    tour = [0, 1, 2, 3, 0]
    result = swap_cities(tour, 2, 2)
    assert result == tour


def test_swap_order_independence():
    """swap(i,j) should equal swap(j,i)."""
    tour = [0, 1, 2, 3, 4, 0]
    result1 = swap_cities(tour, 1, 3)
    result2 = swap_cities(tour, 3, 1)
    assert result1 == result2
