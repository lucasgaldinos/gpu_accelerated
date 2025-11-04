# GPU-Accelerated TSP/VRP Architecture Documentation

## Overview

This document describes the modular "Lego brick" architecture for GPU-accelerated optimization algorithms. The architecture emphasizes:

- **Separation of concerns**: CPU and GPU algorithms are clearly separated
- **Data centralization**: ProblemContext holds all problem data and caches computations
- **Composability**: Different strategies can be combined to create complete solvers
- **Performance**: Distance matrices are computed once and reused

## Core Components

### 1. ProblemContext

The `ProblemContext` class is the central data holder that all strategies operate on.

```python
from src.protocols import ProblemContext

# Create a problem context from coordinates
coords = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
context = ProblemContext(coordinates=coords)

# The context automatically computes and caches distance matrices
distances_cpu = context.compute_distance_matrix_cpu()  # Computed once
distances_cpu2 = context.compute_distance_matrix_cpu() # Returns cached version

# GPU distance matrix (if CuPy available)
distances_gpu = context.compute_distance_matrix_gpu()
```

**Key Features:**
- Validates input data on initialization
- Caches distance matrices to avoid redundant computation
- Supports both TSP and CVRP (with demands and capacity)
- Provides factory methods for easy instantiation

### 2. Strategy Protocols

Protocols define the interface that all strategies must implement:

- **CPUStrategy**: For CPU-based algorithms using NumPy
- **GPUStrategy**: For GPU-based algorithms using CuPy
- **ImprovementStrategy**: For algorithms that refine existing solutions
- **ComposableStrategy**: For strategies that can be composed together

```python
from src.protocols import CPUStrategy, GPUStrategy

class MyCustomCPUStrategy:
    def solve(self, context: ProblemContext) -> np.ndarray:
        # Your algorithm here
        pass
    
    def get_solution_cost(self, context: ProblemContext, solution: np.ndarray) -> float:
        # Cost calculation here
        pass
```

### 3. Algorithm Strategies ("Lego Bricks")

The architecture provides multiple algorithm strategies that can be used independently or combined:

#### CPU Strategies

**NearestNeighborCPU**
```python
from src.algorithms import NearestNeighborCPU

solver = NearestNeighborCPU(start_node=0)
tour = solver.solve(context)
cost = solver.get_solution_cost(context, tour)
```

**RandomInsertionCPU**
```python
from src.algorithms import RandomInsertionCPU

solver = RandomInsertionCPU(seed=42)  # Reproducible with seed
tour = solver.solve(context)
```

**CheapestInsertionCPU**
```python
from src.algorithms import CheapestInsertionCPU

solver = CheapestInsertionCPU()
tour = solver.solve(context)
```

#### GPU Strategies

**TwoOptGPU**
```python
from src.algorithms import TwoOptGPU

# Requires CuPy
optimizer = TwoOptGPU(max_iterations=100)

# Improve an existing tour
improved_tour = optimizer.improve(context, initial_tour)

# Or solve from scratch (creates initial tour first)
tour = optimizer.solve(context)
```

### 4. Compositional Solver ("Lego Blocks")

Combine multiple strategies to create complete solvers:

```python
from src.algorithms import CompositionalTSPSolver, NearestNeighborCPU, TwoOptGPU

# Construction + Improvement
constructor = NearestNeighborCPU()
improver = TwoOptGPU(max_iterations=50)

solver = CompositionalTSPSolver(constructor, improver)

# Get detailed statistics
stats = solver.solve_with_stats(context)
print(f"Initial cost: {stats['initial_cost']:.2f}")
print(f"Final cost: {stats['final_cost']:.2f}")
print(f"Improvement: {stats['improvement_percent']:.1f}%")
```

## Architecture Benefits

### 1. No Redundant Computation

The old architecture had a critical flaw: sequential algorithms would recompute the distance matrix multiple times, often causing GPU overhead when called in Python loops.

**Old (Anti-pattern):**
```python
# BAD: Distance matrix computed in every iteration
for i in range(n):
    distances = compute_distance_matrix(coords, xp)  # Recomputed!
    nearest = find_nearest(distances, current)
```

**New (Efficient):**
```python
# GOOD: Distance matrix computed once and cached
context = ProblemContext(coordinates=coords)
solver = NearestNeighborCPU()
tour = solver.solve(context)  # Uses cached distance matrix
```

### 2. Clear Backend Separation

No more passing `xp` (NumPy or CuPy) as a parameter. Backend is enforced at the class level:

- `NearestNeighborCPU` always uses NumPy
- `TwoOptGPU` always uses CuPy

This eliminates the possibility of accidentally using the wrong backend.

### 3. Modular "Lego Brick" Design

Different strategies can be easily swapped and combined:

```python
# Try different construction strategies
strategies = [
    NearestNeighborCPU(),
    RandomInsertionCPU(seed=42),
    CheapestInsertionCPU(),
]

results = []
for strategy in strategies:
    tour = strategy.solve(context)
    cost = strategy.get_solution_cost(context, tour)
    results.append((strategy, cost))

# Pick the best
best_strategy, best_cost = min(results, key=lambda x: x[1])
```

### 4. Easy Benchmarking

Compare algorithms on the same problem:

```python
import time

def benchmark_strategy(strategy, context):
    start = time.time()
    tour = strategy.solve(context)
    elapsed = time.time() - start
    cost = strategy.get_solution_cost(context, tour)
    return {
        'strategy': str(strategy),
        'time': elapsed,
        'cost': cost,
    }

strategies = [NearestNeighborCPU(), RandomInsertionCPU(), CheapestInsertionCPU()]
benchmarks = [benchmark_strategy(s, context) for s in strategies]

for b in sorted(benchmarks, key=lambda x: x['cost']):
    print(f"{b['strategy']:30s} - Cost: {b['cost']:.2f}, Time: {b['time']:.4f}s")
```

## Testing

The architecture includes comprehensive tests:

```bash
# Run all tests (requires pytest and numpy)
pytest code/tests/

# Run specific test suites
pytest code/tests/unit/test_problem_context.py
pytest code/tests/unit/test_cpu_algorithms.py
pytest code/tests/integration/test_lego_architecture.py
```

Test coverage includes:
- ProblemContext validation and caching
- Each algorithm strategy
- Compositional solver patterns
- "Lego brick" modularity
- Distance matrix computation and reuse

## Example: Complete Workflow

```python
import numpy as np
from src.protocols import ProblemContext
from src.algorithms import (
    NearestNeighborCPU,
    CheapestInsertionCPU,
    CompositionalTSPSolver,
)

# 1. Create problem
coords = np.random.rand(50, 2) * 100
context = ProblemContext(coordinates=coords)

# 2. Try simple construction strategies
nn_solver = NearestNeighborCPU()
nn_tour = nn_solver.solve(context)
nn_cost = nn_solver.get_solution_cost(context, nn_tour)
print(f"Nearest Neighbor: {nn_cost:.2f}")

ci_solver = CheapestInsertionCPU()
ci_tour = ci_solver.solve(context)
ci_cost = ci_solver.get_solution_cost(context, ci_tour)
print(f"Cheapest Insertion: {ci_cost:.2f}")

# 3. Try compositional approach (if GPU available)
try:
    from src.algorithms import TwoOptGPU
    
    constructor = CheapestInsertionCPU()
    improver = TwoOptGPU(max_iterations=100)
    solver = CompositionalTSPSolver(constructor, improver)
    
    stats = solver.solve_with_stats(context)
    print(f"\nCompositional Solver:")
    print(f"  Initial: {stats['initial_cost']:.2f}")
    print(f"  Final:   {stats['final_cost']:.2f}")
    print(f"  Improvement: {stats['improvement_percent']:.1f}%")
except ImportError:
    print("CuPy not available, skipping GPU improvement")

# 4. Note: Distance matrix was computed only ONCE
# and reused across all solvers!
print(f"\nDistance matrix computed once: {context.distance_matrix_cpu is not None}")
```

## Design Principles

1. **Single Responsibility**: Each class has one clear purpose
2. **Open/Closed**: Easy to add new strategies without modifying existing code
3. **Dependency Inversion**: Strategies depend on ProblemContext abstraction
4. **Interface Segregation**: Separate protocols for CPU, GPU, and composition
5. **Composition over Inheritance**: Strategies are composed, not inherited

## Future Extensions

The architecture is designed to easily support:

- Additional construction heuristics (Savings, Sweep, etc.)
- More improvement algorithms (3-opt, Lin-Kernighan, etc.)
- Hybrid CPU/GPU algorithms
- Multi-objective optimization
- Constraint handling for VRP variants
- Parallel strategy execution
- Custom distance metrics

## Performance Considerations

### CPU vs GPU

- **Use CPU strategies** for:
  - Small problems (< 1000 nodes)
  - Sequential algorithms with many Python loops
  - When GPU is not available

- **Use GPU strategies** for:
  - Large problems (> 1000 nodes)
  - Algorithms with parallelizable operations
  - Improvement phases with many iterations

### Memory Management

- Distance matrices are O(n²) in memory
- For very large problems, consider:
  - On-the-fly distance calculation
  - Sparse matrix representations
  - Chunked processing

### Caching Strategy

- Distance matrices are cached by default
- Use `force=True` to recompute if coordinates change
- GPU and CPU caches are independent

## Troubleshooting

**CuPy not available:**
```python
from src.protocols import CUPY_AVAILABLE

if not CUPY_AVAILABLE:
    print("CuPy not installed. Install with: pip install cupy-cuda12x")
```

**Import errors:**
Make sure you're running from the repository root:
```bash
cd /path/to/gpu_accelerated
python3 -c "from src.protocols import ProblemContext"
```

**Distance matrix not cached:**
Check that you're using the same ProblemContext instance across solvers.
