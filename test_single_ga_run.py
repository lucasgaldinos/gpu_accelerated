#!/usr/bin/env python3
"""Quick single-run GA test to debug the cost issue."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "code"))

import numpy as np
import cupy as cp
from src.loaders.database_loader import DatabaseLoader
from src.protocols.problem_context import ProblemContext
from src.algorithms.metaheuristics.genetic_algorithm_hybrid_naive import (
    GeneticAlgorithmHybridNaive,
)

# Load kroA100
db_path = Path("datasets/routing.duckdb")
with DatabaseLoader(str(db_path)) as loader:
    problem = loader.load("kroA100")

# Create context
context = ProblemContext(problem, xp=cp)

# Create GA
ga = GeneticAlgorithmHybridNaive(
    population_size=10,  # Small for testing
    mutation_rate=0.02,
    tournament_size=3,
    two_opt_iterations=1,
    seed=42,
)

# Run for just 1 generation
customers = list(range(problem.dimension))
tour, stats = ga.evolve(context, customers, max_generations=1)

print(f"Problem: kroA100 (n={problem.dimension})")
print(f"TSPLIB optimal: 21282")
print()
print(f"Best tour after 1 generation:")
print(f"  Tour length: {len(tour)}")
print(f"  Unique cities: {len(set(tour))}")
print(f"  All cities present: {set(tour) == set(range(problem.dimension))}")
print(f"  Tour: {tour[:20]}...")
print(f"  Best cost: {stats['best_fitness']:.2f}")
print(f"  Initial cost: {stats['initial_fitness']:.2f}")
print()

# Manual validation
distances = context.get_cpu_distances()
manual_cost = sum(
    distances[tour[i], tour[(i + 1) % len(tour)]] for i in range(len(tour))
)
print(f"Manual cost recalculation: {manual_cost:.2f}")
print(f"Matches GA cost: {np.isclose(manual_cost, stats['best_fitness'])}")
