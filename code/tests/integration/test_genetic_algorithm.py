"""
Integration tests for Genetic Algorithm metaheuristic.

These tests validate GA behavior with OX crossover, mutation operators,
2-opt integration, and verify protocol compliance.
"""

import pytest
import numpy as np
from dataclasses import dataclass
from typing import Optional

from src.algorithms.metaheuristics import GeneticAlgorithm
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


class TestGeneticAlgorithmProtocol:
    """Test protocol compliance."""

    def test_protocol_methods_exist(self):
        """Test that all required protocol methods exist."""
        ga = GeneticAlgorithm()
        assert hasattr(ga, "set_params")
        assert hasattr(ga, "build_tour_with_stats")
        assert hasattr(ga, "get_stats")

    def test_set_params(self):
        """Test hyperparameter configuration."""
        ga = GeneticAlgorithm()
        ga.set_params(population_size=100, max_generations=500)

        assert ga._hyperparams["population_size"] == 100
        assert ga._hyperparams["max_generations"] == 500

    def test_build_tour_returns_correct_structure(self):
        """Test that build_tour_with_stats returns (tour, stats)."""
        problem = create_test_problem(8)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        ga = GeneticAlgorithm()
        ga.set_params(population_size=20, max_generations=10)

        result = ga.build_tour_with_stats(context, customers)

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

        ga = GeneticAlgorithm()
        ga.set_params(population_size=20, max_generations=10)

        _, stats1 = ga.build_tour_with_stats(context, customers)
        stats2 = ga.get_stats()

        # Modify stats2
        stats2["best_fitness"] = -999

        # Original should be unchanged
        stats3 = ga.get_stats()
        assert stats3["best_fitness"] != -999


class TestGeneticAlgorithmOXCrossover:
    """Test OX (Order Crossover) operator."""

    def test_ox_creates_valid_tours(self):
        """Test that OX produces valid tours."""
        problem = create_test_problem(10)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        ga = GeneticAlgorithm()
        ga.set_params(
            population_size=20,
            max_generations=10,
            crossover_rate=1.0,  # Always crossover
            mutation_rate=0.0,  # No mutation
            use_2opt=False,
        )

        tour, stats = ga.build_tour_with_stats(context, customers)

        # Tour should be valid
        assert tour[0] == 0
        assert tour[-1] == 0
        assert len(tour) == problem.dimension + 1
        assert len(set(tour[:-1])) == problem.dimension

        # Crossovers should have occurred
        assert stats["crossover_count"] > 0

    def test_ox_preserves_genes(self):
        """Test that OX preserves all cities in tour."""
        problem = create_test_problem(12)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        ga = GeneticAlgorithm()
        ga.set_params(
            population_size=30,
            max_generations=20,
            crossover_rate=1.0,
            mutation_rate=0.0,
            use_2opt=False,
        )

        tour, _ = ga.build_tour_with_stats(context, customers)

        # All customers should be in tour exactly once (plus depot twice)
        tour_set = set(tour)
        expected_set = set([0] + customers)
        assert tour_set == expected_set


class TestGeneticAlgorithmMutationOperators:
    """Test mutation operators."""

    @pytest.mark.parametrize("method", ["swap", "inversion", "insertion"])
    def test_mutation_method(self, method):
        """Test each mutation method."""
        problem = create_test_problem(10)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        ga = GeneticAlgorithm()
        ga.set_params(
            population_size=20,
            max_generations=10,
            crossover_rate=0.0,  # No crossover
            mutation_rate=1.0,  # Always mutate
            mutation_method=method,
            use_2opt=False,
        )

        tour, stats = ga.build_tour_with_stats(context, customers)

        # Validate tour
        assert tour[0] == 0
        assert tour[-1] == 0
        assert len(set(tour[:-1])) == problem.dimension

        # Mutations should have occurred
        assert stats["mutation_count"] > 0


class TestGeneticAlgorithm2optIntegration:
    """Test 2-opt local search integration."""

    def test_2opt_can_be_disabled(self):
        """Test that 2-opt can be disabled."""
        problem = create_test_problem(10)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        ga = GeneticAlgorithm()
        ga.set_params(population_size=20, max_generations=10, use_2opt=False)

        tour, _ = ga.build_tour_with_stats(context, customers)

        # Should still produce valid tour
        assert len(tour) == problem.dimension + 1
        assert tour[0] == 0
        assert tour[-1] == 0

    def test_2opt_improves_quality(self):
        """Test that 2-opt generally improves solution quality."""
        problem = create_test_problem(15)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        # Run WITHOUT 2-opt
        np.random.seed(42)
        ga_no_2opt = GeneticAlgorithm()
        ga_no_2opt.set_params(population_size=30, max_generations=30, use_2opt=False)
        _, stats_no_2opt = ga_no_2opt.build_tour_with_stats(context, customers)

        # Run WITH 2-opt
        np.random.seed(42)
        ga_with_2opt = GeneticAlgorithm()
        ga_with_2opt.set_params(population_size=30, max_generations=30, use_2opt=True)
        _, stats_with_2opt = ga_with_2opt.build_tour_with_stats(context, customers)

        # 2-opt should give same or better result
        assert stats_with_2opt["best_fitness"] <= stats_no_2opt["best_fitness"] + 5


class TestGeneticAlgorithmStatistics:
    """Test statistics tracking."""

    def test_required_statistics_present(self):
        """Test that all required statistics are present."""
        problem = create_test_problem(8)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        ga = GeneticAlgorithm()
        ga.set_params(population_size=20, max_generations=20)

        _, stats = ga.build_tour_with_stats(context, customers)

        # Required keys from TspMetaheuristicStrategy protocol
        assert "best_fitness" in stats
        assert "final_fitness" in stats
        assert "iterations" in stats
        assert "convergence_history" in stats
        assert "runtime_seconds" in stats
        assert "hyperparameters" in stats

    def test_optional_statistics_present(self):
        """Test that optional GA-specific statistics are present."""
        problem = create_test_problem(8)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        ga = GeneticAlgorithm()
        ga.set_params(population_size=20, max_generations=20)

        _, stats = ga.build_tour_with_stats(context, customers)

        # GA-specific optional keys
        assert "population_diversity" in stats
        assert "crossover_count" in stats
        assert "mutation_count" in stats

    def test_convergence_history_length(self):
        """Test that convergence history has correct length."""
        problem = create_test_problem(8)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        max_gen = 30
        ga = GeneticAlgorithm()
        ga.set_params(population_size=20, max_generations=max_gen)

        _, stats = ga.build_tour_with_stats(context, customers)

        # History should have max_gen + 1 (initial + per generation)
        history = stats["convergence_history"]
        assert len(history) == max_gen + 1


class TestGeneticAlgorithmBehavior:
    """Test algorithm behavior and correctness."""

    def test_maintains_or_improves_solution(self):
        """Test that GA maintains or improves initial best."""
        problem = create_test_problem(12)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        ga = GeneticAlgorithm()
        ga.set_params(population_size=40, max_generations=50)

        _, stats = ga.build_tour_with_stats(context, customers)

        history = stats["convergence_history"]
        initial_best = history[0]
        final_best = stats["best_fitness"]

        # Final best should be <= initial best
        assert final_best <= initial_best

    def test_population_diversity_decreases(self):
        """Test that population diversity generally decreases over time."""
        problem = create_test_problem(12)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        ga = GeneticAlgorithm()
        ga.set_params(population_size=40, max_generations=100)

        _, stats = ga.build_tour_with_stats(context, customers)

        diversity = stats["population_diversity"]
        initial_diversity = diversity[0]
        final_diversity = diversity[-1]

        # Diversity should generally decrease (convergence)
        # (Not strict guarantee, but highly likely)
        assert final_diversity <= initial_diversity

    def test_larger_population_improves_quality(self):
        """Test that larger population generally improves quality."""
        problem = create_test_problem(15, seed=100)
        context = ProblemContext(problem, xp=np)
        customers = list(range(1, problem.dimension))

        # Small population
        np.random.seed(42)
        ga_small = GeneticAlgorithm()
        ga_small.set_params(population_size=20, max_generations=50)
        _, stats_small = ga_small.build_tour_with_stats(context, customers)

        # Large population
        np.random.seed(42)
        ga_large = GeneticAlgorithm()
        ga_large.set_params(population_size=100, max_generations=50)
        _, stats_large = ga_large.build_tour_with_stats(context, customers)

        # Larger population should give same or better result
        # (Not guaranteed but highly likely)
        assert stats_large["best_fitness"] <= stats_small["best_fitness"] + 20


class TestGeneticAlgorithmEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_customers_raises_error(self):
        """Test that empty customers list raises ValueError."""
        problem = create_test_problem(5)
        context = ProblemContext(problem, xp=np)

        ga = GeneticAlgorithm()

        with pytest.raises(ValueError, match="cannot be empty"):
            ga.build_tour_with_stats(context, [])

    def test_single_customer_handled_correctly(self):
        """Test that single customer case is handled."""
        problem = create_test_problem(2)  # Only depot and 1 customer
        context = ProblemContext(problem, xp=np)
        customers = [1]

        ga = GeneticAlgorithm()
        ga.set_params(population_size=10, max_generations=10)

        tour, stats = ga.build_tour_with_stats(context, customers)

        # Tour should be [0, 1, 0]
        assert tour == [0, 1, 0]
        assert stats["best_fitness"] > 0
