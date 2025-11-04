"""
ProblemContext: Centralized data holder for TSP/VRP problem instances.

This class serves as the central data structure that strategies operate on,
following the "Lego brick" architectural pattern. It holds all problem data
and computed artifacts (like distance matrices) to avoid redundant computation.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False


@dataclass
class ProblemContext:
    """
    Centralized problem data holder for routing optimization problems.
    
    This class holds all problem-specific data and computed artifacts,
    allowing strategies to access what they need without redundant computation.
    
    Attributes:
        coordinates: Node coordinates as numpy array (n_nodes, 2)
        demands: Node demands for VRP (optional)
        capacity: Vehicle capacity for VRP (optional)
        distance_matrix_cpu: Precomputed distance matrix on CPU
        distance_matrix_gpu: Precomputed distance matrix on GPU (if available)
        n_nodes: Number of nodes in the problem
    """
    
    coordinates: np.ndarray
    demands: Optional[np.ndarray] = None
    capacity: Optional[float] = None
    distance_matrix_cpu: Optional[np.ndarray] = None
    distance_matrix_gpu: Optional = None  # CuPy array if available
    
    def __post_init__(self):
        """Validate and initialize the problem context."""
        if self.coordinates is None or len(self.coordinates) == 0:
            raise ValueError("Coordinates must be provided and non-empty")
        
        # Ensure coordinates is a numpy array
        if not isinstance(self.coordinates, np.ndarray):
            self.coordinates = np.asarray(self.coordinates)
        
        # Validate shape
        if self.coordinates.ndim != 2 or self.coordinates.shape[1] != 2:
            raise ValueError("Coordinates must be a 2D array with shape (n_nodes, 2)")
        
        # Validate demands if provided
        if self.demands is not None:
            if not isinstance(self.demands, np.ndarray):
                self.demands = np.asarray(self.demands)
            if len(self.demands) != len(self.coordinates):
                raise ValueError("Demands length must match number of nodes")
    
    @property
    def n_nodes(self) -> int:
        """Return the number of nodes in the problem."""
        return len(self.coordinates)
    
    def compute_distance_matrix_cpu(self, force: bool = False) -> np.ndarray:
        """
        Compute or retrieve the distance matrix on CPU.
        
        Args:
            force: If True, recompute even if already cached
            
        Returns:
            Distance matrix as numpy array (n_nodes, n_nodes)
        """
        if self.distance_matrix_cpu is None or force:
            # Compute Euclidean distance matrix
            coords = self.coordinates
            diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
            self.distance_matrix_cpu = np.sqrt(np.sum(diff ** 2, axis=2))
        
        return self.distance_matrix_cpu
    
    def compute_distance_matrix_gpu(self, force: bool = False):
        """
        Compute or retrieve the distance matrix on GPU.
        
        Args:
            force: If True, recompute even if already cached
            
        Returns:
            Distance matrix as CuPy array (n_nodes, n_nodes)
            
        Raises:
            RuntimeError: If CuPy is not available
        """
        if not CUPY_AVAILABLE:
            raise RuntimeError("CuPy is not available. Cannot compute GPU distance matrix.")
        
        if self.distance_matrix_gpu is None or force:
            # Transfer coordinates to GPU and compute distance matrix
            coords_gpu = cp.asarray(self.coordinates)
            diff = coords_gpu[:, cp.newaxis, :] - coords_gpu[cp.newaxis, :, :]
            self.distance_matrix_gpu = cp.sqrt(cp.sum(diff ** 2, axis=2))
        
        return self.distance_matrix_gpu
    
    def has_capacity_constraints(self) -> bool:
        """Check if this is a capacitated VRP problem."""
        return self.demands is not None and self.capacity is not None
    
    @classmethod
    def from_coordinates(cls, coordinates: np.ndarray, **kwargs) -> "ProblemContext":
        """
        Create a ProblemContext from coordinates.
        
        Args:
            coordinates: Node coordinates
            **kwargs: Additional arguments (demands, capacity)
            
        Returns:
            ProblemContext instance
        """
        return cls(coordinates=coordinates, **kwargs)
    
    @classmethod
    def from_tsplib_problem(cls, problem) -> "ProblemContext":
        """
        Create a ProblemContext from a TSPLIB problem instance.
        
        Args:
            problem: TSPLIB problem object with node_coords attribute
            
        Returns:
            ProblemContext instance
        """
        # Extract coordinates from TSPLIB problem - iterate over dict items for efficiency
        # Sort by node index to ensure correct order
        coordinates = np.array([
            coords for _, coords in sorted(problem.node_coords.items())
        ])
        
        # Extract demands and capacity if available
        demands = None
        capacity = None
        
        if hasattr(problem, 'demands') and problem.demands:
            # Extract demands in the same order as coordinates
            demands = np.array([
                problem.demands.get(node_id, 0) 
                for node_id in sorted(problem.node_coords.keys())
            ])
        
        if hasattr(problem, 'capacity'):
            capacity = problem.capacity
        
        return cls(coordinates=coordinates, demands=demands, capacity=capacity)
