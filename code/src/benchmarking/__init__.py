"""
Statistical analysis for Chapter 4 validation benchmarks.

This module provides statistical testing functions for comparing
ISO-algorithmic GA variants:
- Friedman test for multiple algorithm comparison
- Nemenyi post-hoc test for pairwise comparison
- Wilcoxon signed-rank test
- Effect size calculation (Cohen's d)

See Also:
    - statistics.py: StatisticalAnalyzer class implementation
"""

from .statistics import StatisticalAnalyzer

__all__ = ["StatisticalAnalyzer"]
