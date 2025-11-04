# GPU-Accelerated Optimization - Code

## Quick Start

### Installation

```bash
# Install core dependencies
pip install numpy

# Install development dependencies (for testing)
pip install pytest pytest-cov

# Optional: GPU support
pip install cupy

# Optional: JIT compilation
pip install numba
```

### Basic Usage

```python
from src.algorithms import (
    NearestNeighborStrategy,
    TwoOptStrategy,
    SimulatedAnnealingStrategy,
    GeneticAlgorithmStrategy,
    ComposableSolver,
)
from src.utils import ProblemContext

# Create a problem
context = ProblemContext.from_random(n_nodes=20, seed=42)

# Create solver
solver = ComposableSolver(context)

# Define optimization strategy chain
strategies = [
    (NearestNeighborStrategy(), {'start_node': 0}),
    (TwoOptStrategy(), {'max_iterations': 100}),
    (SimulatedAnnealingStrategy(seed=42), {'max_iterations': 1000}),
]

# Solve
solution, cost, metrics = solver.solve(strategies, verbose=True)

print(f"Best solution cost: {cost:.2f}")
print(f"Total time: {metrics['total_time']:.3f}s")
```

### Running the Demo

```bash
cd code
python demo_hybrid_metaheuristics.py
```

### Running Tests

```bash
cd code
python -m pytest tests/ -v
```

## Project Structure

```
code/
├── src/                          # Source code
│   ├── algorithms/               # Optimization algorithms
│   │   ├── nearest_neighbor.py   # Constructive heuristic
│   │   ├── two_opt.py            # Improvement heuristic
│   │   ├── simulated_annealing.py # SA metaheuristic
│   │   ├── genetic_algorithm.py  # GA metaheuristic
│   │   └── composable_solver.py  # Composition framework
│   ├── protocols/                # Type protocols
│   │   └── strategy.py           # Strategy interfaces
│   └── utils/                    # Utilities
│       └── problem_context.py    # Problem data management
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
├── ARCHITECTURE.md               # Architecture documentation
└── demo_hybrid_metaheuristics.py # Demonstration script
```

## Architecture Highlights

### Modular "Lego Brick" Design

Each optimization strategy is an independent, composable component:

- **NearestNeighbor**: Fast constructive heuristic
- **TwoOpt**: Local search improvement
- **SimulatedAnnealing**: Temperature-based metaheuristic
- **GeneticAlgorithm**: Population-based metaheuristic

### Composable Solver

Strategies can be chained in any order:

```python
# Fluent interface
from src.algorithms import StrategyChain

chain = (StrategyChain()
    .construct_with(NearestNeighborStrategy(), start_node=0)
    .improve_with(TwoOptStrategy(), max_iterations=100)
    .optimize_with(SimulatedAnnealingStrategy(seed=42), max_iterations=1000)
)

solution, cost, metrics = solver.solve(chain.build())
```

### Centralized Data Management

ProblemContext prevents expensive recomputations:

```python
context = ProblemContext(coordinates=coords)

# Distance matrix computed once and cached
dist_matrix = context.distance_matrix  # First access: computes
dist_matrix = context.distance_matrix  # Subsequent: cached

# Utilities
cost = context.compute_tour_cost(tour)
is_valid = context.validate_tour(tour)
```

## Testing

### Test Coverage

- 18 tests total (100% passing)
- 11 unit tests
- 7 integration tests

### Run Tests

```bash
# All tests
python -m pytest tests/ -v

# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Development

### Adding a New Strategy

1. Implement the appropriate protocol (`ConstructiveStrategy`, `ImprovementStrategy`, or `MetaheuristicStrategy`)
2. Add the strategy to `src/algorithms/`
3. Export it in `src/algorithms/__init__.py`
4. Add tests in `tests/unit/`
5. Update documentation

Example:

```python
# src/algorithms/my_strategy.py
import numpy as np
from numpy.typing import NDArray

class MyStrategy:
    @property
    def name(self) -> str:
        return "MyStrategy"
    
    @property
    def backend(self) -> str:
        return "cpu"
    
    def improve(self, solution, distance_matrix, **kwargs):
        # Implementation
        return improved_solution, cost
```

### Code Quality

All code follows:
- Type hints for clarity
- Comprehensive docstrings
- Protocol-based interfaces
- Unit test coverage
- Performance considerations

## Performance

### Anti-Pattern Avoidance

✅ **No GPU kernel overhead in sequential code**  
✅ **Centralized distance matrix computation**  
✅ **Vectorized operations where possible**  
✅ **Backend-appropriate algorithm selection**  

### Benchmarking

```python
# Benchmark a strategy chain
stats = solver.benchmark_strategies(strategies, n_runs=10)

print(f"Mean cost: {stats['mean_cost']:.2f} ± {stats['std_cost']:.2f}")
print(f"Mean time: {stats['mean_time']:.3f}s")
```

## Documentation

- **ARCHITECTURE.md**: Detailed architecture documentation
- **Code docstrings**: All classes and methods documented
- **Type hints**: Full type annotations
- **Demo script**: Interactive examples

## Future Work

- [ ] GPU-accelerated strategies (CuPy)
- [ ] JIT-compiled strategies (Numba)
- [ ] Ant Colony Optimization (ACO)
- [ ] Tabu Search
- [ ] Parallel strategy evaluation
- [ ] Adaptive parameter tuning
- [ ] Multi-objective optimization

## License

See repository root for license information.

## Contributing

See repository root for contribution guidelines.
