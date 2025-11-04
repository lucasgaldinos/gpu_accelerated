"""
Protocol definitions and core data structures for the optimization framework.
"""

from .problem_context import ProblemContext, CUPY_AVAILABLE
from .strategy_protocols import (
    CPUStrategy,
    GPUStrategy,
    ImprovementStrategy,
    ComposableStrategy,
)

__all__ = [
    'ProblemContext',
    'CUPY_AVAILABLE',
    'CPUStrategy',
    'GPUStrategy',
    'ImprovementStrategy',
    'ComposableStrategy',
]
