"""
Unit tests for NearestNeighbor strategy.
"""

import numpy as np
import pytest

from src.algorithms.nearest_neighbor import NearestNeighborStrategy
from src.utils.problem_context import ProblemContext


def test_nearest_neighbor_construction():
    """Test basic nearest neighbor tour construction."""
    # Simple 4-node square problem
    coords = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float64)
    context = ProblemContext(coordinates=coords)
    
    strategy = NearestNeighborStrategy()
    tour, cost = strategy.construct(context.distance_matrix, start_node=0)
    
    # Check tour is valid
    assert len(tour) == 4
    assert len(set(tour)) == 4  # All nodes visited once
    assert tour[0] == 0  # Starts at node 0


def test_nearest_neighbor_properties():
    """Test strategy properties."""
    strategy = NearestNeighborStrategy(backend="cpu")
    
    assert strategy.name == "NearestNeighbor"
    assert strategy.backend == "cpu"


def test_nearest_neighbor_deterministic():
    """Test that nearest neighbor is deterministic."""
    context = ProblemContext.from_random(10, seed=42)
    strategy = NearestNeighborStrategy()
    
    tour1, cost1 = strategy.construct(context.distance_matrix, start_node=0)
    tour2, cost2 = strategy.construct(context.distance_matrix, start_node=0)
    
    assert np.array_equal(tour1, tour2)
    assert cost1 == cost2


def test_nearest_neighbor_different_starts():
    """Test that different start nodes produce different tours."""
    context = ProblemContext.from_random(10, seed=42)
    strategy = NearestNeighborStrategy()
    
    tour1, cost1 = strategy.construct(context.distance_matrix, start_node=0)
    tour2, cost2 = strategy.construct(context.distance_matrix, start_node=5)
    
    # Tours should start at different nodes
    assert tour1[0] == 0
    assert tour2[0] == 5
    
    # Tours may be different (not always, but usually)
    # Just check they're valid
    assert len(set(tour1)) == 10
    assert len(set(tour2)) == 10
