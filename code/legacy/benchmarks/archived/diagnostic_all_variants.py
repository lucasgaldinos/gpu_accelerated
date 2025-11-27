#!/usr/bin/env python3
"""Diagnostic: Compare ALL GA variants for quality consistency.

Tests if HybridOptimized and FullGPU also show quality degradation vs CPU.
If all GPU variants degrade by ~1.8%, the bug is in shared kernel/logic.

Author: AI Assistant
Date: 2025-01-28
"""

import numpy as np
import cupy as cp
import time
from src.algorithms.metaheuristics.genetic_algorithm_cpu import GeneticAlgorithmCPU
from src.algorithms.metaheuristics.genetic_algorithm_hybrid_naive import GeneticAlgorithmHybridNaive
from src.algorithms.metaheuristics.genetic_algorithm_hybrid_optimized import GeneticAlgorithmHybridOptimized
from src.algorithms.metaheuristics.genetic_algorithm_full_gpu_iso import GeneticAlgorithmFullGPU
from src.loaders.database_loader import DatabaseLoader
from src.protocols.problem_context import ProblemContext

def test_variant(name, ga_class, config, problem, customers, seed, use_gpu=False):
    """Run single variant and return stats."""
    np.random.seed(seed)
    ga = ga_class(**config)
    xp = cp if use_gpu else np
    ctx = ProblemContext(problem, xp=xp)
    
    t0 = time.perf_counter()
    tour, stats = ga.evolve(ctx, customers, max_generations=1)
    elapsed = time.perf_counter() - t0
    
    return {
        "name": name,
        "initial": stats['initial_fitness'],
        "final": stats['best_fitness'],
        "improvement": stats['initial_fitness'] - stats['best_fitness'],
        "time": elapsed,
        "h2d_mb": stats.get('h2d_bytes', 0) / 1e6,
        "d2h_mb": stats.get('d2h_bytes', 0) / 1e6,
        "kernels": stats.get('kernel_launches', 0),
    }

def main():
    print("=" * 80)
    print("DIAGNOSTIC: Quality Comparison Across All GA Variants")
    print("=" * 80)
    print()
    
    # Load problem
    db_path = "../datasets/routing.duckdb"
    with DatabaseLoader(db_path) as loader:
        problem = loader.load("kroA100")
    customers = list(range(problem.dimension))
    
    print(f"Problem: kroA100 (n={problem.dimension})")
    print(f"Optimal: 21282")
    print()
    
    # Check GPU
    if not cp.cuda.is_available():
        print("❌ GPU unavailable - cannot test GPU variants")
        return
    print(f"✓ GPU: {cp.cuda.runtime.getDeviceProperties(0)['name'].decode()}")
    print()
    
    config = {
        "population_size": 10,
        "mutation_rate": 0.1,
        "tournament_size": 2,
        "two_opt_iterations": 10,
    }
    SEED = 42
    
    # Test all variants
    print("Running variants (1 generation each)...")
    print("-" * 80)
    
    results = []
    
    # CPU baseline
    print("1/4 CPU...")
    results.append(test_variant("CPU", GeneticAlgorithmCPU, config, problem, customers, SEED, use_gpu=False))
    
    # GPU variants
    print("2/4 HybridNaive...")
    results.append(test_variant("HybridNaive", GeneticAlgorithmHybridNaive, config, problem, customers, SEED, use_gpu=True))
    
    print("3/4 HybridOptimized...")
    results.append(test_variant("HybridOptimized", GeneticAlgorithmHybridOptimized, config, problem, customers, SEED, use_gpu=True))
    
    print("4/4 FullGPU...")
    try:
        results.append(test_variant("FullGPU", GeneticAlgorithmFullGPU, config, problem, customers, SEED, use_gpu=True))
    except Exception as e:
        print(f"   ⚠️  FullGPU FAILED: {e}")
        results.append({"name": "FullGPU", "final": None, "time": None})
    
    print()
    
    # Display results
    print("=" * 80)
    print("RESULTS COMPARISON")
    print("=" * 80)
    print()
    
    cpu_result = results[0]
    
    print(f"{'Variant':<20} {'Initial':<12} {'Final':<12} {'Δ vs CPU':<12} {'Time (s)':<10} {'Speedup':<8}")
    print("-" * 80)
    
    for r in results:
        if r['final'] is None:
            print(f"{r['name']:<20} {'N/A':<12} {'N/A':<12} {'FAILED':<12} {'N/A':<10} {'N/A':<8}")
            continue
            
        delta_vs_cpu = r['final'] - cpu_result['final']
        pct_diff = (delta_vs_cpu / cpu_result['final']) * 100
        speedup = cpu_result['time'] / r['time'] if r['time'] > 0 else 0
        
        status = ""
        if abs(delta_vs_cpu) < 1e-6:
            status = " ✅"
        elif delta_vs_cpu > 0:
            status = f" ⚠️ +{pct_diff:.2f}%"
        else:
            status = f" ⬇️ {pct_diff:.2f}%"
        
        print(f"{r['name']:<20} {r['initial']:<12.2f} {r['final']:<12.2f} {delta_vs_cpu:<12.2f} {r['time']:<10.4f} {speedup:<8.2f}x{status}")
    
    print()
    
    # Analysis
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()
    
    gpu_results = [r for r in results[1:] if r['final'] is not None]
    
    if not gpu_results:
        print("❌ No GPU variants succeeded")
        return
    
    all_degrade = all(r['final'] > cpu_result['final'] + 1e-6 for r in gpu_results)
    all_equivalent = all(abs(r['final'] - cpu_result['final']) < 1e-6 for r in gpu_results)
    
    if all_equivalent:
        print("✅ ALL GPU variants produce IDENTICAL results to CPU")
        print("   → No quality degradation bug")
        print("   → Floating-point determinism maintained")
    elif all_degrade:
        print("⚠️  ALL GPU variants show quality DEGRADATION vs CPU")
        print("   → Bug is in SHARED kernel logic (not variant-specific)")
        print("   → Likely issue in:")
        print("      1. two_opt_single.cu kernel (tour reversal?)")
        print("      2. Parallel reduction (non-deterministic tie-breaking?)")
        print("      3. Distance matrix indexing (row-major vs col-major?)")
    else:
        print("⚠️  MIXED results - some GPU variants worse, some equivalent")
        print("   → Bug is VARIANT-SPECIFIC (not shared kernel)")
        print()
        for r in gpu_results:
            diff = r['final'] - cpu_result['final']
            if abs(diff) > 1e-6:
                print(f"   {r['name']}: {diff:+.2f} ({diff/cpu_result['final']*100:+.2f}%)")
    
    print()
    
    # Detailed comparison
    print("Detailed Metrics:")
    print("-" * 80)
    for r in results:
        if r['final'] is None:
            continue
        print(f"\n{r['name']}:")
        print(f"  Initial cost: {r['initial']:.2f}")
        print(f"  Final cost: {r['final']:.2f}")
        print(f"  Improvement: {r['improvement']:.2f} ({r['improvement']/r['initial']*100:.2f}%)")
        print(f"  Time: {r['time']:.4f}s")
        if 'h2d_mb' in r:
            print(f"  Transfers: {r['h2d_mb']:.2f}MB H2D, {r['d2h_mb']:.2f}MB D2H")
            print(f"  Kernel launches: {r['kernels']}")

if __name__ == "__main__":
    main()
