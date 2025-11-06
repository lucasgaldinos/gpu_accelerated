"""
GPU-specific integration tests for Genetic Algorithm.

Tests verify that GA runs correctly on CuPy backend and produces
valid results. These tests validate Milestone 2's Class P-Data refactoring.

Classification: Integration Tests
Dependencies: CuPy (optional), ProblemContext, GeneticAlgorithm
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
from src.algorithms.metaheuristics.genetic_algorithm import GeneticAlgorithm


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
class TestGeneticAlgorithmGPU:
    """Test GA with CuPy backend (Class P-Data validation)."""

    @pytest.fixture
    def gpu_context(self):
        """Create test problem context with GPU backend."""
        problem = create_test_problem_gpu(5)  # Simple 5-city problem
        return ProblemContext(problem, xp=cp)

    def test_ga_runs_on_gpu(self, gpu_context):
        """Verify GA executes on GPU without errors."""
        ga = GeneticAlgorithm()
        ga.set_params(
            population_size=10,  # Small for fast test
            max_generations=5,
            crossover_rate=0.8,
            mutation_rate=0.2,
        )

        customers = list(range(1, gpu_context.problem.dimension))
        tour, _ = ga.build_tour_with_stats(gpu_context, customers)

        # Verify valid tour structure
        assert len(tour) == len(customers) + 2  # depot + customers + depot
        assert tour[0] == 0  # starts at depot
        assert tour[-1] == 0  # ends at depot
        assert set(tour[1:-1]) == set(customers)  # visits all customers

    def test_gpu_produces_reasonable_solutions(self, gpu_context):
        """Verify GPU results are within expected quality range."""
        ga = GeneticAlgorithm()
        ga.set_params(
            population_size=30,
            max_generations=20,
            use_2opt=True,  # Enable local search
        )

        customers = list(range(1, gpu_context.problem.dimension))
        tour, _ = ga.build_tour_with_stats(gpu_context, customers)

        stats = ga.get_stats()

        # Check tour is valid
        tour_cost = self._compute_tour_cost(tour, gpu_context.distances)
        assert tour_cost == pytest.approx(stats["best_fitness"], rel=1e-6)

    def test_gpu_cpu_equivalence(self):
        """Verify GPU and CPU produce equivalent quality results."""
        # Same problem on CPU and GPU
        problem = create_test_problem_gpu(5)

        cpu_context = ProblemContext(problem, xp=np)
        gpu_context = ProblemContext(problem, xp=cp)

        # Same hyperparameters, different random seed
        params = {
            "population_size": 20,
            "max_generations": 10,
            "crossover_rate": 0.7,
            "mutation_rate": 0.1,
        }

        customers = list(range(1, problem.dimension))

        # CPU run
        ga_cpu = GeneticAlgorithm()
        ga_cpu.set_params(**params)
        tour_cpu, _ = ga_cpu.build_tour_with_stats(cpu_context, customers)
        cost_cpu = self._compute_tour_cost(tour_cpu, cpu_context.distances)

        # GPU run
        ga_gpu = GeneticAlgorithm()
        ga_gpu.set_params(**params)
        tour_gpu, _ = ga_gpu.build_tour_with_stats(gpu_context, customers)
        cost_gpu = self._compute_tour_cost(tour_gpu, gpu_context.distances)

        # Both should produce valid tours
        assert len(tour_cpu) == len(tour_gpu) == len(customers) + 2

        # Quality should be in similar range (within 50% due to randomness)
        # This is a loose bound - main goal is to catch catastrophic failures
        assert abs(cost_cpu - cost_gpu) / min(cost_cpu, cost_gpu) < 0.5

    def test_batch_fitness_vectorization(self, gpu_context):
        """Verify vectorized fitness computation works on GPU."""
        ga = GeneticAlgorithm()
        customers = list(range(1, gpu_context.problem.dimension))

        # Create test population
        xp = gpu_context.xp
        population = [
            [0] + list(np.random.permutation(customers)) + [0] for _ in range(5)
        ]

        # Compute batch fitness (should use GPU vectorization)
        fitness = ga._compute_batch_fitness(
            population, gpu_context.distances, gpu_context.xp
        )

        # Verify results
        assert len(fitness) == len(population)
        assert fitness.shape == (5,)  # CuPy array

        # All fitness values should be positive
        assert (fitness > 0).all()

        # Verify matches sequential computation
        for i, tour in enumerate(population):
            expected = ga._compute_tour_cost(tour, gpu_context.distances, xp)
            assert float(fitness[i]) == pytest.approx(expected, rel=1e-6)

    def test_gpu_statistics_computation(self, gpu_context):
        """Verify statistics computation works with CuPy arrays."""
        ga = GeneticAlgorithm()
        ga.set_params(population_size=15, max_generations=10)

        customers = list(range(1, gpu_context.problem.dimension))
        _ = ga.build_tour_with_stats(gpu_context, customers)

        stats = ga.get_stats()

        # All statistics should be Python floats, not CuPy arrays
        assert isinstance(stats["best_fitness"], float)
        assert isinstance(stats["final_fitness"], float)
        assert isinstance(stats["runtime_seconds"], float)

        # Convergence history should be list of floats
        assert all(isinstance(x, float) for x in stats["convergence_history"])

    # ========== Helper Methods ==========

    def _compute_tour_cost(self, tour: List[int], distances) -> float:
        """Compute tour cost (backend-agnostic)."""
        xp = cp.get_array_module(distances)
        tour_array = xp.array(tour)
        edge_costs = distances[tour_array[:-1], tour_array[1:]]
        return float(xp.sum(edge_costs))
