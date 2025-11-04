"""
Algorithm implementations for TSP/VRP optimization.

This module contains various algorithm strategies that implement the
CPU and GPU protocols. Algorithms can be composed together using the
compositional solver pattern.
"""

from .nearest_neighbor_cpu import NearestNeighborCPU
from .random_insertion_cpu import RandomInsertionCPU
from .cheapest_insertion_cpu import CheapestInsertionCPU
from .compositional_solver import CompositionalTSPSolver

__all__ = [
    'NearestNeighborCPU',
    'RandomInsertionCPU',
    'CheapestInsertionCPU',
    'CompositionalTSPSolver',
]

# GPU algorithms are imported conditionally
try:
    from .two_opt_gpu import TwoOptGPU
    __all__.append('TwoOptGPU')
except (ImportError, RuntimeError):
    # CuPy not available
    pass
