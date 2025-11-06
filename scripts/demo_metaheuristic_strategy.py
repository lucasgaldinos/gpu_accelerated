#!/usr/bin/env python3
"""
Demonstration script for TspMetaheuristicStrategy protocol.

Shows how to implement and use metaheuristic strategies for TSP/CVRP.
This is a COMPREHENSIVE DEMO that includes:
1. Protocol validation
2. Mock implementation example
3. Usage patterns
4. Statistics analysis

Usage:
    uv run python scripts/demo_metaheuristic_strategy.py
"""

import numpy as np
import time
from typing import List, Dict, Any


def demo_protocol_structure():
    """Demonstrate protocol structure and requirements."""
    print("=" * 80)
    print("TspMetaheuristicStrategy Protocol Demo")
    print("=" * 80)
    print()

    print("1. PROTOCOL REQUIREMENTS")
    print("-" * 80)
    print("""
The TspMetaheuristicStrategy protocol defines the interface for metaheuristic
TSP solvers (Genetic Algorithm, Simulated Annealing, etc.).

Required Methods:
    - set_params(**hyperparameters) -> None
      Configure algorithm-specific hyperparameters
    
    - build_tour_with_stats(context, customers) -> (List[int], Dict)
      Solve TSP and return tour with optimization statistics
    
    - get_stats() -> Dict
      Retrieve statistics from most recent optimization run

Statistics Dictionary Format:
    Required keys:
        - best_fitness: Best tour cost found
        - final_fitness: Final tour cost  
        - iterations: Number of iterations executed
        - convergence_history: Fitness by iteration
        - runtime_seconds: Total execution time
        - hyperparameters: Hyperparameter values used
    
    Optional algorithm-specific keys:
        - population_diversity: GA/PSO diversity metrics
        - temperature_schedule: SA temperature by iteration
        - acceptance_rate: SA fraction of accepted moves
        - crossover_count, mutation_count: GA operator counts
""")


def demo_simple_implementation():
    """Demonstrate a simple metaheuristic implementation."""
    print()
    print("2. SIMPLE IMPLEMENTATION EXAMPLE")
    print("-" * 80)
    print()

    class SimpleMetaheuristicStrategy:
        """
        Simple metaheuristic strategy (Random Search baseline).

        This minimal implementation satisfies the protocol and provides
        a baseline for comparison with more sophisticated algorithms.
        """

        def __init__(self):
            self._hyperparams = {"max_iterations": 100}
            self._stats = {}

        def set_params(self, **hyperparameters):
            """Configure hyperparameters."""
            self._hyperparams.update(hyperparameters)
            print(f"  Hyperparameters set: {hyperparameters}")

        def build_tour_with_stats(self, context, customers):
            """Build tour using random search."""
            print(f"  Running random search with {len(customers)} customers...")

            start_time = time.time()
            max_iterations = self._hyperparams["max_iterations"]

            # Initialize with sorted tour
            best_tour = [0] + sorted(customers) + [0]
            best_cost = self._compute_cost(best_tour, context)

            convergence = [best_cost]

            # Random search
            for i in range(max_iterations):
                # Generate random permutation
                random_customers = np.random.permutation(customers).tolist()
                tour = [0] + random_customers + [0]
                cost = self._compute_cost(tour, context)

                # Update best if improved
                if cost < best_cost:
                    best_tour = tour
                    best_cost = cost

                convergence.append(best_cost)

            runtime = time.time() - start_time

            # Build statistics
            self._stats = {
                "best_fitness": best_cost,
                "final_fitness": self._compute_cost(best_tour, context),
                "iterations": max_iterations,
                "convergence_history": convergence,
                "runtime_seconds": runtime,
                "hyperparameters": self._hyperparams.copy(),
            }

            print(f"  Best cost: {best_cost:.2f}")
            print(f"  Runtime: {runtime:.3f}s")

            return best_tour, self._stats

        def get_stats(self):
            """Retrieve statistics."""
            return self._stats.copy()

        def _compute_cost(self, tour, context):
            """Compute tour cost."""
            distances = context.get_cpu_distances()
            cost = 0.0
            for i in range(len(tour) - 1):
                cost += distances[tour[i], tour[i + 1]]
            return cost

    print("Implementation created: SimpleMetaheuristicStrategy")
    print()
    print("Key features:")
    print("  - Satisfies TspMetaheuristicStrategy protocol")
    print("  - Uses random search as baseline algorithm")
    print("  - Tracks convergence history")
    print("  - Returns standardized statistics")
    print()

    return SimpleMetaheuristicStrategy


def demo_usage_with_real_problem(StrategyClass):
    """Demonstrate usage with a real TSP problem."""
    print()
    print("3. USAGE WITH REAL PROBLEM")
    print("-" * 80)
    print()

    # Create sample problem
    from src.data_models.problem import Problem
    from src.protocols.problem_context import ProblemContext

    problem = Problem(
        name="demo_problem",
        dimension=10,
        problem_type="TSP",
        edge_type="EUC_2D",
        coordinates=np.array(
            [
                [0, 0],  # Depot
                [10, 0],
                [20, 0],
                [30, 0],
                [30, 10],
                [30, 20],
                [20, 20],
                [10, 20],
                [0, 20],
                [0, 10],
            ]
        ),
        distances=None,
    )

    context = ProblemContext(problem, xp=np)
    print(f"Problem: {problem.name}")
    print(f"Dimension: {problem.dimension}")
    print(f"Type: {problem.problem_type}")
    print()

    # Create and configure strategy
    strategy = StrategyClass()
    print("Strategy: SimpleMetaheuristicStrategy")

    strategy.set_params(max_iterations=200)
    print()

    # Solve
    customers = list(range(1, problem.dimension))
    print(f"Solving TSP for customers: {customers}")
    print()

    tour, stats = strategy.build_tour_with_stats(context, customers)

    print()
    print("Results:")
    print(f"  Tour: {tour}")
    print(f"  Best fitness: {stats['best_fitness']:.2f}")
    print(f"  Iterations: {stats['iterations']}")
    print(f"  Runtime: {stats['runtime_seconds']:.3f}s")
    print()

    # Retrieve stats again
    stats2 = strategy.get_stats()
    assert stats2 == stats, "get_stats() should return same statistics"
    print("✅ Statistics retrieval verified")
    print()


def demo_statistics_analysis():
    """Demonstrate statistics analysis and visualization."""
    print()
    print("4. STATISTICS ANALYSIS")
    print("-" * 80)
    print()

    print("Statistics can be used for:")
    print("  1. Convergence analysis - plot convergence_history")
    print("  2. Hyperparameter tuning - compare best_fitness across configs")
    print("  3. Performance profiling - analyze runtime_seconds")
    print("  4. Algorithm comparison - compare different metaheuristics")
    print()

    print("Example analysis code:")
    print(
        """
    # Convergence plot
    import matplotlib.pyplot as plt
    plt.plot(stats['convergence_history'])
    plt.xlabel('Iteration')
    plt.ylabel('Best Fitness')
    plt.title('Convergence History')
    plt.show()
    
    # Hyperparameter grid search
    results = []
    for pop_size in [50, 100, 200]:
        for mut_rate in [0.05, 0.1, 0.2]:
            strategy.set_params(population_size=pop_size, mutation_rate=mut_rate)
            tour, stats = strategy.build_tour_with_stats(context, customers)
            results.append({
                'pop_size': pop_size,
                'mut_rate': mut_rate,
                'fitness': stats['best_fitness'],
                'runtime': stats['runtime_seconds']
            })
    
    # Find best configuration
    best = min(results, key=lambda x: x['fitness'])
    print(f"Best config: pop_size={best['pop_size']}, mut_rate={best['mut_rate']}")
"""
    )


def demo_next_steps():
    """Show next implementation steps."""
    print()
    print("5. NEXT STEPS")
    print("-" * 80)
    print()

    print("To implement real metaheuristic algorithms:")
    print()
    print("1. Genetic Algorithm (Todo #7):")
    print("   - Population initialization")
    print("   - Selection operators (tournament, roulette)")
    print("   - Crossover operators (OX, PMX, CX)")
    print("   - Mutation operators (swap, inversion, insertion)")
    print("   - GPU acceleration for fitness evaluation")
    print()

    print("2. Simulated Annealing (Todo #8):")
    print("   - Temperature schedule (geometric, linear, adaptive)")
    print("   - Neighbor generation (2-opt, swap, insertion)")
    print("   - Metropolis acceptance criterion")
    print("   - GPU acceleration for batch neighbor evaluation")
    print()

    print("3. Testing and Validation:")
    print("   - Create integration tests (test_genetic_algorithm.py)")
    print("   - Validate on benchmark problems (berlin52, etc.)")
    print("   - Compare against known optimal solutions")
    print("   - Benchmark CPU vs GPU performance")
    print()

    print("4. Advanced Features:")
    print("   - Hybrid approaches (NN + SA, GA + 2-opt)")
    print("   - Adaptive hyperparameters")
    print("   - Multi-objective optimization")
    print("   - Parallel island models (GPU)")
    print()


def main():
    """Main demo entry point."""
    print()
    print("🚀 TspMetaheuristicStrategy Protocol Demonstration")
    print()

    # Show protocol structure
    demo_protocol_structure()

    # Create simple implementation
    StrategyClass = demo_simple_implementation()

    # Demonstrate usage
    demo_usage_with_real_problem(StrategyClass)

    # Show analysis patterns
    demo_statistics_analysis()

    # Show next steps
    demo_next_steps()

    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)
    print()
    print("Summary:")
    print("  ✅ Protocol structure explained")
    print("  ✅ Simple implementation demonstrated")
    print("  ✅ Real problem usage shown")
    print("  ✅ Statistics analysis patterns provided")
    print("  ✅ Next implementation steps outlined")
    print()
    print("Ready to implement:")
    print("  - GeneticAlgorithmStrategy (Todo #7)")
    print("  - SimulatedAnnealingStrategy (Todo #8)")
    print()


if __name__ == "__main__":
    main()
