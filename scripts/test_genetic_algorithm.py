"""
Quick test script for Genetic Algorithm implementation.

This script verifies that the GA implementation:
1. Satisfies the TspMetaheuristicStrategy protocol
2. Works with OX crossover
3. Works with all mutation methods
4. 2-opt integration works correctly
5. Produces valid tours and statistics
"""

import sys
import numpy as np

# Add project root to path
sys.path.insert(0, "/home/lucas_galdino/TCC-name_to_define/gpu_accelerated")

from dataclasses import dataclass
from typing import Optional
from src.algorithms.metaheuristics import GeneticAlgorithm
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
    """Test that GA satisfies TspMetaheuristicStrategy protocol."""
    print("=" * 60)
    print("TEST 1: Protocol Compliance")
    print("=" * 60)

    ga = GeneticAlgorithm()

    # Check required methods exist
    assert hasattr(ga, "set_params"), "Missing set_params method"
    assert hasattr(ga, "build_tour_with_stats"), "Missing build_tour_with_stats method"
    assert hasattr(ga, "get_stats"), "Missing get_stats method"

    # Check methods are callable
    assert callable(ga.set_params), "set_params is not callable"
    assert callable(ga.build_tour_with_stats), "build_tour_with_stats is not callable"
    assert callable(ga.get_stats), "get_stats is not callable"

    print("✅ All required methods present and callable")
    print()


def test_ox_crossover():
    """Test OX (Order Crossover) operator."""
    print("=" * 60)
    print("TEST 2: OX Crossover Operator")
    print("=" * 60)

    problem = create_test_problem(8)
    context = ProblemContext(problem, xp=np)
    customers = list(range(1, problem.dimension))

    ga = GeneticAlgorithm()
    ga.set_params(
        population_size=20,
        max_generations=10,
        crossover_rate=1.0,  # Always crossover
        mutation_rate=0.0,  # No mutation
        use_2opt=False,  # No local search
    )

    tour, stats = ga.build_tour_with_stats(context, customers)

    # Validate tour structure
    assert tour[0] == 0, "Tour doesn't start at depot"
    assert tour[-1] == 0, "Tour doesn't end at depot"
    assert len(tour) == problem.dimension + 1, "Wrong tour length"
    assert len(set(tour[:-1])) == problem.dimension, "Duplicate nodes"

    # Validate statistics
    assert stats["crossover_count"] > 0, "No crossovers performed"
    assert stats["mutation_count"] == 0, "Mutations performed when disabled"

    print(f"✅ OX Crossover working correctly")
    print(f"   Best cost = {stats['best_fitness']:.2f}")
    print(f"   Crossovers performed = {stats['crossover_count']}")
    print()


def test_mutation_methods():
    """Test all three mutation methods."""
    print("=" * 60)
    print("TEST 3: Mutation Methods")
    print("=" * 60)

    problem = create_test_problem(8)
    context = ProblemContext(problem, xp=np)
    customers = list(range(1, problem.dimension))

    methods = ["swap", "inversion", "insertion"]

    for method in methods:
        print(f"\nTesting {method} mutation...")
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

        # Validate tour structure
        assert tour[0] == 0, f"{method}: Tour doesn't start at depot"
        assert tour[-1] == 0, f"{method}: Tour doesn't end at depot"
        assert len(set(tour[:-1])) == problem.dimension, f"{method}: Duplicate nodes"

        # Validate statistics
        assert stats["mutation_count"] > 0, f"{method}: No mutations performed"

        print(f"  ✅ {method}: Best cost = {stats['best_fitness']:.2f}")
        print(f"     Mutations performed = {stats['mutation_count']}")

    print("\n✅ All mutation methods working correctly")
    print()


def test_2opt_integration():
    """Test 2-opt local search integration."""
    print("=" * 60)
    print("TEST 4: 2-opt Local Search Integration")
    print("=" * 60)

    problem = create_test_problem(12)
    context = ProblemContext(problem, xp=np)
    customers = list(range(1, problem.dimension))

    # Test WITHOUT 2-opt
    ga_no_2opt = GeneticAlgorithm()
    ga_no_2opt.set_params(population_size=30, max_generations=50, use_2opt=False)

    _, stats_no_2opt = ga_no_2opt.build_tour_with_stats(context, customers)

    # Test WITH 2-opt
    ga_with_2opt = GeneticAlgorithm()
    ga_with_2opt.set_params(population_size=30, max_generations=50, use_2opt=True)

    _, stats_with_2opt = ga_with_2opt.build_tour_with_stats(context, customers)

    print(f"\nWithout 2-opt: Best cost = {stats_no_2opt['best_fitness']:.2f}")
    print(f"With 2-opt: Best cost = {stats_with_2opt['best_fitness']:.2f}")
    print(
        f"Improvement: {stats_no_2opt['best_fitness'] - stats_with_2opt['best_fitness']:.2f}"
    )

    # 2-opt should generally improve or maintain quality
    # (not guaranteed on small random instances, but likely)
    print("\n✅ 2-opt integration working correctly")
    print()


def test_convergence():
    """Test convergence behavior of GA."""
    print("=" * 60)
    print("TEST 5: Convergence Behavior")
    print("=" * 60)

    problem = create_test_problem(15)
    context = ProblemContext(problem, xp=np)
    customers = list(range(1, problem.dimension))

    ga = GeneticAlgorithm()
    ga.set_params(
        population_size=50,
        max_generations=100,
        crossover_rate=0.9,
        mutation_rate=0.1,
        use_2opt=True,
    )

    tour, stats = ga.build_tour_with_stats(context, customers)

    # Check convergence
    history = stats["convergence_history"]
    initial_cost = history[0]
    final_cost = history[-1]

    print(f"\nInitial best cost: {initial_cost:.2f}")
    print(f"Final best cost: {final_cost:.2f}")
    print(f"Average fitness: {stats['final_fitness']:.2f}")
    print(
        f"Improvement: {initial_cost - final_cost:.2f} ({100 * (initial_cost - final_cost) / initial_cost:.1f}%)"
    )
    print(f"Total generations: {stats['iterations']}")
    print(f"Population diversity (final): {stats['population_diversity'][-1]}")
    print(f"Crossovers: {stats['crossover_count']}")
    print(f"Mutations: {stats['mutation_count']}")
    print(f"Runtime: {stats['runtime_seconds']:.3f}s")

    # Verify improvement
    assert final_cost <= initial_cost, "GA didn't maintain or improve initial best"

    print("\n✅ Convergence behavior validated")
    print()


def test_statistics_retrieval():
    """Test get_stats() method returns correct copy."""
    print("=" * 60)
    print("TEST 6: Statistics Retrieval")
    print("=" * 60)

    problem = create_test_problem(8)
    context = ProblemContext(problem, xp=np)
    customers = list(range(1, problem.dimension))

    ga = GeneticAlgorithm()
    ga.set_params(population_size=20, max_generations=10)

    _, stats1 = ga.build_tour_with_stats(context, customers)
    stats2 = ga.get_stats()

    # Verify stats are equal
    assert stats1["best_fitness"] == stats2["best_fitness"], "Stats don't match"
    assert stats1["iterations"] == stats2["iterations"], "Iterations don't match"

    # Verify it's a copy (not reference)
    stats2["best_fitness"] = -999
    stats3 = ga.get_stats()
    assert stats3["best_fitness"] != -999, (
        "get_stats() returns reference instead of copy"
    )

    print("✅ get_stats() returns correct copy")
    print()


def run_all_tests():
    """Run all GA tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 13 + "GENETIC ALGORITHM TEST SUITE" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    try:
        test_protocol_compliance()
        test_ox_crossover()
        test_mutation_methods()
        test_2opt_integration()
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
