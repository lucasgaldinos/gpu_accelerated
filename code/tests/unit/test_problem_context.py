"""
Unit tests for ProblemContext.
"""

import numpy as np
import pytest

from src.utils.problem_context import ProblemContext


def test_problem_context_creation():
    """Test basic ProblemContext creation."""
    coords = np.array([[0, 0], [1, 1], [2, 0]])
    context = ProblemContext(coordinates=coords)
    
    assert context.n_nodes == 3
    assert context.coordinates.shape == (3, 2)


def test_distance_matrix_computation():
    """Test distance matrix is computed correctly."""
    # Simple 3-node problem
    coords = np.array([[0, 0], [1, 0], [0, 1]], dtype=np.float64)
    context = ProblemContext(coordinates=coords)
    
    dist_matrix = context.distance_matrix
    
    # Check shape
    assert dist_matrix.shape == (3, 3)
    
    # Check symmetry
    assert np.allclose(dist_matrix, dist_matrix.T)
    
    # Check diagonal is zero
    assert np.allclose(np.diag(dist_matrix), 0.0)
    
    # Check known distances
    assert np.isclose(dist_matrix[0, 1], 1.0)  # Distance (0,0) to (1,0)
    assert np.isclose(dist_matrix[0, 2], 1.0)  # Distance (0,0) to (0,1)
    assert np.isclose(dist_matrix[1, 2], np.sqrt(2))  # Distance (1,0) to (0,1)


def test_distance_matrix_caching():
    """Test that distance matrix is cached and not recomputed."""
    coords = np.array([[0, 0], [1, 1], [2, 0]])
    context = ProblemContext(coordinates=coords)
    
    # First access computes the matrix
    dist_matrix1 = context.distance_matrix
    
    # Second access should return the same object (cached)
    dist_matrix2 = context.distance_matrix
    
    assert dist_matrix1 is dist_matrix2


def test_tour_cost_computation():
    """Test tour cost computation."""
    coords = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float64)
    context = ProblemContext(coordinates=coords)
    
    # Square tour: 0->1->2->3->0
    tour = np.array([0, 1, 2, 3])
    cost = context.compute_tour_cost(tour)
    
    # Expected cost: 1 + 1 + 1 + 1 = 4
    assert np.isclose(cost, 4.0)


def test_tour_validation_valid():
    """Test validation of valid tours."""
    coords = np.array([[0, 0], [1, 1], [2, 0]])
    context = ProblemContext(coordinates=coords)
    
    tour = np.array([0, 1, 2])
    assert context.validate_tour(tour)
    
    tour = np.array([2, 0, 1])
    assert context.validate_tour(tour)


def test_tour_validation_invalid():
    """Test validation rejects invalid tours."""
    coords = np.array([[0, 0], [1, 1], [2, 0]])
    context = ProblemContext(coordinates=coords)
    
    # Too short
    tour = np.array([0, 1])
    assert not context.validate_tour(tour)
    
    # Duplicate node
    tour = np.array([0, 1, 1])
    assert not context.validate_tour(tour)
    
    # Invalid index
    tour = np.array([0, 1, 5])
    assert not context.validate_tour(tour)


def test_random_problem_creation():
    """Test creation of random problem instances."""
    context = ProblemContext.from_random(10, seed=42)
    
    assert context.n_nodes == 10
    assert context.coordinates.shape == (10, 2)
    
    # Test reproducibility
    context2 = ProblemContext.from_random(10, seed=42)
    assert np.allclose(context.coordinates, context2.coordinates)
