from numba import cuda

@cuda.jit
def cube(x):
    x[0] = x[0] ** 3

try:
    data = cuda.to_device([2])
    cube[1, 1](data)
    result = data.copy_to_host()
    print("Success, result: ", result)
except cuda.CudaSupportError as e:
    print("CUDA initialization failed: ", str(e))
except Exception as e:
    print("Error: ", str(e))
