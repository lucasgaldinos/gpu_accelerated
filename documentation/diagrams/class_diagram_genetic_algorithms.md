# Class Diagram: Genetic Algorithm Architecture

This diagram shows the class hierarchy, inheritance relationships, and composition patterns for the genetic algorithm implementations in the codebase.

```mermaid

```

## Key Design Patterns

### 1. Template Method Pattern

`GeneticAlgorithmBase` defines the algorithm skeleton with identical logic for all variants:

- Selection (Tournament k=5)
- Crossover (Order Crossover)
- Mutation (Swap, rate=0.02)
- Survival selection (μ+λ)

Subclasses only implement:

- `_improve_population()` - 2-opt improvement location (CPU/GPU)
- `_evaluate_population()` - Fitness calculation location (CPU/GPU)

### 2. Strategy Pattern

The base class composes three strategy objects:

- `TournamentSelection` - Selects parents via k-tournament
- `OrderCrossover` - Creates offspring via OX operator
- `SwapMutation` - Mutates tours by swapping cities

These strategies are **identical across all variants**, ensuring ISO-algorithmic comparison.

### 3. Dependency Injection

- `xp` parameter (BackendModule protocol) injected at runtime
- Enables backend-agnostic code: `xp.array()` works for NumPy or CuPy
- All algorithms accept `xp`, no hardcoded backend references

### 4. Lazy Loading

`ProblemContext` prevents performance anti-patterns:

- Distance matrix computed **once** on target backend
- Cached for reuse across all algorithm calls
- Prevents redundant O(n²) computations in loops

## Variant Differences

| Variant | 2-opt Location | Fitness Location | Transfers per Generation |
|---------|---------------|------------------|-------------------------|
| CPU | NumPy (CPU) | NumPy (CPU) | 0 (no GPU) |
| HybridNaive | 256 GPU calls | CPU | ~20MB |
| HybridOptimized | 1 batch GPU call | GPU (chained) | ~10MB |
| FullGPU | GPU-resident | GPU-resident | 0 (after initial setup) |

## Academic References

- **Template Method**: Gamma et al. (1994) - Design Patterns
- **Strategy Pattern**: Gamma et al. (1994) - Design Patterns  
- **Fujimoto Kernel**: Fujimoto & Tsutsui (2011) - "A highly parallel TSP solver for GPUs"
- **Tournament Selection**: Miller & Goldberg (1995)
- **Order Crossover**: Davis (1985)
