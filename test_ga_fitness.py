#!/usr/bin/env python3
"""Minimal test to check GA fitness calculation."""

import sys
import numpy as np

# Direct import check
from code.src.algorithms.metaheuristics.genetic_algorithm_hybrid_naive import (
    GeneticAlgorithmHybridNaive,
)
from code.src.loaders.database_loader import DatabaseLoader
from code.src.protocols.problem_context import ProblemContext
from pathlib import Path

# Load problem
db_path = Path("datasets/routing.duckdb")
with DatabaseLoader(str(db_path)) as loader:
    problem = loader.load("kroA100")

print(f"Loaded: kroA100 (n={problem.dimension})")
print(f"TSPLIB optimal: 21282")
print()

# Create context
context = ProblemContext(problem, xp=np)
distances = context.distances

# Test 1: Manual tour cost calculation
np.random.seed(42)
test_tour = np.random.permutation(problem.dimension).astype(np.int32)
manual_cost = sum(
    distances[test_tour[i], test_tour[(i + 1) % len(test_tour)]]
    for i in range(len(test_tour))
)
print(f"Test 1: Manual cost calculation")
print(f"  Random tour (seed=42): {test_tour[:10]}...")
print(f"  Cost: {manual_cost:.2f}")
print()

# Test 2: GA fitness function
ga = GeneticAlgorithmHybridNaive(
    population_size=10,
    mutation_rate=0.02,
    tournament_size=3,
    two_opt_iterations=1,
    seed=42,
)

# Create population with our test tour
population = np.array([test_tour] * 10)  # 10 copies of same tour
fitness = ga._evaluate_population(population, distances, np)
print(f"Test 2: GA fitness function")
print(f"  Same tour (10 copies)")
print(f"  Fitness[0]: {fitness[0]:.2f}")
print(f"  All identical: {np.all(fitness == fitness[0])}")
print(f"  Matches manual: {np.isclose(fitness[0], manual_cost)}")
print()

# Test 3: Initial population
initial_pop = ga._initialize_population(problem.dimension)
initial_fitness = ga._evaluate_population(initial_pop, distances, np)
print(f"Test 3: Initial random population")
print(f"  Population shape: {initial_pop.shape}")
print(f"  Tour 0: {initial_pop[0][:10]}...")
print(f"  Best cost: {initial_fitness.min():.2f}")
print(f"  Avg cost: {initial_fitness.mean():.2f}")
print(f"  Worst cost: {initial_fitness.max():.2f}")
print(f"  All below optimal?: {np.all(initial_fitness < 21282)}")
print()

# Test 4: Check tour validity
print(f"Test 4: Tour validity checks")
for i in range(min(3, len(initial_pop))):
    tour = initial_pop[i]
    unique = len(np.unique(tour))
    expected = problem.dimension
    contains_all = set(tour) == set(range(problem.dimension))
    print(f"  Tour {i}: unique={unique}/{expected}, valid={contains_all}")
