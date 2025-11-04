"""
GPU-Accelerated TSP/VRP Optimization Framework.

This package provides a modular architecture for solving TSP and VRP problems
using both CPU and GPU backends with ProblemContext-based caching.

Example:
    >>> from src.loaders import DatabaseLoader
    >>> from src.protocols import ProblemContext
    >>> from src.algorithms.strategies import NearestNeighborStrategy
    >>> import numpy as np
    >>> 
    >>> with DatabaseLoader() as loader:
    ...     problem = loader.load('berlin52')
    >>> 
    >>> context = ProblemContext(problem, xp=np)
    >>> strategy = NearestNeighborStrategy()
    >>> tour = strategy.build_tour(context, customers=[1, 2, 3])
"""

# Core exports - minimal to avoid circular imports
__version__ = '0.1.0'

__all__ = ['__version__']
