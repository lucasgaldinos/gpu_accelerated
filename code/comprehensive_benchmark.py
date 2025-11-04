"""
Comprehensive benchmark of CVRP solution approaches.

Tests multiple combinations of bin packing and TSP strategies, including:
- Bin-first approach (bin packing → TSP per bin)
- Routing-first approach (giant TSP → split by capacity)

Metrics collected:
- Total distance
- Total distance + number of routes (weighted)
- Number of routes
- Bin packing efficiency
- Strategy names
- Execution time (mean, std, min, max over multiple runs)

GPU backend support using CuPy.
"""

import sys
import time
import numpy as np
import duckdb
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field

# Import strategies from src
from src.algorithms.strategies.bin_packing_strategies import FFDStrategy, BFDStrategy
from src.algorithms.strategies.tsp_strategies import (
    NearestNeighborStrategy,
    ChristofidesStrategy,
)
from src.algorithms.compositional_cvrp_solver import lego_cvrp_solver


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""

    approach: str
    bin_strategy: str
    tsp_strategy: str
    problem: str
    distance: float
    num_routes: int
    distance_plus_routes: float  # distance + 100 * num_routes
    bin_efficiency: float  # total_demand / (num_routes * capacity)
    time_mean: float
    time_std: float
    time_min: float
    time_max: float
    gap_distance: float  # (distance - optimal) / optimal * 100
    gap_combined: (
        float  # (distance_plus_routes - optimal_combined) / optimal_combined * 100
    )
    valid: bool
    with_2opt: bool = False
    backend: str = "numpy"
    routes: List[List[int]] = field(default_factory=list)


def load_problem_from_db(
    problem_name: str,
) -> Tuple[np.ndarray, np.ndarray, float, float]:
    """Load problem from database."""
    conn = duckdb.connect("../datasets/routing.duckdb", read_only=True)

    # Get problem info (filter by CVRP type)
    problem_info = conn.execute(
        """
        SELECT id, dimension, capacity
        FROM problems
        WHERE name = ? AND type = 'CVRP'
    """,
        [problem_name],
    ).fetchone()

    if not problem_info:
        raise ValueError(f"CVRP problem {problem_name} not found")

    problem_id, dimension, capacity = problem_info

    # Get best known solution
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

    # Get nodes
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

    # Convert to arrays
    locations = np.array([[x, y] for _, x, y, _ in nodes])
    demands = np.array([d if d else 0.0 for _, _, _, d in nodes])

    return locations, demands, capacity, best_known


def calculate_route_distance(route: List[int], locations: np.ndarray, xp=np) -> float:
    """Calculate total distance for a single route."""
    if len(route) < 2:
        return 0.0

    total_dist = 0.0
    for i in range(len(route) - 1):
        diff = locations[route[i]] - locations[route[i + 1]]
        total_dist += float(xp.sqrt(xp.sum(diff**2)))

    return total_dist


def calculate_solution_cost(
    routes: List[List[int]], locations: np.ndarray, xp=np
) -> float:
    """Calculate total distance for all routes."""
    return sum(calculate_route_distance(route, locations, xp) for route in routes)


def validate_solution(
    routes: List[List[int]], demands: np.ndarray, capacity: float
) -> bool:
    """Validate CVRP solution constraints."""
    # Check all routes start and end at depot (0)
    for route in routes:
        if len(route) < 2 or route[0] != 0 or route[-1] != 0:
            return False

    # Check capacity constraints
    for route in routes:
        route_demand = sum(demands[i] for i in route[1:-1])
        if route_demand > capacity:
            return False

    # Check all customers covered exactly once
    customers_covered = set()
    for route in routes:
        for node in route[1:-1]:
            if node in customers_covered:
                return False
            customers_covered.add(node)

    expected_customers = set(range(1, len(demands)))
    if customers_covered != expected_customers:
        return False

    return True


def calculate_bin_efficiency(
    routes: List[List[int]], demands: np.ndarray, capacity: float
) -> float:
    """Calculate bin packing efficiency (total demand / total capacity used)."""
    total_demand = sum(demands[1:])  # Exclude depot
    total_capacity_used = len(routes) * capacity
    return total_demand / total_capacity_used if total_capacity_used > 0 else 0.0


def nearest_neighbor_tsp(locations: np.ndarray, start: int = 0, xp=np) -> List[int]:
    """Simple greedy nearest neighbor TSP."""
    n = len(locations)
    unvisited = set(range(n))
    unvisited.remove(start)

    tour = [start]
    current = start

    while unvisited:
        # Find nearest unvisited node
        nearest = min(
            unvisited,
            key=lambda node: xp.linalg.norm(locations[current] - locations[node]),
        )
        tour.append(nearest)
        current = nearest
        unvisited.remove(nearest)

    tour.append(start)  # Return to depot
    return tour


def routing_first_approach(
    locations: np.ndarray, demands: np.ndarray, capacity: float, tsp_func, xp=np
) -> List[List[int]]:
    """
    Routing-first approach: Build giant TSP tour, then split by capacity.

    This preserves spatial structure better than bin-first.
    """
    # Build giant tour (all customers)
    giant_tour = tsp_func(locations, start=0, xp=xp)

    # Split tour by capacity constraints
    routes = []
    current_route = [0]  # Start at depot
    current_load = 0.0

    for node in giant_tour[1:-1]:  # Skip depot at start and end
        node_demand = demands[node]

        if current_load + node_demand <= capacity:
            # Add to current route
            current_route.append(node)
            current_load += node_demand
        else:
            # Start new route
            current_route.append(0)  # Return to depot
            routes.append(current_route)
            current_route = [0, node]
            current_load = node_demand

    # Close last route
    if len(current_route) > 1:
        current_route.append(0)
        routes.append(current_route)

    return routes


def two_opt_route(route: List[int], locations: np.ndarray) -> List[int]:
    """
    Improve a single route using 2-opt local search.

    Args:
        route: List of node indices [depot, n1, n2, ..., depot]
        locations: (n, 2) array of node coordinates

    Returns:
        Improved route with same depot constraints

    Note:
        Preserves depot at start and end. Only optimizes internal segment.
    """
    if len(route) <= 3:  # [depot, customer, depot] - can't improve
        return route

    improved = True
    best_route = route[:]

    while improved:
        improved = False
        best_distance = calculate_route_distance(best_route, locations)

        # Try all edge swaps (skip depot at start/end)
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route) - 1):
                # Create new route by reversing segment [i:j+1]
                new_route = (
                    best_route[:i] + best_route[i : j + 1][::-1] + best_route[j + 1 :]
                )

                new_distance = calculate_route_distance(new_route, locations)

                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
                    break  # Restart search with improved route

            if improved:
                break

    return best_route


def two_opt_solution(routes: List[List[int]], locations: np.ndarray) -> List[List[int]]:
    """
    Apply 2-opt improvement to all routes in a solution.

    Args:
        routes: List of routes, each route is list of node indices
        locations: (n, 2) array of node coordinates

    Returns:
        Improved solution with same route structure
    """
    return [two_opt_route(route, locations) for route in routes]


def run_benchmark(
    problem_name: str,
    approach: str,
    bin_strategy,
    tsp_strategy,
    backend: str = "numpy",
    num_iterations: int = 5,
    apply_2opt: bool = False,
) -> BenchmarkResult:
    """Run a single benchmark configuration."""
    # Load problem
    locations, demands, capacity, best_known = load_problem_from_db(problem_name)

    # Select backend
    xp = np
    if backend == "cupy":
        try:
            import cupy as cp

            xp = cp
            locations = cp.array(locations)
            demands = cp.array(demands)
        except ImportError:
            print(f"  Warning: CuPy not available, using NumPy")
            backend = "numpy"

    # Run multiple iterations for timing
    times = []
    routes = None

    for i in range(num_iterations):
        start_time = time.time()

        if approach == "bin_first":
            # Use compositional solver
            routes = lego_cvrp_solver(
                locations=locations,
                demands=demands,
                capacity=capacity,
                bin_packing_strategy=bin_strategy,
                tsp_strategy=tsp_strategy,
                xp=xp,
            )
        elif approach == "routing_first":
            # Use routing-first approach (tsp_strategy must have a compatible interface)
            # For now, use simple NN TSP
            routes = routing_first_approach(
                locations=locations,
                demands=demands,
                capacity=capacity,
                tsp_func=nearest_neighbor_tsp,
                xp=xp,
            )
        else:
            raise ValueError(f"Unknown approach: {approach}")

        # Apply 2-opt improvement if requested
        if apply_2opt:
            # Convert to NumPy for 2-opt (CPU-only for now)
            if backend == "cupy":
                locations_np = xp.asnumpy(locations)
            else:
                locations_np = locations

            routes = two_opt_solution(routes, locations_np)

        elapsed = time.time() - start_time
        times.append(elapsed)

    # Convert back to NumPy for validation
    if backend == "cupy":
        locations = xp.asnumpy(locations)
        demands = xp.asnumpy(demands)

    # Calculate metrics
    distance = calculate_solution_cost(routes, locations, np)
    num_routes = len(routes)
    distance_plus_routes = distance + 100 * num_routes
    bin_efficiency = calculate_bin_efficiency(routes, demands, capacity)
    valid = validate_solution(routes, demands, capacity)

    # Calculate gaps
    gap_distance = ((distance - best_known) / best_known * 100) if best_known else 0.0
    optimal_combined = (
        best_known + 100 * num_routes if best_known else distance_plus_routes
    )
    gap_combined = (
        ((distance_plus_routes - optimal_combined) / optimal_combined * 100)
        if optimal_combined > 0
        else 0.0
    )

    # Strategy names
    bin_name = bin_strategy.__class__.__name__ if bin_strategy else "N/A"
    tsp_name = tsp_strategy.__class__.__name__ if tsp_strategy else "N/A"

    return BenchmarkResult(
        approach=approach,
        bin_strategy=bin_name,
        tsp_strategy=tsp_name,
        problem=problem_name,
        distance=distance,
        num_routes=num_routes,
        distance_plus_routes=distance_plus_routes,
        bin_efficiency=bin_efficiency,
        time_mean=np.mean(times),
        time_std=np.std(times),
        time_min=np.min(times),
        time_max=np.max(times),
        gap_distance=gap_distance,
        gap_combined=gap_combined,
        valid=valid,
        with_2opt=apply_2opt,
        backend=backend,
        routes=routes,
    )


def print_results_table(results: List[BenchmarkResult]):
    """Print comprehensive results table."""
    print("\n" + "=" * 120)
    print("COMPREHENSIVE BENCHMARK RESULTS")
    print("=" * 120)

    # Group by problem
    by_problem = {}
    for r in results:
        if r.problem not in by_problem:
            by_problem[r.problem] = []
        by_problem[r.problem].append(r)

    for problem, prob_results in by_problem.items():
        print(f"\nProblem: {problem}")
        print("-" * 130)
        print(
            f"{'Approach':<15} {'Bin':<8} {'TSP':<15} {'Distance':>10} {'Routes':>7} {'Dist+Rts':>10} "
            f"{'Eff%':>6} {'Gap%':>7} {'2opt':<5} {'Time(ms)':>10} {'Valid':<5} {'Backend':<7}"
        )
        print("-" * 130)

        for r in prob_results:
            opt_mark = "✓" if r.with_2opt else " "
            print(
                f"{r.approach:<15} {r.bin_strategy:<8} {r.tsp_strategy:<15} "
                f"{r.distance:>10.2f} {r.num_routes:>7} {r.distance_plus_routes:>10.2f} "
                f"{r.bin_efficiency * 100:>6.1f} {r.gap_distance:>7.2f} "
                f"{opt_mark:<5} {r.time_mean * 1000:>10.2f} {str(r.valid):<5} {r.backend:<7}"
            )

        print()


if __name__ == "__main__":
    print("Starting comprehensive CVRP benchmark with 2-opt improvement...")
    print("Testing: bin-first vs routing-first, with and without 2-opt")
    print()

    # Test problems
    problems = ["eil22", "eil30", "eil51"]

    # Test configurations
    results = []

    # NumPy backend tests - WITHOUT 2-opt (baseline)
    print("=" * 80)
    print("PHASE 1: Testing WITHOUT 2-opt (baseline)")
    print("=" * 80)
    for problem in problems:
        print(f"\nBenchmarking {problem} (no 2-opt)...")

        # Test best combinations only (to save time)
        # FFD + Christofides (best from previous benchmark)
        print(f"  Testing bin_first: FFD + Christofides")
        result = run_benchmark(
            problem_name=problem,
            approach="bin_first",
            bin_strategy=FFDStrategy(),
            tsp_strategy=ChristofidesStrategy(),
            backend="numpy",
            num_iterations=5,
            apply_2opt=False,
        )
        results.append(result)

        # Routing-first approach
        print(f"  Testing routing_first: NN TSP → Split")
        result = run_benchmark(
            problem_name=problem,
            approach="routing_first",
            bin_strategy=None,
            tsp_strategy=None,
            backend="numpy",
            num_iterations=5,
            apply_2opt=False,
        )
        results.append(result)

    # NumPy backend tests - WITH 2-opt
    print("\n" + "=" * 80)
    print("PHASE 2: Testing WITH 2-opt improvement")
    print("=" * 80)
    for problem in problems:
        print(f"\nBenchmarking {problem} (with 2-opt)...")

        # FFD + Christofides + 2-opt
        print(f"  Testing bin_first + 2-opt: FFD + Christofides")
        result = run_benchmark(
            problem_name=problem,
            approach="bin_first",
            bin_strategy=FFDStrategy(),
            tsp_strategy=ChristofidesStrategy(),
            backend="numpy",
            num_iterations=5,
            apply_2opt=True,
        )
        results.append(result)

        # Routing-first + 2-opt
        print(f"  Testing routing_first + 2-opt: NN TSP → Split")
        result = run_benchmark(
            problem_name=problem,
            approach="routing_first",
            bin_strategy=None,
            tsp_strategy=None,
            backend="numpy",
            num_iterations=5,
            apply_2opt=True,
        )
        results.append(result)

    # Print results
    print_results_table(results)

    print("\n" + "=" * 130)
    print("BENCHMARK COMPLETE - 2-OPT IMPROVEMENT ANALYSIS")
    print("=" * 130)
