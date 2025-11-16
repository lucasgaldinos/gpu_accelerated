# Import Dependency Graph (M14 Refactor)

**Purpose:** Define acyclic import architecture for Strategy Pattern refactor (Metaheuristics)

**Date Created:** 2025-01-28  
**Refactor Scope:** M14-M15 (Simulated Annealing + Genetic Algorithm)

---

## Layered Architecture

```
Layer 1: protocols/
         ↓
Layer 2: algorithms/tour_operators/
         ↓
Layer 3: algorithms/strategies/ (metaheuristic strategies)
         ↓
Layer 4: algorithms/metaheuristics/
         ↓
Layer 5: benchmarking/
```

**Key Principle:** Lower layers NEVER import from higher layers (acyclic graph)

---

## Layer Definitions

### Layer 1: protocols/

**Location:** `code/src/protocols/`

**Responsibilities:**

- Define typing.Protocol interfaces for all components
- NO concrete implementations
- NO imports from algorithms/

**Files:**

- `backend.py` (existing - BackendModule for NumPy/CuPy)
- `strategy_protocols.py` (NEW - NeighborStrategy, MutationOperator, CrossoverStrategy, ImprovementOperator)

**Import Rules:**

- ✅ Can import: `typing`, `abc`, standard library
- ❌ Cannot import: anything from `algorithms/`, `data_models/`, `benchmarking/`

**Example:**

```python
# protocols/strategy_protocols.py
from typing import Protocol, List
from .backend import BackendModule  # Same layer OK
# NO: from ..algorithms.metaheuristics import SimulatedAnnealing
```

---

### Layer 2: algorithms/tour_operators/

**Location:** `code/src/algorithms/tour_operators/`

**Responsibilities:**

- Pure functions for tour manipulation (swap, insert, invert)
- Shared utilities for SA neighbor methods AND GA mutations
- Backend-agnostic (work with any BackendModule)

**Files:**

- `swap.py` - swap_cities(tour, i, j) → List[int]
- `insertion.py` - insert_city(tour, from_pos, to_pos) → List[int]
- `inversion.py` - invert_segment(tour, i, j) → List[int]

**Import Rules:**

- ✅ Can import: `protocols/` (BackendModule)
- ❌ Cannot import: `strategies/`, `metaheuristics/`

**Example:**

```python
# tour_operators/swap.py
from typing import List
from ...protocols.backend import BackendModule  # Layer 1 OK
# NO: from ..strategies import RandomSwapStrategy
```

---

### Layer 3: algorithms/strategies/

**Location:** `code/src/algorithms/strategies/`

**Responsibilities:**

- Concrete implementations of strategy protocols
- Compose tour_operators into higher-level behaviors
- SEPARATE from CVRP composition strategies (see NOTE below)

**Files (NEW - Metaheuristic Strategies):**

- `neighbor_strategies.py` - RandomSwapStrategy, Random2OptStrategy, TwoOptMoveStrategy
- `mutation_strategies.py` - SwapMutation, InsertionMutation, InversionMutation
- `crossover_strategies.py` - OrderCrossover
- `improvement_strategies.py` - TwoOptImprovement (post-processing)

**Files (EXISTING - CVRP Composition Strategies):**

- `bin_packing_strategies.py` - FFDStrategy, BFDStrategy
- `tsp_strategies.py` - NearestNeighborStrategy, ChristofidesStrategy
- `clustering_strategies.py` - Clustering algorithms

**Import Rules:**

- ✅ Can import: `protocols/`, `tour_operators/`
- ❌ Cannot import: `metaheuristics/`, `benchmarking/`

**Example:**

```python
# strategies/neighbor_strategies.py
from typing import List
from ...protocols.strategy_protocols import NeighborStrategy  # Layer 1 OK
from ..tour_operators import swap_cities  # Layer 2 OK
# NO: from ..metaheuristics import SimulatedAnnealing
```

**NOTE - Strategy Directory Organization:**

The `strategies/` directory serves TWO purposes:

1. **CVRP Compositional Solver** (existing):
   - bin_packing_strategies.py
   - tsp_strategies.py
   - clustering_strategies.py

2. **Metaheuristic Strategy Pattern** (NEW - M14-M15):
   - neighbor_strategies.py
   - mutation_strategies.py
   - crossover_strategies.py
   - improvement_strategies.py

Both use the "Lego Blocks" composition philosophy but for different levels:

- CVRP strategies: Compose bin packing + TSP + clustering into CVRP solver
- Metaheuristic strategies: Compose neighbor/mutation/crossover operators into SA/GA

**Registries:**

- `NEIGHBOR_REGISTRY: Dict[str, Callable[[], NeighborStrategy]]`
- `MUTATION_REGISTRY: Dict[str, Callable[[], MutationOperator]]`
- `CROSSOVER_REGISTRY: Dict[str, Callable[[], CrossoverStrategy]]`
- `IMPROVEMENT_REGISTRY: Dict[str, Callable[[], ImprovementOperator]]`

---

### Layer 4: algorithms/metaheuristics/

**Location:** `code/src/algorithms/metaheuristics/`

**Responsibilities:**

- High-level search algorithms (SA, GA, Tabu, ILS)
- Accept strategies via dependency injection
- Use REGISTRY for string → strategy resolution

**Files:**

- `simulated_annealing.py` (REFACTOR to accept neighbor_strategy parameter)
- `genetic_algorithm.py` (REFACTOR to accept mutation_operator, crossover_strategy parameters)

**Import Rules:**

- ✅ Can import: `protocols/` (NOT concrete strategies)
- ✅ Can import: `strategies/` (ONLY for registries, NOT concrete classes)
- ❌ Cannot import: Concrete strategy classes directly

**Example:**

```python
# metaheuristics/simulated_annealing.py
from typing import Optional
from ...protocols.strategy_protocols import NeighborStrategy  # Protocol OK
from ..strategies import NEIGHBOR_REGISTRY  # Registry OK

# ❌ WRONG (creates circular dependency risk):
# from ..strategies.neighbor_strategies import RandomSwapStrategy

class SimulatedAnnealing:
    def __init__(
        self,
        neighbor_strategy: Optional[NeighborStrategy] = None,
        neighbor_method: str = "swap",  # Legacy fallback
        **kwargs
    ):
        if neighbor_strategy is not None:
            self.neighbor_strategy = neighbor_strategy
        else:
            # Use registry for string lookup
            self.neighbor_strategy = NEIGHBOR_REGISTRY[neighbor_method]()
```

**Rationale:** Metaheuristics depend on strategy PROTOCOLS (compile-time), not concrete implementations (runtime via registry).

---

### Layer 5: benchmarking/

**Location:** `code/src/benchmarking/`

**Responsibilities:**

- Orchestrate experiments
- Compose algorithms using ALGORITHM_MAP
- Report results

**Files:**

- `runner.py` (uses ALGORITHM_MAP for string → algorithm factories)

**Import Rules:**

- ✅ Can import: ALL layers (top of the stack)
- Uses lambda factories for algorithm composition

**Example:**

```python
# benchmarking/runner.py
from ..algorithms.metaheuristics import SimulatedAnnealing, GeneticAlgorithm
from ..algorithms.strategies import (
    NEIGHBOR_REGISTRY,
    TwoOptMoveStrategy,
    RandomSwapStrategy
)

ALGORITHM_MAP = {
    "SA_swap": lambda **kwargs: SimulatedAnnealing(
        neighbor_strategy=RandomSwapStrategy(),
        **kwargs
    ),
    "SA_2opt": lambda **kwargs: SimulatedAnnealing(
        neighbor_strategy=TwoOptMoveStrategy(),
        **kwargs
    ),
}
```

---

## Rules (ENFORCE VIA CODE REVIEW)

### 1. NEVER import from lower layers

**Violation Example:**

```python
# ❌ WRONG: protocols/ importing from algorithms/
# protocols/strategy_protocols.py
from ..algorithms.strategies import RandomSwapStrategy  # CIRCULAR!
```

**Correct:**

```python
# ✅ CORRECT: protocols/ only imports typing
# protocols/strategy_protocols.py
from typing import Protocol, List
```

---

### 2. Strategy Resolution via Registry

**Why:** Metaheuristics need to instantiate strategies at runtime, but importing concrete classes creates circular dependencies.

**Solution:** Registry pattern (string → class factory lookup)

**Implementation:**

```python
# strategies/__init__.py
from .neighbor_strategies import RandomSwapStrategy, Random2OptStrategy

NEIGHBOR_REGISTRY: Dict[str, Callable[[], NeighborStrategy]] = {
    "swap": lambda: RandomSwapStrategy(),
    "2opt": lambda: Random2OptStrategy(),
}
```

**Usage in Metaheuristics:**

```python
# metaheuristics/simulated_annealing.py
from ..strategies import NEIGHBOR_REGISTRY  # Import registry, not classes

def __init__(self, neighbor_method: str = "swap", **kwargs):
    # Runtime lookup
    self.neighbor_strategy = NEIGHBOR_REGISTRY[neighbor_method]()
```

---

### 3. Circular Import Prevention

**Symptom:** `ImportError: cannot import name 'X' from partially initialized module`

**Common Causes:**

- Protocol imports strategy implementation
- Strategy imports metaheuristic
- Metaheuristic directly imports strategy class

**Fixes:**

**Option A: Use Registry** (preferred)

```python
# Instead of:
from ..strategies.neighbor_strategies import RandomSwapStrategy

# Use:
from ..strategies import NEIGHBOR_REGISTRY
strategy = NEIGHBOR_REGISTRY["swap"]()
```

**Option B: Lazy Import** (for tests/utils only)

```python
def test_something():
    # Import inside function (deferred until call time)
    from code.src.algorithms.strategies import RandomSwapStrategy
    ...
```

**Option C: Type-Only Import** (for type hints)

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..strategies.neighbor_strategies import RandomSwapStrategy

def foo(strategy: "RandomSwapStrategy") -> None:  # String quote for forward ref
    ...
```

---

### 4. Never use `from X import *`

**Why:** Makes dependencies implicit and hard to track

**Example:**

```python
# ❌ WRONG:
from ..strategies import *

# ✅ CORRECT:
from ..strategies import NEIGHBOR_REGISTRY, RandomSwapStrategy
```

---

## Validation Commands

### Import Order Check

Run these in sequence - each should succeed without ImportError:

```bash
# Layer 1: Protocols
python -c "from code.src.protocols.strategy_protocols import NeighborStrategy"

# Layer 2: Tour Operators
python -c "from code.src.algorithms.tour_operators.swap import swap_cities"

# Layer 3: Strategies
python -c "from code.src.algorithms.strategies.neighbor_strategies import RandomSwapStrategy"

# Layer 4: Metaheuristics
python -c "from code.src.algorithms.metaheuristics.simulated_annealing import SimulatedAnnealing"

# Layer 5: Benchmarking
python -c "from code.src.benchmarking.runner import ALGORITHM_MAP"
```

### Dependency Graph Visualization (Future)

```bash
# Use pydeps to visualize imports (once installed)
uv pip install pydeps
pydeps code/src/ --max-bacon=5 --cluster
# Should show acyclic graph
```

---

## Architecture Validation Checklist

Before merging M14-M15 refactor:

- [ ] All imports follow layer ordering (protocols → tour_operators → strategies → metaheuristics → benchmarking)
- [ ] No circular imports (all `python -c "import X"` commands succeed)
- [ ] Metaheuristics use REGISTRY, not direct strategy imports
- [ ] mypy --strict passes (protocols properly typed)
- [ ] Import validation commands all succeed
- [ ] No `from X import *` in production code

---

## Notes

**Created:** 2025-01-28 (M14.0.1)  
**Last Updated:** 2025-01-28  
**Next Review:** After M14.5 (registry implementation)

**Related Documents:**

- M14_M15_DETAILED_TASKS.md (implementation guide)
- M14_task_log.md (progress tracking)
