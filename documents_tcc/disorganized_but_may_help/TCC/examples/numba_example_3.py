from numba import njit, cuda, prange # type: ignore
import numpy as np
import cupy as cp  # Ensure CuPy is installed to use it

import time


def time_function(func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    print(f"{func.__name__} took {end_time - start_time:.6f} seconds.")
    return result


data_cpu = np.arange(9999999, dtype=np.float32)

# Numba CPU Implementation


@njit(parallel=False)
def sum_of_squares_numba_cpu(data):
    total = 0
    for i in range(data.size):
        total += data[i] ** 2
    return total


result_numba_cpu = time_function(sum_of_squares_numba_cpu, data_cpu)
print("Sum of squares (CPU):", result_numba_cpu)

# Adding a NumPy reduction equivalent


def sum_of_squares_numpy(data):
    return np.sum(data ** 2)


result_numpy = time_function(sum_of_squares_numpy, data_cpu)
print("Sum of squares (NumPy):", result_numpy)

# Numba CPU Parallel Implementation


@njit(parallel=True)
def sum_of_squares_numba_cpu_parallel(data):
    total = 0.0
    for i in prange(data.size):
        total += data[i] ** 2
    return total


result_numba_cpu_parallel = time_function(
    sum_of_squares_numba_cpu_parallel, data_cpu)
print("Sum of squares (CPU) parallel:", result_numba_cpu_parallel)

# Numba GPU Implementation


@cuda.jit
def sum_of_squares_numba_gpu(data, result):
    idx = cuda.grid(1)
    if idx < data.size:
        cuda.atomic.add(result, 0, data[idx] ** 2)


data_gpu = cuda.to_device(data_cpu)
result_gpu = cuda.to_device(np.zeros(1, dtype=np.float32))

threads_per_block = 256
blocks_per_grid = (data_cpu.size + (threads_per_block - 1)
                   ) // threads_per_block


def gpu_function_call():
    sum_of_squares_numba_gpu[blocks_per_grid,
                             threads_per_block](data_gpu, result_gpu)
    cuda.synchronize()


time_function(gpu_function_call)

result_numba_gpu = result_gpu.copy_to_host()[0]
print("Sum of squares (GPU):", result_numba_gpu)

# Adding a CuPy reduction equivalent
data_cupy = cp.array(data_cpu)  # Transfer data to GPU with CuPy


def sum_of_squares_cupy(data):
    return cp.sum(data ** 2)


# Use .get() to transfer result back to CPU
result_cupy = time_function(sum_of_squares_cupy, data_cupy).get()
print("Sum of squares (CuPy):", result_cupy)
