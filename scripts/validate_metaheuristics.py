#!/usr/bin/env python3
"""
Validation Script for Metaheuristic Algorithms

Validates that Simulated Annealing and Genetic Algorithm implementations
comply with the TspMetaheuristicStrategy protocol.

Usage:
    uv run python scripts/validate_metaheuristics.py
"""

import sys
from pathlib import Path

# Add code to path for imports
code_path = Path(__file__).parent.parent / "code"
sys.path.insert(0, str(code_path))

import numpy as np
from src.algorithms.metaheuristics import SimulatedAnnealing, GeneticAlgorithm


def validate_protocol_compliance(algorithm_class, algorithm_name: str) -> bool:
    """
    Validate that an algorithm class implements TspMetaheuristicStrategy.

    Args:
        algorithm_class: The algorithm class to validate
        algorithm_name: Name for reporting

    Returns:
        True if compliant, False otherwise
    """
    print(f"\n{'=' * 60}")
    print(f"Validating {algorithm_name}")
    print(f"{'=' * 60}")

    # Check protocol compliance
    required_methods = ["set_params", "build_tour_with_stats", "get_stats"]

    for method_name in required_methods:
        if not hasattr(algorithm_class, method_name):
            print(f"❌ Missing method: {method_name}")
            return False
        print(f"✅ Has method: {method_name}")

    # Instantiate and test basic functionality
    try:
        algo = algorithm_class()
        print(f"✅ Can instantiate {algorithm_name}")
    except Exception as e:
        print(f"❌ Cannot instantiate: {e}")
        return False

    # Test set_params
    try:
        if algorithm_name == "SimulatedAnnealing":
            algo.set_params(initial_temp=500.0, max_iterations=100)
        else:  # GeneticAlgorithm
            algo.set_params(population_size=30, max_generations=50)
        print(f"✅ set_params() works")
    except Exception as e:
        print(f"❌ set_params() failed: {e}")
        return False

    # Test build_tour_with_stats with tiny problem
    try:
        # Create tiny TSP problem: depot + 2 customers
        # Customers are represented as indices (1, 2)
        customers = [1, 2]

        # Minimal context with distance matrix
        class MinimalContext:
            def __init__(self):
                self.xp = np
                self.depot = np.array([0.0, 0.0])
                self.distance_matrix = np.array(
                    [[0.0, 1.0, 1.0], [1.0, 0.0, 1.414], [1.0, 1.414, 0.0]]
                )

            def get_cpu_distances(self):
                return self.distance_matrix

            def get_gpu_distances(self):
                return self.distance_matrix

        context = MinimalContext()
        tour, stats = algo.build_tour_with_stats(context, customers)

        # Validate tour structure
        assert isinstance(tour, list), "Tour must be a list"
        assert tour[0] == 0 and tour[-1] == 0, "Tour must start and end at depot"
        assert len(tour) == 4, f"Tour length should be 4, got {len(tour)}"
        print(f"✅ build_tour_with_stats() returns valid tour: {tour}")

        # Validate statistics
        required_stats = [
            "best_fitness",
            "final_fitness",
            "iterations",
            "convergence_history",
            "runtime_seconds",
            "hyperparameters",
        ]
        for stat_key in required_stats:
            assert stat_key in stats, f"Missing required stat: {stat_key}"
        print(f"✅ Statistics contain all required keys")

        # Check specific optional stats
        if algorithm_name == "SimulatedAnnealing":
            assert "temperature_schedule" in stats, (
                "SA should have temperature_schedule"
            )
            assert "acceptance_rate" in stats, "SA should have acceptance_rate"
            print(f"✅ SA-specific statistics present")
        else:  # GeneticAlgorithm
            assert "population_diversity" in stats, (
                "GA should have population_diversity"
            )
            assert "crossover_count" in stats, "GA should have crossover_count"
            assert "mutation_count" in stats, "GA should have mutation_count"
            print(f"✅ GA-specific statistics present")

    except Exception as e:
        print(f"❌ build_tour_with_stats() failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Test get_stats
    try:
        stats_copy = algo.get_stats()
        assert isinstance(stats_copy, dict), "get_stats() must return dict"
        print(f"✅ get_stats() returns dictionary copy")
    except Exception as e:
        print(f"❌ get_stats() failed: {e}")
        return False

    print(f"\n✅ {algorithm_name} FULLY COMPLIANT with TspMetaheuristicStrategy\n")
    return True


def main():
    """Run validation for both metaheuristic algorithms."""
    print("\n" + "=" * 60)
    print("METAHEURISTIC PROTOCOL VALIDATION")
    print("=" * 60)

    results = {}

    # Validate Simulated Annealing
    results["SA"] = validate_protocol_compliance(
        SimulatedAnnealing, "SimulatedAnnealing"
    )

    # Validate Genetic Algorithm
    results["GA"] = validate_protocol_compliance(GeneticAlgorithm, "GeneticAlgorithm")

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Simulated Annealing: {'✅ PASS' if results['SA'] else '❌ FAIL'}")
    print(f"Genetic Algorithm:   {'✅ PASS' if results['GA'] else '❌ FAIL'}")
    print("=" * 60)

    # Exit code
    if all(results.values()):
        print("\n✅ ALL VALIDATIONS PASSED\n")
        return 0
    else:
        print("\n❌ SOME VALIDATIONS FAILED\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
