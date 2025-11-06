"""
Unit tests for TspMetaheuristicStrategy protocol.

These tests verify the protocol structure and provide examples for
implementations (Genetic Algorithm, Simulated Annealing, etc.).
"""

import pytest
from typing import Protocol
from src.protocols.algorithm_strategies import TspMetaheuristicStrategy


class TestTspMetaheuristicProtocol:
    """Test TspMetaheuristicStrategy protocol structure."""

    def test_protocol_is_defined(self):
        """Test that TspMetaheuristicStrategy protocol exists."""
        assert TspMetaheuristicStrategy is not None
        assert issubclass(TspMetaheuristicStrategy.__class__, type(Protocol))

    def test_protocol_has_set_params(self):
        """Test that protocol requires set_params method."""
        assert hasattr(TspMetaheuristicStrategy, "set_params")
        assert callable(getattr(TspMetaheuristicStrategy, "set_params"))

    def test_protocol_has_build_tour_with_stats(self):
        """Test that protocol requires build_tour_with_stats method."""
        assert hasattr(TspMetaheuristicStrategy, "build_tour_with_stats")
        assert callable(getattr(TspMetaheuristicStrategy, "build_tour_with_stats"))

    def test_protocol_has_get_stats(self):
        """Test that protocol requires get_stats method."""
        assert hasattr(TspMetaheuristicStrategy, "get_stats")
        assert callable(getattr(TspMetaheuristicStrategy, "get_stats"))

    def test_protocol_has_comprehensive_docstring(self):
        """Test that protocol has comprehensive documentation."""
        assert TspMetaheuristicStrategy.__doc__ is not None
        doc = TspMetaheuristicStrategy.__doc__

        # Check for key concepts
        assert "metaheuristic" in doc.lower()
        assert "hyperparameter" in doc.lower()
        assert "statistics" in doc.lower()
        assert "gpu" in doc.lower()

        # Check for algorithm mentions
        assert "genetic" in doc.lower() or "ga" in doc.lower()
        assert "simulated annealing" in doc.lower() or "sa" in doc.lower()

        # Check for examples
        assert "example" in doc.lower()


class MockMetaheuristicStrategy:
    """
    Mock implementation of TspMetaheuristicStrategy for testing.

    This demonstrates the minimal implementation required to satisfy
    the protocol contract.
    """

    def __init__(self):
        self._hyperparams = {"max_iterations": 100}
        self._stats = {}

    def set_params(self, **hyperparameters):
        """Configure hyperparameters."""
        self._hyperparams.update(hyperparameters)

    def build_tour_with_stats(self, context, customers):
        """Build tour with statistics tracking."""
        import time

        start_time = time.time()

        # Simple greedy construction (placeholder)
        tour = [0] + sorted(customers) + [0]

        # Mock statistics
        self._stats = {
            "best_fitness": 1000.0,
            "final_fitness": 1000.0,
            "iterations": self._hyperparams.get("max_iterations", 100),
            "convergence_history": [1000.0],
            "runtime_seconds": time.time() - start_time,
            "hyperparameters": self._hyperparams.copy(),
        }

        return tour, self._stats

    def get_stats(self):
        """Retrieve statistics from last run."""
        return self._stats.copy()


class TestMockImplementation:
    """Test that mock implementation satisfies protocol."""

    def test_mock_satisfies_protocol(self):
        """Test that MockMetaheuristicStrategy implements all required methods."""
        strategy = MockMetaheuristicStrategy()

        # Check all protocol methods exist
        assert hasattr(strategy, "set_params")
        assert hasattr(strategy, "build_tour_with_stats")
        assert hasattr(strategy, "get_stats")

        # Check they're callable
        assert callable(strategy.set_params)
        assert callable(strategy.build_tour_with_stats)
        assert callable(strategy.get_stats)

    def test_mock_set_params(self):
        """Test that set_params configures hyperparameters."""
        strategy = MockMetaheuristicStrategy()

        # Set custom hyperparameters
        strategy.set_params(max_iterations=500, custom_param=42)

        # Verify stored
        assert strategy._hyperparams["max_iterations"] == 500
        assert strategy._hyperparams["custom_param"] == 42

    def test_mock_returns_valid_statistics(self):
        """Test that build_tour_with_stats returns standardized statistics."""
        from src.data_models.problem import Problem
        from src.protocols.problem_context import ProblemContext
        import numpy as np

        # Create minimal problem
        problem = Problem(
            name="test",
            dimension=5,
            problem_type="TSP",
            edge_type="EUC_2D",
            coordinates=np.array([[0, 0], [1, 0], [0, 1], [1, 1], [0.5, 0.5]]),
            distances=None,
        )
        context = ProblemContext(problem, xp=np)

        strategy = MockMetaheuristicStrategy()
        strategy.set_params(max_iterations=50)

        # Build tour
        tour, stats = strategy.build_tour_with_stats(context, [1, 2, 3, 4])

        # Verify tour structure
        assert tour[0] == 0, "Tour should start at depot"
        assert tour[-1] == 0, "Tour should end at depot"
        assert len(tour) == 6, "Tour should have depot + 4 customers + depot"

        # Verify required statistics keys
        required_keys = [
            "best_fitness",
            "final_fitness",
            "iterations",
            "convergence_history",
            "runtime_seconds",
            "hyperparameters",
        ]
        for key in required_keys:
            assert key in stats, f"Statistics missing required key: {key}"

        # Verify statistics types
        assert isinstance(stats["best_fitness"], (int, float))
        assert isinstance(stats["final_fitness"], (int, float))
        assert isinstance(stats["iterations"], int)
        assert isinstance(stats["convergence_history"], list)
        assert isinstance(stats["runtime_seconds"], float)
        assert isinstance(stats["hyperparameters"], dict)

        # Verify iterations matches configured value
        assert stats["iterations"] == 50

    def test_mock_get_stats_returns_copy(self):
        """Test that get_stats() returns a copy (not reference)."""
        from src.data_models.problem import Problem
        from src.protocols.problem_context import ProblemContext
        import numpy as np

        problem = Problem(
            name="test",
            dimension=4,
            problem_type="TSP",
            edge_type="EUC_2D",
            coordinates=np.array([[0, 0], [1, 0], [0, 1], [1, 1]]),
            distances=None,
        )
        context = ProblemContext(problem, xp=np)

        strategy = MockMetaheuristicStrategy()
        _, stats1 = strategy.build_tour_with_stats(context, [1, 2, 3])

        # Get stats twice
        stats2 = strategy.get_stats()
        stats3 = strategy.get_stats()

        # Should be equal but not the same object
        assert stats2 == stats3
        assert stats2 is not stats3, "get_stats() should return a copy"

        # Modifying returned stats should not affect internal state
        stats2["best_fitness"] = 999999
        stats4 = strategy.get_stats()
        assert stats4["best_fitness"] != 999999


class TestProtocolDocumentation:
    """Test protocol documentation completeness."""

    def test_statistics_format_documented(self):
        """Test that statistics dictionary format is documented."""
        doc = TspMetaheuristicStrategy.__doc__

        # Required statistics keys should be documented
        assert "best_fitness" in doc
        assert "final_fitness" in doc
        assert "iterations" in doc
        assert "convergence_history" in doc
        assert "runtime_seconds" in doc
        assert "hyperparameters" in doc

    def test_gpu_acceleration_documented(self):
        """Test that GPU acceleration is documented."""
        doc = TspMetaheuristicStrategy.__doc__

        assert "gpu" in doc.lower()
        assert "cupy" in doc.lower() or "cuda" in doc.lower()
        assert "parallel" in doc.lower()

    def test_algorithm_examples_documented(self):
        """Test that algorithm examples are provided."""
        doc = TspMetaheuristicStrategy.__doc__

        # Should mention specific algorithms
        algorithms = ["genetic", "simulated annealing", "ant colony", "particle swarm"]
        mentions = sum(1 for alg in algorithms if alg in doc.lower())

        assert mentions >= 2, "Should document at least 2 metaheuristic algorithms"
