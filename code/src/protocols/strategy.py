"""
Strategy Protocol - Defines the interface for optimization strategies.

This protocol enables the "Lego brick" pattern where different optimization
strategies can be composed together to form hybrid metaheuristics.
"""

from typing import Protocol, TypeVar, runtime_checkable
import numpy as np
from numpy.typing import NDArray


# Type variables for flexibility
SolutionType = TypeVar('SolutionType', bound=NDArray[np.int_])
CostType = TypeVar('CostType', bound=float)


@runtime_checkable
class OptimizationStrategy(Protocol):
    """
    Protocol defining the interface for optimization strategies.
    
    This allows for modular, composable optimization components that can
    work on CPU or GPU, sequentially or in parallel.
    """
    
    def optimize(
        self,
        solution: NDArray[np.int_],
        distance_matrix: NDArray[np.float64],
        **kwargs
    ) -> tuple[NDArray[np.int_], float]:
        """
        Optimize a given solution.
        
        Args:
            solution: Current solution as array of node indices
            distance_matrix: Precomputed distance matrix
            **kwargs: Strategy-specific parameters
            
        Returns:
            Tuple of (improved_solution, cost)
        """
        ...
    
    @property
    def name(self) -> str:
        """Return the strategy name for logging/debugging."""
        ...
    
    @property
    def backend(self) -> str:
        """Return the computational backend (cpu, gpu, etc.)."""
        ...


@runtime_checkable
class ConstructiveStrategy(Protocol):
    """
    Protocol for constructive heuristics that build solutions from scratch.
    """
    
    def construct(
        self,
        distance_matrix: NDArray[np.float64],
        start_node: int = 0,
        **kwargs
    ) -> tuple[NDArray[np.int_], float]:
        """
        Construct a solution from scratch.
        
        Args:
            distance_matrix: Precomputed distance matrix
            start_node: Starting node index
            **kwargs: Strategy-specific parameters
            
        Returns:
            Tuple of (solution, cost)
        """
        ...
    
    @property
    def name(self) -> str:
        """Return the strategy name."""
        ...
    
    @property
    def backend(self) -> str:
        """Return the computational backend."""
        ...


@runtime_checkable
class ImprovementStrategy(Protocol):
    """
    Protocol for improvement heuristics that enhance existing solutions.
    """
    
    def improve(
        self,
        solution: NDArray[np.int_],
        distance_matrix: NDArray[np.float64],
        max_iterations: int = 1000,
        **kwargs
    ) -> tuple[NDArray[np.int_], float]:
        """
        Improve an existing solution.
        
        Args:
            solution: Current solution to improve
            distance_matrix: Precomputed distance matrix
            max_iterations: Maximum number of improvement iterations
            **kwargs: Strategy-specific parameters
            
        Returns:
            Tuple of (improved_solution, cost)
        """
        ...
    
    @property
    def name(self) -> str:
        """Return the strategy name."""
        ...
    
    @property
    def backend(self) -> str:
        """Return the computational backend."""
        ...


@runtime_checkable
class MetaheuristicStrategy(Protocol):
    """
    Protocol for metaheuristic strategies (SA, GA, ACO, etc.).
    """
    
    def search(
        self,
        initial_solution: NDArray[np.int_],
        distance_matrix: NDArray[np.float64],
        max_iterations: int = 10000,
        **kwargs
    ) -> tuple[NDArray[np.int_], float]:
        """
        Perform metaheuristic search.
        
        Args:
            initial_solution: Starting solution
            distance_matrix: Precomputed distance matrix
            max_iterations: Maximum search iterations
            **kwargs: Strategy-specific parameters (temperature, population, etc.)
            
        Returns:
            Tuple of (best_solution, best_cost)
        """
        ...
    
    @property
    def name(self) -> str:
        """Return the strategy name."""
        ...
    
    @property
    def backend(self) -> str:
        """Return the computational backend."""
        ...
