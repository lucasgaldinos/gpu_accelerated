"""
Reverse a segment of the tour (2-opt move operation).

Used by:
- Random2OptStrategy (SA neighbor generation)
- InversionMutation (GA mutation)
- TwoOptCPU/GPU (improvement operators)

Complexity: O(k) where k = j - i (segment length)

References:
- Croes (1958): "A method for solving traveling salesman problems"
- Lin & Kernighan (1973): "An effective heuristic for TSP"
"""

from typing import List


def invert_segment(tour: List[int], i: int, j: int) -> List[int]:
    """
    Reverse tour segment between positions i and j (inclusive).

    Args:
        tour: Tour to modify [depot, c1, c2, ..., depot]
        i, j: Segment boundaries (0 < i < j < len-1)
            - Segment tour[i:j+1] will be reversed
            - Depot positions excluded

    Returns:
        Modified tour with reversed segment

    Example:
        >>> tour = [0, 1, 2, 3, 4, 5, 0]
        >>> invert_segment(tour, 2, 4)  # Reverse [2,3,4]
        [0, 1, 4, 3, 2, 5, 0]

    2-opt Interpretation:
        Reversing [i, j] breaks edges (i-1, i) and (j, j+1),
        adds edges (i-1, j) and (i, j+1).

    Algorithm:
        tour[:i] + reversed(tour[i:j+1]) + tour[j+1:]
    """
    if i > j:
        i, j = j, i  # Ensure i < j

    new_tour = tour[:i] + tour[i : j + 1][::-1] + tour[j + 1 :]
    return new_tour
