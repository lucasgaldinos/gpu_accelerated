"""
Remove city from tour and reinsert at different position.

Used by:
- RandomInsertionStrategy (SA neighbor generation)
- InsertionMutation (GA mutation)

Complexity: O(n) - list slicing and concatenation
"""

from typing import List


def insert_city(tour: List[int], from_pos: int, to_pos: int) -> List[int]:
    """
    Remove city at from_pos and insert at to_pos.

    Args:
        tour: Tour to modify [depot, c1, c2, ..., depot]
        from_pos: Position to remove city from (0 < from_pos < len-1)
        to_pos: Position to insert city at (0 < to_pos < len-1)
            - Positions are depot-exclusive (cannot move depot)

    Returns:
        Modified tour with city moved

    Example:
        >>> tour = [0, 5, 3, 7, 2, 0]
        >>> insert_city(tour, 1, 3)  # Move city 5 to position 3
        [0, 3, 7, 5, 2, 0]
        # Removed 5, shifted [3,7] left, inserted 5 before 2

    Algorithm:
        1. Extract city at from_pos
        2. Remove from_pos from tour
        3. Insert city at to_pos
    """
    new_tour = tour.copy()
    city = new_tour.pop(from_pos)
    new_tour.insert(to_pos, city)
    return new_tour
