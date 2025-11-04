# Hybrid Metaheuristics Architecture

## Overview

This implementation provides a modular, composable architecture for solving TSP/VRP problems using hybrid metaheuristics. The design follows a "Lego brick" pattern where different optimization strategies can be combined flexibly.

## Architecture Features

### 1. Modular Strategy Design

The architecture defines clear protocol interfaces for different types of strategies:

- **ConstructiveStrategy**: Builds solutions from scratch (e.g., Nearest Neighbor)
- **ImprovementStrategy**: Enhances existing solutions (e.g., 2-Opt)
- **MetaheuristicStrategy**: Performs guided search (e.g., SA, GA)

### 2. Centralized Data Management

The `ProblemContext` class addresses the anti-pattern of recomputing distance matrices by:
- Computing the distance matrix once on first access
- Caching the matrix for all subsequent uses
- Providing utilities for tour cost calculation and validation

### 3. Composable Solver Framework

The `ComposableSolver` allows strategies to be chained together:

```python
solver = ComposableSolver(context)

strategies = [
    (NearestNeighborStrategy(), {'start_node': 0}),
    (TwoOptStrategy(), {'max_iterations': 100}),
    (SimulatedAnnealingStrategy(), {'max_iterations': 1000}),
]

solution, cost, metrics = solver.solve(strategies)
```

### 4. Fluent Interface

The `StrategyChain` provides a builder pattern for readable composition:

```python
chain = (StrategyChain()
    .construct_with(nearest_neighbor, start_node=0)
    .improve_with(two_opt, max_iterations=100)
    .optimize_with(simulated_annealing, max_iterations=1000)
)
```

## Implemented Strategies

### 1. Nearest Neighbor (Constructive)
- **CPU-optimized** implementation
- Avoids GPU kernel anti-pattern by using vectorized NumPy operations
- Deterministic greedy construction

### 2. 2-Opt (Improvement)
- Local search improvement heuristic
- Removes crossing edges
- Iterative refinement

### 3. Simulated Annealing (Metaheuristic)
- Temperature-based acceptance probability
- Escapes local optima
- Configurable cooling schedule

### 4. Genetic Algorithm (Metaheuristic)
- Population-based search
- Order crossover (OX) operator
- Swap mutation
- Tournament selection

## Performance Anti-Pattern Avoidance

### Problem: Excessive GPU Kernel Launches

**Anti-pattern identified**: Sequential algorithms (like Nearest Neighbor) using GPU operations in Python loops cause excessive kernel launches, degrading performance.

**Solution implemented**:
- Sequential algorithms use CPU/NumPy backend
- Distance matrix computed once and cached
- Vectorized operations where possible
- Clear separation of CPU and GPU strategies

## Usage Examples

### Basic Usage

```python
from src.algorithms import NearestNeighborStrategy, TwoOptStrategy, ComposableSolver
from src.utils import ProblemContext

# Create problem
context = ProblemContext.from_random(n_nodes=50, seed=42)

# Create solver
solver = ComposableSolver(context)

# Define strategy chain
nn = NearestNeighborStrategy()
two_opt = TwoOptStrategy()

strategies = [
    (nn, {'start_node': 0}),
    (two_opt, {'max_iterations': 100}),
]

# Solve
solution, cost, metrics = solver.solve(strategies, verbose=True)
```

### Hybrid Metaheuristic

```python
# Four-stage hybrid
strategies = [
    (NearestNeighborStrategy(), {'start_node': 0}),
    (TwoOptStrategy(), {'max_iterations': 100}),
    (SimulatedAnnealingStrategy(seed=42), {'max_iterations': 1000}),
    (GeneticAlgorithmStrategy(seed=42), {'max_iterations': 50}),
]

solution, cost, metrics = solver.solve(strategies)
```

### Benchmarking

```python
stats = solver.benchmark_strategies(strategies, n_runs=10, verbose=False)

print(f"Mean cost: {stats['mean_cost']:.2f} ± {stats['std_cost']:.2f}")
print(f"Mean time: {stats['mean_time']:.3f}s")
```

## Testing

Comprehensive test suite includes:

- **Unit tests**: Individual strategy components
- **Integration tests**: Strategy composition and hybrid algorithms
- **Benchmark tests**: Performance validation

Run tests:

```bash
cd code
python -m pytest tests/ -v
```

## Design Decisions

### Why This Architecture?

1. **Modularity**: Each strategy is independent and reusable
2. **Flexibility**: Strategies can be combined in any order
3. **Performance**: Avoids known anti-patterns
4. **Testability**: Each component can be tested in isolation
5. **Extensibility**: New strategies can be added without modifying existing code

### Backend Strategy

- **CPU/NumPy**: Sequential algorithms (NN, SA)
- **GPU/CuPy**: Parallel algorithms (future work)
- **JIT/Numba**: Optimized CPU algorithms (future work)

Each backend is appropriate for its algorithm type, avoiding the anti-pattern of forcing GPU acceleration on inherently sequential algorithms.

## Future Enhancements

1. Add GPU-accelerated strategies for parallel operations
2. Implement Ant Colony Optimization (ACO)
3. Add multi-objective optimization support
4. Implement parallel strategy evaluation
5. Add adaptive parameter tuning

## References

- Problem statement analysis and flaws.md critique
- Actor-critic architecture evaluation
- Hybrid metaheuristics research literature
