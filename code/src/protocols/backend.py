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
