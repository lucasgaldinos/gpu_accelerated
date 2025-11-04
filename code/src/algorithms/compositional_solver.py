"""
Compositional TSP Solver demonstrating the "Lego block" pattern.

This solver combines multiple strategies (construction + improvement)
to create a complete TSP solving approach.
"""

import numpy as np
from ..protocols import ProblemContext, CPUStrategy


class CompositionalTSPSolver:
    """
    Compositional TSP solver that combines construction and improvement strategies.
    
    This demonstrates the "Lego block" architectural pattern where different
    algorithm strategies can be composed together to form a complete solver.
    
    Example usage:
        # Construct initial solution with Nearest Neighbor
        constructor = NearestNeighborCPU()
        
        # Create compositional solver
        solver = CompositionalTSPSolver(constructor)
        
        # Solve
        solution = solver.solve(context)
    """
    
    def __init__(self, constructor: CPUStrategy, improver=None):
        """
        Initialize compositional solver.
        
        Args:
            constructor: Strategy to construct initial solution
            improver: Optional improvement strategy to refine solution
        """
        self.constructor = constructor
        self.improver = improver
    
    def solve(self, context: ProblemContext) -> np.ndarray:
        """
        Solve TSP using composition of strategies.
        
        Args:
            context: ProblemContext with problem data
            
        Returns:
            Final solution as numpy array
        """
        # Phase 1: Construct initial solution
        initial_solution = self.constructor.solve(context)
        
        # Phase 2: Improve if improver is provided
        if self.improver is not None:
            if hasattr(self.improver, 'improve'):
                final_solution = self.improver.improve(context, initial_solution)
            else:
                # If improver doesn't have improve method, treat it as a solver
                final_solution = self.improver.solve(context, initial_solution)
        else:
            final_solution = initial_solution
        
        return final_solution
    
    def get_solution_cost(self, context: ProblemContext, solution: np.ndarray) -> float:
        """
        Calculate solution cost using the constructor's cost method.
        
        Args:
            context: ProblemContext with problem data
            solution: Solution to evaluate
            
        Returns:
            Total cost
        """
        return self.constructor.get_solution_cost(context, solution)
    
    def solve_with_stats(self, context: ProblemContext) -> dict:
        """
        Solve and return detailed statistics about the solving process.
        
        Args:
            context: ProblemContext with problem data
            
        Returns:
            Dictionary with solution, costs, and statistics
        """
        # Compute distance matrix once (it will be cached in context)
        context.compute_distance_matrix_cpu()
        
        # Construct initial solution
        initial_solution = self.constructor.solve(context)
        initial_cost = self.constructor.get_solution_cost(context, initial_solution)
        
        # Improve if improver is provided
        if self.improver is not None:
            if hasattr(self.improver, 'improve'):
                final_solution = self.improver.improve(context, initial_solution)
            else:
                final_solution = self.improver.solve(context, initial_solution)
            final_cost = self.constructor.get_solution_cost(context, final_solution)
            improvement = initial_cost - final_cost
            improvement_pct = (improvement / initial_cost) * 100
        else:
            final_solution = initial_solution
            final_cost = initial_cost
            improvement = 0
            improvement_pct = 0
        
        return {
            'solution': final_solution,
            'initial_solution': initial_solution,
            'initial_cost': initial_cost,
            'final_cost': final_cost,
            'improvement': improvement,
            'improvement_percent': improvement_pct,
            'constructor': str(self.constructor),
            'improver': str(self.improver) if self.improver else None,
        }
    
    def __repr__(self) -> str:
        improver_str = f", improver={self.improver}" if self.improver else ""
        return f"CompositionalTSPSolver(constructor={self.constructor}{improver_str})"


if __name__ == "__main__":
    # This is a demonstration - actual usage would import strategies
    print("CompositionalTSPSolver - combine different 'Lego bricks' to solve TSP")
    print("Example: NearestNeighbor (construction) + 2-Opt (improvement)")
