"""
Backend protocols for type safety across NumPy/CuPy implementations.

This package defines typing.Protocol interfaces that ensure type safety
when switching between NumPy (CPU) and CuPy (GPU) backends.

It also includes ProblemContext (not a protocol), which provides backend-specific
problem data caching to eliminate distance matrix recomputation anti-patterns.
"""

from .backend import BackendModule
from .bin_packing_protocol import BinPackingStrategy
from .problem_context import ProblemContext

__all__ = ["BackendModule", "BinPackingStrategy", "ProblemContext"]
