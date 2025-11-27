import numpy as np
from numba import njit, jit

def numpy_kde(eval_points, samples, bandwidths):
    # This uses a lot of RAM and doesn't scale to larger datasets
    rescaled_x = (eval_points[:, np.newaxis] - samples[np.newaxis, :]) / bandwidths[np.newaxis, :]
    gaussian = np.exp(-0.5 * rescaled_x**2) / np.sqrt(2 * np.pi) / bandwidths[np.newaxis, :]
    return gaussian.sum(axis=1) / len(samples)

@njit
def gaussian(x):
    return np.exp(-0.5 * x**2) / np.sqrt(2 * np.pi)

@jit(nopython=True)
def nb_kde(eval_points, samples, bandwidths):
    result = np.zeros_like(eval_points)

    for i, eval_x in enumerate(eval_points):
        for sample, bandwidth in zip(samples, bandwidths):
            result[i] += gaussian((eval_x - sample) / bandwidth) / bandwidth
        result[i] /= len(samples)

    return result

@jit(nopython=True, parallel=True)
def nb_kde_multithread(eval_points, samples, bandwidths):
    result = np.zeros_like(eval_points)

    # SPEEDTIP: Parallelize over evaluation points with prange()
    for i in nb.prange(len(eval_points)):
        eval_x = eval_points[i]
        for sample, bandwidth in zip(samples, bandwidths):
            result[i] += gaussian((eval_x - sample) / bandwidth) / bandwidth
        result[i] /= len(samples)

    return result

def main():
    print(numpy_kde)
    print(nb_kde)
    print(nb_kde_multithread)