"""
Swap two cities in a tour.

Used by:
- RandomSwapStrategy (SA neighbor generation)
- SwapMutation (GA mutation)

Complexity: O(1) - in-place swap
"""

from typing import List


def swap_cities(tour: List[int], i: int, j: int) -> List[int]:
    """
    Swap cities at positions i and j.

    Args:
        tour: Tour to modify [depot, c1, c2, ..., depot]
        i, j: Positions to swap (0 < i, j < len(tour)-1)
            - i, j should NOT be depot positions (0 or len-1)
            - Order doesn't matter (swap(i,j) == swap(j,i))

    Returns:
        Modified tour with tour[i] ↔ tour[j]

    Example:
        >>> tour = [0, 5, 3, 7, 2, 0]
        >>> swap_cities(tour, 1, 3)  # Swap cities 5 and 7
        [0, 7, 3, 5, 2, 0]

    Note:
        Creates NEW list (does not modify in-place).
        For in-place version, use tour[i], tour[j] = tour[j], tour[i]
    """
    new_tour = tour.copy()
    new_tour[i], new_tour[j] = new_tour[j], new_tour[i]
    return new_tour
