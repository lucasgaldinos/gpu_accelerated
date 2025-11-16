"""
Tour operators (city-level mutations).

Shared utilities for SA neighbor methods and GA mutations.
Pure functions - take tour, return modified tour.

Architecture:
    Layer 2 in import dependency graph:
    - Imports FROM: protocols/ (BackendModule)
    - Imports TO: strategies/ (neighbor_strategies, mutation_strategies)
    - NEVER imports: metaheuristics/

Design Philosophy:
    - Pure functions (no side effects)
    - Backend-agnostic (work with NumPy or CuPy)
    - Single Responsibility (each operator does ONE thing)
    - DRY (Don't Repeat Yourself) - shared by SA and GA

Operators:
    - swap_cities: Swap two cities in a tour (O(1))
    - insert_city: Remove city, insert elsewhere (O(n))
    - invert_segment: Reverse tour segment (O(k)) - used in 2-opt

Used By:
    - strategies/neighbor_strategies.py (SA neighbor generation)
    - strategies/mutation_strategies.py (GA mutation operators)
    - NOT used directly by metaheuristics (they use strategies)

Example:
    >>> from code.src.algorithms.tour_operators import swap_cities
    >>> tour = [0, 1, 2, 3, 4, 0]
    >>> new_tour = swap_cities(tour, 1, 3)
    >>> new_tour
    [0, 3, 2, 1, 4, 0]

See Also:
    - documentation/architecture/import_dependencies.md (layer definitions)
    - protocols/strategy_protocols.py (NeighborStrategy, MutationOperator)
"""

# Import tour operators
from .swap import swap_cities
from .insertion import insert_city
from .inversion import invert_segment

__all__ = [
    "swap_cities",
    "insert_city",
    "invert_segment",
]
