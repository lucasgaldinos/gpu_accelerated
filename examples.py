#!/usr/bin/env python3
"""
Example demonstrating the modular "Lego brick" architecture.

This script shows how different algorithm strategies can be composed
to solve TSP problems efficiently.
"""

import sys
import os

# Add code directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))

try:
    import numpy as np
except ImportError:
    print("NumPy is required. Install with: pip install numpy")
    sys.exit(1)

from src.protocols import ProblemContext, CUPY_AVAILABLE
from src.algorithms import (
    NearestNeighborCPU,
    RandomInsertionCPU,
    CheapestInsertionCPU,
    CompositionalTSPSolver,
)


def print_separator(title=""):
    """Print a separator line."""
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}\n")
    else:
        print(f"{'=' * 60}\n")


def example_1_basic_usage():
    """Example 1: Basic usage with a simple TSP."""
    print_separator("Example 1: Basic TSP Solving")
    
    # Create a simple 5-city TSP
    coords = np.array([
        [0, 0],      # City 0
        [10, 0],     # City 1
        [10, 10],    # City 2
        [0, 10],     # City 3
        [5, 5],      # City 4 (center)
    ])
    
    print("Cities:")
    for i, (x, y) in enumerate(coords):
        print(f"  City {i}: ({x:5.1f}, {y:5.1f})")
    
    # Create problem context
    context = ProblemContext(coordinates=coords)
    print(f"\nProblem: {context.n_nodes} cities")
    
    # Solve with Nearest Neighbor
    solver = NearestNeighborCPU(start_node=0)
    tour = solver.solve(context)
    cost = solver.get_solution_cost(context, tour)
    
    print(f"\nNearest Neighbor Solution:")
    print(f"  Tour: {tour}")
    print(f"  Cost: {cost:.2f}")
    
    # Note: Distance matrix was computed and cached
    print(f"\n✓ Distance matrix cached in ProblemContext")


def example_2_compare_strategies():
    """Example 2: Compare different construction strategies."""
    print_separator("Example 2: Comparing Strategies")
    
    # Create a random problem
    np.random.seed(42)
    coords = np.random.rand(15, 2) * 100
    context = ProblemContext(coordinates=coords)
    
    print(f"Random TSP with {context.n_nodes} cities\n")
    
    # Define strategies to compare
    strategies = [
        ("Nearest Neighbor", NearestNeighborCPU()),
        ("Random Insertion", RandomInsertionCPU(seed=42)),
        ("Cheapest Insertion", CheapestInsertionCPU()),
        ("NN (start at 5)", NearestNeighborCPU(start_node=5)),
    ]
    
    results = []
    
    print(f"{'Strategy':<25} {'Cost':>12} {'Tour Length':>12}")
    print("-" * 50)
    
    for name, strategy in strategies:
        tour = strategy.solve(context)
        cost = strategy.get_solution_cost(context, tour)
        results.append((name, cost))
        print(f"{name:<25} {cost:>12.2f} {len(tour):>12}")
    
    # Find best
    best_name, best_cost = min(results, key=lambda x: x[1])
    print(f"\n✓ Best: {best_name} with cost {best_cost:.2f}")
    
    # All strategies used the same cached distance matrix!
    print(f"✓ All strategies reused the same distance matrix")


def example_3_compositional_solver():
    """Example 3: Using compositional solver."""
    print_separator("Example 3: Compositional Solver")
    
    # Create problem
    np.random.seed(123)
    coords = np.random.rand(20, 2) * 100
    context = ProblemContext(coordinates=coords)
    
    print(f"TSP with {context.n_nodes} cities")
    print("\nUsing compositional approach:")
    print("  Construction: Cheapest Insertion")
    print("  Improvement: (none in this example)")
    
    # Create compositional solver
    constructor = CheapestInsertionCPU()
    solver = CompositionalTSPSolver(constructor)
    
    # Solve with statistics
    stats = solver.solve_with_stats(context)
    
    print(f"\nResults:")
    print(f"  Initial cost: {stats['initial_cost']:.2f}")
    print(f"  Final cost:   {stats['final_cost']:.2f}")
    print(f"  Improvement:  {stats['improvement']:.2f} ({stats['improvement_percent']:.1f}%)")
    
    print(f"\n✓ Compositional solver demonstrates 'Lego block' pattern")


def example_4_benchmark():
    """Example 4: Benchmark different strategies."""
    print_separator("Example 4: Performance Benchmark")
    
    import time
    
    # Create larger problem
    np.random.seed(456)
    coords = np.random.rand(50, 2) * 1000
    context = ProblemContext(coordinates=coords)
    
    print(f"Benchmarking on {context.n_nodes}-city TSP\n")
    
    strategies = [
        ("Nearest Neighbor", NearestNeighborCPU()),
        ("Random Insertion", RandomInsertionCPU(seed=42)),
        ("Cheapest Insertion", CheapestInsertionCPU()),
    ]
    
    benchmarks = []
    
    print(f"{'Strategy':<25} {'Time (s)':>12} {'Cost':>12} {'Quality':>10}")
    print("-" * 60)
    
    for name, strategy in strategies:
        start = time.time()
        tour = strategy.solve(context)
        elapsed = time.time() - start
        cost = strategy.get_solution_cost(context, tour)
        benchmarks.append((name, elapsed, cost))
    
    # Find best cost for quality comparison
    best_cost = min(b[2] for b in benchmarks)
    
    for name, elapsed, cost in benchmarks:
        quality = (cost / best_cost - 1) * 100  # % worse than best
        print(f"{name:<25} {elapsed:>12.4f} {cost:>12.2f} {quality:>9.1f}%")
    
    print(f"\n✓ All solvers benefited from cached distance matrix")


def example_5_gpu_acceleration():
    """Example 5: GPU acceleration (if available)."""
    print_separator("Example 5: GPU Acceleration")
    
    if not CUPY_AVAILABLE:
        print("CuPy not available. This example requires GPU support.")
        print("Install with: pip install cupy-cuda12x")
        return
    
    from src.algorithms import TwoOptGPU
    
    # Create problem
    np.random.seed(789)
    coords = np.random.rand(30, 2) * 100
    context = ProblemContext(coordinates=coords)
    
    print(f"TSP with {context.n_nodes} cities")
    
    # Create initial solution with CPU
    print("\n1. Creating initial solution (CPU)...")
    constructor = NearestNeighborCPU()
    initial_tour = constructor.solve(context)
    initial_cost = constructor.get_solution_cost(context, initial_tour)
    print(f"   Initial cost: {initial_cost:.2f}")
    
    # Improve with GPU
    print("\n2. Improving with 2-opt (GPU)...")
    improver = TwoOptGPU(max_iterations=50)
    improved_tour = improver.improve(context, initial_tour)
    final_cost = improver.get_solution_cost(context, improved_tour)
    
    improvement = initial_cost - final_cost
    improvement_pct = (improvement / initial_cost) * 100
    
    print(f"   Final cost: {final_cost:.2f}")
    print(f"   Improvement: {improvement:.2f} ({improvement_pct:.1f}%)")
    
    print(f"\n✓ GPU acceleration demonstrated")
    print(f"✓ Distance matrix transferred to GPU and cached")


def example_6_vrp_with_capacity():
    """Example 6: VRP with capacity constraints."""
    print_separator("Example 6: VRP with Capacity")
    
    # Create VRP problem
    coords = np.array([
        [0, 0],    # Depot
        [5, 5],    # Customer 1
        [10, 0],   # Customer 2
        [10, 10],  # Customer 3
        [0, 10],   # Customer 4
    ])
    
    demands = np.array([0, 15, 10, 20, 25])  # Depot has 0 demand
    capacity = 40
    
    context = ProblemContext(
        coordinates=coords,
        demands=demands,
        capacity=capacity
    )
    
    print(f"VRP Problem:")
    print(f"  Nodes: {context.n_nodes}")
    print(f"  Vehicle capacity: {capacity}")
    print(f"  Has capacity constraints: {context.has_capacity_constraints()}")
    
    print(f"\nDemands:")
    for i, d in enumerate(demands):
        print(f"  Node {i}: {d}")
    
    # For this example, we just use TSP solver
    # (Full VRP solver would respect capacity constraints)
    solver = CheapestInsertionCPU()
    tour = solver.solve(context)
    
    print(f"\nTSP Tour (ignoring capacity): {tour}")
    print(f"Note: Full VRP solver would split into multiple routes")
    
    print(f"\n✓ ProblemContext supports both TSP and VRP data")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("  GPU-Accelerated TSP: Architecture Examples")
    print("  Demonstrating the 'Lego Brick' Modular Design")
    print("=" * 60)
    
    examples = [
        example_1_basic_usage,
        example_2_compare_strategies,
        example_3_compositional_solver,
        example_4_benchmark,
        example_5_gpu_acceleration,
        example_6_vrp_with_capacity,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n✗ Example failed: {e}")
            import traceback
            traceback.print_exc()
    
    print_separator()
    print("Examples complete!")
    print("\nKey Takeaways:")
    print("  ✓ 4+ different strategy 'Lego bricks' available")
    print("  ✓ Distance matrices cached and reused efficiently")
    print("  ✓ CPU and GPU algorithms clearly separated")
    print("  ✓ Strategies can be easily composed together")
    print("  ✓ Architecture supports both TSP and VRP")
    print("\nNext steps:")
    print("  - Read documentation/ARCHITECTURE.md for details")
    print("  - Run tests with: pytest code/tests/")
    print("  - Create your own custom strategies!")
    print("")


if __name__ == "__main__":
    main()
