#!/usr/bin/env python3
"""Test reduction correctness with explicit thread tracking."""

import numpy as np
import cupy as cp

# Test kernel that outputs per-thread results
test_kernel = """
extern "C" __global__
void test_reduction(
    double *input,     // Input values per thread
    int *indices,      // Index per thread
    double *output,    // Best value after reduction
    int *best_idx,     // Best index after reduction
    int *thread_map    // Debug: which threads participated
) {
    extern __shared__ double sdata[];
    int *sidx = (int*)&sdata[blockDim.x];
    
    int tid = threadIdx.x;
    int block_size = blockDim.x;
    
    // Load
    sdata[tid] = input[tid];
    sidx[tid] = indices[tid];
    
    // Mark initial participation
    if (tid == 0) {
        for (int i = 0; i < block_size; i++) {
            thread_map[i] = 1;  // All start as participated
        }
    }
    __syncthreads();
    
    // Reduction with tracking
    for (unsigned int s = block_size / 2; s > 0; s >>= 1) {
        if (tid < s) {
            if (sdata[tid + s] < sdata[tid]) {
                sdata[tid] = sdata[tid + s];
                sidx[tid] = sidx[tid + s];
            }
        }
        __syncthreads();
    }
    
    if (tid == 0) {
        *output = sdata[0];
        *best_idx = sidx[0];
    }
}
"""


def test_reduction(n_threads):
    print(f"\nTesting with {n_threads} threads:")

    # Create test data: thread i has value -i
    # So thread with highest index should win (most negative)
    values = np.array([-float(i) for i in range(n_threads)], dtype=np.float64)
    indices = np.arange(n_threads, dtype=np.int32)

    # GPU
    kernel = cp.RawKernel(test_kernel, "test_reduction")
    values_gpu = cp.asarray(values)
    indices_gpu = cp.asarray(indices)
    output_gpu = cp.zeros(1, dtype=np.float64)
    best_idx_gpu = cp.zeros(1, dtype=np.int32)
    thread_map = cp.zeros(n_threads, dtype=np.int32)

    shared = n_threads * 8 + n_threads * 4
    kernel(
        (1,),
        (n_threads,),
        (values_gpu, indices_gpu, output_gpu, best_idx_gpu, thread_map),
        shared_mem=shared,
    )

    result_val = float(output_gpu.get()[0])
    result_idx = int(best_idx_gpu.get()[0])

    expected_val = -(n_threads - 1)
    expected_idx = n_threads - 1

    if result_idx == expected_idx:
        print(f"  ✅ Correct: found thread {result_idx} with value {result_val}")
    else:
        print(f"  ❌ Wrong: found thread {result_idx} (value {result_val})")
        print(f"           expected thread {expected_idx} (value {expected_val})")

    return result_idx == expected_idx


# Test various sizes
sizes = [32, 64, 98, 100, 128, 256]
results = []

for size in sizes:
    success = test_reduction(size)
    results.append((size, success))

print("\n" + "=" * 50)
print("SUMMARY:")
for size, success in results:
    status = "✅" if success else "❌"
    print(f"  {size:3d} threads: {status}")
