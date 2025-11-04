"""
TSP Construction Heuristics.

This module contains greedy construction algorithms for building initial
TSP tours from scratch.
"""

from .nearest_neighbor import nearest_neighbor
from .minimum_spanning_tree import minimum_spanning_tree
from .christofides import christofides

__all__ = [
    "nearest_neighbor",
    "minimum_spanning_tree",
    "christofides",
]  # TODO update anytime a new heuristic is added.
