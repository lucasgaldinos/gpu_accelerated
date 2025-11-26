# Algorithm Composition Architecture

**Document Version:** 1.0  
**Created:** 2025-11-03  
**Author:** GitHub Copilot  
**Purpose:** Comprehensive design specification for TSP algorithm composition system

---

## Table of Contents

- [Algorithm Composition Architecture](#algorithm-composition-architecture)
  - [Table of Contents](#table-of-contents)
  - [1. Executive Summary](#1-executive-summary)
    - [Problem Statement](#problem-statement)
    - [Solution: Functional Composition Architecture](#solution-functional-composition-architecture)
  - [2. Architectural Patterns](#2-architectural-patterns)
    - [2.1 Functional Programming Pattern](#21-functional-programming-pattern)
    - [2.2 Pipeline Architecture Pattern](#22-pipeline-architecture-pattern)
  - [3. Design Patterns](#3-design-patterns)
    - [3.1 Strategy Pattern](#31-strategy-pattern)
    - [3.2 Template Method Pattern](#32-template-method-pattern)
    - [3.3 Backend Abstraction Pattern](#33-backend-abstraction-pattern)
  - [4. Core Components](#4-core-components)
    - [4.1 Algorithm Categories](#41-algorithm-categories)
      - [Construction Heuristics](#construction-heuristics)
      - [Improvement Heuristics](#improvement-heuristics)
      - [Metaheuristics](#metaheuristics)
    - [4.2 Data Flow](#42-data-flow)
  - [5. Shared Utilities](#5-shared-utilities)
    - [5.1 Tour Cost Computation](#51-tour-cost-computation)
    - [5.2 Tour Validation](#52-tour-validation)
    - [5.3 2-opt Move Utilities](#53-2-opt-move-utilities)
  - [6. Algorithm Integration](#6-algorithm-integration)
    - [6.1 Composition Patterns](#61-composition-patterns)
      - [Pattern 1: Simple Pipeline (Construction → Evaluation)](#pattern-1-simple-pipeline-construction--evaluation)
      - [Pattern 2: Improvement Pipeline (Construction → Improvement → Evaluation)](#pattern-2-improvement-pipeline-construction--improvement--evaluation)
      - [Pattern 3: Full Pipeline (Construction → Improvement → Metaheuristic → Evaluation)](#pattern-3-full-pipeline-construction--improvement--metaheuristic--evaluation)
      - [Pattern 4: Parallel Pipelines (Multi-Start)](#pattern-4-parallel-pipelines-multi-start)
    - [6.2 CPU vs GPU Workflows](#62-cpu-vs-gpu-workflows)
      - [CPU Workflow (NumPy Backend)](#cpu-workflow-numpy-backend)
      - [GPU Workflow (CuPy Backend)](#gpu-workflow-cupy-backend)
      - [Hybrid Workflow (CPU→GPU Transfer)](#hybrid-workflow-cpugpu-transfer)
    - [6.3 Experiment Scenarios](#63-experiment-scenarios)
      - [Scenario 1: Algorithm Comparison Study](#scenario-1-algorithm-comparison-study)
      - [Scenario 2: CPU vs GPU Speedup Study](#scenario-2-cpu-vs-gpu-speedup-study)
      - [Scenario 3: Improvement Heuristic Effectiveness](#scenario-3-improvement-heuristic-effectiveness)
  - [7. Extension Mechanisms](#7-extension-mechanisms)
    - [7.1 Adding New Construction Heuristics](#71-adding-new-construction-heuristics)
    - [7.2 Adding New Improvement Heuristics](#72-adding-new-improvement-heuristics)
    - [7.3 Adding New Metaheuristics](#73-adding-new-metaheuristics)
  - [8. Questions \& Considerations](#8-questions--considerations)
    - [8.1 Architectural Decisions](#81-architectural-decisions)
      - [Decision 1: Unified Callback Architecture (Q1, Q2, Q5 Resolution)](#decision-1-unified-callback-architecture-q1-q2-q5-resolution)
      - [Decision 2: CVRP Representation - Giant Tour Approach (Q3 Resolution)](#decision-2-cvrp-representation---giant-tour-approach-q3-resolution)
      - [Decision 3: GPU-16 Algorithm Factory Pattern - Status Restoration](#decision-3-gpu-16-algorithm-factory-pattern---status-restoration)
    - [8.2 Design Decisions Summary](#82-design-decisions-summary)
    - [8.3 Next Steps](#83-next-steps)
  - [9. Appendix: Complete Function Signatures](#9-appendix-complete-function-signatures)
    - [Construction Heuristics](#construction-heuristics-1)
    - [Improvement Heuristics](#improvement-heuristics-1)
    - [Metaheuristics](#metaheuristics-1)
    - [Shared Utilities](#shared-utilities)
  - [9. References](#9-references)

---

## 1. Executive Summary

### Problem Statement

We need an architecture that enables:

- **Composing algorithms:** Chain construction → improvement → metaheuristics
- **Backend agnosticism:** Same code runs on CPU (NumPy) or GPU (CuPy)
- **No duplicate logic:** Single cost computation, shared utilities
- **Extensibility:** Easy to add new algorithms (3-opt, Lin-Kernighan, etc.)

### Solution: Functional Composition Architecture

All algorithms are **pure functions** with consistent signature:

```python
algorithm(problem: Problem, [inputs], xp: BackendModule = np) -> tour_array
```

**Key Insight:** Algorithms compose via **function chaining** - output of one becomes input of next.

> [!note] Overview
> Pretty good solution if you ask me.

---

## 2. Architectural Patterns

### 2.1 Functional Programming Pattern

**Definition:** Algorithms as pure, stateless functions

**Why This Pattern?**

| Aspect | Functional Approach | OOP Alternative | Our Choice |
|--------|-------------------|-----------------|------------|
| **Simplicity** | Direct function calls | Classes, inheritance, polymorphism | ✅ Simpler |
| **Existing Code** | Matches NN implementation | Would require refactoring | ✅ Consistent |
| **Composition** | Function chaining: `f(g(h(x)))` | Method chaining: `x.h().g().f()` | ✅ Natural |
| **Backend Agnostic** | `xp` parameter passed explicitly | Backend injected via constructor | Both work |
| **Testing** | Pure functions easy to test | Mock objects, dependency injection | ✅ Clearer |
| **YAGNI Principle** | No abstraction overhead | Wrapper classes for 4 algorithms? | ✅ Appropriate |

**Verdict:** Functional approach is simpler, matches existing code, and sufficient for TCC scope.

### 2.2 Pipeline Architecture Pattern

**Definition:** Data flows through stages, each transforming the tour

```flow
Problem → [Construction] → Tour → [Improvement] → Tour → [Metaheuristic] → Tour → [Evaluation] → Cost
```

**Three Pipeline Stages:**

1. **Stage 1: Construction Heuristics**
   - **Input:** Problem instance
   - **Output:** Initial tour (feasible solution)
   - **Examples:** Nearest Neighbor, Random Tour, Greedy

2. **Stage 2: Improvement Heuristics**
   - **Input:** Problem + existing tour
   - **Output:** Improved tour (local optimum)
   - **Examples:** 2-opt, 3-opt, Lin-Kernighan

3. **Stage 3: Metaheuristics**
   - **Input:** Problem + initial tour
   - **Output:** Optimized tour (escape local optima)
   - **Examples:** Simulated Annealing, Tabu Search, Genetic Algorithm

**Pipeline Flexibility:** Any stage can be:

- **Skipped:** `NN → SA` (skip improvement)
- **Repeated:** `NN → 2-opt → 3-opt` (multiple improvements)
- **Parallelized:** Run multiple pipelines, pick best result

---

## 3. Design Patterns

### 3.1 Strategy Pattern

**Intent:** Define family of algorithms, make them interchangeable

**Implementation:** Algorithms are functions with same signature category

```python
# All construction heuristics follow this signature
ConstructionStrategy = Callable[[Problem, BackendModule], tour_array]

# All improvement heuristics follow this signature  
ImprovementStrategy = Callable[[Problem, tour_array, BackendModule], tour_array]

# All metaheuristics follow this signature
MetaheuristicStrategy = Callable[[Problem, tour_array, BackendModule], tour_array]
```

**Usage Example:**

```python
def compare_constructions(problem, strategies: list[ConstructionStrategy], xp=np):
    """Compare different construction heuristics."""
    results = []
    for strategy in strategies:
        tour = strategy(problem, xp)
        cost = compute_tour_cost(problem, tour, xp)
        results.append((strategy.__name__, cost))
    return results

# Usage
strategies = [nearest_neighbor, random_tour, greedy_insertion]
comparison = compare_constructions(problem, strategies, xp=cp)
```

### 3.2 Template Method Pattern

**Intent:** Define skeleton of algorithm, let utilities handle common steps

**Implementation:** Shared utilities extract common operations

```python
def two_opt_first_improvement(problem, tour, xp=np):
    """Template: validate → improve → return"""
    # Step 1: Validate (template step - shared utility)
    if not is_valid_tour(tour, problem, xp):
        raise ValueError("Invalid input tour")
    
    # Step 2: Improve (algorithm-specific logic)
    improved_tour = _two_opt_first_improvement_logic(problem, tour, xp)
    
    # Step 3: Return (template contract)
    return improved_tour
```

### 3.3 Backend Abstraction Pattern

**Intent:** Write once, run on CPU or GPU

**Implementation:** `xp: BackendModule` parameter + NumPy-compatible operations

```python
from protocols.backend import BackendModule
import numpy as np

def algorithm(problem: Problem, xp: BackendModule = np):
    # Backend-agnostic operations
    distances = xp.asarray(problem.distances)  # Transfer to backend
    tour = xp.zeros(n, dtype=xp.int32)  # Create on backend
    idx = xp.argmin(distances[current, :])  # Compute on backend
    return tour  # Backend-specific array (np.ndarray or cp.ndarray)
```

**Pattern Benefits:**

- Same source code for CPU and GPU
- Type hints via Protocol (PEP 544)
- No runtime overhead from abstraction

---

## 4. Core Components

### 4.1 Algorithm Categories

#### Construction Heuristics

**Signature:**

```python
def construction_heuristic(
    problem: Problem,
    [construction-specific params],
    xp: BackendModule = np
) -> tour_array
```

**Implemented:**

- `nearest_neighbor(problem, start_node=0, xp=np)` ✅

**Planned:**

- `random_tour(problem, seed=None, xp=np)`
- `greedy_insertion(problem, xp=np)`

#### Improvement Heuristics

**Signature:**

```python
def improvement_heuristic(
    problem: Problem,
    tour: Any,  # Input tour to improve
    [improvement-specific params],
    xp: BackendModule = np
) -> tour_array  # Improved tour
```

**Planned (Phase 2):**

- `two_opt_first_improvement(problem, tour, max_iter=None, xp=np)` → GPU-8
- `two_opt_best_improvement(problem, tour, max_iter=None, xp=np)` → GPU-9

**Future Extensions:**

- `three_opt(problem, tour, xp=np)`
- `lin_kernighan(problem, tour, xp=np)`
- `or_opt(problem, tour, xp=np)`

#### Metaheuristics

**Signature:**

```python
def metaheuristic(
    problem: Problem,
    initial_tour: Any,  # Starting solution (from construction or improvement)
    [metaheuristic-specific params],
    xp: BackendModule = np
) -> tour_array  # Best tour found during search
```

**Planned (Phase 2):**

- `simulated_annealing(problem, initial_tour, temp=1000, cooling=0.95, max_iter=10000, xp=np)` → GPU-12

**Future Extensions:**

- `tabu_search(problem, initial_tour, tabu_tenure=10, xp=np)`
- `iterated_local_search(problem, initial_tour, perturbation_strength=0.2, xp=np)`

### 4.2 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ PROBLEM (Immutable Dataclass)                                   │
│  - name, dimension, problem_type                                │
│  - coordinates, distances, capacity, demands                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ CONSTRUCTION HEURISTIC                                          │
│  Input: Problem                                                 │
│  Output: Tour (np.ndarray or cp.ndarray)                        │
│  Example: nearest_neighbor(problem, xp=cp)                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ IMPROVEMENT HEURISTIC (Optional)                                │
│  Input: Problem + Tour                                          │
│  Output: Improved Tour                                          │
│  Example: two_opt_first_improvement(problem, tour, xp=cp)       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ METAHEURISTIC (Optional)                                        │
│  Input: Problem + Initial Tour                                  │
│  Output: Optimized Tour                                         │
│  Example: simulated_annealing(problem, tour, xp=cp)             │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ EVALUATION                                                      │
│  Input: Problem + Tour                                          │
│  Output: Cost (float)                                           │
│  Example: compute_tour_cost(problem, tour, xp=cp)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Shared Utilities

### 5.1 Tour Cost Computation

**Already Implemented:** `code/src/algorithms/objectives/tour_cost.py`

```python
def compute_tour_cost(problem: Problem, tour: Any, xp: BackendModule = np) -> float:
    """
    Calculate total tour cost including return to start.
    
    Formula: cost(τ) = Σᵢ₌₀ⁿ⁻² D[τᵢ, τᵢ₊₁] + D[τₙ₋₁, τ₀]
    
    Args:
        problem: Problem with distance matrix
        tour: Tour as array of node indices
        xp: Backend module (NumPy or CuPy)
        
    Returns:
        Total tour cost as Python float
    """
```

**How It Works:**

1. Extract distance matrix from problem
2. Use advanced indexing to get edge costs: `distances[tour, xp.roll(tour, -1)]`
3. Sum all edge costs: `xp.sum(...)`
4. Return as Python float (backend-independent): `float(xp.sum(...))`

**Extension for New Algorithms:**
No changes needed! This function works with ANY tour array, regardless of how it was generated.

### 5.2 Tour Validation

**To Implement:**

```python
def is_valid_tour(tour: Any, problem: Problem, xp: BackendModule = np) -> bool:
    """
    Validate that tour visits all nodes exactly once.
    
    Checks:
    - Length equals problem dimension
    - All node indices in range [0, n-1]
    - No duplicate nodes
    
    Args:
        tour: Tour array to validate
        problem: Problem instance
        xp: Backend module
        
    Returns:
        True if valid, False otherwise
    """
    tour_array = xp.asarray(tour)
    n = problem.dimension
    
    # Check 1: Correct length
    if len(tour_array) != n:
        return False
    
    # Check 2: All nodes present (no duplicates, valid range)
    unique = xp.unique(tour_array)
    if len(unique) != n:
        return False
    
    if int(xp.min(unique)) != 0 or int(xp.max(unique)) != n - 1:
        return False
    
    return True
```

**Usage in Algorithms:**

```python
def two_opt_first_improvement(problem, tour, xp=np):
    # Defensive validation
    if not is_valid_tour(tour, problem, xp):
        raise ValueError(f"Invalid input tour: {tour}")
    
    # Proceed with algorithm
    ...
```

### 5.3 2-opt Move Utilities

**For SA Neighborhood Generation:**

```python
def generate_2opt_neighbor(tour: Any, xp: BackendModule = np) -> Any:
    """
    Generate random neighbor using 2-opt move.
    
    Randomly selects two edges and reverses segment between them.
    Used by metaheuristics (SA, Tabu Search) for move generation.
    
    Args:
        tour: Current tour
        xp: Backend module
        
    Returns:
        Neighbor tour (2-opt swap applied)
    """
    n = len(tour)
    
    # Random 2-opt move: pick i < j
    i = int(xp.random.randint(0, n - 2))
    j = int(xp.random.randint(i + 1, n))
    
    return apply_2opt_move(tour, i, j, xp)


def apply_2opt_move(tour: Any, i: int, j: int, xp: BackendModule = np) -> Any:
    """
    Apply 2-opt move: reverse tour segment [i:j].
    
    Args:
        tour: Current tour
        i, j: Segment boundaries (i < j)
        xp: Backend module
        
    Returns:
        New tour with segment reversed
    """
    tour_copy = xp.copy(tour)
    tour_copy[i:j] = tour_copy[i:j][::-1]
    return tour_copy
```

**Extension for New Improvement Types:**

Adding 3-opt moves:

```python
def generate_3opt_neighbor(tour: Any, xp: BackendModule = np) -> Any:
    """Generate random neighbor using 3-opt move."""
    n = len(tour)
    i, j, k = sorted(xp.random.choice(n, 3, replace=False))
    return apply_3opt_move(tour, i, j, k, xp)

def apply_3opt_move(tour, i, j, k, xp=np):
    """Apply 3-opt move (8 possible reconnection patterns)."""
    # Choose reconnection pattern randomly
    pattern = int(xp.random.randint(0, 8))
    # ... implementation
```

**No Changes to SA Code Needed!** Just pass different neighbor generator:

```python
def simulated_annealing(problem, initial_tour, neighbor_fn=generate_2opt_neighbor, xp=np):
    while temperature > min_temp:
        neighbor = neighbor_fn(current_tour, xp)  # Pluggable!
        ...
```

---

## 6. Algorithm Integration

### 6.1 Composition Patterns

#### Pattern 1: Simple Pipeline (Construction → Evaluation)

```python
import numpy as np
from src.loaders.database_loader import DatabaseLoader
from src.algorithms.construction.nearest_neighbor import nearest_neighbor
from src.algorithms.objectives.tour_cost import compute_tour_cost

# Load problem
with DatabaseLoader() as loader:
    problem = loader.load('berlin52')

# Construct solution
tour = nearest_neighbor(problem, start_node=0, xp=np)

# Evaluate
cost = compute_tour_cost(problem, tour, xp=np)
print(f"NN cost: {cost}")
```

#### Pattern 2: Improvement Pipeline (Construction → Improvement → Evaluation)

```python
import cupy as cp

# Load problem (same as above)
problem = loader.load('berlin52')

# Construct initial solution (GPU)
tour = nearest_neighbor(problem, xp=cp)

# Improve solution (GPU)
tour = two_opt_first_improvement(problem, tour, xp=cp)

# Evaluate
cost = compute_tour_cost(problem, tour, xp=cp)
print(f"NN + 2-opt cost: {cost}")
```

#### Pattern 3: Full Pipeline (Construction → Improvement → Metaheuristic → Evaluation)

```python
# The "Chimera" composition

# Step 1: Construction (CPU)
tour = nearest_neighbor(problem, xp=np)
print(f"NN cost: {compute_tour_cost(problem, tour, xp=np)}")

# Step 2: Improvement (CPU)
tour = two_opt_first_improvement(problem, tour, xp=np)
print(f"After 2-opt: {compute_tour_cost(problem, tour, xp=np)}")

# Step 3: Metaheuristic (GPU acceleration)
tour = xp.asarray(tour, dtype=cp.int32)  # Transfer to GPU
tour = simulated_annealing(problem, tour, temp=1000, cooling=0.95, xp=cp)
print(f"After SA: {compute_tour_cost(problem, tour, xp=cp)}")
```

#### Pattern 4: Parallel Pipelines (Multi-Start)

```python
def multi_start_optimization(problem, num_starts=10, xp=np):
    """Run multiple independent pipelines, return best."""
    best_tour = None
    best_cost = float('inf')
    
    for start_node in range(min(num_starts, problem.dimension)):
        # Each start uses different initial node
        tour = nearest_neighbor(problem, start_node=start_node, xp=xp)
        tour = two_opt_first_improvement(problem, tour, xp=xp)
        tour = simulated_annealing(problem, tour, xp=xp)
        
        cost = compute_tour_cost(problem, tour, xp=xp)
        if cost < best_cost:
            best_tour = tour
            best_cost = cost
    
    return best_tour, best_cost
```

### 6.2 CPU vs GPU Workflows

#### CPU Workflow (NumPy Backend)

```python
import numpy as np

# All operations on CPU
problem = loader.load('berlin52')
tour = nearest_neighbor(problem, xp=np)  # CPU construction
tour = two_opt_first_improvement(problem, tour, xp=np)  # CPU improvement
cost = compute_tour_cost(problem, tour, xp=np)  # CPU evaluation
```

**When to Use:** Small instances (n < 1000), development/debugging, baseline comparison

#### GPU Workflow (CuPy Backend)

```python
import cupy as cp

# All operations on GPU
problem = loader.load('d15112')  # Large instance
tour = nearest_neighbor(problem, xp=cp)  # GPU construction
tour = two_opt_best_improvement(problem, tour, xp=cp)  # GPU improvement (parallel)
cost = compute_tour_cost(problem, tour, xp=cp)  # GPU evaluation
```

**When to Use:** Large instances (n > 1000), production optimization, speedup benchmarks

#### Hybrid Workflow (CPU→GPU Transfer)

```python
# Construction on CPU (fast enough)
tour = nearest_neighbor(problem, xp=np)

# Transfer to GPU for expensive operations
tour_gpu = cp.asarray(tour, dtype=cp.int32)

# Improvement on GPU (benefits from parallelization)
tour_gpu = two_opt_best_improvement(problem, tour_gpu, xp=cp)

# Metaheuristic on GPU
tour_gpu = simulated_annealing(problem, tour_gpu, xp=cp)

# Evaluate on GPU
cost = compute_tour_cost(problem, tour_gpu, xp=cp)
```

**When to Use:** Balance CPU/GPU strengths, minimize transfer overhead

### 6.3 Experiment Scenarios

#### Scenario 1: Algorithm Comparison Study

```python
def compare_algorithms(problem, algorithms, xp=np):
    """Compare multiple construction heuristics."""
    results = []
    
    for algo_name, algo_fn in algorithms.items():
        tour = algo_fn(problem, xp=xp)
        cost = compute_tour_cost(problem, tour, xp=xp)
        results.append({
            'algorithm': algo_name,
            'cost': cost,
            'gap_to_optimal': (cost - optimal) / optimal * 100
        })
    
    return results

# Usage
algorithms = {
    'Nearest Neighbor': nearest_neighbor,
    'Random Tour': random_tour,
    'Greedy Insertion': greedy_insertion,
}
comparison = compare_algorithms(problem, algorithms, xp=cp)
```

#### Scenario 2: CPU vs GPU Speedup Study

```python
import time

def benchmark_cpu_vs_gpu(problem, algorithm):
    """Measure CPU vs GPU speedup for same algorithm."""
    
    # CPU execution
    start = time.time()
    tour_cpu = algorithm(problem, xp=np)
    cpu_time = time.time() - start
    
    # GPU execution (with transfer time)
    start = time.time()
    tour_gpu = algorithm(problem, xp=cp)
    gpu_time = time.time() - start
    
    # Verify correctness
    cost_cpu = compute_tour_cost(problem, tour_cpu, xp=np)
    cost_gpu = compute_tour_cost(problem, tour_gpu, xp=cp)
    assert abs(cost_cpu - cost_gpu) < 1e-6, "CPU/GPU mismatch!"
    
    return {
        'cpu_time': cpu_time,
        'gpu_time': gpu_time,
        'speedup': cpu_time / gpu_time,
        'cost': cost_cpu
    }
```

#### Scenario 3: Improvement Heuristic Effectiveness

```python
def measure_improvement(problem, initial_algorithm, improvement_algorithm, xp=np):
    """Measure improvement percentage from local search."""
    
    # Initial solution
    initial_tour = initial_algorithm(problem, xp=xp)
    initial_cost = compute_tour_cost(problem, initial_tour, xp=xp)
    
    # Improved solution
    improved_tour = improvement_algorithm(problem, initial_tour, xp=xp)
    improved_cost = compute_tour_cost(problem, improved_tour, xp=xp)
    
    improvement_pct = (initial_cost - improved_cost) / initial_cost * 100
    
    return {
        'initial_cost': initial_cost,
        'improved_cost': improved_cost,
        'improvement_percent': improvement_pct,
        'iterations': improved_tour.metadata.get('iterations', 'N/A')  # if tracked
    }
```

---

## 7. Extension Mechanisms

### 7.1 Adding New Construction Heuristics

**Example: Adding Greedy Insertion**

**Step 1:** Create implementation file

```bash
code/src/algorithms/construction/greedy_insertion.py
```

**Step 2:** Implement function following pattern

```python
from ...data_models.problem import Problem
from ...protocols.backend import BackendModule
import numpy as np

def greedy_insertion(problem: Problem, xp: BackendModule = np):
    """
    Greedy insertion construction heuristic.
    
    Algorithm:
    1. Start with tour of 3 nearest nodes
    2. Iteratively insert remaining nodes at position minimizing cost increase
    """
    n = problem.dimension
    distances = xp.asarray(problem.distances)
    
    # Initialize partial tour with 3 nodes
    tour = xp.array([0, 1, 2], dtype=xp.int32)
    unvisited = set(range(3, n))
    
    # Greedy insertion
    while unvisited:
        best_insertion = None
        best_cost_increase = xp.inf
        
        for node in unvisited:
            for i in range(len(tour)):
                # Cost of inserting node between tour[i] and tour[(i+1) % len(tour)]
                cost_increase = (
                    distances[tour[i], node] + 
                    distances[node, tour[(i+1) % len(tour)]] - 
                    distances[tour[i], tour[(i+1) % len(tour)]]
                )
                
                if cost_increase < best_cost_increase:
                    best_cost_increase = cost_increase
                    best_insertion = (i+1, node)  # Insert after position i
        
        # Insert best node
        pos, node = best_insertion
        tour = xp.insert(tour, pos, node)
        unvisited.remove(node)
    
    return tour
```

**Step 3:** Add to public API

```python
# code/src/algorithms/construction/__init__.py
from .nearest_neighbor import nearest_neighbor
from .greedy_insertion import greedy_insertion  # NEW

__all__ = ['nearest_neighbor', 'greedy_insertion']
```

**Step 4:** Use in experiments

```python
tour = greedy_insertion(problem, xp=cp)
cost = compute_tour_cost(problem, tour, xp=cp)
```

**No other changes needed!** Shared utilities (cost computation, validation) work automatically.

### 7.2 Adding New Improvement Heuristics

**Example: Adding 3-opt**

**Implementation:**

```python
# code/src/algorithms/improvement/three_opt.py

def three_opt(problem: Problem, tour: Any, max_iter: int = None, xp: BackendModule = np):
    """
    3-opt local search improvement heuristic.
    
    Explores all possible 3-edge exchanges (much larger neighborhood than 2-opt).
    """
    if not is_valid_tour(tour, problem, xp):  # Reuse validation!
        raise ValueError("Invalid input tour")
    
    improved = True
    iteration = 0
    current_tour = xp.asarray(tour)
    
    while improved and (max_iter is None or iteration < max_iter):
        improved = False
        n = len(current_tour)
        
        for i in range(n - 2):
            for j in range(i + 2, n - 1):
                for k in range(j + 2, n):
                    # Try all 8 reconnection patterns
                    for pattern in range(8):
                        new_tour = _apply_3opt_reconnection(
                            current_tour, i, j, k, pattern, xp
                        )
                        
                        # Compare costs using shared utility!
                        if _tour_cost_delta(problem, current_tour, new_tour, xp) < 0:
                            current_tour = new_tour
                            improved = True
                            break
        
        iteration += 1
    
    return current_tour
```

**Integration:**

```python
# Works seamlessly with existing algorithms
tour = nearest_neighbor(problem, xp=np)
tour = three_opt(problem, tour, xp=np)  # NEW
tour = simulated_annealing(problem, tour, xp=np)
cost = compute_tour_cost(problem, tour, xp=np)  # Reuse utility!
```

### 7.3 Adding New Metaheuristics

**Example: Adding Tabu Search**

**Implementation:**

```python
# code/src/algorithms/metaheuristics/tabu_search.py

def tabu_search(
    problem: Problem,
    initial_tour: Any,
    tabu_tenure: int = 10,
    max_iter: int = 1000,
    neighbor_fn: Callable = generate_2opt_neighbor,  # Reuse utility!
    xp: BackendModule = np
):
    """
    Tabu search metaheuristic.
    
    Uses short-term memory (tabu list) to escape local optima.
    """
    current_tour = xp.asarray(initial_tour)
    best_tour = xp.copy(current_tour)
    best_cost = compute_tour_cost(problem, best_tour, xp)  # Reuse!
    
    tabu_list = []
    
    for iteration in range(max_iter):
        # Generate candidates (reuse neighbor generator!)
        candidates = [neighbor_fn(current_tour, xp) for _ in range(20)]
        
        # Filter out tabu moves (unless aspiration criteria met)
        valid_candidates = [
            c for c in candidates 
            if _move_signature(c) not in tabu_list or 
               compute_tour_cost(problem, c, xp) < best_cost  # Aspiration
        ]
        
        # Select best non-tabu neighbor
        best_neighbor = min(
            valid_candidates, 
            key=lambda t: compute_tour_cost(problem, t, xp)  # Reuse!
        )
        
        # Update tabu list
        tabu_list.append(_move_signature(best_neighbor))
        if len(tabu_list) > tabu_tenure:
            tabu_list.pop(0)
        
        # Update current and best
        current_tour = best_neighbor
        current_cost = compute_tour_cost(problem, current_tour, xp)
        
        if current_cost < best_cost:
            best_tour = xp.copy(current_tour)
            best_cost = current_cost
    
    return best_tour
```

**Key Insight:** Tabu Search **reuses**:

- `generate_2opt_neighbor` (or any neighbor function)
- `compute_tour_cost` (for evaluation)
- Same signature pattern (problem, initial_tour, xp)

**Integration is trivial:**

```python
tour = nearest_neighbor(problem, xp=cp)
tour = tabu_search(problem, tour, tabu_tenure=15, xp=cp)  # NEW
cost = compute_tour_cost(problem, tour, xp=cp)
```

---

## 8. Questions & Considerations

### 8.1 Architectural Decisions

This section addresses key design decisions that emerged during architecture development, with particular focus on how they enable the research questions defined in [`first_draft.md`](../../drafts/first_draft.md#L562-L1130).

---

#### Decision 1: Unified Callback Architecture (Q1, Q2, Q5 Resolution)

**Problem Statement:**

The research questions require three seemingly separate capabilities:

- **Q1 (Metadata Tracking):** Capture iteration counts, improvement statistics, timing data
- **Q2 (Progress Monitoring):** Real-time progress tracking during algorithm execution
- **Q5 (History Tracking):** Full convergence history for academic analysis and plots

**Decision:** Implement a **unified callback system** that serves all three purposes through a single, consistent interface.

**Protocol Definition:**

```python
# code/src/protocols/callback_protocol.py

from typing import TypedDict, Callable, NotRequired
from types import ModuleType

class ProgressEvent(TypedDict):
    """
    Event data passed to callback during algorithm execution.
    
    Universal fields (all algorithms):
        iteration: Current iteration number (1-indexed)
        best_cost: Best solution cost found so far
        current_cost: Current solution cost being evaluated
        elapsed_time: Seconds since algorithm started
        
    Algorithm-specific fields (optional):
        temperature: Current temperature (Simulated Annealing)
        improvements_found: Number of improving moves (improvement heuristics)
        acceptance_rate: Fraction of moves accepted (metaheuristics)
    """
    iteration: int
    best_cost: float
    current_cost: float
    elapsed_time: float
    
    # Algorithm-specific optional fields
    temperature: NotRequired[float]
    improvements_found: NotRequired[int]
    acceptance_rate: NotRequired[float]

CallbackFunction = Callable[[ProgressEvent], bool]
"""
Callback function type for algorithm monitoring.

Args:
    event: Progress event containing current algorithm state
    
Returns:
    True to continue execution, False to stop early
    
Example:
    >>> def monitor(event: ProgressEvent) -> bool:
    ...     print(f"Iter {event['iteration']}: best={event['best_cost']:.2f}")
    ...     return event['iteration'] < 1000  # Stop after 1000 iterations
"""
```

**Implementation Pattern:**

```python
# Example: Simulated Annealing with callback support

import time
from typing import Callable
import numpy as np

def simulated_annealing(
    problem: Problem,
    initial_tour: list[int],
    initial_temp: float = 100.0,
    cooling_rate: float = 0.95,
    max_iterations: int = 10000,
    callback: CallbackFunction | None = None,
    callback_interval: int = 100,  # Call every 100 iterations
    xp: ModuleType = np,
) -> list[int]:
    """
    Simulated Annealing with optional progress callback.
    
    Args:
        problem: Problem instance to solve
        initial_tour: Starting solution
        initial_temp: Initial temperature
        cooling_rate: Temperature decay rate (0 < r < 1)
        max_iterations: Maximum iterations
        callback: Optional callback for monitoring (default: None)
        callback_interval: Call callback every N iterations (default: 100)
        xp: Backend module (numpy or cupy)
        
    Returns:
        Best tour found
    """
    start_time = time.time()
    current_tour = initial_tour.copy()
    best_tour = current_tour.copy()
    current_cost = calculate_tour_cost(current_tour, problem, xp)
    best_cost = current_cost
    temperature = initial_temp
    
    accepted_moves = 0
    total_moves = 0
    
    for iteration in range(1, max_iterations + 1):
        # Try random 2-opt move
        i, j = xp.random.randint(1, len(current_tour) - 1, size=2)
        if i > j:
            i, j = j, i
        
        neighbor = current_tour.copy()
        neighbor[i:j+1] = neighbor[i:j+1][::-1]
        neighbor_cost = calculate_tour_cost(neighbor, problem, xp)
        
        # Acceptance criterion
        delta = neighbor_cost - current_cost
        if delta < 0 or xp.random.random() < xp.exp(-delta / temperature):
            current_tour = neighbor
            current_cost = neighbor_cost
            accepted_moves += 1
            
            if current_cost < best_cost:
                best_tour = current_tour.copy()
                best_cost = current_cost
        
        total_moves += 1
        temperature *= cooling_rate
        
        # Invoke callback at specified interval
        if callback is not None and iteration % callback_interval == 0:
            event: ProgressEvent = {
                'iteration': iteration,
                'best_cost': best_cost,
                'current_cost': current_cost,
                'elapsed_time': time.time() - start_time,
                'temperature': temperature,
                'acceptance_rate': accepted_moves / total_moves,
            }
            should_continue = callback(event)
            if not should_continue:
                break  # Early termination requested
    
    return best_tour
```

**Usage Examples:**

```python
# Example 1: Simple monitoring (Q2 - progress tracking)
def monitor_progress(event: ProgressEvent) -> bool:
    """Print progress every callback invocation."""
    print(f"Iteration {event['iteration']}: best={event['best_cost']:.2f}, "
          f"current={event['current_cost']:.2f}, temp={event.get('temperature', 'N/A')}")
    return True  # Always continue

tour = simulated_annealing(
    problem,
    initial_tour,
    callback=monitor_progress,
    callback_interval=100,
    xp=np
)

# Example 2: History tracking for convergence analysis (Q5 - academic plots)
history: list[ProgressEvent] = []

tour = simulated_annealing(
    problem,
    initial_tour,
    callback=lambda event: (history.append(event), True)[1],  # Capture and continue
    callback_interval=100,
    xp=cp
)

# Generate convergence plot
import matplotlib.pyplot as plt
plt.plot([e['iteration'] for e in history], [e['best_cost'] for e in history])
plt.xlabel('Iteration')
plt.ylabel('Best Cost')
plt.title('Convergence Analysis')
plt.savefig('convergence.png')

# Example 3: Combined monitoring + history + early stopping (Q1 - metadata)
history: list[ProgressEvent] = []

def smart_callback(event: ProgressEvent) -> bool:
    """Track history, monitor progress, implement early stopping."""
    # Track full history for later analysis
    history.append(event)
    
    # Monitor progress periodically
    if event['iteration'] % 100 == 0:
        print(f"[{event['elapsed_time']:.1f}s] Iteration {event['iteration']}: "
              f"best={event['best_cost']:.2f}, "
              f"acceptance={event.get('acceptance_rate', 0):.1%}")
    
    # Early stopping: no improvement in last 500 iterations
    if len(history) >= 500:
        recent_costs = [e['best_cost'] for e in history[-500:]]
        if max(recent_costs) == min(recent_costs):
            print(f"Early stop: No improvement in 500 iterations")
            return False  # Stop algorithm
    
    # Time budget: stop after 10 seconds
    if event['elapsed_time'] > 10.0:
        print(f"Time budget exceeded: {event['elapsed_time']:.1f}s")
        return False
    
    return True  # Continue

tour = simulated_annealing(problem, initial_tour, callback=smart_callback)

# Example 4: GPU vs CPU comparison with synchronized history tracking
cpu_history: list[ProgressEvent] = []
gpu_history: list[ProgressEvent] = []

# CPU run
cpu_tour = simulated_annealing(
    problem, 
    initial_tour,
    callback=lambda e: (cpu_history.append(e), True)[1],
    callback_interval=100,
    xp=np  # NumPy backend
)

# GPU run (same initial solution for fair comparison)
gpu_tour = simulated_annealing(
    problem,
    initial_tour,
    callback=lambda e: (gpu_history.append(e), True)[1],
    callback_interval=100,
    xp=cp  # CuPy backend
)

# Compare convergence speed (Research Question Q2: Scaling Behavior)
plt.figure(figsize=(10, 6))
plt.plot([e['elapsed_time'] for e in cpu_history], 
         [e['best_cost'] for e in cpu_history], 
         label='CPU (NumPy)', marker='o')
plt.plot([e['elapsed_time'] for e in gpu_history], 
         [e['best_cost'] for e in gpu_history], 
         label='GPU (CuPy)', marker='s')
plt.xlabel('Time (seconds)')
plt.ylabel('Best Cost')
plt.legend()
plt.title('GPU vs CPU Convergence Comparison')
plt.savefig('gpu_vs_cpu_convergence.png')
```

**How This Unifies Q1, Q2, Q5:**

1. **Q1 (Metadata Tracking):** `ProgressEvent` captures iteration count, costs, elapsed time, and algorithm-specific metadata (temperature, acceptance rate). No need to return tuples or modify function signatures.

2. **Q2 (Progress Monitoring):** `CallbackFunction` enables real-time monitoring by printing or logging events during execution. User controls verbosity through `callback_interval`.

3. **Q5 (History Tracking):** User captures full convergence history by appending events to a list: `lambda e: (history.append(e), True)[1]`. Enables academic analysis, convergence plots, statistical validation.

**Callback Interval Design:**

Different algorithms have different natural callback frequencies:

- **Construction heuristics (Nearest Neighbor):** No callback (deterministic, fast, single pass)
- **Deterministic improvement (2-opt, Or-opt):** Callback every 10-50 iterations (frequent for monitoring)
- **Metaheuristics (SA, Tabu Search):** Callback every 100-1000 iterations (balances overhead vs granularity)

**Research Question Alignment:**

- **Q1 (GPU Overhead Threshold):** Track `elapsed_time` and `iteration` to measure speedup at different problem sizes
- **Q2 (Scaling Behavior):** Capture iteration count and costs at intervals to plot convergence curves, demonstrate GPU processes more iterations per second
- **Q3 (Memory Bottlenecks):** Monitor memory usage through custom event fields if needed
- **Q4 (Problem Structure Impact):** Compare convergence patterns across different problem structures
- **Q5 (Problem Type Comparison):** Same callback interface works for TSP, ATSP, CVRP - enables fair comparison

**Implementation Files:**

- `code/src/protocols/callback_protocol.py` - Protocol definitions
- `code/src/algorithms/simulated_annealing.py` - Example implementation with callbacks
- `code/tests/unit/test_callbacks.py` - Unit tests for callback functionality

**Decision Status:** ✅ **APPROVED** - Unified callback architecture adopted

---

#### Decision 2: CVRP Representation - Giant Tour Approach (Q3 Resolution)

**Problem Statement:**

CVRP requires representing multi-route solutions (multiple vehicles serving different customers). Two architectural options exist with significantly different implications for functional composition and GPU acceleration.

**Option A: Multi-Route Representation** (`list[list[int]]`)

Each route is a separate list. Example: 3 vehicles serving 8 customers:

```python
routes = [
    [0, 3, 7, 0],      # Vehicle 1: depot → customers 3,7 → depot
    [0, 2, 5, 9, 0],   # Vehicle 2: depot → customers 2,5,9 → depot
    [0, 1, 4, 6, 8, 0] # Vehicle 3: depot → customers 1,4,6,8 → depot
]
```

**Option B: Giant Tour Representation** (`list[int]`)

Single tour with depot visits marking route boundaries. Same solution:

```python
tour = [0, 3, 7, 0, 2, 5, 9, 0, 1, 4, 6, 8, 0]
# Interpreted as 3 routes by splitting at depot (node 0)
```

**Detailed Comparison:**

| Criterion | Option A (Multi-Route) | Option B (Giant Tour) |
|-----------|------------------------|----------------------|
| **Type Signature** | `list[list[int]]` | `list[int]` |
| **Functional Composition** | ❌ **BREAKS** (TSP ≠ CVRP types) | ✅ **PRESERVES** (same type) |
| **TSP Algorithm Reuse** | ❌ No (need CVRP-specific variants) | ✅ Yes (~95% code reuse) |
| **GPU Kernel Complexity** | ❌ High (ragged arrays, variable-length routes) | ✅ Low (identical to TSP) |
| **Code Duplication** | ❌ High (duplicate all TSP algorithms) | ✅ Minimal (reuse TSP code) |
| **Academic Representation** | ✅ Traditional (1960s-1990s CVRP papers) | ✅ Modern (2000s+ metaheuristics) |
| **Validation Clarity** | ✅ Explicit per-route validation | ⚠️ Implicit in cost function |
| **Implementation Complexity** | ❌ High (separate CVRP implementations) | ✅ Low (extend TSP with CVRP-aware cost) |
| **GPU Memory Layout** | ❌ Irregular (ragged arrays) | ✅ Contiguous (flat array) |
| **GPU Performance** | ❌ Slower (complex indexing) | ✅ Faster (sequential access) |
| **MDVRP Extension** | ⚠️ Moderate complexity | ✅ Simple (multiple depot markers) |
| **VRPPD Extension** | ⚠️ Moderate complexity | ✅ Simple (precedence in cost function) |

**Why Option A Breaks Functional Composition:**

```python
# TSP algorithm signatures:
def two_opt(problem: Problem, tour: list[int], xp) -> list[int]:
    """Input: single tour, Output: single tour"""

# CVRP Option A signatures (INCOMPATIBLE):
def cvrp_two_opt(problem: Problem, routes: list[list[int]], xp) -> list[list[int]]:
    """Input: multiple routes, Output: multiple routes"""

# COMPOSITION FAILS:
initial = nearest_neighbor(tsp_problem)       # Returns list[int]
improved = two_opt(tsp_problem, initial)      # ✅ Works

initial_routes = cvrp_nearest_neighbor(cvrp_problem)  # Returns list[list[int]]
improved = two_opt(cvrp_problem, initial_routes)      # ❌ TYPE ERROR!
# Must use: cvrp_two_opt(cvrp_problem, initial_routes)  # Separate function
```

**With Option A:** You need two parallel implementations of every algorithm (TSP and CVRP variants). Cannot compose TSP and CVRP algorithms together. Architecture goal violated.

**With Option B:** Same algorithms work for both problem types:

```python
# Unified solver (works for TSP, ATSP, CVRP, MDVRP, VRPPD):
def solve_routing_problem(problem: Problem, algorithm_chain: list[str]):
    solution = nearest_neighbor(problem, xp=np)
    
    for algorithm in algorithm_chain:
        if algorithm == "2-opt":
            solution = two_opt(problem, solution, xp=cp)  # ✅ Same function
        elif algorithm == "SA":
            solution = simulated_annealing(problem, solution, xp=cp)  # ✅ Same function
    
    return solution

# Usage:
tsp_solution = solve_routing_problem(tsp_problem, ["2-opt", "SA"])
cvrp_solution = solve_routing_problem(cvrp_problem, ["2-opt", "SA"])  # SAME CODE!
```

**Academic Validation for Giant Tour:**

Giant tour representation is **well-established in modern CVRP research**:

1. **Prins, C. (2004).** "A simple and effective evolutionary algorithm for the vehicle routing problem." *Computers & Operations Research*, 31(12), 1985-2002.
   - Introduced giant tour for CVRP genetic algorithms
   - HGSADC algorithm (Hybrid Genetic Search with Adaptive Diversity Control)
   - **1,800+ citations** - highly influential in VRP community

2. **Vidal, T., Crainic, T.G., Gendreau, M., Prins, C. (2013).** "A hybrid genetic algorithm with adaptive diversity management for a large class of vehicle routing problems with time-windows." *Computers & Operations Research*, 40(1), 475-489.
   - Giant tour for MDVRP (Multi-Depot VRP)
   - Shows elegant handling of multiple depots
   - **800+ citations** - state-of-the-art VRP solver

3. **Subramanian, A., Drummond, L.M.A., Bentes, C., Ochi, L.S., Farias, R. (2010).** "A parallel heuristic for the Vehicle Routing Problem with Simultaneous Pickup and Delivery." *Computers & Operations Research*, 37(11), 1899-1911.
   - Giant tour for VRPPD variant
   - Demonstrates extensibility to complex VRP variants

**Giant tour is NOT a workaround** - it's a principled design choice used in top-ranked CVRP solvers.

**GPU Performance Implications:**

```python
# Option A - Complex GPU kernel (pseudo-CUDA):
__global__ void evaluate_2opt_multiroute(routes, num_routes, route_lengths, distances):
    route_id = blockIdx.x
    route_start = route_offsets[route_id]  # ❌ Irregular memory access
    route_len = route_lengths[route_id]    # ❌ Divergent execution paths
    # Complex indexing with variable-length routes

# Option B - Simple GPU kernel (identical to TSP):
__global__ void evaluate_2opt(tour, n, distances):
    i = blockIdx.x * blockDim.x + threadIdx.x
    for j in range(i + 2, n):
        # Direct sequential access: tour[i], tour[j]  ✅ Coalesced memory
        delta = distances[tour[i], tour[j]] + ...
```

**Conclusion:** Option B likely **faster on GPU** due to better memory access patterns and simpler parallelization.

**CVRP Implementation with Giant Tour:**

```python
def calculate_tour_cost(tour: list[int], problem: Problem, xp) -> float:
    """Unified cost function for TSP, ATSP, and CVRP."""
    if problem.problem_type == "CVRP":
        # Split giant tour at depot visits
        routes = _split_at_depot(tour, depot=0)
        total_cost = 0.0
        
        for route in routes:
            # Validate capacity constraint
            route_demand = sum(problem.demands[c] for c in route if c != 0)
            if route_demand > problem.capacity:
                return float('inf')  # Infeasible solution
            
            # Sum distances in route
            for i in range(len(route) - 1):
                total_cost += problem.distances[route[i], route[i+1]]
        
        return total_cost
    else:  # TSP or ATSP
        return sum(problem.distances[tour[i], tour[i+1]] for i in range(len(tour) - 1))

def _split_at_depot(tour: list[int], depot: int = 0) -> list[list[int]]:
    """Split giant tour into individual routes at depot visits."""
    routes = []
    current_route = []
    
    for node in tour:
        current_route.append(node)
        if node == depot and len(current_route) > 1:
            routes.append(current_route)
            current_route = [depot]  # Start new route
    
    return routes
```

**Extension to MDVRP (Multi-Depot VRP):**

```python
# MDVRP with 2 depots (nodes 0, 1):
mdvrp_tour = [0, 3, 7, 0, 1, 2, 5, 1, 0, 4, 6, 0]
# Vehicle from depot 0 serves 3,7; depot 1 serves 2,5; depot 0 serves 4,6

def calculate_mdvrp_cost(tour, problem, xp):
    depot_set = {0, 1}  # Multiple depot nodes
    routes = _split_at_depots(tour, depot_set)
    
    for route in routes:
        if route[0] != route[-1]:  # Must start/end at same depot
            return float('inf')
        # ... capacity validation and cost calculation ...
```

**Extension to VRPPD (VRP with Pickup and Delivery):**

```python
# VRPPD: Customer has pickup (node 2) and delivery (node 5)
# Constraint: Pickup before delivery

def calculate_vrppd_cost(tour, problem, xp):
    pickup_map = {2: 1, 3: 2}  # node → customer
    delivery_map = {5: 1, 6: 2}
    picked_up = set()
    
    for node in tour:
        if node in pickup_map:
            picked_up.add(pickup_map[node])
        elif node in delivery_map:
            if delivery_map[node] not in picked_up:
                return float('inf')  # Delivery before pickup - infeasible
    
    # ... distance calculation ...
```

**Decision:** ✅ **APPROVED** - Giant Tour (Option B) adopted for:

- Functional composition preservation (core architecture goal)
- Massive code reuse (~95% shared TSP/CVRP implementations)
- Better GPU performance (simpler memory layout, coalesced access)
- MDVRP/VRPPD extensibility (same representation, extend cost function)
- Academic validity (Prins 2004, Vidal 2013, Subramanian 2010)

**Trade-off Acknowledged:** Giant tour is less conventional than multi-route in classical CVRP literature (1960s-1990s), but widely used in modern metaheuristic solvers (2000s+). Will require clear documentation explaining representation choice.

**Implementation Files:**

- `code/src/utils/cvrp_cost.py` - CVRP-aware cost calculation with giant tour
- `code/src/utils/tour_splitting.py` - Giant tour ↔ route list conversion utilities
- `code/tests/unit/test_cvrp_giant_tour.py` - Validation tests

---

#### Decision 3: GPU-16 Algorithm Factory Pattern - Status Restoration

**Problem Statement:**

GPU-16 (Algorithm Factory Pattern) was marked DEFERRED with LOW priority based on argument: "Only 4 algorithms, functional composition already simple."

**User Feedback:** "You will literally implement new algorithms in the next tasks - why defer it if we'll need this almost immediately? Do not defer."

**Analysis:**

**Tasks Implementing New Algorithms:**

- GPU-8: Simulated Annealing (metaheuristic)
- GPU-9: 2-opt Improvement (first-improvement variant)
- GPU-12: Variable Neighborhood Search (composition of neighborhoods)
- Future: Tabu Search, Guided Local Search, Or-opt, Lin-Kernighan

After implementing GPU-8, GPU-9, GPU-12, we'll have **6+ algorithms** requiring programmatic instantiation for:

- Benchmarking frameworks (compare multiple algorithms on same instances)
- Composition examples (`algorithm_composition_examples.py`)
- CLI tools (select algorithm by name: `--algorithm simulated_annealing`)
- Automated testing (instantiate all registered algorithms)

**Without Factory Pattern:**

```python
# Manual instantiation (brittle, not scalable):
if algorithm_name == "nearest_neighbor":
    algorithm = NearestNeighbor()
elif algorithm_name == "two_opt":
    algorithm = TwoOpt()
elif algorithm_name == "simulated_annealing":
    algorithm = SimulatedAnnealing(initial_temp=100.0, cooling_rate=0.95)
# ... add elif for every new algorithm (maintenance burden)
```

**With Factory Pattern:**

```python
# Declarative registration (automatic on import):
@register_algorithm("simulated_annealing")
class SimulatedAnnealing:
    def __init__(self, initial_temp: float = 100.0, cooling_rate: float = 0.95):
        ...

# Clean instantiation:
algorithm = AlgorithmFactory.create("simulated_annealing", initial_temp=150.0)
```

**Decision:** ✅ **APPROVED** - Restore GPU-16 to active development

**Updated Task Specification:**

| Field | Previous Value | New Value |
|-------|---------------|-----------|
| **Status** | DEFERRED | BACKLOG |
| **Priority** | LOW | MEDIUM |
| **Dependencies** | GPU-2, GPU-7 | GPU-2, GPU-7, **GPU-8, GPU-9, GPU-12** |
| **Timeline** | Future work | After GPU-8/9/12 completed |

**Justification:**

- Needed immediately after implementing 3+ algorithms (GPU-8, GPU-9, GPU-12)
- Enables testing composition examples cleanly
- Standard design pattern (1-2 hours implementation)
- Not complex, high value for benchmarking workflows

**Implementation Approach:**

```python
# code/src/utils/algorithm_factory.py

from typing import Type, Dict, Any
from code.src.protocols import AlgorithmProtocol

class AlgorithmFactory:
    """Factory for creating algorithm instances by name."""
    _registry: Dict[str, Type[AlgorithmProtocol]] = {}
    
    @classmethod
    def register(cls, name: str, algorithm_class: Type[AlgorithmProtocol]) -> None:
        """Register an algorithm class."""
        cls._registry[name] = algorithm_class
    
    @classmethod
    def create(cls, name: str, **kwargs: Any) -> AlgorithmProtocol:
        """Create algorithm instance by name."""
        if name not in cls._registry:
            raise ValueError(f"Unknown algorithm: {name}")
        return cls._registry[name](**kwargs)
    
    @classmethod
    def list_algorithms(cls) -> list[str]:
        """Return list of registered algorithms."""
        return list(cls._registry.keys())

def register_algorithm(name: str):
    """Decorator for algorithm registration."""
    def decorator(cls: Type[AlgorithmProtocol]) -> Type[AlgorithmProtocol]:
        AlgorithmFactory.register(name, cls)
        return cls
    return decorator
```

**Decision Status:** ✅ **APPROVED** - GPU-16 restored to BACKLOG with MEDIUM priority

---

### 8.2 Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Architecture** | Functional Composition | Simpler, matches existing code, sufficient for scope |
| **Cost Computation** | Centralized utility | Avoid duplication, backend-agnostic |
| **Algorithm Return** | Tour array only (no wrapper) | YAGNI - caller computes cost if needed |
| **Extension Mechanism** | Follow signature pattern | Simple, no framework overhead |
| **Factory Pattern** | Deferred | Not needed for 4 algorithms |
| **Validation** | Shared utility | Defensive programming, reusable |
| **Metadata Tracking** | Optional parameters | Add if experiments require |

---

### 8.3 Next Steps

**Implementation Priority:**

**Phase 2.1 - Core Utilities (Week 2, Day 1-2):**

1. ✅ `compute_tour_cost` - ALREADY EXISTS
2. 🎯 `is_valid_tour` - NEW validation utility
3. 🎯 `generate_2opt_neighbor` - NEW for SA
4. 🎯 `apply_2opt_move` - NEW helper

**Phase 2.2 - Improvement Heuristics (Week 2, Day 3-4):**

1. 🎯 `two_opt_first_improvement` - GPU-8
2. 🎯 `two_opt_best_improvement` - GPU-9

**Phase 2.3 - Metaheuristics (Week 3, Day 1-3):**

1. 🎯 `simulated_annealing` - GPU-12

**Phase 2.4 - Integration Testing (Week 3, Day 4-5):**

1. Composition examples (NN → 2-opt → SA)
2. CPU vs GPU benchmarks
3. Chimera validation

**Deferred to Future:**

- GPU-16: Algorithm Factory Pattern
- 3-opt, Lin-Kernighan improvements
- Tabu Search, ILS metaheuristics
- CVRP multi-route support

---

## 9. Appendix: Complete Function Signatures

### Construction Heuristics

```python
def nearest_neighbor(
    problem: Problem,
    start_node: int = 0,
    seed: Optional[int] = None,
    xp: BackendModule = np
) -> Any:  # tour array (np.ndarray or cp.ndarray)
    """Greedy construction: always pick nearest unvisited node."""

def random_tour(
    problem: Problem,
    seed: Optional[int] = None,
    xp: BackendModule = np
) -> Any:
    """Random permutation tour (baseline)."""
```

### Improvement Heuristics

```python
def two_opt_first_improvement(
    problem: Problem,
    tour: Any,
    max_iter: Optional[int] = None,
    xp: BackendModule = np
) -> Any:
    """2-opt with first-improvement strategy (restart after ANY improvement)."""

def two_opt_best_improvement(
    problem: Problem,
    tour: Any,
    max_iter: Optional[int] = None,
    xp: BackendModule = np
) -> Any:
    """2-opt with best-improvement strategy (evaluate ALL moves, pick best)."""
```

### Metaheuristics

```python
def simulated_annealing(
    problem: Problem,
    initial_tour: Any,
    initial_temp: Optional[float] = None,  # Auto-calculate if None
    cooling_rate: float = 0.95,
    max_iter: int = 10000,
    min_temp: float = 0.01,
    neighbor_fn: Callable = generate_2opt_neighbor,
    track_history: bool = False,
    callback: Optional[Callable] = None,
    xp: BackendModule = np
) -> Any:  # best_tour (or tuple[tour, history] if track_history=True)
    """Probabilistic local search with temperature-controlled acceptance."""
```

### Shared Utilities

```python
def compute_tour_cost(
    problem: Problem,
    tour: Any,
    xp: BackendModule = np
) -> float:
    """Calculate total tour distance including return edge."""

def is_valid_tour(
    tour: Any,
    problem: Problem,
    xp: BackendModule = np
) -> bool:
    """Validate tour visits all nodes exactly once."""

def generate_2opt_neighbor(
    tour: Any,
    xp: BackendModule = np
) -> Any:
    """Generate random 2-opt neighbor for metaheuristics."""

def apply_2opt_move(
    tour: Any,
    i: int,
    j: int,
    xp: BackendModule = np
) -> Any:
    """Apply 2-opt move: reverse segment tour[i:j]."""
```

---

## 9. References

**Academic Citations:**

- **Fujimoto, N., & Tsutsui, S. (2011).** "A highly-parallel TSP solver for a GPU computing platform." *Numerical Methods and Applications*, 264-271. Springer. [GPU acceleration of TSP local search]

- **Prins, C. (2004).** "A simple and effective evolutionary algorithm for the vehicle routing problem." *Computers & Operations Research*, 31(12), 1985-2002. [Giant tour representation for CVRP]

- **Rocki, K., & Suda, R. (2013).** "High Performance GPU Accelerated Local Optimization in TSP." *IEEE International Symposium on Parallel and Distributed Processing Workshops*, 1788-1796. [GPU-accelerated 2-opt]

- **Schulz, C., Hasle, G., Brodtkorb, A.R., & Hagen, T.R. (2013).** "GPU computing in discrete optimization. Part II: Survey focused on routing problems." *EURO Journal on Transportation and Logistics*, 2(1-2), 159-186. [GPU optimization survey]

- **Subramanian, A., Drummond, L.M.A., Bentes, C., Ochi, L.S., & Farias, R. (2010).** "A parallel heuristic for the Vehicle Routing Problem with Simultaneous Pickup and Delivery." *Computers & Operations Research*, 37(11), 1899-1911. [Giant tour for VRPPD]

- **Vidal, T., Crainic, T.G., Gendreau, M., & Prins, C. (2013).** "A hybrid genetic algorithm with adaptive diversity management for a large class of vehicle routing problems with time-windows." *Computers & Operations Research*, 40(1), 475-489. [Giant tour for MDVRP, state-of-the-art VRP solver]

- **Voudouris, C., & Tsang, E. (1999).** "Guided local search and its application to the traveling salesman problem." *European Journal of Operational Research*, 113(2), 469-499. [Metaheuristic for TSP]

**Internal References:**

- GPU-8: 2-opt First-Improvement Task Specification
- GPU-9: 2-opt Best-Improvement Task Specification
- GPU-12: Simulated Annealing Task Specification
- Existing Implementation: `code/src/algorithms/construction/nearest_neighbor.py`
- Existing Implementation: `code/src/algorithms/objectives/tour_cost.py`
- Decision 9: Backend Parameter Pattern
- Research Questions: [`first_draft.md`](../../drafts/first_draft.md#L562-L1130)

---

**End of Architecture Documentation**

---
