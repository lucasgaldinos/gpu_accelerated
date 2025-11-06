"""
Metaheuristic algorithms for TSP and CVRP.

This module provides population-based and trajectory-based metaheuristics
for solving routing problems.

Classes:
    SimulatedAnnealing: Single-trajectory probabilistic search
    GeneticAlgorithm: Population-based evolutionary algorithm with OX crossover
"""

from .simulated_annealing import SimulatedAnnealing
from .genetic_algorithm import GeneticAlgorithm

__all__ = ["SimulatedAnnealing", "GeneticAlgorithm"]
