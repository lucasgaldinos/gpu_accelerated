"""
Tests for backend protocol compatibility.

Validates that NumPy and CuPy satisfy the BackendModule protocol
and that common operations work correctly with both backends.
"""

import numpy as np
import pytest

from src.protocols.backend import BackendModule


def test_numpy_satisfies_protocol():
    """Verify NumPy satisfies the BackendModule protocol."""
    # This will pass type checking if NumPy satisfies the protocol
    backend: BackendModule = np

    # Test basic operations
    arr = backend.array([1, 2, 3, 4])
    assert arr.shape == (4,)

    # Test mathematical operations
    result = backend.sqrt(backend.sum(arr**2))
    expected = np.sqrt(1 + 4 + 9 + 16)
    assert abs(result - expected) < 1e-10


def test_cupy_satisfies_protocol():
    """Verify CuPy satisfies the BackendModule protocol (if available)."""
    try:
        import cupy as cp
    except ImportError:
        pytest.skip("CuPy not available")

    # This will pass type checking if CuPy satisfies the protocol
    backend: BackendModule = cp

    # Test basic operations
    arr = backend.array([1, 2, 3, 4])
    assert arr.shape == (4,)

    # Test mathematical operations
    result = backend.sqrt(backend.sum(arr**2))
    expected = np.sqrt(1 + 4 + 9 + 16)
    # Convert CuPy result to Python float for comparison
    result_scalar = float(cp.asnumpy(result))
    assert abs(result_scalar - expected) < 1e-10


def test_backend_array_creation():
    """Test array creation methods work with both backends."""
    backends = [np]
    try:
        import cupy as cp

        backends.append(cp)
    except ImportError:
        pass

    for xp in backends:
        # Test zeros
        zeros = xp.zeros((3, 2))
        assert zeros.shape == (3, 2)
        assert xp.sum(zeros) == 0

        # Test ones
        ones = xp.ones(5)
        assert ones.shape == (5,)
        assert xp.sum(ones) == 5

        # Test empty (just check shape)
        empty = xp.empty((2, 2))
        assert empty.shape == (2, 2)


def test_backend_trigonometric_functions():
    """Test trigonometric functions needed for GEO distance."""
    backends = [np]
    try:
        import cupy as cp

        backends.append(cp)
    except ImportError:
        pass

    for xp in backends:
        # Test radians conversion
        degrees = xp.array([0, 90, 180, 360])
        radians = xp.radians(degrees)

        # Test sin
        sin_vals = xp.sin(radians)
        assert abs(sin_vals[0]) < 1e-10  # sin(0) = 0
        assert abs(sin_vals[1] - 1.0) < 1e-10  # sin(90°) = 1

        # Test cos
        cos_vals = xp.cos(radians)
        assert abs(cos_vals[0] - 1.0) < 1e-10  # cos(0) = 1
        assert abs(cos_vals[1]) < 1e-10  # cos(90°) = 0


def test_backend_equivalence():
    """Verify NumPy and CuPy produce identical results for same operations."""
    try:
        import cupy as cp
    except ImportError:
        pytest.skip("CuPy not available for equivalence test")

    # Test data
    coords = np.random.rand(5, 2)

    # Compute with NumPy
    diff_np = coords[:, None, :] - coords[None, :, :]
    dist_np = np.sqrt(np.sum(diff_np**2, axis=2))

    # Compute with CuPy
    coords_cp = cp.array(coords)
    diff_cp = coords_cp[:, None, :] - coords_cp[None, :, :]
    dist_cp = cp.sqrt(cp.sum(diff_cp**2, axis=2))

    # Results should be identical (within floating point precision)
    np.testing.assert_allclose(dist_np, cp.asnumpy(dist_cp), rtol=1e-6)


def test_newaxis_usage():
    """Verify None works for axis expansion (newaxis equivalent)."""
    backends = [np]
    try:
        import cupy as cp

        backends.append(cp)
    except ImportError:
        pass

    for xp in backends:
        arr = xp.array([[1, 2], [3, 4]])

        # Using None for newaxis (protocol-compatible)
        expanded = arr[:, None, :]
        assert expanded.shape == (2, 1, 2)

        # Both None and xp.newaxis should work
        expanded2 = arr[:, xp.newaxis, :]
        assert expanded2.shape == (2, 1, 2)
