"""
TSP improvement algorithms (local search heuristics).

This module contains tour improvement strategies that refine initial solutions
constructed by construction heuristics.

Available Strategies:
    - TwoOptCPU: Sequential 2-opt local search on CPU
    - TwoOptGPU: Parallel 2-opt local search on GPU (Fujimoto 2011)

Design Pattern:
    All improvement strategies implement the TspImprovementStrategy protocol,
    enabling runtime strategy selection via dependency injection.

Example Usage:
    >>> from .two_opt_cpu import TwoOptCPU
    >>> from .two_opt_gpu import TwoOptGPU
    >>>
    >>> # CPU improvement
    >>> cpu_strategy = TwoOptCPU(max_iterations=1000)
    >>> improved_tour = cpu_strategy.improve_tour(tour, distances, xp=np)
    >>>
    >>> # GPU improvement
    >>> gpu_strategy = TwoOptGPU(max_iterations=1000)
    >>> improved_tour = gpu_strategy.improve_tour(tour, distances, xp=cp)

See Also:
    - protocols.algorithm_strategies.TspImprovementStrategy
    - algorithms.construction (tour construction)
"""

__all__ = ["TwoOptCPU", "TwoOptGPU"]


# Lazy imports to avoid circular dependencies
def __getattr__(name: str):
    if name == "TwoOptCPU":
        from .two_opt_cpu import TwoOptCPU

        return TwoOptCPU
    elif name == "TwoOptGPU":
        from .two_opt_gpu import TwoOptGPU

        return TwoOptGPU
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
