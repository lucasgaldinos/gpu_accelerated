"""
Quick test script for Simulated Annealing implementation.

This script verifies that the SA implementation:
1. Satisfies the TspMetaheuristicStrategy protocol
2. Works with all neighbor generation methods
3. Works with all cooling schedules
4. Produces valid tours and statistics
"""

import sys
import numpy as np

# Add project root to path
sys.path.insert(0, "/home/lucas_galdino/TCC-name_to_define/gpu_accelerated")

from dataclasses import dataclass
from typing import Optional
from src.algorithms.metaheuristics import SimulatedAnnealing
from src.protocols.problem_context import ProblemContext


@dataclass(frozen=True)
class Problem:
    """Minimal Problem dataclass for testing."""

    name: str
    dimension: int
    problem_type: str
    edge_type: str
    coordinates: Optional[np.ndarray]
    distances: Optional[np.ndarray]
    capacity: Optional[int] = None
    demands: Optional[np.ndarray] = None


def create_test_problem(n: int = 10) -> Problem:
    """Create small random TSP problem for testing."""
    np.random.seed(42)
    coords = np.random.rand(n, 2) * 100
    coords[0] = [0, 0]  # Depot at origin

    # Compute Euclidean distances
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


def test_protocol_compliance():
    """Test that SA satisfies TspMetaheuristicStrategy protocol."""
    print("=" * 60)
    print("TEST 1: Protocol Compliance")
    print("=" * 60)

    sa = SimulatedAnnealing()

    # Check required methods exist
    assert hasattr(sa, "set_params"), "Missing set_params method"
    assert hasattr(sa, "build_tour_with_stats"), "Missing build_tour_with_stats method"
    assert hasattr(sa, "get_stats"), "Missing get_stats method"

    # Check methods are callable
    assert callable(sa.set_params), "set_params is not callable"
    assert callable(sa.build_tour_with_stats), "build_tour_with_stats is not callable"
    assert callable(sa.get_stats), "get_stats is not callable"

    print("✅ All required methods present and callable")
    print()


def test_neighbor_methods():
    """Test all three neighbor generation methods."""
    print("=" * 60)
    print("TEST 2: Neighbor Generation Methods")
    print("=" * 60)

    problem = create_test_problem(8)
    context = ProblemContext(problem, xp=np)
    customers = list(range(1, problem.dimension))

    methods = ["2-opt", "swap", "insertion"]

    for method in methods:
        print(f"\nTesting {method} method...")
        sa = SimulatedAnnealing()
        sa.set_params(max_iterations=100, neighbor_method=method, initial_temp=500)

        tour, stats = sa.build_tour_with_stats(context, customers)

        # Validate tour structure
        assert tour[0] == 0, f"{method}: Tour doesn't start at depot"
        assert tour[-1] == 0, f"{method}: Tour doesn't end at depot"
        assert len(tour) == problem.dimension + 1, f"{method}: Wrong tour length"
        assert len(set(tour[:-1])) == problem.dimension, f"{method}: Duplicate nodes"

        # Validate statistics
        assert "best_fitness" in stats, f"{method}: Missing best_fitness"
        assert "final_fitness" in stats, f"{method}: Missing final_fitness"
        assert "iterations" in stats, f"{method}: Missing iterations"
        assert "convergence_history" in stats, f"{method}: Missing convergence_history"

        print(f"  ✅ {method}: Best cost = {stats['best_fitness']:.2f}")
        print(f"     Iterations = {stats['iterations']}")
        print(f"     Acceptance rate = {stats['acceptance_rate']:.2%}")

    print("\n✅ All neighbor methods working correctly")
    print()


def test_cooling_schedules():
    """Test all three cooling schedules."""
    print("=" * 60)
    print("TEST 3: Cooling Schedules")
    print("=" * 60)

    problem = create_test_problem(8)
    context = ProblemContext(problem, xp=np)
    customers = list(range(1, problem.dimension))

    schedules = ["geometric", "linear", "adaptive"]

    for schedule in schedules:
        print(f"\nTesting {schedule} schedule...")
        sa = SimulatedAnnealing()
        sa.set_params(max_iterations=100, schedule=schedule, initial_temp=500)

        tour, stats = sa.build_tour_with_stats(context, customers)

        # Validate temperature schedule
        assert "temperature_schedule" in stats, f"{schedule}: Missing temp schedule"
        temp_sched = stats["temperature_schedule"]
        assert len(temp_sched) > 0, f"{schedule}: Empty temp schedule"
        assert temp_sched[0] == 500, f"{schedule}: Wrong initial temp"
        assert temp_sched[-1] < temp_sched[0], f"{schedule}: Temp didn't decrease"

        print(f"  ✅ {schedule}: Final temp = {temp_sched[-1]:.4f}")
        print(f"     Best cost = {stats['best_fitness']:.2f}")
        print(f"     Runtime = {stats['runtime_seconds']:.3f}s")

    print("\n✅ All cooling schedules working correctly")
    print()


def test_convergence():
    """Test that SA improves solution over iterations."""
    print("=" * 60)
    print("TEST 4: Convergence Behavior")
    print("=" * 60)

    problem = create_test_problem(15)
    context = ProblemContext(problem, xp=np)
    customers = list(range(1, problem.dimension))

    sa = SimulatedAnnealing()
    sa.set_params(
        max_iterations=500,
        initial_temp=1000,
        cooling_rate=0.95,
        neighbor_method="2-opt",
    )

    tour, stats = sa.build_tour_with_stats(context, customers)

    # Check convergence
    history = stats["convergence_history"]
    initial_cost = history[0]

    print(f"\nInitial solution cost: {initial_cost:.2f}")
    print(f"Best solution cost: {stats['best_fitness']:.2f}")
    print(f"Final solution cost: {stats['final_fitness']:.2f}")
    print(
        f"Improvement: {initial_cost - stats['best_fitness']:.2f} ({100 * (initial_cost - stats['best_fitness']) / initial_cost:.1f}%)"
    )
    print(f"Total iterations: {stats['iterations']}")
    print(f"Acceptance rate: {stats['acceptance_rate']:.2%}")
    print(f"Runtime: {stats['runtime_seconds']:.3f}s")

    # Verify improvement
    assert stats["best_fitness"] <= initial_cost, (
        "SA didn't maintain or improve initial solution"
    )

    print("\n✅ Convergence behavior validated")
    print()


def test_statistics_retrieval():
    """Test get_stats() method returns correct copy."""
    print("=" * 60)
    print("TEST 5: Statistics Retrieval")
    print("=" * 60)

    problem = create_test_problem(8)
    context = ProblemContext(problem, xp=np)
    customers = list(range(1, problem.dimension))

    sa = SimulatedAnnealing()
    sa.set_params(max_iterations=50)

    tour, stats1 = sa.build_tour_with_stats(context, customers)
    stats2 = sa.get_stats()

    # Verify stats are equal
    assert stats1["best_fitness"] == stats2["best_fitness"], "Stats don't match"
    assert stats1["iterations"] == stats2["iterations"], "Iterations don't match"

    # Verify it's a copy (not reference)
    stats2["best_fitness"] = -999
    stats3 = sa.get_stats()
    assert stats3["best_fitness"] != -999, (
        "get_stats() returns reference instead of copy"
    )

    print("✅ get_stats() returns correct copy")
    print()


def run_all_tests():
    """Run all SA tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "SIMULATED ANNEALING TEST SUITE" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    try:
        test_protocol_compliance()
        test_neighbor_methods()
        test_cooling_schedules()
        test_convergence()
        test_statistics_retrieval()

        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 17 + "ALL TESTS PASSED" + " " * 24 + "║")
        print("╚" + "=" * 58 + "╝")
        print()
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
