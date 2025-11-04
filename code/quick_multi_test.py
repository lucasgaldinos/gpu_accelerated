"""Quick multi-problem test of compositional solver."""

import sys

sys.path.insert(0, "src")

import numpy as np
import duckdb
import time
from src.algorithms.strategies.bin_packing_strategies import FFDStrategy, BFDStrategy
from src.algorithms.strategies.tsp_strategies import (
    NearestNeighborStrategy,
    ChristofidesStrategy,
)
from src.algorithms.compositional_cvrp_solver import lego_cvrp_solver


def load_problem(problem_id):
    conn = duckdb.connect("../datasets/routing.duckdb", read_only=True)
    nodes = conn.execute(
        f"SELECT x, y, demand FROM nodes WHERE problem_id = {problem_id} ORDER BY node_id"
    ).fetchall()
    meta = conn.execute(
        f"SELECT name, capacity FROM problems WHERE id = {problem_id}"
    ).fetchone()
    best = conn.execute(
        f"SELECT MIN(cost) FROM solutions WHERE problem_id = {problem_id}"
    ).fetchone()
    conn.close()

    locations = np.array([[x, y] for x, y, _ in nodes])
    demands = np.array([d if d else 0 for _, _, d in nodes])

    return locations, demands, meta[1], meta[0], best[0] if best and best[0] else None


def calc_cost(routes, locations):
    cost = 0
    for route in routes:
        for i in range(len(route) - 1):
            diff = locations[route[i]] - locations[route[i + 1]]
            cost += np.sqrt(np.sum(diff**2))
    return cost


# Test problems
problems = [
    (111, "eil22"),
    (118, "eil30"),
    (115, "eil51"),
]

print("=" * 80)
print("MULTI-PROBLEM COMPOSITIONAL SOLVER TEST")
print("=" * 80)
print()

for pid, pname in problems:
    locations, demands, capacity, name, best_known = load_problem(pid)

    print(f"Problem: {name} ({len(locations)} nodes)")

    # Test only best combination
    start = time.time()
    routes = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=ChristofidesStrategy(),
        xp=np,
    )
    elapsed = time.time() - start

    cost = calc_cost(routes, locations)
    gap = ((cost - best_known) / best_known * 100) if best_known else None

    if best_known is not None:
        print(f"  Best known: {best_known:.2f}")
    else:
        print("  Best known: N/A")
    print(f"  Our solution: {cost:.2f} ({len(routes)} routes)")
    if gap is not None:
        print(f"  Gap: {gap:.2f}%")
    print(f"  Time: {elapsed:.3f}s")
    print()

print("=" * 80)
