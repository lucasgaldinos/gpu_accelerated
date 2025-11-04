#!/usr/bin/env python3
"""
Benchmark CPU vs GPU 2-opt implementations.

This script compares the performance of TwoOptCPU and TwoOptGPU
across different problem sizes to verify GPU acceleration benefits.

Test Methodology:
    - Problem sizes: N = 10, 50, 100, 500, 1000
    - Random Euclidean instances (seed=42 for reproducibility)
    - Same initial tour for both CPU and GPU
    - Measure wall-clock time using time.perf_counter()
    - Report speedup factor (CPU time / GPU time)
    - Verify solution quality (improvement %)

Expected Results (based on Fujimoto 2011):
    - N < 100: GPU slower (overhead dominates)
    - N = 100-500: GPU comparable or slightly faster
    - N > 500: GPU 5-20x faster (parallel advantage)

Hardware Context:
    - GPU: NVIDIA GeForce GTX 1050 (4GB VRAM)
    - CPU: Intel i7-7700HQ @ 2.80GHz (8 cores)
    - CUDA: 12.6
"""

import sys
import time
import numpy as np
import cupy as cp
from typing import List, Tuple

# Add code directory to path
sys.path.insert(0, "/home/lucas_galdino/TCC-name_to_define/gpu_accelerated/code")

from src.algorithms.improvement.two_opt_cpu import TwoOptCPU
from src.algorithms.improvement.two_opt_gpu import TwoOptGPU


def generate_random_problem(n: int, seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate random Euclidean TSP instance.

    Args:
        n: Number of nodes
        seed: Random seed for reproducibility

    Returns:
        (locations, distances): Node coordinates and distance matrix
    """
    np.random.seed(seed)
    locations = np.random.rand(n, 2) * 100  # 100x100 square

    # Compute distance matrix
    diff = locations[:, None, :] - locations[None, :, :]
    distances = np.sqrt(np.sum(diff**2, axis=2))

    return locations, distances


def create_random_tour(n: int) -> List[int]:
    """
    Create random initial tour starting/ending at depot 0.

    Args:
        n: Number of nodes

    Returns:
        Random tour [0, ..., 0]
    """
    # Random permutation of non-depot nodes
    interior = list(np.random.permutation(range(1, n)))
    return [0] + interior + [0]


def compute_tour_cost(tour: List[int], distances: np.ndarray) -> float:
    """
    Compute total tour cost.

    Args:
        tour: Node sequence
        distances: Distance matrix

    Returns:
        Total cost (sum of edge weights)
    """
    return sum(distances[tour[i], tour[i + 1]] for i in range(len(tour) - 1))


def benchmark_cpu(
    tour: List[int], distances: np.ndarray, max_iterations: int = 1000
) -> Tuple[float, List[int], float]:
    """
    Benchmark CPU 2-opt implementation.

    Args:
        tour: Initial tour
        distances: Distance matrix (NumPy)
        max_iterations: Maximum iterations

    Returns:
        (elapsed_time, improved_tour, final_cost)
    """
    strategy = TwoOptCPU(max_iterations=max_iterations)

    start = time.perf_counter()
    improved_tour = strategy.improve_tour(tour.copy(), distances, xp=np)
    elapsed = time.perf_counter() - start

    final_cost = compute_tour_cost(improved_tour, distances)

    return elapsed, improved_tour, final_cost


def benchmark_gpu(
    tour: List[int],
    distances: np.ndarray,
    max_iterations: int = 1000,
    threads_per_block: int = 256,
) -> Tuple[float, List[int], float]:
    """
    Benchmark GPU 2-opt implementation.

    Args:
        tour: Initial tour
        distances: Distance matrix (NumPy, will be transferred to GPU)
        max_iterations: Maximum iterations
        threads_per_block: CUDA threads per block

    Returns:
        (elapsed_time, improved_tour, final_cost)
    """
    # Transfer distance matrix to GPU (measured in timing)
    strategy = TwoOptGPU(
        max_iterations=max_iterations, threads_per_block=threads_per_block
    )

    start = time.perf_counter()

    # Transfer to GPU
    distances_gpu = cp.asarray(distances)

    # Run improvement
    improved_tour = strategy.improve_tour(tour.copy(), distances_gpu, xp=cp)

    # Synchronize to ensure completion
    cp.cuda.Stream.null.synchronize()

    elapsed = time.perf_counter() - start

    # Compute cost on CPU for fair comparison
    final_cost = compute_tour_cost(improved_tour, distances)

    return elapsed, improved_tour, final_cost


def run_benchmark_suite():
    """
    Run comprehensive CPU vs GPU benchmark suite.
    """
    print("=" * 80)
    print("CPU vs GPU 2-Opt Benchmark Suite")
    print("=" * 80)
    print()

    # Test problem sizes
    problem_sizes = [10, 50, 100, 500, 1000]
    max_iterations = 1000

    print(f"Configuration:")
    print(f"  Max iterations: {max_iterations}")
    print(f"  GPU threads/block: 256")
    print(f"  Random seed: 42")
    print()

    # Check GPU availability
    print("GPU Status:")
    print(f"  CuPy version: {cp.__version__}")
    print(f"  CUDA version: {cp.cuda.runtime.runtimeGetVersion()}")
    device = cp.cuda.Device()
    print(f"  Device: {device.compute_capability}")
    meminfo = cp.cuda.Device().mem_info
    print(f"  Memory: {meminfo[0] / 1e9:.2f}GB free / {meminfo[1] / 1e9:.2f}GB total")
    print()

    # Warmup GPU (compile kernel)
    print("Warming up GPU (kernel compilation)...")
    _, warmup_dist = generate_random_problem(10)
    warmup_tour = create_random_tour(10)
    _ = benchmark_gpu(warmup_tour, warmup_dist, max_iterations=10)
    print("✅ GPU warmed up")
    print()

    # Results table
    print("=" * 80)
    print(
        f"{'Size':<6} {'CPU Time':<12} {'GPU Time':<12} {'Speedup':<10} "
        f"{'CPU Impr%':<12} {'GPU Impr%':<12}"
    )
    print("=" * 80)

    results = []

    for n in problem_sizes:
        print(f"Testing N={n}...", end=" ", flush=True)

        # Generate problem
        locations, distances = generate_random_problem(n)

        # Create same initial tour for both
        np.random.seed(42 + n)  # Different tour per size
        tour = create_random_tour(n)
        initial_cost = compute_tour_cost(tour, distances)

        try:
            # Benchmark CPU
            cpu_time, cpu_tour, cpu_cost = benchmark_cpu(
                tour, distances, max_iterations
            )
            cpu_improvement = 100 * (initial_cost - cpu_cost) / initial_cost

            # Benchmark GPU
            gpu_time, gpu_tour, gpu_cost = benchmark_gpu(
                tour, distances, max_iterations
            )
            gpu_improvement = 100 * (initial_cost - gpu_cost) / initial_cost

            # Calculate speedup
            speedup = cpu_time / gpu_time if gpu_time > 0 else 0

            # Store results
            results.append(
                {
                    "n": n,
                    "cpu_time": cpu_time,
                    "gpu_time": gpu_time,
                    "speedup": speedup,
                    "cpu_improvement": cpu_improvement,
                    "gpu_improvement": gpu_improvement,
                    "initial_cost": initial_cost,
                    "cpu_cost": cpu_cost,
                    "gpu_cost": gpu_cost,
                }
            )

            # Print row
            print(
                f"\r{n:<6} {cpu_time:>10.4f}s {gpu_time:>10.4f}s {speedup:>8.2f}x "
                f"{cpu_improvement:>10.1f}% {gpu_improvement:>10.1f}%"
            )

        except Exception as e:
            print(f"\r{n:<6} ERROR: {e}")
            continue

    print("=" * 80)
    print()

    # Summary statistics
    if results:
        print("Summary Statistics:")
        print("-" * 80)

        # Average speedup for large problems (N >= 100)
        large_results = [r for r in results if r["n"] >= 100]
        if large_results:
            avg_speedup_large = np.mean([r["speedup"] for r in large_results])
            print(f"  Average speedup (N≥100): {avg_speedup_large:.2f}x")

        # Best speedup
        best_result = max(results, key=lambda r: r["speedup"])
        print(f"  Best speedup: {best_result['speedup']:.2f}x at N={best_result['n']}")

        # Solution quality comparison
        avg_cpu_impr = np.mean([r["cpu_improvement"] for r in results])
        avg_gpu_impr = np.mean([r["gpu_improvement"] for r in results])
        print(f"  Average CPU improvement: {avg_cpu_impr:.1f}%")
        print(f"  Average GPU improvement: {avg_gpu_impr:.1f}%")

        print("-" * 80)
        print()

        # Detailed results
        print("Detailed Results:")
        print("-" * 80)
        for r in results:
            print(
                f"N={r['n']:4d}: Initial={r['initial_cost']:8.2f}, "
                f"CPU={r['cpu_cost']:8.2f} ({r['cpu_time']:6.4f}s), "
                f"GPU={r['gpu_cost']:8.2f} ({r['gpu_time']:6.4f}s), "
                f"Speedup={r['speedup']:5.2f}x"
            )
        print("-" * 80)
        print()

    # GPU memory cleanup
    cp.get_default_memory_pool().free_all_blocks()

    # Final memory check
    meminfo_final = cp.cuda.Device().mem_info
    print(
        f"Final GPU Memory: {meminfo_final[0] / 1e9:.2f}GB free / "
        f"{meminfo_final[1] / 1e9:.2f}GB total"
    )
    print()
    print("✅ Benchmark complete!")


if __name__ == "__main__":
    run_benchmark_suite()
