#!/usr/bin/env python3
"""Diagnostic Test: HybridNaive vs CPU Correctness Validation.

Author: AI Assistant (Actor-Critic Debug Session)
Date: 2025-01-28
"""

import numpy as np
import cupy as cp
from src.algorithms.metaheuristics.genetic_algorithm_cpu import GeneticAlgorithmCPU
from src.algorithms.metaheuristics.genetic_algorithm_hybrid_naive import (
    GeneticAlgorithmHybridNaive,
)
from src.loaders.database_loader import DatabaseLoader
from src.protocols.problem_context import ProblemContext


def run_diagnostic():
    print("=" * 70)
    print("DIAGNOSTIC: HybridNaive Correctness")
    print("=" * 70)
    print()

    db_path = "../datasets/routing.duckdb"
    with DatabaseLoader(db_path) as loader:
        problem = loader.load("kroA100")
    customers = list(range(problem.dimension))

    print(f"Problem: kroA100 (n={problem.dimension})")
    print("Optimal: 21282")
    print()

    config = {
        "population_size": 10,
        "mutation_rate": 0.1,
        "tournament_size": 2,
        "two_opt_iterations": 10,
    }
    SEED = 42

    # CPU
    print("TEST 1: CPU")
    print("-" * 70)
    np.random.seed(SEED)
    ga_cpu = GeneticAlgorithmCPU(**config)
    ctx_cpu = ProblemContext(problem, xp=np)

    import time

    t0 = time.perf_counter()
    tour_cpu, stats_cpu = ga_cpu.evolve(ctx_cpu, customers, max_generations=1)
    t_cpu = time.perf_counter() - t0

    print(f"Initial: {stats_cpu['initial_fitness']:.2f}")
    print(f"Final: {stats_cpu['best_fitness']:.2f}")
    print(f"Time: {t_cpu:.4f}s\n")

    # GPU
    print("TEST 2: HybridNaive (GPU)")
    print("-" * 70)
    if not cp.cuda.is_available():
        print("❌ GPU unavailable")
        return

    print(f"✓ GPU: {cp.cuda.runtime.getDeviceProperties(0)['name'].decode()}")
    np.random.seed(SEED)
    ga_gpu = GeneticAlgorithmHybridNaive(**config)
    ctx_gpu = ProblemContext(problem, xp=cp)

    t0 = time.perf_counter()
    tour_gpu, stats_gpu = ga_gpu.evolve(ctx_gpu, customers, max_generations=1)
    t_gpu = time.perf_counter() - t0

    print(f"Initial: {stats_gpu['initial_fitness']:.2f}")
    print(f"Final: {stats_gpu['best_fitness']:.2f}")
    print(f"Time: {t_gpu:.4f}s")
    print(
        f"Transfers: {stats_gpu.get('h2d_bytes', 0) / 1e6:.2f}MB H2D, {stats_gpu.get('d2h_bytes', 0) / 1e6:.2f}MB D2H"
    )
    print(f"Kernels: {stats_gpu.get('kernel_launches', 0)}\n")

    # Compare
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    initial_diff = abs(stats_cpu["initial_fitness"] - stats_gpu["initial_fitness"])
    final_diff = abs(stats_cpu["best_fitness"] - stats_gpu["best_fitness"])
    speedup = t_cpu / t_gpu

    print(f"Initial diff: {initial_diff:.2e} {'✅' if initial_diff < 1e-6 else '❌'}")
    print(f"Final diff: {final_diff:.2e} {'✅' if final_diff < 1e-6 else '⚠️'}")
    print(f"Speedup: {speedup:.2f}x {'✅' if speedup >= 3 else '⚠️'}")

    if final_diff >= 1e-6:
        print(
            f"\n⚠️  Quality mismatch: CPU={stats_cpu['best_fitness']:.2f}, GPU={stats_gpu['best_fitness']:.2f}"
        )


if __name__ == "__main__":
    run_diagnostic()
