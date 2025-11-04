"""
Protocol definitions for optimization strategies.
"""

from .strategy import (
    OptimizationStrategy,
    ConstructiveStrategy,
    ImprovementStrategy,
    MetaheuristicStrategy,
)

__all__ = [
    'OptimizationStrategy',
    'ConstructiveStrategy',
    'ImprovementStrategy',
    'MetaheuristicStrategy',
]
