"""
Greedy/Cheapest Insertion heuristic for TSP on CPU.

This is a constructive heuristic that builds a tour by always selecting
the node that can be inserted with minimum cost increase.
"""

import numpy as np
from ..protocols import ProblemContext, CPUStrategy


class CheapestInsertionCPU:
    """
    CPU-based Cheapest Insertion heuristic for TSP.
    
    This implementation builds a tour incrementally by always inserting
    the node that causes the smallest increase in tour length.
    
    Algorithm:
    1. Create initial tour with 3 nodes
    2. While there are uninserted nodes:
       - For each uninserted node, find its best insertion position
       - Select the node with the smallest insertion cost
       - Insert it at its best position
    3. Return the complete tour
    """
    
    def __init__(self):
        """Initialize the Cheapest Insertion strategy."""
        pass
    
    def solve(self, context: ProblemContext) -> np.ndarray:
        """
        Solve TSP using Cheapest Insertion heuristic on CPU.
        
        Args:
            context: ProblemContext with problem data
            
        Returns:
            Tour as numpy array of node indices
        """
        distances = context.compute_distance_matrix_cpu()
        n_nodes = context.n_nodes
        
        if n_nodes < 3:
            # For very small problems, just return all nodes
            return np.arange(n_nodes + 1)
        
        # Create initial tour with 3 nodes
        tour = self._create_initial_tour(distances, n_nodes)
        inserted = set(tour)
        
        # Insert remaining nodes one by one, always choosing the cheapest
        while len(inserted) < n_nodes:
            best_node = -1
            best_position = -1
            best_cost_increase = np.inf
            
            # Find the node and position with minimum cost increase
            for node in range(n_nodes):
                if node in inserted:
                    continue
                
                position, cost_increase = self._find_best_insertion(tour, node, distances)
                
                if cost_increase < best_cost_increase:
                    best_cost_increase = cost_increase
                    best_node = node
                    best_position = position
            
            # Insert the best node at its best position
            tour = np.insert(tour, best_position, best_node)
            inserted.add(best_node)
        
        # Close the tour
        tour_with_return = np.zeros(len(tour) + 1, dtype=np.int32)
        tour_with_return[:-1] = tour
        tour_with_return[-1] = tour[0]
        
        return tour_with_return
    
    def _create_initial_tour(self, distances: np.ndarray, n_nodes: int) -> np.ndarray:
        """
        Create initial 3-node tour.
        
        Args:
            distances: Distance matrix
            n_nodes: Number of nodes
            
        Returns:
            Initial tour as array of 3 node indices
        """
        # Start with node 0
        tour = [0]
        
        # Find furthest node from 0
        furthest_from_0 = np.argmax(distances[0])
        tour.append(furthest_from_0)
        
        # Find node furthest from both 0 and furthest_from_0
        min_dist_to_tour = np.minimum(distances[0], distances[furthest_from_0])
        furthest_from_tour = np.argmax(min_dist_to_tour)
        tour.append(furthest_from_tour)
        
        return np.array(tour, dtype=np.int32)
    
    def _find_best_insertion(self, tour: np.ndarray, node: int, 
                            distances: np.ndarray) -> tuple[int, float]:
        """
        Find the best position to insert a node and the cost increase.
        
        Args:
            tour: Current tour (without closing edge)
            node: Node to insert
            distances: Distance matrix
            
        Returns:
            Tuple of (best_position, cost_increase)
        """
        best_cost_increase = np.inf
        best_position = 0
        
        # Try inserting between each pair of consecutive nodes
        for i in range(len(tour)):
            # Cost of current edge
            if i < len(tour) - 1:
                current_edge_cost = distances[tour[i], tour[i + 1]]
            else:
                # Edge back to start
                current_edge_cost = distances[tour[i], tour[0]]
            
            # Cost of new edges
            next_node = tour[i + 1] if i < len(tour) - 1 else tour[0]
            new_edges_cost = distances[tour[i], node] + distances[node, next_node]
            
            # Cost increase
            cost_increase = new_edges_cost - current_edge_cost
            
            if cost_increase < best_cost_increase:
                best_cost_increase = cost_increase
                best_position = i + 1
        
        return best_position, best_cost_increase
    
    def get_solution_cost(self, context: ProblemContext, solution: np.ndarray) -> float:
        """
        Calculate the total cost of a tour.
        
        Args:
            context: ProblemContext with problem data
            solution: Tour as array of node indices
            
        Returns:
            Total tour distance
        """
        distances = context.compute_distance_matrix_cpu()
        
        total_cost = 0.0
        for i in range(len(solution) - 1):
            total_cost += distances[solution[i], solution[i + 1]]
        
        return total_cost
    
    def __repr__(self) -> str:
        return "CheapestInsertionCPU()"


if __name__ == "__main__":
    # Simple test
    coords = np.array([
        [0, 0],
        [1, 0],
        [1, 1],
        [0, 1],
        [0.5, 0.5],
        [2, 2],
    ])
    
    context = ProblemContext(coordinates=coords)
    solver = CheapestInsertionCPU()
    
    tour = solver.solve(context)
    cost = solver.get_solution_cost(context, tour)
    
    print(f"Tour: {tour}")
    print(f"Cost: {cost:.2f}")
