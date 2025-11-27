#!/usr/bin/env python3
"""Chapter 4 Validation: Comprehensive ISO-Algorithmic GA Benchmark.

This benchmark validates memory transfer optimization claims in Chapter 4
by comparing 4 ISO-algorithmic GA variants on 30 diverse TSPLIB instances.

Academic Requirements (first_draft.md section 3.5):
    - 30 repetitions per algorithm for statistical significance
    - TSPLIB instances with known optimal solutions
    - Adaptive generation formula: 2 × n × sqrt(n)
    - Statistical validation: Friedman + Nemenyi + pairwise tests
    - Solution quality tracking: gap to optimum
    - Memory transfer measurement: H2D/D2H bytes

Architecture:
    - Single unified benchmark function (data-driven)
    - 30 TSP problems spanning 51 to 1002 cities
    - Configuration at top for easy modification
    - Comprehensive statistics per problem and cross-problem
    - Memory cleanup between runs

Author: AI Assistant
Date: 2025-01-28
"""

import argparse
import gc
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import cupy as cp

# Import algorithm variants
from src.algorithms.metaheuristics.genetic_algorithm_cpu import GeneticAlgorithmCPU
from src.algorithms.metaheuristics.genetic_algorithm_hybrid_naive import (
    GeneticAlgorithmHybridNaive,
)
from src.algorithms.metaheuristics.genetic_algorithm_hybrid_optimized import (
    GeneticAlgorithmHybridOptimized,
)
from src.algorithms.metaheuristics.genetic_algorithm_full_gpu_early_stop import (
    GeneticAlgorithmFullGPUEarlyStop,
)
from src.loaders.database_loader import DatabaseLoader
from src.protocols.problem_context import ProblemContext
from src.benchmarking.statistics import StatisticalAnalyzer


# ============================================================================
# CONFIGURATION SECTION
# ============================================================================

# Display constants
LINE_WIDTH = 80
SEPARATOR = "=" * LINE_WIDTH
SHORT_SEP = "-" * LINE_WIDTH

# Genetic Algorithm parameters (ISO-algorithmic across all variants)
GA_PARAMS = {
    "population_size": 256,
    "mutation_rate": 0.02,
    "tournament_size": 5,
    "two_opt_iterations": 10,
    "seed": 42,
}

# Benchmark parameters
BENCHMARK_PARAMS = {
    "repetitions": 30,
    "patience": 50,  # Early stopping patience
    "skip_cpu_default": False,  # Include CPU for small problems (n<100)
    "cpu_size_threshold": 100,  # Only run CPU on problems with n < threshold
}

# Algorithm configurations
ALGORITHM_CONFIGS = {
    "CPU": {
        "class": GeneticAlgorithmCPU,
        "use_gpu": False,
        "description": "Pure NumPy CPU baseline",
    },
    "HybridNaive": {
        "class": GeneticAlgorithmHybridNaive,
        "use_gpu": True,
        "description": "GPU operators with naive memory transfers",
    },
    "HybridOptimized": {
        "class": GeneticAlgorithmHybridOptimized,
        "use_gpu": True,
        "description": "GPU operators with optimized memory transfers",
    },
    "FullGPU": {
        "class": GeneticAlgorithmFullGPUEarlyStop,
        "use_gpu": True,
        "description": "Fujimoto's full-GPU kernel with early stopping",
    },
}

# Problem set: 30 diverse TSP instances with known optima
# Selected for size diversity (51 to 1002 cities) and different characteristics
# ============================================================================
# TEST CONFIGURATION - Only 2 problems for quick validation
# ============================================================================
PROBLEM_SET_FULL = [
    # Small problems (50-100 cities) - Fast convergence, good for testing
    {"name": "eil51", "optimal": 426, "size": 51},
    {"name": "berlin52", "optimal": 7542, "size": 52},
    {"name": "st70", "optimal": 675, "size": 70},
    {"name": "eil76", "optimal": 538, "size": 76},
    {"name": "pr76", "optimal": 108159, "size": 76},
    {"name": "rat99", "optimal": 1211, "size": 99},
    {"name": "kroA100", "optimal": 21282, "size": 100},
    {"name": "kroB100", "optimal": 22141, "size": 100},
    {"name": "kroC100", "optimal": 20749, "size": 100},
    {"name": "kroD100", "optimal": 21294, "size": 100},
    {"name": "kroE100", "optimal": 22068, "size": 100},
    {"name": "rd100", "optimal": 7910, "size": 100},
    # Medium problems (100-200 cities) - Balanced runtime/difficulty
    {"name": "eil101", "optimal": 629, "size": 101},
    {"name": "lin105", "optimal": 14379, "size": 105},
    {"name": "pr107", "optimal": 44303, "size": 107},
    {"name": "pr124", "optimal": 59030, "size": 124},
    {"name": "bier127", "optimal": 118282, "size": 127},
    {"name": "ch130", "optimal": 6110, "size": 130},
    {"name": "pr136", "optimal": 96772, "size": 136},
    {"name": "pr144", "optimal": 58537, "size": 144},
    {"name": "ch150", "optimal": 6528, "size": 150},
    {"name": "kroA150", "optimal": 26524, "size": 150},
    {"name": "kroB150", "optimal": 26130, "size": 150},
    {"name": "pr152", "optimal": 73682, "size": 152},
    {"name": "u159", "optimal": 42080, "size": 159},
    {"name": "rat195", "optimal": 2323, "size": 195},
    {"name": "d198", "optimal": 15780, "size": 198},
    {"name": "kroA200", "optimal": 29368, "size": 200},
    # Large problems (200-1000 cities) - Challenging, shows GPU advantage
    {"name": "ts225", "optimal": 126643, "size": 225},
    {"name": "pr264", "optimal": 49135, "size": 264},
    {"name": "pr299", "optimal": 48191, "size": 299},
    {"name": "lin318", "optimal": 42029, "size": 318},
    {"name": "rd400", "optimal": 15281, "size": 400},
    {"name": "fl417", "optimal": 11861, "size": 417},
    {"name": "pr439", "optimal": 107217, "size": 439},
    {"name": "pcb442", "optimal": 50778, "size": 442},
    {"name": "rat783", "optimal": 8806, "size": 783},
    {"name": "pr1002", "optimal": 259045, "size": 1002},
]

# Problem set: Default to full benchmark (38 problems)
# Can be overridden to 2 problems with --test-mode flag
PROBLEM_SET = PROBLEM_SET_FULL


# ============================================================================
# CHECKPOINT SYSTEM (Fault Tolerance)
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
CHECKPOINT_DIR = SCRIPT_DIR / "results" / "checkpoints"
PROBLEM_STATS_DIR = SCRIPT_DIR / "results" / "problem_statistics"


def ensure_checkpoint_dirs():
    """Create checkpoint directories if they don't exist."""
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    PROBLEM_STATS_DIR.mkdir(parents=True, exist_ok=True)


def get_checkpoint_path(problem_name: str, algorithm_name: str) -> Path:
    """Get checkpoint file path for a (problem, algorithm) pair."""
    return CHECKPOINT_DIR / f"{problem_name}_{algorithm_name}.json"


def get_problem_stats_path(problem_name: str) -> Path:
    """Get statistics file path for a problem."""
    return PROBLEM_STATS_DIR / f"{problem_name}_stats.json"


def is_valid_checkpoint(filepath: Path, expected_reps: int = 30) -> bool:
    """Validate checkpoint file integrity and completeness.

    Args:
        filepath: Path to checkpoint file
        expected_reps: Expected number of repetitions (default: 30)

    Returns:
        True if checkpoint exists, is valid JSON, has all required fields,
        and has expected number of successful runs.
    """
    if not filepath.exists():
        return False

    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        # Check structure - checkpoint contains summary statistics, not raw repetitions
        required_fields = [
            "algorithm",
            "repetitions",
            "successful_runs",
            "mean_time",
            "mean_cost",
            "raw_times",
            "raw_costs",
            "raw_gaps",
        ]
        if not all(field in data for field in required_fields):
            logging.warning(f"Checkpoint {filepath.name} missing required fields")
            return False

        # Check repetitions match
        if data["repetitions"] != expected_reps:
            logging.warning(
                f"Checkpoint {filepath.name} has {data['repetitions']} reps, "
                f"expected {expected_reps}"
            )
            return False

        # Check successful runs
        if data["successful_runs"] != expected_reps:
            logging.warning(
                f"Checkpoint {filepath.name} incomplete: "
                f"{data['successful_runs']}/{expected_reps} successful runs"
            )
            return False

        return True

    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        logging.warning(f"Checkpoint {filepath.name} corrupted: {e}")
        return False


def numpy_to_json_converter(obj):
    """Convert numpy types to JSON-serializable Python types.

    Handles numpy arrays (via tolist()) and numpy scalars (via item()).
    This covers all numpy dtypes: int8-64, float16-64, bool, etc.
    """
    if hasattr(obj, "tolist"):  # numpy array
        return obj.tolist()
    elif hasattr(obj, "item"):  # numpy scalar
        val = obj.item()
        # Handle NaN: convert to null for valid JSON (RFC 8259 compliance)
        if isinstance(val, float) and (val != val):  # NaN check
            return None
        return val
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def save_checkpoint_atomic(filepath: Path, results: Dict[str, Any]):
    """Save checkpoint using atomic write (temp file + rename).

    Prevents corruption if process crashes during write.

    Args:
        filepath: Destination checkpoint file
        results: Results dictionary to save
    """
    # Write to temporary file first
    temp_fd, temp_path = tempfile.mkstemp(
        dir=filepath.parent, prefix=f".tmp_{filepath.stem}_", suffix=".json"
    )

    try:
        with os.fdopen(temp_fd, "w") as f:
            # Use default converter to handle all numpy types
            json.dump(results, f, indent=2, default=numpy_to_json_converter)
            f.flush()  # Flush Python buffers
            os.fsync(
                f.fileno()
            )  # Ensure OS writes to disk (prevents corruption on disk full)

        # Atomic rename (POSIX guarantees atomicity)
        os.replace(temp_path, filepath)
        logging.info(f"    ✓ Checkpoint saved: {filepath.name}")

    except Exception as e:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except Exception:
            pass
        raise RuntimeError(f"Failed to save checkpoint: {e}") from e


def load_checkpoint(filepath: Path) -> Dict[str, Any]:
    """Load results from checkpoint file.

    Args:
        filepath: Checkpoint file to load

    Returns:
        Results dictionary
    """
    with open(filepath, "r") as f:
        return json.load(f)


def count_completed_checkpoints(
    problem_set: List[Dict], algorithms: List[str], expected_reps: int = 30
) -> tuple:
    """Count how many checkpoints already exist.

    Args:
        problem_set: List of problem configurations
        algorithms: List of algorithm names
        expected_reps: Expected number of repetitions for validation

    Returns:
        (completed_count, total_count) tuple
    """
    completed = 0
    total = 0

    for problem in problem_set:
        problem_name = problem["name"]
        problem_size = problem["size"]

        # Determine which algorithms to run for this problem
        problem_algorithms = (
            algorithms
            if problem_size <= BENCHMARK_PARAMS["cpu_size_threshold"]
            else [a for a in algorithms if ALGORITHM_CONFIGS[a]["use_gpu"]]
        )

        for algo in problem_algorithms:
            total += 1
            checkpoint_path = get_checkpoint_path(problem_name, algo)
            if is_valid_checkpoint(checkpoint_path, expected_reps):
                completed += 1

    return completed, total


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def adaptive_generations(n: int) -> int:
    """Calculate adaptive generations: 2 × n × sqrt(n)."""
    return int(2 * n * math.sqrt(n))


def log_benchmark_configuration(args, selected_algorithms: List[str]):
    """Log benchmark configuration at startup."""
    logging.info(SEPARATOR)
    logging.info("CHAPTER 4 VALIDATION: COMPREHENSIVE GA BENCHMARK")
    logging.info(SEPARATOR)
    logging.info("")
    logging.info("Configuration:")
    logging.info(f"  Problems: {len(PROBLEM_SET)} TSP instances")
    logging.info(
        f"  Size range: {PROBLEM_SET[0]['size']} to {PROBLEM_SET[-1]['size']} cities"
    )
    logging.info(f"  Algorithms: {', '.join(selected_algorithms)}")
    logging.info(f"  Repetitions: {args.repetitions} per algorithm")
    logging.info(
        f"  Early stopping patience: {BENCHMARK_PARAMS['patience']} generations"
    )
    logging.info("")
    logging.info("GA Parameters:")
    for key, value in GA_PARAMS.items():
        logging.info(f"  {key}: {value}")
    logging.info("")
    logging.info("Problem Set:")
    logging.info(f"{'#':<4} {'Name':<12} {'Size':<6} {'Optimal':<12} {'Max Gens':<10}")
    logging.info(SHORT_SEP)
    for i, prob in enumerate(PROBLEM_SET, 1):
        max_gens = adaptive_generations(prob["size"])
        logging.info(
            f"{i:<4} {prob['name']:<12} {prob['size']:<6} {prob['optimal']:<12} {max_gens:<10}"
        )
    logging.info("")
    logging.info("Algorithm-Problem Combinations:")
    total_combinations = len(PROBLEM_SET) * len(selected_algorithms)
    total_runs = total_combinations * args.repetitions
    logging.info(
        f"  Total combinations: {len(PROBLEM_SET)} problems × {len(selected_algorithms)} algorithms = {total_combinations}"
    )
    logging.info(
        f"  Total runs: {total_combinations} × {args.repetitions} reps = {total_runs}"
    )
    logging.info(SEPARATOR)
    logging.info("")


def run_single_algorithm(
    algorithm_name: str,
    algorithm_instance,
    problem,
    problem_name: str,
    problem_size: int,
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
        problem_name: Problem identifier
        problem_size: Number of cities
        customers: Customer indices
        max_generations: Number of generations
        optimal_cost: Known optimal solution cost
        repetitions: Number of runs
        use_gpu: Whether to use GPU backend

    Returns:
        Dictionary with aggregated results
    """
    backend = "GPU" if use_gpu else "CPU"
    logging.info(
        f"\n  [{algorithm_name}] Processing {problem_name} (n={problem_size}, optimal={optimal_cost:.0f})"
    )
    logging.info(
        f"    Backend: {backend} | Early stopping: 50 gen patience | Repetitions: {repetitions}"
    )

    results = {
        "times": [],
        "initial_costs": [],
        "final_costs": [],
        "gaps": [],
        "improvements": [],
        "generations": [],
        "stop_reasons": [],
        "h2d_bytes": [],
        "d2h_bytes": [],
        "kernel_launches": [],  # Will store Python ints to avoid overflow
        "best_tours": [],
    }

    for rep in range(repetitions):
        # Create fresh context for each run
        xp = cp if use_gpu else np
        context = ProblemContext(problem, xp=xp, seed=42 + rep)

        # Log repetition start
        logging.info(f"    Repetition {rep + 1}/{repetitions}...")

        # Run algorithm
        start_time = time.perf_counter()
        try:
            tour, stats = algorithm_instance.evolve(
                context,
                customers,
                max_generations,
                optimal_cost=optimal_cost,
                patience=BENCHMARK_PARAMS["patience"],
            )
            elapsed = time.perf_counter() - start_time

            # Extract metrics
            initial_cost = stats["initial_fitness"]
            final_cost = stats["best_fitness"]
            gap = (final_cost - optimal_cost) / optimal_cost * 100
            improvement = (initial_cost - final_cost) / initial_cost * 100
            generations = stats.get("generations_completed", 0)
            stop_reason = stats.get("stop_reason", "completed")

            results["times"].append(elapsed)
            results["initial_costs"].append(initial_cost)
            results["final_costs"].append(final_cost)
            results["gaps"].append(gap)
            results["improvements"].append(improvement)
            results["generations"].append(generations)
            results["stop_reasons"].append(stop_reason)
            results["h2d_bytes"].append(stats.get("h2d_bytes", 0))
            results["d2h_bytes"].append(stats.get("d2h_bytes", 0))
            results["kernel_launches"].append(stats.get("kernel_launches", 0))
            results["best_tours"].append(tour)

            # Log completion with key metrics
            logging.info(
                f"      → Completed in {elapsed:.2f}s | "
                f"Cost: {final_cost:.0f} (gap: {gap:.2f}%) | "
                f"Generations: {generations}/{max_generations}"
            )

        except Exception as e:
            logging.error(f"    Rep {rep + 1} FAILED: {e}")
            import traceback

            traceback.print_exc()
            # CRITICAL: Append to ALL lists to maintain synchronization
            results["times"].append(np.nan)
            results["initial_costs"].append(np.nan)
            results["final_costs"].append(np.nan)
            results["gaps"].append(np.nan)
            results["improvements"].append(np.nan)
            results["generations"].append(0)
            results["stop_reasons"].append("error")
            results["h2d_bytes"].append(0)
            results["d2h_bytes"].append(0)
            results["kernel_launches"].append(0)
            results["best_tours"].append(None)

    # Calculate statistics
    times = np.array(results["times"])
    initial_costs_arr = np.array(results["initial_costs"])
    final_costs = np.array(results["final_costs"])
    gaps = np.array(results["gaps"])
    improvements = np.array(results["improvements"])
    generations_arr = np.array(results["generations"])
    h2d = np.array(results["h2d_bytes"])
    d2h = np.array(results["d2h_bytes"])

    # Remove NaN values
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
        # Initial costs
        "mean_initial_cost": np.nanmean(initial_costs_arr),
        "std_initial_cost": np.nanstd(initial_costs_arr),
        # Gap to optimal
        "mean_gap": np.nanmean(gaps),
        "std_gap": np.nanstd(gaps),
        "best_gap": np.nanmin(gaps),
        # Improvement from initial
        "mean_improvement": np.nanmean(improvements),
        # Convergence metrics
        "mean_generations": np.nanmean(generations_arr),
        "std_generations": np.nanstd(generations_arr),
        "min_generations": np.nanmin(generations_arr),
        "max_generations": np.nanmax(generations_arr),
        # Memory transfers
        "mean_h2d_mb": np.nanmean(h2d) / 1e6,
        "mean_d2h_mb": np.nanmean(d2h) / 1e6,
        "total_transfer_mb": (np.nanmean(h2d) + np.nanmean(d2h)) / 1e6,
        # Kernel launches
        "mean_kernels": np.nanmean(results["kernel_launches"]),
        # Raw data for statistical tests
        "raw_times": times[valid_mask],
        "raw_initial_costs": initial_costs_arr[valid_mask],
        "raw_costs": final_costs[valid_mask],
        "raw_gaps": gaps[valid_mask],
        "raw_generations": generations_arr[valid_mask],
        "raw_stop_reasons": [
            results["stop_reasons"][i] for i in range(len(valid_mask)) if valid_mask[i]
        ],
        # Problem metadata (will be added by caller)
        # Algorithm parameters (will be added by caller)
    }

    logging.info(
        f"\n    ✓ {algorithm_name} summary for {problem_name}: "
        f"Cost={summary['mean_cost']:.0f}±{summary['std_cost']:.1f} | "
        f"Gap={summary['mean_gap']:.2f}%±{summary['std_gap']:.2f}% | "
        f"Time={summary['mean_time']:.2f}s±{summary['std_time']:.2f}s"
    )

    return summary


def holm_bonferroni_correction(p_values: List[float], alpha: float = 0.05):
    """Apply Holm-Bonferroni multiple comparison correction.

    Args:
        p_values: List of p-values to correct
        alpha: Significance level (default: 0.05)

    Returns:
        Tuple of (reject, pvals_corrected) where:
        - reject: Boolean array indicating which hypotheses to reject
        - pvals_corrected: Adjusted p-values
    """
    n = len(p_values)
    if n == 0:
        return [], []

    # Sort p-values with original indices
    sorted_indices = np.argsort(p_values)
    sorted_pvals = np.array(p_values)[sorted_indices]

    # Holm-Bonferroni critical values
    critical_values = alpha / (n - np.arange(n))

    # Reject hypotheses where p < critical value
    reject_sorted = sorted_pvals < critical_values

    # Adjusted p-values (step-down procedure)
    # CRITICAL: Must use maximum.accumulate for monotonicity (p_adj must be non-decreasing)
    raw_adjusted = np.minimum(
        (n - np.arange(n)) * sorted_pvals, 1.0
    )  # Clip each to 1.0
    pvals_corrected_sorted = np.maximum.accumulate(raw_adjusted)  # Enforce monotonicity

    # Restore original order
    reject = np.zeros(n, dtype=bool)
    pvals_corrected = np.zeros(n)
    reject[sorted_indices] = reject_sorted
    pvals_corrected[sorted_indices] = pvals_corrected_sorted

    return reject.tolist(), pvals_corrected.tolist()


def _get_data_field(results_dict: Dict[str, Any], field: str) -> list:
    """Safely extract data field with fallback for checkpoint vs direct format.

    Args:
        results_dict: Algorithm results dictionary
        field: Field name ('costs', 'times', or 'gaps')

    Returns:
        List of values
    """
    # Checkpoint format uses raw_* prefix
    raw_field = f"raw_{field}"
    # Direct format uses final_costs, times, gaps
    direct_field = "final_costs" if field == "costs" else field

    return results_dict.get(raw_field, results_dict.get(direct_field, []))


def perform_statistical_analysis(
    problem_name: str,
    optimal_cost: float,
    results: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Perform statistical analysis on results for a single problem.

    Args:
        problem_name: Name of TSPLIB instance
        optimal_cost: Known optimal solution
        results: Dictionary of algorithm results

    Returns:
        Dictionary containing all statistical test results
    """
    logging.info(f"\nStatistical Analysis: {problem_name}")
    logging.info(SHORT_SEP)

    analyzer = StatisticalAnalyzer()
    algorithm_names = list(results.keys())

    # Guard against empty algorithm list (e.g., all checkpoints failed validation)
    if len(algorithm_names) < 2:
        logging.warning(
            f"Skipping statistical analysis for {problem_name}: "
            f"only {len(algorithm_names)} algorithm(s) available (need ≥2)"
        )
        return {
            "problem_name": problem_name,
            "optimal_cost": optimal_cost,
            "error": "insufficient_data",
            "available_algorithms": algorithm_names,
        }

    cost_data = [
        np.array(_get_data_field(results[name], "costs")) for name in algorithm_names
    ]

    # Friedman test
    if len(algorithm_names) >= 3:
        friedman_result = analyzer.friedman_test(cost_data)

        logging.info(f"Friedman Test (k={len(algorithm_names)} algorithms):")
        logging.info(f"  Statistic: {friedman_result['statistic']:.4f}")
        logging.info(f"  p-value: {friedman_result['p_value']:.6f}")
        logging.info(f"  Significant: {friedman_result['significant']}")

        # Calculate mean ranks for interpretation (standard Friedman output)
        from scipy.stats import rankdata

        mean_ranks = {}
        n_obs = len(cost_data[0])
        for i, name in enumerate(algorithm_names):
            ranks = []
            for obs_idx in range(n_obs):
                obs_costs = [cost_data[j][obs_idx] for j in range(len(algorithm_names))]
                obs_ranks = rankdata(obs_costs, method="average")
                ranks.append(obs_ranks[i])
            mean_ranks[name] = float(np.mean(ranks))

        # Nemenyi post-hoc if significant
        if friedman_result["post_hoc_required"]:
            logging.info("\nNemenyi Post-Hoc Test:")
            nemenyi_result = analyzer.nemenyi_posthoc(cost_data, algorithm_names)

            logging.info(
                f"  Critical distance: {nemenyi_result['critical_distance']:.4f}"
            )
            logging.info("  Mean ranks:")
            for name, rank in mean_ranks.items():
                logging.info(f"    {name}: {rank:.2f}")

            logging.info("\n  Significant pairwise differences:")
            if nemenyi_result["significant_pairs"]:
                for i, j, p_val in nemenyi_result["significant_pairs"]:
                    name_i = nemenyi_result["algorithm_names"][i]
                    name_j = nemenyi_result["algorithm_names"][j]
                    rank_diff = abs(mean_ranks[name_i] - mean_ranks[name_j])
                    logging.info(
                        f"    {name_i} vs {name_j}: "
                        f"rank_diff={rank_diff:.2f}, p={p_val:.4f}"
                    )
            else:
                logging.info("    None (no significant differences detected)")

    # Pairwise comparisons with proper statistical tests
    logging.info("\nPairwise Comparisons:")
    logging.info("Following gpu_cpu_comparison_methodology.md guidelines:")
    logging.info("  - Normality testing (Shapiro-Wilk)")
    logging.info("  - Test selection (paired t-test vs Wilcoxon)")
    logging.info("  - Effect size (Cohen's d)")
    logging.info("  - 95% Confidence Intervals")
    logging.info("  - Holm-Bonferroni multiple comparison correction\n")

    comparisons = []
    for i, name1 in enumerate(algorithm_names):
        for name2 in algorithm_names[i + 1 :]:
            summary = analyzer.paired_comparison(
                np.array(_get_data_field(results[name1], "costs")),
                np.array(_get_data_field(results[name2], "costs")),
                f"{name1} vs {name2}",
                metric_name="cost",
            )
            comparisons.append(summary)

            # Handle degenerate case (zero variance) with special messaging
            if summary.test_used == "no_test_needed":
                logging.info(f"  {name1} vs {name2}:")
                logging.info(f"    All measurements identical (no variance)")
                logging.info(f"    Mean {name1}: {summary.mean_a:.2f}")
                logging.info(f"    Mean {name2}: {summary.mean_b:.2f}")
                logging.info(
                    f"    No statistical test needed - algorithms performed identically"
                )
                continue

            logging.info(f"  {name1} vs {name2}:")
            logging.info(f"    Normality (Shapiro-Wilk):")
            logging.info(
                f"      {name1}: p={summary.normality_p_value_a:.4f} {'(normal)' if summary.normality_p_value_a >= 0.05 else '(non-normal)'}"
            )
            logging.info(
                f"      {name2}: p={summary.normality_p_value_b:.4f} {'(normal)' if summary.normality_p_value_b >= 0.05 else '(non-normal)'}"
            )
            logging.info(f"    Test selected: {summary.test_used}")
            logging.info(f"    Mean difference: {summary.mean_difference:.2f}")
            logging.info(
                f"    95% CI difference: [{summary.ci_95_difference[0]:.2f}, {summary.ci_95_difference[1]:.2f}]"
            )
            logging.info(f"    p-value (uncorrected): {summary.p_value:.6f}")
            logging.info(f"    Cohen's d: {summary.effect_size:.4f}")
            if abs(summary.effect_size) < 0.2:
                effect_interp = "negligible"
            elif abs(summary.effect_size) < 0.5:
                effect_interp = "small"
            elif abs(summary.effect_size) < 0.8:
                effect_interp = "medium"
            else:
                effect_interp = "large"
            logging.info(f"    Effect size interpretation: {effect_interp}")

    # Apply Holm-Bonferroni correction
    if len(comparisons) > 1:
        p_values = [c.p_value for c in comparisons]
        reject, pvals_corrected = holm_bonferroni_correction(p_values, alpha=0.05)

        logging.info("\n  Multiple Comparison Correction (Holm-Bonferroni, α=0.05):")
        for comp, p_orig, p_adj, sig in zip(
            comparisons, p_values, pvals_corrected, reject
        ):
            logging.info(f"    {comp.comparison_label}:")
            logging.info(f"      Original p-value: {p_orig:.6f}")
            logging.info(f"      Adjusted p-value: {p_adj:.6f}")
            logging.info(f"      Significant (after correction): {sig}")

    # Summary table
    logging.info(f"\nSummary: {problem_name} (optimal={optimal_cost})")
    logging.info(SHORT_SEP)
    header_fmt = f"{'Algorithm':<20} {'Mean Cost':<15} {'Gap (%)':<12} {'Time (s)':<12} {'H2D (MB)':<12} {'D2H (MB)':<12}"
    logging.info(header_fmt)
    logging.info(SHORT_SEP)
    for name in algorithm_names:
        r = results[name]
        row_fmt = (
            f"{name:<20} "
            f"{r['mean_cost']:<15.2f} "
            f"{r['mean_gap']:<12.2f} "
            f"{r['mean_time']:<12.2f} "
            f"{r['mean_h2d_mb']:<12.2f} "
            f"{r['mean_d2h_mb']:<12.2f}"
        )
        logging.info(row_fmt)

    # Calculate and log speedups
    logging.info("\nSpeedups (relative to baseline):")
    # Use CPU as baseline if available, otherwise HybridNaive
    baseline_name = "CPU" if "CPU" in results else "HybridNaive"
    baseline_time = results[baseline_name]["mean_time"]

    for name in algorithm_names:
        if name == baseline_name:
            logging.info(f"  {name}: 1.00x (baseline)")
        else:
            speedup = baseline_time / results[name]["mean_time"]
            logging.info(f"  {name}: {speedup:.2f}x vs {baseline_name}")

    logging.info("")

    # BUILD STATISTICAL RESULTS DICTIONARY TO RETURN
    statistical_results = {
        "problem_name": problem_name,
        "optimal_cost": optimal_cost,
        "baseline_algorithm": baseline_name,
    }

    # Add Friedman test results if applicable
    if len(algorithm_names) >= 3:
        statistical_results["friedman_test"] = {
            "statistic": float(friedman_result["statistic"]),
            "p_value": float(friedman_result["p_value"]),
            "significant": bool(friedman_result["significant"]),
            "post_hoc_required": bool(friedman_result["post_hoc_required"]),
        }

        # Add Nemenyi results if performed
        if friedman_result["post_hoc_required"] and "nemenyi_result" in locals():
            statistical_results["nemenyi_posthoc"] = {
                "critical_distance": float(nemenyi_result["critical_distance"]),
                "mean_ranks": mean_ranks,
                "algorithm_names": nemenyi_result["algorithm_names"],
                "significant_pairs": [
                    {
                        "algorithm_i": nemenyi_result["algorithm_names"][i],
                        "algorithm_j": nemenyi_result["algorithm_names"][j],
                        "p_value": float(p_val),
                        "rank_difference": abs(
                            mean_ranks[nemenyi_result["algorithm_names"][i]]
                            - mean_ranks[nemenyi_result["algorithm_names"][j]]
                        ),
                    }
                    for i, j, p_val in nemenyi_result["significant_pairs"]
                ],
            }

    # Add pairwise comparison results
    statistical_results["pairwise_comparisons"] = []
    for i, comp in enumerate(comparisons):
        comparison_dict = {
            "comparison": comp.comparison_label,
            "test_used": comp.test_used,
            "p_value": float(comp.p_value),
            "mean_difference": float(comp.mean_difference),
            "ci_95_lower": float(comp.ci_95_difference[0]),
            "ci_95_upper": float(comp.ci_95_difference[1]),
            "cohens_d": float(comp.effect_size),
            "normality_p_value_a": float(comp.normality_p_value_a),
            "normality_p_value_b": float(comp.normality_p_value_b),
        }

        # Add corrected p-value if available
        if len(comparisons) > 1 and i < len(pvals_corrected):
            comparison_dict["p_value_corrected"] = float(pvals_corrected[i])
            comparison_dict["significant_after_correction"] = bool(reject[i])

        # Effect size interpretation
        abs_d = abs(comp.effect_size)
        if abs_d < 0.2:
            comparison_dict["effect_interpretation"] = "negligible"
        elif abs_d < 0.5:
            comparison_dict["effect_interpretation"] = "small"
        elif abs_d < 0.8:
            comparison_dict["effect_interpretation"] = "medium"
        else:
            comparison_dict["effect_interpretation"] = "large"

        statistical_results["pairwise_comparisons"].append(comparison_dict)

    return statistical_results


def perform_cross_problem_analysis(all_results: Dict[str, Dict[str, Dict[str, Any]]]):
    """Perform cross-problem statistical analysis with STRATIFIED approach.
    
    **BUG FIX**: Original implementation failed with ValueError due to unequal
    sample sizes (CPU: 12 problems, GPU: 38 problems).
    
    **Solution**: Stratified analysis:
    - Stratum 1: Small problems (n<100) with ALL algorithms (CPU + GPU)
    - Stratum 2: All problems with GPU-only algorithms
    
    This maintains maximum statistical power while avoiding pairing issues.
    """
    logging.info(SEPARATOR)
    logging.info("CROSS-PROBLEM ANALYSIS (STRATIFIED APPROACH)")
    logging.info(SEPARATOR)

    analyzer = StatisticalAnalyzer()

    problem_names = list(all_results.keys())
    algorithm_names = list(all_results[problem_names[0]].keys())

    logging.info(f"Total problems analyzed: {len(problem_names)}")
    logging.info(f"Algorithms present: {', '.join(algorithm_names)}")
    logging.info("")
    logging.info("Using stratified analysis to handle CPU/GPU problem coverage difference:")
    logging.info(f"  - CPU runs: Problems with n < {BENCHMARK_PARAMS['cpu_size_threshold']}")
    logging.info("  - GPU runs: All problems")
    logging.info("")

    # =========================================================================
    # STRATUM 1: Small Problems (n < cpu_size_threshold) with ALL Algorithms
    # =========================================================================
    
    small_problems = [
        p for p in problem_names 
        if next((prob["size"] for prob in PROBLEM_SET if prob["name"] == p), 9999) 
           < BENCHMARK_PARAMS['cpu_size_threshold']
    ]
    small_problem_algos = [
        a for a in algorithm_names
        if all(a in all_results[p] for p in small_problems)
    ]
    
    if len(small_problem_algos) >= 3 and len(small_problems) >= 3:
        logging.info(SEPARATOR)
        logging.info(f"STRATUM 1: Small Problems (n < {BENCHMARK_PARAMS['cpu_size_threshold']})")
        logging.info(SEPARATOR)
        logging.info(f"Problems: {len(small_problems)} ({', '.join(sorted(small_problems)[:5])}{'...' if len(small_problems) > 5 else ''})")
        logging.info(f"Algorithms: {len(small_problem_algos)} ({', '.join(small_problem_algos)})")
        logging.info("")
        
        # Collect gap data for each algorithm
        small_data = []
        for algo in small_problem_algos:
            algo_gaps = []
            for problem in small_problems:
                algo_gaps.append(all_results[problem][algo]["mean_gap"])
            small_data.append(np.array(algo_gaps))
            logging.info(f"  {algo}: mean_gap={np.mean(algo_gaps):.2f}% ± {np.std(algo_gaps):.2f}%")
        
        logging.info("")
        
        # Friedman test
        friedman_result = analyzer.friedman_test(small_data)
        logging.info("Friedman Test:")
        logging.info(f"  Statistic: {friedman_result['statistic']:.4f}")
        logging.info(f"  p-value: {friedman_result['p_value']:.6f}")
        logging.info(f"  Significant: {friedman_result['significant']}")
        
        # Nemenyi post-hoc if significant
        if friedman_result.get("post_hoc_required", False):
            logging.info("\nNemenyi Post-Hoc Test:")
            nemenyi_result = analyzer.nemenyi_posthoc(small_data, small_problem_algos)
            
            logging.info(f"  Critical distance: {nemenyi_result['critical_distance']:.4f}")
            
            if nemenyi_result.get("significant_pairs", []):
                logging.info("  Significant pairwise differences:")
                for i, j, p_val in nemenyi_result["significant_pairs"]:
                    name_i = nemenyi_result["algorithm_names"][i]
                    name_j = nemenyi_result["algorithm_names"][j]
                    logging.info(f"    {name_i} vs {name_j}: p={p_val:.4f}")
            else:
                logging.info("  No significant pairwise differences detected")
        
        logging.info("")
    else:
        logging.info(f"STRATUM 1: Skipped (need ≥3 algorithms and ≥3 problems)")
        logging.info(f"  Found: {len(small_problem_algos)} algorithms, {len(small_problems)} problems")
        logging.info("")
    
    # =========================================================================
    # STRATUM 2: All Problems with GPU-Only Algorithms
    # =========================================================================
    
    gpu_algos = [a for a in algorithm_names if a != "CPU"]
    all_gpu_problems = [
        p for p in problem_names
        if all(a in all_results[p] for a in gpu_algos)
    ]
    
    if len(gpu_algos) >= 3 and len(all_gpu_problems) >= 3:
        logging.info(SEPARATOR)
        logging.info("STRATUM 2: All Problems (GPU Algorithms Only)")
        logging.info(SEPARATOR)
        
        size_range = [
            next((prob["size"] for prob in PROBLEM_SET if prob["name"] == p), 0)
            for p in all_gpu_problems
        ]
        logging.info(
            f"Problems: {len(all_gpu_problems)} "
            f"(n={min(size_range)} to {max(size_range)})"
        )
        logging.info(f"Algorithms: {len(gpu_algos)} ({', '.join(gpu_algos)})")
        logging.info("")
        
        # Collect gap data
        all_data = []
        for algo in gpu_algos:
            algo_gaps = []
            for problem in all_gpu_problems:
                algo_gaps.append(all_results[problem][algo]["mean_gap"])
            all_data.append(np.array(algo_gaps))
            logging.info(f"  {algo}: mean_gap={np.mean(algo_gaps):.2f}% ± {np.std(algo_gaps):.2f}%")
        
        logging.info("")
        
        # Calculate geometric mean speedup vs baseline
        logging.info("Geometric mean speedup (vs HybridNaive baseline):")
        baseline_algo = "HybridNaive" if "HybridNaive" in gpu_algos else gpu_algos[0]
        for algo in gpu_algos:
            if algo == baseline_algo:
                logging.info(f"  {algo}: 1.00x (baseline)")
            else:
                speedups = []
                for problem in all_gpu_problems:
                    baseline_time = all_results[problem][baseline_algo]["mean_time"]
                    algo_time = all_results[problem][algo]["mean_time"]
                    if algo_time > 0:
                        speedups.append(baseline_time / algo_time)
                
                if speedups:
                    geomean_speedup = np.exp(np.mean(np.log(speedups)))
                    logging.info(f"  {algo}: {geomean_speedup:.2f}x vs {baseline_algo}")
        
        logging.info("")
        
        # Friedman test
        friedman_result = analyzer.friedman_test(all_data)
        logging.info("Friedman Test:")
        logging.info(f"  Statistic: {friedman_result['statistic']:.4f}")
        logging.info(f"  p-value: {friedman_result['p_value']:.6f}")
        logging.info(f"  Significant: {friedman_result['significant']}")
        
        # Nemenyi post-hoc if significant
        if friedman_result.get("post_hoc_required", False):
            logging.info("\nNemenyi Post-Hoc Test:")
            nemenyi_result = analyzer.nemenyi_posthoc(all_data, gpu_algos)
            
            logging.info(f"  Critical distance: {nemenyi_result['critical_distance']:.4f}")
            
            if nemenyi_result.get("significant_pairs", []):
                logging.info("  Significant pairwise differences:")
                for i, j, p_val in nemenyi_result["significant_pairs"]:
                    name_i = nemenyi_result["algorithm_names"][i]
                    name_j = nemenyi_result["algorithm_names"][j]
                    logging.info(f"    {name_i} vs {name_j}: p={p_val:.4f}")
            else:
                logging.info("  No significant pairwise differences detected")
        
        logging.info("")
    else:
        logging.info(f"STRATUM 2: Skipped (need ≥3 algorithms and ≥3 problems)")
        logging.info(f"  Found: {len(gpu_algos)} algorithms, {len(all_gpu_problems)} problems")
        logging.info("")
    
    # =========================================================================
    # Summary Statistics (All Algorithms, All Their Problems)
    # =========================================================================
    
    logging.info(SEPARATOR)
    logging.info("CROSS-PROBLEM SUMMARY")
    logging.info(SEPARATOR)

    # Determine universal baseline
    universal_baseline = (
        "HybridNaive" if "HybridNaive" in algorithm_names else algorithm_names[0]
    )

    for algorithm in algorithm_names:
        gaps = []
        speedups = []

        for problem in problem_names:
            # Skip if algorithm doesn't exist for this problem
            if algorithm not in all_results[problem]:
                continue
            
            gaps.extend(_get_data_field(all_results[problem][algorithm], "gaps"))

            # Calculate speedup vs baseline for this problem
            if algorithm != universal_baseline:
                # Skip if baseline doesn't exist for this problem
                if universal_baseline not in all_results[problem]:
                    continue
                    
                baseline_time = all_results[problem][universal_baseline]["mean_time"]
                algo_time = all_results[problem][algorithm]["mean_time"]
                if algo_time > 0:
                    speedups.append(baseline_time / algo_time)

        # Geometric mean for speedups
        if speedups:
            geomean_speedup = np.exp(np.mean(np.log(speedups)))
            speedup_str = (
                f", geomean_speedup={geomean_speedup:.2f}× vs {universal_baseline}"
            )
        else:
            speedup_str = " (baseline)"

        logging.info(
            f"{algorithm}: "
            f"mean_gap={np.mean(gaps):.2f}%±{np.std(gaps):.2f}"
            f"{speedup_str}"
        )

    logging.info("")


# ============================================================================
# TABLE GENERATION
# ============================================================================


def generate_result_tables(
    all_results: Dict[str, Dict[str, Dict[str, Any]]], benchmark_name: str
):
    """Generate Markdown and LaTeX tables from benchmark results.

    Following gpu_cpu_comparison_methodology.md guidelines for academic reporting.

    Args:
        all_results: Dictionary mapping problem names to algorithm results
        benchmark_name: Name for output files
    """
    from pathlib import Path

    # Create output directories
    results_dir = Path("results")
    tables_dir = results_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    logging.info(SEPARATOR)
    logging.info("GENERATING RESULT TABLES")
    logging.info(SEPARATOR)

    problem_names = sorted(all_results.keys())
    algorithm_names = sorted(list(all_results[problem_names[0]].keys()))

    # ========================================================================
    # Table 1: Summary Statistics Per Problem
    # ========================================================================

    md_lines = []
    tex_lines = []

    # Markdown header with proper alignment
    md_lines.append("# Chapter 4 Validation Results\n")
    md_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_lines.append("## Table 1: Summary Statistics by Problem\n")
    md_lines.append(
        "| Problem | Algorithm | Mean Cost | Std Dev | Gap (%) | Mean Time (s) | Speedup |"
    )
    md_lines.append(
        "|:--------|:----------|----------:|--------:|--------:|--------------:|--------:|"
    )

    # LaTeX header with complete document structure
    tex_lines.append("% Chapter 4 Validation Results - Auto-generated")
    tex_lines.append(f"% Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    tex_lines.append("% Compile with: pdflatex chapter4_validation.tex\n")
    tex_lines.append("\\documentclass[11pt,a4paper]{article}")
    tex_lines.append("\\usepackage{booktabs}  % Professional tables")
    tex_lines.append("\\usepackage{multirow}  % Row spanning")
    tex_lines.append("\\usepackage{geometry}  % Page margins")
    tex_lines.append("\\usepackage{caption}   % Better captions")
    tex_lines.append("\\geometry{margin=1in}")
    tex_lines.append("\\captionsetup{font=small,labelfont=bf}\n")
    tex_lines.append(
        "\\title{Chapter 4 Validation: GPU-Accelerated Genetic Algorithm Benchmark}"
    )
    tex_lines.append(f"\\date{{{time.strftime('%B %d, %Y')}}}")
    tex_lines.append("\\author{Automated Benchmark Report}\n")
    tex_lines.append("\\begin{document}")
    tex_lines.append("\\maketitle\n")
    tex_lines.append("\\section{Summary Statistics by Problem}\n")
    tex_lines.append("\\begin{table}[htbp]")
    tex_lines.append("\\centering")
    tex_lines.append(
        "\\caption{Summary Statistics by Problem. Speedup relative to baseline algorithm (HybridNaive when CPU not available).}"
    )
    tex_lines.append("\\label{tab:chapter4_summary}")
    tex_lines.append("\\begin{tabular}{llrrrrr}")
    tex_lines.append("\\toprule")
    tex_lines.append(
        "Problem & Algorithm & Mean Cost & Std Dev & Gap (\\%) & Time (s) & Speedup \\\\"
    )
    tex_lines.append("\\midrule")

    # Universal baseline: HybridNaive (exists for all problem sizes)
    # This ensures consistent speedup interpretation across entire table
    baseline_algorithm = "HybridNaive"
    baseline_times = {}

    for problem in problem_names:
        if baseline_algorithm in all_results[problem]:
            baseline_times[problem] = all_results[problem][baseline_algorithm][
                "mean_time"
            ]
        else:
            # Fallback if baseline doesn't exist (shouldn't happen with HybridNaive)
            first_alg = next(iter(all_results[problem].keys()))
            baseline_times[problem] = all_results[problem][first_alg]["mean_time"]
            logging.warning(
                f"Baseline {baseline_algorithm} not found for {problem}, using {first_alg}"
            )

    # Data rows
    for problem in problem_names:
        # Count actual algorithms for this problem (for multirow)
        algs_in_problem = [
            alg for alg in algorithm_names if alg in all_results[problem]
        ]

        for i, alg in enumerate(algs_in_problem):
            r = all_results[problem][alg]

            # Calculate speedup relative to baseline
            speedup = ""
            if problem in baseline_times:
                if alg == baseline_algorithm:
                    speedup = "—"
                    tex_speedup = "—"
                else:
                    # Guard against division by zero for very fast algorithms
                    if r["mean_time"] < 1e-6:  # < 1 microsecond
                        speedup = "—"  # Display as em dash
                        tex_speedup = "—"
                    else:
                        speedup_val = baseline_times[problem] / r["mean_time"]
                        speedup = f"{speedup_val:.2f}×"
                        tex_speedup = f"{speedup_val:.2f}$\\times$"
            else:
                speedup = "—"
                tex_speedup = "—"

            # Markdown row
            md_lines.append(
                f"| {problem} | {alg} | {r['mean_cost']:.2f} | {r['std_cost']:.2f} | "
                f"{r['mean_gap']:.2f} | {r['mean_time']:.2f} | {speedup} |"
            )

            # LaTeX row
            if i == 0:
                multirow = f"\\multirow{{{len(algs_in_problem)}}}{{*}}{{{problem}}}"
            else:
                multirow = " " * len(problem)  # Empty space, same width

            tex_lines.append(
                f"{multirow:15} & {alg:15} & {r['mean_cost']:9.2f} & {r['std_cost']:7.2f} & "
                f"{r['mean_gap']:7.2f} & {r['mean_time']:8.2f} & {tex_speedup:>12} \\\\"
            )

        # Add separator between problems in LaTeX
        if problem != problem_names[-1]:
            tex_lines.append("\\midrule")

    # Markdown footer
    md_lines.append("")
    md_lines.append(
        f"*Note: Speedup calculated relative to {baseline_algorithm if baseline_algorithm else 'baseline'} (—\ indicates baseline algorithm).*\n"
    )

    # LaTeX footer
    tex_lines.append("\\bottomrule")
    tex_lines.append("\\end{tabular}")
    tex_lines.append("\\vspace{0.5em}")
    tex_lines.append(
        f"{{\\small \\textit{{Note:}} Speedup calculated relative to {baseline_algorithm if baseline_algorithm else 'baseline'}. — indicates baseline algorithm.}}"
    )
    tex_lines.append("\\end{table}")
    tex_lines.append("\\clearpage\n")

    # ========================================================================
    # Table 2: Algorithm Comparison (Mean Across All Problems)
    # ========================================================================

    md_lines.append("## Table 2: Algorithm Performance Comparison (All Problems)\n")
    md_lines.append(
        "| Algorithm | Mean Gap (%) | Std Gap | Mean Time (s) | Std Time | Avg Speedup |"
    )
    md_lines.append(
        "|:----------|-------------:|--------:|--------------:|---------:|------------:|"
    )

    tex_lines.append("\\section{Algorithm Performance Comparison}\n")
    tex_lines.append("\\begin{table}[htbp]")
    tex_lines.append("\\centering")
    tex_lines.append(
        "\\caption{Algorithm Performance Comparison Across All Problems (aggregated statistics)}"
    )
    tex_lines.append("\\label{tab:chapter4_algorithm_comparison}")
    tex_lines.append("\\begin{tabular}{lrrrrr}")
    tex_lines.append("\\toprule")
    tex_lines.append(
        "Algorithm & Mean Gap (\\%) & Std Gap & Mean Time (s) & Std Time & Avg Speedup \\\\"
    )
    tex_lines.append("\\midrule")

    baseline_mean_time = None
    baseline_alg_name = baseline_algorithm if baseline_algorithm else "HybridNaive"
    for alg in algorithm_names:
        all_gaps = []
        all_times = []

        for problem in problem_names:
            if alg in all_results[problem]:
                all_gaps.append(all_results[problem][alg]["mean_gap"])
                all_times.append(all_results[problem][alg]["mean_time"])

        if not all_gaps:
            continue

        mean_gap = np.mean(all_gaps)
        std_gap = np.std(all_gaps)
        mean_time = np.mean(all_times)
        std_time = np.std(all_times)

        if alg == baseline_alg_name:
            baseline_mean_time = mean_time

        speedup_str = ""
        tex_speedup_str = ""
        if alg == baseline_alg_name:
            speedup_str = "—"
            tex_speedup_str = "—"
        elif baseline_mean_time is not None:
            avg_speedup = baseline_mean_time / mean_time
            speedup_str = f"{avg_speedup:.2f}×"
            tex_speedup_str = f"{avg_speedup:.2f}$\\times$"
        else:
            speedup_str = "—"
            tex_speedup_str = "—"

        # Markdown
        md_lines.append(
            f"| {alg} | {mean_gap:.2f} | {std_gap:.2f} | {mean_time:.2f} | "
            f"{std_time:.2f} | {speedup_str} |"
        )

        # LaTeX
        tex_lines.append(
            f"{alg:15} & {mean_gap:8.2f} & {std_gap:7.2f} & {mean_time:8.2f} & "
            f"{std_time:8.2f} & {tex_speedup_str:>12} \\\\"
        )

    tex_lines.append("\\bottomrule")
    tex_lines.append("\\end{tabular}")
    tex_lines.append("\\vspace{0.5em}")
    tex_lines.append(
        f"{{\\small \\textit{{Note:}} Speedup calculated relative to {baseline_alg_name}. — indicates baseline algorithm.}}"
    )
    tex_lines.append("\\end{table}")
    tex_lines.append("\\clearpage\n")

    # ========================================================================
    # Table 3: Best Results Per Problem Size Category
    # ========================================================================

    md_lines.append("\n## Table 3: Best Algorithm by Problem Size\n")
    md_lines.append(
        "| Size Category | Problems | Best Algorithm | Mean Gap (%) | Mean Time (s) |"
    )
    md_lines.append(
        "|---------------|----------|----------------|--------------|---------------|"
    )

    tex_lines.append("\\begin{table}[htbp]")
    tex_lines.append("\\centering")
    tex_lines.append("\\caption{Best Performing Algorithm by Problem Size Category}")
    tex_lines.append("\\label{tab:chapter4_size_categories}")
    tex_lines.append("\\begin{tabular}{lllrr}")
    tex_lines.append("\\toprule")
    tex_lines.append(
        "Size Category & Problems & Best Algorithm & Mean Gap (\\%) & Mean Time (s) \\\\"
    )
    tex_lines.append("\\midrule")

    # Categorize problems by size
    size_categories = {
        "Small (n<100)": [],
        "Medium (100≤n<300)": [],
        "Large (n≥300)": [],
    }

    for problem in problem_names:
        # Get problem size from PROBLEM_SET
        problem_size = next(
            (p["size"] for p in PROBLEM_SET if p["name"] == problem), None
        )
        if problem_size is None:
            continue

        if problem_size < 100:
            size_categories["Small (n<100)"].append(problem)
        elif problem_size < 300:
            size_categories["Medium (100≤n<300)"].append(problem)
        else:
            size_categories["Large (n≥300)"].append(problem)

    for category, problems in size_categories.items():
        if not problems:
            continue

        # Find best algorithm for this category
        best_alg = None
        best_gap = float("inf")
        best_time = 0

        for alg in algorithm_names:
            gaps = []
            times = []
            for prob in problems:
                if alg in all_results[prob]:
                    gaps.append(all_results[prob][alg]["mean_gap"])
                    times.append(all_results[prob][alg]["mean_time"])

            if gaps:
                avg_gap = np.mean(gaps)
                if avg_gap < best_gap:
                    best_gap = avg_gap
                    best_alg = alg
                    best_time = np.mean(times)

        problems_str = ", ".join(problems)

        # Markdown
        md_lines.append(
            f"| {category} | {problems_str} | {best_alg} | {best_gap:.2f} | {best_time:.2f} |"
        )

        # LaTeX - wrap long problem lists
        if len(problems_str) > 60:
            problems_str = problems_str[:57] + "..."
        tex_lines.append(
            f"{category:20} & {problems_str:40} & {best_alg:15} & {best_gap:8.2f} & {best_time:8.2f} \\\\"
        )

    tex_lines.append("\\bottomrule")
    tex_lines.append("\\end{tabular}")
    tex_lines.append("\\vspace{0.5em}")
    tex_lines.append(
        "{\\small \\textit{Note:} Best algorithm determined by lowest mean gap to known optimum.}"
    )
    tex_lines.append("\\end{table}")
    tex_lines.append("\n\\end{document}")

    # ========================================================================
    # Write files
    # ========================================================================

    md_path = tables_dir / f"{benchmark_name}.md"
    tex_path = tables_dir / f"{benchmark_name}.tex"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex_lines))

    logging.info(f"Tables generated:")
    logging.info(f"  Markdown: {md_path}")
    logging.info(f"  LaTeX: {tex_path}")
    logging.info("")


# ============================================================================
# MAIN BENCHMARK FUNCTION
# ============================================================================


def run_comprehensive_benchmark(args):
    """Run comprehensive benchmark on all configured problems and algorithms.

    Args:
        args: Command-line arguments with repetitions and skip_cpu settings
    """
    # Determine which algorithms to run
    selected_algorithms = []
    for alg_name in ALGORITHM_CONFIGS.keys():
        if args.skip_cpu and alg_name == "CPU":
            continue
        selected_algorithms.append(alg_name)

    # Log configuration
    log_benchmark_configuration(args, selected_algorithms)

    # Setup checkpoint system
    ensure_checkpoint_dirs()

    # Database path (adjusted for benchmarks/ directory)
    db_path = Path(__file__).parent.parent.parent / "datasets" / "routing.duckdb"

    # Check for existing progress
    completed, total = count_completed_checkpoints(
        PROBLEM_SET, selected_algorithms, args.repetitions
    )
    if completed > 0:
        logging.info(f"\n✓ Found {completed}/{total} completed checkpoints")
        logging.info("  Resuming from previous run...\n")

    # Results storage: problem -> algorithm -> metrics
    problem_results = {}

    # Main benchmark loop: Problems × Algorithms (with checkpointing)
    for prob_idx, problem_config in enumerate(PROBLEM_SET, 1):
        problem_name = problem_config["name"]
        optimal_cost = problem_config["optimal"]
        problem_size = problem_config["size"]

        logging.info("\n" + "=" * 80)
        logging.info(f"PROBLEM {prob_idx}/{len(PROBLEM_SET)}: {problem_name}")
        logging.info(f"Size: {problem_size} cities | Optimal: {optimal_cost}")
        logging.info("=" * 80)

        # Determine which algorithms to run for this problem
        # For small problems (n≤100): run selected algorithms (may exclude CPU if --skip-cpu)
        # For large problems (n>100): skip CPU (prohibitive runtime)
        if problem_size <= BENCHMARK_PARAMS["cpu_size_threshold"]:
            problem_algorithms = selected_algorithms
            logging.info(
                f"Running {len(problem_algorithms)} algorithm(s) (n≤{BENCHMARK_PARAMS['cpu_size_threshold']})\n"
            )
        else:
            problem_algorithms = [
                a for a in selected_algorithms if ALGORITHM_CONFIGS[a]["use_gpu"]
            ]
            logging.info(
                f"Running {len(problem_algorithms)} GPU algorithms only (n>{BENCHMARK_PARAMS['cpu_size_threshold']})\n"
            )

        # Initialize results for this problem
        problem_results[problem_name] = {}

        # Load problem once for all algorithms
        try:
            with DatabaseLoader(str(db_path)) as loader:
                problem = loader.load(problem_name)
        except Exception as e:
            logging.error(f"Failed to load {problem_name}: {e}")
            continue

        max_generations = adaptive_generations(problem_size)
        customers = list(range(problem_size))

        # Run each algorithm on this problem
        for algo_idx, alg_name in enumerate(problem_algorithms, 1):
            alg_config = ALGORITHM_CONFIGS[alg_name]
            backend_type = "GPU" if alg_config["use_gpu"] else "CPU"

            # Check for existing checkpoint
            checkpoint_path = get_checkpoint_path(problem_name, alg_name)
            if is_valid_checkpoint(checkpoint_path, args.repetitions):
                logging.info(
                    f"  [{algo_idx}/{len(problem_algorithms)}] {alg_name} ({backend_type}): "
                    f"✓ Loading from checkpoint"
                )
                problem_results[problem_name][alg_name] = load_checkpoint(
                    checkpoint_path
                )

                # CRITICAL: Cleanup GPU memory even when loading from checkpoint
                # Prevents memory leak accumulation across resumed problems
                if alg_config["use_gpu"]:
                    cp.get_default_memory_pool().free_all_blocks()

                continue

            # Run algorithm
            logging.info(
                f"  [{algo_idx}/{len(problem_algorithms)}] {alg_name} ({backend_type}): "
                f"Running {args.repetitions} repetitions..."
            )

            # Create algorithm instance
            algorithm_instance = alg_config["class"](**GA_PARAMS)

            # Run benchmark
            results = run_single_algorithm(
                alg_name,
                algorithm_instance,
                problem,
                problem_name,
                problem_size,
                customers,
                max_generations,
                optimal_cost,
                args.repetitions,
                alg_config["use_gpu"],
            )

            # ENHANCE CHECKPOINT WITH METADATA
            results["problem_name"] = problem_name
            results["problem_size"] = problem_size
            results["optimal_cost"] = optimal_cost
            results["max_generations_configured"] = max_generations  # Configured limit
            # Note: Actual generations completed stored in "mean_generations" and "raw_generations"
            results["backend"] = "GPU" if alg_config["use_gpu"] else "CPU"
            results["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

            # Extract algorithm configuration
            results["algorithm_config"] = {
                "population_size": getattr(
                    algorithm_instance,
                    "population_size",
                    GA_PARAMS.get("population_size"),
                ),
                "mutation_rate": getattr(
                    algorithm_instance, "mutation_rate", GA_PARAMS.get("mutation_rate")
                ),
                "tournament_size": getattr(
                    algorithm_instance,
                    "tournament_size",
                    GA_PARAMS.get("tournament_size"),
                ),
                "two_opt_iterations": getattr(
                    algorithm_instance,
                    "two_opt_iterations",
                    GA_PARAMS.get("two_opt_iterations"),
                ),
                "seed": getattr(algorithm_instance, "seed", GA_PARAMS.get("seed")),
            }

            # Strategy information
            results["strategies"] = {
                "selection": getattr(
                    algorithm_instance.selection,
                    "__class__.__name__",
                    "TournamentSelection",
                )
                if hasattr(algorithm_instance, "selection")
                else "TournamentSelection",
                "crossover": getattr(
                    algorithm_instance.crossover, "__class__.__name__", "OrderCrossover"
                )
                if hasattr(algorithm_instance, "crossover")
                else "OrderCrossover",
                "mutation": getattr(
                    algorithm_instance.mutation, "__class__.__name__", "SwapMutation"
                )
                if hasattr(algorithm_instance, "mutation")
                else "SwapMutation",
            }

            # Construction heuristic (assuming nearest neighbor, can be extracted if available)
            results["construction_heuristic"] = "random_initialization"

            # SAVE CHECKPOINT IMMEDIATELY (fault tolerance)
            save_checkpoint_atomic(checkpoint_path, results)
            problem_results[problem_name][alg_name] = results

            # Cleanup algorithm instance
            del algorithm_instance
            gc.collect()
            if alg_config["use_gpu"]:
                cp.get_default_memory_pool().free_all_blocks()

        # GENERATE AND LOG PER-PROBLEM STATISTICS IMMEDIATELY
        logging.info(f"\n{'─' * 80}")
        logging.info(f"STATISTICS FOR {problem_name}")
        logging.info(f"{'─' * 80}")
        statistical_test_results = perform_statistical_analysis(
            problem_name, optimal_cost, problem_results[problem_name]
        )

        # Save problem statistics to file
        stats_path = get_problem_stats_path(problem_name)
        try:
            # Compute summary statistics for each algorithm
            problem_stats = {
                "problem_info": {
                    "name": problem_name,
                    "size": problem_size,
                    "optimal_cost": optimal_cost,
                },
                "algorithms": {},
                "statistical_tests": statistical_test_results,
            }

            for alg_name, results in problem_results[problem_name].items():
                # Handle both checkpoint format (raw_*) and direct format (*)
                times = np.array(results.get("raw_times", results.get("times", [])))
                initial_costs = np.array(
                    results.get("raw_initial_costs", results.get("initial_costs", []))
                )
                costs = np.array(
                    results.get("raw_costs", results.get("final_costs", []))
                )
                gaps = np.array(results.get("raw_gaps", results.get("gaps", [])))
                generations = np.array(
                    results.get("raw_generations", results.get("generations", []))
                )

                valid_mask = ~np.isnan(times)
                problem_stats["algorithms"][alg_name] = {
                    "mean_time": float(np.nanmean(times)),
                    "std_time": float(np.nanstd(times)),
                    "mean_initial_cost": float(np.nanmean(initial_costs)),
                    "std_initial_cost": float(np.nanstd(initial_costs)),
                    "mean_cost": float(np.nanmean(costs)),
                    "std_cost": float(np.nanstd(costs)),
                    "mean_gap": float(np.nanmean(gaps)),
                    "std_gap": float(np.nanstd(gaps)),
                    "mean_generations": float(np.nanmean(generations)),
                    "std_generations": float(np.nanstd(generations)),
                    "success_rate": float(np.sum(valid_mask) / len(times))
                    if len(times) > 0
                    else 0.0,
                    "backend": results.get("backend", "unknown"),
                    "algorithm_config": results.get("algorithm_config", {}),
                    "strategies": results.get("strategies", {}),
                }

            with open(stats_path, "w", encoding="utf-8") as f:
                json.dump(problem_stats, f, indent=2)
            logging.info(f"✓ Problem statistics saved: {stats_path.name}\n")
        except Exception as e:
            logging.warning(f"Failed to save problem statistics: {e}\n")

        # Cleanup problem
        del problem
        gc.collect()

    # Final cross-problem analysis
    logging.info("\n" + "=" * 80)
    logging.info("CROSS-PROBLEM ANALYSIS")
    logging.info("=" * 80)

    if len(problem_results) > 1:
        perform_cross_problem_analysis(problem_results)

    # Generate and export final tables
    generate_result_tables(problem_results, "chapter4_validation")

    logging.info(SEPARATOR)
    logging.info("BENCHMARK COMPLETE")
    logging.info(SEPARATOR)

    return problem_results


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Chapter 4 Validation: Comprehensive ISO-Algorithmic GA Benchmark"
    )
    parser.add_argument(
        "--skip-cpu",
        action="store_true",
        default=BENCHMARK_PARAMS["skip_cpu_default"],
        help=f"Skip CPU variant (default: {BENCHMARK_PARAMS['skip_cpu_default']})",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=BENCHMARK_PARAMS["repetitions"],
        help=f"Number of repetitions per algorithm (default: {BENCHMARK_PARAMS['repetitions']})",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        default=False,
        help="Run on first 2 problems only for testing (default: False, runs all 38 problems)",
    )

    args = parser.parse_args()

    # Setup logging early
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Set problem set based on test mode
    global PROBLEM_SET
    PROBLEM_SET = PROBLEM_SET_FULL[:2] if args.test_mode else PROBLEM_SET_FULL

    if args.test_mode:
        logging.info("=" * 80)
        logging.info("⚠️  TEST MODE ENABLED")
        logging.info("=" * 80)
        logging.info("Running on first 2 problems only (eil51, berlin52)")
        logging.info("Use without --test-mode for full 38-problem benchmark")
        logging.info("=" * 80)
        logging.info("")

    # Run benchmark
    run_comprehensive_benchmark(args)


if __name__ == "__main__":
    main()
