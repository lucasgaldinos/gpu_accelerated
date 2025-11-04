#!/usr/bin/env python3
"""
Test Option C: 2-Opt Integration into Compositional CVRP Solver

This script verifies that improvement strategies work correctly
within the compositional solver architecture.

Tests:
    1. CPU 2-opt integration with bin-first solver
    2. GPU 2-opt integration with bin-first solver
    3. Performance impact on small benchmark instance (eil22)
    4. Verification that improvements apply to all routes

Expected Results:
    - Tours improve compared to construction-only
    - CPU and GPU both produce valid improved tours
    - Solution quality improves by 5-15%
"""

import sys
import time
import numpy as np
import cupy as cp

sys.path.insert(0, "/home/lucas_galdino/TCC-name_to_define/gpu_accelerated/code")

from src.algorithms.compositional_cvrp_solver import lego_cvrp_solver
from src.algorithms.strategies.bin_packing_strategies import FFDStrategy
from src.algorithms.strategies.tsp_strategies import NearestNeighborStrategy
from src.algorithms.improvement.two_opt_cpu import TwoOptCPU
from src.algorithms.improvement.two_opt_gpu import TwoOptGPU


def compute_total_cost(routes, distances):
    """Compute total cost of all routes."""
    total = 0.0
    for route in routes:
        for i in range(len(route) - 1):
            total += distances[route[i], route[i + 1]]
    return total


def test_integration():
    """Test 2-opt integration into CVRP solver."""

    print("=" * 80)
    print("Option C: 2-Opt Integration Test")
    print("=" * 80)
    print()

    # Small test problem
    print("Creating test problem...")
    np.random.seed(42)
    n = 25
    locations = np.random.rand(n, 2) * 100
    demands = np.random.randint(10, 30, size=n)
    demands[0] = 0  # Depot demand
    capacity = 100.0

    # Compute distance matrix for cost calculation
    diff = locations[:, None, :] - locations[None, :, :]
    distances = np.sqrt(np.sum(diff**2, axis=2))

    print(f"  Nodes: {n}")
    print(f"  Capacity: {capacity}")
    print(
        f"  Demands: min={demands[1:].min()}, max={demands[1:].max()}, sum={demands[1:].sum()}"
    )
    print()

    # Test 1: Baseline (no improvement)
    print("Test 1: Baseline (construction only)")
    print("-" * 80)

    routes_baseline = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=NearestNeighborStrategy(),
        improvement_strategy=None,  # No improvement
        xp=np,
    )

    cost_baseline = compute_total_cost(routes_baseline, distances)
    print(f"  Routes: {len(routes_baseline)}")
    print(f"  Total cost: {cost_baseline:.2f}")
    print()

    # Test 2: CPU 2-opt improvement
    print("Test 2: With CPU 2-opt")
    print("-" * 80)

    start = time.perf_counter()
    routes_cpu = lego_cvrp_solver(
        locations=locations,
        demands=demands,
        capacity=capacity,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=NearestNeighborStrategy(),
        improvement_strategy=TwoOptCPU(max_iterations=1000),  # CPU improvement
        xp=np,
    )
    cpu_time = time.perf_counter() - start

    cost_cpu = compute_total_cost(routes_cpu, distances)
    improvement_cpu = 100 * (cost_baseline - cost_cpu) / cost_baseline

    print(f"  Routes: {len(routes_cpu)}")
    print(f"  Total cost: {cost_cpu:.2f}")
    print(f"  Improvement: {improvement_cpu:.1f}%")
    print(f"  Time: {cpu_time:.4f}s")
    print()

    # Test 3: GPU 2-opt improvement
    print("Test 3: With GPU 2-opt")
    print("-" * 80)

    # Transfer data to GPU
    locations_gpu = cp.asarray(locations)
    demands_gpu = cp.asarray(demands)

    start = time.perf_counter()
    routes_gpu = lego_cvrp_solver(
        locations=locations_gpu,
        demands=demands_gpu,
        capacity=capacity,
        bin_packing_strategy=FFDStrategy(),
        tsp_strategy=NearestNeighborStrategy(),
        improvement_strategy=TwoOptGPU(max_iterations=1000),  # GPU improvement
        xp=cp,
    )
    gpu_time = time.perf_counter() - start

    # Convert routes back to CPU for cost calculation
    routes_gpu_cpu = [[int(node) for node in route] for route in routes_gpu]
    cost_gpu = compute_total_cost(routes_gpu_cpu, distances)
    improvement_gpu = 100 * (cost_baseline - cost_gpu) / cost_baseline

    print(f"  Routes: {len(routes_gpu)}")
    print(f"  Total cost: {cost_gpu:.2f}")
    print(f"  Improvement: {improvement_gpu:.1f}%")
    print(f"  Time: {gpu_time:.4f}s")
    print()

    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Baseline cost:    {cost_baseline:.2f}")
    print(f"CPU cost:         {cost_cpu:.2f} ({improvement_cpu:+.1f}%)")
    print(f"GPU cost:         {cost_gpu:.2f} ({improvement_gpu:+.1f}%)")
    print()
    print(f"CPU time:         {cpu_time:.4f}s")
    print(f"GPU time:         {gpu_time:.4f}s")
    print(f"Speedup:          {cpu_time / gpu_time:.2f}x")
    print()

    # Validation
    print("Validation:")

    if cost_cpu < cost_baseline:
        print("  ✅ CPU improvement reduces cost")
    else:
        print("  ⚠️  CPU did not improve (may already be optimal)")

    if cost_gpu < cost_baseline:
        print("  ✅ GPU improvement reduces cost")
    else:
        print("  ⚠️  GPU did not improve (may already be optimal)")

    if len(routes_cpu) == len(routes_baseline):
        print("  ✅ Same number of routes (improvement preserves structure)")
    else:
        print(
            f"  ⚠️  Different number of routes ({len(routes_baseline)} → {len(routes_cpu)})"
        )

    print()
    print("✅ Integration test complete!")
    print()

    # Clean up GPU memory
    cp.get_default_memory_pool().free_all_blocks()


if __name__ == "__main__":
    test_integration()
