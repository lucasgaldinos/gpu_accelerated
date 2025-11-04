"""
Composable Solver - Framework for combining optimization strategies.

This module provides the "Lego block" composition framework that allows
different optimization strategies to be combined in flexible ways.
"""

from typing import List, Union, Optional, Callable
import numpy as np
from numpy.typing import NDArray
import time

from ..utils.problem_context import ProblemContext


class ComposableSolver:
    """
    Framework for composing multiple optimization strategies.
    
    This class enables hybrid metaheuristics by allowing strategies to be
    chained together, where each strategy can build upon the results of
    previous strategies.
    """
    
    def __init__(self, problem: ProblemContext):
        """
        Initialize the solver with a problem context.
        
        Args:
            problem: Problem context with coordinates and cached distance matrix
        """
        self.problem = problem
        self.history: List[dict] = []
    
    def solve(
        self,
        strategies: List[tuple],
        initial_solution: Optional[NDArray[np.int_]] = None,
        verbose: bool = False
    ) -> tuple[NDArray[np.int_], float, dict]:
        """
        Solve the problem using a sequence of strategies.
        
        Args:
            strategies: List of (strategy, kwargs) tuples
            initial_solution: Optional starting solution
            verbose: Whether to print progress
            
        Returns:
            Tuple of (best_solution, best_cost, metrics)
        """
        current_solution = initial_solution
        current_cost = float('inf')
        
        metrics = {
            'stages': [],
            'total_time': 0.0,
            'improvement_history': []
        }
        
        start_time = time.time()
        
        for idx, (strategy, kwargs) in enumerate(strategies):
            stage_start = time.time()
            
            # Determine which method to call based on strategy type
            if hasattr(strategy, 'construct'):
                # Constructive strategy
                solution, cost = strategy.construct(
                    self.problem.distance_matrix,
                    **kwargs
                )
            elif hasattr(strategy, 'improve'):
                # Improvement strategy
                if current_solution is None:
                    raise ValueError("Improvement strategy requires initial solution")
                solution, cost = strategy.improve(
                    current_solution,
                    self.problem.distance_matrix,
                    **kwargs
                )
            elif hasattr(strategy, 'search'):
                # Metaheuristic strategy
                if current_solution is None:
                    raise ValueError("Metaheuristic strategy requires initial solution")
                solution, cost = strategy.search(
                    current_solution,
                    self.problem.distance_matrix,
                    **kwargs
                )
            else:
                raise ValueError(f"Unknown strategy type: {type(strategy)}")
            
            stage_time = time.time() - stage_start
            
            # Track improvement
            improvement = current_cost - cost if current_cost != float('inf') else 0.0
            improvement_pct = (improvement / current_cost * 100) if current_cost not in (float('inf'), 0.0) else 0.0
            
            # Update current solution
            current_solution = solution
            current_cost = cost
            
            # Record metrics
            stage_metrics = {
                'stage': idx,
                'strategy': strategy.name,
                'backend': strategy.backend,
                'cost': cost,
                'improvement': improvement,
                'improvement_pct': improvement_pct,
                'time': stage_time
            }
            metrics['stages'].append(stage_metrics)
            metrics['improvement_history'].append(cost)
            
            if verbose:
                print(f"Stage {idx + 1}: {strategy.name} ({strategy.backend})")
                print(f"  Cost: {cost:.2f}")
                print(f"  Improvement: {improvement:.2f} ({improvement_pct:.2f}%)")
                print(f"  Time: {stage_time:.3f}s")
        
        metrics['total_time'] = time.time() - start_time
        
        return current_solution, current_cost, metrics
    
    def benchmark_strategies(
        self,
        strategies: List[tuple],
        n_runs: int = 5,
        verbose: bool = False
    ) -> dict:
        """
        Benchmark a sequence of strategies over multiple runs.
        
        Args:
            strategies: List of (strategy, kwargs) tuples
            n_runs: Number of benchmark runs
            verbose: Whether to print progress
            
        Returns:
            Dictionary with benchmark statistics
        """
        results = {
            'costs': [],
            'times': [],
            'runs': []
        }
        
        for run in range(n_runs):
            if verbose:
                print(f"\n=== Run {run + 1}/{n_runs} ===")
            
            solution, cost, metrics = self.solve(strategies, verbose=verbose)
            
            results['costs'].append(cost)
            results['times'].append(metrics['total_time'])
            results['runs'].append(metrics)
        
        # Calculate statistics
        costs = np.array(results['costs'])
        times = np.array(results['times'])
        
        statistics = {
            'mean_cost': np.mean(costs),
            'std_cost': np.std(costs),
            'min_cost': np.min(costs),
            'max_cost': np.max(costs),
            'mean_time': np.mean(times),
            'std_time': np.std(times),
            'runs': results['runs']
        }
        
        return statistics


class StrategyChain:
    """
    Builder for creating strategy chains with a fluent interface.
    
    Example:
        chain = (StrategyChain()
            .construct_with(nearest_neighbor)
            .improve_with(two_opt, max_iterations=100)
            .optimize_with(simulated_annealing, max_iterations=5000)
        )
    """
    
    def __init__(self):
        self.strategies: List[tuple] = []
    
    def construct_with(self, strategy, **kwargs):
        """Add a constructive strategy."""
        self.strategies.append((strategy, kwargs))
        return self
    
    def improve_with(self, strategy, **kwargs):
        """Add an improvement strategy."""
        self.strategies.append((strategy, kwargs))
        return self
    
    def optimize_with(self, strategy, **kwargs):
        """Add a metaheuristic strategy."""
        self.strategies.append((strategy, kwargs))
        return self
    
    def build(self) -> List[tuple]:
        """Build the strategy list."""
        return self.strategies
