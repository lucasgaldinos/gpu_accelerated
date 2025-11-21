#!/usr/bin/env python3
"""Debug: Print what GPU kernel is finding for best swap."""

import numpy as np
import cupy as cp
from pathlib import Path
import duckdb

# Simplified kernel with debug output
debug_kernel_source = """
extern "C" __global__
void two_opt_debug(
    int *tour,
    const double *dist,
    int n,
    double *best_delta_out,
    int *best_i_out,
    int *best_j_out
) {
    extern __shared__ double shared_mem[];
    
    double *s_deltas = shared_mem;
    int *s_swap_i = (int*)&s_deltas[blockDim.x];
    int *s_swap_j = (int*)&s_swap_i[blockDim.x];
    int *s_tour = (int*)&s_swap_j[blockDim.x];
    
    int tid = threadIdx.x;
    int block_size = blockDim.x;
    
    // Load tour
    for (int i = tid; i < n; i += block_size) {
        s_tour[i] = tour[i];
    }
    __syncthreads();
    
    // Initialize
    s_deltas[tid] = 0.0;
    s_swap_i[tid] = -1;
    s_swap_j[tid] = -1;
    
    // Evaluate swaps
    for (int i = tid; i < n - 2; i += block_size) {
        int node_i = s_tour[i];
        int node_i1 = s_tour[i + 1];
        
        for (int j = i + 2; j < n; ++j) {
            int node_j = s_tour[j];
            int node_j1 = s_tour[(j + 1) % n];
            
            double old_dist = dist[node_i * n + node_i1] + dist[node_j * n + node_j1];
            double new_dist = dist[node_i * n + node_j] + dist[node_i1 * n + node_j1];
            double delta = new_dist - old_dist;
            
            if (delta < s_deltas[tid]) {
                s_deltas[tid] = delta;
                s_swap_i[tid] = i;
                s_swap_j[tid] = j;
            }
        }
    }
    __syncthreads();
    
    // FIXED reduction
    for (unsigned int s = block_size / 2; s > 0; s >>= 1) {
        if (tid < s) {
            if (s_deltas[tid + s] < s_deltas[tid]) {
                s_deltas[tid] = s_deltas[tid + s];
                s_swap_i[tid] = s_swap_i[tid + s];
                s_swap_j[tid] = s_swap_j[tid + s];
            }
        }
        __syncthreads();
    }
    
    // Output result
    if (tid == 0) {
        *best_delta_out = s_deltas[0];
        *best_i_out = s_swap_i[0];
        *best_j_out = s_swap_j[0];
    }
}
"""


def main():
    # Load problem
    conn = duckdb.connect("../datasets/routing.duckdb")
    n = 100
    coords = conn.execute(
        "SELECT node_id, x, y FROM nodes WHERE problem_id = (SELECT id FROM problems WHERE name = 'kroA100') ORDER BY node_id"
    ).fetchall()
    coords_array = np.array([[x, y] for _, x, y in coords], dtype=np.float64)
    distances = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = coords_array[i, 0] - coords_array[j, 0]
                dy = coords_array[i, 1] - coords_array[j, 1]
                distances[i, j] = np.sqrt(dx * dx + dy * dy)
    conn.close()

    # Initial tour
    tour = np.arange(n, dtype=np.int32)

    # Compile debug kernel
    kernel = cp.RawKernel(debug_kernel_source, "two_opt_debug")

    # Allocate GPU memory
    tour_gpu = cp.asarray(tour, dtype=cp.int32)
    dist_gpu = cp.asarray(distances, dtype=cp.float64)
    best_delta_gpu = cp.zeros(1, dtype=cp.float64)
    best_i_gpu = cp.zeros(1, dtype=cp.int32)
    best_j_gpu = cp.zeros(1, dtype=cp.int32)

    # Launch
    threads = min(256, n - 2)
    shared = threads * 8 + threads * 4 + threads * 4 + n * 4

    kernel(
        (1,),
        (threads,),
        (tour_gpu, dist_gpu, n, best_delta_gpu, best_i_gpu, best_j_gpu),
        shared_mem=shared,
    )

    # Get results
    delta = float(best_delta_gpu.get()[0])
    best_i = int(best_i_gpu.get()[0])
    best_j = int(best_j_gpu.get()[0])

    print(f"GPU found: ({best_i}, {best_j}) with delta = {delta:.4f}")
    print(f"Expected:  (51, 77) with delta = -6663.5931")
    print()

    if best_i == 51 and best_j == 77:
        print("✅ CORRECT! GPU found the optimal swap")
    else:
        print(f"❌ WRONG! GPU found ({best_i}, {best_j}) instead of (51, 77)")

        # Verify this is an improving move at least
        if delta < 0:
            print(f"   But it IS an improvement: delta = {delta:.4f}")
        else:
            print(f"   And it's NOT even an improvement: delta = {delta:.4f}")


if __name__ == "__main__":
    main()
