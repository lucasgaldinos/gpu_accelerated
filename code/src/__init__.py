"""
GPU-Accelerated TSP/VRP Optimization Framework.

This package provides a modular architecture for solving TSP and VRP problems
using both CPU and GPU backends.

Example:
    >>> from src.protocols import ProblemContext
    >>> from src.algorithms import NearestNeighborCPU
    >>> 
    >>> coords = [[0, 0], [1, 0], [1, 1], [0, 1]]
    >>> context = ProblemContext(coordinates=coords)
    >>> solver = NearestNeighborCPU()
    >>> tour = solver.solve(context)
"""

from .protocols import (
    ProblemContext,
    CUPY_AVAILABLE,
    CPUStrategy,
    GPUStrategy,
    ImprovementStrategy,
    ComposableStrategy,
)

from .algorithms import (
    NearestNeighborCPU,
    RandomInsertionCPU,
    CheapestInsertionCPU,
    CompositionalTSPSolver,
)

__all__ = [
    # Core
    'ProblemContext',
    'CUPY_AVAILABLE',
    
    # Protocols
    'CPUStrategy',
    'GPUStrategy',
    'ImprovementStrategy',
    'ComposableStrategy',
    
    # Algorithms
    'NearestNeighborCPU',
    'RandomInsertionCPU',
    'CheapestInsertionCPU',
    'CompositionalTSPSolver',
]

# Conditionally export GPU algorithms
if CUPY_AVAILABLE:
    from .algorithms import TwoOptGPU
    __all__.append('TwoOptGPU')

__version__ = '0.1.0'
