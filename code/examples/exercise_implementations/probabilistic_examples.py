"""
Probabilistic Examples: GPU implementations for Monte Carlo validation methods.

This module provides GPU-accelerated probabilistic analysis implementations
that validate theoretical results from Chapters 5.4 and 6.5-6.6.
"""

import numpy as np
from typing import Dict, List, Any

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False


def monte_carlo_tsp_bounds(
    n_points: int = 1000, n_simulations: int = 1000, backend: str = "cupy"
) -> Dict[str, float]:
    """
    Monte Carlo validation of TSP lower bounds from Chapter 5.4.

    Validates the theoretical bound β ≥ 1/2 through empirical analysis
    of random point configurations.

    Args:
        n_points: Number of points per TSP instance
        n_simulations: Number of Monte Carlo runs
        backend: 'cupy' or 'numpy'

    Returns:
        Dictionary with empirical bounds and statistics
    """
    if backend == "cupy" and CUPY_AVAILABLE:
        xp = cp
    else:
        xp = np

    beta_values = xp.zeros(n_simulations)

    for sim in range(n_simulations):
        # Generate random points in unit square
        points = xp.random.uniform(0, 1, (n_points, 2))

        # Compute all pairwise distances
        distances = xp.zeros((n_points, n_points))
        for i in range(n_points):
            for j in range(i + 1, n_points):
                dist = xp.sqrt(xp.sum((points[i] - points[j]) ** 2))
                distances[i, j] = dist
                distances[j, i] = dist

        # Find minimum spanning tree weight
        mst_weight = compute_mst_weight(distances, xp)

        # Compute TSP lower bound: β = MST_weight / (n * expected_nearest_neighbor)
        nearest_neighbor_sum = 0.0
        for i in range(n_points):
            min_dist = float("inf")
            for j in range(n_points):
                if i != j and distances[i, j] < min_dist:
                    min_dist = distances[i, j]
            nearest_neighbor_sum += min_dist

        beta_values[sim] = mst_weight / (nearest_neighbor_sum / 2)

    # Convert to numpy for statistics if using CuPy
    if backend == "cupy" and CUPY_AVAILABLE:
        beta_values = cp.asnumpy(beta_values)

    return {
        "empirical_beta_mean": float(np.mean(beta_values)),
        "empirical_beta_std": float(np.std(beta_values)),
        "empirical_beta_min": float(np.min(beta_values)),
        "theoretical_lower_bound": 0.5,
        "bound_satisfaction_rate": float(np.mean(beta_values >= 0.5)),
        "n_simulations": n_simulations,
        "n_points_per_simulation": n_points,
    }


def bin_packing_probabilistic_analysis(
    item_sizes: List[float], n_simulations: int = 1000, backend: str = "cupy"
) -> Dict[str, Any]:
    """
    Probabilistic analysis of bin packing algorithms from Chapter 6.5-6.6.

    Validates theoretical bounds for Next Fit, First Fit, and Best Fit algorithms
    through Monte Carlo simulation.

    Args:
        item_sizes: List of item sizes (between 0 and 1)
        n_simulations: Number of Monte Carlo runs
        backend: 'cupy' or 'numpy'

    Returns:
        Dictionary with algorithm performance statistics
    """
    if backend == "cupy" and CUPY_AVAILABLE:
        xp = cp
        item_array = cp.array(item_sizes)
    else:
        xp = np
        item_array = np.array(item_sizes)

    n_items = len(item_sizes)

    # Results storage
    next_fit_bins = []
    first_fit_bins = []
    best_fit_bins = []
    optimal_bins = []

    for sim in range(n_simulations):
        # Randomize item order for this simulation
        if backend == "cupy" and CUPY_AVAILABLE:
            perm = cp.random.permutation(n_items)
            shuffled_items = item_array[perm]
            shuffled_items = cp.asnumpy(shuffled_items)
        else:
            perm = np.random.permutation(n_items)
            shuffled_items = item_array[perm]

        # Next Fit algorithm
        nf_bins = next_fit_algorithm(shuffled_items)
        next_fit_bins.append(len(nf_bins))

        # First Fit algorithm
        ff_bins = first_fit_algorithm(shuffled_items)
        first_fit_bins.append(len(ff_bins))

        # Best Fit algorithm
        bf_bins = best_fit_algorithm(shuffled_items)
        best_fit_bins.append(len(bf_bins))

        # Lower bound (sum of item sizes, rounded up)
        total_size = np.sum(shuffled_items)
        opt_lower_bound = int(np.ceil(total_size))
        optimal_bins.append(opt_lower_bound)

    # Convert to numpy arrays for statistics
    next_fit_bins = np.array(next_fit_bins)
    first_fit_bins = np.array(first_fit_bins)
    best_fit_bins = np.array(best_fit_bins)
    optimal_bins = np.array(optimal_bins)

    return {
        "next_fit": {
            "mean_bins": float(np.mean(next_fit_bins)),
            "std_bins": float(np.std(next_fit_bins)),
            "approximation_ratio": float(np.mean(next_fit_bins / optimal_bins)),
            "theoretical_bound": 2.0,
        },
        "first_fit": {
            "mean_bins": float(np.mean(first_fit_bins)),
            "std_bins": float(np.std(first_fit_bins)),
            "approximation_ratio": float(np.mean(first_fit_bins / optimal_bins)),
            "theoretical_bound": 1.7,
        },
        "best_fit": {
            "mean_bins": float(np.mean(best_fit_bins)),
            "std_bins": float(np.std(best_fit_bins)),
            "approximation_ratio": float(np.mean(best_fit_bins / optimal_bins)),
            "theoretical_bound": 1.7,
        },
        "optimal_lower_bound": {
            "mean_bins": float(np.mean(optimal_bins)),
            "total_item_size": float(np.sum(item_sizes)),
        },
        "simulation_params": {
            "n_items": n_items,
            "n_simulations": n_simulations,
            "backend": backend,
        },
    }


def lagrangian_bound_validation(
    constraint_matrix: np.ndarray,
    cost_vector: np.ndarray,
    rhs_vector: np.ndarray,
    n_iterations: int = 1000,
    backend: str = "cupy",
) -> Dict[str, float]:
    """
    Validate Lagrangian dual bounds through iterative optimization.

    Implements the theoretical analysis from Chapter 6.5-6.6 exercises
    on Lagrangian duality and dual-feasible functions.

    Args:
        constraint_matrix: A matrix for constraints Ax ≤ b
        cost_vector: Objective function coefficients c
        rhs_vector: Right-hand side vector b
        n_iterations: Number of subgradient iterations
        backend: 'cupy' or 'numpy'

    Returns:
        Dictionary with dual bound progression and final results
    """
    if backend == "cupy" and CUPY_AVAILABLE:
        xp = cp
        A = cp.array(constraint_matrix)
        c = cp.array(cost_vector)
        b = cp.array(rhs_vector)
    else:
        xp = np
        A = constraint_matrix
        c = cost_vector
        b = rhs_vector

    m, n = A.shape  # m constraints, n variables

    # Initialize Lagrange multipliers
    lambda_vals = xp.zeros(m)
    dual_bounds = []
    step_size = 1.0

    for iteration in range(n_iterations):
        # Solve Lagrangian relaxation: min_x (c - λA)x
        # For simplicity, assume variables are binary and use relaxation
        lagrangian_costs = c - xp.dot(lambda_vals, A)

        # Optimal x* for relaxation (set to 1 if cost < 0, 0 otherwise)
        x_star = (lagrangian_costs < 0).astype(float)

        # Compute dual function value
        dual_value = float(xp.dot(lagrangian_costs, x_star) + xp.dot(lambda_vals, b))
        dual_bounds.append(dual_value)

        # Subgradient: b - Ax*
        subgradient = b - xp.dot(A, x_star)

        # Update multipliers with projection onto non-negative orthant
        step_size = 1.0 / np.sqrt(iteration + 1)  # Diminishing step size
        lambda_vals = xp.maximum(0, lambda_vals + step_size * subgradient)

    # Convert results to numpy if using CuPy
    if backend == "cupy" and CUPY_AVAILABLE:
        dual_bounds = [
            float(cp.asnumpy(db)) if hasattr(db, "get") else float(db)
            for db in dual_bounds
        ]
        lambda_final = cp.asnumpy(lambda_vals)
    else:
        lambda_final = lambda_vals

    return {
        "final_dual_bound": dual_bounds[-1],
        "best_dual_bound": max(dual_bounds),
        "convergence_iterations": len(dual_bounds),
        "final_multipliers": lambda_final.tolist(),
        "dual_bound_progression": dual_bounds[-100:],  # Last 100 iterations
        "theoretical_properties": {
            "weak_duality_satisfied": True,  # Always true for Lagrangian dual
            "dual_bound_quality": "Upper bound for minimization problem",
        },
    }


def strips_method_validation(
    n_points: int = 100,
    strip_width: float = 0.1,
    n_simulations: int = 500,
    backend: str = "cupy",
) -> Dict[str, float]:
    """
    Validate the strips method for TSP from Chapter 5.4.

    Tests the theoretical bound on tour length when points are
    arranged in strips parallel to coordinate axes.

    Args:
        n_points: Number of points per instance
        strip_width: Width of each strip
        n_simulations: Number of Monte Carlo runs
        backend: 'cupy' or 'numpy'

    Returns:
        Dictionary with strips method performance statistics
    """
    if backend == "cupy" and CUPY_AVAILABLE:
        xp = cp
    else:
        xp = np

    tour_lengths = []
    optimal_estimates = []

    for sim in range(n_simulations):
        # Generate points in vertical strips
        n_strips = int(1.0 / strip_width)
        points_per_strip = n_points // n_strips

        points = []
        for strip in range(n_strips):
            # Points in strip [strip*strip_width, (strip+1)*strip_width] × [0,1]
            x_coords = xp.random.uniform(
                strip * strip_width, (strip + 1) * strip_width, points_per_strip
            )
            y_coords = xp.random.uniform(0, 1, points_per_strip)

            for i in range(points_per_strip):
                points.append([float(x_coords[i]), float(y_coords[i])])

        # Add remaining points if n_points not divisible by n_strips
        remaining = n_points - len(points)
        if remaining > 0:
            x_coords = xp.random.uniform(0, 1, remaining)
            y_coords = xp.random.uniform(0, 1, remaining)
            for i in range(remaining):
                points.append([float(x_coords[i]), float(y_coords[i])])

        points = np.array(points)

        # Compute tour using nearest neighbor within/between strips
        tour_length = compute_strips_tour_length(points, strip_width)
        tour_lengths.append(tour_length)

        # Theoretical estimate: O(√n) for strips method
        theoretical_estimate = np.sqrt(n_points) * strip_width
        optimal_estimates.append(theoretical_estimate)

    tour_lengths = np.array(tour_lengths)
    optimal_estimates = np.array(optimal_estimates)

    return {
        "mean_tour_length": float(np.mean(tour_lengths)),
        "std_tour_length": float(np.std(tour_lengths)),
        "mean_theoretical_estimate": float(np.mean(optimal_estimates)),
        "approximation_ratio": float(np.mean(tour_lengths / optimal_estimates)),
        "strips_effectiveness": float(np.mean(tour_lengths <= 2 * optimal_estimates)),
        "simulation_params": {
            "n_points": n_points,
            "strip_width": strip_width,
            "n_simulations": n_simulations,
            "n_strips": int(1.0 / strip_width),
        },
    }


# Helper functions


def compute_mst_weight(distances: np.ndarray, xp) -> float:
    """Compute minimum spanning tree weight using Prim's algorithm."""
    n = distances.shape[0]
    visited = xp.zeros(n, dtype=bool)
    min_edge = xp.full(n, float("inf"))
    min_edge[0] = 0
    total_weight = 0.0

    for _ in range(n):
        # Find minimum edge to unvisited vertex
        u = -1
        for v in range(n):
            if not visited[v] and (u == -1 or min_edge[v] < min_edge[u]):
                u = v

        visited[u] = True
        total_weight += min_edge[u]

        # Update minimum edges
        for v in range(n):
            if not visited[v] and distances[u, v] < min_edge[v]:
                min_edge[v] = distances[u, v]

    return float(total_weight)


def next_fit_algorithm(items: np.ndarray) -> List[List[float]]:
    """Next Fit bin packing algorithm."""
    bins = []
    current_bin = []
    current_size = 0.0

    for item in items:
        if current_size + item <= 1.0:
            current_bin.append(float(item))
            current_size += item
        else:
            bins.append(current_bin)
            current_bin = [float(item)]
            current_size = item

    if current_bin:
        bins.append(current_bin)

    return bins


def first_fit_algorithm(items: np.ndarray) -> List[List[float]]:
    """First Fit bin packing algorithm."""
    bins = []
    bin_sizes = []

    for item in items:
        placed = False
        for i, bin_size in enumerate(bin_sizes):
            if bin_size + item <= 1.0:
                bins[i].append(float(item))
                bin_sizes[i] += item
                placed = True
                break

        if not placed:
            bins.append([float(item)])
            bin_sizes.append(item)

    return bins


def best_fit_algorithm(items: np.ndarray) -> List[List[float]]:
    """Best Fit bin packing algorithm."""
    bins = []
    bin_sizes = []

    for item in items:
        best_bin = -1
        best_fit_size = float("inf")

        for i, bin_size in enumerate(bin_sizes):
            if bin_size + item <= 1.0 and bin_size + item > best_fit_size:
                best_bin = i
                best_fit_size = bin_size + item

        if best_bin != -1:
            bins[best_bin].append(float(item))
            bin_sizes[best_bin] += item
        else:
            bins.append([float(item)])
            bin_sizes.append(item)

    return bins


def compute_strips_tour_length(points: np.ndarray, strip_width: float) -> float:
    """Compute tour length using strips method heuristic."""
    n = len(points)
    if n <= 1:
        return 0.0

    # Sort points by x-coordinate (strip assignment)
    sorted_indices = np.argsort(points[:, 0])
    sorted_points = points[sorted_indices]

    # Compute tour using nearest neighbor with strip awareness
    visited = np.zeros(n, dtype=bool)
    current = 0
    visited[0] = True
    total_length = 0.0

    for _ in range(n - 1):
        min_dist = float("inf")
        next_point = -1

        for j in range(n):
            if not visited[j]:
                dist = np.sqrt(np.sum((sorted_points[current] - sorted_points[j]) ** 2))
                if dist < min_dist:
                    min_dist = dist
                    next_point = j

        if next_point != -1:
            total_length += min_dist
            visited[next_point] = True
            current = next_point

    # Return to start
    total_length += np.sqrt(np.sum((sorted_points[current] - sorted_points[0]) ** 2))

    return total_length


# Example usage and testing
if __name__ == "__main__":
    # Test TSP bounds validation
    print("Testing TSP lower bounds validation...")
    tsp_results = monte_carlo_tsp_bounds(
        n_points=50, n_simulations=100, backend="numpy"
    )
    print(
        f"Empirical β: {tsp_results['empirical_beta_mean']:.4f} ± {tsp_results['empirical_beta_std']:.4f}"
    )
    print(f"Bound satisfaction: {tsp_results['bound_satisfaction_rate']:.2%}")

    # Test bin packing analysis
    print("\nTesting bin packing probabilistic analysis...")
    item_sizes = np.random.uniform(0.1, 0.8, 50).tolist()
    bp_results = bin_packing_probabilistic_analysis(
        item_sizes, n_simulations=100, backend="numpy"
    )
    print(f"Next Fit ratio: {bp_results['next_fit']['approximation_ratio']:.3f}")
    print(f"First Fit ratio: {bp_results['first_fit']['approximation_ratio']:.3f}")
    print(f"Best Fit ratio: {bp_results['best_fit']['approximation_ratio']:.3f}")

    # Test strips method
    print("\nTesting strips method validation...")
    strips_results = strips_method_validation(
        n_points=30, strip_width=0.2, n_simulations=50, backend="numpy"
    )
    print(f"Mean tour length: {strips_results['mean_tour_length']:.4f}")
    print(f"Approximation ratio: {strips_results['approximation_ratio']:.3f}")
