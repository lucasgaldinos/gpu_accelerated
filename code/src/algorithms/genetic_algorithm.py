"""
Genetic Algorithm Metaheuristic.

This strategy uses evolutionary principles (selection, crossover, mutation)
to evolve a population of solutions toward better fitness.
"""

import numpy as np
from numpy.typing import NDArray
from typing import Optional


class GeneticAlgorithmStrategy:
    """
    Genetic Algorithm metaheuristic for TSP.
    
    Uses population-based search with crossover and mutation operators
    to explore the solution space.
    """
    
    def __init__(
        self,
        population_size: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        backend: str = "cpu",
        seed: Optional[int] = None
    ):
        """
        Initialize the strategy.
        
        Args:
            population_size: Number of individuals in population
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            backend: Computational backend
            seed: Random seed for reproducibility
        """
        self._backend = backend
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.rng = np.random.default_rng(seed)
    
    @property
    def name(self) -> str:
        return "GeneticAlgorithm"
    
    @property
    def backend(self) -> str:
        return self._backend
    
    def search(
        self,
        initial_solution: NDArray[np.int_],
        distance_matrix: NDArray[np.float64],
        max_iterations: int = 1000,
        **kwargs
    ) -> tuple[NDArray[np.int_], float]:
        """
        Perform genetic algorithm search.
        
        Args:
            initial_solution: Starting tour (used as template)
            distance_matrix: Precomputed distance matrix
            max_iterations: Maximum number of generations
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (best_solution, best_cost)
        """
        n_nodes = len(initial_solution)
        
        # Initialize population
        population = self._initialize_population(n_nodes)
        
        # Evaluate initial population
        fitness = np.array([
            self._calculate_cost(individual, distance_matrix)
            for individual in population
        ])
        
        best_idx = np.argmin(fitness)
        best_solution = population[best_idx].copy()
        best_cost = fitness[best_idx]
        
        # Evolution loop
        for generation in range(max_iterations):
            # Selection
            parents = self._tournament_selection(population, fitness)
            
            # Create next generation
            next_population = []
            
            for i in range(0, self.population_size, 2):
                parent1 = parents[i]
                parent2 = parents[(i + 1) % self.population_size]
                
                # Crossover
                if self.rng.random() < self.crossover_rate:
                    child1, child2 = self._order_crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutation
                if self.rng.random() < self.mutation_rate:
                    child1 = self._swap_mutation(child1)
                if self.rng.random() < self.mutation_rate:
                    child2 = self._swap_mutation(child2)
                
                next_population.extend([child1, child2])
            
            population = np.array(next_population[:self.population_size])
            
            # Evaluate new population
            fitness = np.array([
                self._calculate_cost(individual, distance_matrix)
                for individual in population
            ])
            
            # Update best solution
            current_best_idx = np.argmin(fitness)
            if fitness[current_best_idx] < best_cost:
                best_solution = population[current_best_idx].copy()
                best_cost = fitness[current_best_idx]
        
        return best_solution, best_cost
    
    def _initialize_population(self, n_nodes: int) -> list[NDArray[np.int_]]:
        """
        Initialize a random population.
        
        Args:
            n_nodes: Number of nodes in the problem
            
        Returns:
            List of random tour permutations
        """
        population = []
        for _ in range(self.population_size):
            tour = np.arange(n_nodes)
            self.rng.shuffle(tour)
            population.append(tour)
        return population
    
    def _tournament_selection(
        self,
        population: list[NDArray[np.int_]],
        fitness: NDArray[np.float64],
        tournament_size: int = 3
    ) -> list[NDArray[np.int_]]:
        """
        Select parents using tournament selection.
        
        Args:
            population: Current population
            fitness: Fitness values
            tournament_size: Number of individuals per tournament
            
        Returns:
            Selected parents
        """
        selected = []
        for _ in range(len(population)):
            # Random tournament
            tournament_idx = self.rng.integers(0, len(population), tournament_size)
            winner_idx = tournament_idx[np.argmin(fitness[tournament_idx])]
            selected.append(population[winner_idx].copy())
        return selected
    
    def _order_crossover(
        self,
        parent1: NDArray[np.int_],
        parent2: NDArray[np.int_]
    ) -> tuple[NDArray[np.int_], NDArray[np.int_]]:
        """
        Order crossover (OX) operator.
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Two offspring
        """
        n = len(parent1)
        
        # Select random crossover points
        cx_point1 = self.rng.integers(0, n)
        cx_point2 = self.rng.integers(cx_point1 + 1, n + 1)
        
        # Create offspring
        child1 = np.full(n, -1, dtype=np.int_)
        child2 = np.full(n, -1, dtype=np.int_)
        
        # Copy segment from parent
        child1[cx_point1:cx_point2] = parent1[cx_point1:cx_point2]
        child2[cx_point1:cx_point2] = parent2[cx_point1:cx_point2]
        
        # Fill remaining positions with order from other parent
        self._fill_offspring(child1, parent2, cx_point2)
        self._fill_offspring(child2, parent1, cx_point2)
        
        return child1, child2
    
    def _fill_offspring(
        self,
        child: NDArray[np.int_],
        parent: NDArray[np.int_],
        start_pos: int
    ):
        """Fill remaining positions in offspring maintaining order from parent."""
        n = len(child)
        child_pos = start_pos % n
        parent_pos = start_pos % n
        
        while -1 in child:
            if parent[parent_pos] not in child:
                child[child_pos] = parent[parent_pos]
                child_pos = (child_pos + 1) % n
            parent_pos = (parent_pos + 1) % n
    
    def _swap_mutation(self, individual: NDArray[np.int_]) -> NDArray[np.int_]:
        """
        Swap mutation operator.
        
        Args:
            individual: Individual to mutate
            
        Returns:
            Mutated individual
        """
        mutated = individual.copy()
        n = len(mutated)
        
        # Random swap
        i, j = self.rng.integers(0, n, 2)
        mutated[i], mutated[j] = mutated[j], mutated[i]
        
        return mutated
    
    def _calculate_cost(
        self,
        tour: NDArray[np.int_],
        distance_matrix: NDArray[np.float64]
    ) -> float:
        """Calculate the total cost of a tour."""
        cost = 0.0
        n = len(tour)
        for i in range(n):
            cost += distance_matrix[tour[i], tour[(i + 1) % n]]
        return cost
