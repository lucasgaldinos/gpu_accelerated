"""
Debug script to trace GPU 2-opt behavior.

This script will:
1. Create a simple test case
2. Run GPU 2-opt with verbose output
3. Compare with CPU 2-opt
4. Identify where the bug occurs
"""

import cupy as cp
import numpy as np
from src.algorithms.improvement.two_opt_gpu import TwoOptGPU
from src.algorithms.improvement.two_opt_cpu import TwoOptCPU


def compute_tour_cost(tour, distances):
    """Compute tour cost manually."""
    cost = 0.0
    for i in range(len(tour) - 1):
        cost += distances[tour[i], tour[i + 1]]
    return cost


def main():
    print("=" * 80)
    print("GPU 2-Opt Debug Session")
    print("=" * 80)

    # Simple test case: 5 nodes (depot + 4 customers)
    np.random.seed(42)
    n = 5
    locations = np.random.rand(n, 2) * 100

    # Ensure depot at origin
    locations[0] = [0, 0]

    print(f"\nLocations:\n{locations}")

    # Compute distance matrix
    distances_np = np.sqrt(
        ((locations[:, np.newaxis] - locations[np.newaxis, :]) ** 2).sum(axis=2)
    )
    distances_gpu = cp.asarray(distances_np)

    print(f"\nDistance Matrix:\n{distances_np}")

    # Create initial tour (simple sequence)
    tour = [0, 1, 2, 3, 4, 0]
    tour_for_gpu = tour.copy()
    tour_for_cpu = tour.copy()

    initial_cost = compute_tour_cost(tour, distances_np)
    print(f"\nInitial Tour: {tour}")
    print(f"Initial Cost: {initial_cost:.4f}")

    # ========== CPU 2-OPT ==========
    print("\n" + "=" * 80)
    print("Running CPU 2-Opt...")
    print("=" * 80)

    cpu_strategy = TwoOptCPU(max_iterations=100)
    cpu_improved = cpu_strategy.improve_tour(tour_for_cpu, distances_np, xp=np)
    cpu_cost = compute_tour_cost(cpu_improved, distances_np)

    print(f"CPU Improved Tour: {cpu_improved}")
    print(f"CPU Final Cost: {cpu_cost:.4f}")
    print(
        f"CPU Improvement: {initial_cost - cpu_cost:.4f} ({100 * (initial_cost - cpu_cost) / initial_cost:.2f}%)"
    )

    # ========== GPU 2-OPT ==========
    print("\n" + "=" * 80)
    print("Running GPU 2-Opt...")
    print("=" * 80)

    gpu_strategy = TwoOptGPU(max_iterations=100, threads_per_block=256)

    # Manually trace what GPU does
    print(f"\nInput to GPU: {tour_for_gpu}")
    print(f"Removing duplicate depot: {tour_for_gpu[:-1]}")

    gpu_improved = gpu_strategy.improve_tour(tour_for_gpu, distances_gpu, xp=cp)
    gpu_cost = compute_tour_cost(gpu_improved, distances_np)

    print(f"GPU Improved Tour: {gpu_improved}")
    print(f"GPU Final Cost: {gpu_cost:.4f}")
    print(
        f"GPU Improvement: {initial_cost - gpu_cost:.4f} ({100 * (initial_cost - gpu_cost) / initial_cost:.2f}%)"
    )

    # ========== COMPARISON ==========
    print("\n" + "=" * 80)
    print("Comparison")
    print("=" * 80)

    print(f"\nInitial: {tour} → {initial_cost:.4f}")
    print(
        f"CPU:     {cpu_improved} → {cpu_cost:.4f} (Δ = {initial_cost - cpu_cost:+.4f})"
    )
    print(
        f"GPU:     {gpu_improved} → {gpu_cost:.4f} (Δ = {initial_cost - gpu_cost:+.4f})"
    )

    if gpu_cost > initial_cost:
        print("\n⚠️  **GPU MADE TOUR WORSE!**")
        print("Checking if tour structure is valid...")
        print(f"  - Starts with depot? {gpu_improved[0] == 0}")
        print(f"  - Ends with depot? {gpu_improved[-1] == 0}")
        print(f"  - Correct length? {len(gpu_improved) == len(tour)}")
        print(f"  - All nodes present? {set(gpu_improved) == set(tour)}")
    elif gpu_cost < cpu_cost:
        print("\n✅ GPU found better solution than CPU")
    else:
        print("\n✅ GPU matches CPU solution")

    # Free GPU memory
    cp.get_default_memory_pool().free_all_blocks()

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
