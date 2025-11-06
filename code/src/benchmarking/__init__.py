"""
Benchmarking infrastructure for statistically rigorous performance evaluation.

This module implements the experimental design from Section 3.5, providing:
- Multi-run orchestration with seed management
- Convergence tracking and metrics collection
- Statistical analysis (normality tests, hypothesis tests, effect sizes)
- Report generation (tables, plots, LaTeX/Markdown output)

Architecture:
    - config.py: Data structures for benchmark configuration and results
    - runner.py: BenchmarkRunner orchestrator for multi-run execution
    - collectors.py: Metrics collection and convergence tracking
    - statistics.py: Statistical analysis functions (scipy integration)
    - reporting.py: Table and plot generation
    - utils.py: Helper functions (seed generation, memory monitoring)

Usage Example:
    >>> from benchmarking import BenchmarkRunner, BenchmarkConfig
    >>> config = BenchmarkConfig(
    ...     algorithm="SA",
    ...     backend="numpy",
    ...     instance_name="berlin52",
    ...     num_repetitions=30
    ... )
    >>> runner = BenchmarkRunner()
    >>> results = runner.run_benchmark(config, problem)
    >>> runner.export_results("results.csv")
"""

from .config import BenchmarkConfig, BenchmarkResult, ComparisonPair
from .runner import BenchmarkRunner
from .collectors import ConvergenceTracker, MetricsCollector
from .statistics import StatisticalAnalyzer, StatisticalSummary
from .reporting import ReportGenerator

__all__ = [
    "BenchmarkConfig",
    "BenchmarkResult",
    "ComparisonPair",
    "BenchmarkRunner",
    "ConvergenceTracker",
    "MetricsCollector",
    "StatisticalAnalyzer",
    "StatisticalSummary",
    "ReportGenerator",
]
