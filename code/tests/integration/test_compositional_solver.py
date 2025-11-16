"""
Integration tests for compositional CVRP solver.

Tests the complete pipeline: Bin Packing → TSP Construction → Routes.

Test Cases:
    1. FFD + Nearest Neighbor combination
    2. BFD + Christofides combination
    3. Capacity constraint validation
    4. Customer coverage (all visited exactly once)
    5. Depot handling (all routes start and end at depot)
    6. Edge case: Single customer
    7. Edge case: All customers in one route
    8. TSP mode: Auto-detection, custom strategy
    9. Large problem: 30-customer CVRP, 50-node TSP

Dependencies:
    pytest, numpy, cupy (optional)
"""

import pytest
import numpy as np

# Import strategies and solver
from src.algorithms.strategies.bin_packing_strategies import FFDStrategy, BFDStrategy
from code.src.algorithms.strategies.construction_strategies import (
    NearestNeighborStrategy,
    ChristofidesStrategy,
)
from src.algorithms.compositional_cvrp_solver import lego_cvrp_solver


# ==============================================================================
# TEST FIXTURES
# ==============================================================================


@pytest.fixture
def small_problem():
    """Small CVRP instance for basic testing."""
    locations = np.array(
        [
            [0.0, 0.0],  # 0: Depot
            [1.0, 0.0],  # 1: Customer
            [2.0, 0.0],  # 2: Customer
            [0.0, 1.0],  # 3: Customer
            [0.0, 2.0],  # 4: Customer
        ]
    )
    demands = np.array([0, 20, 30, 25, 15])
    capacity = 50
    return locations, demands, capacity


@pytest.fixture
def medium_problem():
    """Medium CVRP instance with 10 customers."""
    np.random.seed(42)
    n_customers = 10
    locations = np.random.rand(n_customers + 1, 2) * 10.0
    locations[0] = [0.0, 0.0]  # Depot at origin
    demands = np.random.randint(5, 30, size=n_customers + 1)
    demands[0] = 0  # Depot demand
    capacity = 60
    return locations, demands, capacity


# ==============================================================================
# BASIC COMBINATION TESTS
# ==============================================================================


def test_ffd_nearest_neighbor(small_problem):
    """Test FFD + Nearest Neighbor strategy combination."""
    locations, demands, capacity = small_problem

    routes = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=NearestNeighborStrategy(),
        xp=np,
    )

    # Basic validation
    assert isinstance(routes, list), "Routes should be a list"
    assert len(routes) > 0, "Should produce at least one route"

    # Check each route
    for route in routes:
        assert isinstance(route, list), "Each route should be a list"
        assert route[0] == 0, "Route should start at depot"
        assert route[-1] == 0, "Route should end at depot"


def test_bfd_christofides(small_problem):
    """Test BFD + Christofides strategy combination."""
    locations, demands, capacity = small_problem

    routes = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=BFDStrategy(),
        tsp_strategy=ChristofidesStrategy(),
        xp=np,
    )

    # Basic validation
    assert isinstance(routes, list), "Routes should be a list"
    assert len(routes) > 0, "Should produce at least one route"

    # Check each route
    for route in routes:
        assert isinstance(route, list), "Each route should be a list"
        assert route[0] == 0, "Route should start at depot"
        assert route[-1] == 0, "Route should end at depot"


# ==============================================================================
# CONSTRAINT VALIDATION TESTS
# ==============================================================================


def test_capacity_constraint(small_problem):
    """Test that all routes respect vehicle capacity."""
    locations, demands, capacity = small_problem

    routes = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=NearestNeighborStrategy(),
        xp=np,
    )

    # Check capacity for each route
    for i, route in enumerate(routes):
        # Calculate total demand (exclude depot appearances)
        route_demand = sum(demands[customer] for customer in route[1:-1])
        assert route_demand <= capacity, (
            f"Route {i} violates capacity: {route_demand} > {capacity}"
        )


def test_customer_coverage(medium_problem):
    """Test that all customers are visited exactly once."""
    locations, demands, capacity = medium_problem
    n_customers = len(locations) - 1  # Exclude depot

    routes = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=BFDStrategy(),
        tsp_strategy=ChristofidesStrategy(),
        xp=np,
    )

    # Collect all visited customers
    visited = set()
    for route in routes:
        # Exclude depot appearances (first and last)
        customers_in_route = route[1:-1]
        for customer in customers_in_route:
            assert customer not in visited, (
                f"Customer {customer} visited multiple times"
            )
            visited.add(customer)

    # Check all customers visited
    expected_customers = set(range(1, n_customers + 1))
    assert visited == expected_customers, (
        f"Not all customers visited: {expected_customers - visited} missing"
    )


def test_depot_handling(small_problem):
    """Test that all routes start and end at depot."""
    locations, demands, capacity = small_problem

    routes = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=NearestNeighborStrategy(),
        xp=np,
    )

    for i, route in enumerate(routes):
        assert route[0] == 0, f"Route {i} doesn't start at depot: {route[0]}"
        assert route[-1] == 0, f"Route {i} doesn't end at depot: {route[-1]}"
        assert len(route) >= 3, f"Route {i} has no customers: {route}"


# ==============================================================================
# EDGE CASE TESTS
# ==============================================================================


def test_single_customer():
    """Test problem with only one customer."""
    locations = np.array([[0.0, 0.0], [1.0, 1.0]])  # Depot + 1 customer
    demands = np.array([0, 20])
    capacity = 50

    routes = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=NearestNeighborStrategy(),
        xp=np,
    )

    assert len(routes) == 1, "Should have exactly one route"
    assert routes[0] == [0, 1, 0], f"Route should be [0, 1, 0], got {routes[0]}"


def test_all_customers_one_route():
    """Test when all customers fit in one vehicle."""
    locations = np.array(
        [
            [0.0, 0.0],  # Depot
            [1.0, 0.0],
            [2.0, 0.0],
            [3.0, 0.0],
        ]
    )
    demands = np.array([0, 10, 10, 10])  # Total: 30
    capacity = 100  # Much larger than total demand

    routes = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=NearestNeighborStrategy(),
        xp=np,
    )

    assert len(routes) == 1, "All customers should fit in one route"
    assert routes[0][0] == 0 and routes[0][-1] == 0, "Route should start/end at depot"
    assert set(routes[0][1:-1]) == {1, 2, 3}, "Route should visit all customers"


# ==============================================================================
# INPUT VALIDATION TESTS
# ==============================================================================


def test_invalid_locations_shape():
    """Test error handling for invalid locations array."""
    locations = np.array([0, 0, 1, 1])  # 1D array (invalid)
    demands = np.array([0, 10])
    capacity = 50

    with pytest.raises(ValueError, match="locations must be 2D"):
        lego_cvrp_solver(
            locations=locations,
            demands=demands,
            capacity=capacity,
            bin_packing_strategy=FFDStrategy(),
            tsp_strategy=NearestNeighborStrategy(),
            xp=np,
        )


def test_demand_exceeds_capacity():
    """Test error handling when demand exceeds capacity."""
    locations = np.array([[0, 0], [1, 1]])
    demands = np.array([0, 100])  # Demand 100 > capacity 50
    capacity = 50

    with pytest.raises(ValueError, match="demands exceed capacity"):
        lego_cvrp_solver(
            locations=locations,
            demands=demands,
            capacity=capacity,
            bin_packing_strategy=FFDStrategy(),
            tsp_strategy=NearestNeighborStrategy(),
            xp=np,
        )


def test_locations_demands_mismatch():
    """Test error handling for locations/demands length mismatch."""
    locations = np.array([[0, 0], [1, 1], [2, 2]])  # 3 locations
    demands = np.array([0, 10])  # 2 demands (mismatch)
    capacity = 50

    with pytest.raises(ValueError, match="length mismatch"):
        lego_cvrp_solver(
            locations=locations,
            demands=demands,
            capacity=capacity,
            bin_packing_strategy=FFDStrategy(),
            tsp_strategy=NearestNeighborStrategy(),
            xp=np,
        )


# ==============================================================================
# PARAMETRIZED TESTS (All Strategy Combinations)
# ==============================================================================


@pytest.mark.parametrize(
    "bin_packing_strategy,tsp_strategy",
    [
        (FFDStrategy(), NearestNeighborStrategy()),
        (FFDStrategy(), ChristofidesStrategy()),
        (BFDStrategy(), NearestNeighborStrategy()),
        (BFDStrategy(), ChristofidesStrategy()),
    ],
)
def test_all_strategy_combinations(small_problem, bin_packing_strategy, tsp_strategy):
    """Test all valid strategy combinations produce valid routes."""
    locations, demands, capacity = small_problem

    routes = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=bin_packing_strategy,
        tsp_strategy=tsp_strategy,
        xp=np,
    )

    # Basic validation for all combinations
    assert len(routes) > 0, "Should produce at least one route"

    for route in routes:
        assert route[0] == 0 and route[-1] == 0, "Route should start/end at depot"
        route_demand = sum(demands[customer] for customer in route[1:-1])
        assert route_demand <= capacity, f"Route violates capacity: {route_demand}"


# ==============================================================================
# TSP MODE TESTS (Auto-detection without demands/capacity)
# ==============================================================================


def test_tsp_mode_default_strategy():
    """Test TSP mode (no demands/capacity) with default strategy."""
    locations = np.array(
        [
            [0.0, 0.0],  # Start
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
            [2.0, 2.0],
        ]
    )

    # Call without demands/capacity - should auto-detect TSP mode
    routes = lego_cvrp_solver(
        locations=locations,
        xp=np,
    )

    # TSP mode returns single route wrapped in list
    assert isinstance(routes, list), "Solver should return list of routes"
    assert len(routes) == 1, "TSP mode should return exactly one route"

    route = routes[0]
    assert len(route) == len(locations) + 1, (
        f"TSP route should visit all {len(locations)} locations and return to start"
    )
    assert route[0] == 0 and route[-1] == 0, (
        "TSP route should start and end at first location"
    )

    # Validate node coverage: each node should appear correct number of times
    from collections import Counter

    node_counts = Counter(route)

    # Node 0 (depot) should appear exactly twice (start and end)
    assert node_counts[0] == 2, (
        f"Depot (node 0) should appear at start and end, got {node_counts[0]} times"
    )

    # All other nodes should appear exactly once
    for node in range(1, len(locations)):
        assert node_counts[node] == 1, (
            f"Node {node} should appear exactly once, got {node_counts[node]} times"
        )


def test_tsp_mode_custom_strategy():
    """Test TSP mode with custom strategy (Christofides)."""
    locations = np.array(
        [
            [0.0, 0.0],
            [3.0, 0.0],
            [3.0, 4.0],
            [0.0, 4.0],
        ]
    )

    routes = lego_cvrp_solver(
        locations=locations,
        tsp_strategy=ChristofidesStrategy(),  # Custom strategy for TSP mode
        xp=np,
    )

    assert isinstance(routes, list), "Solver should return list of routes"
    assert len(routes) == 1, "TSP mode should return exactly one route"

    route = routes[0]
    assert route[0] == 0 and route[-1] == 0, "TSP route should form closed tour"
    assert len(set(route[:-1])) == len(locations), "All locations should be visited"


def test_tsp_mode_rejects_bin_packing():
    """Test that TSP mode rejects bin packing strategy parameter."""
    locations = np.array([[0, 0], [1, 1], [2, 2]])

    with pytest.raises(
        ValueError, match="bin_packing_strategy provided but demands/capacity are None"
    ):
        lego_cvrp_solver(
            locations=locations,
            bin_packing_strategy=FFDStrategy(),  # Invalid for TSP mode
            xp=np,
        )


# ==============================================================================
# LARGE PROBLEM TESTS (Scalability)
# ==============================================================================


def test_large_cvrp_problem():
    """Test scalability with 30 customers (realistic CVRP problem size)."""
    np.random.seed(42)  # Reproducibility

    n_customers = 30
    locations = np.random.rand(n_customers + 1, 2) * 100.0  # 30 customers + depot
    locations[0] = [50.0, 50.0]  # Depot at center

    # Demands: 10-30 units per customer
    demands = np.concatenate(
        [
            [0],  # Depot has 0 demand
            np.random.randint(10, 31, size=n_customers),
        ]
    )

    capacity = 100  # Vehicle capacity

    routes = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=NearestNeighborStrategy(),  # Fast heuristic for large problem
        xp=np,
    )

    # Validation
    assert len(routes) > 0, "Should produce at least one route"

    visited = set()
    for route in routes:
        # Depot handling
        assert route[0] == 0 and route[-1] == 0, "Route should start/end at depot"

        # Capacity constraint
        route_demand = sum(demands[customer] for customer in route[1:-1])
        assert route_demand <= capacity, (
            f"Route violates capacity: {route_demand} > {capacity}"
        )

        # Coverage tracking
        for customer in route[1:-1]:
            assert customer not in visited, (
                f"Customer {customer} visited multiple times"
            )
            visited.add(customer)

    # All customers visited
    expected_customers = set(range(1, n_customers + 1))
    assert visited == expected_customers, (
        f"Not all customers visited: {expected_customers - visited} missing"
    )


def test_large_tsp_problem():
    """Test scalability with 50-node TSP (larger than typical test cases)."""
    np.random.seed(123)  # Reproducibility

    n_nodes = 50
    locations = np.random.rand(n_nodes, 2) * 100.0

    routes = lego_cvrp_solver(
        locations=locations,
        tsp_strategy=NearestNeighborStrategy(),  # Fast for large problem
        xp=np,
    )

    # TSP mode returns single route wrapped in list
    assert isinstance(routes, list), "Solver should return list of routes"
    assert len(routes) == 1, "TSP mode should return exactly one route"

    route = routes[0]
    assert len(route) == n_nodes + 1, f"Should visit all {n_nodes} nodes"
    assert route[0] == 0 and route[-1] == 0, "Should form closed tour"

    # All nodes visited exactly once
    visited_count = {}
    for node in route[:-1]:  # Exclude final depot return
        visited_count[node] = visited_count.get(node, 0) + 1

    assert len(visited_count) == n_nodes, f"Should visit {n_nodes} unique nodes"
    assert all(count == 1 for count in visited_count.values()), (
        "Each node should be visited exactly once"
    )


# ==============================================================================
# BIN PACKING DEFAULT TEST (Task #13 - bin_packing "necessary" bug fix)
# ==============================================================================


def test_cvrp_uses_default_bin_packing(small_problem):
    """
    Test that bin_packing_strategy is OPTIONAL and defaults to FFD.

    This test verifies the fix for the "bin_packing necessary" bug where
    tests made it appear that bin_packing_strategy was a required parameter,
    when in fact it should default to FFDStrategy() if not provided.

    Background:
        - Implementation: compositional_cvrp_solver.py correctly defaults to FFDStrategy()
        - Bug: ALL 19 existing tests explicitly pass bin_packing_strategy
        - Result: Users might think bin_packing_strategy is required
        - Fix: Add this test demonstrating CVRP works without explicit bin_packing

    See Also:
        - Milestone 1 task breakdown
        - compositional_cvrp_solver.py lines 183-195
    """
    locations, demands, capacity = small_problem

    # Call solver WITHOUT bin_packing_strategy parameter
    # Should automatically default to FFDStrategy()
    routes = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        tsp_strategy=NearestNeighborStrategy(),
        xp=np,
        # NO bin_packing_strategy parameter - should auto-default to FFD
    )

    # Verify solution is valid
    assert isinstance(routes, list), "Should return list of routes"
    assert len(routes) > 0, "Should have at least one route"

    # All routes should be valid
    for route in routes:
        assert route[0] == 0 and route[-1] == 0, "Route must start/end at depot"

    # All customers covered exactly once
    all_customers = set()
    for route in routes:
        for node in route[1:-1]:  # Exclude depot
            all_customers.add(node)

    expected_customers = set(range(1, len(locations)))
    assert all_customers == expected_customers, "All customers must be visited once"


# ==============================================================================
# NOTES
# ==============================================================================

# Testing Strategy:
# 1. Basic combination tests: Verify FFD+NN and BFD+Christofides work
# 2. Constraint tests: Capacity, coverage, depot handling
# 3. Edge cases: Single customer, all in one route
# 4. Input validation: Invalid shapes, capacity violations, mismatches
# 5. Parametrized tests: All 4 strategy combinations
# 6. TSP mode tests: Auto-detection, custom strategy, parameter validation
# 7. Large problem tests: 30-customer CVRP, 50-node TSP (scalability)
# 8. Default bin packing: Verify bin_packing_strategy is optional (defaults to FFD)

# Future Tests (when GPU backend is available):
# - test_cupy_backend(): Test with xp=cupy
# - test_clustering_integration(): Test with optional clustering_strategy
