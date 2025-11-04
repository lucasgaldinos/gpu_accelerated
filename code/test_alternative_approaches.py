"""
Test Alternative CVRP Approaches - Prototypes

This script tests different algorithmic approaches to CVRP:
1. Routing-first: Build giant TSP tour, split by capacity
2. Spatial-first: Cluster by location, then pack+route per cluster
3. 2-opt improvement: Local search on routes

Goal: Test if we can achieve >60% improvement over baseline (134% gap).

NOTE: This is a PROTOTYPE - code is self-contained for rapid testing.
"""

import time
import numpy as np
import duckdb
from typing import List


def load_problem_from_db(problem_name: str):
    """Load problem from routing.duckdb database."""
    conn = duckdb.connect("../datasets/routing.duckdb", read_only=True)

    # Get problem info (filter by type='CVRP' to avoid TSP variants)
    problem_info = conn.execute(
        """
        SELECT id, dimension, capacity
        FROM problems
        WHERE name = ? AND type = 'CVRP'
    """,
        [problem_name],
    ).fetchone()

    if not problem_info:
        raise ValueError(f"Problem {problem_name} not found")

    problem_id, dimension, capacity = problem_info

    # Get best known solution cost
    best_known_result = conn.execute(
        """
        SELECT MIN(cost)
        FROM solutions
        WHERE problem_id = ?
    """,
        [problem_id],
    ).fetchone()

    best_known = (
        best_known_result[0] if best_known_result and best_known_result[0] else None
    )

    # Get node coordinates
    nodes = conn.execute(
        """
        SELECT node_id, x, y, demand
        FROM nodes
        WHERE problem_id = ?
        ORDER BY node_id
    """,
        [problem_id],
    ).fetchall()

    conn.close()

    # Build arrays
    locations = np.array([[n[1], n[2]] for n in nodes], dtype=np.float64)
    demands = np.array(
        [n[3] if n[3] else 0 for n in nodes[1:]], dtype=np.float64
    )  # Skip depot

    return {
        "name": problem_name,
        "locations": locations,
        "demands": demands,
        "capacity": capacity,
        "best_known": best_known,
        "n_customers": len(demands),
    }


def calculate_solution_cost(routes: List[List[int]], locations: np.ndarray) -> float:
    """Calculate total Euclidean distance of all routes."""
    total_cost = 0.0
    for route in routes:
        for i in range(len(route) - 1):
            from_node = route[i]
            to_node = route[i + 1]
            distance = np.linalg.norm(locations[from_node] - locations[to_node])
            total_cost += distance
    return total_cost


def validate_solution(
    routes: List[List[int]], demands: np.ndarray, capacity: float
) -> dict:
    """Validate CVRP solution constraints."""
    n_customers = len(demands)

    visited = set()
    for route in routes:
        # Check depot start/end
        if route[0] != 0 or route[-1] != 0:
            return {"valid": False, "reason": "Route must start and end at depot"}

        # Check capacity
        route_demand = sum(demands[i - 1] for i in route[1:-1])
        if route_demand > capacity:
            return {
                "valid": False,
                "reason": f"Route exceeds capacity: {route_demand} > {capacity}",
            }

        # Track visited customers
        for customer in route[1:-1]:
            if customer in visited:
                return {
                    "valid": False,
                    "reason": f"Customer {customer} visited multiple times",
                }
            visited.add(customer)

    # Check all customers visited
    expected = set(range(1, n_customers + 1))
    if visited != expected:
        missing = expected - visited
        return {"valid": False, "reason": f"Missing customers: {missing}"}

    return {"valid": True}


# ============================================================================
# HELPER: NEAREST NEIGHBOR TSP (simple greedy heuristic)
# ============================================================================


def nearest_neighbor_tsp(customers: List[int], locations: np.ndarray) -> List[int]:
    """
    Build TSP tour using nearest neighbor heuristic.
    Returns tour starting and ending at depot (0).
    """
    if not customers:
        return [0, 0]

    # Start at depot
    tour = [0]
    unvisited = set(customers)
    current = 0

    while unvisited:
        # Find nearest unvisited customer
        nearest = min(
            unvisited, key=lambda c: np.linalg.norm(locations[current] - locations[c])
        )
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    # Return to depot
    tour.append(0)
    return tour


# ============================================================================
# HELPER: FIRST FIT DECREASING BIN PACKING
# ============================================================================


def ffd_bin_packing(demands: np.ndarray, capacity: float) -> List[List[int]]:
    """
    First Fit Decreasing bin packing.
    Returns list of bins, each bin is list of indices into demands array.
    """
    # Sort indices by decreasing demand
    indices = np.argsort(-demands)

    bins = []
    bin_loads = []

    for idx in indices:
        demand = demands[idx]

        # Try to fit in existing bin
        placed = False
        for bin_idx, bin_load in enumerate(bin_loads):
            if bin_load + demand <= capacity:
                bins[bin_idx].append(int(idx))
                bin_loads[bin_idx] += demand
                placed = True
                break

        # Create new bin if needed
        if not placed:
            bins.append([int(idx)])
            bin_loads.append(demand)

    return bins


# ============================================================================
# PROTOTYPE 1: ROUTING-FIRST APPROACH
# ============================================================================


def prototype_routing_first(
    locations: np.ndarray, demands: np.ndarray, capacity: float
) -> List[List[int]]:
    """
    Build giant TSP tour over all customers, then split by capacity.

    Hypothesis: Preserves spatial structure better than bin-packing-first.
    """
    n = len(locations)

    # Build giant tour using nearest neighbor over ALL customers
    print("  Building giant TSP tour...")
    all_customers = list(range(1, n))  # All customers except depot
    giant_tour = nearest_neighbor_tsp(all_customers, locations)

    # Split tour by capacity
    print("  Splitting tour by capacity...")
    routes = []
    current_route = [0]  # Start at depot
    current_load = 0.0

    # Walk the tour (skip depot at start and end)
    for customer in giant_tour[1:-1]:
        demand = demands[customer - 1]

        if current_load + demand <= capacity:
            # Add to current route
            current_route.append(customer)
            current_load += demand
        else:
            # Start new route
            current_route.append(0)  # Return to depot
            routes.append(current_route)

            current_route = [0, customer]
            current_load = demand

    # Close last route
    if len(current_route) > 1:
        current_route.append(0)
        routes.append(current_route)

    return routes


# ============================================================================
# BASELINE: BIN-PACKING-FIRST
# ============================================================================


def baseline_bin_first(
    locations: np.ndarray, demands: np.ndarray, capacity: float
) -> List[List[int]]:
    """Current approach: bin-packing-first using FFD + nearest neighbor TSP."""
    # Bin pack by demand
    bins = ffd_bin_packing(demands, capacity)

    # Build TSP tour for each bin
    routes = []
    for bin_indices in bins:
        # Map bin indices to customer indices (bin indices are into demands array)
        customers = [i + 1 for i in bin_indices]  # demands[i] is customer i+1
        tour = nearest_neighbor_tsp(customers, locations)
        routes.append(tour)

    return routes


# ============================================================================
# MAIN TEST
# ============================================================================


def run_comparison(problem_name: str = "eil51"):
    """Run all prototypes and compare results."""
    print(f"\n{'=' * 80}")
    print(f"TESTING ALTERNATIVE APPROACHES ON {problem_name}")
    print(f"{'=' * 80}\n")

    # Load problem
    problem = load_problem_from_db(problem_name)
    print(f"Problem: {problem['name']}")
    print(
        f"  Nodes: {problem['n_customers'] + 1} (1 depot + {problem['n_customers']} customers)"
    )
    print(f"  Capacity: {problem['capacity']}")
    print(f"  Best known: {problem['best_known']}")
    print()

    results = {}

    # Test 1: Baseline (bin-first)
    print("=" * 80)
    print("BASELINE: Bin-Packing-First (FFD + Nearest Neighbor)")
    print("=" * 80)
    start = time.time()
    routes = baseline_bin_first(
        problem["locations"], problem["demands"], problem["capacity"]
    )
    elapsed = time.time() - start

    cost = calculate_solution_cost(routes, problem["locations"])
    validation = validate_solution(routes, problem["demands"], problem["capacity"])
    gap = (cost - problem["best_known"]) / problem["best_known"] * 100

    results["baseline_bin_first"] = {
        "cost": cost,
        "gap": gap,
        "routes": len(routes),
        "time": elapsed,
        "valid": validation["valid"],
    }

    print(f"  Cost: {cost:.2f}")
    print(f"  Gap: {gap:.2f}%")
    print(f"  Routes: {len(routes)}")
    print(f"  Time: {elapsed:.4f}s")
    print(f"  Valid: {validation['valid']}")
    if not validation["valid"]:
        print(f"  Reason: {validation['reason']}")
    print()

    # Test 2: Routing-first
    print("=" * 80)
    print("PROTOTYPE 1: Routing-First (Giant Tour → Split)")
    print("=" * 80)
    start = time.time()
    routes = prototype_routing_first(
        problem["locations"], problem["demands"], problem["capacity"]
    )
    elapsed = time.time() - start

    cost = calculate_solution_cost(routes, problem["locations"])
    validation = validate_solution(routes, problem["demands"], problem["capacity"])
    gap = (cost - problem["best_known"]) / problem["best_known"] * 100

    results["routing_first"] = {
        "cost": cost,
        "gap": gap,
        "routes": len(routes),
        "time": elapsed,
        "valid": validation["valid"],
    }

    print(f"  Cost: {cost:.2f}")
    print(f"  Gap: {gap:.2f}%")
    print(f"  Routes: {len(routes)}")
    print(f"  Time: {elapsed:.4f}s")
    print(f"  Valid: {validation['valid']}")
    if not validation["valid"]:
        print(f"  Reason: {validation['reason']}")
    print()

    # Comparison
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print(f"\n{'Approach':<30} {'Cost':>10} {'Gap':>10} {'Routes':>8} {'Time':>10}")
    print("-" * 80)

    for approach, data in results.items():
        status = "✓" if data["valid"] else "✗"
        print(
            f"{approach:<30} {data['cost']:>10.2f} {data['gap']:>9.1f}% {data['routes']:>8} {data['time']:>9.4f}s {status}"
        )

    print("\n")
    print(f"Best known: {problem['best_known']:.2f}")

    # Calculate improvement
    baseline_gap = results["baseline_bin_first"]["gap"]
    routing_gap = results["routing_first"]["gap"]
    improvement = baseline_gap - routing_gap

    print("\nRouting-first vs Baseline:")
    print(f"  Baseline gap: {baseline_gap:.1f}%")
    print(f"  Routing-first gap: {routing_gap:.1f}%")
    print(f"  Improvement: {improvement:.1f} percentage points")

    if improvement > 0:
        print(f"  ✓ Routing-first is BETTER by {improvement:.1f}%")
    elif improvement < 0:
        print(f"  ✗ Routing-first is WORSE by {abs(improvement):.1f}%")
    else:
        print("  = No difference")

    return results


if __name__ == "__main__":
    run_comparison("eil51")
