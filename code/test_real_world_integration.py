"""
Comprehensive integration test of compositional CVRP solver with real database problems.

Tests all 4 strategy combinations on real problems and compares solution quality.
"""

import sys

sys.path.insert(0, "src")

import numpy as np
import duckdb
import time
from typing import List, Tuple, Dict

from src.algorithms.strategies.bin_packing_strategies import FFDStrategy, BFDStrategy
from src.algorithms.strategies.tsp_strategies import (
    NearestNeighborStrategy,
    ChristofidesStrategy,
)
from src.algorithms.compositional_cvrp_solver import lego_cvrp_solver


def load_problem_from_db(problem_id: int) -> Tuple[np.ndarray, np.ndarray, float, str]:
    """Load problem data from routing.duckdb."""
    conn = duckdb.connect("../datasets/routing.duckdb", read_only=True)

    # Get problem metadata
    problem_query = """
    SELECT name, dimension, capacity, type
    FROM problems
    WHERE id = ?
    """
    prob_data = conn.execute(problem_query, [problem_id]).fetchone()
    name, dimension, capacity, ptype = prob_data

    # Get node coordinates and demands
    nodes_query = """
    SELECT node_id, x, y, demand, is_depot
    FROM nodes
    WHERE problem_id = ?
    ORDER BY node_id ASC
    """
    nodes = conn.execute(nodes_query, [problem_id]).fetchall()

    # Build arrays
    locations = np.zeros((len(nodes), 2))
    demands = np.zeros(len(nodes))

    for i, (node_id, x, y, demand, is_depot) in enumerate(nodes):
        locations[i] = [x, y]
        demands[i] = demand if demand else 0

    # Get best known solution cost (if exists)
    solution_query = """
    SELECT MIN(cost) as best_cost
    FROM solutions
    WHERE problem_id = ?
    """
    result = conn.execute(solution_query, [problem_id]).fetchone()
    best_known = result[0] if result and result[0] else None

    conn.close()

    print(f"Loaded problem: {name}")
    print(f"  Dimension: {dimension} nodes")
    print(f"  Capacity: {capacity}")
    print(f"  Best known cost: {best_known if best_known else 'N/A'}")
    print()

    return locations, demands, capacity, name


def calculate_route_cost(route: List[int], locations: np.ndarray) -> float:
    """Calculate total Euclidean distance for a route."""
    total_cost = 0.0
    for i in range(len(route) - 1):
        loc1 = locations[route[i]]
        loc2 = locations[route[i + 1]]
        distance = np.sqrt(np.sum((loc1 - loc2) ** 2))
        total_cost += distance
    return total_cost


def calculate_solution_cost(routes: List[List[int]], locations: np.ndarray) -> float:
    """Calculate total cost for all routes."""
    return sum(calculate_route_cost(route, locations) for route in routes)


def validate_solution(
    routes: List[List[int]], demands: np.ndarray, capacity: float, n_customers: int
) -> Dict[str, bool]:
    """Validate CVRP solution constraints."""
    validation = {
        "all_start_depot": True,
        "all_end_depot": True,
        "capacity_respected": True,
        "all_customers_visited": False,
        "no_duplicates": True,
    }

    visited = set()

    for route in routes:
        # Check depot start/end
        if route[0] != 0:
            validation["all_start_depot"] = False
        if route[-1] != 0:
            validation["all_end_depot"] = False

        # Check capacity
        route_demand = sum(demands[customer] for customer in route[1:-1])
        if route_demand > capacity:
            validation["capacity_respected"] = False

        # Check for duplicates
        for customer in route[1:-1]:
            if customer in visited:
                validation["no_duplicates"] = False
            visited.add(customer)

    # Check all customers visited
    expected_customers = set(
        range(1, n_customers + 1)
    )  # FIX: +1 to include last customer
    validation["all_customers_visited"] = visited == expected_customers

    # Debug output if validation fails
    if not validation["all_customers_visited"]:
        missing = expected_customers - visited
        extra = visited - expected_customers
        print(
            f"  DEBUG: Expected {len(expected_customers)} customers, visited {len(visited)}"
        )
        if missing:
            print(
                f"  DEBUG: Missing customers ({len(missing)}): {sorted(list(missing))[:10]}"
            )
        if extra:
            print(
                f"  DEBUG: Extra customers ({len(extra)}): {sorted(list(extra))[:10]}"
            )

    return validation


def test_strategy_combination(
    problem_name: str,
    locations: np.ndarray,
    demands: np.ndarray,
    capacity: float,
    bin_packing_strategy,
    tsp_strategy,
) -> Dict:
    """Test a specific strategy combination and return results."""
    bp_name = bin_packing_strategy.__class__.__name__
    tsp_name = tsp_strategy.__class__.__name__

    print(f"Testing: {bp_name} + {tsp_name}")

    try:
        # Run solver
        start_time = time.time()
        routes = lego_cvrp_solver(
            locations=locations,
            demands=demands,
            capacity=capacity,
            bin_packing_strategy=bin_packing_strategy,
            tsp_strategy=tsp_strategy,
            xp=np,
        )
        elapsed_time = time.time() - start_time

        # Calculate cost
        total_cost = calculate_solution_cost(routes, locations)

        # Validate
        n_customers = len(locations) - 1
        validation = validate_solution(routes, demands, capacity, n_customers)

        # Check if valid
        is_valid = all(validation.values())

        result = {
            "combination": f"{bp_name}+{tsp_name}",
            "success": True,
            "valid": is_valid,
            "num_routes": len(routes),
            "cost": total_cost,
            "time": elapsed_time,
            "validation": validation,
            "error": None,
        }

        print(f"  ✅ Success")
        print(f"  Routes: {len(routes)}")
        print(f"  Cost: {total_cost:.2f}")
        print(f"  Time: {elapsed_time:.3f}s")
        print(f"  Valid: {is_valid}")
        if not is_valid:
            print(f"  Validation issues: {[k for k, v in validation.items() if not v]}")
        print()

        return result

    except Exception as e:
        print(f"  ❌ FAILED: {str(e)}")
        print()

        return {
            "combination": f"{bp_name}+{tsp_name}",
            "success": False,
            "valid": False,
            "num_routes": 0,
            "cost": float("inf"),
            "time": 0.0,
            "validation": {},
            "error": str(e),
        }


def main():
    print("=" * 80)
    print("COMPOSITIONAL CVRP SOLVER - REAL-WORLD INTEGRATION TEST")
    print("=" * 80)
    print()

    # Load test problem (eil51 - has known solution)
    problem_id = 115  # eil51
    locations, demands, capacity, problem_name = load_problem_from_db(problem_id)

    # Define all strategy combinations
    strategies = [
        (FFDStrategy(), NearestNeighborStrategy()),
        (FFDStrategy(), ChristofidesStrategy()),
        (BFDStrategy(), NearestNeighborStrategy()),
        (BFDStrategy(), ChristofidesStrategy()),
    ]

    # Test all combinations
    results = []
    for bp_strat, tsp_strat in strategies:
        result = test_strategy_combination(
            problem_name,
            locations,
            demands,
            capacity,
            bp_strat,
            tsp_strat,
        )
        results.append(result)

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    print(f"Problem: {problem_name}")
    print(f"Nodes: {len(locations)}")
    print(f"Capacity: {capacity}")
    print(f"Best known cost: 426.0")
    print()

    # Sort by cost
    successful_results = [r for r in results if r["success"] and r["valid"]]
    if successful_results:
        successful_results.sort(key=lambda x: x["cost"])

        print("RESULTS (sorted by cost):")
        print()
        for r in successful_results:
            gap = ((r["cost"] - 426.0) / 426.0) * 100
            print(
                f"{r['combination']:40} Cost: {r['cost']:8.2f}  Gap: {gap:6.2f}%  Routes: {r['num_routes']:2}  Time: {r['time']:.3f}s"
            )

        best = successful_results[0]
        worst = successful_results[-1]
        print()
        print(f"Best combination: {best['combination']} (cost: {best['cost']:.2f})")
        print(f"Worst combination: {worst['combination']} (cost: {worst['cost']:.2f})")
        print(
            f"Cost variation: {((worst['cost'] - best['cost']) / best['cost']) * 100:.2f}%"
        )

    # Report failures
    failed_results = [r for r in results if not r["success"] or not r["valid"]]
    if failed_results:
        print()
        print("FAILURES:")
        for r in failed_results:
            print(
                f"  {r['combination']}: {r['error'] if r['error'] else 'Invalid solution'}"
            )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
