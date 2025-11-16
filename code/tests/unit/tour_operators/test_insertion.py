"""Tests for insert_city utility."""

from src.algorithms.tour_operators.insertion import insert_city


def test_insert_city_basic():
    """Test basic insertion functionality."""
    tour = [0, 1, 2, 3, 4, 0]
    result = insert_city(tour, 1, 3)  # Move 1 to position 3
    assert result == [0, 2, 3, 1, 4, 0]


def test_insert_city_forward():
    """Insert city forward in tour."""
    tour = [0, 5, 3, 7, 2, 0]
    result = insert_city(tour, 1, 3)  # Move 5 after 7
    assert result == [0, 3, 7, 5, 2, 0]


def test_insert_city_backward():
    """Insert city backward in tour."""
    tour = [0, 5, 3, 7, 2, 0]
    result = insert_city(tour, 3, 1)  # Move 7 before 3
    assert result == [0, 7, 5, 3, 2, 0]


def test_insert_city_preserves_depot():
    """Depot should remain at first and last positions."""
    tour = [0, 1, 2, 3, 0]
    result = insert_city(tour, 1, 2)
    assert result[0] == 0
    assert result[-1] == 0


def test_insert_city_does_not_modify_original():
    """Should return new list."""
    tour = [0, 1, 2, 3, 0]
    original = tour.copy()
    result = insert_city(tour, 1, 2)
    assert tour == original


def test_insert_same_position():
    """Inserting at same position should return unchanged tour."""
    tour = [0, 1, 2, 3, 0]
    result = insert_city(tour, 2, 2)
    assert result == tour
