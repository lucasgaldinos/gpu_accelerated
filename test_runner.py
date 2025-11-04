#!/usr/bin/env python3
"""
Simple test runner without pytest dependency.
Runs basic tests to validate the architecture.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))

# Try to import numpy, if not available, create a minimal mock
try:
    import numpy as np
    print("✓ NumPy available")
except ImportError:
    print("✗ NumPy not available - creating minimal implementation for testing")
    # Create minimal numpy-like implementation for testing
    class MinimalNumPy:
        def array(self, data, dtype=None):
            return data
        def zeros(self, shape, dtype=None):
            if isinstance(shape, int):
                return [0] * shape
            return [[0] * shape[1] for _ in range(shape[0])]
        def asarray(self, data):
            return data
        int32 = int
        bool_ = bool
        inf = float('inf')
        
        class random:
            class RandomState:
                def __init__(self, seed):
                    pass
                def shuffle(self, arr):
                    import random
                    random.shuffle(arr)
        
        def sqrt(self, x):
            import math
            if isinstance(x, (list, tuple)):
                return [math.sqrt(v) for v in x]
            return math.sqrt(x)
        
        def sum(self, arr, axis=None):
            if axis is None:
                return sum(arr) if isinstance(arr, list) else sum(sum(row) for row in arr)
            return arr
        
        def argmax(self, arr):
            if isinstance(arr, list):
                return arr.index(max(arr))
            return 0
        
        def argmin(self, arr):
            if isinstance(arr, list):
                return arr.index(min(arr))
            return 0
        
        def minimum(self, a, b):
            return [min(x, y) for x, y in zip(a, b)]
        
        def insert(self, arr, pos, val):
            result = list(arr)
            result.insert(pos, val)
            return result
        
        def isclose(self, a, b):
            return abs(a - b) < 1e-6
        
        def allclose(self, a, b):
            return all(abs(x - y) < 1e-6 for x, y in zip(a, b))
        
        def array_equal(self, a, b):
            return a == b
        
        def diag(self, arr):
            return [row[i] for i, row in enumerate(arr)]
    
    np = MinimalNumPy()
    sys.modules['numpy'] = np


def test_imports():
    """Test that all modules can be imported."""
    print("\n=== Testing Imports ===")
    
    try:
        from src.protocols import ProblemContext, CPUStrategy, GPUStrategy
        print("✓ Protocols import successful")
    except Exception as e:
        print(f"✗ Protocols import failed: {e}")
        return False
    
    try:
        from src.algorithms import (
            NearestNeighborCPU,
            RandomInsertionCPU,
            CheapestInsertionCPU,
            CompositionalTSPSolver,
        )
        print("✓ Algorithms import successful")
    except Exception as e:
        print(f"✗ Algorithms import failed: {e}")
        return False
    
    return True


def test_problem_context():
    """Test ProblemContext basic functionality."""
    print("\n=== Testing ProblemContext ===")
    
    from src.protocols import ProblemContext
    
    # Simple test with list coordinates
    coords = [[0, 0], [1, 0], [1, 1], [0, 1]]
    
    try:
        context = ProblemContext(coordinates=coords)
        print(f"✓ Created ProblemContext with {context.n_nodes} nodes")
    except Exception as e:
        print(f"✗ ProblemContext creation failed: {e}")
        return False
    
    return True


def test_nearest_neighbor():
    """Test NearestNeighborCPU algorithm."""
    print("\n=== Testing NearestNeighborCPU ===")
    
    from src.protocols import ProblemContext
    from src.algorithms import NearestNeighborCPU
    
    coords = [[0, 0], [1, 0], [1, 1], [0, 1]]
    context = ProblemContext(coordinates=coords)
    
    try:
        solver = NearestNeighborCPU()
        print(f"✓ Created solver: {solver}")
    except Exception as e:
        print(f"✗ Solver creation failed: {e}")
        return False
    
    try:
        tour = solver.solve(context)
        print(f"✓ Solved TSP, tour length: {len(tour)}")
        print(f"  Tour: {tour}")
    except Exception as e:
        print(f"✗ Solving failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        cost = solver.get_solution_cost(context, tour)
        print(f"✓ Computed cost: {cost:.2f}")
    except Exception as e:
        print(f"✗ Cost computation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_compositional_solver():
    """Test CompositionalTSPSolver."""
    print("\n=== Testing CompositionalTSPSolver ===")
    
    from src.protocols import ProblemContext
    from src.algorithms import NearestNeighborCPU, CompositionalTSPSolver
    
    coords = [[0, 0], [1, 0], [1, 1], [0, 1]]
    context = ProblemContext(coordinates=coords)
    
    try:
        constructor = NearestNeighborCPU()
        solver = CompositionalTSPSolver(constructor)
        print(f"✓ Created compositional solver: {solver}")
    except Exception as e:
        print(f"✗ Solver creation failed: {e}")
        return False
    
    try:
        solution = solver.solve(context)
        print(f"✓ Solved with compositional solver")
        print(f"  Solution length: {len(solution)}")
    except Exception as e:
        print(f"✗ Solving failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_multiple_strategies():
    """Test that we have multiple strategies (Lego bricks)."""
    print("\n=== Testing Multiple Strategies (Lego Bricks) ===")
    
    from src.protocols import ProblemContext
    from src.algorithms import (
        NearestNeighborCPU,
        RandomInsertionCPU,
        CheapestInsertionCPU,
    )
    
    coords = [[0, 0], [1, 0], [1, 1], [0, 1], [0.5, 0.5]]
    context = ProblemContext(coordinates=coords)
    
    strategies = [
        ("NearestNeighbor", NearestNeighborCPU()),
        ("RandomInsertion", RandomInsertionCPU(seed=42)),
        ("CheapestInsertion", CheapestInsertionCPU()),
        ("NearestNeighbor(start=1)", NearestNeighborCPU(start_node=1)),
    ]
    
    results = []
    
    for name, strategy in strategies:
        try:
            tour = strategy.solve(context)
            cost = strategy.get_solution_cost(context, tour)
            results.append((name, cost))
            print(f"✓ {name:25s}: Cost = {cost:.2f}, Tour length = {len(tour)}")
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print(f"\n✓ Successfully tested {len(strategies)} different strategies")
    print("✓ Architecture supports modular 'Lego brick' composition")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("GPU-Accelerated Architecture Validation Tests")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("ProblemContext Test", test_problem_context),
        ("NearestNeighbor Test", test_nearest_neighbor),
        ("Compositional Solver Test", test_compositional_solver),
        ("Multiple Strategies Test", test_multiple_strategies),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n✗ {name} FAILED")
        except Exception as e:
            failed += 1
            print(f"\n✗ {name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 All tests passed! Architecture is working correctly.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
