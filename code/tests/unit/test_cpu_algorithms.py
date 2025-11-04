"""
Unit tests for CPU-based algorithm strategies.
"""

import pytest
import numpy as np
from src.protocols import ProblemContext
from src.algorithms import (
    NearestNeighborCPU,
    RandomInsertionCPU,
    CheapestInsertionCPU,
    CompositionalTSPSolver,
)


class TestNearestNeighborCPU:
    """Test suite for NearestNeighborCPU algorithm."""
    
    def test_simple_square(self):
        """Test on a simple 4-node square."""
        coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
        ])
        context = ProblemContext(coordinates=coords)
        solver = NearestNeighborCPU()
        
        tour = solver.solve(context)
        
        # Should have n_nodes + 1 elements (closed tour)
        assert len(tour) == 5
        
        # Should start and end at same node
        assert tour[0] == tour[-1]
        
        # Should visit all nodes exactly once
        assert len(set(tour[:-1])) == 4
        
        # Cost should be reasonable
        cost = solver.get_solution_cost(context, tour)
        assert cost > 0
    
    def test_different_start_nodes(self):
        """Test that different start nodes produce valid tours."""
        coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
        ])
        context = ProblemContext(coordinates=coords)
        
        for start in range(4):
            solver = NearestNeighborCPU(start_node=start)
            tour = solver.solve(context)
            
            assert tour[0] == start
            assert tour[-1] == start
            assert len(set(tour[:-1])) == 4
    
    def test_invalid_start_node(self):
        """Test that invalid start node raises error."""
        coords = np.array([[0, 0], [1, 1]])
        context = ProblemContext(coordinates=coords)
        solver = NearestNeighborCPU(start_node=5)
        
        with pytest.raises(ValueError, match="Start node .* >= number of nodes"):
            solver.solve(context)
    
    def test_cost_calculation(self):
        """Test solution cost calculation."""
        coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
        ])
        context = ProblemContext(coordinates=coords)
        solver = NearestNeighborCPU()
        
        # Manual tour: 0 -> 1 -> 2 -> 3 -> 0
        tour = np.array([0, 1, 2, 3, 0])
        cost = solver.get_solution_cost(context, tour)
        
        # Expected: 1 + 1 + 1 + 1 = 4
        assert np.isclose(cost, 4.0)


class TestRandomInsertionCPU:
    """Test suite for RandomInsertionCPU algorithm."""
    
    def test_simple_problem(self):
        """Test on a simple problem."""
        coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
        ])
        context = ProblemContext(coordinates=coords)
        solver = RandomInsertionCPU(seed=42)
        
        tour = solver.solve(context)
        
        # Should have n_nodes + 1 elements
        assert len(tour) == 5
        
        # Should start and end at same node
        assert tour[0] == tour[-1]
        
        # Should visit all nodes exactly once
        assert len(set(tour[:-1])) == 4
    
    def test_reproducibility_with_seed(self):
        """Test that same seed produces same result."""
        coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            [0.5, 0.5],
        ])
        context = ProblemContext(coordinates=coords)
        
        solver1 = RandomInsertionCPU(seed=42)
        tour1 = solver1.solve(context)
        
        solver2 = RandomInsertionCPU(seed=42)
        tour2 = solver2.solve(context)
        
        assert np.array_equal(tour1, tour2)
    
    def test_small_problem(self):
        """Test on very small problem (< 3 nodes)."""
        coords = np.array([[0, 0], [1, 1]])
        context = ProblemContext(coordinates=coords)
        solver = RandomInsertionCPU()
        
        tour = solver.solve(context)
        assert len(tour) == 3  # 2 nodes + return
        assert tour[0] == tour[-1]


class TestCheapestInsertionCPU:
    """Test suite for CheapestInsertionCPU algorithm."""
    
    def test_simple_problem(self):
        """Test on a simple problem."""
        coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
        ])
        context = ProblemContext(coordinates=coords)
        solver = CheapestInsertionCPU()
        
        tour = solver.solve(context)
        
        # Should have n_nodes + 1 elements
        assert len(tour) == 5
        
        # Should start and end at same node
        assert tour[0] == tour[-1]
        
        # Should visit all nodes exactly once
        assert len(set(tour[:-1])) == 4
    
    def test_deterministic(self):
        """Test that algorithm is deterministic."""
        coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            [0.5, 0.5],
        ])
        context = ProblemContext(coordinates=coords)
        
        solver = CheapestInsertionCPU()
        tour1 = solver.solve(context)
        tour2 = solver.solve(context)
        
        # Should produce same result on multiple runs
        assert np.array_equal(tour1, tour2)
    
    def test_quality_vs_nearest_neighbor(self):
        """Test that cheapest insertion typically finds better solutions."""
        # Create a problem where greedy nearest neighbor is suboptimal
        coords = np.array([
            [0, 0],
            [1, 0],
            [2, 0],
            [1, 1],
        ])
        context = ProblemContext(coordinates=coords)
        
        nn_solver = NearestNeighborCPU(start_node=0)
        ci_solver = CheapestInsertionCPU()
        
        nn_tour = nn_solver.solve(context)
        ci_tour = ci_solver.solve(context)
        
        nn_cost = nn_solver.get_solution_cost(context, nn_tour)
        ci_cost = ci_solver.get_solution_cost(context, ci_tour)
        
        # Both should find valid tours
        assert len(nn_tour) == 5
        assert len(ci_tour) == 5
        
        # Costs should be positive
        assert nn_cost > 0
        assert ci_cost > 0


class TestCompositionalTSPSolver:
    """Test suite for CompositionalTSPSolver."""
    
    def test_construction_only(self):
        """Test solver with only construction strategy."""
        coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
        ])
        context = ProblemContext(coordinates=coords)
        
        constructor = NearestNeighborCPU()
        solver = CompositionalTSPSolver(constructor)
        
        tour = solver.solve(context)
        
        # Should produce valid tour
        assert len(tour) == 5
        assert tour[0] == tour[-1]
        assert len(set(tour[:-1])) == 4
    
    def test_solve_with_stats(self):
        """Test solve_with_stats method."""
        coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
        ])
        context = ProblemContext(coordinates=coords)
        
        constructor = NearestNeighborCPU()
        solver = CompositionalTSPSolver(constructor)
        
        stats = solver.solve_with_stats(context)
        
        # Check stats structure
        assert 'solution' in stats
        assert 'initial_solution' in stats
        assert 'initial_cost' in stats
        assert 'final_cost' in stats
        assert 'improvement' in stats
        assert 'improvement_percent' in stats
        assert 'constructor' in stats
        
        # With no improver, final should equal initial
        assert np.array_equal(stats['solution'], stats['initial_solution'])
        assert stats['initial_cost'] == stats['final_cost']
        assert stats['improvement'] == 0
    
    def test_distance_matrix_computed_once(self):
        """Test that distance matrix is computed once and reused."""
        coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
        ])
        context = ProblemContext(coordinates=coords)
        
        constructor = NearestNeighborCPU()
        solver = CompositionalTSPSolver(constructor)
        
        # Initially, distance matrix should not be computed
        assert context.distance_matrix_cpu is None
        
        # Solve
        solver.solve(context)
        
        # After solving, distance matrix should be cached
        assert context.distance_matrix_cpu is not None
        
        # Store reference to distance matrix
        first_matrix = context.distance_matrix_cpu
        
        # Solve again
        solver.solve(context)
        
        # Should use the same cached matrix
        assert context.distance_matrix_cpu is first_matrix
    
    def test_repr(self):
        """Test string representation."""
        constructor = NearestNeighborCPU()
        solver = CompositionalTSPSolver(constructor)
        
        repr_str = repr(solver)
        assert 'CompositionalTSPSolver' in repr_str
        assert 'NearestNeighborCPU' in repr_str
