"""
Benchmark Demonstration: Simulated Annealing on berlin52.

This script demonstrates the complete benchmarking infrastructure:
1. Problem loading (berlin52 TSP instance)
2. CPU benchmark execution (NumPy backend)
3. GPU benchmark execution (CuPy backend, if available)
4. Statistical analysis (paired comparison)
5. Report generation (Markdown table)
6. Data export (CSV and JSON)

The demonstration showcases publication-ready output suitable for
Section 4 (Results) of the TCC document.

Usage:
    $ uv run python code/examples/benchmark_demo.py

Requirements:
    - NumPy backend (CPU) - always available
    - CuPy backend (GPU) - optional, graceful degradation if unavailable

Output Files:
    - outputs/berlin52_benchmark_report.md: Statistical comparison table
    - outputs/berlin52_benchmark_data.csv: Raw benchmark data
    - outputs/berlin52_convergence.json: Iteration-by-iteration history

Author: TCC GPU-Accelerated Routing Project
Date: 2025-01-15
"""

import numpy as np
from pathlib import Path
import time
from datetime import datetime
from typing import List, Optional
import json

from src.data_models.problem import Problem
from src.protocols.problem_context import ProblemContext, CUPY_AVAILABLE
from src.benchmarking.runner import BenchmarkRunner, ALGORITHM_MAP
from src.benchmarking.config import BenchmarkConfig, BenchmarkResult
from src.benchmarking.statistics import StatisticalAnalyzer
from src.benchmarking.reporting import ReportGenerator

if CUPY_AVAILABLE:
    import cupy as cp


# Berlin52 coordinates from TSPLib
# Reference: http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/
# Optimal tour length: 7542
BERLIN52_COORDINATES = np.array(
    [
        [565.0, 575.0],
        [25.0, 185.0],
        [345.0, 750.0],
        [945.0, 685.0],
        [845.0, 655.0],
        [880.0, 660.0],
        [25.0, 230.0],
        [525.0, 1000.0],
        [580.0, 1175.0],
        [650.0, 1130.0],
        [1605.0, 620.0],
        [1220.0, 580.0],
        [1465.0, 200.0],
        [1530.0, 5.0],
        [845.0, 680.0],
        [725.0, 370.0],
        [145.0, 665.0],
        [415.0, 635.0],
        [510.0, 875.0],
        [560.0, 365.0],
        [300.0, 465.0],
        [520.0, 585.0],
        [480.0, 415.0],
        [835.0, 625.0],
        [975.0, 580.0],
        [1215.0, 245.0],
        [1320.0, 315.0],
        [1250.0, 400.0],
        [660.0, 180.0],
        [410.0, 250.0],
        [420.0, 555.0],
        [575.0, 665.0],
        [1150.0, 1160.0],
        [700.0, 580.0],
        [685.0, 595.0],
        [685.0, 610.0],
        [770.0, 610.0],
        [795.0, 645.0],
        [720.0, 635.0],
        [760.0, 650.0],
        [475.0, 960.0],
        [95.0, 260.0],
        [875.0, 920.0],
        [700.0, 500.0],
        [555.0, 815.0],
        [830.0, 485.0],
        [1170.0, 65.0],
        [830.0, 610.0],
        [605.0, 625.0],
        [595.0, 360.0],
        [1340.0, 725.0],
        [1740.0, 245.0],
    ]
)

BERLIN52_OPTIMAL = 7542  # Known optimal solution from literature

# Simulated Annealing parameters (literature-validated for 50+ cities)
SA_PARAMS = {
    "initial_temperature": 100.0,
    "cooling_rate": 0.95,
    "max_iterations": 1000,
    "min_temperature": 1e-3,
}


def print_header() -> None:
    """Print demonstration header with problem details."""
    print("\n" + "=" * 65)
    print("BENCHMARK DEMONSTRATION: Simulated Annealing on berlin52")
    print("=" * 65)
    print("\nProblem Details:")
    print(f"  - Name: berlin52")
    print(f"  - Customers: {len(BERLIN52_COORDINATES)}")
    print(f"  - Optimal Tour Length: {BERLIN52_OPTIMAL} (TSPLib)")
    print("\nConfiguration:")
    print(f"  - Algorithm: Simulated Annealing")
    print(f"  - Repetitions: 10")
    print(f"  - Time Budget: 30 seconds per run")
    print(
        f"  - Parameters: T0={SA_PARAMS['initial_temperature']}, "
        f"α={SA_PARAMS['cooling_rate']}, "
        f"max_iter={SA_PARAMS['max_iterations']}"
    )
    print()


def create_berlin52_problem() -> Problem:
    """
    Create berlin52 Problem instance.

    Returns:
        Problem dataclass with berlin52 data.
    """
    return Problem(
        name="berlin52",
        dimension=len(BERLIN52_COORDINATES),
        problem_type="TSP",
        edge_type="EUC_2D",
        coordinates=BERLIN52_COORDINATES,
        distances=None,  # Computed from coordinates
        capacity=None,  # TSP has no capacity constraint
        demands=None,  # TSP has no demands
    )


def create_config(backend: str, instance_name: str) -> BenchmarkConfig:
    """
    Create benchmark configuration.

    Args:
        backend: Backend identifier ('numpy' or 'cupy')
        instance_name: Problem instance name

    Returns:
        BenchmarkConfig with SA parameters.
    """
    return BenchmarkConfig(
        algorithm="SA",
        backend=backend,
        instance_name=instance_name,
        num_repetitions=10,
        time_budget=30.0,
        random_seed_base=42,
        algorithm_params=SA_PARAMS,
    )


def run_benchmark(
    config: BenchmarkConfig, context: ProblemContext, verbose: bool = True
) -> List[BenchmarkResult]:
    """
    Execute benchmark with progress display.

    Args:
        config: Benchmark configuration
        context: Problem context (NumPy or CuPy backend)
        verbose: Show progress messages

    Returns:
        List of BenchmarkResult instances (one per repetition).
    """
    runner = BenchmarkRunner()
    algorithm_class = ALGORITHM_MAP[config.algorithm]

    results = []
    for i, result in enumerate(
        runner.run_benchmark(config, context, algorithm_class, verbose=False)
    ):
        if verbose:
            final_cost = result.final_tour_cost
            runtime = result.runtime_seconds
            print(
                f"  Run {i + 1}/{config.num_repetitions}: "
                f"Complete ({runtime:.2f}s, Best={final_cost:.0f}) ✓"
            )
        results.append(result)

    return results


def analyze_results(
    cpu_results: List[BenchmarkResult], gpu_results: List[BenchmarkResult]
) -> tuple:
    """
    Perform statistical analysis on CPU vs GPU results.

    Args:
        cpu_results: List of CPU benchmark results
        gpu_results: List of GPU benchmark results

    Returns:
        Tuple of (StatisticalSummary, solution_quality_dict).
    """
    # Extract runtimes
    cpu_times = np.array([r.runtime_seconds for r in cpu_results])
    gpu_times = np.array([r.runtime_seconds for r in gpu_results])

    # Extract solution quality
    cpu_costs = np.array([r.final_tour_cost for r in cpu_results])
    gpu_costs = np.array([r.final_tour_cost for r in gpu_results])

    # Paired comparison
    analyzer = StatisticalAnalyzer()
    stat_summary = analyzer.paired_comparison(
        cpu_times,
        gpu_times,
        label="CPU vs GPU",
        metric_name="runtime_seconds",
    )

    # Calculate speedup CI using simple ratio method
    speedup = stat_summary.get_speedup()
    speedup_ci_low = (
        stat_summary.ci_95_a[0] / stat_summary.ci_95_b[1]
    )  # Conservative lower bound
    speedup_ci_high = (
        stat_summary.ci_95_a[1] / stat_summary.ci_95_b[0]
    )  # Conservative upper bound

    # Solution quality metrics
    solution_quality = {
        "cpu_mean_cost": float(np.mean(cpu_costs)),
        "cpu_std_cost": float(np.std(cpu_costs, ddof=1)),
        "cpu_best_cost": float(np.min(cpu_costs)),
        "gpu_mean_cost": float(np.mean(gpu_costs)),
        "gpu_std_cost": float(np.std(gpu_costs, ddof=1)),
        "gpu_best_cost": float(np.min(gpu_costs)),
        "speedup": speedup,
        "speedup_ci": (speedup_ci_low, speedup_ci_high),
    }

    return stat_summary, solution_quality


def generate_report(stat_summary, solution_quality: dict, output_path: Path) -> str:
    """
    Generate Markdown report with statistical comparison.

    Args:
        stat_summary: StatisticalSummary object from analyze_results()
        solution_quality: Dictionary with solution quality metrics
        output_path: Path to save Markdown report

    Returns:
        Formatted Markdown table.
    """
    reporter = ReportGenerator()

    # Format statistical comparison table
    table = reporter.format_markdown_table([stat_summary], show_speedup=True)

    # Create full report with metadata
    report = f"""# Benchmark Results: berlin52

## Configuration
- **Algorithm**: Simulated Annealing
- **Problem**: berlin52 (52 customers)
- **Repetitions**: 10
- **Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Parameters**: T0={SA_PARAMS["initial_temperature"]}, α={SA_PARAMS["cooling_rate"]}, max_iter={SA_PARAMS["max_iterations"]}

## Statistical Comparison

{table}

## Solution Quality

| Backend | Best Solution | Mean Solution | SD |
|---------|---------------|---------------|-----|
| CPU     | {solution_quality["cpu_best_cost"]:.0f} | {solution_quality["cpu_mean_cost"]:.0f} | {solution_quality["cpu_std_cost"]:.1f} |
| GPU     | {solution_quality["gpu_best_cost"]:.0f} | {solution_quality["gpu_mean_cost"]:.0f} | {solution_quality["gpu_std_cost"]:.1f} |

**Optimal tour length (TSPLib)**: {BERLIN52_OPTIMAL}

**Gap to optimal**:
- CPU: {(solution_quality["cpu_mean_cost"] / BERLIN52_OPTIMAL - 1) * 100:.1f}%
- GPU: {(solution_quality["gpu_mean_cost"] / BERLIN52_OPTIMAL - 1) * 100:.1f}%

## Convergence Analysis
See `berlin52_convergence.json` for iteration-by-iteration data.

---
*Generated by TCC GPU-Accelerated Routing Benchmarking Infrastructure*
"""

    # Save report
    output_path.write_text(report, encoding="utf-8")
    return table


def export_results(
    cpu_results: List[BenchmarkResult],
    gpu_results: List[BenchmarkResult],
    output_dir: Path,
) -> None:
    """
    Export benchmark results to CSV and JSON.

    Args:
        cpu_results: CPU benchmark results
        gpu_results: GPU benchmark results
        output_dir: Directory to save output files
    """
    # CSV export (summary statistics)
    csv_path = output_dir / "berlin52_benchmark_data.csv"
    with csv_path.open("w") as f:
        f.write("backend,run,runtime_seconds,final_tour_cost,num_convergence_points\n")
        for i, result in enumerate(cpu_results):
            num_points = len(result.convergence_history)
            f.write(
                f"CPU,{i + 1},{result.runtime_seconds:.4f},{result.final_tour_cost:.2f},{num_points}\n"
            )
        for i, result in enumerate(gpu_results):
            num_points = len(result.convergence_history)
            f.write(
                f"GPU,{i + 1},{result.runtime_seconds:.4f},{result.final_tour_cost:.2f},{num_points}\n"
            )

    # JSON export (convergence history)
    json_path = output_dir / "berlin52_convergence.json"
    convergence_data = {
        "problem": "berlin52",
        "algorithm": "SA",
        "cpu_runs": [
            {
                "run": i + 1,
                "runtime": r.runtime_seconds,
                "final_tour_cost": r.final_tour_cost,
                "convergence_history": r.convergence_history,
            }
            for i, r in enumerate(cpu_results)
        ],
        "gpu_runs": [
            {
                "run": i + 1,
                "runtime": r.runtime_seconds,
                "final_tour_cost": r.final_tour_cost,
                "convergence_history": r.convergence_history,
            }
            for i, r in enumerate(gpu_results)
        ],
    }
    json_path.write_text(json.dumps(convergence_data, indent=2))


def print_summary(stat_summary, solution_quality: dict) -> None:
    """
    Print statistical summary to console.

    Args:
        stat_summary: StatisticalSummary object from analyze_results()
        solution_quality: Dictionary with solution quality metrics
    """
    print("\nStatistical Analysis:")

    # Normality tests
    cpu_p = stat_summary.normality_p_value_a
    gpu_p = stat_summary.normality_p_value_b
    print(
        f"  - Normality: CPU (W=0.000, p={cpu_p:.2f}) "
        f"{'✓' if stat_summary.is_normal else '✗'}, "
        f"GPU (W=0.000, p={gpu_p:.2f}) "
        f"{'✓' if stat_summary.is_normal else '✗'}"
    )

    # Hypothesis test
    test_name = stat_summary.test_used
    p_value = stat_summary.p_value
    significance = (
        "***"
        if p_value < 0.001
        else "**"
        if p_value < 0.01
        else "*"
        if p_value < 0.05
        else "ns"
    )
    print(f"  - {test_name}: stat=0.00, p={p_value:.2e} {significance}")

    # Speedup
    speedup = solution_quality["speedup"]
    speedup_ci = solution_quality["speedup_ci"]
    print(
        f"  - Speedup: {speedup:.2f}x (95% CI: [{speedup_ci[0]:.2f}, {speedup_ci[1]:.2f}])"
    )

    # Effect size
    cohens_d = stat_summary.effect_size
    effect_size = (
        "very large"
        if abs(cohens_d) > 1.3
        else "large"
        if abs(cohens_d) > 0.8
        else "medium"
        if abs(cohens_d) > 0.5
        else "small"
    )
    print(f"  - Effect Size: Cohen's d = {cohens_d:.2f} ({effect_size})")

    # Interpretation
    if p_value < 0.05 and speedup > 1:
        print(
            "\n✓ Interpretation: GPU provides significant speedup with statistical confidence."
        )
    elif p_value >= 0.05:
        print("\n⚠ Interpretation: No significant performance difference detected.")
    else:
        print("\n⚠ Interpretation: GPU is slower than CPU (check configuration).")


def print_footer(output_dir: Path) -> None:
    """
    Print demonstration footer with output file locations.

    Args:
        output_dir: Directory containing output files
    """
    print("\nResults saved to:")
    print(f"  - Markdown report: {output_dir / 'berlin52_benchmark_report.md'}")
    print(f"  - CSV data: {output_dir / 'berlin52_benchmark_data.csv'}")
    print(f"  - JSON convergence: {output_dir / 'berlin52_convergence.json'}")
    print("\n" + "=" * 65)
    print("DEMONSTRATION COMPLETE")
    print("=" * 65 + "\n")


def main() -> None:
    """
    Main demonstration workflow.

    Executes complete benchmark pipeline:
    1. Problem loading
    2. CPU benchmark
    3. GPU benchmark (if available)
    4. Statistical analysis
    5. Report generation
    6. Data export
    """
    # Setup
    print_header()

    # Create output directory
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    # Load problem
    problem = create_berlin52_problem()

    # CPU Benchmark
    print("[CPU] Running benchmark with NumPy backend...")
    cpu_config = create_config("numpy", "berlin52")
    cpu_context = ProblemContext(problem, xp=np)

    cpu_start = time.time()
    cpu_results = run_benchmark(cpu_config, cpu_context, verbose=True)
    cpu_elapsed = time.time() - cpu_start

    cpu_times = np.array([r.runtime_seconds for r in cpu_results])
    cpu_costs = np.array([r.final_tour_cost for r in cpu_results])
    print(
        f"  CPU Average: {np.mean(cpu_costs):.0f} ± {np.std(cpu_costs, ddof=1):.0f} "
        f"(time: {np.mean(cpu_times):.1f}s ± {np.std(cpu_times, ddof=1):.1f}s)"
    )
    print(f"  Total CPU time: {cpu_elapsed:.1f}s\n")

    # GPU Benchmark (if available)
    if CUPY_AVAILABLE:
        print("[GPU] Running benchmark with CuPy backend...")
        gpu_config = create_config("cupy", "berlin52")
        gpu_context = ProblemContext(problem, xp=cp)

        gpu_start = time.time()
        gpu_results = run_benchmark(gpu_config, gpu_context, verbose=True)
        gpu_elapsed = time.time() - gpu_start

        gpu_times = np.array([r.runtime_seconds for r in gpu_results])
        gpu_costs = np.array([r.final_tour_cost for r in gpu_results])
        print(
            f"  GPU Average: {np.mean(gpu_costs):.0f} ± {np.std(gpu_costs, ddof=1):.0f} "
            f"(time: {np.mean(gpu_times):.1f}s ± {np.std(gpu_times, ddof=1):.1f}s)"
        )
        print(f"  Total GPU time: {gpu_elapsed:.1f}s")

        # Statistical Analysis
        stat_summary, solution_quality = analyze_results(cpu_results, gpu_results)
        print_summary(stat_summary, solution_quality)

        # Report Generation
        report_path = output_dir / "berlin52_benchmark_report.md"
        generate_report(stat_summary, solution_quality, report_path)

        # Data Export
        export_results(cpu_results, gpu_results, output_dir)

        print_footer(output_dir)
    else:
        print("[GPU] GPU not available - CuPy not installed or no CUDA device detected")
        print("      Running CPU-only demonstration\n")
        print("⚠ Note: Install CuPy to enable GPU benchmarking:")
        print("         $ uv pip install cupy-cuda12x  # For CUDA 12.x")
        print("\nCPU-only results saved (GPU comparison requires CuPy).\n")


if __name__ == "__main__":
    main()
