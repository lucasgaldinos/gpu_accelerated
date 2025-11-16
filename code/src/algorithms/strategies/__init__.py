"""
Algorithm strategy implementations for "Lego Blocks" compositional CVRP.

This package provides concrete strategy implementations for:
- Bin packing algorithms (FFD, BFD)
- TSP construction heuristics (Nearest Neighbor, Christofides)
- Clustering algorithms (K-Means, DBSCAN) [Future]

These strategies implement protocols defined in `protocols.algorithm_strategies`
and can be mixed and matched via dependency injection.

Example Usage:
    >>> from algorithms.strategies import FFDStrategy, NearestNeighborStrategy
    >>> from algorithms.compositional_cvrp_solver import lego_cvrp_solver
    >>>
    >>> routes = lego_cvrp_solver(
    ...     locations, demands, capacity,
    ...     bin_packing_strategy=FFDStrategy(),
    ...     tsp_strategy=NearestNeighborStrategy(),
    ...     xp=cp  # GPU backend
    ... )

See Also:
    - protocols.algorithm_strategies: Protocol definitions
    - algorithms.compositional_cvrp_solver: Main composition function
"""

# Export implemented strategies
from .bin_packing_strategies import FFDStrategy, BFDStrategy
from .construction_strategies import (
    RandomConstructionStrategy,
    NearestNeighborStrategy,
    ChristofidesStrategy,
)

# Clustering strategies not yet implemented
# from .clustering_strategies import KMeansStrategy, DBSCANStrategy

__all__ = [
    # Bin Packing Strategies
    "FFDStrategy",
    "BFDStrategy",
    # TSP Construction Strategies
    "RandomConstructionStrategy",
    "NearestNeighborStrategy",
    "ChristofidesStrategy",
    # Clustering Strategies (Future)
    # 'KMeansStrategy',
    # 'DBSCANStrategy',
]
