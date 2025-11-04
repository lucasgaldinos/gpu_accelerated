"""
FIXED GPU 2-opt implementation based on debug findings.

Root cause: The tour was not being fully loaded into shared memory because
we only had 3 threads but 5 tour elements to load. Fixed by using a loop
to ensure all elements are loaded.

Author: Debug session
Date: 2025-01-27
"""

import cupy as cp
import numpy as np
from typing import List


class TwoOptGPUFixed:
    """Fixed GPU 2-opt implementation."""

    def __init__(self, max_iterations: int = 100, threads_per_block: int = 256):
        self.max_iterations = max_iterations
        self.threads_per_block = threads_per_block
        self._compile_kernel()

    def _compile_kernel(self):
        """Compile CUDA kernel with tour loading fix."""
        kernel_code = r"""
        extern "C" __global__
        void two_opt_fixed_kernel(
            int *tour,
            const float *dist,
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
            
            // Initialize shared memory for this thread
            s_deltas[tid] = 0.0f;
            s_swap_i[tid] = -1;
            s_swap_j[tid] = -1;
            
            // Each thread evaluates a subset of i positions
            for (int i = tid; i < n - 2; i += block_size) {
                int node_i = s_tour[i];
                int node_i1 = s_tour[i + 1];
                
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
                    
                    // Update best for this thread (delta < 0 means improvement)
                    if (delta < s_deltas[tid]) {
                        s_deltas[tid] = delta;
                        s_swap_i[tid] = i;
                        s_swap_j[tid] = j;
                    }
                }
            }
            __syncthreads();
            
            // Parallel reduction to find minimum delta (most negative = best improvement)
            // Handle small block sizes correctly
            if (tid < 16 && tid + 16 < block_size && s_deltas[tid + 16] < s_deltas[tid]) {
                s_deltas[tid] = s_deltas[tid + 16];
                s_swap_i[tid] = s_swap_i[tid + 16];
                s_swap_j[tid] = s_swap_j[tid + 16];
            }
            __syncthreads();
            
            if (tid < 8 && tid + 8 < block_size && s_deltas[tid + 8] < s_deltas[tid]) {
                s_deltas[tid] = s_deltas[tid + 8];
                s_swap_i[tid] = s_swap_i[tid + 8];
                s_swap_j[tid] = s_swap_j[tid + 8];
            }
            __syncthreads();
            
            if (tid < 4 && tid + 4 < block_size && s_deltas[tid + 4] < s_deltas[tid]) {
                s_deltas[tid] = s_deltas[tid + 4];
                s_swap_i[tid] = s_swap_i[tid + 4];
                s_swap_j[tid] = s_swap_j[tid + 4];
            }
            __syncthreads();
            
            if (tid < 2 && tid + 2 < block_size && s_deltas[tid + 2] < s_deltas[tid]) {
                s_deltas[tid] = s_deltas[tid + 2];
                s_swap_i[tid] = s_swap_i[tid + 2];
                s_swap_j[tid] = s_swap_j[tid + 2];
            }
            __syncthreads();
            
            if (tid < 1 && tid + 1 < block_size && s_deltas[tid + 1] < s_deltas[tid]) {
                s_deltas[0] = s_deltas[1];
                s_swap_i[0] = s_swap_i[1];
                s_swap_j[0] = s_swap_j[1];
            }
            __syncthreads();
            
            // Apply best swap (Thread 0 only)
            if (tid == 0 && s_deltas[0] < 0.0f) {
                int swap_i = s_swap_i[0];
                int swap_j = s_swap_j[0];
                
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
            }
            __syncthreads();
            
            // FIX: Write back using loop to handle n > block_size
            for (int i = tid; i < n; i += block_size) {
                tour[i] = s_tour[i];
            }
        }
        """

        self._kernel = cp.RawKernel(kernel_code, "two_opt_fixed_kernel")

    def improve_tour(self, tour: List[int], distances: cp.ndarray, xp=cp) -> List[int]:
        """
        Run one iteration of 2-opt improvement.

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

        # Calculate shared memory size
        shared_mem_size = (
            self.threads_per_block * 4  # s_deltas (float)
            + self.threads_per_block * 4  # s_swap_i (int)
            + self.threads_per_block * 4  # s_swap_j (int)
            + n * 4  # s_tour (int)
        )

        # Launch kernel
        block_size = min(self.threads_per_block, n - 2)

        self._kernel(
            (1,),  # 1 block
            (block_size,),  # threads per block
            (tour_gpu, distances, n, 0),
            shared_mem=shared_mem_size,
        )

        # Synchronize
        cp.cuda.Device().synchronize()

        # Convert back to list with duplicate depot
        improved_tour = tour_gpu.get().tolist()
        improved_tour.append(0)

        return improved_tour


def test_fixed():
    """Test the fixed version."""
    print("Testing Fixed GPU 2-Opt\n")

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

    # Run fixed GPU 2-opt
    strategy = TwoOptGPUFixed(max_iterations=1, threads_per_block=256)
    improved = strategy.improve_tour(tour, distances_gpu)

    final_cost = compute_cost(improved, distances_np)
    improvement_pct = 100 * (initial_cost - final_cost) / initial_cost

    print(f"GPU improved tour: {improved}")
    print(f"GPU final cost: {final_cost:.4f}")
    print(
        f"GPU improvement: {initial_cost - final_cost:.4f} ({improvement_pct:.2f}%)\n"
    )

    # Compare with CPU
    import sys

    sys.path.insert(0, "/home/lucas_galdino/TCC-name_to_define/gpu_accelerated")
    from src.algorithms.improvement.two_opt_cpu import TwoOptCPU

    cpu_strategy = TwoOptCPU(max_iterations=1)
    cpu_tour = tour.copy()
    cpu_improved = cpu_strategy.improve_tour(cpu_tour, distances_np, xp=np)
    cpu_cost = compute_cost(cpu_improved, distances_np)
    cpu_improvement_pct = 100 * (initial_cost - cpu_cost) / initial_cost

    print(f"CPU improved tour: {cpu_improved}")
    print(f"CPU final cost: {cpu_cost:.4f}")
    print(
        f"CPU improvement: {initial_cost - cpu_cost:.4f} ({cpu_improvement_pct:.2f}%)\n"
    )

    # Verify they match
    if abs(final_cost - cpu_cost) < 0.01:
        print("✅ GPU and CPU results MATCH!")
    else:
        print("❌ GPU and CPU results DIFFER!")
        print(f"   Difference: {abs(final_cost - cpu_cost):.4f}")


if __name__ == "__main__":
    test_fixed()
