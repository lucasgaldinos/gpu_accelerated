"""
Unit tests for the Nearest Neighbor construction heuristic.

Tests include:
- Tour validity (permutation checks)
- Small instance verification (burma14, berlin52, st70)
- Edge cases (1-node, 2-node, missing distances)
- Performance (d2103: 2103 nodes in <1 second)
- Determinism (seed-based tie-breaking)
"""

import numpy as np
import pytest

from src.algorithms.construction.nearest_neighbor import nearest_neighbor
from src.algorithms.objectives.tour_cost import compute_tour_cost
from src.loaders.database_loader import DatabaseLoader
from src.data_models.problem import Problem


class TestNearestNeighborTourValidity:
    """Test that generated tours are valid TSP solutions."""

    def test_tour_visits_all_nodes_exactly_once(self):
        """Verify tour is a valid permutation of all nodes."""
        with DatabaseLoader() as loader:
            problem = loader.load("burma14")

        tour = nearest_neighbor(problem, start_node=0)

        # Check all nodes present
        assert len(tour) == problem.dimension
        assert set(tour) == set(range(problem.dimension))

        # Check no duplicates
        assert len(set(tour)) == len(tour)

    def test_tour_starts_at_specified_node(self):
        """Verify tour begins at the requested start node."""
        with DatabaseLoader() as loader:
            problem = loader.load("burma14")

        for start in [0, 5, 13]:
            tour = nearest_neighbor(problem, start_node=start)
            assert tour[0] == start

    def test_tour_is_numpy_array_int32(self):
        """Verify return type is int32 numpy array."""
        with DatabaseLoader() as loader:
            problem = loader.load("berlin52")

        tour = nearest_neighbor(problem)

        assert isinstance(tour, np.ndarray)
        assert tour.dtype == np.int32
        assert tour.ndim == 1

    def test_tour_shape_matches_dimension(self):
        """Verify tour length equals problem dimension."""
        with DatabaseLoader() as loader:
            problem = loader.load("st70")

        tour = nearest_neighbor(problem)
        assert tour.shape == (problem.dimension,)


class TestNearestNeighborSmallInstances:
    """Test correctness on small instances with known characteristics."""

    def test_burma14_produces_reasonable_tour(self):
        """Test NN on burma14 (14 cities in Burma/Myanmar)."""
        with DatabaseLoader() as loader:
            problem = loader.load("burma14")

        tour = nearest_neighbor(problem, start_node=0)
        cost = compute_tour_cost(problem, tour)

        # Optimal tour for burma14: 3,323
        # NN typically 20-30% worse: expect ~4,000-4,500
        # Known NN from node 0: approximately 4,106
        assert 3_500 < cost < 5_000, f"Unexpected cost: {cost}"

    def test_berlin52_produces_reasonable_tour(self):
        """Test NN on berlin52 (52 locations in Berlin)."""
        with DatabaseLoader() as loader:
            problem = loader.load("berlin52")

        tour = nearest_neighbor(problem, start_node=0)
        cost = compute_tour_cost(problem, tour)

        # Optimal tour for berlin52: 7,542
        # NN typically produces ~9,000-10,000
        assert 8_000 < cost < 12_000, f"Unexpected cost: {cost}"

    def test_st70_produces_reasonable_tour(self):
        """Test NN on st70 (70-city problem)."""
        with DatabaseLoader() as loader:
            problem = loader.load("st70")

        tour = nearest_neighbor(problem, start_node=0)
        cost = compute_tour_cost(problem, tour)

        # Optimal tour for st70: 675
        # NN typically 20-30% worse: ~800-900
        assert 700 < cost < 1_100, f"Unexpected cost: {cost}"


class TestNearestNeighborEdgeCases:
    """Test edge cases and error handling."""

    def test_single_node_problem(self):
        """Test behavior with trivial 1-node problem."""
        # Create minimal problem
        distances = np.array([[0.0]], dtype=np.float64)
        problem = Problem(
            name="single_node",
            dimension=1,
            problem_type="TSP",
            edge_type="EXPLICIT",
            coordinates=None,
            distances=distances,
            capacity=None,
            demands=None,
        )

        tour = nearest_neighbor(problem, start_node=0)

        assert len(tour) == 1
        assert tour[0] == 0

        cost = compute_tour_cost(problem, tour)
        assert cost == 0.0

    def test_two_node_problem(self):
        """Test behavior with 2-node problem."""
        distances = np.array([[0.0, 10.0], [10.0, 0.0]], dtype=np.float64)

        problem = Problem(
            name="two_nodes",
            dimension=2,
            problem_type="TSP",
            edge_type="EXPLICIT",
            coordinates=None,
            distances=distances,
            capacity=None,
            demands=None,
        )

        tour = nearest_neighbor(problem, start_node=0)

        assert len(tour) == 2
        assert set(tour) == {0, 1}

        cost = compute_tour_cost(problem, tour)
        assert cost == 20.0  # 0->1 (10) + 1->0 (10)

    def test_raises_on_missing_distances(self):
        """Verify error when problem has no distance matrix."""
        problem = Problem(
            name="no_distances",
            dimension=5,
            problem_type="TSP",
            edge_type="EUC_2D",
            coordinates=np.random.rand(5, 2),
            distances=None,  # Missing
            capacity=None,
            demands=None,
        )

        with pytest.raises(ValueError, match="has no distance matrix"):
            nearest_neighbor(problem)

    def test_raises_on_invalid_start_node(self):
        """Verify error when start_node is out of bounds."""
        with DatabaseLoader() as loader:
            problem = loader.load("burma14")

        # start_node >= dimension
        with pytest.raises(ValueError, match="out of bounds"):
            nearest_neighbor(problem, start_node=14)

        # start_node < 0
        with pytest.raises(ValueError, match="out of bounds"):
            nearest_neighbor(problem, start_node=-1)

    def test_raises_on_wrong_type(self):
        """Verify error when problem is not Problem instance."""
        with pytest.raises(TypeError, match="must be Problem instance"):
            nearest_neighbor({"name": "fake"}, start_node=0)


class TestNearestNeighborDifferentStartNodes:
    """Test that different start nodes produce different tours."""

    def test_different_starts_produce_different_tours(self):
        """Verify tour quality varies with start node."""
        with DatabaseLoader() as loader:
            problem = loader.load("berlin52")

        costs = []
        for start in [0, 10, 25, 40, 51]:
            tour = nearest_neighbor(problem, start_node=start)
            cost = compute_tour_cost(problem, tour)
            costs.append(cost)

        # Different starts should produce different costs
        # (unless very unlucky with geometry)
        assert len(set(costs)) > 1, "All start nodes produced identical cost"


class TestComputeTourCost:
    """Test tour cost calculation function."""

    def test_cost_includes_return_edge(self):
        """Verify cost includes return to start."""
        # Simple 3-node triangle
        distances = np.array(
            [[0.0, 1.0, 2.0], [1.0, 0.0, 3.0], [2.0, 3.0, 0.0]], dtype=np.float64
        )

        problem = Problem(
            name="triangle",
            dimension=3,
            problem_type="TSP",
            edge_type="EXPLICIT",
            coordinates=None,
            distances=distances,
            capacity=None,
            demands=None,
        )

        # Tour: 0 -> 1 -> 2 -> 0
        tour = np.array([0, 1, 2], dtype=np.int32)
        cost = compute_tour_cost(problem, tour)

        # Cost: 0->1 (1) + 1->2 (3) + 2->0 (2) = 6
        assert cost == 6.0

    def test_raises_on_dimension_mismatch(self):
        """Verify error when tour length doesn't match problem."""
        with DatabaseLoader() as loader:
            problem = loader.load("burma14")

        # Wrong length tour
        bad_tour = np.array([0, 1, 2], dtype=np.int32)

        with pytest.raises(ValueError, match="doesn't match problem dimension"):
            compute_tour_cost(problem, bad_tour)


class TestNearestNeighborPerformance:
    """Test performance requirements."""

    @pytest.mark.slow
    def test_performance_on_large_instance(self):
        """Verify NN runs in <1 second for 2000-node instance."""
        import time

        with DatabaseLoader() as loader:
            # d2103 has 2,103 nodes
            problem = loader.load("d2103")

        start_time = time.time()
        tour = nearest_neighbor(problem, start_node=0)
        elapsed = time.time() - start_time

        # Acceptance criteria: <1 second
        assert elapsed < 1.0, f"Took {elapsed:.2f}s, expected <1.0s"

        # Verify correctness
        assert len(tour) == problem.dimension
        assert len(set(tour)) == problem.dimension


class TestNearestNeighborDeterminism:
    """Test deterministic behavior."""

    def test_same_seed_produces_same_tour(self):
        """Verify deterministic tie-breaking with seed."""
        with DatabaseLoader() as loader:
            problem = loader.load("burma14")

        tour1 = nearest_neighbor(problem, start_node=0, seed=42)
        tour2 = nearest_neighbor(problem, start_node=0, seed=42)

        np.testing.assert_array_equal(tour1, tour2)

    def test_different_seeds_may_produce_different_tours(self):
        """Verify different seeds can break ties differently."""
        with DatabaseLoader() as loader:
            problem = loader.load("burma14")

        tour1 = nearest_neighbor(problem, start_node=0, seed=42)
        tour2 = nearest_neighbor(problem, start_node=0, seed=123)

        # May or may not differ (depends on tie occurrences)
        # Just verify both are valid
        assert len(tour1) == len(tour2) == problem.dimension
        assert set(tour1) == set(tour2) == set(range(problem.dimension))
