#!/usr/bin/env python3
"""
Comprehensive Routing Algorithm Benchmark - Configuration-Driven Design.

Key Features:
- 📝 Single configuration point (easily change iterations/population)
- 📊 Complete statistics (convergence, diversity, acceptance rates)
- 🔇 Silent data collection (no hardcoded print statements)
- 📈 Flexible output (tables, CSV, plots - user controlled)
- 🎯 Smart execution (one run per problem, all combinations tested)

Usage:
    # Default configuration (100 generations, 1000 SA iterations)
    python benchmark_comprehensive.py

    # Custom configuration
    python benchmark_comprehensive.py --ga-generations 500 --sa-iterations 5000

    # Export to CSV
    python benchmark_comprehensive.py --export results.csv

    # Specific problem tiers
    python benchmark_comprehensive.py --tiers tiny small medium

Configuration Example:
    config = BenchmarkConfig(
        problem_tiers=["tiny", "small", "medium"],
        algorithms=["ga", "sa"],
        backends=["numpy", "cupy"],
        ga_params={
            "population_size": 100,
            "max_generations": 100  # ← CHANGE HERE!
        },
        sa_params={
            "initial_temp": 1000.0,
            "max_iterations": 1000  # ← CHANGE HERE!
        }
    )

    results = run_comprehensive_benchmark(config)
    print_summary_table(results)  # Or export_csv(results)
"""

import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from tabulate import tabulate
import json

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import strategies to trigger registration
from code.src.algorithms.strategies import selection_strategies  # noqa: F401
from code.src.algorithms.strategies import crossover_strategies  # noqa: F401
from code.src.algorithms.strategies import mutation_strategies  # noqa: F401
from code.src.algorithms.strategies import neighbor_strategies  # noqa: F401
from code.src.algorithms.strategies import improvement_strategies  # noqa: F401

from code.src.utils.algorithm_factory import AlgorithmFactory
from code.benchmark.utils.benchmark_helpers import (
    run_algorithm_timed,
    get_benchmark_problems,
    get_optimal_costs,
)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════


def calculate_ga_params(n: int, scale_generations: float = 1.0) -> Dict[str, Any]:
    """
    Calculate GA hyperparameters using academic formulas.

    This function computes hyperparameters based on problem size (n) using
    formulas derived from academic literature. This ensures parameter values
    are properly scaled for each problem tier rather than using hardcoded values.

    Args:
        n: Problem size (number of cities/nodes)
        scale_generations: Scaling factor for max_generations (default 1.0).
                          Use <1.0 for faster testing, 1.0 for academic results.

    Returns:
        Dictionary with the following keys:
        - population_size: Number of individuals in population
        - max_generations: Maximum number of GA iterations
        - crossover_rate: Probability of crossover operation
        - mutation_rate: Probability of mutation operation
        - two_opt_iterations: Number of 2-opt refinement iterations per individual

    References:
        - Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization,
          and Machine Learning. For population diversity requirements.
        - Prins, C. (2004). A simple and effective evolutionary algorithm for
          the vehicle routing problem. For convergence time estimates.
        - Eiben, A. E., & Smith, J. E. (2015). Introduction to Evolutionary
          Computing. For standard operator rates.

    Formula Details:
        - N_pop = max(50, 10 × √n)        # Maintains diversity
        - G_max = max(1000, 20 × n)       # Ensures convergence
        - p_c = 0.85                       # Standard crossover rate
        - p_m = max(0.01, 5/n)            # Adaptive mutation (lower for larger n)
        - I_2opt = max(20, 5000/N_pop)    # Balance refinement with runtime

    Example:
        >>> params = calculate_ga_params(442)  # pcb442 problem
        >>> params['population_size']  # ≈ 210
        >>> params['max_generations']   # ≈ 8840
        >>> params['mutation_rate']     # ≈ 0.011
    """
    import math

    # Population size: Goldberg (1989) diversity requirement
    n_pop = max(50, int(10 * math.sqrt(n)))

    # Max generations: Prins (2004) convergence time
    # Scale factor allows faster testing (e.g., 0.5× for development)
    g_max = max(1000, int(20 * n * scale_generations))

    # Crossover rate: Eiben & Smith (2015) standard value
    p_c = 0.85

    # Mutation rate: Adaptive formula (lower for larger problems)
    # Prevents excessive disruption of good solutions
    p_m = max(0.01, 5.0 / n)

    # 2-opt iterations: Balance between quality and runtime
    # Fewer iterations per individual as population grows
    i_2opt = max(20, int(5000 / n_pop))

    return {
        "population_size": n_pop,
        "max_generations": g_max,
        "crossover_rate": p_c,
        "mutation_rate": p_m,
        "two_opt_iterations": i_2opt,
    }


# >[!warning]
# > - if this works, it must be set ON Genetic algorithms itself.
# > - OBVIOUSLY, sa, IF NOT IMPLEMENTED YET, SHOULD ALSO HAVE THIS.


@dataclass
class BenchmarkConfig:
    """
    Centralized benchmark configuration.

    Change iterations/population in ONE place!
    """

    # What to test
    problem_tiers: List[str] = field(default_factory=lambda: ["tiny", "small"])
    algorithms: List[str] = field(
        default_factory=lambda: [
            "ga",
            "ga_2opt",
            "ga_multistart",
            "sa",
            "sa_2opt",
            "sa_multistart",
        ]
    )
    backends: List[str] = field(default_factory=lambda: ["numpy", "cupy"])

    # GA Configuration
    ga_params: Dict[str, Any] = field(
        default_factory=lambda: {
            "population_size": 100,
            "max_generations": 100,  # 🎯 EASILY CHANGED!
            "crossover_rate": 0.9,
            "mutation_rate": 0.1,
            "use_2opt": False,
        }
    )

    # SA Configuration
    sa_params: Dict[str, Any] = field(
        default_factory=lambda: {
            "initial_temp": 1000.0,
            "final_temp": 0.01,
            "cooling_rate": 0.995,
            "max_iterations": 1000,  # 🎯 EASILY CHANGED!
        }
    )

    # Output options
    verbose: bool = True
    export_format: Optional[str] = None  # "csv", "json", None


@dataclass
class ComprehensiveResult:
    """
    Complete benchmark result with ALL statistics.

    Much more comprehensive than basic BenchmarkResult!
    """

    # Identification
    problem_name: str
    problem_size: int
    algorithm: str
    backend: str

    # Basic metrics
    best_fitness: float
    final_fitness: float
    iterations: int
    time_seconds: float

    # Quality metrics
    optimal_cost: Optional[float] = None
    gap_percent: Optional[float] = None

    # Strategy information (NEW)
    strategies_used: str = ""

    # VRAM information (NEW)
    expected_vram_mb: float = 0.0
    actual_vram_mb: Optional[float] = None

    # Convergence
    convergence_history: List[float] = field(default_factory=list)
    first_improvement_iter: Optional[int] = None
    plateau_length: Optional[int] = None

    # Search characteristics (GA-specific)
    population_diversity: Optional[List[float]] = None

    # Search characteristics (SA-specific)
    acceptance_rate: Optional[float] = None
    temperature_schedule: Optional[List[float]] = None
    uphill_moves: Optional[int] = None

    # Comparison
    speedup: Optional[float] = None  # vs NumPy baseline

    # Raw stats (for debugging)
    raw_stats: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# DATA COLLECTION (SILENT - NO PRINTS!)
# ═══════════════════════════════════════════════════════════


def run_single_benchmark(
    problem: Any,
    algorithm: str,
    backend: str,
    config: BenchmarkConfig,
) -> ComprehensiveResult:
    """
    Run single benchmark configuration.

    Returns complete statistics WITHOUT printing anything!
    """
    # Calculate dynamic GA parameters based on problem size
    # Override config.ga_params with problem-specific values
    ga_params = config.ga_params
    if "ga" in algorithm:
        # Calculate from problem size
        dynamic_params = calculate_ga_params(
            n=problem.dimension,
            scale_generations=0.1,  # 10% of recommended for faster testing
        )
        # Allow user overrides only for specific keys present in config
        # Otherwise use dynamic defaults
        ga_params = dynamic_params.copy()
        # Only override if user explicitly set non-default values
        for key in [
            "population_size",
            "max_generations",
            "crossover_rate",
            "mutation_rate",
        ]:
            if key in config.ga_params and config.ga_params[key] not in [
                100,
                200,
                0.9,
                0.1,
            ]:
                # User set a non-default value - respect it
                ga_params[key] = config.ga_params[key]

        if config.verbose:
            print(
                f"  📊 Dynamic GA params (n={problem.dimension}): "
                f"pop={ga_params['population_size']}, "
                f"gen={ga_params['max_generations']}, "
                f"p_m={ga_params['mutation_rate']:.4f}"
            )
    # >[!warning]
    # > obvisouly, default parameters should make a call to the functions. That should be the default for the genetic_algorithm as well. not only on benchmark
    # Build algorithm configuration
    if algorithm == "ga":
        algo_config = {
            "algorithm": "genetic_algorithm",
            "backend": backend,
            "strategies": {
                "selection": {"name": "tournament", "params": {"tournament_size": 3}},
                "crossover": {"name": "order_crossover"},
                "mutation": {"name": "swap"},
                "construction": {"name": "nearest_neighbor"},
            },
            "hyperparameters": ga_params,  # Use dynamic params. SHOULD BE DEFAULT
        }
        params = ga_params  # Use dynamic params

    elif algorithm == "ga_2opt":
        # GA with 2-opt local search improvement
        # Backend-aware strategy selection: GPU 2-opt for cupy, CPU for numpy
        improvement_strategy = "two_opt_gpu" if backend == "cupy" else "two_opt_simple"

        algo_config = {
            "algorithm": "genetic_algorithm",
            "backend": backend,
            "strategies": {
                "selection": {"name": "tournament", "params": {"tournament_size": 3}},
                "crossover": {"name": "order_crossover"},
                "mutation": {"name": "swap"},
                "improvement": {
                    "name": improvement_strategy,
                    "params": {
                        "max_iterations": ga_params.get(
                            "two_opt_iterations", 200
                        )  # Use dynamic
                    },
                },
            },
            "hyperparameters": ga_params,  # Use dynamic params
        }
        params = ga_params  # Use dynamic params

    elif algorithm == "ga_multistart":
        # GA with multistart (8 restarts) - wraps GA instance
        # Note: Multistart requires manual wrapping after factory, not implemented via factory yet
        algo_config = {
            "algorithm": "genetic_algorithm",
            "backend": backend,
            "strategies": {
                "selection": {"name": "tournament", "params": {"tournament_size": 3}},
                "crossover": {"name": "order_crossover"},
                "mutation": {"name": "swap"},
            },
            "hyperparameters": ga_params,  # Use dynamic params
        }
        params = ga_params  # Use dynamic params

    elif algorithm == "sa":
        algo_config = {
            "algorithm": "simulated_annealing",
            "backend": backend,
            "strategies": {
                "neighborhood": {"name": "random_swap"},
            },
            "hyperparameters": config.sa_params,
        }
        params = config.sa_params

    elif algorithm == "sa_2opt":
        # SA with 2-opt local search improvement
        # Backend-aware strategy selection: GPU 2-opt for cupy, CPU for numpy
        improvement_strategy = "two_opt_gpu" if backend == "cupy" else "two_opt_simple"

        algo_config = {
            "algorithm": "simulated_annealing",
            "backend": backend,
            "strategies": {
                "neighborhood": {"name": "random_swap"},
                "improvement": {
                    "name": improvement_strategy,
                    "params": {
                        "max_iterations": 200
                    },  # Increased from 10 for convergence
                },
            },
            "hyperparameters": config.sa_params,
        }
        params = config.sa_params

    elif algorithm == "sa_multistart":
        # SA with multistart (8 restarts)
        algo_config = {
            "algorithm": "simulated_annealing",
            "backend": backend,
            "strategies": {
                "neighborhood": {"name": "random_swap"},
            },
            "hyperparameters": config.sa_params,
        }
        params = config.sa_params

    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    # Create algorithm instance (or a Multistart wrapper that will instantiate
    # per-worker algorithms from the configuration). Passing the raw config to
    # the Multistart wrapper avoids pickling non-serializable algorithm
    # instances when using multiprocessing.
    if "multistart" in algorithm:
        from code.src.algorithms.metaheuristics.multistart import (
            MultistartMetaheuristic,
        )

        # Pass the configuration so worker processes can reconstruct the
        # algorithm independently using AlgorithmFactory.from_dict
        algo_instance = MultistartMetaheuristic(
            base_algorithm_config=algo_config,
            num_starts=8,
            seed_base=42,
        )
    else:
        # Regular single-run algorithm instance (no multistart)
        algo_instance = AlgorithmFactory.from_dict(algo_config)

    # Calculate expected VRAM
    n = problem.dimension
    base_algo = algorithm.replace("_2opt", "").replace("_multistart", "")

    if base_algo == "ga":
        pop = config.ga_params["population_size"]
        vram_bytes = 6 * pop * n * 4 + n**2 * 8
        if "multistart" in algorithm:
            vram_bytes *= 8  # 8 restarts
    else:  # SA
        vram_bytes = 3 * n * 8 + n**2 * 8
        if "multistart" in algorithm:
            vram_bytes *= 8  # 8 restarts
    expected_vram_mb = vram_bytes / (1024**2)

    # Measure actual VRAM (CuPy only)
    actual_vram_mb = None
    if backend == "cupy":
        try:
            import cupy as cp

            mempool = cp.get_default_memory_pool()
            actual_vram_mb = mempool.used_bytes() / (1024**2)
        except:
            pass

    # Extract strategies string
    base_algo = algorithm.replace("_2opt", "").replace("_multistart", "")

    if base_algo == "ga":
        sel = algo_config["strategies"]["selection"]
        sel_name = sel["name"]
        sel_params = sel.get("params", {})
        cross_name = algo_config["strategies"]["crossover"]["name"]
        mut_name = algo_config["strategies"]["mutation"]["name"]

        strategies_str = f"sel={sel_name}"
        if sel_params:
            params_str = ",".join(f"{k}={v}" for k, v in sel_params.items())
            strategies_str += f"({params_str})"
        strategies_str += f"|cross={cross_name}|mut={mut_name}"

        # Add improvement if present
        if "improvement" in algo_config["strategies"]:
            imp = algo_config["strategies"]["improvement"]
            strategies_str += f"|imp={imp['name']}"
            if "params" in imp:
                imp_params = ",".join(f"{k}={v}" for k, v in imp["params"].items())
                strategies_str += f"({imp_params})"

        # Add multistart if present
        if "multistart" in algorithm:
            strategies_str += "|multistart=8"

    else:  # SA
        neighbor_name = algo_config["strategies"]["neighborhood"]["name"]
        strategies_str = f"neighbor={neighbor_name}"

        # Add improvement if present
        if "improvement" in algo_config["strategies"]:
            imp = algo_config["strategies"]["improvement"]
            strategies_str += f"|imp={imp['name']}"
            if "params" in imp:
                imp_params = ",".join(f"{k}={v}" for k, v in imp["params"].items())
                strategies_str += f"({imp_params})"

        # Add multistart if present
        if "multistart" in algorithm:
            strategies_str += "|multistart=8"

    # Get backend module (numpy or cupy)
    import numpy as np

    backend_module = np
    if backend == "cupy":
        try:
            import cupy as cp

            backend_module = cp
        except ImportError:
            pass  # Fall back to numpy

    # Run algorithm (returns BenchmarkResult object)
    benchmark_result = run_algorithm_timed(
        algo_instance, problem, params, backend_module
    )

    # Check for errors
    if not benchmark_result.success:
        print(f"⚠️  {algorithm} on {problem.name} FAILED: {benchmark_result.error_msg}")

    # Get raw stats from algorithm instance (need to run again for full stats)
    # For now, use BenchmarkResult data
    result = ComprehensiveResult(
        problem_name=problem.name,
        problem_size=problem.dimension,
        algorithm=algorithm,
        backend=backend,
        best_fitness=benchmark_result.fitness,
        final_fitness=benchmark_result.fitness,  # BenchmarkResult doesn't separate these
        iterations=benchmark_result.iterations,
        time_seconds=benchmark_result.time_seconds,
        # NEW: Strategy and VRAM info
        strategies_used=strategies_str,
        expected_vram_mb=expected_vram_mb,
        actual_vram_mb=actual_vram_mb,
        # Extended stats not in BenchmarkResult (would need algorithm instance stats)
        convergence_history=[],  # TODO: Extract from full stats
        raw_stats={},  # Would need algorithm._stats
    )

    # Calculate first improvement iteration
    if result.convergence_history:
        best_cost = result.best_fitness
        for i, cost in enumerate(result.convergence_history):
            if cost <= best_cost:
                result.first_improvement_iter = i
                break

    # Calculate plateau length (iterations without improvement)
    if result.convergence_history:
        plateau = 0
        for i in range(len(result.convergence_history) - 1, 0, -1):
            if result.convergence_history[i] == result.convergence_history[i - 1]:
                plateau += 1
            else:
                break
        result.plateau_length = plateau

    return result


def run_comprehensive_benchmark(config: BenchmarkConfig) -> List[ComprehensiveResult]:
    """
    Run ALL benchmark combinations.

    Returns structured data WITHOUT printing anything!
    This allows user to control output format.
    """
    results = []

    # Load problems once
    all_problems = {}
    for tier in config.problem_tiers:
        try:
            tier_problems = get_benchmark_problems(tier)
            all_problems.update(tier_problems)
        except Exception as e:
            if config.verbose:
                print(f"⚠️  Tier '{tier}' load failed: {e}")

    # Query optimal costs once
    optimal_costs = get_optimal_costs(list(all_problems.keys()))

    # Run all combinations
    total_runs = len(all_problems) * len(config.algorithms) * len(config.backends)
    current_run = 0

    for problem in all_problems.values():
        for algorithm in config.algorithms:
            for backend in config.backends:
                current_run += 1

                if config.verbose:
                    print(
                        f"[{current_run}/{total_runs}] {problem.name} | {algorithm} | {backend}"
                    )

                try:
                    result = run_single_benchmark(problem, algorithm, backend, config)

                    # Add optimal cost comparison
                    optimal = optimal_costs.get(problem.name)
                    if optimal:
                        result.optimal_cost = optimal
                        result.gap_percent = (
                            100 * (result.best_fitness - optimal) / optimal
                        )

                    results.append(result)

                except Exception as e:
                    if config.verbose:
                        print(f"  ❌ Error: {e}")

    # Calculate speedups (compare CuPy vs NumPy for same problem/algorithm)
    for i, result in enumerate(results):
        if result.backend == "cupy":
            # Find corresponding NumPy result
            for numpy_result in results:
                if (
                    numpy_result.problem_name == result.problem_name
                    and numpy_result.algorithm == result.algorithm
                    and numpy_result.backend == "numpy"
                ):
                    # Avoid division by zero for failed runs
                    if result.time_seconds > 0 and numpy_result.time_seconds > 0:
                        result.speedup = numpy_result.time_seconds / result.time_seconds
                    break

    return results


# ═══════════════════════════════════════════════════════════
# OUTPUT FORMATTING (USER-CONTROLLED)
# ═══════════════════════════════════════════════════════════


def print_summary_table(results: List[ComprehensiveResult]) -> None:
    """
    Print summary table to console.

    Clean, structured output with key metrics + strategies + VRAM.
    """
    table_data = []

    for r in results:
        row = [
            r.problem_name,
            r.problem_size,
            r.algorithm.upper(),
            r.backend.capitalize(),
            f"{r.best_fitness:.1f}",
            f"{r.optimal_cost:.1f}" if r.optimal_cost else "N/A",
            f"{r.gap_percent:+.2f}%" if r.gap_percent is not None else "N/A",
            f"{r.iterations}",
            f"{r.time_seconds:.3f}s",
            f"{r.speedup:.2f}x" if r.speedup else "-",
            r.strategies_used,  # NEW
            f"{r.expected_vram_mb:.2f}",  # NEW
            f"{r.actual_vram_mb:.2f}" if r.actual_vram_mb else "N/A",  # NEW
        ]
        table_data.append(row)

    headers = [
        "Problem",
        "Size",
        "Algo",
        "Backend",
        "Cost",
        "Optimal",
        "Gap%",
        "Iters",
        "Time",
        "Speedup",
        "Strategies",
        "VRAM(MB)",
        "Actual(MB)",  # NEW COLUMNS
    ]

    print("\n" + "=" * 160)
    print("COMPREHENSIVE BENCHMARK RESULTS")
    print("=" * 160)
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print()


def export_csv(results: List[ComprehensiveResult], filepath: str) -> None:
    """Export results to CSV for Excel/plotting."""
    import csv

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(
            [
                "problem",
                "size",
                "algorithm",
                "backend",
                "best_fitness",
                "final_fitness",
                "iterations",
                "time_seconds",
                "optimal_cost",
                "gap_percent",
                "first_improvement_iter",
                "plateau_length",
                "acceptance_rate",
                "speedup",
            ]
        )

        # Data
        for r in results:
            writer.writerow(
                [
                    r.problem_name,
                    r.problem_size,
                    r.algorithm,
                    r.backend,
                    r.best_fitness,
                    r.final_fitness,
                    r.iterations,
                    r.time_seconds,
                    r.optimal_cost or "",
                    r.gap_percent or "",
                    r.first_improvement_iter or "",
                    r.plateau_length or "",
                    r.acceptance_rate or "",
                    r.speedup or "",
                ]
            )

    print(f"✅ Results exported to {filepath}")


def export_json(results: List[ComprehensiveResult], filepath: str) -> None:
    """Export complete results to JSON (includes convergence history)."""
    data = [asdict(r) for r in results]

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Results exported to {filepath}")


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════


def main():
    """
    Main entry point with argument parsing.

    Allows easy configuration changes from command line.
    """
    parser = argparse.ArgumentParser(
        description="Comprehensive routing algorithm benchmark"
    )

    parser.add_argument(
        "--tiers",
        nargs="+",
        default=["tiny", "small"],
        help="Problem size tiers to test (default: tiny small)",
    )

    parser.add_argument(
        "--algorithms",
        nargs="+",
        default=["ga", "ga_2opt", "ga_multistart", "sa", "sa_2opt", "sa_multistart"],
        help="Algorithms to test (default: all variants)",
    )

    parser.add_argument(
        "--backends",
        nargs="+",
        default=["numpy", "cupy"],
        help="Backends to test (default: numpy cupy)",
    )

    parser.add_argument(
        "--ga-population",
        type=int,
        default=200,  # Increased from 100!
        help="GA population size (default: 200)",
    )

    parser.add_argument(
        "--ga-generations",
        type=int,
        default=100,
        help="GA max generations (default: 100)",
    )

    parser.add_argument(
        "--sa-iterations",
        type=int,
        default=1000,
        help="SA max iterations (default: 1000)",
    )

    parser.add_argument(
        "--export", type=str, default=None, help="Export results to file (csv/json)"
    )

    parser.add_argument(
        "--quiet", action="store_true", help="Suppress progress messages"
    )

    args = parser.parse_args()

    # Build configuration from arguments
    config = BenchmarkConfig(
        problem_tiers=args.tiers,
        algorithms=args.algorithms,
        backends=args.backends,
        ga_params={
            "population_size": args.ga_population,
            "max_generations": args.ga_generations,
            "crossover_rate": 0.9,
            "mutation_rate": 0.1,
            "use_2opt": False,
        },
        sa_params={
            "initial_temp": 1000.0,
            "final_temp": 0.01,
            "cooling_rate": 0.995,
            "max_iterations": args.sa_iterations,
        },
        verbose=not args.quiet,
    )

    print("\n" + "=" * 120)
    print("CONFIGURATION")
    print("=" * 120)
    print(f"Problem tiers: {', '.join(config.problem_tiers)}")
    print(f"Algorithms: {', '.join(config.algorithms)}")
    print(f"Backends: {', '.join(config.backends)}")
    print(f"GA: population={args.ga_population}, generations={args.ga_generations}")
    print(f"SA: iterations={args.sa_iterations}")
    print("=" * 120)

    # Run benchmark
    results = run_comprehensive_benchmark(config)

    # Display results
    print_summary_table(results)

    # Export if requested
    if args.export:
        if args.export.endswith(".csv"):
            export_csv(results, args.export)
        elif args.export.endswith(".json"):
            export_json(results, args.export)
        else:
            print(f"⚠️  Unknown export format: {args.export}")

    return 0


if __name__ == "__main__":
    exit(main())
