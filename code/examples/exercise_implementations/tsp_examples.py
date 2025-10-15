"""
TSP Examples: GPU implementations for TSP analysis and bounds verification.

This module provides GPU-accelerated implementations for validating the
theoretical results from Chapter 5.4 TSP exercises.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False


def verify_tsp_lower_bound(
    n_points: int = 1000, n_simulations: int = 100, backend: str = "cupy"
) -> Dict[str, float]:
    """
    Verify TSP lower bound β ≥ 1/2 through Monte Carlo simulation.

    Implements the theoretical analysis from Exercise 5.1 by generating
    random point sets and computing nearest neighbor distance statistics.

    Args:
        n_points: Number of points per instance
        n_simulations: Number of Monte Carlo runs
        backend: 'cupy' or 'numpy'

    Returns:
        Dictionary with empirical bounds and statistics
    """
    if backend == "cupy" and CUPY_AVAILABLE:
        xp = cp
    else:
        xp = np

    # Generate random point sets
    points = xp.random.uniform(0, 1, (n_simulations, n_points, 2))

    # Compute nearest neighbor distances
    nn_distances = _compute_nearest_neighbor_distances(points, xp)

    # Calculate empirical lower bounds
    nn_bounds = xp.sum(nn_distances, axis=1) / xp.sqrt(n_points)

    # Statistical analysis
    mean_bound = float(xp.mean(nn_bounds))
    std_bound = float(xp.std(nn_bounds))

    return {
        "empirical_beta_lower": mean_bound,
        "standard_deviation": std_bound,
        "theoretical_minimum": 0.5,
        "confidence_interval": (
            mean_bound - 1.96 * std_bound,
            mean_bound + 1.96 * std_bound,
        ),
        "n_points": n_points,
        "n_simulations": n_simulations,
    }


def run_strips_method(
    points: Union[np.ndarray, "cp.ndarray"], strip_width: float, backend: str = "cupy"
) -> Dict[str, float]:
    """
    Implement strips method for TSP upper bound analysis.

    Based on Exercise 5.2 theoretical analysis, partitions unit square
    into horizontal strips and constructs zigzag tour.

    Args:
        points: Array of 2D points in unit square
        strip_width: Width of horizontal strips
        backend: 'cupy' or 'numpy'

    Returns:
        Tour information and performance metrics
    """
    if backend == "cupy" and CUPY_AVAILABLE:
        xp = cp
    else:
        xp = np

    if not isinstance(points, type(xp.array([]))):
        points = xp.array(points)

    n_points = points.shape[0]

    # Assign points to strips
    strip_indices = xp.floor(points[:, 1] / strip_width).astype(int)
    n_strips = int(xp.max(strip_indices)) + 1

    total_length = 0.0
    tour_order = []

    for strip_id in range(n_strips):
        # Get points in current strip
        mask = strip_indices == strip_id
        strip_points = points[mask]
        strip_point_indices = xp.where(mask)[0]

        if len(strip_points) > 0:
            # Sort by x-coordinate (alternating direction)
            if strip_id % 2 == 0:
                sorted_indices = xp.argsort(strip_points[:, 0])
            else:
                sorted_indices = xp.argsort(strip_points[:, 0])[::-1]

            strip_points = strip_points[sorted_indices]
            strip_indices_ordered = strip_point_indices[sorted_indices]
            tour_order.extend(strip_indices_ordered.tolist())

            # Calculate path length within strip
            for i in range(len(strip_points) - 1):
                diff = strip_points[i + 1] - strip_points[i]
                total_length += float(xp.sqrt(xp.sum(diff**2)))

    # Add inter-strip connections (simplified)
    total_length += (n_strips - 1) * strip_width

    return {
        "tour_length": total_length,
        "normalized_length": total_length / np.sqrt(n_points),
        "n_strips": n_strips,
        "theoretical_bound": 1.16,
        "tour_order": tour_order,
    }


def hybrid_tsp_strategy(
    points: Union[np.ndarray, "cp.ndarray"], backend: str = "cupy"
) -> Dict[str, float]:
    """
    Implement hybrid TSP strategy from Exercise 5.3.

    Algorithm:
    1. Start at point 0, move to nearest neighbor
    2. Solve TSP on remaining points starting/ending at nearest neighbor
    3. Return to starting point

    Args:
        points: Array of 2D points
        backend: 'cupy' or 'numpy'

    Returns:
        Strategy performance and cost breakdown
    """
    if backend == "cupy" and CUPY_AVAILABLE:
        xp = cp
    else:
        xp = np

    if not isinstance(points, type(xp.array([]))):
        points = xp.array(points)

    n_points = points.shape[0]
    if n_points < 2:
        return {"total_cost": 0.0, "approximation_ratio": 1.0}

    # Phase 1: Find nearest neighbor to point 0
    distances_from_0 = xp.sqrt(xp.sum((points[1:] - points[0]) ** 2, axis=1))
    nearest_idx = xp.argmin(distances_from_0) + 1
    d_01 = float(distances_from_0[nearest_idx - 1])

    # Phase 2: Solve TSP on remaining points (simplified with nearest neighbor)
    remaining_points = xp.concatenate(
        [
            points[nearest_idx : nearest_idx + 1],
            points[1:nearest_idx],
            points[nearest_idx + 1 :],
        ]
    )
    remaining_tour_cost = _simple_tsp_tour(remaining_points, xp)

    # Phase 3: Return cost
    total_cost = 2 * d_01 + remaining_tour_cost

    # Estimate optimal tour for comparison (using nearest neighbor)
    optimal_estimate = _simple_tsp_tour(points, xp)
    approximation_ratio = total_cost / optimal_estimate if optimal_estimate > 0 else 1.0

    return {
        "total_cost": total_cost,
        "phase1_cost": d_01,
        "phase2_cost": remaining_tour_cost,
        "phase3_cost": d_01,
        "approximation_ratio": approximation_ratio,
        "theoretical_bound": 1.5,
    }


def _compute_nearest_neighbor_distances(
    points: Union[np.ndarray, "cp.ndarray"], xp
) -> Union[np.ndarray, "cp.ndarray"]:
    """Compute nearest neighbor distances efficiently."""
    n_sim, n_points, dim = points.shape
    nn_distances = xp.zeros((n_sim, n_points))

    for sim in range(n_sim):
        pts = points[sim]
        for i in range(n_points):
            # Compute distances to all other points
            other_pts = xp.concatenate([pts[:i], pts[i + 1 :]])
            distances = xp.sqrt(xp.sum((other_pts - pts[i]) ** 2, axis=1))
            nn_distances[sim, i] = xp.min(distances)

    return nn_distances


def _simple_tsp_tour(points: Union[np.ndarray, "cp.ndarray"], xp) -> float:
    """Simple nearest neighbor TSP tour for comparison."""
    n_points = points.shape[0]
    if n_points <= 1:
        return 0.0

    visited = xp.zeros(n_points, dtype=bool)
    current = 0
    visited[0] = True
    total_cost = 0.0

    for _ in range(n_points - 1):
        min_dist = float("inf")
        next_point = -1

        for j in range(n_points):
            if not visited[j]:
                dist = float(xp.sqrt(xp.sum((points[j] - points[current]) ** 2)))
                if dist < min_dist:
                    min_dist = dist
                    next_point = j

        if next_point >= 0:
            total_cost += min_dist
            visited[next_point] = True
            current = next_point

    # Return to start
    total_cost += float(xp.sqrt(xp.sum((points[0] - points[current]) ** 2)))

    return total_cost
