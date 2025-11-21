"""Test the reduction logic in isolation with the hybrid parallel+serial approach."""

import cupy as cp
import numpy as np

# CUDA kernel with hybrid reduction (parallel for large strides, serial for tail)
reduction_kernel_code = r"""
extern "C" __global__ void test_reduction(
    int* values,
    int* result,
    int block_size
) {
    extern __shared__ int s_values[];
    
    int tid = threadIdx.x;
    
    // Load value
    if (tid < block_size) {
        s_values[tid] = values[tid];
    } else {
        s_values[tid] = 2147483647;  // Max int (neutral for min reduction)
    }
    __syncthreads();
    
    // Parallel reduction for strides down to 1
    // Key insight: bound check prevents accessing threads outside block_size
    for (unsigned int s = block_size / 2; s > 0; s >>= 1) {
        if (tid < s) {
            int partner = tid + s;
            if (partner < block_size && s_values[partner] < s_values[tid]) {
                s_values[tid] = s_values[partner];
            }
        }
        __syncthreads();
    }
    
    // Thread 0 has the final result after full reduction
    if (tid == 0) {
        *result = s_values[0];
    }
}
"""
"""

# Compile kernel
module = cp.RawModule(code=reduction_kernel_code)
reduction_kernel = module.get_function("test_reduction")

def test_block_size(block_size):
    """Test reduction with a specific block size.
    
    Input: thread i has value -i (so thread block_size-1 should win)
    """
    # Create input where thread i has value -i
    values_cpu = np.array([-i for i in range(block_size)], dtype=np.int32)
    values_gpu = cp.asarray(values_cpu)
    result_gpu = cp.zeros(1, dtype=np.int32)
    
    # Use next power of 2 for block size (CUDA requirement)
    threads = 1 << (block_size - 1).bit_length()  # Next power of 2
    shared_mem = threads * 4  # 4 bytes per int
    
    # Launch kernel
    reduction_kernel(
        (1,), (threads,),
        (values_gpu, result_gpu, block_size, shared_mem)
    )
    
    result = int(result_gpu.get()[0])
    expected = -(block_size - 1)
    
    if result == expected:
        print(f"✅ Block size {block_size:3d}: Found value {result:4d} (thread {-result})")
        return True
    else:
        print(f"❌ Block size {block_size:3d}: Found value {result:4d} (thread {-result}), expected {expected} (thread {block_size-1})")
        return False

# Test various block sizes
print("Testing hybrid parallel+serial reduction:")
print("=" * 60)

test_sizes = [32, 64, 98, 100, 128, 256]
results = []

for size in test_sizes:
    success = test_block_size(size)
    results.append(success)

print("=" * 60)
if all(results):
    print("✅ ALL TESTS PASSED - Reduction works for all block sizes!")
else:
    print("❌ SOME TESTS FAILED")
