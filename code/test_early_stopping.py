#!/usr/bin/env python3
"""Quick test of early stopping feature."""

from pathlib import Path
from src.algorithms.metaheuristics.genetic_algorithm_full_gpu_iso import GeneticAlgorithmFullGPU
from src.loaders.database_loader import DatabaseLoader
from src.protocols.problem_context import ProblemContext
import cupy as cp
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Load problem
db_path = Path(__file__).parent.parent / "datasets" / "routing.duckdb"
with DatabaseLoader(str(db_path)) as loader:
    problem = loader.load('kroA100')

customers = list(range(problem.dimension))
context = ProblemContext(problem, xp=cp)

print("=" * 80)
print("EARLY STOPPING TEST: kroA100")
print("=" * 80)
print(f"Optimal cost: 21282")
print(f"Max generations: 2000")
print(f"Patience: 50 (stop if no improvement)")
print()

# Test GA with early stopping
ga = GeneticAlgorithmFullGPU(
    population_size=100, 
    mutation_rate=0.01,
    tournament_size=5,
    two_opt_iterations=10,
    seed=42
)
tour, stats = ga.evolve(
    context, 
    customers, 
    max_generations=2000, 
    optimal_cost=21282,  # Stop when reached
    patience=50  # Stop if no improvement for 50 gens
)

print()
print("=" * 80)
print("RESULTS")
print("=" * 80)
print(f"Final cost: {stats['best_fitness']:.2f}")
print(f"Optimal cost: 21282.00")
print(f"Gap: {(stats['best_fitness'] - 21282) / 21282 * 100:.2f}%")
print(f"Generations run: {len(stats['best_cost_history'])}/2000")
print(f"Stopped early: {'YES' if len(stats['best_cost_history']) < 2000 else 'NO'}")
print()

if stats['best_fitness'] <= 21282:
    print("✅ SUCCESS: Reached optimal and stopped early!")
elif len(stats['best_cost_history']) < 2000:
    print("✅ SUCCESS: Stagnated and stopped early!")
else:
    print("❌ FAILED: Did not stop early")
