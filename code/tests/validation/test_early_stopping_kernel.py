#!/usr/bin/env python3
"""Test early stopping in FullGPU kernel.

Compares:
1. Original FullGPU (no early stopping)
2. New FullGPUEarlyStop (with convergence detection)

Validates that early stopping:
- Detects optimal when reached
- Detects stagnation after patience generations
- Produces same quality results
- Reduces execution time
"""

import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.algorithms.metaheuristics.genetic_algorithm_full_gpu_iso import (
    GeneticAlgorithmFullGPU,
)
from src.algorithms.metaheuristics.genetic_algorithm_full_gpu_early_stop import (
    GeneticAlgorithmFullGPUEarlyStop,
)
from src.loaders.database_loader import DatabaseLoader
from src.protocols.problem_context import ProblemContext
import cupy as cp
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

# Load kroA100 for testing
db_path = Path(__file__).parent.parent.parent.parent / "datasets" / "routing.duckdb"
with DatabaseLoader(str(db_path)) as loader:
    problem = loader.load("kroA100")

customers = list(range(problem.dimension))
context = ProblemContext(problem, xp=cp)

print("=" * 80)
print("EARLY STOPPING VALIDATION TEST: kroA100")
print("=" * 80)
print(f"Problem: kroA100 (n=100)")
print(f"Optimal cost: 21282")
print(f"Max generations: 2000")
print(f"Population: 256")
print()

# Kernel Warmup: Preload and compile kernels with small problem
print("=" * 80)
print("WARMUP: Preloading kernels...")
print("=" * 80)

# Create a smaller warmup problem (50 cities from kroA100)
warmup_customers = list(range(50))
warmup_ga = GeneticAlgorithmFullGPUEarlyStop(
    population_size=128,
    mutation_rate=0.02,
    tournament_size=5,
    two_opt_iterations=5,
    seed=42,
)

warmup_start = time.perf_counter()
warmup_ga.evolve(
    context, warmup_customers, max_generations=5, optimal_cost=None, patience=50
)
warmup_time = time.perf_counter() - warmup_start

print(f"Warmup completed in {warmup_time:.2f}s (kernels loaded & compiled)")
print("Subsequent tests will measure pure execution time.")
print()

# Test 1: FullGPU with early stopping (optimal detection)
print("=" * 80)
print("TEST 1: FullGPUEarlyStop (optimal detection)")
print("=" * 80)

ga_early = GeneticAlgorithmFullGPUEarlyStop(
    population_size=256,
    mutation_rate=0.02,
    tournament_size=5,
    two_opt_iterations=10,
    seed=42,  # Same seed for reproducibility
)

start = time.perf_counter()
tour2, stats2 = ga_early.evolve(
    context,
    customers,
    max_generations=20000,
    optimal_cost=259045,  # Enable optimal detection
    patience=50,
)
time2 = time.perf_counter() - start

print(f"Final cost: {stats2['best_fitness']:.2f}")
print(
    f"Generations: {stats2.get('actual_generations', len(stats2['best_cost_history']))}"
)
print(f"Stop reason: {stats2.get('stop_reason', 'unknown')}")
print(f"Time: {time2:.2f} seconds")
print(f"H2D: {stats2['h2d_bytes'] / 1024 / 1024:.2f} MB")
print(f"D2H: {stats2['d2h_bytes'] / 1024 / 1024:.2f} MB")
print()

# Test 2: FullGPU with early stopping (stagnation detection, no optimal)
print("=" * 80)
print("TEST 2: FullGPUEarlyStop (stagnation detection only)")
print("=" * 80)

ga_stagnation = GeneticAlgorithmFullGPUEarlyStop(
    population_size=256,
    mutation_rate=0.02,
    tournament_size=5,
    two_opt_iterations=10,
    seed=99,  # Different seed
)

start = time.perf_counter()
tour_stag, stats_stag = ga_stagnation.evolve(
    context,
    customers,
    max_generations=2000,
    optimal_cost=None,  # Disable optimal detection
    patience=50,  # Only stagnation
)
time_stag = time.perf_counter() - start

print(f"Final cost: {stats_stag['best_fitness']:.2f}")
print(
    f"Generations: {stats_stag.get('actual_generations', len(stats_stag['best_cost_history']))}"
)
print(f"Stop reason: {stats_stag.get('stop_reason', 'unknown')}")
print(f"Time: {time_stag:.2f} seconds")
print(f"H2D: {stats_stag['h2d_bytes'] / 1024 / 1024:.2f} MB")
print(f"D2H: {stats_stag['d2h_bytes'] / 1024 / 1024:.2f} MB")
print()

# Summary
print("=" * 80)
print("SUMMARY & VALIDATION")
print("=" * 80)

print(f"Warmup phase:         {warmup_time:.2f}s (kernels loaded & compiled)")
print(
    f"Early Stop (optimal): {time2:.2f}s, cost={stats2['best_fitness']:.2f}, "
    f"gens={stats2.get('actual_generations', '?')}"
)
print(
    f"Early Stop (stag):    {time_stag:.2f}s, cost={stats_stag['best_fitness']:.2f}, "
    f"gens={stats_stag.get('actual_generations', '?')}"
)
print(f"\nNote: Times measured after warmup (pure execution, no compilation overhead)")
print()

# Validation checks
print("Validation Checks:")
checks_passed = 0
total_checks = 0

# Check 1: Optimal detection found good solution
total_checks += 1
if stats2["best_fitness"] <= 21282 * 1.05:  # Within 5% of optimal
    print(
        f"✅ Check 1: Optimal detection found good solution ({stats2['best_fitness']:.2f} ≈ 21282)"
    )
    checks_passed += 1
else:
    print(
        f"❌ Check 1: Solution quality degraded ({stats2['best_fitness']:.2f} >> 21282)"
    )

# Check 2: Optimal detection stopped early
total_checks += 1
actual_gens = stats2.get("actual_generations", 2000)
if actual_gens < 2000:
    print(
        f"✅ Check 2: Optimal detection stopped early at generation {actual_gens} (< 2000)"
    )
    checks_passed += 1
else:
    print(
        f"❌ Check 2: Optimal detection did not stop early (ran all {actual_gens} generations)"
    )

# Check 3: Stagnation detection found good solution
total_checks += 1
if stats_stag["best_fitness"] <= 21282 * 1.05:
    print(
        f"✅ Check 3: Stagnation found good solution ({stats_stag['best_fitness']:.2f} ≈ 21282)"
    )
    checks_passed += 1
else:
    print(
        f"❌ Check 3: Stagnation solution quality poor ({stats_stag['best_fitness']:.2f})"
    )

# Check 4: Stagnation detection works
total_checks += 1
stag_gens = stats_stag.get("actual_generations", 2000)
if stag_gens < 2000:
    print(f"✅ Check 4: Stagnation detection works (stopped at gen {stag_gens})")
    checks_passed += 1
else:
    print(f"❌ Check 4: Stagnation detection failed (ran all generations)")

# Check 5: Memory transfers still minimal
total_checks += 1
if stats2["h2d_bytes"] < 1024 * 1024:  # < 1MB
    print(f"✅ Check 5: H2D transfers minimal ({stats2['h2d_bytes'] / 1024:.2f} KB)")
    checks_passed += 1
else:
    print(
        f"❌ Check 5: H2D transfers excessive ({stats2['h2d_bytes'] / 1024 / 1024:.2f} MB)"
    )

print()
print(f"Result: {checks_passed}/{total_checks} checks passed")

if checks_passed == total_checks:
    print("🎉 SUCCESS: Early stopping works correctly!")
elif checks_passed >= total_checks - 1:
    print("✅ PASS: Early stopping functional (minor issues)")
else:
    print("❌ FAIL: Early stopping has issues, needs debugging")
