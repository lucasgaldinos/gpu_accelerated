#!/usr/bin/env python3
"""Chapter 4 Validation: ISO-Algorithmic GA Benchmark with TSPLIB Instances.

This benchmark validates the memory transfer optimization claims in Chapter 4
by comparing 4 ISO-algorithmic GA variants on real TSPLIB instances.

Academic Requirements (first_draft.md section 3.5):
    - 30 repetitions per algorithm for statistical significance
    - TSPLIB instances with known optimal solutions
    - Adaptive generation formula: 2 × n × sqrt(n)
    - Statistical validation: Friedman + Nemenyi + pairwise tests
    - Solution quality tracking: gap to optimum
    - Memory transfer measurement: H2D/D2H bytes

Architecture:
    - 3 problem boilerplates (not loops - per user requirement)
    - ONE PROBLEM AT A TIME with memory cleanup
    - GPU-only by default (--skip-cpu flag)
    - Comprehensive metrics: time, quality, transfers, kernels

Author: AI Assistant
Date: 2025-01-28
"""

import argparse
import gc
import time
import numpy as np
import cupy as cp
from pathlib import Path
from typing import Dict, Any, List, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Import ISO-algorithmic variants
from src.algorithms.metaheuristics.genetic_algorithm_cpu import GeneticAlgorithmCPU
from src.algorithms.metaheuristics.genetic_algorithm_hybrid_naive import (
    GeneticAlgorithmHybridNaive,
)
from src.algorithms.metaheuristics.genetic_algorithm_hybrid_optimized import (
    GeneticAlgorithmHybridOptimized,
)
from src.algorithms.metaheuristics.genetic_algorithm_full_gpu_iso import (
    GeneticAlgorithmFullGPU,
)
from src.loaders.database_loader import DatabaseLoader
from src.protocols.problem_context import ProblemContext
from src.benchmarking.statistics import StatisticalAnalyzer


# TSPLIB optimal solutions (from tsplib95_format.md)
OPTIMAL_SOLUTIONS = {
    "kroA100": 21282,
    "lin318": 42029,
    "pr1002": 259045,
}


def adaptive_generations(n: int) -> int:
    """Calculate adaptive generations: 2 × n × sqrt(n)."""
    import math

    return int(2 * n * math.sqrt(n))


def run_single_algorithm(
    algorithm_name: str,
    algorithm_instance,
    problem,
    customers: List[int],
    max_generations: int,
    optimal_cost: float,
    repetitions: int,
    use_gpu: bool,
) -> Dict[str, Any]:
    """Run single algorithm for specified repetitions.

    Args:
        algorithm_name: Name of algorithm variant
        algorithm_instance: Algorithm instance
        problem: Problem to solve
        customers: Customer indices
        max_generations: Number of generations
        optimal_cost: Known optimal solution cost
        repetitions: Number of runs
        use_gpu: Whether to use GPU backend

    Returns:
        Dictionary with aggregated results
    """
    logging.info(f"Running {algorithm_name} for {repetitions} repetitions...")

    results = {
        "times": [],
        "initial_costs": [],
        "final_costs": [],
        "gaps": [],  # Gap to optimal (%)
        "improvements": [],  # Improvement from initial (%)
        "h2d_bytes": [],
        "d2h_bytes": [],
        "kernel_launches": [],
        "best_tours": [],
    }

    for rep in range(repetitions):
        # Create fresh context for each run
        xp = cp if use_gpu else np
        context = ProblemContext(problem, xp=xp)

        # Run algorithm
        start_time = time.perf_counter()
        try:
            tour, stats = algorithm_instance.evolve(
                context, 
                customers, 
                max_generations,
                optimal_cost=optimal_cost,  # Enable early stopping when optimal reached
                patience=50  # Stop if no improvement for 50 generations
            )
            elapsed = time.perf_counter() - start_time

            # Extract metrics
            initial_cost = stats["initial_fitness"]
            final_cost = stats["best_fitness"]
            gap = (final_cost - optimal_cost) / optimal_cost * 100
            improvement = (initial_cost - final_cost) / initial_cost * 100

            results["times"].append(elapsed)
            results["initial_costs"].append(initial_cost)
            results["final_costs"].append(final_cost)
            results["gaps"].append(gap)
            results["improvements"].append(improvement)
            results["h2d_bytes"].append(stats.get("h2d_bytes", 0))
            results["d2h_bytes"].append(stats.get("d2h_bytes", 0))
            results["kernel_launches"].append(stats.get("kernel_launches", 0))
            results["best_tours"].append(tour)

            if (rep + 1) % 5 == 0:
                logging.info(
                    f"  Rep {rep + 1}/{repetitions}: "
                    f"cost={final_cost:.2f}, gap={gap:.2f}%, time={elapsed:.2f}s"
                )

        except Exception as e:
            logging.error(f"  Rep {rep + 1} FAILED: {e}")
            import traceback

            traceback.print_exc()
            # Fill with NaN for failed runs
            results["times"].append(np.nan)
            results["final_costs"].append(np.nan)
            results["gaps"].append(np.nan)

    # Calculate statistics
    times = np.array(results["times"])
    final_costs = np.array(results["final_costs"])
    gaps = np.array(results["gaps"])
    improvements = np.array(results["improvements"])
    h2d = np.array(results["h2d_bytes"])
    d2h = np.array(results["d2h_bytes"])

    # Remove NaN values for statistics
    valid_mask = ~np.isnan(times)

    summary = {
        "algorithm": algorithm_name,
        "repetitions": repetitions,
        "successful_runs": np.sum(valid_mask),
        # Time statistics
        "mean_time": np.nanmean(times),
        "std_time": np.nanstd(times),
        "min_time": np.nanmin(times),
        "max_time": np.nanmax(times),
        # Solution quality
        "mean_cost": np.nanmean(final_costs),
        "std_cost": np.nanstd(final_costs),
        "best_cost": np.nanmin(final_costs),
        "worst_cost": np.nanmax(final_costs),
        # Gap to optimal
        "mean_gap": np.nanmean(gaps),
        "std_gap": np.nanstd(gaps),
        "best_gap": np.nanmin(gaps),
        # Improvement from initial
        "mean_improvement": np.nanmean(improvements),
        # Memory transfers
        "mean_h2d_mb": np.nanmean(h2d) / 1e6,
        "mean_d2h_mb": np.nanmean(d2h) / 1e6,
        "total_transfer_mb": (np.nanmean(h2d) + np.nanmean(d2h)) / 1e6,
        # Kernel launches
        "mean_kernels": np.nanmean(results["kernel_launches"]),
        # Raw data for statistical tests
        "raw_times": times[valid_mask],
        "raw_costs": final_costs[valid_mask],
        "raw_gaps": gaps[valid_mask],
    }

    logging.info(
        f"{algorithm_name} completed: "
        f"mean_cost={summary['mean_cost']:.2f}±{summary['std_cost']:.2f}, "
        f"mean_gap={summary['mean_gap']:.2f}%, "
        f"mean_time={summary['mean_time']:.2f}s"
    )

    return summary


def perform_statistical_analysis(
    instance_name: str,
    results: Dict[str, Dict[str, Any]],
    optimal_cost: float,
):
    """Perform statistical analysis on results.

    Args:
        instance_name: Name of TSPLIB instance
        results: Dictionary of algorithm results
        optimal_cost: Known optimal solution
    """
    logging.info(f"\nStatistical Analysis for {instance_name}")
    logging.info("=" * 80)

    analyzer = StatisticalAnalyzer()

    # Extract cost data for each algorithm
    algorithm_names = list(results.keys())
    cost_data = [results[name]["raw_costs"] for name in algorithm_names]

    # Friedman test (non-parametric ANOVA for repeated measures)
    if len(algorithm_names) >= 3:
        friedman_result = analyzer.friedman_test(cost_data)

        logging.info(f"\nFriedman Test (k={len(algorithm_names)} algorithms):")
        logging.info(f"  Statistic: {friedman_result['statistic']:.4f}")
        logging.info(f"  p-value: {friedman_result['p_value']:.6f}")
        logging.info(f"  Significant: {friedman_result['is_significant']}")

        # Nemenyi post-hoc if significant
        if friedman_result["post_hoc_required"]:
            logging.info("\n  Performing Nemenyi post-hoc test...")
            nemenyi_result = analyzer.nemenyi_posthoc(cost_data, algorithm_names)

            logging.info(
                f"  Critical distance: {nemenyi_result['critical_distance']:.4f}"
            )
            logging.info("  Mean ranks:")
            for name, rank in nemenyi_result["mean_ranks"].items():
                logging.info(f"    {name}: {rank:.2f}")

            logging.info("\n  Pairwise comparisons:")
            for comp in nemenyi_result["pairwise_comparisons"]:
                logging.info(
                    f"    {comp['algorithm1']} vs {comp['algorithm2']}: "
                    f"rank_diff={comp['rank_difference']:.2f}, "
                    f"significant={comp['significant']}"
                )

    # Pairwise comparisons (parametric)
    logging.info("\nPairwise t-tests (with Holm-Bonferroni correction):")
    for i, name1 in enumerate(algorithm_names):
        for name2 in algorithm_names[i + 1 :]:
            comparison = analyzer.paired_comparison(
                results[name1]["raw_costs"],
                results[name2]["raw_costs"],
                name1,
                name2,
            )

            logging.info(f"  {name1} vs {name2}:")
            logging.info(f"    Mean diff: {comparison['mean_difference']:.2f}")
            logging.info(f"    t-statistic: {comparison['t_statistic']:.4f}")
            logging.info(f"    p-value: {comparison['p_value']:.6f}")
            logging.info(f"    Significant: {comparison['is_significant']}")
            logging.info(f"    Cohen's d: {comparison['cohens_d']:.4f}")

    # Summary table
    logging.info("\n" + "=" * 80)
    logging.info(f"SUMMARY: {instance_name} (optimal={optimal_cost})")
    logging.info("=" * 80)
    print(
        f"\n{'Algorithm':<20} {'Mean Cost':<15} {'Gap (%)':<12} {'Time (s)':<12} {'H2D (MB)':<12} {'D2H (MB)':<12}"
    )
    print("-" * 95)
    for name in algorithm_names:
        r = results[name]
        print(
            f"{name:<20} "
            f"{r['mean_cost']:<15.2f} "
            f"{r['mean_gap']:<12.2f} "
            f"{r['mean_time']:<12.2f} "
            f"{r['mean_h2d_mb']:<12.2f} "
            f"{r['mean_d2h_mb']:<12.2f}"
        )
    print()


def benchmark_kroa100(args) -> Dict[str, Any]:
    """BOILERPLATE 1: Benchmark on kroA100 (n=100)."""
    instance_name = "kroA100"
    optimal_cost = OPTIMAL_SOLUTIONS[instance_name]

    logging.info("\n" + "=" * 80)
    logging.info(f"BENCHMARK 1: {instance_name}")
    logging.info("=" * 80)

    # Load problem
    db_path = Path(__file__).parent.parent / "datasets" / "routing.duckdb"
    with DatabaseLoader(str(db_path)) as loader:
        problem = loader.load(instance_name)

    n = problem.dimension
    max_generations = adaptive_generations(n)
    customers = list(range(n))

    logging.info(f"Problem: {instance_name}")
    logging.info(f"Dimension: {n} cities")
    logging.info(f"Optimal: {optimal_cost}")
    logging.info(f"Generations: {max_generations}")
    logging.info(f"Repetitions: {args.repetitions}")
    logging.info("")

    # ISO-algorithmic parameters (SAME for all)
    params = {
        "population_size": 256,
        "mutation_rate": 0.02,
        "tournament_size": 5,
        "two_opt_iterations": 10,
        "seed": 42,
    }

    results = {}

    # Run CPU variant (if not skipped)
    if not args.skip_cpu:
        ga_cpu = GeneticAlgorithmCPU(**params)
        results["CPU"] = run_single_algorithm(
            "CPU",
            ga_cpu,
            problem,
            customers,
            max_generations,
            optimal_cost,
            args.repetitions,
            use_gpu=False,
        )
        gc.collect()

    # Run GPU variants
    ga_naive = GeneticAlgorithmHybridNaive(**params)
    results["HybridNaive"] = run_single_algorithm(
        "HybridNaive",
        ga_naive,
        problem,
        customers,
        max_generations,
        optimal_cost,
        args.repetitions,
        use_gpu=True,
    )
    gc.collect()
    cp.get_default_memory_pool().free_all_blocks()

    ga_optimized = GeneticAlgorithmHybridOptimized(**params)
    results["HybridOptimized"] = run_single_algorithm(
        "HybridOptimized",
        ga_optimized,
        problem,
        customers,
        max_generations,
        optimal_cost,
        args.repetitions,
        use_gpu=True,
    )
    gc.collect()
    cp.get_default_memory_pool().free_all_blocks()

    ga_full_gpu = GeneticAlgorithmFullGPU(**params)
    results["FullGPU"] = run_single_algorithm(
        "FullGPU",
        ga_full_gpu,
        problem,
        customers,
        max_generations,
        optimal_cost,
        args.repetitions,
        use_gpu=True,
    )
    gc.collect()
    cp.get_default_memory_pool().free_all_blocks()

    # Statistical analysis
    perform_statistical_analysis(instance_name, results, optimal_cost)

    # Cleanup
    del problem, ga_naive, ga_optimized, ga_full_gpu
    if not args.skip_cpu:
        del ga_cpu
    gc.collect()

    return results


def benchmark_lin318(args) -> Dict[str, Any]:
    """BOILERPLATE 2: Benchmark on lin318 (n=318)."""
    instance_name = "lin318"
    optimal_cost = OPTIMAL_SOLUTIONS[instance_name]

    logging.info("\n" + "=" * 80)
    logging.info(f"BENCHMARK 2: {instance_name}")
    logging.info("=" * 80)

    # Load problem
    db_path = Path(__file__).parent.parent / "datasets" / "routing.duckdb"
    with DatabaseLoader(str(db_path)) as loader:
        problem = loader.load(instance_name)

    n = problem.dimension
    max_generations = adaptive_generations(n)
    customers = list(range(n))

    logging.info(f"Problem: {instance_name}")
    logging.info(f"Dimension: {n} cities")
    logging.info(f"Optimal: {optimal_cost}")
    logging.info(f"Generations: {max_generations}")
    logging.info(f"Repetitions: {args.repetitions}")
    logging.info("")

    params = {
        "population_size": 256,
        "mutation_rate": 0.02,
        "tournament_size": 5,
        "two_opt_iterations": 10,
        "seed": 42,
    }

    results = {}

    if not args.skip_cpu:
        ga_cpu = GeneticAlgorithmCPU(**params)
        results["CPU"] = run_single_algorithm(
            "CPU",
            ga_cpu,
            problem,
            customers,
            max_generations,
            optimal_cost,
            args.repetitions,
            use_gpu=False,
        )
        gc.collect()

    ga_naive = GeneticAlgorithmHybridNaive(**params)
    results["HybridNaive"] = run_single_algorithm(
        "HybridNaive",
        ga_naive,
        problem,
        customers,
        max_generations,
        optimal_cost,
        args.repetitions,
        use_gpu=True,
    )
    gc.collect()
    cp.get_default_memory_pool().free_all_blocks()

    ga_optimized = GeneticAlgorithmHybridOptimized(**params)
    results["HybridOptimized"] = run_single_algorithm(
        "HybridOptimized",
        ga_optimized,
        problem,
        customers,
        max_generations,
        optimal_cost,
        args.repetitions,
        use_gpu=True,
    )
    gc.collect()
    cp.get_default_memory_pool().free_all_blocks()

    ga_full_gpu = GeneticAlgorithmFullGPU(**params)
    results["FullGPU"] = run_single_algorithm(
        "FullGPU",
        ga_full_gpu,
        problem,
        customers,
        max_generations,
        optimal_cost,
        args.repetitions,
        use_gpu=True,
    )
    gc.collect()
    cp.get_default_memory_pool().free_all_blocks()

    perform_statistical_analysis(instance_name, results, optimal_cost)

    del problem, ga_naive, ga_optimized, ga_full_gpu
    if not args.skip_cpu:
        del ga_cpu
    gc.collect()

    return results


def benchmark_pr1002(args) -> Dict[str, Any]:
    """BOILERPLATE 3: Benchmark on pr1002 (n=1002)."""
    instance_name = "pr1002"
    optimal_cost = OPTIMAL_SOLUTIONS[instance_name]

    logging.info("\n" + "=" * 80)
    logging.info(f"BENCHMARK 3: {instance_name}")
    logging.info("=" * 80)

    # Load problem
    db_path = Path(__file__).parent.parent / "datasets" / "routing.duckdb"
    with DatabaseLoader(str(db_path)) as loader:
        problem = loader.load(instance_name)

    n = problem.dimension
    max_generations = adaptive_generations(n)
    customers = list(range(n))

    logging.info(f"Problem: {instance_name}")
    logging.info(f"Dimension: {n} cities")
    logging.info(f"Optimal: {optimal_cost}")
    logging.info(f"Generations: {max_generations}")
    logging.info(f"Repetitions: {args.repetitions}")
    logging.info("")

    params = {
        "population_size": 256,
        "mutation_rate": 0.02,
        "tournament_size": 5,
        "two_opt_iterations": 10,
        "seed": 42,
    }

    results = {}

    if not args.skip_cpu:
        ga_cpu = GeneticAlgorithmCPU(**params)
        results["CPU"] = run_single_algorithm(
            "CPU",
            ga_cpu,
            problem,
            customers,
            max_generations,
            optimal_cost,
            args.repetitions,
            use_gpu=False,
        )
        gc.collect()

    ga_naive = GeneticAlgorithmHybridNaive(**params)
    results["HybridNaive"] = run_single_algorithm(
        "HybridNaive",
        ga_naive,
        problem,
        customers,
        max_generations,
        optimal_cost,
        args.repetitions,
        use_gpu=True,
    )
    gc.collect()
    cp.get_default_memory_pool().free_all_blocks()

    ga_optimized = GeneticAlgorithmHybridOptimized(**params)
    results["HybridOptimized"] = run_single_algorithm(
        "HybridOptimized",
        ga_optimized,
        problem,
        customers,
        max_generations,
        optimal_cost,
        args.repetitions,
        use_gpu=True,
    )
    gc.collect()
    cp.get_default_memory_pool().free_all_blocks()

    ga_full_gpu = GeneticAlgorithmFullGPU(**params)
    results["FullGPU"] = run_single_algorithm(
        "FullGPU",
        ga_full_gpu,
        problem,
        customers,
        max_generations,
        optimal_cost,
        args.repetitions,
        use_gpu=True,
    )
    gc.collect()
    cp.get_default_memory_pool().free_all_blocks()

    perform_statistical_analysis(instance_name, results, optimal_cost)

    del problem, ga_naive, ga_optimized, ga_full_gpu
    if not args.skip_cpu:
        del ga_cpu
    gc.collect()

    return results


def cross_instance_analysis(all_results: Dict[str, Dict[str, Dict[str, Any]]]):
    """Perform cross-instance Friedman analysis."""
    logging.info("\n" + "=" * 80)
    logging.info("CROSS-INSTANCE ANALYSIS")
    logging.info("=" * 80)

    analyzer = StatisticalAnalyzer()

    instance_names = list(all_results.keys())
    algorithm_names = list(all_results[instance_names[0]].keys())

    logging.info(f"Instances: {instance_names}")
    logging.info(f"Algorithms: {algorithm_names}")
    logging.info("")

    for algorithm in algorithm_names:
        gaps = []
        for instance in instance_names:
            gaps.extend(all_results[instance][algorithm]["raw_gaps"])

        logging.info(
            f"{algorithm}: mean_gap={np.mean(gaps):.2f}%, std_gap={np.std(gaps):.2f}%"
        )

    logging.info("\nFriedman test across all instances:")
    algorithm_gap_data = []
    for algorithm in algorithm_names:
        instance_gaps = []
        for instance in instance_names:
            mean_gap = all_results[instance][algorithm]["mean_gap"]
            instance_gaps.append(mean_gap)
        algorithm_gap_data.append(np.array(instance_gaps))

    if len(algorithm_names) >= 3:
        friedman_result = analyzer.friedman_test(algorithm_gap_data)

        logging.info(f"  Statistic: {friedman_result['statistic']:.4f}")
        logging.info(f"  p-value: {friedman_result['p_value']:.6f}")
        logging.info(f"  Significant: {friedman_result['is_significant']}")


def main():
    """Main benchmark execution."""
    parser = argparse.ArgumentParser(
        description="Chapter 4 Validation: ISO-Algorithmic GA Benchmark"
    )
    parser.add_argument(
        "--skip-cpu",
        action="store_true",
        default=True,
        help="Skip CPU variant (default: True)",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=30,
        help="Number of repetitions per algorithm (default: 30)",
    )
    parser.add_argument(
        "--instances",
        nargs="+",
        choices=["kroA100", "lin318", "pr1002"],
        default=["kroA100", "lin318", "pr1002"],
        help="TSPLIB instances to benchmark (default: all 3)",
    )

    args = parser.parse_args()

    logging.info("=" * 80)
    logging.info("CHAPTER 4 VALIDATION: ISO-ALGORITHMIC GA BENCHMARK")
    logging.info("=" * 80)
    logging.info(f"Configuration:")
    logging.info(f"  Skip CPU: {args.skip_cpu}")
    logging.info(f"  Repetitions: {args.repetitions}")
    logging.info(f"  Instances: {args.instances}")
    logging.info("")

    all_results = {}

    # Run benchmarks (THREE SEPARATE BOILERPLATES)
    if "kroA100" in args.instances:
        all_results["kroA100"] = benchmark_kroa100(args)

    if "lin318" in args.instances:
        all_results["lin318"] = benchmark_lin318(args)

    if "pr1002" in args.instances:
        all_results["pr1002"] = benchmark_pr1002(args)

    # Cross-instance analysis
    if len(all_results) > 1:
        cross_instance_analysis(all_results)

    logging.info("\n" + "=" * 80)
    logging.info("BENCHMARK COMPLETE")
    logging.info("=" * 80)


if __name__ == "__main__":
    main()
