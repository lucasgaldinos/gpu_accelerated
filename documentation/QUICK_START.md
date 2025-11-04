# Quick Start Guide

## Installation

### Basic Installation (CPU only)

```bash
cd gpu_accelerated
pip install numpy
```

### Full Installation (with GPU support)

```bash
cd gpu_accelerated
pip install numpy cupy-cuda12x
```

## Basic Usage

### 1. Solve a Simple TSP

```python
import numpy as np
from src.protocols import ProblemContext
from src.algorithms import NearestNeighborCPU

# Define problem coordinates
coords = np.array([
    [0, 0],    # City 0
    [1, 0],    # City 1
    [1, 1],    # City 2
    [0, 1],    # City 3
])

# Create problem context
context = ProblemContext(coordinates=coords)

# Solve with Nearest Neighbor
solver = NearestNeighborCPU()
tour = solver.solve(context)
cost = solver.get_solution_cost(context, tour)

print(f"Tour: {tour}")
print(f"Cost: {cost:.2f}")
```

### 2. Compare Multiple Strategies

```python
from src.algorithms import (
    NearestNeighborCPU,
    RandomInsertionCPU,
    CheapestInsertionCPU,
)

# Define problem
coords = np.random.rand(20, 2) * 100
context = ProblemContext(coordinates=coords)

# Try different strategies
strategies = {
    'Nearest Neighbor': NearestNeighborCPU(),
    'Random Insertion': RandomInsertionCPU(seed=42),
    'Cheapest Insertion': CheapestInsertionCPU(),
}

results = {}
for name, strategy in strategies.items():
    tour = strategy.solve(context)
    cost = strategy.get_solution_cost(context, tour)
    results[name] = cost
    print(f"{name:20s}: {cost:.2f}")

best = min(results, key=results.get)
print(f"\nBest: {best} with cost {results[best]:.2f}")
```

### 3. Use Compositional Solver

```python
from src.algorithms import CompositionalTSPSolver

# Combine construction + improvement
constructor = CheapestInsertionCPU()
solver = CompositionalTSPSolver(constructor)

# Get detailed statistics
stats = solver.solve_with_stats(context)

print(f"Constructor: {stats['constructor']}")
print(f"Initial Cost: {stats['initial_cost']:.2f}")
print(f"Final Cost: {stats['final_cost']:.2f}")
```

### 4. GPU Acceleration (if available)

```python
from src.protocols import CUPY_AVAILABLE

if CUPY_AVAILABLE:
    from src.algorithms import TwoOptGPU
    
    # Create initial solution
    constructor = NearestNeighborCPU()
    initial_tour = constructor.solve(context)
    
    # Improve with GPU
    improver = TwoOptGPU(max_iterations=100)
    improved_tour = improver.improve(context, initial_tour)
    
    initial_cost = constructor.get_solution_cost(context, initial_tour)
    final_cost = improver.get_solution_cost(context, improved_tour)
    
    print(f"Initial: {initial_cost:.2f}")
    print(f"Improved: {final_cost:.2f}")
    print(f"Gain: {((initial_cost - final_cost) / initial_cost * 100):.1f}%")
else:
    print("CuPy not available. Install with: pip install cupy-cuda12x")
```

## Common Patterns

### Create VRP Problem with Demands

```python
coords = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
demands = np.array([0, 10, 15, 20])  # Depot has 0 demand
capacity = 30

context = ProblemContext(
    coordinates=coords,
    demands=demands,
    capacity=capacity
)

print(f"Has capacity constraints: {context.has_capacity_constraints()}")
```

### Benchmark Strategies

```python
import time

def benchmark(strategy, context, name):
    start = time.time()
    tour = strategy.solve(context)
    elapsed = time.time() - start
    cost = strategy.get_solution_cost(context, tour)
    return {
        'name': name,
        'cost': cost,
        'time': elapsed,
        'tour_length': len(tour),
    }

# Generate random problem
np.random.seed(42)
coords = np.random.rand(100, 2) * 1000
context = ProblemContext(coordinates=coords)

# Benchmark
strategies = [
    (NearestNeighborCPU(), 'Nearest Neighbor'),
    (RandomInsertionCPU(seed=42), 'Random Insertion'),
    (CheapestInsertionCPU(), 'Cheapest Insertion'),
]

results = [benchmark(s, context, n) for s, n in strategies]

print("\nBenchmark Results:")
print(f"{'Strategy':<20} {'Cost':>10} {'Time (s)':>10}")
print("-" * 42)
for r in sorted(results, key=lambda x: x['cost']):
    print(f"{r['name']:<20} {r['cost']:>10.2f} {r['time']:>10.4f}")
```

### Reuse Distance Matrix Across Solvers

```python
# The distance matrix is automatically cached in ProblemContext
context = ProblemContext(coordinates=coords)

# First solver triggers computation
solver1 = NearestNeighborCPU()
tour1 = solver1.solve(context)  # Distance matrix computed here

# Subsequent solvers reuse cached matrix
solver2 = CheapestInsertionCPU()
tour2 = solver2.solve(context)  # Uses cached matrix (no recomputation!)

solver3 = RandomInsertionCPU()
tour3 = solver3.solve(context)  # Also uses cached matrix

# Verify caching
print(f"Distance matrix cached: {context.distance_matrix_cpu is not None}")
```

## Running Tests

### With pytest (recommended)

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest code/tests/

# Run with coverage
pytest code/tests/ --cov=code/src --cov-report=html

# Run specific test file
pytest code/tests/unit/test_cpu_algorithms.py -v
```

### With simple test runner

```bash
# No dependencies needed
python3 test_runner.py
```

## Next Steps

1. Read [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed documentation
2. Explore example algorithms in `code/src/algorithms/`
3. Check integration tests for advanced usage patterns
4. Experiment with your own strategies implementing the protocols

## Troubleshooting

**ModuleNotFoundError: No module named 'src'**

Make sure you're in the repository root directory:
```bash
cd /path/to/gpu_accelerated
python3 -c "from src.protocols import ProblemContext"
```

Or add the code directory to your Python path:
```python
import sys
sys.path.insert(0, '/path/to/gpu_accelerated/code')
from src.protocols import ProblemContext
```

**ImportError: No module named 'cupy'**

GPU features require CuPy. Install it:
```bash
pip install cupy-cuda12x  # For CUDA 12.x
# or
pip install cupy-cuda11x  # For CUDA 11.x
```

Or continue using CPU-only features:
```python
from src.protocols import CUPY_AVAILABLE
if not CUPY_AVAILABLE:
    print("Using CPU-only mode")
```

**Tests fail with numpy errors**

Make sure numpy is installed:
```bash
pip install numpy
python3 -c "import numpy; print(numpy.__version__)"
```
