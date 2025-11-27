#!/usr/bin/env python3
"""Debug fitness calculation to understand tour cost discrepancy."""

import numpy as np
from pathlib import Path

# Add src to path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from loaders.database_loader import DatabaseLoader
from pathlib import Path

# Load kroA100
db_path = Path(__file__).parent.parent / "datasets" / "routing.duckdb"
with DatabaseLoader(str(db_path)) as loader:
    problem = loader.load("kroA100")

distances = problem.distance_matrix
n = problem.dimension

print(f"Problem: kroA100")
print(f"Dimension: {n}")
print(f"TSPLIB Optimal: 21282")
print()

# Test 1: Sequential tour [0, 1, 2, ..., 99]
tour_sequential = np.arange(n, dtype=np.int32)
cost_sequential = sum(
    distances[tour_sequential[i], tour_sequential[(i + 1) % n]] for i in range(n)
)
print(f"Test 1: Sequential tour [0,1,2,...,99]")
print(f"  Cost: {cost_sequential:.2f}")
print()

# Test 2: Random permutation
np.random.seed(42)
tour_random = np.random.permutation(n).astype(np.int32)
cost_random = sum(distances[tour_random[i], tour_random[(i + 1) % n]] for i in range(n))
print(f"Test 2: Random permutation (seed=42)")
print(f"  Tour: {tour_random[:10]}...")
print(f"  Cost: {cost_random:.2f}")
print()

# Test 3: Check if distances are symmetric
print(f"Test 3: Distance matrix properties")
print(f"  Symmetric: {np.allclose(distances, distances.T)}")
print(f"  Diagonal zeros: {np.allclose(np.diag(distances), 0)}")
print(f"  Min distance: {distances[distances > 0].min():.2f}")
print(f"  Max distance: {distances.max():.2f}")
print()

# Test 4: What if we DON'T include return edge?
cost_no_return = sum(
    distances[tour_random[i], tour_random[i + 1]] for i in range(n - 1)
)
print(f"Test 4: Cost WITHOUT return edge")
print(f"  Cost: {cost_no_return:.2f}")
print(
    f"  Missing edge: d[{tour_random[-1]}, {tour_random[0]}] = {distances[tour_random[-1], tour_random[0]]:.2f}"
)
print(
    f"  Total with return: {cost_no_return + distances[tour_random[-1], tour_random[0]]:.2f}"
)
print()


# Test 5: Simulate GA's fitness function
def ga_fitness(tour, distances):
    """Exact copy of GeneticAlgorithmHybridNaive._evaluate_population logic."""
    cost = 0.0
    for j in range(len(tour)):
        city_from = tour[j]
        city_to = tour[(j + 1) % len(tour)]
        cost += distances[city_from, city_to]
    return cost


cost_ga_method = ga_fitness(tour_random, distances)
print(f"Test 5: GA fitness function (with modulo)")
print(f"  Cost: {cost_ga_method:.2f}")
print(f"  Matches Test 2: {np.isclose(cost_ga_method, cost_random)}")
print()

# Test 6: Check if problem is loading optimal solution somehow
print(f"Test 6: Problem object inspection")
print(f"  Attributes: {dir(problem)}")
if hasattr(problem, "optimal_cost"):
    print(f"  Optimal cost (if stored): {problem.optimal_cost}")
