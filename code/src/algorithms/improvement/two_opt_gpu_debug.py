"""
Heavily instrumented GPU 2-opt implementation for debugging.

This version adds extensive printf debugging to the CUDA kernel to trace:
1. What each thread is evaluating (i, j pairs)
2. Distance matrix accesses
3. Delta calculations
4. Reduction steps
5. Tour reversal

Author: Debug session
Date: 2025-01-27
"""

import cupy as cp
import numpy as np
from typing import List


class TwoOptGPUDebug:
    """GPU 2-opt with extensive debugging output."""

    def __init__(self, max_iterations: int = 100, threads_per_block: int = 256):
        self.max_iterations = max_iterations
        self.threads_per_block = threads_per_block
        self._compile_kernel()

    def _compile_kernel(self):
        """Compile CUDA kernel with debug printf statements."""
        kernel_code = r"""
        extern "C" __global__
        void two_opt_debug_kernel(
            int *tour,
            const float *dist,
            float *debug_deltas,
            int *debug_swap_i,
            int *debug_swap_j,
            int n,
            int tour_idx
        ) {
            extern __shared__ float shared_mem[];
            
            // Partition shared memory
            float *s_deltas = shared_mem;
            int *s_swap_i = (int*)&s_deltas[blockDim.x];
            int *s_swap_j = (int*)&s_swap_i[blockDim.x];
            int *s_tour = (int*)&s_swap_j[blockDim.x];
            
            int tid = threadIdx.x;
            int block_size = blockDim.x;
            
            // FIX: Load tour using loop to handle n > block_size
            for (int i = tid; i < n; i += block_size) {
                s_tour[i] = tour[i];
            }
            __syncthreads();
            
            // Debug: Print tour
            if (tid == 0) {
                printf("\n=== GPU 2-Opt Debug - Thread Block %d ===\n", blockIdx.x);
                printf("Tour (n=%d): ", n);
                for (int k = 0; k < n; k++) {
                    printf("%d ", s_tour[k]);
                }
                printf("\n");
            }
            __syncthreads();
            
            // Initialize shared memory for this thread
            s_deltas[tid] = 0.0f;
            s_swap_i[tid] = -1;
            s_swap_j[tid] = -1;
            
            // Each thread evaluates a subset of i positions
            for (int i = tid; i < n - 2; i += block_size) {
                int node_i = s_tour[i];
                int node_i1 = s_tour[i + 1];
                
                printf("Thread %d evaluating i=%d (nodes %d->%d)\n", 
                       tid, i, node_i, node_i1);
                
                // Serial inner loop over j
                for (int j = i + 2; j < n; ++j) {
                    int node_j = s_tour[j];
                    int node_j1 = s_tour[(j + 1) % n];
                    
                    // Calculate delta (new - old: negative = improvement)
                    float old_dist = dist[node_i * n + node_i1] + 
                                   dist[node_j * n + node_j1];
                    float new_dist = dist[node_i * n + node_j] + 
                                   dist[node_i1 * n + node_j1];
                    float delta = new_dist - old_dist;  // Negative = improvement
                    
                    printf("  Thread %d: i=%d j=%d | edges (%d->%d, %d->%d) vs (%d->%d, %d->%d) | old=%.2f new=%.2f delta=%.2f\n",
                           tid, i, j,
                           node_i, node_i1, node_j, node_j1,
                           node_i, node_j, node_i1, node_j1,
                           old_dist, new_dist, delta);
                    
                    // Update best for this thread
                    if (delta < s_deltas[tid]) {
                        printf("    Thread %d: NEW BEST delta=%.2f at i=%d j=%d (old best was %.2f)\n",
                               tid, delta, i, j, s_deltas[tid]);
                        s_deltas[tid] = delta;
                        s_swap_i[tid] = i;
                        s_swap_j[tid] = j;
                    }
                }
            }
            __syncthreads();
            
            // Debug: Show each thread's best
            if (tid < block_size) {
                printf("Thread %d best: delta=%.2f i=%d j=%d\n",
                       tid, s_deltas[tid], s_swap_i[tid], s_swap_j[tid]);
            }
            __syncthreads();
            
            // Parallel reduction
            if (tid == 0) {
                printf("\n=== Starting Reduction (block_size=%d) ===\n", block_size);
            }
            __syncthreads();
            
            // Reduction for blocks with < 32 threads
            if (tid < 2 && tid + 2 < block_size && s_deltas[tid + 2] < s_deltas[tid]) {
                printf("Reduction step [2]: Thread %d comparing %.2f vs %.2f\n",
                       tid, s_deltas[tid], s_deltas[tid + 2]);
                s_deltas[tid] = s_deltas[tid + 2];
                s_swap_i[tid] = s_swap_i[tid + 2];
                s_swap_j[tid] = s_swap_j[tid + 2];
            }
            __syncthreads();
            
            if (tid < 1 && tid + 1 < block_size && s_deltas[tid + 1] < s_deltas[tid]) {
                printf("Reduction step [1]: Thread 0 comparing %.2f vs %.2f\n",
                       s_deltas[0], s_deltas[1]);
                s_deltas[0] = s_deltas[1];
                s_swap_i[0] = s_swap_i[1];
                s_swap_j[0] = s_swap_j[1];
            }
            __syncthreads();
            
            // Apply best swap (Thread 0 only)
            if (tid == 0) {
                printf("\n=== Reduction Result ===\n");
                printf("Global best: delta=%.2f i=%d j=%d\n",
                       s_deltas[0], s_swap_i[0], s_swap_j[0]);
                
                if (s_deltas[0] < 0.0f) {
                    int swap_i = s_swap_i[0];
                    int swap_j = s_swap_j[0];
                    
                    printf("APPLYING SWAP: Reversing s_tour[%d:%d]\n", 
                           swap_i + 1, swap_j + 1);
                    printf("Before reversal: ");
                    for (int k = 0; k < n; k++) {
                        printf("%d ", s_tour[k]);
                    }
                    printf("\n");
                    
                    // Reverse segment [i+1, j]
                    int left = swap_i + 1;
                    int right = swap_j;
                    while (left < right) {
                        int temp = s_tour[left];
                        s_tour[left] = s_tour[right];
                        s_tour[right] = temp;
                        left++;
                        right--;
                    }
                    
                    printf("After reversal: ");
                    for (int k = 0; k < n; k++) {
                        printf("%d ", s_tour[k]);
                    }
                    printf("\n");
                } else {
                    printf("NO IMPROVEMENT FOUND (delta >= 0)\n");
                }
            }
            __syncthreads();
            
            // FIX: Write back using loop to handle n > block_size
            for (int i = tid; i < n; i += block_size) {
                tour[i] = s_tour[i];
            }
            
            // Store debug info
            if (tid < block_size) {
                debug_deltas[tid] = s_deltas[tid];
                debug_swap_i[tid] = s_swap_i[tid];
                debug_swap_j[tid] = s_swap_j[tid];
            }
        }
        """

        self._kernel = cp.RawKernel(kernel_code, "two_opt_debug_kernel")

    def improve_tour(self, tour: List[int], distances: cp.ndarray, xp=cp) -> List[int]:
        """
        Run one iteration of 2-opt with full debugging output.

        Args:
            tour: Tour WITH duplicate depot [0, 1, 2, 3, 4, 0]
            distances: Distance matrix (CuPy array)
            xp: Array backend (ignored, always uses CuPy)

        Returns:
            Improved tour WITH duplicate depot
        """
        # Strip duplicate depot for GPU
        tour_gpu = cp.array(tour[:-1], dtype=cp.int32)
        n = len(tour_gpu)

        print(f"\n{'=' * 80}")
        print(f"GPU Debug - Input Tour: {tour}")
        print(f"GPU Debug - Stripped Tour: {tour[:-1]} (n={n})")
        print(f"{'=' * 80}\n")

        # Allocate debug arrays
        debug_deltas = cp.zeros(self.threads_per_block, dtype=cp.float32)
        debug_swap_i = cp.full(self.threads_per_block, -1, dtype=cp.int32)
        debug_swap_j = cp.full(self.threads_per_block, -1, dtype=cp.int32)

        # Calculate shared memory size
        # 1 float array + 3 int arrays
        shared_mem_size = (
            self.threads_per_block * 4  # s_deltas (float)
            + self.threads_per_block * 4  # s_swap_i (int)
            + self.threads_per_block * 4  # s_swap_j (int)
            + n * 4  # s_tour (int)
        )

        # Launch kernel
        block_size = min(self.threads_per_block, n - 2)
        print(
            f"Launching kernel: block_size={block_size}, n={n}, shared_mem={shared_mem_size} bytes"
        )

        self._kernel(
            (1,),  # 1 block
            (block_size,),  # threads per block
            (
                tour_gpu,
                distances,
                debug_deltas,
                debug_swap_i,
                debug_swap_j,
                n,
                0,  # tour_idx
            ),
            shared_mem=shared_mem_size,
        )

        # Synchronize to ensure all printf output is flushed
        cp.cuda.Device().synchronize()

        # Print debug results
        print("\n" + "=" * 80)
        print("Debug Results from GPU")
        print("=" * 80)
        debug_deltas_cpu = debug_deltas.get()
        debug_swap_i_cpu = debug_swap_i.get()
        debug_swap_j_cpu = debug_swap_j.get()

        for tid in range(min(block_size, 10)):  # Print first 10 threads
            print(
                f"Thread {tid}: delta={debug_deltas_cpu[tid]:.4f}, "
                f"i={debug_swap_i_cpu[tid]}, j={debug_swap_j_cpu[tid]}"
            )

        # Convert back to list with duplicate depot
        improved_tour = tour_gpu.get().tolist()
        improved_tour.append(0)

        print(f"\nFinal GPU tour: {improved_tour}")
        print("=" * 80 + "\n")

        return improved_tour


def test_debug():
    """Test the debug version."""
    print("Testing GPU 2-Opt Debug Version\n")

    # Simple 5-node case
    np.random.seed(42)
    n = 5
    locations = np.random.rand(n, 2) * 100
    locations[0] = [0, 0]  # Depot at origin

    # Distance matrix
    distances_np = np.sqrt(
        ((locations[:, np.newaxis] - locations[np.newaxis, :]) ** 2).sum(axis=2)
    )
    distances_gpu = cp.asarray(distances_np, dtype=cp.float32)

    print(f"Locations:\n{locations}\n")
    print(f"Distance Matrix:\n{distances_np}\n")

    # Initial tour
    tour = [0, 1, 2, 3, 4, 0]

    def compute_cost(tour, dist):
        return sum(dist[tour[i], tour[i + 1]] for i in range(len(tour) - 1))

    initial_cost = compute_cost(tour, distances_np)
    print(f"Initial tour: {tour}")
    print(f"Initial cost: {initial_cost:.4f}\n")

    # Run debug GPU 2-opt
    strategy = TwoOptGPUDebug(max_iterations=1, threads_per_block=256)
    improved = strategy.improve_tour(tour, distances_gpu)

    final_cost = compute_cost(improved, distances_np)
    print(f"\nFinal tour: {improved}")
    print(f"Final cost: {final_cost:.4f}")
    print(
        f"Improvement: {initial_cost - final_cost:.4f} ({100 * (initial_cost - final_cost) / initial_cost:.2f}%)"
    )


if __name__ == "__main__":
    test_debug()
