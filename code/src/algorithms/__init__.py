"""
Optimization algorithms package.

This package provides modular "Lego brick" optimization strategies that can
be composed together to form hybrid metaheuristics.
"""

from .nearest_neighbor import NearestNeighborStrategy
from .two_opt import TwoOptStrategy
from .simulated_annealing import SimulatedAnnealingStrategy
from .genetic_algorithm import GeneticAlgorithmStrategy
from .composable_solver import ComposableSolver, StrategyChain

__all__ = [
    'NearestNeighborStrategy',
    'TwoOptStrategy',
    'SimulatedAnnealingStrategy',
    'GeneticAlgorithmStrategy',
    'ComposableSolver',
    'StrategyChain',
]
