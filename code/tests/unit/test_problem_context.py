"""
Unit tests for ProblemContext.
"""

import pytest
import numpy as np
from src.protocols import ProblemContext, CUPY_AVAILABLE


class TestProblemContext:
    """Test suite for ProblemContext class."""
    
    def test_initialization_with_coordinates(self):
        """Test basic initialization with coordinates."""
        coords = np.array([[0, 0], [1, 1], [2, 2]])
        context = ProblemContext(coordinates=coords)
        
        assert context.n_nodes == 3
        assert np.array_equal(context.coordinates, coords)
        assert context.demands is None
        assert context.capacity is None
    
    def test_initialization_with_demands(self):
        """Test initialization with demands for VRP."""
        coords = np.array([[0, 0], [1, 1], [2, 2]])
        demands = np.array([0, 10, 20])
        capacity = 50
        
        context = ProblemContext(
            coordinates=coords,
            demands=demands,
            capacity=capacity
        )
        
        assert context.n_nodes == 3
        assert np.array_equal(context.demands, demands)
        assert context.capacity == capacity
        assert context.has_capacity_constraints()
    
    def test_initialization_with_list_coordinates(self):
        """Test initialization with list instead of numpy array."""
        coords = [[0, 0], [1, 1], [2, 2]]
        context = ProblemContext(coordinates=coords)
        
        assert isinstance(context.coordinates, np.ndarray)
        assert context.n_nodes == 3
    
    def test_invalid_coordinates_raises_error(self):
        """Test that invalid coordinates raise errors."""
        # Empty coordinates
        with pytest.raises(ValueError, match="must be provided and non-empty"):
            ProblemContext(coordinates=None)
        
        # Wrong shape
        with pytest.raises(ValueError, match="must be a 2D array"):
            ProblemContext(coordinates=np.array([1, 2, 3]))
        
        with pytest.raises(ValueError, match="shape \\(n_nodes, 2\\)"):
            ProblemContext(coordinates=np.array([[1], [2], [3]]))
    
    def test_invalid_demands_length(self):
        """Test that demands must match number of nodes."""
        coords = np.array([[0, 0], [1, 1], [2, 2]])
        demands = np.array([10, 20])  # Wrong length
        
        with pytest.raises(ValueError, match="Demands length must match"):
            ProblemContext(coordinates=coords, demands=demands)
    
    def test_compute_distance_matrix_cpu(self):
        """Test CPU distance matrix computation."""
        coords = np.array([[0, 0], [1, 0], [0, 1]])
        context = ProblemContext(coordinates=coords)
        
        distances = context.compute_distance_matrix_cpu()
        
        # Check shape
        assert distances.shape == (3, 3)
        
        # Check diagonal is zero
        assert np.allclose(np.diag(distances), 0)
        
        # Check symmetry
        assert np.allclose(distances, distances.T)
        
        # Check specific distances
        assert np.isclose(distances[0, 1], 1.0)  # Distance from [0,0] to [1,0]
        assert np.isclose(distances[0, 2], 1.0)  # Distance from [0,0] to [0,1]
        assert np.isclose(distances[1, 2], np.sqrt(2))  # Distance from [1,0] to [0,1]
    
    def test_distance_matrix_caching(self):
        """Test that distance matrix is cached after first computation."""
        coords = np.array([[0, 0], [1, 0], [0, 1]])
        context = ProblemContext(coordinates=coords)
        
        # First computation
        distances1 = context.compute_distance_matrix_cpu()
        
        # Second call should return cached value
        distances2 = context.compute_distance_matrix_cpu()
        
        # Should be the same object (not just equal values)
        assert distances1 is distances2
    
    def test_distance_matrix_force_recompute(self):
        """Test force recomputation of distance matrix."""
        coords = np.array([[0, 0], [1, 0], [0, 1]])
        context = ProblemContext(coordinates=coords)
        
        distances1 = context.compute_distance_matrix_cpu()
        distances2 = context.compute_distance_matrix_cpu(force=True)
        
        # Values should be equal but objects different
        assert np.array_equal(distances1, distances2)
        assert distances1 is not distances2
    
    @pytest.mark.skipif(not CUPY_AVAILABLE, reason="CuPy not available")
    def test_compute_distance_matrix_gpu(self):
        """Test GPU distance matrix computation."""
        import cupy as cp
        
        coords = np.array([[0, 0], [1, 0], [0, 1]])
        context = ProblemContext(coordinates=coords)
        
        distances_gpu = context.compute_distance_matrix_gpu()
        
        # Check it's a CuPy array
        assert isinstance(distances_gpu, cp.ndarray)
        
        # Check shape
        assert distances_gpu.shape == (3, 3)
        
        # Compare with CPU version
        distances_cpu = context.compute_distance_matrix_cpu()
        assert np.allclose(cp.asnumpy(distances_gpu), distances_cpu)
    
    def test_compute_distance_matrix_gpu_without_cupy(self):
        """Test that GPU distance matrix raises error without CuPy."""
        if CUPY_AVAILABLE:
            pytest.skip("CuPy is available")
        
        coords = np.array([[0, 0], [1, 0], [0, 1]])
        context = ProblemContext(coordinates=coords)
        
        with pytest.raises(RuntimeError, match="CuPy is not available"):
            context.compute_distance_matrix_gpu()
    
    def test_from_coordinates_factory(self):
        """Test factory method from_coordinates."""
        coords = np.array([[0, 0], [1, 1]])
        context = ProblemContext.from_coordinates(coords)
        
        assert context.n_nodes == 2
        assert np.array_equal(context.coordinates, coords)
    
    def test_has_capacity_constraints(self):
        """Test capacity constraints detection."""
        coords = np.array([[0, 0], [1, 1]])
        
        # Without demands/capacity
        context1 = ProblemContext(coordinates=coords)
        assert not context1.has_capacity_constraints()
        
        # With demands but no capacity
        context2 = ProblemContext(coordinates=coords, demands=np.array([10, 20]))
        assert not context2.has_capacity_constraints()
        
        # With capacity but no demands
        context3 = ProblemContext(coordinates=coords, capacity=50)
        assert not context3.has_capacity_constraints()
        
        # With both
        context4 = ProblemContext(
            coordinates=coords,
            demands=np.array([10, 20]),
            capacity=50
        )
        assert context4.has_capacity_constraints()
