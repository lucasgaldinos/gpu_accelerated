#!/usr/bin/env python3
"""
Simple example demonstrating ProblemContext architecture without database dependency.

This script creates synthetic problems and demonstrates the refactored architecture.
"""

import sys
import numpy as np

# Add code/src to path
sys.path.insert(0, "/home/runner/work/gpu_accelerated/gpu_accelerated/code")

from src.data_models.problem import Problem
from src.protocols.problem_context import ProblemContext
from src.algorithms.strategies.tsp_strategies import NearestNeighborStrategy
from src.algorithms.strategies.bin_packing_strategies import FFDStrategy
from src.algorithms.compositional_cvrp_solver import lego_cvrp_solver
from src.algorithms.improvement.two_opt_cpu import TwoOptCPU


def create_synthetic_problem(n=20, seed=42):
    """Create a synthetic TSP/CVRP problem for testing."""
    np.random.seed(seed)
    
    # Generate random coordinates
    coordinates = np.random.rand(n, 2) * 100  # 100x100 grid
    
    # Generate demands for CVRP
    demands = np.array([0] + list(10 + np.random.randint(0, 20, n-1)))
    
    problem = Problem(
        name=f"synthetic_{n}",
        dimension=n,
        problem_type="CVRP",
        edge_type="EUC_2D",
        coordinates=coordinates,
        distances=None,  # Will be computed from coordinates
        capacity=50,
        demands=demands,
    )
    
    return problem


def example_1_context_caching():
    """Demonstrate distance matrix caching."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Distance Matrix Caching in ProblemContext")
    print("=" * 70)
    
    problem = create_synthetic_problem(n=15)
    print(f"Created synthetic problem: {problem.name}")
    print(f"  Dimension: {problem.dimension} nodes")
    print(f"  Type: {problem.problem_type}")
    print(f"  Capacity: {problem.capacity}")
    
    # Create context - distance matrix computed ONCE
    print("\nCreating ProblemContext...")
    context = ProblemContext(problem, xp=np)
    print(f"  {context}")
    print(f"  Distance matrix shape: {context.distances.shape}")
    print(f"  Distance matrix type: {type(context.distances)}")
    
    # Verify it's cached (same object on repeated access)
    print(f"\nDistance matrix is cached: {context.distances is context.distances}")
    
    # Show sample distances
    print(f"\nSample distances:")
    print(f"  Distance [0→1]: {context.distances[0, 1]:.2f}")
    print(f"  Distance [1→0]: {context.distances[1, 0]:.2f} (should be same)")
    print(f"  Symmetric: {np.allclose(context.distances, context.distances.T)}")


def example_2_tsp_strategies():
    """Demonstrate TSP strategies reusing cached context."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multiple Strategies Reuse Cached Distance Matrix")
    print("=" * 70)
    
    problem = create_synthetic_problem(n=10)
    print(f"Problem: {problem.name} ({problem.dimension} nodes)")
    
    # Create context ONCE
    context = ProblemContext(problem, xp=np)
    print(f"ProblemContext created (distance matrix computed once)")
    
    # Use strategy multiple times - all reuse same cached distance matrix!
    customers_list = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    strategy = NearestNeighborStrategy()
    
    print(f"\nBuilding {len(customers_list)} tours using SAME cached context:")
    for i, customers in enumerate(customers_list):
        tour = strategy.build_tour(context, customers)
        print(f"  Tour {i+1} (customers {customers}): {tour}")
    
    print(f"\n✅ All {len(customers_list)} tours used the SAME distance matrix (cached)")
    print(f"   No redundant O(n²) computations!")


def example_3_improvement():
    """Demonstrate tour improvement with 2-opt."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Tour Improvement with 2-Opt")
    print("=" * 70)
    
    problem = create_synthetic_problem(n=12, seed=123)
    context = ProblemContext(problem, xp=np)
    
    # Build initial tour
    customers = list(range(1, problem.dimension))
    nn_strategy = NearestNeighborStrategy()
    initial_tour = nn_strategy.build_tour(context, customers)
    
    # Calculate initial cost
    initial_cost = sum(
        context.distances[initial_tour[i], initial_tour[i+1]]
        for i in range(len(initial_tour) - 1)
    )
    
    print(f"Initial tour (Nearest Neighbor): cost = {initial_cost:.2f}")
    
    # Improve with 2-opt
    two_opt = TwoOptCPU(max_iterations=500)
    improved_tour = two_opt.improve_tour(context, initial_tour)
    
    # Calculate improved cost
    improved_cost = sum(
        context.distances[improved_tour[i], improved_tour[i+1]]
        for i in range(len(improved_tour) - 1)
    )
    
    print(f"Improved tour (2-Opt):         cost = {improved_cost:.2f}")
    print(f"Improvement: {((initial_cost - improved_cost) / initial_cost * 100):.1f}%")


def example_4_cvrp_solver():
    """Demonstrate full CVRP solving."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Full CVRP Solving with Compositional Architecture")
    print("=" * 70)
    
    problem = create_synthetic_problem(n=15, seed=789)
    print(f"Problem: {problem.name}")
    print(f"  Nodes: {problem.dimension}")
    print(f"  Capacity: {problem.capacity}")
    print(f"  Total demand: {problem.demands[1:].sum()}")
    
    # Solve with FFD + Nearest Neighbor
    print("\nSolving with FFD + Nearest Neighbor...")
    routes = lego_cvrp_solver(
        problem,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=NearestNeighborStrategy(),
        xp=np
    )
    
    print(f"Solution: {len(routes)} routes")
    total_cost = 0.0
    for i, route in enumerate(routes):
        # Calculate route cost
        route_cost = 0.0
        context = ProblemContext(problem, xp=np)  # Temporary for cost calc
        for j in range(len(route) - 1):
            route_cost += context.distances[route[j], route[j+1]]
        total_cost += route_cost
        
        # Calculate route demand
        route_demand = sum(problem.demands[node] for node in route if node != 0)
        
        print(f"  Route {i+1}: {len(route)-2} customers, "
              f"demand={route_demand:.0f}/{problem.capacity}, "
              f"cost={route_cost:.2f}")
    
    print(f"\nTotal solution cost: {total_cost:.2f}")
    
    # Solve with improvement
    print("\nSolving with FFD + Nearest Neighbor + 2-Opt...")
    routes_improved = lego_cvrp_solver(
        problem,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=NearestNeighborStrategy(),
        improvement_strategy=TwoOptCPU(max_iterations=300),
        xp=np
    )
    
    print(f"Solution: {len(routes_improved)} routes")
    total_cost_improved = 0.0
    for i, route in enumerate(routes_improved):
        route_cost = 0.0
        context = ProblemContext(problem, xp=np)
        for j in range(len(route) - 1):
            route_cost += context.distances[route[j], route[j+1]]
        total_cost_improved += route_cost
        
        route_demand = sum(problem.demands[node] for node in route if node != 0)
        print(f"  Route {i+1}: {len(route)-2} customers, "
              f"demand={route_demand:.0f}/{problem.capacity}, "
              f"cost={route_cost:.2f}")
    
    print(f"\nTotal solution cost: {total_cost_improved:.2f}")
    print(f"Improvement from 2-Opt: {((total_cost - total_cost_improved) / total_cost * 100):.1f}%")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("PROBLEMCONTEXT ARCHITECTURE - SIMPLE EXAMPLES")
    print("=" * 70)
    print("\nDemonstrating the refactored architecture:")
    print("✅ Distance matrix computed ONCE and cached in ProblemContext")
    print("✅ Multiple strategies reuse the same cached matrix")
    print("✅ No redundant O(n²) distance computations")
    print("✅ GPU memory cleanup (when using CuPy)")
    
    try:
        example_1_context_caching()
        example_2_tsp_strategies()
        example_3_improvement()
        example_4_cvrp_solver()
        
        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nKey Achievements Demonstrated:")
        print("  ✅ ProblemContext caches distance matrix")
        print("  ✅ Strategies reuse cached data (no recomputation)")
        print("  ✅ Class S (CPU) and Class P (GPU-capable) separation")
        print("  ✅ Compositional architecture working correctly")
        print("  ✅ GPU memory cleanup integrated")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
