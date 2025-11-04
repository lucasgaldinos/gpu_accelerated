#!/usr/bin/env python3
"""
Algorithm Composition Examples - Runnable Demonstrations

This script provides concrete examples of algorithm composition patterns
documented in algorithm_composition_architecture.md.

Usage:
    # Run all examples (once implementations are complete)
    python -m scripts.algorithm_composition_examples

    # Run specific example
    python -m scripts.algorithm_composition_examples --example simple_pipeline

    # Use GPU backend
    python -m scripts.algorithm_composition_examples --backend cupy --example cpu_vs_gpu

⚠️  NOTE: This script requires GPU-8, GPU-9, GPU-12 implementations to run fully.
    Currently includes placeholder functions for demonstration purposes.
    Run after implementing the actual algorithms to see complete pipelines.

Examples Included:
    1. simple_pipeline: Construction → Evaluation
    2. improvement_pipeline: Construction → Improvement → Evaluation
    3. full_pipeline: Construction → Improvement → Metaheuristic (The Chimera)
    4. multi_start: Parallel pipelines with different start nodes
    5. cpu_vs_gpu: Backend comparison benchmark
    6. algorithm_comparison: Compare multiple construction heuristics
"""

import argparse
import time

import numpy as np

# Conditional CuPy import
try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False

# Import project modules
import sys
from pathlib import Path

# Add code/src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "code" / "src"))

from data_models.problem import Problem
from loaders.database_loader import DatabaseLoader
from algorithms.construction.nearest_neighbor import nearest_neighbor
from algorithms.objectives.tour_cost import compute_tour_cost


# Placeholder imports for not-yet-implemented algorithms
# These will be replaced with actual imports when implemented
def two_opt_first_improvement(problem, tour, xp=np):
    """Placeholder for GPU-8 implementation."""
    print("⚠️  two_opt_first_improvement not yet implemented (GPU-8)")
    return tour


def simulated_annealing(
    problem, initial_tour, temp=1000, cooling=0.95, max_iter=1000, xp=np
):
    """Placeholder for GPU-12 implementation."""
    print("⚠️  simulated_annealing not yet implemented (GPU-12)")
    return initial_tour


# ============================================================================
# EXAMPLE 1: Simple Pipeline (Construction → Evaluation)
# ============================================================================


def example_simple_pipeline(problem: Problem, xp=np):
    """
    Demonstrate simplest composition: construct solution and evaluate.

    Pipeline:
        Problem → [Nearest Neighbor] → Tour → [Cost Computation] → Cost

    Key Concepts:
        - Algorithm returns tour array only
        - Cost computed by separate utility
        - Backend-agnostic (works with NumPy or CuPy)
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Simple Pipeline (Construction → Evaluation)")
    print("=" * 80)

    backend_name = "CuPy (GPU)" if xp.__name__ == "cupy" else "NumPy (CPU)"
    print(f"Backend: {backend_name}")
    print(f"Problem: {problem.name} ({problem.dimension} nodes)")
    print()

    # Step 1: Construct solution
    print("Step 1: Construction Heuristic")
    print("  Algorithm: Nearest Neighbor")
    start_time = time.time()
    tour = nearest_neighbor(problem, start_node=0, xp=xp)
    construction_time = time.time() - start_time
    print(f"  ✓ Tour generated in {construction_time:.4f}s")
    print(f"  Tour preview: {tour[:10]}...")
    print()

    # Step 2: Evaluate solution
    print("Step 2: Evaluation")
    print("  Utility: compute_tour_cost()")
    cost = compute_tour_cost(problem, tour, xp=xp)
    print(f"  ✓ Total cost: {cost:.2f}")
    print()

    return {
        "tour": tour,
        "cost": cost,
        "time": construction_time,
        "backend": backend_name,
    }


# ============================================================================
# EXAMPLE 2: Improvement Pipeline (Construction → Improvement → Evaluation)
# ============================================================================


def example_improvement_pipeline(problem: Problem, xp=np):
    """
    Demonstrate construction followed by local search improvement.

    Pipeline:
        Problem → [NN] → Tour → [2-opt] → Improved Tour → [Cost] → Cost

    Key Concepts:
        - Improvement heuristic accepts existing tour
        - Sequential composition: output of NN becomes input of 2-opt
        - Compare before/after costs to measure improvement
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Improvement Pipeline (Construction → Improvement)")
    print("=" * 80)

    backend_name = "CuPy (GPU)" if xp.__name__ == "cupy" else "NumPy (CPU)"
    print(f"Backend: {backend_name}")
    print(f"Problem: {problem.name} ({problem.dimension} nodes)")
    print()

    # Step 1: Construction
    print("Step 1: Construction Heuristic")
    tour = nearest_neighbor(problem, start_node=0, xp=xp)
    initial_cost = compute_tour_cost(problem, tour, xp=xp)
    print(f"  ✓ NN tour cost: {initial_cost:.2f}")
    print()

    # Step 2: Improvement
    print("Step 2: Improvement Heuristic")
    print("  Algorithm: 2-opt First-Improvement")
    start_time = time.time()
    improved_tour = two_opt_first_improvement(problem, tour, xp=xp)
    improvement_time = time.time() - start_time
    improved_cost = compute_tour_cost(problem, improved_tour, xp=xp)
    print(f"  ✓ Improved tour cost: {improved_cost:.2f}")
    print(f"  ✓ Improvement time: {improvement_time:.4f}s")
    print()

    # Analysis
    improvement_pct = (initial_cost - improved_cost) / initial_cost * 100
    print("Analysis:")
    print(f"  Initial cost:     {initial_cost:.2f}")
    print(f"  Improved cost:    {improved_cost:.2f}")
    print(f"  Improvement:      {improvement_pct:.2f}%")
    print()

    return {
        "initial_tour": tour,
        "improved_tour": improved_tour,
        "initial_cost": initial_cost,
        "improved_cost": improved_cost,
        "improvement_percent": improvement_pct,
        "time": improvement_time,
    }


# ============================================================================
# EXAMPLE 3: Full Pipeline - The Chimera
# ============================================================================


def example_full_pipeline_chimera(problem: Problem, xp=np):
    """
    Demonstrate complete composition: construction → improvement → metaheuristic.

    Pipeline:
        Problem → [NN] → Tour → [2-opt] → Tour → [SA] → Best Tour → [Cost]

    This is the "Chimera" composition mentioned in user requirements:
        "imagine this project as a chimera, where we can start by using a
        construction heuristic and combining it with a local search heuristic
        if and when possible"

    Key Concepts:
        - Multi-stage composition
        - Each stage refines the solution
        - Metaheuristic accepts initial_tour (composability)
        - Track progress through pipeline
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Full Pipeline - The CHIMERA")
    print("=" * 80)

    backend_name = "CuPy (GPU)" if xp.__name__ == "cupy" else "NumPy (CPU)"
    print(f"Backend: {backend_name}")
    print(f"Problem: {problem.name} ({problem.dimension} nodes)")
    print()
    print("Pipeline: NN → 2-opt → Simulated Annealing")
    print()

    costs = []
    times = []

    # Stage 1: Construction
    print("Stage 1: Construction (Nearest Neighbor)")
    start = time.time()
    tour = nearest_neighbor(problem, start_node=0, xp=xp)
    t1 = time.time() - start
    c1 = compute_tour_cost(problem, tour, xp=xp)
    print(f"  ✓ Cost: {c1:.2f} (time: {t1:.4f}s)")
    costs.append(c1)
    times.append(t1)
    print()

    # Stage 2: Improvement
    print("Stage 2: Improvement (2-opt First-Improvement)")
    start = time.time()
    tour = two_opt_first_improvement(problem, tour, xp=xp)
    t2 = time.time() - start
    c2 = compute_tour_cost(problem, tour, xp=xp)
    improvement_2opt = (c1 - c2) / c1 * 100
    print(f"  ✓ Cost: {c2:.2f} (time: {t2:.4f}s)")
    print(f"  ✓ Improvement from Stage 1: {improvement_2opt:.2f}%")
    costs.append(c2)
    times.append(t2)
    print()

    # Stage 3: Metaheuristic
    print("Stage 3: Metaheuristic (Simulated Annealing)")
    start = time.time()
    tour = simulated_annealing(
        problem, tour, temp=1000, cooling=0.95, max_iter=1000, xp=xp
    )
    t3 = time.time() - start
    c3 = compute_tour_cost(problem, tour, xp=xp)
    improvement_sa = (c2 - c3) / c2 * 100
    print(f"  ✓ Cost: {c3:.2f} (time: {t3:.4f}s)")
    print(f"  ✓ Improvement from Stage 2: {improvement_sa:.2f}%")
    costs.append(c3)
    times.append(t3)
    print()

    # Summary
    total_improvement = (c1 - c3) / c1 * 100
    total_time = sum(times)

    print("=" * 80)
    print("CHIMERA SUMMARY")
    print("=" * 80)
    print(f"{'Stage':<20} {'Cost':>12} {'Time (s)':>12} {'Improvement':>15}")
    print("-" * 80)
    print(f"{'1. NN':<20} {c1:>12.2f} {t1:>12.4f} {'-':>15}")
    print(f"{'2. NN + 2-opt':<20} {c2:>12.2f} {t2:>12.4f} {improvement_2opt:>14.2f}%")
    print(
        f"{'3. NN + 2-opt + SA':<20} {c3:>12.2f} {t3:>12.4f} {improvement_sa:>14.2f}%"
    )
    print("-" * 80)
    print(f"{'TOTAL':<20} {c3:>12.2f} {total_time:>12.4f} {total_improvement:>14.2f}%")
    print("=" * 80)
    print()

    return {
        "final_tour": tour,
        "costs": costs,
        "times": times,
        "total_improvement": total_improvement,
        "total_time": total_time,
    }


# ============================================================================
# EXAMPLE 4: Multi-Start Optimization
# ============================================================================


def example_multi_start(problem: Problem, num_starts: int = 5, xp=np):
    """
    Demonstrate parallel pipeline pattern: run multiple independent pipelines.

    Pattern:
        For each start_node in [0, 1, 2, ..., num_starts-1]:
            tour = NN(start_node) → 2-opt → SA
        Return best tour across all starts

    Key Concepts:
        - Exploration vs exploitation tradeoff
        - Different starting points may find different local optima
        - Embarrassingly parallel (each pipeline independent)
        - Best-of-N selection
    """
    print("\n" + "=" * 80)
    print(f"EXAMPLE 4: Multi-Start Optimization ({num_starts} starts)")
    print("=" * 80)

    backend_name = "CuPy (GPU)" if xp.__name__ == "cupy" else "NumPy (CPU)"
    print(f"Backend: {backend_name}")
    print(f"Problem: {problem.name} ({problem.dimension} nodes)")
    print()

    results = []

    for start_node in range(min(num_starts, problem.dimension)):
        print(f"Start {start_node + 1}/{num_starts} (initial node: {start_node})")

        # Pipeline: NN → 2-opt → SA
        tour = nearest_neighbor(problem, start_node=start_node, xp=xp)
        tour = two_opt_first_improvement(problem, tour, xp=xp)
        tour = simulated_annealing(
            problem, tour, temp=1000, cooling=0.95, max_iter=500, xp=xp
        )

        cost = compute_tour_cost(problem, tour, xp=xp)
        results.append({"start_node": start_node, "tour": tour, "cost": cost})

        print(f"  ✓ Cost: {cost:.2f}")

    print()

    # Select best
    best_result = min(results, key=lambda r: r["cost"])
    worst_result = max(results, key=lambda r: r["cost"])
    avg_cost = np.mean([r["cost"] for r in results])

    print("=" * 80)
    print("MULTI-START SUMMARY")
    print("=" * 80)
    print(
        f"Best cost:  {best_result['cost']:.2f} (start node {best_result['start_node']})"
    )
    print(
        f"Worst cost: {worst_result['cost']:.2f} (start node {worst_result['start_node']})"
    )
    print(f"Avg cost:   {avg_cost:.2f}")
    print(f"Spread:     {worst_result['cost'] - best_result['cost']:.2f}")
    print("=" * 80)
    print()

    return {
        "best_tour": best_result["tour"],
        "best_cost": best_result["cost"],
        "best_start": best_result["start_node"],
        "all_results": results,
    }


# ============================================================================
# EXAMPLE 5: CPU vs GPU Backend Comparison
# ============================================================================


def example_cpu_vs_gpu_benchmark(problem: Problem):
    """
    Demonstrate backend abstraction: same code runs on CPU or GPU.

    Measures:
        - Execution time for CPU (NumPy)
        - Execution time for GPU (CuPy) including transfer overhead
        - Speedup factor
        - Correctness verification (CPU and GPU produce same cost)

    Key Concepts:
        - Backend parameter (xp=np vs xp=cp)
        - Zero code changes between backends
        - GPU benefits scale with problem size
        - Transfer overhead matters for small problems
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: CPU vs GPU Backend Comparison")
    print("=" * 80)

    if not CUPY_AVAILABLE:
        print("⚠️  CuPy not available - skipping GPU benchmark")
        print("Install CuPy with: uv add cupy-cuda12x")
        return None

    print(f"Problem: {problem.name} ({problem.dimension} nodes)")
    print()

    # CPU execution
    print("CPU Execution (NumPy):")
    start = time.time()
    tour_cpu = nearest_neighbor(problem, xp=np)
    tour_cpu = two_opt_first_improvement(problem, tour_cpu, xp=np)
    cpu_time = time.time() - start
    cost_cpu = compute_tour_cost(problem, tour_cpu, xp=np)
    print(f"  ✓ Time: {cpu_time:.4f}s")
    print(f"  ✓ Cost: {cost_cpu:.2f}")
    print()

    # GPU execution (with transfer time)
    print("GPU Execution (CuPy):")
    start = time.time()
    tour_gpu = nearest_neighbor(problem, xp=cp)
    tour_gpu = two_opt_first_improvement(problem, tour_gpu, xp=cp)
    cp.cuda.Stream.null.synchronize()  # Ensure GPU operations complete
    gpu_time = time.time() - start
    cost_gpu = compute_tour_cost(problem, tour_gpu, xp=cp)
    print(f"  ✓ Time: {gpu_time:.4f}s")
    print(f"  ✓ Cost: {cost_gpu:.2f}")
    print()

    # Analysis
    speedup = cpu_time / gpu_time
    cost_diff = abs(cost_cpu - cost_gpu)

    print("=" * 80)
    print("BENCHMARK SUMMARY")
    print("=" * 80)
    print(f"CPU Time:    {cpu_time:.4f}s")
    print(f"GPU Time:    {gpu_time:.4f}s")
    print(f"Speedup:     {speedup:.2f}x")
    print(f"Cost Match:  {cost_diff < 1e-6} (diff: {cost_diff:.6f})")
    print("=" * 80)
    print()

    if speedup < 1.0:
        print("⚠️  GPU slower than CPU - this is normal for small problems!")
        print("    GPU shines with larger instances (n > 1000)")
        print()

    return {
        "cpu_time": cpu_time,
        "gpu_time": gpu_time,
        "speedup": speedup,
        "cost_cpu": cost_cpu,
        "cost_gpu": cost_gpu,
        "cost_match": cost_diff < 1e-6,
    }


# ============================================================================
# EXAMPLE 6: Algorithm Comparison Study
# ============================================================================


def example_algorithm_comparison(problem: Problem, xp=np):
    """
    Demonstrate Strategy pattern: compare multiple construction heuristics.

    Compares:
        - Nearest Neighbor
        - Random Tour (when implemented)
        - Greedy Insertion (when implemented)

    Key Concepts:
        - Algorithms are interchangeable (same signature)
        - Higher-order function accepts algorithm as parameter
        - Enables systematic comparison studies
        - Foundation for academic experiments
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Algorithm Comparison Study")
    print("=" * 80)

    backend_name = "CuPy (GPU)" if xp.__name__ == "cupy" else "NumPy (CPU)"
    print(f"Backend: {backend_name}")
    print(f"Problem: {problem.name} ({problem.dimension} nodes)")
    print()

    # Define algorithms to compare
    algorithms = {
        "Nearest Neighbor": nearest_neighbor,
        # 'Random Tour': random_tour,  # Not yet implemented
        # 'Greedy Insertion': greedy_insertion,  # Not yet implemented
    }

    results = []

    for name, algorithm in algorithms.items():
        print(f"Testing: {name}")
        start = time.time()
        tour = algorithm(problem, xp=xp)
        exec_time = time.time() - start
        cost = compute_tour_cost(problem, tour, xp=xp)

        results.append({"algorithm": name, "cost": cost, "time": exec_time})

        print(f"  ✓ Cost: {cost:.2f} (time: {exec_time:.4f}s)")

    print()

    # Sort by cost
    results_sorted = sorted(results, key=lambda r: r["cost"])
    best = results_sorted[0]

    print("=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print(f"{'Algorithm':<25} {'Cost':>12} {'Time (s)':>12} {'Gap to Best':>15}")
    print("-" * 80)

    for r in results_sorted:
        gap = (r["cost"] - best["cost"]) / best["cost"] * 100 if best["cost"] > 0 else 0
        gap_str = f"{gap:.2f}%" if gap > 0 else "BEST"
        print(
            f"{r['algorithm']:<25} {r['cost']:>12.2f} {r['time']:>12.4f} {gap_str:>15}"
        )

    print("=" * 80)
    print()

    return {
        "results": results,
        "best_algorithm": best["algorithm"],
        "best_cost": best["cost"],
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Algorithm Composition Examples - Runnable Demonstrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all examples
  uv run scripts/algorithm_composition_examples.py
  
  # Run specific example
  uv run scripts/algorithm_composition_examples.py --example simple_pipeline
  
  # Use GPU backend
  uv run scripts/algorithm_composition_examples.py --backend cupy --example cpu_vs_gpu
  
  # Specify custom problem
  uv run scripts/algorithm_composition_examples.py --problem eil51
        """,
    )

    parser.add_argument(
        "--example",
        type=str,
        choices=[
            "simple_pipeline",
            "improvement_pipeline",
            "full_pipeline",
            "multi_start",
            "cpu_vs_gpu",
            "algorithm_comparison",
            "all",
        ],
        default="all",
        help="Which example to run (default: all)",
    )

    parser.add_argument(
        "--backend",
        type=str,
        choices=["numpy", "cupy"],
        default="numpy",
        help="Backend to use (default: numpy)",
    )

    parser.add_argument(
        "--problem",
        type=str,
        default="berlin52",
        help="Problem instance to load (default: berlin52)",
    )

    args = parser.parse_args()

    # Setup backend
    if args.backend == "cupy":
        if not CUPY_AVAILABLE:
            print("ERROR: CuPy not available")
            print("Install with: uv add cupy-cuda12x")
            return 1
        xp = cp
    else:
        xp = np

    # Load problem
    print("=" * 80)
    print("ALGORITHM COMPOSITION EXAMPLES")
    print("=" * 80)
    print(f"Loading problem: {args.problem}")

    try:
        with DatabaseLoader() as loader:
            problem = loader.load(args.problem)
    except Exception as e:
        print(f"ERROR: Failed to load problem '{args.problem}'")
        print(f"       {e}")
        return 1

    print(f"✓ Loaded: {problem.name} ({problem.dimension} nodes)")
    print()

    # Run examples
    examples = {
        "simple_pipeline": lambda: example_simple_pipeline(problem, xp),
        "improvement_pipeline": lambda: example_improvement_pipeline(problem, xp),
        "full_pipeline": lambda: example_full_pipeline_chimera(problem, xp),
        "multi_start": lambda: example_multi_start(problem, num_starts=5, xp=xp),
        "cpu_vs_gpu": lambda: example_cpu_vs_gpu_benchmark(problem),
        "algorithm_comparison": lambda: example_algorithm_comparison(problem, xp),
    }

    if args.example == "all":
        # Run all examples
        for name, example_fn in examples.items():
            try:
                example_fn()
            except Exception as e:
                print(f"⚠️  Example '{name}' failed: {e}")
                print()
    else:
        # Run specific example
        try:
            examples[args.example]()
        except Exception as e:
            print(f"ERROR: Example failed: {e}")
            import traceback

            traceback.print_exc()
            return 1

    print("=" * 80)
    print("ALL EXAMPLES COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print(
        "  1. Review architecture: documentation/developer_guides/algorithm_composition_architecture.md"
    )
    print("  2. Implement GPU-8: two_opt_first_improvement")
    print("  3. Implement GPU-9: two_opt_best_improvement")
    print("  4. Implement GPU-12: simulated_annealing")
    print("  5. Re-run these examples to see full pipelines in action!")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
