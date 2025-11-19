#!/usr/bin/env python3
"""Diagnostic: Compare FIRST 2-opt iteration between CPU and GPU.

Isolates the bug by running a single 2-opt pass on the SAME initial tour
and comparing the resulting tour + delta values.

Author: AI Assistant
Date: 2025-01-28
"""

import numpy as np
import cupy as cp
import duckdb

def load_problem_direct(db_path, instance_name):
    """Direct load without circular imports."""
    conn = duckdb.connect(db_path)
    
    # Get problem metadata
    meta = conn.execute(
        "SELECT dimension, edge_weight_type FROM problems WHERE name = ?",
        [instance_name]
    ).fetchone()
    
    if not meta:
        raise ValueError(f"Problem {instance_name} not found")
    
    n, edge_type = meta
    
    # Get coordinates
    coords = conn.execute(
        "SELECT node_id, x, y FROM nodes WHERE problem_id = (SELECT id FROM problems WHERE name = ?) ORDER BY node_id",
        [instance_name]
    ).fetchall()
    
    coords_array = np.array([[x, y] for _, x, y in coords], dtype=np.float64)
    
    # Compute distance matrix (EUC_2D)
    distances = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = coords_array[i, 0] - coords_array[j, 0]
                dy = coords_array[i, 1] - coords_array[j, 1]
                distances[i, j] = np.sqrt(dx*dx + dy*dy)
    
    conn.close()
    return n, distances

def cpu_single_2opt_pass(tour, distances):
    """CPU reference: single 2-opt pass (best-improvement)."""
    n = len(tour)
    best_delta = 0.0
    best_i, best_j = -1, -1
    
    # Track ALL negative deltas for comparison
    improvements = []
    
    for ii in range(n - 1):
        for jj in range(ii + 2, n):
            city_i = tour[ii]
            city_i_next = tour[ii + 1]
            city_j = tour[jj]
            city_j_next = tour[(jj + 1) % n]
            
            old_dist = distances[city_i, city_i_next] + distances[city_j, city_j_next]
            new_dist = distances[city_i, city_j] + distances[city_i_next, city_j_next]
            delta = new_dist - old_dist
            
            if delta < 0:
                improvements.append((ii, jj, delta))
            
            if delta < best_delta:
                best_delta = delta
                best_i, best_j = ii, jj
    
    # Apply swap if improvement found
    if best_delta < 0:
        tour[best_i + 1 : best_j + 1] = tour[best_i + 1 : best_j + 1][::-1]
    
    return tour, best_delta, best_i, best_j, improvements

def gpu_single_2opt_pass(tour_np, distances_np):
    """GPU: single 2-opt pass using two_opt_single.cu kernel."""
    from pathlib import Path
    
    # Load kernel
    kernel_path = Path("src/algorithms/kernels/two_opt_single.cu")
    with open(kernel_path, "r") as f:
        kernel_source = f.read()
    kernel = cp.RawKernel(kernel_source, "two_opt_kernel")
    
    # Transfer data
    tour_gpu = cp.asarray(tour_np, dtype=cp.int32)
    distances_gpu = cp.asarray(distances_np, dtype=cp.float64)
    
    n = len(tour_np)
    threads_per_block = min(256, n - 2)
    shared_mem = (
        threads_per_block * 8  # s_deltas
        + threads_per_block * 4  # s_swap_i
        + threads_per_block * 4  # s_swap_j
        + n * 4  # s_tour
    )
    
    # Launch kernel (single pass)
    kernel(
        (1,),
        (threads_per_block,),
        (tour_gpu, distances_gpu, n, 0),
        shared_mem=shared_mem,
    )
    
    # Transfer back
    tour_result = tour_gpu.get()
    
    return tour_result

def main():
    print("=" * 80)
    print("DIAGNOSTIC: CPU vs GPU Single 2-opt Pass")
    print("=" * 80)
    print()
    
    # Load problem
    db_path = "../datasets/routing.duckdb"
    n, distances = load_problem_direct(db_path, "kroA100")
    
    # Simple initial tour: [0, 1, 2, ..., n-1]
    tour_init = np.arange(n, dtype=np.int32)
    
    # Calculate initial cost
    init_cost = sum(distances[tour_init[i], tour_init[(i+1) % n]] for i in range(n))
    
    print(f"Problem: kroA100 (n={n})")
    print(f"Initial tour: [0, 1, 2, ..., {n-1}]")
    print(f"Initial cost: {init_cost:.2f}")
    print()
    
    # CPU pass
    print("-" * 80)
    print("CPU: Single 2-opt pass")
    print("-" * 80)
    
    tour_cpu = tour_init.copy()
    tour_cpu, best_delta_cpu, best_i_cpu, best_j_cpu, improvements_cpu = cpu_single_2opt_pass(tour_cpu, distances)
    
    cost_cpu = sum(distances[tour_cpu[i], tour_cpu[(i+1) % n]] for i in range(n))
    
    print(f"Best swap found: ({best_i_cpu}, {best_j_cpu}) with delta = {best_delta_cpu:.4f}")
    print(f"Total improvements found: {len(improvements_cpu)}")
    print(f"Top 5 improvements:")
    for ii, jj, delta in sorted(improvements_cpu, key=lambda x: x[2])[:5]:
        print(f"  ({ii:3d}, {jj:3d}): delta = {delta:10.4f}")
    print(f"Final cost: {cost_cpu:.2f}")
    print(f"Tour changed: {not np.array_equal(tour_init, tour_cpu)}")
    if best_i_cpu >= 0:
        print(f"Reversed segment: tour[{best_i_cpu+1}:{best_j_cpu+1}]")
    print()
    
    # GPU pass
    print("-" * 80)
    print("GPU: Single 2-opt pass")
    print("-" * 80)
    
    if not cp.cuda.is_available():
        print("❌ GPU unavailable")
        return
    
    tour_gpu = gpu_single_2opt_pass(tour_init.copy(), distances)
    
    cost_gpu = sum(distances[tour_gpu[i], tour_gpu[(i+1) % n]] for i in range(n))
    
    print(f"Final cost: {cost_gpu:.2f}")
    print(f"Tour changed: {not np.array_equal(tour_init, tour_gpu)}")
    print()
    
    # Comparison
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print()
    
    cost_diff = abs(cost_cpu - cost_gpu)
    tour_diff = not np.array_equal(tour_cpu, tour_gpu)
    
    print(f"Cost difference: {cost_diff:.4f} ({cost_diff/cost_cpu*100:.4f}%)")
    print(f"Tours identical: {not tour_diff}")
    
    if cost_diff < 1e-6:
        print("\n✅ CPU and GPU produce IDENTICAL results")
        print("   → Kernel is correct (bug is elsewhere)")
    else:
        print(f"\n⚠️  CPU cost: {cost_cpu:.2f}")
        print(f"   GPU cost: {cost_gpu:.2f}")
        print(f"   Difference: {cost_gpu - cost_cpu:+.2f}")
        
        if tour_diff:
            # Find first difference
            for i in range(n):
                if tour_cpu[i] != tour_gpu[i]:
                    print(f"\n   First tour difference at index {i}:")
                    print(f"     CPU: {tour_cpu[max(0,i-3):i+4]}")
                    print(f"     GPU: {tour_gpu[max(0,i-3):i+4]}")
                    break
            
            # Check if GPU applied WRONG swap
            if best_delta_cpu < 0:
                print(f"\n   CPU applied swap ({best_i_cpu}, {best_j_cpu})")
                print(f"   Expected reversal: tour[{best_i_cpu+1}:{best_j_cpu+1}]")
                
                # Check if GPU's tour matches expected result
                tour_expected = tour_init.copy()
                tour_expected[best_i_cpu + 1 : best_j_cpu + 1] = tour_expected[best_i_cpu + 1 : best_j_cpu + 1][::-1]
                
                if np.array_equal(tour_gpu, tour_expected):
                    print("   ✅ GPU applied SAME swap correctly")
                else:
                    print("   ❌ GPU applied DIFFERENT or INCORRECT swap")
                    
                    # Try to identify GPU's swap by comparing segments
                    print("\n   Analyzing GPU tour to identify swap...")
                    
        else:
            print("\n   🤔 Tours are IDENTICAL but costs differ")
            print("   → Bug is in cost calculation or floating-point precision")

if __name__ == "__main__":
    main()
