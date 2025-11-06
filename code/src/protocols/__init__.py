"""
Backend protocols for type safety across NumPy/CuPy implementations.

This package defines typing.Protocol interfaces that ensure type safety
when switching between NumPy (CPU) and CuPy (GPU) backends.
"""

from .backend import BackendModule
from .bin_packing_protocol import BinPackingStrategy

__all__ = ["BackendModule", "BinPackingStrategy"]
