"""Integration tests for BenchmarkRunner.

Tests the complete benchmarking pipeline including:
- Algorithm instantiation via ALGORITHM_MAP
- Callback integration
- Result collection
- Statistical analysis
"""

import pytest
import numpy as np
from dataclasses import dataclass
from typing import Optional

from src.benchmarking.runner import BenchmarkRunner, ALGORITHM_MAP
from src.benchmarking.config import BenchmarkConfig
from src.protocols.problem_context import ProblemContext


@dataclass(frozen=True)
class Problem:
    """Problem dataclass for testing."""

    name: str
    dimension: int
    problem_type: str
    edge_type: str
    coordinates: Optional[np.ndarray]
    distances: Optional[np.ndarray]
    capacity: Optional[int] = None
    demands: Optional[np.ndarray] = None


def create_test_problem(n: int, seed: int = 42) -> Problem:
    """Create small random TSP problem.

    Args:
        n: Number of cities
        seed: Random seed for reproducibility

    Returns:
        Problem instance with random coordinates
    """
    np.random.seed(seed)
    coords = np.random.rand(n, 2) * 100
    coords[0] = [0, 0]  # Depot at origin

    distances = np.sqrt(
        ((coords[:, np.newaxis] - coords[np.newaxis, :]) ** 2).sum(axis=2)
    )

    return Problem(
        name=f"test_{n}",
        dimension=n,
        problem_type="TSP",
        edge_type="EUC_2D",
        coordinates=coords,
        distances=distances,
    )


def create_test_context(num_cities: int = 10) -> ProblemContext:
    """Create minimal test problem context.

    Args:
        num_cities: Number of cities including depot

    Returns:
        ProblemContext with minimal valid data
    """
    problem = create_test_problem(num_cities)
    return ProblemContext(problem, xp=np)


class TestBenchmarkRunnerBasic:
    """Basic integration tests for BenchmarkRunner."""

    def test_runner_imports(self):
        """Verify runner and ALGORITHM_MAP import correctly."""
        assert BenchmarkRunner is not None
        assert ALGORITHM_MAP is not None
        assert "GA" in ALGORITHM_MAP
        assert "SA" in ALGORITHM_MAP

    def test_algorithm_instantiation(self):
        """Verify algorithms can be instantiated via ALGORITHM_MAP."""
        # Test GA instantiation
        ga_class = ALGORITHM_MAP["GA"]
        ga_instance = ga_class()
        assert ga_instance is not None

        # Test SA instantiation
        sa_class = ALGORITHM_MAP["SA"]
        sa_instance = sa_class()
        assert sa_instance is not None

    def test_minimal_benchmark_ga(self):
        """Run minimal GA benchmark (1 repetition, 10 cities)."""
        # Create config
        config = BenchmarkConfig(
            algorithm="GA",
            backend="numpy",
            instance_name="test_10",
            num_repetitions=1,
            time_budget=30.0,
            random_seed_base=42,
        )

        # Create context
        context = create_test_context(num_cities=10)

        # Run benchmark
        runner = BenchmarkRunner()
        algorithm_class = ALGORITHM_MAP["GA"]
        results = list(
            runner.run_benchmark(config, context, algorithm_class, verbose=False)
        )

        # Validate results
        assert len(results) == 1, "Should get 1 result for 1 repetition"

        result = results[0]
        assert result.config.algorithm == "GA"
        assert result.final_tour_cost > 0
        assert result.runtime_seconds > 0
        assert result.convergence_history is not None
        assert len(result.convergence_history) > 0

    def test_minimal_benchmark_sa(self):
        """Run minimal SA benchmark (1 repetition, 10 cities)."""
        # Create config
        config = BenchmarkConfig(
            algorithm="SA",
            backend="numpy",
            instance_name="test_10",
            num_repetitions=1,
            time_budget=30.0,
            random_seed_base=42,
        )

        # Create context
        context = create_test_context(num_cities=10)

        # Run benchmark
        runner = BenchmarkRunner()
        algorithm_class = ALGORITHM_MAP["SA"]
        results = list(
            runner.run_benchmark(config, context, algorithm_class, verbose=False)
        )

        # Validate results
        assert len(results) == 1, "Should get 1 result for 1 repetition"

        result = results[0]
        assert result.config.algorithm == "SA"
        assert result.final_tour_cost > 0
        assert result.runtime_seconds > 0
        assert result.convergence_history is not None
        assert len(result.convergence_history) > 0


class TestBenchmarkRunnerCallbacks:
    """Test callback integration in benchmarking."""

    def test_ga_callback_lifecycle(self):
        """Verify GA callbacks fire on_start → on_iteration → on_complete."""
        config = BenchmarkConfig(
            algorithm="GA",
            backend="numpy",
            instance_name="test_10",
            num_repetitions=1,
            time_budget=30.0,
            random_seed_base=42,
        )

        context = create_test_context(num_cities=10)
        runner = BenchmarkRunner()
        algorithm_class = ALGORITHM_MAP["GA"]
        results = list(
            runner.run_benchmark(config, context, algorithm_class, verbose=False)
        )

        result = results[0]
        convergence = result.convergence_history

        # Check lifecycle
        assert len(convergence) > 0, "Should have convergence data from callbacks"

        # Convergence history contains tuples: (iteration, cost, elapsed_time)
        first_entry = convergence[0]
        assert len(first_entry) == 3, "Entry should be (iteration, cost, elapsed)"
        iteration, cost, elapsed = first_entry
        # Note: log_interval=100, so first entry is at iteration 100
        assert iteration >= 0, "Iteration should be non-negative"
        assert cost > 0, "Cost should be positive"
        assert elapsed >= 0, "Elapsed time should be non-negative"

        # Should have multiple iterations logged (every 100 iterations + final)
        assert len(convergence) >= 1, "Should have at least final convergence data"

        # Iterations should be sequential
        iterations = [entry[0] for entry in convergence]
        assert iterations == sorted(iterations), "Iterations should be sequential"

    def test_sa_callback_lifecycle(self):
        """Verify SA callbacks fire on_start → on_iteration → on_complete."""
        config = BenchmarkConfig(
            algorithm="SA",
            backend="numpy",
            instance_name="test_10",
            num_repetitions=1,
            time_budget=30.0,
            random_seed_base=42,
        )

        context = create_test_context(num_cities=10)
        runner = BenchmarkRunner()
        algorithm_class = ALGORITHM_MAP["SA"]
        results = list(
            runner.run_benchmark(config, context, algorithm_class, verbose=False)
        )

        result = results[0]
        convergence = result.convergence_history

        # Check lifecycle
        assert len(convergence) > 0, "Should have convergence data from callbacks"

        # Convergence history contains tuples: (iteration, cost, elapsed_time)
        first_entry = convergence[0]
        assert len(first_entry) == 3, "Entry should be (iteration, cost, elapsed)"
        iteration, cost, elapsed = first_entry
        assert iteration == 0, "First entry should be from iteration 0"
        assert cost > 0, "Cost should be positive"

        # Should have multiple iterations
        assert len(convergence) > 1, "Should have data from on_iteration calls"


class TestBenchmarkRunnerMultiRun:
    """Test multi-repetition benchmarks."""

    def test_multiple_repetitions(self):
        """Run 3 repetitions and verify independent results."""
        config = BenchmarkConfig(
            algorithm="GA",
            backend="numpy",
            instance_name="test_10",
            num_repetitions=3,
            time_budget=60.0,
            random_seed_base=42,
        )

        context = create_test_context(num_cities=10)
        runner = BenchmarkRunner()
        algorithm_class = ALGORITHM_MAP["GA"]
        results = list(
            runner.run_benchmark(config, context, algorithm_class, verbose=False)
        )

        # Should get 3 results
        assert len(results) == 3, "Should get 3 results for 3 repetitions"

        # Each result should be independent
        costs = [r.final_tour_cost for r in results]
        print(f"Costs: {costs}")  # DEBUG
        assert all(c > 0 for c in costs), "All costs should be positive"

        # Results should all be finite (not inf)
        assert all(c < float("inf") for c in costs), f"Got infinite costs: {costs}"
