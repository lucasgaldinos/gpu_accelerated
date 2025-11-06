"""
GPU-specific integration tests for Simulated Annealing.

Tests verify that SA runs correctly on CuPy backend and produces
valid results. These tests validate Milestone 3's Class P-Data refactoring.

Classification: Integration Tests
Dependencies: CuPy (optional), ProblemContext, SimulatedAnnealing
"""

import pytest
import numpy as np
from dataclasses import dataclass
from typing import Optional, List

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False

from src.protocols.problem_context import ProblemContext
from src.algorithms.metaheuristics.simulated_annealing import SimulatedAnnealing


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


def create_test_problem_gpu(n: int, seed: int = 42) -> Problem:
    """Create small random TSP problem for GPU testing."""
    np.random.seed(seed)
    coords = np.random.rand(n, 2) * 100
    coords[0] = [0, 0]

    distances = np.sqrt(
        ((coords[:, np.newaxis] - coords[np.newaxis, :]) ** 2).sum(axis=2)
    )

    return Problem(
        name=f"gpu_test_{n}",
        dimension=n,
        problem_type="TSP",
        edge_type="EUC_2D",
        coordinates=coords,
        distances=distances,
    )


@pytest.mark.skipif(not CUPY_AVAILABLE, reason="CuPy not available")
class TestSimulatedAnnealingGPU:
    """Test SA with CuPy backend (Class P-Data validation)."""

    @pytest.fixture
    def gpu_context(self):
        """Create test problem context with GPU backend."""
        problem = create_test_problem_gpu(6)  # 6-city problem
        return ProblemContext(problem, xp=cp)

    def test_sa_runs_on_gpu(self, gpu_context):
        """Verify SA executes on GPU without errors."""
        sa = SimulatedAnnealing()
        sa.set_params(
            initial_temp=500,
            max_iterations=100,  # Small for fast test
            neighbor_method="2-opt",
        )

        customers = list(range(1, gpu_context.problem.dimension))
        tour, _ = sa.build_tour_with_stats(gpu_context, customers)

        # Verify valid tour structure
        assert len(tour) == len(customers) + 2  # depot + customers + depot
        assert tour[0] == 0  # starts at depot
        assert tour[-1] == 0  # ends at depot
        assert set(tour[1:-1]) == set(customers)  # visits all customers

    def test_gpu_produces_reasonable_solutions(self, gpu_context):
        """Verify GPU results are within expected quality range."""
        sa = SimulatedAnnealing()
        sa.set_params(initial_temp=1000, max_iterations=500, neighbor_method="2-opt")

        customers = list(range(1, gpu_context.problem.dimension))
        tour, _ = sa.build_tour_with_stats(gpu_context, customers)

        stats = sa.get_stats()

        # Check tour is valid
        tour_cost = self._compute_tour_cost(tour, gpu_context.distances)
        assert tour_cost == pytest.approx(stats["best_fitness"], rel=1e-6)

        # Acceptance rate should be reasonable
        assert 0.0 <= stats["acceptance_rate"] <= 1.0

    def test_gpu_cpu_equivalence(self):
        """Verify GPU and CPU produce equivalent quality results."""
        # Same problem on CPU and GPU
        problem = create_test_problem_gpu(6, seed=123)

        cpu_context = ProblemContext(problem, xp=np)
        gpu_context = ProblemContext(problem, xp=cp)

        # Same hyperparameters for deterministic comparison
        params = {
            "initial_temp": 800,
            "max_iterations": 200,
            "neighbor_method": "2-opt",
            "cooling_rate": 0.95,
        }

        customers = list(range(1, problem.dimension))

        # CPU run
        sa_cpu = SimulatedAnnealing()
        sa_cpu.set_params(**params)
        tour_cpu, _ = sa_cpu.build_tour_with_stats(cpu_context, customers)
        cost_cpu = self._compute_tour_cost(tour_cpu, cpu_context.distances)

        # GPU run
        sa_gpu = SimulatedAnnealing()
        sa_gpu.set_params(**params)
        tour_gpu, _ = sa_gpu.build_tour_with_stats(gpu_context, customers)
        cost_gpu = self._compute_tour_cost(tour_gpu, gpu_context.distances)

        # Both should produce valid tours
        assert len(tour_cpu) == len(tour_gpu) == len(customers) + 2

        # Quality should be in similar range (within 50% due to randomness)
        assert abs(cost_cpu - cost_gpu) / min(cost_cpu, cost_gpu) < 0.5

    def test_all_neighbor_methods_on_gpu(self, gpu_context):
        """Verify all neighbor generation methods work on GPU."""
        methods = ["2-opt", "swap", "insertion"]
        customers = list(range(1, gpu_context.problem.dimension))

        for method in methods:
            sa = SimulatedAnnealing()
            sa.set_params(initial_temp=500, max_iterations=50, neighbor_method=method)

            tour, _ = sa.build_tour_with_stats(gpu_context, customers)

            # Verify valid tour
            assert len(tour) == len(customers) + 2
            assert tour[0] == 0
            assert tour[-1] == 0
            assert set(tour[1:-1]) == set(customers)

    def test_gpu_statistics_computation(self, gpu_context):
        """Verify statistics computation works with CuPy arrays."""
        sa = SimulatedAnnealing()
        sa.set_params(initial_temp=600, max_iterations=150)

        customers = list(range(1, gpu_context.problem.dimension))
        _ = sa.build_tour_with_stats(gpu_context, customers)

        stats = sa.get_stats()

        # All statistics should be Python types, not CuPy arrays
        assert isinstance(stats["best_fitness"], float)
        assert isinstance(stats["final_fitness"], float)
        assert isinstance(stats["runtime_seconds"], float)
        assert isinstance(stats["acceptance_rate"], float)

        # Convergence history should be list of floats
        assert all(isinstance(x, (int, float)) for x in stats["convergence_history"])
        assert all(isinstance(x, (int, float)) for x in stats["temperature_schedule"])

    # ========== Helper Methods ==========

    def _compute_tour_cost(self, tour: List[int], distances) -> float:
        """Compute tour cost (backend-agnostic)."""
        xp = cp.get_array_module(distances)
        tour_array = xp.array(tour)
        edge_costs = distances[tour_array[:-1], tour_array[1:]]
        return float(xp.sum(edge_costs))
