"""
BenchmarkRunner orchestrator for multi-run experiment execution.

Coordinates benchmark execution following Section 3.5 experimental design:
- Multi-run orchestration (30 repetitions)
- Seed management for reproducibility
- Progress tracking with ETA
- Result streaming to avoid memory overflow
"""

import time
import numpy as np
from typing import List, Iterator, Optional
from pathlib import Path

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False

from .config import BenchmarkConfig, BenchmarkResult
from .collectors import MetricsCollector, ConvergenceTracker

# Import algorithm classes for ALGORITHM_MAP
from ..algorithms.metaheuristics.genetic_algorithm import GeneticAlgorithm
from ..algorithms.metaheuristics.simulated_annealing import SimulatedAnnealing


# Algorithm registry for string-based lookup
ALGORITHM_MAP = {
    "GA": GeneticAlgorithm,
    "SA": SimulatedAnnealing,
    # Future: "2opt": TwoOpt, "NN": NearestNeighbor, etc.
}


class BenchmarkRunner:
    """
    Orchestrates benchmark experiment execution.

    Manages repetitions, seed control, and result streaming following
    reproducibility requirements from Section 3.5.4.

    Example:
        >>> from data_models.problem import Problem
        >>> from protocols.problem_context import ProblemContext
        >>> from algorithms.metaheuristics import SimulatedAnnealing
        >>>
        >>> # Load problem
        >>> problem = Problem(...)  # Load from database
        >>> context_cpu = ProblemContext(problem, xp=np)
        >>>
        >>> # Configure benchmark
        >>> config = BenchmarkConfig(
        ...     algorithm="SA",
        ...     backend="numpy",
        ...     instance_name="berlin52",
        ...     num_repetitions=30
        ... )
        >>>
        >>> # Run benchmark
        >>> runner = BenchmarkRunner()
        >>> results = list(runner.run_benchmark(config, context_cpu, SimulatedAnnealing))
        >>>
        >>> # Export results
        >>> runner.export_csv(results, "sa_cpu_berlin52.csv")
    """

    def run_benchmark(
        self,
        config: BenchmarkConfig,
        context: "ProblemContext",
        algorithm_class: type,
        problem_optimal_cost: Optional[float] = None,
        verbose: bool = True,
    ) -> Iterator[BenchmarkResult]:
        """
        Execute benchmark with multiple repetitions.

        Yields results as they complete (streaming to avoid memory overflow).

        Args:
            config: Benchmark configuration
            context: ProblemContext with backend-specific data
            algorithm_class: Algorithm class (e.g., SimulatedAnnealing, GeneticAlgorithm)
            problem_optimal_cost: Known optimal cost for target gap calculation
            verbose: Print progress messages

        Yields:
            BenchmarkResult for each completed run

        Example:
            >>> for result in runner.run_benchmark(config, context, SimulatedAnnealing):
            ...     print(f"Run {result.run_id}: {result.final_tour_cost:.2f}")
        """
        collector = MetricsCollector(config, problem_optimal_cost)

        if verbose:
            print(f"\n{'=' * 70}")
            print(
                f"Benchmark: {config.algorithm} on {config.instance_name} ({config.backend})"
            )
            print(f"Repetitions: {config.num_repetitions}")
            print(f"{'=' * 70}\n")

        for run_id in range(config.num_repetitions):
            # Set seeds for reproducibility
            seed = config.get_run_seed(run_id)
            np.random.seed(seed)
            if config.backend == "cupy" and CUPY_AVAILABLE:
                cp.random.seed(seed)

            # Create tracker
            tracker = collector.create_tracker()

            # Instantiate algorithm with callback
            start_time = time.perf_counter()
            algorithm = algorithm_class(callback=tracker)

            # Set algorithm parameters if provided
            if config.algorithm_params:
                algorithm.set_params(**config.algorithm_params)

            # Extract customers list from problem (exclude depot 0)
            customers = list(range(1, context.problem.dimension))

            # Run algorithm
            try:
                tour, stats = algorithm.build_tour_with_stats(context, customers)
                runtime = time.perf_counter() - start_time
            finally:
                # Always cleanup GPU memory, even on exception
                if config.backend == "cupy" and CUPY_AVAILABLE:
                    cp.get_default_memory_pool().free_all_blocks()

            # Get memory usage
            memory_mb = collector.get_memory_usage_mb(config.backend)

            # Package result
            result = collector.create_result(
                run_id=run_id,
                runtime_seconds=runtime,
                final_tour_cost=stats.get("best_fitness", float("inf")),
                final_tour=tour,
                tracker=tracker,
                memory_peak_mb=memory_mb,
                validation_passed=True,  # TODO: Add validation logic
            )

            if verbose:
                progress = (run_id + 1) / config.num_repetitions * 100
                print(
                    f"[{progress:5.1f}%] Run {run_id + 1:2d}/{config.num_repetitions}: "
                    f"cost={result.final_tour_cost:10.2f}, "
                    f"time={result.runtime_seconds:6.3f}s, "
                    f"mem={result.memory_peak_mb:6.1f}MB"
                )

            yield result

        if verbose:
            print(f"\n{'=' * 70}")
            print("Benchmark complete!")
            print(f"{'=' * 70}\n")

    def export_csv(self, results: List[BenchmarkResult], filepath: Path) -> None:
        """
        Export results to CSV file.

        Creates CSV with columns:
        - run_id, seed, runtime_seconds, final_tour_cost, time_to_target, memory_peak_mb

        Args:
            results: List of BenchmarkResults
            filepath: Output file path

        Example:
            >>> results = list(runner.run_benchmark(config, context, SA))
            >>> runner.export_csv(results, Path("sa_cpu_berlin52.csv"))
        """
        import csv

        if not results:
            return

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(
                [
                    "run_id",
                    "random_seed",
                    "runtime_seconds",
                    "final_tour_cost",
                    "time_to_target",
                    "memory_peak_mb",
                    "validation_passed",
                    "convergence_points",
                ]
            )

            # Data rows
            for result in results:
                writer.writerow(
                    [
                        result.run_id,
                        result.random_seed,
                        result.runtime_seconds,
                        result.final_tour_cost,
                        result.time_to_target
                        if result.time_to_target is not None
                        else "",
                        result.memory_peak_mb,
                        result.validation_passed,
                        len(result.convergence_history),
                    ]
                )

        print(f"Results exported to: {filepath}")

    def export_json(self, results: List[BenchmarkResult], filepath: Path) -> None:
        """
        Export results to JSON file (includes convergence history).

        Args:
            results: List of BenchmarkResults
            filepath: Output file path

        Example:
            >>> runner.export_json(results, Path("sa_cpu_berlin52.json"))
        """
        import json

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "config": results[0].config.to_dict() if results else {},
            "results": [r.to_dict() for r in results],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Results (with convergence history) exported to: {filepath}")
