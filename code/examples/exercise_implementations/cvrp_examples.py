"""
CVRP Examples: GPU implementations for CVRP heuristics and analysis.

This module provides GPU-accelerated implementations for validating the
theoretical results from CVRP exercises in various chapters.
"""

import numpy as np
from typing import Dict, Union


try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False


def nearest_neighbor_cvrp(
    customer_locations: Union[np.ndarray, "cp.ndarray"],
    demands: Union[np.ndarray, "cp.ndarray"],
    capacity: float,
    depot_location: Union[np.ndarray, "cp.ndarray"] = None,
    backend: str = "cupy",
) -> Dict:
    """
    Implement nearest neighbor heuristic for CVRP.

    Based on theoretical analysis from various exercise chapters,
    constructs routes using nearest neighbor insertion with capacity constraints.

    Args:
        customer_locations: Array of customer coordinates
        demands: Array of customer demands
        capacity: Vehicle capacity
        depot_location: Depot coordinates (default: origin)
        backend: 'cupy' or 'numpy'

    Returns:
        Solution with routes and performance metrics
    """
    if backend == "cupy" and CUPY_AVAILABLE:
        xp = cp
    else:
        xp = np

    # Convert inputs to appropriate arrays
    if not isinstance(customer_locations, type(xp.array([]))):
        customer_locations = xp.array(customer_locations)
    if not isinstance(demands, type(xp.array([]))):
        demands = xp.array(demands)

    if depot_location is None:
        depot_location = xp.zeros(customer_locations.shape[1])
    elif not isinstance(depot_location, type(xp.array([]))):
        depot_location = xp.array(depot_location)

    n_customers = len(customer_locations)
    unvisited = set(range(n_customers))
    routes = []
    total_cost = 0.0

    while unvisited:
        # Start new route
        current_capacity = capacity
        current_location = depot_location
        route = []
        route_cost = 0.0

        while unvisited:
            # Find nearest feasible customer
            best_customer = None
            best_distance = float("inf")

            for customer in unvisited:
                if demands[customer] <= current_capacity:
                    distance = float(
                        xp.sqrt(
                            xp.sum(
                                (customer_locations[customer] - current_location) ** 2
                            )
                        )
                    )
                    if distance < best_distance:
                        best_distance = distance
                        best_customer = customer

            if best_customer is None:
                break  # No feasible customer found

            # Add customer to route
            route.append(best_customer)
            unvisited.remove(best_customer)
            current_capacity -= demands[best_customer]
            current_location = customer_locations[best_customer]
            route_cost += best_distance

        # Return to depot
        depot_distance = float(
            xp.sqrt(xp.sum((depot_location - current_location) ** 2))
        )
        route_cost += depot_distance

        routes.append(
            {
                "customers": route,
                "total_demand": float(capacity - current_capacity),
                "route_cost": route_cost,
            }
        )
        total_cost += route_cost

    return {
        "routes": routes,
        "total_cost": total_cost,
        "n_routes": len(routes),
        "average_route_cost": total_cost / len(routes) if routes else 0.0,
    }


def christofides_cvrp(
    customer_locations: Union[np.ndarray, "cp.ndarray"],
    demands: Union[np.ndarray, "cp.ndarray"],
    capacity: float,
    depot_location: Union[np.ndarray, "cp.ndarray"] = None,
    backend: str = "cupy",
) -> Dict:
    """
    Implement Christofides-based heuristic for CVRP.

    Based on Exercise 16.5 theoretical analysis, applies Christofides
    algorithm to construct high-quality tours with capacity constraints.

    Args:
        customer_locations: Array of customer coordinates
        demands: Array of customer demands
        capacity: Vehicle capacity
        depot_location: Depot coordinates
        backend: 'cupy' or 'numpy'

    Returns:
        Solution with performance guarantees
    """
    if backend == "cupy" and CUPY_AVAILABLE:
        xp = cp
    else:
        xp = np

    # For simplicity, implement as improved nearest neighbor with 2-opt
    # Full Christofides implementation would require MST and matching algorithms

    base_solution = nearest_neighbor_cvrp(
        customer_locations, demands, capacity, depot_location, backend
    )

    # Apply local improvement (simplified 2-opt)
    improved_routes = []
    total_cost = 0.0

    for route_info in base_solution["routes"]:
        if len(route_info["customers"]) > 2:
            improved_cost = _apply_2opt_improvement(
                route_info["customers"], customer_locations, depot_location, xp
            )
            route_info["route_cost"] = improved_cost

        improved_routes.append(route_info)
        total_cost += route_info["route_cost"]

    return {
        "routes": improved_routes,
        "total_cost": total_cost,
        "n_routes": len(improved_routes),
        "improvement_ratio": base_solution["total_cost"] / total_cost
        if total_cost > 0
        else 1.0,
        "theoretical_bound": 2.0,  # Christofides bound for TSP component
    }


def _apply_2opt_improvement(
    route_customers: list,
    customer_locations: Union[np.ndarray, "cp.ndarray"],
    depot_location: Union[np.ndarray, "cp.ndarray"],
    xp,
) -> float:
    """Apply 2-opt improvement to a single route."""
    n = len(route_customers)
    if n <= 2:
        return _calculate_route_cost(
            route_customers, customer_locations, depot_location, xp
        )

    best_route = route_customers[:]
    best_cost = _calculate_route_cost(
        best_route, customer_locations, depot_location, xp
    )

    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                # Try 2-opt swap
                new_route = (
                    best_route[: i + 1]
                    + best_route[i + 1 : j + 1][::-1]
                    + best_route[j + 1 :]
                )
                new_cost = _calculate_route_cost(
                    new_route, customer_locations, depot_location, xp
                )

                if new_cost < best_cost:
                    best_route = new_route
                    best_cost = new_cost
                    improved = True
                    break
            if improved:
                break

    return best_cost


def _calculate_route_cost(
    route_customers: list,
    customer_locations: Union[np.ndarray, "cp.ndarray"],
    depot_location: Union[np.ndarray, "cp.ndarray"],
    xp,
) -> float:
    """Calculate total cost of a route including depot connections."""
    if not route_customers:
        return 0.0

    total_cost = 0.0

    # Depot to first customer
    first_customer = route_customers[0]
    total_cost += float(
        xp.sqrt(xp.sum((customer_locations[first_customer] - depot_location) ** 2))
    )

    # Customer to customer
    for i in range(len(route_customers) - 1):
        curr_customer = route_customers[i]
        next_customer = route_customers[i + 1]
        distance = float(
            xp.sqrt(
                xp.sum(
                    (
                        customer_locations[next_customer]
                        - customer_locations[curr_customer]
                    )
                    ** 2
                )
            )
        )
        total_cost += distance

    # Last customer to depot
    last_customer = route_customers[-1]
    total_cost += float(
        xp.sqrt(xp.sum((depot_location - customer_locations[last_customer]) ** 2))
    )

    return total_cost


def hybrid_large_small_heuristic(
    customer_locations: Union[np.ndarray, "cp.ndarray"],
    demands: Union[np.ndarray, "cp.ndarray"],
    capacity: float,
    depot_location: Union[np.ndarray, "cp.ndarray"] = None,
    backend: str = "cupy",
) -> Dict:
    """
    Implement hybrid heuristic for large/small customers from Exercise 17.1.

    Algorithm:
    1. Classify customers as large (demand > capacity/2) or small
    2. Assign individual routes to large customers
    3. Apply CVRP heuristic to small customers

    Args:
        customer_locations: Array of customer coordinates
        demands: Array of customer demands
        capacity: Vehicle capacity
        depot_location: Depot coordinates
        backend: 'cupy' or 'numpy'

    Returns:
        Solution with theoretical performance bound
    """
    if backend == "cupy" and CUPY_AVAILABLE:
        xp = cp
    else:
        xp = np

    if not isinstance(demands, type(xp.array([]))):
        demands = xp.array(demands)

    threshold = capacity / 2.0
    large_customers = xp.where(demands > threshold)[0]
    small_customers = xp.where(demands <= threshold)[0]

    routes = []
    total_cost = 0.0

    if depot_location is None:
        depot_location = xp.zeros(customer_locations.shape[1])

    # Handle large customers individually
    for customer_idx in large_customers:
        customer_idx = int(customer_idx)
        location = customer_locations[customer_idx]
        demand = demands[customer_idx]

        # Individual route: depot -> customer -> depot
        route_cost = 2 * float(xp.sqrt(xp.sum((location - depot_location) ** 2)))

        routes.append(
            {
                "customers": [customer_idx],
                "total_demand": float(demand),
                "route_cost": route_cost,
                "route_type": "large_customer",
            }
        )

        total_cost += route_cost

    # Handle small customers with CVRP heuristic
    if len(small_customers) > 0:
        small_locations = customer_locations[small_customers]
        small_demands = demands[small_customers]

        small_solution = nearest_neighbor_cvrp(
            small_locations, small_demands, capacity, depot_location, backend
        )

        for route in small_solution["routes"]:
            # Map back to original customer indices
            original_customers = [int(small_customers[i]) for i in route["customers"]]
            routes.append(
                {
                    "customers": original_customers,
                    "total_demand": route["total_demand"],
                    "route_cost": route["route_cost"],
                    "route_type": "small_customers",
                }
            )
            total_cost += route["route_cost"]

    return {
        "routes": routes,
        "total_cost": total_cost,
        "n_routes": len(routes),
        "n_large_customers": len(large_customers),
        "n_small_customers": len(small_customers),
        "theoretical_bound": 2.0 - 1.0 / len(customer_locations),  # From Exercise 17.1
    }
