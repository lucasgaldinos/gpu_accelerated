from math import e
import time
from numba import njit, cuda
import numpy as np

def time_function(func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    print(f"{func.__name__} took {end_time - start_time:.6f} seconds.")
    return result

# 1. Pure Python
def sum_of_squares_pure(data):
    return sum(x**2 for x in data)

data = list(range(9999999))


# Timing Pure Python
result_pure = time_function(sum_of_squares_pure, data)

# 2. Numba
@njit
def sum_of_squares_numba(data):
    total = 0
    for x in data:
        total += x**2
    return total

# Timing Numba
result_numba = time_function(sum_of_squares_numba, np.array(data))

# 3. Numba + GPU
@cuda.jit
def sum_of_squares_gpu(data, result):
    idx = cuda.grid(1)
    if idx < data.size:
        cuda.atomic.add(result, 0, data[idx] ** 2)

# Initialize CPU data with np.arange
data_cpu = np.arange(1000000, dtype=np.float32)

# Transfer the data to the GPU
data_gpu = cuda.to_device(data_cpu)

# Also initialize a result array on the GPU
result_gpu = cuda.to_device(np.zeros(1, dtype=np.float32))

# Call the GPU kernel with timing
threads_per_block = 256
blocks_per_grid = (data_cpu.size + (threads_per_block - 1)) // threads_per_block

# Timing Numba + GPU execution
def gpu_function_call():
    sum_of_squares_gpu[blocks_per_grid, threads_per_block](data_gpu, result_gpu)
    cuda.synchronize()  # Ensure the kernel has finished

time_function(gpu_function_call)

# Transfer the result back to CPU
result_cpu = result_gpu.copy_to_host()

# Print the result
print("Sum of squares (GPU):", result_cpu[0])
