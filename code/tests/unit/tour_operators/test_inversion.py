"""Tests for invert_segment utility."""

from src.algorithms.tour_operators.inversion import invert_segment


def test_invert_segment_basic():
    """Test basic segment reversal."""
    tour = [0, 1, 2, 3, 4, 5, 0]
    result = invert_segment(tour, 2, 4)
    assert result == [0, 1, 4, 3, 2, 5, 0]


def test_invert_segment_full_tour():
    """Reverse entire middle section."""
    tour = [0, 1, 2, 3, 4, 0]
    result = invert_segment(tour, 1, 4)
    assert result == [0, 4, 3, 2, 1, 0]


def test_invert_segment_two_cities():
    """Reversing two cities is equivalent to swap."""
    tour = [0, 1, 2, 3, 0]
    result = invert_segment(tour, 1, 2)
    assert result == [0, 2, 1, 3, 0]


def test_invert_segment_single_city():
    """Reversing single city should return unchanged."""
    tour = [0, 1, 2, 3, 0]
    result = invert_segment(tour, 2, 2)
    assert result == tour


def test_invert_segment_preserves_depot():
    """Depot should remain at first and last."""
    tour = [0, 5, 3, 7, 2, 0]
    result = invert_segment(tour, 1, 3)
    assert result[0] == 0
    assert result[-1] == 0


def test_invert_segment_order_independence():
    """invert(i,j) should equal invert(j,i)."""
    tour = [0, 1, 2, 3, 4, 0]
    result1 = invert_segment(tour, 1, 3)
    result2 = invert_segment(tour, 3, 1)
    assert result1 == result2


def test_invert_segment_does_not_modify_original():
    """Should return new list."""
    tour = [0, 1, 2, 3, 0]
    original = tour.copy()
    result = invert_segment(tour, 1, 2)
    assert tour == original
