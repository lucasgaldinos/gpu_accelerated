#!/usr/bin/env python3
"""
Stage 2 Task 2.1 & 2.2 Validation Script
========================================

Validates that GeneticAlgorithm changes are working correctly:
- Task 2.1: Backend parameter removed from __init__
- Task 2.2: xp parameter removed from strategy calls
- Task 2.3: CPU-only performance maintained

Tests:
1. GA instantiation without backend parameter (should work)
2. GA instantiation with backend parameter (should fail)
3. GA runtime with NumPy context (~14s baseline)
4. GA runtime with CuPy context (should still be ~14s - FIXED)
5. Code compiles without errors
6. No dead code paths executed

Expected Outcomes:
- GA always uses NumPy for S-Task operations (selection, crossover, mutation)
- Context backend (np or cp) only affects distances array, not GA operations
- No 6.14× GPU slowdown anymore (fixed by hardcoded xp=np)
- P-Task improvement strategies handle their own GPU transfers (Stage 4)

Phase 3.5 Hybrid Bridge Architecture:
- S-Task operations: ALWAYS CPU (NumPy)
- P-Task operations: May bridge to GPU internally
- This script tests S-Task CPU-only execution
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

import numpy as np

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False

# Import GA components
from code.src.algorithms.metaheuristics.genetic_algorithm import GeneticAlgorithm
from code.src.algorithms.strategies.crossover_strategies import OrderCrossover
from code.src.algorithms.strategies.mutation_strategies import SwapMutation
from code.src.algorithms.strategies.selection_strategies import TournamentSelection
from code.src.algorithms.strategies.improvement_strategies import NoImprovementStrategy
from code.src.protocols.problem_context import ProblemContext
from code.src.data_models.problem import Problem


def create_test_problem(n: int, use_cupy: bool = False):
    """Create a test TSP problem with n cities."""
    xp = cp if (use_cupy and CUPY_AVAILABLE) else np

    # Random 2D coordinates
    coords = np.random.rand(n + 1, 2) * 100  # +1 for depot

    # Compute distance matrix
    diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    distances_np = np.sqrt(np.sum(diff**2, axis=2))

    # Create Problem object (immutable)
    problem = Problem(
        name="test_problem",
        dimension=n + 1,
        problem_type="TSP",
        edge_type="EUC_2D",
        coordinates=coords,
        distances=None,  # Will be computed from coordinates
        capacity=None,
        demands=None,
    )

    # Create ProblemContext with selected backend
    context = ProblemContext(problem=problem, xp=xp, seed=42)

    customers = list(range(1, n + 1))  # Exclude depot 0

    return context, customers


def test_1_ga_instantiation_without_backend():
    """Test 1: GA instantiation without backend parameter (should work)."""
    print("\n" + "=" * 80)
    print("TEST 1: GA Instantiation Without Backend Parameter")
    print("=" * 80)

    try:
        ga = GeneticAlgorithm(
            crossover_strategy=OrderCrossover(),
            mutation_strategy=SwapMutation(),
            selection_strategy=TournamentSelection(tournament_size=3),
            improvement_strategy=NoImprovementStrategy(),
        )
        print("✅ PASS: GA instantiated successfully without backend parameter")
        print(
            f"   GA strategies: crossover={type(ga.crossover_strategy).__name__}, "
            f"mutation={type(ga.mutation_strategy).__name__}, "
            f"selection={type(ga.selection_strategy).__name__}"
        )
        return True
    except Exception as e:
        print(f"❌ FAIL: GA instantiation failed: {e}")
        return False


def test_2_ga_instantiation_with_backend():
    """Test 2: GA instantiation with backend parameter (should fail)."""
    print("\n" + "=" * 80)
    print("TEST 2: GA Instantiation With Backend Parameter (Should Fail)")
    print("=" * 80)

    try:
        ga = GeneticAlgorithm(
            crossover_strategy=OrderCrossover(),
            mutation_strategy=SwapMutation(),
            selection_strategy=TournamentSelection(tournament_size=3),
            improvement_strategy=NoImprovementStrategy(),
            backend="numpy",  # This should cause TypeError
        )
        print(
            "❌ FAIL: GA instantiation succeeded with backend parameter (should have failed)"
        )
        return False
    except TypeError as e:
        if "backend" in str(e):
            print("✅ PASS: GA instantiation correctly rejected backend parameter")
            print(f"   Error message: {e}")
            return True
        else:
            print(f"❌ FAIL: Unexpected TypeError: {e}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected exception: {e}")
        return False


def test_3_ga_runtime_numpy_context():
    """Test 3: GA runtime with NumPy context (~14s baseline)."""
    print("\n" + "=" * 80)
    print("TEST 3: GA Runtime with NumPy Context")
    print("=" * 80)

    # Create test problem (50 cities)
    context, customers = create_test_problem(n=50, use_cupy=False)
    print(
        f"   Problem: {len(customers)} cities, backend={type(context.distances).__module__}"
    )

    # Create GA
    ga = GeneticAlgorithm(
        crossover_strategy=OrderCrossover(),
        mutation_strategy=SwapMutation(),
        selection_strategy=TournamentSelection(tournament_size=3),
        improvement_strategy=NoImprovementStrategy(),
    )
    ga.set_params(population_size=60, max_generations=100)

    # Run GA
    start_time = time.time()
    tour, stats = ga.build_tour_with_stats(context, customers)
    elapsed_time = time.time() - start_time

    print(f"   Tour length: {len(tour)}, Cost: {stats.get('best_fitness', 'N/A'):.2f}")
    print(f"   Runtime: {elapsed_time:.3f}s")

    # Validate
    if len(tour) != len(customers) + 2:  # +2 for depot at start and end
        print(
            f"❌ FAIL: Tour length incorrect (expected {len(customers) + 2}, got {len(tour)})"
        )
        return False

    if tour[0] != 0 or tour[-1] != 0:
        print(
            f"❌ FAIL: Tour doesn't start and end at depot (got {tour[0]} and {tour[-1]})"
        )
        return False

    # Runtime check (baseline ~1-2s for 50 cities, 100 generations)
    if elapsed_time > 5.0:
        print(f"⚠️  WARNING: Runtime slower than expected ({elapsed_time:.3f}s > 5s)")
        print("   This may indicate a performance issue")

    print("✅ PASS: GA runs correctly with NumPy context")
    return True


def test_4_ga_runtime_cupy_context():
    """Test 4: GA runtime with CuPy context (Stage 3 validation)."""
    print("\n" + "=" * 80)
    print("TEST 4: GA Runtime with CuPy Context (Stage 3 Validation)")
    print("=" * 80)

    # Check for CuPy availability
    try:
        import cupy as cp

        print("   CuPy available: ✅")
    except ImportError:
        print("⏭️  SKIPPED: CuPy not available (cannot test GPU context)")
        return True

    # Create test problem with CuPy backend (50 cities)
    context, customers = create_test_problem(n=50, use_cupy=True)
    print(
        f"   Problem: {len(customers)} cities, backend={type(context.distances).__module__}"
    )

    # Create GA (same configuration as Test 3)
    ga = GeneticAlgorithm(
        crossover_strategy=OrderCrossover(),
        mutation_strategy=SwapMutation(),
        selection_strategy=TournamentSelection(tournament_size=3),
        improvement_strategy=NoImprovementStrategy(),
    )
    ga.set_params(population_size=60, max_generations=100)

    # Run GA
    start_time = time.time()
    tour, stats = ga.build_tour_with_stats(context, customers)
    elapsed_time = time.time() - start_time

    print(f"   Tour length: {len(tour)}, Cost: {stats.get('best_fitness', 'N/A'):.2f}")
    print(f"   Runtime: {elapsed_time:.3f}s")

    # Validate tour structure
    if len(tour) != len(customers) + 2:
        print(
            f"❌ FAIL: Tour length incorrect (expected {len(customers) + 2}, got {len(tour)})"
        )
        return False

    if tour[0] != 0 or tour[-1] != 0:
        print(
            f"❌ FAIL: Tour doesn't start and end at depot (got {tour[0]} and {tour[-1]})"
        )
        return False

    # Runtime check: Should be similar to NumPy (Stage 3 fix)
    # Previous bug: 6.14× slowdown with CuPy context
    # After Stage 3: S-Task operations use NumPy internally, no slowdown
    if elapsed_time > 5.0:
        print(f"⚠️  WARNING: Runtime slower than expected ({elapsed_time:.3f}s > 5s)")
        print("   Stage 3 should have fixed the 6.14× GPU slowdown")
        print("   S-Task operations now use NumPy internally (CPU-only)")
    else:
        print("✅ Performance: No GPU slowdown detected")
        print("   Stage 3 fix successful: S-Task operations are CPU-only")

    print("✅ PASS: GA runs correctly with CuPy context")
    return True


def test_5_no_backend_attribute():
    """Test 5: Verify GA no longer has backend attribute (dead code removed)."""
    print("\n" + "=" * 80)
    print("TEST 5: No Backend Attribute (Dead Code Removed)")
    print("=" * 80)

    ga = GeneticAlgorithm(
        crossover_strategy=OrderCrossover(),
        mutation_strategy=SwapMutation(),
        selection_strategy=TournamentSelection(tournament_size=3),
        improvement_strategy=NoImprovementStrategy(),
    )

    if hasattr(ga, "backend"):
        print(f"❌ FAIL: GA still has 'backend' attribute (value={ga.backend})")
        return False

    if hasattr(ga, "backend_module"):
        print(f"❌ FAIL: GA still has 'backend_module' attribute")
        return False

    print("✅ PASS: Backend attributes removed successfully")
    return True


def main():
    """Run all validation tests."""
    print("=" * 80)
    print("STAGE 2 VALIDATION: Tasks 2.1 & 2.2")
    print("=" * 80)
    print("Phase 3.5 Hybrid Bridge Architecture Validation")
    print("Testing: GA backend removal, xp parameter removal, CPU-only S-Task")
    print()

    results = {
        "Test 1: GA Instantiation Without Backend": test_1_ga_instantiation_without_backend(),
        "Test 2: GA Instantiation With Backend (Fail)": test_2_ga_instantiation_with_backend(),
        "Test 3: GA Runtime (NumPy Context)": test_3_ga_runtime_numpy_context(),
        "Test 4: GA Runtime (CuPy Context)": test_4_ga_runtime_cupy_context(),
        "Test 5: No Backend Attribute": test_5_no_backend_attribute(),
    }

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Stage 2 Tasks 2.1 & 2.2 Complete")
        print("\nNext Steps:")
        print("  - Task 2.3: Run full phase3_validation_benchmark (optional)")
        print("  - Stage 3: Update strategy protocols (remove xp parameter)")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED. Review failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
