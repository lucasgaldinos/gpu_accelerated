"""
Backend module protocol for NumPy/CuPy interoperability.

This module defines typing.Protocol interfaces that ensure type-safe
backend switching between NumPy (CPU) and CuPy (GPU) implementations.

The protocol pattern allows type checkers to validate that code using
backend modules (passed as `xp` parameter) only calls methods that exist
in both NumPy and CuPy.

Example:
    >>> import numpy as np
    >>> def compute_distance(coords, xp: BackendModule):
    ...     # Type checker knows xp.sqrt and xp.sum are safe
    ...     diff = coords[:, None, :] - coords[None, :, :]
    ...     return xp.sqrt(xp.sum(diff**2, axis=2))

> [!important] For later documentation
"""

from typing import Any, Optional, Protocol, Tuple, Union


class BackendModule(Protocol):
    """
    Protocol defining required operations for backend modules (NumPy/CuPy).

    This protocol specifies the minimum set of operations required by
    distance calculation functions. Both NumPy and CuPy satisfy this protocol.

    The protocol ensures:
    - Type safety when switching backends
    - Clear documentation of backend requirements
    - Prevention of accidentally using backend-specific methods

    Attributes:
        ndarray: Array type for the backend (numpy.ndarray or cupy.ndarray)

    Note:
        Return types use `Any` because NumPy and CuPy have incompatible
        array type hierarchies. Type checkers will still validate that
        methods exist and are called correctly.
    """

    # Array creation and conversion
    def array(
        self,
        object: Any,
        dtype: Optional[Any] = None,
        *,
        copy: Optional[bool] = None,
        order: Optional[str] = None,
        ndmin: int = 0,
    ) -> Any:
        """
        Create an array from an object.

        Args:
            object: Array-like object to convert
            dtype: Desired data type
            copy: If True, ensure array is copied
            order: Memory layout ('C' or 'F')
            ndmin: Minimum number of dimensions

        Returns:
            Array (numpy.ndarray or cupy.ndarray)
        """
        ...

    def zeros(
        self, shape: Union[int, Tuple[int, ...]], dtype: Optional[Any] = None
    ) -> Any:
        """Create array filled with zeros."""
        ...

    def ones(
        self, shape: Union[int, Tuple[int, ...]], dtype: Optional[Any] = None
    ) -> Any:
        """Create array filled with ones."""
        ...

    def empty(
        self, shape: Union[int, Tuple[int, ...]], dtype: Optional[Any] = None
    ) -> Any:
        """Create uninitialized array."""
        ...

    # Mathematical operations
    def sqrt(self, x: Any) -> Any:
        """Element-wise square root."""
        ...

    def sum(
        self,
        a: Any,
        axis: Optional[Union[int, Tuple[int, ...]]] = None,
        keepdims: bool = False,
    ) -> Any:
        """Sum array elements over given axis."""
        ...

    def abs(self, x: Any) -> Any:
        """Element-wise absolute value."""
        ...

    def ceil(self, x: Any) -> Any:
        """Element-wise ceiling (round up)."""
        ...

    def floor(self, x: Any) -> Any:
        """Element-wise floor (round down)."""
        ...

    # Trigonometric functions (needed for GEO distance)
    def sin(self, x: Any) -> Any:
        """Element-wise sine."""
        ...

    def cos(self, x: Any) -> Any:
        """Element-wise cosine."""
        ...

    def arcsin(self, x: Any) -> Any:
        """Element-wise inverse sine (arcsine)."""
        ...

    def radians(self, x: Any) -> Any:
        """Convert degrees to radians."""
        ...

    # Array manipulation
    def asarray(self, a: Any, dtype: Optional[Any] = None) -> Any:
        """
        Convert input to array (avoid copy if possible).

        Note: For axis expansion, use None instead of xp.newaxis:
            coords[:, None, :]  # Correct - works with all backends
            coords[:, xp.newaxis, :]  # Also correct, but None is simpler
        """
        ...

    def arccos(self, x: Any) -> Any:
        """Element-wise inverse cosine (arccosine)."""
        ...

    # Reduction operations
    def any(
        self,
        a: Any,
        axis: Optional[Union[int, Tuple[int, ...]]] = None,
        keepdims: bool = False,
    ) -> Any:
        """
        Test whether any array element evaluates to True.

        Args:
            a: Input array or condition
            axis: Axis along which to perform reduction
            keepdims: Keep reduced dimensions as size 1

        Returns:
            Boolean or array of booleans
        """
        ...

    def all(
        self,
        a: Any,
        axis: Optional[Union[int, Tuple[int, ...]]] = None,
        keepdims: bool = False,
    ) -> Any:
        """
        Test whether all array elements evaluate to True.

        Args:
            a: Input array or condition
            axis: Axis along which to perform reduction
            keepdims: Keep reduced dimensions as size 1

        Returns:
            Boolean or array of booleans
        """
        ...

    def max(
        self,
        a: Any,
        axis: Optional[Union[int, Tuple[int, ...]]] = None,
        keepdims: bool = False,
    ) -> Any:
        """
        Return maximum value along axis.

        Args:
            a: Input array
            axis: Axis along which to find maximum
            keepdims: Keep reduced dimensions as size 1

        Returns:
            Maximum value(s)
        """
        ...

    def min(
        self,
        a: Any,
        axis: Optional[Union[int, Tuple[int, ...]]] = None,
        keepdims: bool = False,
    ) -> Any:
        """
        Return minimum value along axis.

        Args:
            a: Input array
            axis: Axis along which to find minimum
            keepdims: Keep reduced dimensions as size 1

        Returns:
            Minimum value(s)
        """
        ...

    def argmax(
        self,
        a: Any,
        axis: Optional[int] = None,
    ) -> Any:
        """
        Return indices of maximum values along axis.

        Args:
            a: Input array
            axis: Axis along which to find argmax

        Returns:
            Index or array of indices
        """
        ...

    def argmin(
        self,
        a: Any,
        axis: Optional[int] = None,
    ) -> Any:
        """
        Return indices of minimum values along axis.

        Args:
            a: Input array
            axis: Axis along which to find argmin

        Returns:
            Index or array of indices
        """
        ...

    # Array creation (additional)
    def arange(
        self,
        start: Union[int, float],
        stop: Optional[Union[int, float]] = None,
        step: Union[int, float] = 1,
        dtype: Optional[Any] = None,
    ) -> Any:
        """
        Return evenly spaced values within interval.

        Args:
            start: Start of interval (or stop if only one arg)
            stop: End of interval
            step: Spacing between values
            dtype: Desired data type

        Returns:
            Array of evenly spaced values
        """
        ...

    def full(
        self,
        shape: Union[int, Tuple[int, ...]],
        fill_value: Any,
        dtype: Optional[Any] = None,
    ) -> Any:
        """
        Create array filled with specific value.

        Args:
            shape: Shape of array
            fill_value: Value to fill array with
            dtype: Desired data type

        Returns:
            Array filled with fill_value
        """
        ...

    # Advanced indexing
    def ix_(self, *args: Any) -> Tuple[Any, ...]:
        """
        Construct open mesh from multiple sequences.

        Used for fancy indexing to extract submatrices.

        Args:
            *args: 1-D sequences (arrays or lists)

        Returns:
            Tuple of arrays for indexing

        Example:
            >>> subset_matrix = full_matrix[xp.ix_([0,2,3], [0,2,3])]
        """
        ...

    # Constants (attributes, not methods)
    @property
    def inf(self) -> float:
        """Positive infinity constant."""
        ...

    @property
    def newaxis(self) -> Any:
        """
        Constant for adding new axes to arrays.

        Note: Using None is equivalent and more portable:
            arr[:, None, :]  # Recommended
            arr[:, xp.newaxis, :]  # Also works
        """
        ...


# ==============================================================================
# CuPy-Specific Methods (Not in Protocol)
# ==============================================================================

"""
Some operations are specific to CuPy and not available in NumPy.
Use hasattr() to check for these methods before calling:

**CuPy-only methods:**

1. **xp.asnumpy(arr)** - Transfer CuPy array to NumPy (GPU → CPU)
   
   Usage pattern:
   ```python
   if hasattr(xp, 'asnumpy'):
       cpu_array = xp.asnumpy(gpu_array)  # CuPy → NumPy
   else:
       cpu_array = np.asarray(gpu_array)  # NumPy (no-op)
   ```

2. **xp.get_array_module(arr)** - Get backend module from array
   
   Usage pattern:
   ```python
   import numpy as np
   try:
       import cupy as cp
       xp = cp.get_array_module(distances)  # Returns cp if CuPy array
   except ImportError:
       xp = np
   ```

**NumPy-only methods:**

- Most NumPy-specific methods have CuPy equivalents
- Check CuPy documentation for compatibility: https://docs.cupy.dev/

**Type checking:**

The protocol uses `Any` for return types because NumPy and CuPy have
incompatible type hierarchies. To check array types at runtime:

```python
import numpy as np
try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False

def is_gpu_array(arr):
    '''Check if array is CuPy array (on GPU).'''
    if CUPY_AVAILABLE:
        return isinstance(arr, cp.ndarray)
    return False

def is_cpu_array(arr):
    '''Check if array is NumPy array (on CPU).'''
    return isinstance(arr, np.ndarray)
```

**Backend detection:**

```python
def get_backend_name(xp):
    '''Get human-readable backend name.'''
    if xp.__name__ == 'cupy':
        return 'CuPy (GPU)'
    elif xp.__name__ == 'numpy':
        return 'NumPy (CPU)'
    else:
        return f'Unknown ({xp.__name__})'
```
"""


# ==============================================================================
# Backend Utility Functions (Lego Bricks for Backend Configuration)
# ==============================================================================

import numpy as np

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False


def get_backend(backend: str) -> Any:
    """
    Get backend module by name (lego brick for backend configuration).

    Enables explicit backend selection in algorithms instead of relying
    on implicit backend from ProblemContext.

    Args:
        backend: Backend name string
            - "numpy": NumPy (CPU) - safe default for all problem sizes
            - "cupy": CuPy (GPU) - requires CUDA, best for large problems (n>1000)

    Returns:
        Backend module (numpy or cupy)

    Raises:
        ValueError: If backend name invalid
        RuntimeError: If cupy requested but not installed

    Example:
        >>> xp = get_backend("numpy")  # CPU
        >>> xp = get_backend("cupy")   # GPU
        >>> arr = xp.array([1, 2, 3])

    Note:
        Numba JIT acceleration is NOT a backend option here because Numba
        operates at the strategy/function level via @jit decorators, not
        at the array module level. For Numba acceleration, implement
        Numba-decorated strategy classes (e.g., Numba2OptStrategy).
        > In fact, numba is not an option anywhere this repo, for now.

    Reference:
        Backend Configuration Architecture (M14_M15_DETAILED_TASKS.md)
        METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 2.1
    """
    if backend == "numpy":
        return np
    elif backend == "cupy":
        if not CUPY_AVAILABLE:
            raise RuntimeError(
                "Backend 'cupy' requested but CuPy not installed.\n"
                "Install with: pip install cupy-cuda12x (for CUDA 12.x)\n"
                "Or: pip install cupy-cuda11x (for CUDA 11.x)"
            )
        return cp
    else:
        raise ValueError(f"Invalid backend '{backend}'. Valid options: 'numpy', 'cupy'")


def get_backend_name(xp) -> str:
    """
    Get human-readable backend name.

    Args:
        xp: Backend module (numpy or cupy)

    Returns:
        Human-readable name: "NumPy (CPU)", "CuPy (GPU)", or "Unknown"

    Example:
        >>> import numpy as np
        >>> get_backend_name(np)
        'NumPy (CPU)'
    """
    if xp.__name__ == "cupy":
        return "CuPy (GPU)"
    elif xp.__name__ == "numpy":
        return "NumPy (CPU)"
    else:
        return f"Unknown ({xp.__name__})"


def is_gpu_array(arr) -> bool:
    """
    Check if array is CuPy array (on GPU).

    Args:
        arr: Array to check

    Returns:
        True if CuPy array, False otherwise
    """
    if CUPY_AVAILABLE:
        return isinstance(arr, cp.ndarray)
    return False


def is_cpu_array(arr) -> bool:
    """
    Check if array is NumPy array (on CPU).

    Args:
        arr: Array to check

    Returns:
        True if NumPy array, False otherwise
    """
    return isinstance(arr, np.ndarray)
