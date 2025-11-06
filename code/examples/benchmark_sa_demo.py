"""
Example: Benchmark SA CPU vs GPU on berlin52.

Demonstrates complete workflow:
1. Configure benchmark
2. Execute multi-run experiment
3. Perform statistical analysis
4. Generate report

Run: python -m code.examples.benchmark_sa_demo
"""

import numpy as np
from pathlib import Path

# Add project root to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.benchmarking import (
    BenchmarkConfig,
    BenchmarkRunner,
    StatisticalAnalyzer,
    ReportGenerator,
)
from src.data_models.problem import Problem
from src.protocols.problem_context import ProblemContext, CUPY_AVAILABLE
from src.algorithms.metaheuristics.simulated_annealing import SimulatedAnnealing


def main():
    """Run benchmark demo."""
    print("\n" + "=" * 70)
    print("Benchmark Demo: Simulated Annealing CPU vs GPU")
    print("=" * 70 + "\n")

    # Create simple test problem (berlin52-like)
    print("Creating test problem (10 cities)...")
    np.random.seed(42)
    coordinates = np.random.rand(10, 2) * 100  # 10 random cities
    problem = Problem(
        name="demo_10cities",
        dimension=10,
        problem_type="TSP",
        edge_type="EUC_2D",
        coordinates=coordinates,
        distances=None,
        capacity=None,
        demands=None,
    )

    # CPU benchmark
    print("\n--- CPU Benchmark ---")
    cpu_config = BenchmarkConfig(
        algorithm="SA",
        backend="numpy",
        instance_name="demo_10cities",
        num_repetitions=5,  # Small for demo
        time_budget=5.0,  # 5 seconds
        algorithm_params={
            "initial_temperature": 100.0,
            "cooling_rate": 0.95,
            "neighbor_method": "2-opt",
        },
    )

    context_cpu = ProblemContext(problem, xp=np)
    runner = BenchmarkRunner()

    cpu_results = list(
        runner.run_benchmark(cpu_config, context_cpu, SimulatedAnnealing, verbose=True)
    )

    # Export CPU results
    output_dir = Path("data/benchmarks/demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    runner.export_csv(cpu_results, output_dir / "sa_cpu_demo.csv")

    # GPU benchmark (if available)
    gpu_results = None
    if CUPY_AVAILABLE:
        import cupy as cp

        print("\n--- GPU Benchmark ---")
        gpu_config = BenchmarkConfig(
            algorithm="SA",
            backend="cupy",
            instance_name="demo_10cities",
            num_repetitions=5,
            time_budget=5.0,
            algorithm_params=cpu_config.algorithm_params,  # Same params
        )

        context_gpu = ProblemContext(problem, xp=cp)
        gpu_results = list(
            runner.run_benchmark(
                gpu_config, context_gpu, SimulatedAnnealing, verbose=True
            )
        )
        runner.export_csv(gpu_results, output_dir / "sa_gpu_demo.csv")
    else:
        print("\n[SKIP] GPU benchmark (CuPy not available)")

    # Statistical analysis
    if gpu_results is not None:
        print("\n--- Statistical Analysis ---")
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # Extract runtimes
        cpu_times = np.array([r.runtime_seconds for r in cpu_results])
        gpu_times = np.array([r.runtime_seconds for r in gpu_results])

        # Paired comparison
        summary = analyzer.paired_comparison(
            cpu_times,
            gpu_times,
            label="SA: demo_10cities",
            metric_name="runtime_seconds",
        )

        print(f"\nSample size: {summary.sample_size}")
        print(f"CPU mean: {summary.mean_a:.3f}s (±{summary.std_a:.3f})")
        print(f"GPU mean: {summary.mean_b:.3f}s (±{summary.std_b:.3f})")
        print(f"Speedup: {summary.get_speedup():.2f}x")
        print(f"p-value: {summary.p_value:.4f}")
        print(f"Effect size (Cohen's d): {summary.effect_size:.2f}")
        print(f"Test used: {summary.test_used}")
        print(f"Data is normal: {summary.is_normal}")

        # Generate report
        print("\n--- Report ---")
        reporter = ReportGenerator()
        print(reporter.format_markdown_table([summary], show_speedup=True))
        print()
        print(reporter.summary_statistics([summary]))
    else:
        print("\n[SKIP] Statistical analysis (no GPU results)")

    print("\n" + "=" * 70)
    print("Demo complete!")
    print(f"Results saved to: {output_dir}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
