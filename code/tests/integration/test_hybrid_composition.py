"""
Integration tests for ComposableSolver and hybrid strategies.
"""

import numpy as np
import pytest

from src.algorithms import (
    NearestNeighborStrategy,
    TwoOptStrategy,
    SimulatedAnnealingStrategy,
    GeneticAlgorithmStrategy,
    ComposableSolver,
    StrategyChain,
)
from src.utils.problem_context import ProblemContext


def test_composable_solver_single_strategy():
    """Test solver with a single constructive strategy."""
    context = ProblemContext.from_random(10, seed=42)
    solver = ComposableSolver(context)
    
    nn = NearestNeighborStrategy()
    strategies = [(nn, {'start_node': 0})]
    
    solution, cost, metrics = solver.solve(strategies)
    
    assert len(solution) == 10
    assert context.validate_tour(solution)
    assert cost > 0
    assert len(metrics['stages']) == 1


def test_composable_solver_construction_then_improvement():
    """Test composition of constructive + improvement strategies."""
    context = ProblemContext.from_random(15, seed=42)
    solver = ComposableSolver(context)
    
    nn = NearestNeighborStrategy()
    two_opt = TwoOptStrategy()
    
    strategies = [
        (nn, {'start_node': 0}),
        (two_opt, {'max_iterations': 100}),
    ]
    
    solution, cost, metrics = solver.solve(strategies)
    
    assert len(solution) == 15
    assert context.validate_tour(solution)
    assert len(metrics['stages']) == 2
    
    # Two-opt should improve or maintain cost
    nn_cost = metrics['stages'][0]['cost']
    two_opt_cost = metrics['stages'][1]['cost']
    assert two_opt_cost <= nn_cost


def test_composable_solver_hybrid_metaheuristic():
    """Test hybrid composition with metaheuristics."""
    context = ProblemContext.from_random(12, seed=42)
    solver = ComposableSolver(context)
    
    nn = NearestNeighborStrategy()
    sa = SimulatedAnnealingStrategy(
        initial_temperature=50.0,
        cooling_rate=0.95,
        seed=42
    )
    
    strategies = [
        (nn, {'start_node': 0}),
        (sa, {'max_iterations': 500}),
    ]
    
    solution, cost, metrics = solver.solve(strategies)
    
    assert len(solution) == 12
    assert context.validate_tour(solution)
    assert len(metrics['stages']) == 2


def test_composable_solver_four_strategies():
    """Test composition of 4 different strategies (Lego bricks)."""
    context = ProblemContext.from_random(10, seed=42)
    solver = ComposableSolver(context)
    
    # Four different "Lego bricks"
    nn = NearestNeighborStrategy()
    two_opt = TwoOptStrategy()
    sa = SimulatedAnnealingStrategy(initial_temperature=30.0, seed=42)
    ga = GeneticAlgorithmStrategy(population_size=20, seed=42)
    
    strategies = [
        (nn, {'start_node': 0}),
        (two_opt, {'max_iterations': 50}),
        (sa, {'max_iterations': 200}),
        (ga, {'max_iterations': 10}),
    ]
    
    solution, cost, metrics = solver.solve(strategies, verbose=False)
    
    assert len(solution) == 10
    assert context.validate_tour(solution)
    assert len(metrics['stages']) == 4
    
    # Each strategy should be recorded
    assert metrics['stages'][0]['strategy'] == 'NearestNeighbor'
    assert metrics['stages'][1]['strategy'] == 'TwoOpt'
    assert metrics['stages'][2]['strategy'] == 'SimulatedAnnealing'
    assert metrics['stages'][3]['strategy'] == 'GeneticAlgorithm'


def test_strategy_chain_builder():
    """Test the StrategyChain fluent interface."""
    context = ProblemContext.from_random(10, seed=42)
    solver = ComposableSolver(context)
    
    nn = NearestNeighborStrategy()
    two_opt = TwoOptStrategy()
    sa = SimulatedAnnealingStrategy(seed=42)
    
    chain = (StrategyChain()
        .construct_with(nn, start_node=0)
        .improve_with(two_opt, max_iterations=50)
        .optimize_with(sa, max_iterations=200)
    )
    
    strategies = chain.build()
    solution, cost, metrics = solver.solve(strategies)
    
    assert len(solution) == 10
    assert context.validate_tour(solution)
    assert len(metrics['stages']) == 3


def test_solver_benchmark():
    """Test benchmarking functionality."""
    context = ProblemContext.from_random(8, seed=42)
    solver = ComposableSolver(context)
    
    nn = NearestNeighborStrategy()
    two_opt = TwoOptStrategy()
    
    strategies = [
        (nn, {'start_node': 0}),
        (two_opt, {'max_iterations': 50}),
    ]
    
    stats = solver.benchmark_strategies(strategies, n_runs=3, verbose=False)
    
    assert 'mean_cost' in stats
    assert 'std_cost' in stats
    assert 'mean_time' in stats
    assert len(stats['runs']) == 3


def test_solver_improvement_tracking():
    """Test that improvement is properly tracked."""
    context = ProblemContext.from_random(10, seed=42)
    solver = ComposableSolver(context)
    
    nn = NearestNeighborStrategy()
    two_opt = TwoOptStrategy()
    
    strategies = [
        (nn, {'start_node': 0}),
        (two_opt, {'max_iterations': 100}),
    ]
    
    solution, cost, metrics = solver.solve(strategies)
    
    # Check improvement history
    assert len(metrics['improvement_history']) == 2
    
    # Two-opt should not increase cost
    assert metrics['improvement_history'][1] <= metrics['improvement_history'][0]
