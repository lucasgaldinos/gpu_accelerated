#!/usr/bin/env python
"""
Demonstration of Hybrid Metaheuristics Architecture.

This script demonstrates the "Lego brick" pattern for composing
optimization strategies into hybrid metaheuristics.
"""

import sys
from pathlib import Path

# Add the code directory to the path for demonstration purposes
code_dir = Path(__file__).parent
sys.path.insert(0, str(code_dir))

from src.algorithms import (
    NearestNeighborStrategy,
    TwoOptStrategy,
    SimulatedAnnealingStrategy,
    GeneticAlgorithmStrategy,
    ComposableSolver,
    StrategyChain,
)
from src.utils import ProblemContext


def main():
    print("=" * 70)
    print("Hybrid Metaheuristics Architecture Demonstration")
    print("=" * 70)
    print()
    
    # Create a random TSP problem
    print("Creating a 20-node TSP problem...")
    context = ProblemContext.from_random(n_nodes=20, seed=42)
    print(f"Problem created with {context.n_nodes} nodes")
    print()
    
    # Demonstrate 1: Single constructive strategy
    print("-" * 70)
    print("Demo 1: Single Constructive Strategy (Nearest Neighbor)")
    print("-" * 70)
    solver = ComposableSolver(context)
    nn = NearestNeighborStrategy()
    
    strategies = [(nn, {'start_node': 0})]
    solution, cost, metrics = solver.solve(strategies, verbose=True)
    print()
    
    # Demonstrate 2: Constructive + Improvement
    print("-" * 70)
    print("Demo 2: Constructive + Improvement (NN + 2-Opt)")
    print("-" * 70)
    solver = ComposableSolver(context)
    nn = NearestNeighborStrategy()
    two_opt = TwoOptStrategy()
    
    strategies = [
        (nn, {'start_node': 0}),
        (two_opt, {'max_iterations': 100}),
    ]
    solution, cost, metrics = solver.solve(strategies, verbose=True)
    print()
    
    # Demonstrate 3: Three-stage hybrid
    print("-" * 70)
    print("Demo 3: Three-Stage Hybrid (NN + 2-Opt + SA)")
    print("-" * 70)
    solver = ComposableSolver(context)
    nn = NearestNeighborStrategy()
    two_opt = TwoOptStrategy()
    sa = SimulatedAnnealingStrategy(
        initial_temperature=100.0,
        cooling_rate=0.99,
        seed=42
    )
    
    strategies = [
        (nn, {'start_node': 0}),
        (two_opt, {'max_iterations': 100}),
        (sa, {'max_iterations': 1000}),
    ]
    solution, cost, metrics = solver.solve(strategies, verbose=True)
    print()
    
    # Demonstrate 4: Four-stage hybrid (all "Lego bricks")
    print("-" * 70)
    print("Demo 4: Four-Stage Hybrid (NN + 2-Opt + SA + GA)")
    print("-" * 70)
    solver = ComposableSolver(context)
    nn = NearestNeighborStrategy()
    two_opt = TwoOptStrategy()
    sa = SimulatedAnnealingStrategy(
        initial_temperature=80.0,
        cooling_rate=0.98,
        seed=42
    )
    ga = GeneticAlgorithmStrategy(
        population_size=50,
        mutation_rate=0.1,
        crossover_rate=0.8,
        seed=42
    )
    
    strategies = [
        (nn, {'start_node': 0}),
        (two_opt, {'max_iterations': 100}),
        (sa, {'max_iterations': 500}),
        (ga, {'max_iterations': 50}),
    ]
    solution, cost, metrics = solver.solve(strategies, verbose=True)
    print()
    
    # Demonstrate 5: Using StrategyChain fluent interface
    print("-" * 70)
    print("Demo 5: Using StrategyChain Fluent Interface")
    print("-" * 70)
    solver = ComposableSolver(context)
    
    chain = (StrategyChain()
        .construct_with(NearestNeighborStrategy(), start_node=0)
        .improve_with(TwoOptStrategy(), max_iterations=100)
        .optimize_with(
            SimulatedAnnealingStrategy(seed=42),
            max_iterations=500
        )
    )
    
    strategies = chain.build()
    solution, cost, metrics = solver.solve(strategies, verbose=True)
    print()
    
    # Demonstrate 6: Benchmarking
    print("-" * 70)
    print("Demo 6: Benchmarking a Strategy Chain (5 runs)")
    print("-" * 70)
    solver = ComposableSolver(context)
    
    nn = NearestNeighborStrategy()
    two_opt = TwoOptStrategy()
    
    strategies = [
        (nn, {'start_node': 0}),
        (two_opt, {'max_iterations': 100}),
    ]
    
    print("Running benchmark with 5 runs...")
    stats = solver.benchmark_strategies(strategies, n_runs=5, verbose=False)
    
    print(f"Results:")
    print(f"  Mean cost: {stats['mean_cost']:.2f} ± {stats['std_cost']:.2f}")
    print(f"  Min cost:  {stats['min_cost']:.2f}")
    print(f"  Max cost:  {stats['max_cost']:.2f}")
    print(f"  Mean time: {stats['mean_time']:.3f}s ± {stats['std_time']:.3f}s")
    print()
    
    print("=" * 70)
    print("Architecture Features Demonstrated:")
    print("=" * 70)
    print("✓ Modular 'Lego brick' strategy design")
    print("✓ Composable solver framework")
    print("✓ 4+ different strategy types (NN, 2-Opt, SA, GA)")
    print("✓ Hybrid metaheuristic composition")
    print("✓ Fluent StrategyChain interface")
    print("✓ Performance benchmarking support")
    print("✓ Centralized distance matrix computation (ProblemContext)")
    print("✓ No GPU kernel anti-patterns in sequential algorithms")
    print()


if __name__ == "__main__":
    main()
