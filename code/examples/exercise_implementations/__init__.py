"""
GPU Implementation Examples for Chapter Exercise Solutions

This module provides GPU-accelerated implementations for the mathematical
concepts explored in the exercise markdown files. These implementations
complement the theoretical analysis with practical computational validation.

Structure:
- TSP analysis and bounds verification
- CVRP heuristics and performance testing
- Probabilistic analysis validation
- Set partitioning and column generation examples

Usage:
    from exercise_implementations import tsp_examples, cvrp_examples

    # Run TSP lower bound verification
    results = tsp_examples.verify_tsp_lower_bound(n_points=1000)

    # Test CVRP heuristics
    solution = cvrp_examples.run_nearest_neighbor_heuristic(problem_data)
"""

from .tsp_examples import *
from .cvrp_examples import *
from .probabilistic_examples import *
from .set_partitioning_examples import *

__all__ = [
    "verify_tsp_lower_bound",
    "run_strips_method",
    "hybrid_tsp_strategy",
    "nearest_neighbor_cvrp",
    "christofides_cvrp",
    "monte_carlo_validation",
    "column_generation_demo",
    "set_partitioning_solver",
]
