"""
Integration tests for Simulated Annealing metaheuristic.

These tests validate SA behavior with various problem configurations,
parameter settings, and verify protocol compliance.
"""

import pytest
import numpy as np
from dataclasses import dataclass
from typing import Optional

from src.algorithms.metaheuristics import SimulatedAnnealing
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
    """Create small random TSP problem."""
    np.random.seed(seed)
    coords = np.random.rand(n, 2) * 100
    coords[0] = [0, 0]

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


class TestSimulatedAnnealingProtocol:
    """Test protocol compliance."""

    def test_protocol_methods_exist(self):
        """Test that all required protocol methods exist."""
        sa = SimulatedAnnealing()
        assert hasattr(sa, "set_params")
        assert hasattr(sa, "build_tour_with_stats")
        assert hasattr(sa, "get_stats")

    def test_set_params(self):
        """Test hyperparameter configuration."""
        sa = SimulatedAnnealing()
        sa.set_params(initial_temp=2000, max_iterations=500)

        assert sa._hyperparams["initial_temp"] == 2000
        assert sa._hyperparams["max_iterations"] == 500

    def test_build_tour_returns_correct_structure(self):
        """Test that build_tour_with_stats returns (tour, stats)."""
        problem = create_test_problem(8)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        sa = SimulatedAnnealing()
        sa.set_params(max_iterations=10)

        result = sa.build_tour_with_stats(context, customers)

        assert isinstance(result, tuple)
        assert len(result) == 2
        tour, stats = result
        assert isinstance(tour, list)
        assert isinstance(stats, dict)

    def test_get_stats_returns_copy(self):
        """Test that get_stats returns a copy, not reference."""
        problem = create_test_problem(8)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        sa = SimulatedAnnealing()
        sa.set_params(max_iterations=10)

        _, stats1 = sa.build_tour_with_stats(context, customers)
        stats2 = sa.get_stats()

        # Modify stats2
        stats2["best_fitness"] = -999

        # Original should be unchanged
        stats3 = sa.get_stats()
        assert stats3["best_fitness"] != -999


class TestSimulatedAnnealingNeighborMethods:
    """Test neighbor generation methods."""

    @pytest.mark.parametrize("method", ["2-opt", "swap", "insertion"])
    def test_neighbor_method(self, method):
        """Test each neighbor generation method."""
        problem = create_test_problem(10)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        sa = SimulatedAnnealing()
        sa.set_params(max_iterations=50, neighbor_method=method, initial_temp=500)

        tour, stats = sa.build_tour_with_stats(context, customers)

        # Validate tour
        assert tour[0] == 0
        assert tour[-1] == 0
        assert len(tour) == problem.dimension + 1
        assert len(set(tour[:-1])) == problem.dimension

        # Validate statistics
        assert "best_fitness" in stats
        assert stats["iterations"] > 0


class TestSimulatedAnnealingCoolingSchedules:
    """Test cooling schedules."""

    @pytest.mark.parametrize("schedule", ["geometric", "linear", "adaptive"])
    def test_cooling_schedule(self, schedule):
        """Test each cooling schedule."""
        problem = create_test_problem(10)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        sa = SimulatedAnnealing()
        sa.set_params(max_iterations=50, schedule=schedule, initial_temp=500)

        tour, stats = sa.build_tour_with_stats(context, customers)

        # Validate temperature schedule
        temp_sched = stats["temperature_schedule"]
        assert len(temp_sched) > 0
        assert temp_sched[0] == 500  # Initial temp
        assert temp_sched[-1] < temp_sched[0]  # Temperature decreased


class TestSimulatedAnnealingStatistics:
    """Test statistics tracking."""

    def test_required_statistics_present(self):
        """Test that all required statistics are present."""
        problem = create_test_problem(8)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        sa = SimulatedAnnealing()
        sa.set_params(max_iterations=20)

        _, stats = sa.build_tour_with_stats(context, customers)

        # Required keys from TspMetaheuristicStrategy protocol
        assert "best_fitness" in stats
        assert "final_fitness" in stats
        assert "iterations" in stats
        assert "convergence_history" in stats
        assert "runtime_seconds" in stats
        assert "hyperparameters" in stats

    def test_optional_statistics_present(self):
        """Test that optional SA-specific statistics are present."""
        problem = create_test_problem(8)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        sa = SimulatedAnnealing()
        sa.set_params(max_iterations=20)

        _, stats = sa.build_tour_with_stats(context, customers)

        # SA-specific optional keys
        assert "temperature_schedule" in stats
        assert "acceptance_rate" in stats

    def test_convergence_history_length(self):
        """Test that convergence history has correct length."""
        problem = create_test_problem(8)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        max_iter = 30
        sa = SimulatedAnnealing()
        sa.set_params(max_iterations=max_iter, min_temp=0.01)

        _, stats = sa.build_tour_with_stats(context, customers)

        # History should have iterations + 1 (initial + per iteration)
        history = stats["convergence_history"]
        assert len(history) == stats["iterations"] + 1


class TestSimulatedAnnealingBehavior:
    """Test algorithm behavior and correctness."""

    def test_maintains_or_improves_solution(self):
        """Test that SA maintains or improves initial solution."""
        problem = create_test_problem(12)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        sa = SimulatedAnnealing()
        sa.set_params(max_iterations=100, initial_temp=1000)

        _, stats = sa.build_tour_with_stats(context, customers)

        history = stats["convergence_history"]
        initial_cost = history[0]
        best_cost = stats["best_fitness"]

        # Best should be <= initial (maintained or improved)
        assert best_cost <= initial_cost

    def test_higher_iterations_improve_quality(self):
        """Test that more iterations generally improve solution quality."""
        problem = create_test_problem(15, seed=100)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        # Few iterations
        np.random.seed(42)
        sa_few = SimulatedAnnealing()
        sa_few.set_params(max_iterations=20)
        _, stats_few = sa_few.build_tour_with_stats(context, customers)

        # Many iterations
        np.random.seed(42)
        sa_many = SimulatedAnnealing()
        sa_many.set_params(max_iterations=200)
        _, stats_many = sa_many.build_tour_with_stats(context, customers)

        # More iterations should give same or better result
        # (Not guaranteed but highly likely)
        assert (
            stats_many["best_fitness"] <= stats_few["best_fitness"] + 10
        )  # Small tolerance


class TestSimulatedAnnealingEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_customers_raises_error(self):
        """Test that empty customers list raises ValueError."""
        problem = create_test_problem(5)
        context = ProblemContext(problem, xp=np)

        sa = SimulatedAnnealing()

        with pytest.raises(ValueError, match="cannot be empty"):
            sa.build_tour_with_stats(context, [])

    def test_single_customer_handled_correctly(self):
        """Test that single customer case is handled."""
        problem = create_test_problem(2)  # Only depot and 1 customer
        context = ProblemContext(problem, xp=np)
        customers = [1]

        sa = SimulatedAnnealing()
        sa.set_params(max_iterations=10)

        tour, stats = sa.build_tour_with_stats(context, customers)

        # Tour should be [0, 1, 0]
        assert tour == [0, 1, 0]
        assert stats["best_fitness"] > 0
