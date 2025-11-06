#!/usr/bin/env python3
"""
Validate BackendModule Protocol Implementation.

Tests that NumPy and CuPy (if available) satisfy the BackendModule protocol
defined in code/src/protocols/backend.py.

Usage:
    python scripts/validate_backend_protocol.py

    # Or with uv:
    uv run python scripts/validate_backend_protocol.py
"""

import sys
from typing import List, Tuple


def test_backend_protocol(xp, backend_name: str) -> Tuple[bool, List[str]]:
    """
    Test if backend module satisfies BackendModule protocol.

    Args:
        xp: Backend module (numpy or cupy)
        backend_name: Human-readable name for reporting

    Returns:
        Tuple of (success: bool, errors: List[str])
    """
    errors = []

    # Test array creation methods
    creation_methods = ["array", "zeros", "ones", "empty", "asarray", "arange", "full"]

    # Test mathematical operations
    math_methods = ["sqrt", "sum", "abs", "ceil", "floor"]

    # Test trigonometric functions
    trig_methods = ["sin", "cos", "arcsin", "arccos", "radians"]

    # Test reduction operations
    reduction_methods = ["any", "all", "max", "min", "argmax", "argmin"]

    # Test advanced indexing
    indexing_methods = ["ix_"]

    # Test constants
    constants = ["inf", "newaxis"]

    all_methods = (
        creation_methods
        + math_methods
        + trig_methods
        + reduction_methods
        + indexing_methods
    )

    # Check methods exist
    print(f"\n{'=' * 60}")
    print(f"Testing {backend_name}")
    print(f"{'=' * 60}\n")

    print("Checking methods...")
    for method in all_methods:
        if not hasattr(xp, method):
            errors.append(f"Missing method: {method}()")
            print(f"  ❌ {method}()")
        else:
            print(f"  ✅ {method}()")

    print("\nChecking constants...")
    for const in constants:
        if not hasattr(xp, const):
            errors.append(f"Missing constant: {const}")
            print(f"  ❌ {const}")
        else:
            print(f"  ✅ {const}")

    # Functional tests
    print("\nFunctional tests...")

    try:
        # Test array creation
        arr = xp.array([1, 2, 3, 4, 5])
        assert arr.shape == (5,), "array() failed"
        print("  ✅ Array creation")

        # Test zeros/ones
        zeros = xp.zeros((3, 3))
        ones = xp.ones((2, 2))
        assert zeros.shape == (3, 3), "zeros() failed"
        assert ones.shape == (2, 2), "ones() failed"
        print("  ✅ zeros() and ones()")

        # Test arange
        range_arr = xp.arange(0, 10, 2)
        assert len(range_arr) == 5, "arange() failed"
        print("  ✅ arange()")

        # Test full
        filled = xp.full((2, 3), 7.5)
        assert filled.shape == (2, 3), "full() failed"
        print("  ✅ full()")

        # Test math operations
        arr_float = xp.array([1.0, 4.0, 9.0, 16.0])
        sqrt_arr = xp.sqrt(arr_float)
        sum_val = xp.sum(arr_float)
        print("  ✅ sqrt() and sum()")

        # Test trigonometric
        angles = xp.array([0.0, 0.5, 1.0])
        sin_vals = xp.sin(angles)
        cos_vals = xp.cos(angles)
        arccos_vals = xp.arccos(xp.array([1.0, 0.5, -1.0]))
        print("  ✅ Trigonometric functions (sin, cos, arccos)")

        # Test reductions
        bool_arr = xp.array([True, False, True])
        any_result = xp.any(bool_arr)
        all_result = xp.all(bool_arr)
        assert any_result == True, "any() failed"
        assert all_result == False, "all() failed"
        print("  ✅ any() and all()")

        max_val = xp.max(arr)
        min_val = xp.min(arr)
        assert max_val == 5, "max() failed"
        assert min_val == 1, "min() failed"
        print("  ✅ max() and min()")

        argmax_idx = xp.argmax(arr)
        argmin_idx = xp.argmin(arr)
        assert argmax_idx == 4, "argmax() failed"
        assert argmin_idx == 0, "argmin() failed"
        print("  ✅ argmax() and argmin()")

        # Test fancy indexing
        matrix = xp.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        subset = matrix[xp.ix_([0, 2], [0, 2])]
        assert subset.shape == (2, 2), "ix_() failed"
        print("  ✅ ix_() fancy indexing")

        # Test constants
        inf_val = xp.inf
        assert inf_val > 1e100, "inf constant failed"
        print("  ✅ inf constant")

        # Test newaxis
        expanded = arr[:, xp.newaxis]
        assert expanded.shape == (5, 1), "newaxis failed"
        print("  ✅ newaxis constant")

    except Exception as e:
        errors.append(f"Functional test failed: {e}")
        print(f"  ❌ Functional test error: {e}")

    # Backend-specific tests
    print("\nBackend-specific features...")

    if hasattr(xp, "asnumpy"):
        print("  ✅ asnumpy() available (CuPy-specific)")
        try:
            test_arr = xp.array([1, 2, 3])
            cpu_arr = xp.asnumpy(test_arr)
            print(f"     Transfer test: {type(cpu_arr).__name__}")
        except Exception as e:
            print(f"     ⚠️  asnumpy() exists but failed: {e}")
    else:
        print("  ℹ️  asnumpy() not available (NumPy doesn't need it)")

    if hasattr(xp, "get_array_module"):
        print("  ✅ get_array_module() available (CuPy-specific)")
    else:
        print("  ℹ️  get_array_module() not available (NumPy-only)")

    # Summary
    print(f"\n{'=' * 60}")
    if errors:
        print(f"❌ {backend_name} FAILED with {len(errors)} error(s):")
        for error in errors:
            print(f"   - {error}")
        return False, errors
    else:
        print(f"✅ {backend_name} PASSED all tests")
        print(f"{'=' * 60}\n")
        return True, []


def main():
    """Main validation script."""
    print("=" * 60)
    print("BackendModule Protocol Validation")
    print("=" * 60)

    results = {}

    # Test NumPy (always available)
    print("\n[1/2] Testing NumPy...")
    try:
        import numpy as np

        success, errors = test_backend_protocol(np, "NumPy (CPU)")
        results["NumPy"] = success
    except ImportError as e:
        print(f"❌ NumPy not available: {e}")
        results["NumPy"] = False
        return 1

    # Test CuPy (optional)
    print("\n[2/2] Testing CuPy...")
    try:
        import cupy as cp

        success, errors = test_backend_protocol(cp, "CuPy (GPU)")
        results["CuPy"] = success
    except ImportError:
        print("\nℹ️  CuPy not installed (optional)")
        print("   To install: pip install cupy-cuda12x")
        results["CuPy"] = None
    except Exception as e:
        print(f"❌ CuPy test failed: {e}")
        results["CuPy"] = False

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    for backend, status in results.items():
        if status is True:
            print(f"✅ {backend}: PASSED")
        elif status is False:
            print(f"❌ {backend}: FAILED")
        else:
            print(f"ℹ️  {backend}: SKIPPED (not installed)")

    print("=" * 60)

    # Exit code
    if results["NumPy"] and (results["CuPy"] in [True, None]):
        print("\n🎉 Protocol validation successful!")
        return 0
    else:
        print("\n💥 Protocol validation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
