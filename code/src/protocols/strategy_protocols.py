"""
Protocol definitions for CPU and GPU optimization strategies.

This module defines the protocol interfaces that all optimization strategies
must implement. By separating CPU and GPU protocols, we enforce backend
selection at the class level rather than through runtime parameters.
"""

from typing import Protocol, runtime_checkable
import numpy as np
from .problem_context import ProblemContext

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False


@runtime_checkable
class CPUStrategy(Protocol):
    """
    Protocol for CPU-based optimization strategies.
    
    All CPU strategies must implement this interface. They work exclusively
    with NumPy arrays and the CPU distance matrix from ProblemContext.
    """
    
    def solve(self, context: ProblemContext) -> np.ndarray:
        """
        Solve the optimization problem using CPU computation.
        
        Args:
            context: ProblemContext containing problem data
            
        Returns:
            Solution as numpy array of node indices representing the tour/routes
        """
        ...
    
    def get_solution_cost(self, context: ProblemContext, solution: np.ndarray) -> float:
        """
        Calculate the cost of a given solution using CPU computation.
        
        Args:
            context: ProblemContext containing problem data
            solution: Solution array
            
        Returns:
            Total cost/distance of the solution
        """
        ...


@runtime_checkable
class GPUStrategy(Protocol):
    """
    Protocol for GPU-based optimization strategies.
    
    All GPU strategies must implement this interface. They work with CuPy arrays
    and the GPU distance matrix from ProblemContext.
    """
    
    def solve(self, context: ProblemContext):
        """
        Solve the optimization problem using GPU computation.
        
        Args:
            context: ProblemContext containing problem data
            
        Returns:
            Solution as CuPy array (or numpy after transfer) of node indices
        """
        ...
    
    def get_solution_cost(self, context: ProblemContext, solution) -> float:
        """
        Calculate the cost of a given solution using GPU computation.
        
        Args:
            context: ProblemContext containing problem data
            solution: Solution array (CuPy or numpy)
            
        Returns:
            Total cost/distance of the solution
        """
        ...


@runtime_checkable
class ImprovementStrategy(Protocol):
    """
    Protocol for improvement strategies that refine existing solutions.
    
    These strategies take an initial solution and improve it through
    local search or other optimization techniques.
    """
    
    def improve(self, context: ProblemContext, initial_solution: np.ndarray) -> np.ndarray:
        """
        Improve an existing solution.
        
        Args:
            context: ProblemContext containing problem data
            initial_solution: Initial solution to improve
            
        Returns:
            Improved solution
        """
        ...


@runtime_checkable
class ComposableStrategy(Protocol):
    """
    Protocol for strategies that can be composed together.
    
    This enables the "Lego brick" pattern where different strategies
    can be combined to create more sophisticated solvers.
    """
    
    def execute(self, context: ProblemContext, **kwargs):
        """
        Execute the strategy as part of a composition.
        
        Args:
            context: ProblemContext containing problem data
            **kwargs: Additional parameters for composition
            
        Returns:
            Result of strategy execution (type depends on strategy)
        """
        ...
