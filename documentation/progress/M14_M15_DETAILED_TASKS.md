# M14-M15: Strategy Pattern Refactor - Complete Task Breakdown

**Objective:** Transform monolithic metaheuristics into composable lego-brick architecture

**Timeline:** ~40h (descoped: no M17 comprehensive demo, defer OX vectorization)

**Process:** Type-Driven Development (Architecture → Skeleton → Implementation → Validation)

> [!WARNING]
> **DOCUMENT STATUS: FULLY UPDATED (2025-01-28)**
>
> This document has been systematically updated to reflect:
>
> - ✅ Current implementation status (protocols, tour operators, strategies exist)
> - ✅ SA refactored with neighbor_strategy (but needs 4 fixes - see M14.3.4 subtasks)
> - ❌ GA NOT refactored (PHASE 4 not started)
> - ✅ All completed tasks marked with verification steps
> - ✅ NEW SUBTASKS added for small fixes (docstrings, parameters, GPU guardrails)
> - ✅ Future work (M16-M19) expanded with detailed task breakdowns
>
> **Architecture Reference:** `METAHEURISTIC_ARCHITECTURE_DECISIONS.md`
>
> **Implementation Status by Phase:**
>
> - ✅ PHASE 0: Tooling (mypy.ini, validation script exist - need verification)
> - ✅ PHASE 1: Protocols (strategy_protocols.py exists with 4 protocols)
> - ✅ PHASE 2: Tour Operators (swap_cities, insert_city, invert_segment exist)
> - ⚠️ PHASE 3: SA Strategies (✅ 3 strategies + SA refactored, BUT needs 4 fixes)
>   - M14.3.4.1: Fix docstring (P-Data → S-Task)
>   - M14.3.4.2: Add backend parameter to SA.**init**
>   - M14.3.4.3: Implement GPU guardrails (_check_vram_capacity)
>   - M14.3.4.4: Implement buffer reuse pattern (optional optimization)
> - ❌ PHASE 4: GA Refactor (NOT STARTED - depends on Phase 3 fixes)
> - ❌ PHASE 5: Registries (NOT STARTED)
> - ❌ PHASE 6: Integration Tests (NOT STARTED)
> - ❌ PHASE 7: TwoOpt Integration (NOT STARTED)
>
> **Next Actions:**
>
> 1. Complete M14.3.4 subtasks (SA fixes)
> 2. Proceed to PHASE 4 (GA refactor)
> 3. Continue through PHASE 7
> 4. Reassess M16-M19 scope after M14-M15 complete
>
> **Document Changes Summary:**
>
> - Every phase updated with ✅/⚠️/❌ status indicators
> - All complete tasks now have "Verify" instructions instead of "Create"
> - 4 NEW subtasks added to M14.3.4 for SA fixes
> - PHASE 4-7 clearly marked as NOT STARTED
> - M16-M19 expanded from summaries to full task breakdowns
> - ~1000 lines of clarifications and corrections added

- [M14-M15: Strategy Pattern Refactor - Complete Task Breakdown](#m14-m15-strategy-pattern-refactor---complete-task-breakdown)
  - [VALIDATION SCRIPT (Use Throughout)](#validation-script-use-throughout)
- [PHASE 0: Foundation (2-3h)](#phase-0-foundation-2-3h)
  - [Backend Configuration Architecture](#backend-configuration-architecture)
    - [Overview](#overview)
    - [Key Principles](#key-principles)
    - [Configuration Patterns](#configuration-patterns)
      - [Pattern 1: Single Backend (All Components Match)](#pattern-1-single-backend-all-components-match)
      - [Pattern 2: Hierarchical Backend (Component Override)](#pattern-2-hierarchical-backend-component-override)
      - [Pattern 3: Per-Component Backends (Full Control)](#pattern-3-per-component-backends-full-control)
    - [Parameter Naming Convention](#parameter-naming-convention)
    - [ALGORITHM\_MAP Factory Pattern](#algorithm_map-factory-pattern)
    - [Registry Pattern (Pass-Through \*\*kwargs)](#registry-pattern-pass-through-kwargs)
    - [Backend Conversion Template](#backend-conversion-template)
    - [Performance Characteristics](#performance-characteristics)
    - [Real-World Use Cases](#real-world-use-cases)
  - [M14.0: Architecture Skeleton \& Tooling Setup](#m140-architecture-skeleton--tooling-setup)
    - [Task M14.0.1: Import Dependency Diagram (45min)](#task-m1401-import-dependency-diagram-45min)
    - [Task M14.0.3: Configure mypy (30min)](#task-m1403-configure-mypy-30min)
    - [Task M14.0.4: Create Validation Script (45min)](#task-m1404-create-validation-script-45min)
    - [Task M14.0.5: Initialize Task Log (15min)](#task-m1405-initialize-task-log-15min)
- [PHASE 1: Protocol Definitions (2-3h)](#phase-1-protocol-definitions-2-3h)
  - [M14.1: Define Strategy Protocols](#m141-define-strategy-protocols)
    - [Task M14.1.1: Research Existing Implementations (45min)](#task-m1411-research-existing-implementations-45min)
    - [Task M14.1.2: Implement Protocol Definitions (90min)](#task-m1412-implement-protocol-definitions-90min)
    - [Task M14.1.3: Protocol Validation Tests (30min)](#task-m1413-protocol-validation-tests-30min)
- [PHASE 2: Shared Utilities (2-3h)](#phase-2-shared-utilities-2-3h)
  - [M14.2: Extract Tour Operators](#m142-extract-tour-operators)
    - [Task M14.2.1: swap\_cities Utility (30min)](#task-m1421-swap_cities-utility-30min)
    - [Task M14.2.2: insert\_city Utility (30min)](#task-m1422-insert_city-utility-30min)
    - [Task M14.2.3: invert\_segment Utility (30min)](#task-m1423-invert_segment-utility-30min)
    - [Task M14.2.4: Update tour\_operators **init**.py (10min)](#task-m1424-update-tour_operators-initpy-10min)
- [PHASE 3: SA Strategy Extraction (3-4h)](#phase-3-sa-strategy-extraction-3-4h)
  - [M14.3: Extract SA Neighbor Strategies](#m143-extract-sa-neighbor-strategies)
    - [Task M14.3.1: RandomSwapStrategy (45min)](#task-m1431-randomswapstrategy-45min)
    - [Task M14.3.2: RandomInsertionStrategy (30min)](#task-m1432-randominsertionstrategy-30min)
    - [Task M14.3.3: Random2OptStrategy (30min)](#task-m1433-random2optstrategy-30min)
    - [Task M14.3.4: Refactor SimulatedAnnealing to Accept Strategy (60min)](#task-m1434-refactor-simulatedannealing-to-accept-strategy-60min)
    - [Task M14.3.5: SA Integration Test (30min)](#task-m1435-sa-integration-test-30min)
    - [Performance Testing Requirements (Data-Driven Constraints)](#performance-testing-requirements-data-driven-constraints)
      - [1. Iteration Counts (Empirically Validated)](#1-iteration-counts-empirically-validated)
      - [2. Problem Size Selection](#2-problem-size-selection)
      - [3. Acceptance Rate Validation](#3-acceptance-rate-validation)
      - [4. Cooling Rate Calculation](#4-cooling-rate-calculation)
      - [5. GPU Testing Constraints](#5-gpu-testing-constraints)
      - [6. Overhead Measurement (Test Pattern)](#6-overhead-measurement-test-pattern)
      - [7. Convergence Analysis](#7-convergence-analysis)
      - [8 type-driven must have data-driven validation](#8-type-driven-must-have-data-driven-validation)
        - [Rationale](#rationale)
      - [Expected Outcomes (Validated Baselines)](#expected-outcomes-validated-baselines)
- [PHASE 4: GA Strategy Extraction (3-4h)](#phase-4-ga-strategy-extraction-3-4h)
  - [M14.4: Extract GA Operator Strategies](#m144-extract-ga-operator-strategies)
    - [Task M14.4.1: Mutation Strategies (60min)](#task-m1441-mutation-strategies-60min)
    - [Task M14.4.2: Crossover Strategies (90min)](#task-m1442-crossover-strategies-90min)
    - [Task M14.4.3: Refactor GeneticAlgorithm to Accept Strategies (90min)](#task-m1443-refactor-geneticalgorithm-to-accept-strategies-90min)
    - [Task M14.4.4: GA Integration Tests (45min)](#task-m1444-ga-integration-tests-45min)
- [PHASE 5: Strategy Registries (1.5-2h)](#phase-5-strategy-registries-15-2h)
  - [M14.5: Create Strategy Registries](#m145-create-strategy-registries)
    - [Task M14.5.0: Classify Strategies as Stateless/Stateful (30min)](#task-m1450-classify-strategies-as-statelessstateful-30min)
    - [Task M14.5.1: Create Strategy Registries (75min)](#task-m1451-create-strategy-registries-75min)
- [PHASE 6: Integration Testing (1-1.5h)](#phase-6-integration-testing-1-15h)
  - [M14.6: Full Pipeline Integration](#m146-full-pipeline-integration)
    - [Task M14.6.1: Full Pipeline Tests (60min)](#task-m1461-full-pipeline-tests-60min)
  - [M15.1.2: TwoOptImprovement (Post-Processing Operator)](#m1512-twooptimprovement-post-processing-operator)
    - [Task M15.1.2.1: Create TwoOptImprovement (60min)](#task-m15121-create-twooptimprovement-60min)
  - [M15.2: Register TwoOpt in Registries](#m152-register-twoopt-in-registries)
    - [Task M15.2.1: Update Registries (20min)](#task-m1521-update-registries-20min)
  - [M15.3: GA + TwoOpt Integration](#m153-ga--twoopt-integration)
    - [Task M15.3.1: Create GA + TwoOpt Integration Tests (45min)](#task-m1531-create-ga--twoopt-integration-tests-45min)
  - [M15.4: ALGORITHM\_MAP Refactor](#m154-algorithm_map-refactor)
    - [Task M15.4.1: Refactor ALGORITHM\_MAP (60min)](#task-m1541-refactor-algorithm_map-60min)
- [PHASE 7: TwoOpt Integration (3-4h)](#phase-7-twoopt-integration-3-4h)
  - [M15.1: TwoOptMove Strategy (Wrap TwoOptCPU/GPU)](#m151-twooptmove-strategy-wrap-twooptcpugpu)
    - [Task M15.1.1: TwoOptMoveStrategy (Wrapper for SA) (60min)](#task-m1511-twooptmovestrategy-wrapper-for-sa-60min)

---

## VALIDATION SCRIPT (Use Throughout)

**File:** `scripts/validate_refactor.sh`

```bash
#!/bin/bash
# Report mode - collect all errors, show summary
set +e

ERRORS=0

echo "======================================"
echo "M14-M15 Validation Suite"
echo "======================================"

echo ""
echo "[1/5] Type Checking (mypy --strict)..."
timeout 60s mypy code/src/ --config-file mypy.ini
if [ $? -ne 0 ]; then
    echo "❌ Type checking failed"
    ((ERRORS++))
else
    echo "✅ Type checking passed"
fi

echo ""
echo "[2/5] Import Safety Check..."
timeout 10s python -c "from code.src.protocols.strategy_protocols import NeighborStrategy" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Protocol imports failed"
    ((ERRORS++))
else
    echo "✅ Protocol imports OK"
fi

timeout 10s python -c "from code.src.algorithms.strategies import neighbor_strategies" 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Strategy imports not ready (expected if not yet implemented)"
else
    echo "✅ Strategy imports OK"
fi

echo ""
echo "[3/5] Protocol Tests..."
timeout 30s pytest tests/unit/protocols/ -v --tb=short 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Protocol tests failed (expected if not yet implemented)"
else
    echo "✅ Protocol tests passed"
fi

echo ""
echo "[4/5] Strategy Tests..."
timeout 60s pytest tests/unit/strategies/ -v --tb=short 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Strategy tests failed (expected if not yet implemented)"
else
    echo "✅ Strategy tests passed"
fi

echo ""
echo "[5/5] Integration Smoke Test..."
timeout 30s pytest tests/integration/ -k "test_sa_strategy or test_ga_strategy" -v --tb=short 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Integration tests failed (expected if not yet implemented)"
else
    echo "✅ Integration tests passed"
fi

echo ""
echo "======================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ ALL CRITICAL VALIDATIONS PASSED"
    exit 0
else
    echo "❌ $ERRORS CRITICAL FAILURES (see above)"
    exit 1
fi
```

---

# PHASE 0: Foundation (2-3h)

---

## Backend Configuration Architecture

> [!WARNING]
> **IMPLEMENTATION GAP: Backend Parameter Not in Current SA**
>
> **This section documents the INTENDED design, but:**
>
> 1. Current `SimulatedAnnealing.__init__` does NOT have `backend` parameter
> 2. Current implementation uses backend from `ProblemContext` (implicit)
> 3. Strategies DO have `backend` parameter (correct)
>
> **Required Changes:**
>
> 1. Add `backend: str = "numpy"` to `SimulatedAnnealing.__init__`
> 2. Store as `self.backend` and use for array operations
> 3. Implement GPU guardrails when `backend="cupy"` (see Section 2.1 of architecture doc)
> 4. Update ALGORITHM_MAP factory to pass `backend` parameter
>
> **Impact:** Medium - affects task M14.3.4 (SA refactor)
> **Timeline:** Add to M14.3.4 acceptance criteria

**Critical Design Pattern for GPU/CPU Mixed Backends**

### Overview

Strategies can run on different backends than their calling metaheuristic. This is **absolutely necessary** for hardware constraints:

- **Your GTX 1050 Mobile**: 4GB VRAM
- **GPU SA**: ~50MB (manageable)
- **GPU 2-opt**: ~56MB working buffers (too much!)
- **Solution**: GPU SA + CPU 2-opt improvement

### Key Principles

1. **Backend is Strategy Property** (not runtime selection)
   ```python
   # ✅ CORRECT: Backend set in __init__
   improvement = TwoOptImprovement(backend="cpu")
   
   # ❌ WRONG: Backend selected at runtime
   if xp.__name__ == 'cupy':
       backend = GPU()
   ```

2. **xp Parameter Purpose** (I/O conversion, not backend selection)
   ```python
   def improve(self, tour, problem, xp):
       # xp tells us: "What array type does CALLER expect?"
       # self.backend tells us: "What hardware do WE use?"
       
       # Convert input to our backend
       tour_internal = self.backend_module.asarray(tour)  # 5μs
       
       # Use OUR backend for work
       result = self._optimize(tour_internal, ...)  # 10-50ms
       
       # Convert output to caller's backend
       return xp.asarray(result)  # 5μs
   ```

3. **Transfer Overhead is Negligible** (for reasonable problem sizes)
   ```
   Tour (n=3000):          12 KB → 5μs transfer
   Distance matrix:        36 MB → 14ms first call, 0ms cached (CuPy)
   2-opt computation:      10-50ms
   
   Overhead: 5μs / 10,000μs = 0.05% ✅ ACCEPTABLE
   ```

### Configuration Patterns

#### Pattern 1: Single Backend (All Components Match)

```json
{
  "algorithm": "simulated_annealing",
  "backend": "gpu",
  "neighbor_strategy": "random_swap",
  "improvement_operator": "two_opt"
}
```

**Result**: All components (SA, neighbor, improvement) use GPU

#### Pattern 2: Hierarchical Backend (Component Override)

```json
{
  "algorithm": "simulated_annealing",
  "backend": "gpu",                    // Default for all
  "improvement_backend": "cpu",         // Override for improvement
  "neighbor_strategy": "random_swap",
  "improvement_operator": "two_opt",
  "improvement_max_iterations": 100
}
```

**Result**: SA + neighbor on GPU, improvement on CPU

#### Pattern 3: Per-Component Backends (Full Control)

```json
{
  "algorithm": "genetic_algorithm",
  "backend": "cpu",                     // Default fallback
  "mutation_backend": "gpu",            // Override: mutation on GPU
  "crossover_backend": "cpu",           // Override: crossover on CPU
  "improvement_backend": "cpu",         // Override: improvement on CPU
  "mutation_operator": "swap",
  "crossover_strategy": "ox",
  "improvement_operator": "two_opt"
}
```

**Result**: Each component uses specified backend

### Parameter Naming Convention

**Fallback Chain**: `{component}_backend` → `backend` → `"cpu"`

| Component | Parameter Name | Fallback |
|-----------|----------------|----------|
| Metaheuristic | `backend` | `"cpu"` |
| Neighbor | `neighbor_backend` | `backend` → `"cpu"` |
| Mutation | `mutation_backend` | `backend` → `"cpu"` |
| Crossover | `crossover_backend` | `backend` → `"cpu"` |
| Improvement | `improvement_backend` | `backend` → `"cpu"` |

### ALGORITHM_MAP Factory Pattern

```python
"simulated_annealing": lambda config: SimulatedAnnealing(
    neighbor_strategy=NEIGHBOR_REGISTRY[config["neighbor_strategy"]](
        problem=config["problem"],  # Injected by benchmark runner
        backend=config.get("neighbor_backend", config.get("backend", "cpu"))
    ),
    improvement_operator=IMPROVEMENT_REGISTRY[config.get("improvement_operator")](
        backend=config.get("improvement_backend", config.get("backend", "cpu")),
        max_iterations=config.get("improvement_max_iterations", 100)
    ) if config.get("improvement_operator") else None,
    backend=config.get("backend", "cpu")
)
```

### Registry Pattern (Pass-Through **kwargs)

**All registries use `lambda **kwargs:`** to pass configuration through:

```python
NEIGHBOR_REGISTRY: Dict[str, Callable[..., NeighborStrategy]] = {
    "two_opt_move": lambda **kwargs: TwoOptMoveStrategy(**kwargs),
}

IMPROVEMENT_REGISTRY: Dict[str, Callable[..., ImprovementOperator]] = {
    "two_opt": lambda **kwargs: TwoOptImprovement(**kwargs),
}
```

**Why `**kwargs`?**

- Enables configuration from user JSON
- Supports backend selection
- Allows max_iterations customization
- Works for both stateless (ignore kwargs) and stateful (use kwargs) strategies

### Backend Conversion Template

**For stateful strategies that run on specific hardware:**

```python
import numpy as np
try:
    import cupy
except ImportError:
    cupy = None

class TwoOptImprovement:
    def __init__(self, max_iterations: int = 100, backend: str = "cpu", **kwargs):
        self.max_iterations = max_iterations
        self.use_gpu = (backend == "gpu")
        
        # Set backend module ONCE (not at runtime)
        if self.use_gpu:
            if cupy is None:
                raise ImportError("CuPy required for GPU backend")
            self.backend_module = cupy
        else:
            self.backend_module = np
    
    def improve(self, tour, problem, xp):
        # Convert input to strategy's backend
        tour_internal = self.backend_module.asarray(tour)
        distances_internal = self.backend_module.asarray(problem.distances)
        
        # Optimize on strategy's backend
        improved = self._optimize_2opt(tour_internal, distances_internal)
        
        # Convert output to caller's backend
        return xp.asarray(improved)
```

**Key Points:**

- `self.backend_module`: What hardware WE use (set in `__init__`)
- `xp` parameter: What array type CALLER expects
- `asarray()`: Smart conversion (no copy if same backend, cached for CuPy)

### Performance Characteristics

**GPU SA + CPU Improvement (n=3000):**

| Operation | Time | Frequency | Amortized |
|-----------|------|-----------|-----------|
| Tour GPU→CPU transfer | 5μs | Every improvement call | 5μs |
| Distance matrix GPU→CPU | 14ms | First call only (cached) | 0.14ms/call |
| 2-opt computation (CPU) | 10-50ms | Every improvement call | 10-50ms |
| Tour CPU→GPU transfer | 5μs | Every improvement call | 5μs |
| **Total overhead** | **10μs** | - | **0.05%** ✅ |

**Conclusion**: Transfer overhead is negligible compared to computation time.

### Real-World Use Cases

1. **VRAM Constraints** (your 4GB GTX 1050)
   - GPU GA (population fits) + CPU 2-opt (avoid VRAM overflow)

2. **Performance Paradox** (CPU sometimes faster)
   - Some ops have kernel launch overhead on GPU
   - CPU NumPy vectorization can be faster for small n

3. **Development Workflow**
   - Develop/debug on CPU (easier)
   - Test in GPU metaheuristic (integration)
   - Keep CPU if fast enough (no GPU port needed)

---

## M14.0: Architecture Skeleton & Tooling Setup

**Status:** ⚠️ PARTIALLY COMPLETE - Validation script and mypy.ini exist, need verification of other tasks

**Prerequisites:** None (starting point)

**Context Files to Read:**

- Review: `code/src/` directory structure (understand current organization)
- Review: `code/src/protocols/backend.py` (lines 1-50, protocol example)
- Review: `pyproject.toml` (check if mypy is installed)

**Objective:** Create acyclic import dependency graph, directory structure, and validation tooling

**Current Reality:**

- ✅ `mypy.ini` EXISTS at project root
- ✅ `scripts/validate_refactor.sh` EXISTS
- ✅ Directory structure EXISTS (tour_operators/, strategies/)
- ❓ Import dependency diagram documentation - needs verification
- ❓ Task log - needs verification

---

### Task M14.0.1: Import Dependency Diagram (45min)

**Status:** ❓ NEEDS VERIFICATION - Check if `documentation/architecture/import_dependencies.md` exists

**Process Steps:**

1. **Design Graph (20min)**

   Draw dependency layers (NEVER import from lower layers):
   ```
   Layer 1: protocols/
     - strategy_protocols.py (NeighborStrategy, MutationOperator, CrossoverStrategy, ImprovementOperator)
     - backend.py (existing)
     - NO imports from algorithms/

   Layer 2: algorithms/tour_operators/
     - swap.py (swap two cities in tour)
     - insertion.py (remove city, insert elsewhere)
     - inversion.py (reverse tour segment)
     - Imports: protocols only (BackendModule)

   Layer 3: algorithms/strategies/
     - neighbor_strategies.py (RandomSwap, Random2Opt, TwoOptMove)
     - mutation_strategies.py (SwapMutation, InsertionMutation)
     - crossover_strategies.py (OrderCrossover)
     - improvement_strategies.py (TwoOptImprovement)
     - Imports: protocols, tour_operators

   Layer 4: algorithms/metaheuristics/
     - simulated_annealing.py (refactored to accept strategies)
     - genetic_algorithm.py (refactored to accept strategies)
     - Imports: protocols (NOT strategies - only via registry)

   Layer 5: benchmarking/
     - runner.py (orchestrates experiments)
     - Imports: metaheuristics, strategies (via ALGORITHM_MAP)
   ```

2. **Validate Acyclic (10min)**

   Check: Can protocols import strategies? NO ✅  
   Check: Can tour_operators import metaheuristics? NO ✅  
   Check: Can strategies import metaheuristics? NO ✅  
   Check: How do metaheuristics get strategies? Via REGISTRY (string lookup) ✅

3. **Document (15min)**

   **Create:** `documentation/architecture/import_dependencies.md`
   ```markdown
   # Import Dependency Graph (M14 Refactor)

   ## Layered Architecture

   ```
   protocols/ → tour_operators/ → strategies/ → metaheuristics/ → benchmarking/
   ```

   ## Rules (ENFORCE VIA CODE REVIEW)

   1. **NEVER import from lower layers**
      - protocols/ imports: standard library only
      - tour_operators/ imports: protocols only
      - strategies/ imports: protocols, tour_operators
      - metaheuristics/ imports: protocols (strategies via registry)

   2. **Strategy Resolution**
      - metaheuristics DO NOT directly import strategies
      - Use STRATEGY_REGISTRY for string → class lookup
      - Example:
        ```python
        # ❌ WRONG (creates circular dependency risk)
        from ..strategies.neighbor_strategies import RandomSwap

        # ✅ CORRECT (registry-based lookup)
        from ..strategies import NEIGHBOR_REGISTRY
        strategy = NEIGHBOR_REGISTRY["swap"]()
        ```

   3. **Circular Import Prevention**
      - If you get ImportError, check layer ordering
      - Move imports inside functions (lazy import) if necessary
      - Never use `from X import *` (makes dependencies implicit)

   ## Validation Command

   ```bash
   # Check import order violations
   python -c "import code.src.protocols.strategy_protocols"  # Should work
   python -c "import code.src.algorithms.tour_operators.swap"  # Should work
   python -c "import code.src.algorithms.strategies.neighbor_strategies"  # Should work
   ```
   ```

**Acceptance Criteria:**

- [ ] Dependency graph drawn (5 layers)
- [ ] Graph validated as acyclic
- [ ] Documentation created with import rules
- [ ] "NEVER import from lower layers" rule documented

**Rollback:** N/A (documentation only)

---

### Task M14.0.2: Create Directory Structure (15min)

**Process Steps:**

```bash
# Create tour_operators directory
mkdir -p code/src/algorithms/tour_operators
cat > code/src/algorithms/tour_operators/__init__.py << 'EOF'
"""
Tour operators (city-level mutations).

Shared utilities for SA neighbor methods and GA mutations.
Pure functions - take tour, return modified tour.

Used by:
- strategies/neighbor_strategies.py (SA)
- strategies/mutation_strategies.py (GA)
"""
EOF

# Create strategies directory
mkdir -p code/src/algorithms/strategies
cat > code/src/algorithms/strategies/__init__.py << 'EOF'
"""
Strategy implementations for metaheuristics.

Protocols:
- NeighborStrategy (SA, Tabu, ILS)
- MutationOperator (GA)
- CrossoverStrategy (GA)
- ImprovementOperator (post-processing)

Registries:
- NEIGHBOR_REGISTRY (string → NeighborStrategy)
- MUTATION_REGISTRY (string → MutationOperator)
- CROSSOVER_REGISTRY (string → CrossoverStrategy)
"""
EOF

# Verify structure
ls -R code/src/algorithms/
```

**Acceptance Criteria:**

- [ ] `tour_operators/` directory exists
- [ ] `strategies/` directory exists
- [ ] `__init__.py` files have docstrings
- [ ] `ls -R` shows new structure

---

### Task M14.0.3: Configure mypy (30min)

**Status:** ✅ COMPLETE - mypy.ini exists at project root

**Verification Steps:**

```bash
# 1. Verify mypy is installed
uv pip list | grep mypy

# 2. Verify mypy.ini exists
ls -la mypy.ini

# 3. Run baseline to document current errors
mypy code/src/ --config-file mypy.ini 2>&1 | tee documentation/progress/mypy_baseline.txt
```

**Acceptance Criteria:**

- [x] mypy installed (`uv pip list | grep mypy`)
- [x] `mypy.ini` exists with strict mode
- [ ] Baseline errors documented (run command above to create mypy_baseline.txt)

---

### Task M14.0.4: Create Validation Script (45min)

**Status:** ✅ COMPLETE - scripts/validate_refactor.sh exists and is executable

**Verification Steps:**

```bash
# 1. Verify script exists and is executable
ls -la scripts/validate_refactor.sh

# 2. Test run (will show current status)
bash scripts/validate_refactor.sh
```

**Expected Output:** Mix of ✅/⚠️/❌ depending on current implementation status

**Acceptance Criteria:**

- [x] Script created and executable
- [ ] Test run completes (verify by running above command)
- [x] No hangs (timeout guards work)
- [ ] Usage documentation exists (check documentation/progress/validation_usage.md)
  - `Any` types from untyped libraries (numpy, cupy)
  - Untyped protocol compliance

  ## Acceptable Errors (won't fix in M14)

  - Third-party library stubs (cupy, numpy)
  - Legacy code not touched by refactor
   ```

**Acceptance Criteria:**

- [ ] mypy installed (`uv pip list | grep mypy`)
- [ ] `mypy.ini` created with strict mode
- [ ] Baseline errors documented

---

### Task M14.0.4: Create Validation Script (45min)

**Process Steps:**

1. **Create Script (30min)**

   **Create:** `scripts/validate_refactor.sh` (content shown at top of this document)

2. **Make Executable (2min)**
   ```bash
   chmod +x scripts/validate_refactor.sh
   ```

3. **Test Run (10min)**
   ```bash
   bash scripts/validate_refactor.sh
   # Expected: Some failures (protocols not yet created)
   # Should NOT crash or hang (timeout guards)
   ```

4. **Document Usage (3min)**

   **Create:** `documentation/progress/validation_usage.md`
   ```markdown
   # Validation Script Usage

   **File:** `scripts/validate_refactor.sh`

   **Purpose:** Continuous validation during M14-M15 refactor

   ## When to Run
   - After EVERY task completion
   - Before EVERY commit
   - Before EVERY git push

   ## Expected Behavior
   - Reports ALL errors (doesn't stop on first failure)
   - Uses `timeout` to prevent hangs
   - Returns exit code 0 if critical tests pass, 1 otherwise

   ## Interpreting Results
   - ✅ = Test passed
   - ❌ = Critical failure (must fix)
   - ⚠️ = Expected failure (not yet implemented)

   ## What to Do on Failure
   1. Check which validation failed
   2. If mypy: Fix type hints
   3. If import: Check layer ordering (import_dependencies.md)
   4. If test: Check test implementation
   5. If stuck >30min: Document blocker in task log
   ```

**Acceptance Criteria:**

- [ ] Script created and executable
- [ ] Test run completes (even with failures)
- [ ] No hangs (timeout guards work)
- [ ] Usage documentation created

**Commit:**

```bash
git add scripts/validate_refactor.sh documentation/progress/validation_usage.md
git commit -m "chore(tooling): Add validation script for M14-M15 refactor"
```

---

### Task M14.0.5: Initialize Task Log (15min)

**Create:** `documentation/progress/M14_task_log.md`

```markdown
# M14-M15 Strategy Pattern Refactor - Task Log

**Start Date:** 2025-01-28  
**Branch:** `refactor/m14-strategy-pattern`  
**Status:** IN PROGRESS

---

## Progress Overview

### Phase 0: Foundation (M14.0)
- [x] M14.0.1: Import dependency diagram
- [x] M14.0.2: Directory structure
- [x] M14.0.3: mypy configuration
- [x] M14.0.4: Validation script
- [x] M14.0.5: Task log initialization

### Phase 1: Protocols (M14.1)
- [ ] M14.1.1: Protocol definitions
- [ ] M14.1.2: Protocol tests

### Phase 2: Shared Utilities (M14.2)
- [ ] M14.2.1: swap_cities utility
- [ ] M14.2.2: insert_city utility
- [ ] M14.2.3: invert_segment utility
- [ ] M14.2.4: Utility tests

### Phase 3: SA Refactor (M14.3)
- [ ] M14.3.1: Extract RandomSwapStrategy
- [ ] M14.3.2: Extract RandomInsertionStrategy
- [ ] M14.3.3: Extract Random2OptStrategy
- [ ] M14.3.4: Refactor SA to accept neighbor_strategy
- [ ] M14.3.5: SA integration test

### Phase 4: GA Refactor (M14.4)
- [ ] M14.4.1: Extract mutation strategies
- [ ] M14.4.2: Extract crossover strategies
- [ ] M14.4.3: Add post_process_strategy to GA
- [ ] M14.4.4: GA integration test

### Phase 5: Registries (M14.5)
- [ ] M14.5.1: NEIGHBOR_REGISTRY
- [ ] M14.5.2: MUTATION_REGISTRY
- [ ] M14.5.3: CROSSOVER_REGISTRY
- [ ] M14.5.4: Registry tests

### Phase 6: Integration (M14.6)
- [ ] M14.6.1: SA + RandomSwap integration test
- [ ] M14.6.2: GA + mutation strategies integration test
- [ ] M14.6.3: Full pipeline test (NN → SA → TwoOpt)

### Phase 7: TwoOpt Integration (M15.1-M15.4)
- [ ] M15.1.1: TwoOptMoveStrategy (wraps TwoOptCPU/GPU)
- [ ] M15.1.2: TwoOptImprovement (post-processing)
- [ ] M15.1.3: TwoOpt strategy tests
- [ ] M15.2.1: Register TwoOpt in NEIGHBOR_REGISTRY
- [ ] M15.2.2: SA + TwoOptMove integration test
- [ ] M15.3.1: TwoOptMutation for GA
- [ ] M15.3.2: GA + TwoOptMutation integration test
- [ ] M15.4.1: Update ALGORITHM_MAP with factories
- [ ] M15.4.2: Refactor BenchmarkRunner to use factories
- [ ] M15.4.3: Benchmark runner integration test

---

## Current Task

**Task:** M14.0.5 - Task log initialization  
**Status:** COMPLETE  
**Started:** 2025-01-28 [TIME]  
**Completed:** 2025-01-28 [TIME]  
**Commits:** [GIT SHA when committed]

---

## Blockers

None currently.

---

## Decisions Log

| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| 2025-01-28 | Separate Neighbor vs Mutation protocols | Semantic difference: exploration vs variation | Clearer architecture, better type safety |
| 2025-01-28 | Registry-based strategy resolution | Avoid circular imports, enable string configs | Metaheuristics don't directly import strategies |
| 2025-01-28 | Report mode for validation script | Don't stop on first failure, show all issues | Faster debugging (see all errors at once) |

---

## Notes

- Import dependency graph validated as acyclic
- Mypy baseline: [COUNT] errors (to be improved during refactor)
- Using timeout in validation script to prevent hangs
- Commit strategy: User handles commits, agent documents commit points
```

**Acceptance Criteria:**

- [ ] Task log created
- [ ] Progress overview populated
- [ ] Decisions log initialized
- [ ] Current task marked complete

**Commit:**

```bash
git add documentation/progress/M14_task_log.md
git commit -m "docs(progress): Initialize M14-M15 task log"
git push origin refactor/m14-strategy-pattern
```

---

**M14.0 COMPLETE - Proceed to M14.1**

---

# PHASE 1: Protocol Definitions (2-3h)

**Status:** ✅ COMPLETE - strategy_protocols.py exists with 4 protocols defined

## M14.1: Define Strategy Protocols

**Status:** ✅ COMPLETE - All protocols implemented and ready for use

**Prerequisites:**

- M14.0 complete (import graph, directories, tooling)

**Context Files to Read:**

- `code/src/protocols/backend.py` (lines 1-60, BackendModule protocol example)
- `code/src/protocols/strategy_protocols.py` (EXISTS - 265 lines, 4 protocols)

**Current Reality:**

- ✅ File EXISTS: `code/src/protocols/strategy_protocols.py` (265 lines)
- ✅ Protocol defined: `NeighborStrategy` (for SA neighbor generation)
- ✅ Protocol defined: `MutationOperator` (for GA mutation)
- ✅ Protocol defined: `CrossoverStrategy` (for GA recombination)
- ✅ Protocol defined: `ImprovementOperator` (for post-processing)

**Objective:** Verify protocol definitions are complete and usable

---

### Task M14.1.1: Research Existing Implementations (45min)

**Status:** ✅ COMPLETE - Research was done, protocols designed based on findings

**Verification:** Protocols in strategy_protocols.py reflect correct signatures

---

### Task M14.1.2: ✅ COMPLETE - Verify Protocol Definitions (30min)

**Original Task:** Implement Protocol Definitions  
**Current Reality:** Already implemented - needs verification only

**Verification Steps:**

1. **Verify File Exists (2min)**
   ```bash
   ls -la code/src/protocols/strategy_protocols.py
   # Should show 265-line file
   ```

2. **Verify All Protocols Present (5min)**
   ```bash
   grep -E "class (NeighborStrategy|MutationOperator|CrossoverStrategy|ImprovementOperator)" code/src/protocols/strategy_protocols.py
   ```
   **Expected Output:** 4 protocol definitions

3. **Verify Type Safety (10min)**
   ```bash
   mypy --strict code/src/protocols/strategy_protocols.py
   # Should pass with 0 errors (or document any existing errors)
   ```

4. **Verify Import Safety (5min)**
   ```bash
   python -c "from code.src.protocols.strategy_protocols import NeighborStrategy, MutationOperator, CrossoverStrategy, ImprovementOperator; print('✅ All protocols importable')"
   ```

5. **Review Protocol Signatures (8min)**
   - Read lines 1-100 of strategy_protocols.py
   - Confirm NeighborStrategy.generate_neighbor signature
   - Confirm MutationOperator.mutate signature
   - Confirm CrossoverStrategy.crossover signature
   - Confirm ImprovementOperator.improve signature

**Acceptance Criteria:**

- [x] Protocol file exists (265 lines)
- [x] All 4 protocols defined
- [ ] mypy --strict passes (verify)
- [ ] Import check succeeds (verify)
- [x] Protocols have comprehensive docstrings

**New Subtasks if Issues Found:**

If verification reveals problems:

- M14.1.2.1: Fix type hints in protocol signatures
- M14.1.2.2: Fix circular import issues
- M14.1.2.3: Add missing docstrings
- M14.1.2.4: Update acceptance criteria documentation

---

### Task M14.1.3: Protocol Validation Tests (30min)

**Status:** ❓ NEEDS VERIFICATION - Check if tests/unit/protocols/test_strategy_protocols.py exists

**Verification Steps:**

```bash
# Check if test file exists
ls -la tests/unit/protocols/test_strategy_protocols.py

# If exists, run tests
uv run pytest tests/unit/protocols/test_strategy_protocols.py -v
```

**Acceptance Criteria:**

- [ ] Test file exists
- [ ] Tests pass with pytest
- [ ] All 4 protocols have validation tests

**Process:**

1. **Read SA neighbor methods (20min)**
   ```bash
   # Open in editor:
   code/src/algorithms/metaheuristics/simulated_annealing.py:400-480
   ```

   **Document findings in task log:**
   ```markdown
   ## M14.1 Research Findings

   ### SA Neighbor Methods
   - `_neighbor_2opt(self, tour, n, xp)`:
     - Parameters: tour (List[int]), n (int, tour length), xp (BackendModule)
     - Returns: List[int] (neighbor tour)
     - Logic: Random i, j → reverse tour[i+1:j+1]
     - Uses xp: `xp.random.randint()` for random indices

   - `_neighbor_swap(self, tour, n, xp)`:
     - Same signature
     - Logic: Random i, j → swap tour[i] ↔ tour[j]

   - `_neighbor_insertion(self, tour, n, xp)`:
     - Same signature
     - Logic: Remove tour[i], insert at position j
   ```

2. **Read GA mutation methods (15min)**
   ```bash
   # Open in editor:
   code/src/algorithms/metaheuristics/genetic_algorithm.py:514-570
   ```

   **Document findings:**
   ```markdown
   ### GA Mutation Methods
   - `_mutation_swap(self, tour, xp)`:
     - Parameters: tour (List[int]), xp (BackendModule)
     - Returns: List[int]
     - Logic: Same as SA._neighbor_swap BUT different parameter (no `n`)

   - `_mutation_inversion(self, tour, xp)`:
     - Logic: Similar to SA._neighbor_2opt (reverse segment)

   - `_mutation_insertion(self, tour, xp)`:
     - Logic: Same as SA._neighbor_insertion
   ```

3. **Compare and Design (10min)**

   **Key Observation:**
   - SA passes `n` (tour length) explicitly
   - GA calculates `n = len(tour) - 1` internally
   - **Decision:** Protocol should NOT require `n` (strategies calculate it)

   **Protocol Design:**
   ```python
   class NeighborStrategy(Protocol):
       def generate_neighbor(self, tour, problem, xp) -> List[int]: ...
       # Uses `problem` for distances, not just tour length
   
   class MutationOperator(Protocol):
       def mutate(self, individual, xp) -> List[int]: ...
       # Does NOT need `problem` (no fitness evaluation during mutation)
   ```

   **Rationale:** Neighbor needs `problem` for move evaluation (if using TwoOptMove), mutation doesn't.

**Acceptance Criteria:**

- [ ] SA neighbor methods analyzed
- [ ] GA mutation methods analyzed
- [ ] Signature differences documented
- [ ] Protocol design decision made (Neighbor vs Mutation)
- [ ] Research findings in task log

---

### Task M14.1.2: Implement Protocol Definitions (90min)

**Process:**

1. **Create Protocol File (60min)**

   **Create:** `code/src/protocols/strategy_protocols.py`

   ```python
   """
   Strategy protocols for algorithm composition (Lego Brick Architecture).

   Enables pluggable operators for metaheuristics:
   - SimulatedAnnealing accepts NeighborStrategy
   - GeneticAlgorithm accepts CrossoverStrategy, MutationOperator, SelectionStrategy, ImprovementOperator

   Design Philosophy:
   - Protocols over inheritance (duck typing + type safety)
   - Single Responsibility (each protocol does ONE thing)
   - Semantic clarity (Neighbor vs Mutation vs Improvement)

   Type Safety:
   - Runtime: Python's structural subtyping (duck typing)
   - Compile-time: mypy validates protocol compliance

   References:
   - PEP 544: Protocols (Structural Subtyping)
   - Gang of Four: Strategy Pattern
   """

   from typing import Protocol, List, Tuple
   from ..data_models.problem import Problem
   from .backend import BackendModule


   class NeighborStrategy(Protocol):
       """
       Generate neighbor solution for local search metaheuristics.
       
       Semantic Context:
           Used by: Simulated Annealing, Tabu Search, Iterated Local Search
           Purpose: Explore solution space via single-move modifications
           Frequency: Called O(iterations) times per solve()
       
       Key Characteristics:
           - Single neighbor generation (not exhaustive search)
           - Stochastic (uses xp.random for randomness)
           - May use problem context (distances for move evaluation)
       
       Examples:
           - RandomSwapStrategy: Swap two random cities
           - RandomInsertionStrategy: Remove city, reinsert elsewhere
           - Random2OptStrategy: Reverse random tour segment
           - TwoOptMoveStrategy: Best single 2-opt move (uses distances)
       
       Comparison with ImprovementOperator:
           - Neighbor: Single move generation (SA's job to accept/reject)
           - Improvement: Iterative search until local optimum
       
       Validation Responsibilities:
           - Metaheuristic validates inputs ONCE (tour dimensions, depot positions)
           - Strategies ASSUME valid inputs (no duplicate validation)
           - Strategies MAY add domain-specific validation (e.g., CVRP capacity constraints)
           - Follow DRY principle: validate once at entry point, not in every strategy
       """
       
       def generate_neighbor(
           self,
           current_tour: List[int],
           problem: Problem,
           xp: BackendModule
       ) -> List[int]:
           """
           Generate neighbor from current tour.
           
           Args:
               current_tour: Current solution [depot, c1, c2, ..., ck, depot]
                   - First and last elements are depot (typically 0)
                   - Length: n+1 for n-city TSP
               problem: Problem instance
                   - problem.distances: (n, n) distance matrix
                   - problem.dimension: Number of nodes (n)
               xp: Backend module (numpy or cupy)
                   - Use xp.random for randomness
                   - Use xp operations for vectorization
                   
           Returns:
               Neighbor tour: List[int] with single modification
                   - Must maintain depot at first/last positions
                   - Must be valid permutation (all cities visited once)
           
           Example:
               >>> # Random swap strategy
               >>> import numpy as np
               >>> tour = [0, 5, 3, 7, 2, 0]  # 4-city TSP
               >>> neighbor = strategy.generate_neighbor(tour, problem, np)
               >>> neighbor  # e.g., [0, 3, 5, 7, 2, 0] (swapped 5 ↔ 3)
           """
           ...


   class MutationOperator(Protocol):
       """
       Introduce variation into genetic algorithm individual.
       
       Semantic Context:
           Used by: Genetic Algorithm
           Purpose: Maintain population diversity, prevent premature convergence
           Frequency: Called O(population_size × generations) times
       
       Key Characteristics:
           - Stochastic variation (not improvement-focused)
           - No fitness evaluation during mutation
           - Independent of problem context (blind variation)
       
       Examples:
           - SwapMutation: Random city swap
           - InversionMutation: Reverse random segment
           - InsertionMutation: Remove and reinsert city
           - TwoOptMutation: Apply single 2-opt move (for intensification)
       
       Comparison with NeighborStrategy:
           - Mutation: Genetic variation (no problem context)
           - Neighbor: SA exploration (may use distances)
           - Both: Single-move operations (not exhaustive)
       
       Validation Responsibilities:
           - Metaheuristic validates inputs ONCE (tour dimensions, depot positions)
           - Operators ASSUME valid inputs (no duplicate validation)
           - Operators MAY add domain-specific validation if needed
           - Follow DRY principle: validate once in GeneticAlgorithm, not in every operator
       """
       
       def mutate(
           self,
           individual: List[int],
           xp: BackendModule
       ) -> List[int]:
           """
           Mutate individual (introduce variation).
           
           Args:
               individual: Tour to mutate [depot, c1, ..., ck, depot]
               xp: Backend module (numpy or cupy)
                   
           Returns:
               Mutated tour: List[int] with variation introduced
                   - Should be structurally valid (depot preserved)
                   - May be worse than original (fitness evaluated later)
           
           Example:
               >>> # Swap mutation
               >>> import numpy as np
               >>> individual = [0, 1, 2, 3, 4, 0]
               >>> mutated = operator.mutate(individual, np)
               >>> mutated  # e.g., [0, 1, 4, 3, 2, 0] (swapped 2 ↔ 4)
           """
           ...


   class CrossoverStrategy(Protocol):
       """
       Combine two parents to produce offspring (genetic recombination).
       
       Semantic Context:
           Used by: Genetic Algorithm
           Purpose: Combine good traits from multiple parents
           Frequency: Called O(population_size × generations) times
       
       Key Characteristics:
           - Deterministic or stochastic (depends on implementation)
           - Must preserve tour validity (all cities visited once)
           - Typically produces 2 offspring from 2 parents
       
       Examples:
           - OrderCrossover (OX): Davis (1985) - preserve relative order
           - PartiallyMappedCrossover (PMX): Goldberg (1985) - preserve positions
           - CycleCrossover (CX): Oliver et al. (1987) - preserve absolute positions
       
       Complexity Note:
           - OX is O(n) in Python (for-loops)
           - Parallel OX (Fujimoto) is O(log n) with CUDA (future work)
       
       Validation Responsibilities:
           - Metaheuristic validates parent tours ONCE (dimensions, depot positions)
           - Crossover strategies ASSUME valid parent tours (no duplicate validation)
           - Strategies MUST ensure offspring validity (all cities visited once)
           - Follow DRY principle: validate inputs once in GeneticAlgorithm, validate outputs in crossover
       """
       
       def crossover(
           self,
           parent1: List[int],
           parent2: List[int],
           xp: BackendModule
       ) -> Tuple[List[int], List[int]]:
           """
           Generate two offspring from two parents.
           
           Args:
               parent1, parent2: Parent tours [depot, ..., depot]
               xp: Backend module (numpy or cupy)
                   
           Returns:
               (child1, child2): Two offspring tours
                   - Both must be valid permutations
                   - Should inherit traits from both parents
           
           Example:
               >>> # Order Crossover (OX)
               >>> parent1 = [0, 1, 2, 3, 4, 5, 0]
               >>> parent2 = [0, 3, 5, 1, 4, 2, 0]
               >>> child1, child2 = strategy.crossover(parent1, parent2, np)
               >>> # Children have segments from both parents
           """
           ...


   class ImprovementOperator(Protocol):
       """
       Improve solution quality via local search (intensification).
       
       Semantic Context:
           Used by: Post-processing, hybrid algorithms, memetic algorithms
           Purpose: Refine solutions to local optima
           Frequency: Called O(1) per solution (or per generation in GA)
       
       Key Characteristics:
           - Exhaustive local search (evaluates multiple moves)
           - Iterative improvement (until no improvement found)
           - Uses problem context (distances for move evaluation)
       
       Examples:
           - TwoOptImprovement: Iterative 2-opt until convergence
           - ThreeOptImprovement: 3-opt local search
           - VNDImprovement: Variable Neighborhood Descent
       
       Comparison with NeighborStrategy:
           - Improvement: Exhaustive search (O(N²) per iteration)
           - Neighbor: Single move generation (O(1) or O(N) for best move)
       
       Use Cases:
           - SA → TwoOpt pipeline: SA explores, TwoOpt refines
           - GA post-processing: Improve best individual after each generation
           - Memetic algorithms: Local search after crossover/mutation
       
       Validation Responsibilities:
           - Metaheuristic validates inputs ONCE (tour dimensions, depot positions, problem validity)
           - Improvement operators ASSUME valid inputs (tour structure pre-validated)
           - Operators MUST ensure output validity (preserved tour structure)
           - Follow DRY principle: validate once at entry point, not in every iteration of improve()
       """
       
       def improve(
           self,
           tour: List[int],
           problem: Problem,
           xp: BackendModule,
           max_iterations: int = 100
       ) -> List[int]:
           """
           Improve tour via local search.
           
           Args:
               tour: Initial tour [depot, ..., depot]
               problem: Problem instance (for distances)
               xp: Backend module (numpy or cupy)
               max_iterations: Maximum improvement iterations
                   - Default: 100 (enough for convergence on most instances)
                   - For TwoOptMove in SA: use max_iterations=1 (single best move)
                   
           Returns:
               Improved tour: Local optimum (or best found within max_iterations)
                   - Cost should be ≤ initial tour cost
                   - May be same as input if already at local optimum
           
           Example:
               >>> # 2-opt improvement
               >>> tour = [0, 5, 3, 7, 2, 0]  # Cost: 150
               >>> improved = operator.improve(tour, problem, np, max_iterations=50)
               >>> # improved cost: 120 (local optimum found in 15 iterations)
           """
           ...
   ```

2. **Validate Type Safety (15min)**
   ```bash
   mypy --strict code/src/protocols/strategy_protocols.py
   # Should pass with 0 errors
   ```

   **If errors:**
   - Check import paths (..data_models.problem, .backend)
   - Fix type hints (List[int] imported from typing)
   - Verify Protocol imported from typing

3. **Import Check (5min)**
   ```bash
   python -c "from code.src.protocols.strategy_protocols import NeighborStrategy, MutationOperator, CrossoverStrategy, ImprovementOperator"
   # Should succeed (no circular imports, no runtime errors)
   ```

4. **Commit (10min)**
   ```bash
   git add code/src/protocols/strategy_protocols.py
   git commit -m "feat(protocols): Add strategy protocols for M14.1

   - NeighborStrategy: SA neighbor generation
   - MutationOperator: GA mutation
   - CrossoverStrategy: GA recombination
   - ImprovementOperator: Post-processing local search

   All protocols include:
   - Comprehensive docstrings with examples
   - Semantic context (when to use)
   - Comparison with related protocols

   Type safety: mypy --strict passes
   Import safety: No circular dependencies (protocols/ is Layer 1)"
   ```

**Acceptance Criteria:**

- [ ] Protocol file created (200+ lines with docstrings)
- [ ] All 4 protocols defined (Neighbor, Mutation, Crossover, Improvement)
- [ ] mypy --strict passes
- [ ] Import check succeeds
- [ ] Docstrings explain semantic differences
- [ ] Examples included in docstrings
- [ ] File committed

**Update Task Log:**

```markdown
## M14.1.2: Implement Protocol Definitions
- **Status:** COMPLETE
- **Commits:** [GIT SHA]
- **Files Created:** strategy_protocols.py (210 lines)
- **Decisions:** 
  - NeighborStrategy uses `problem` parameter (for move evaluation)
  - MutationOperator does NOT use `problem` (blind variation)
  - ImprovementOperator has `max_iterations` parameter (flexibility)
```

**If Validation Fails:**

1. **mypy errors:** Check import paths, type hint syntax
2. **Import errors:** Verify layer 1 (protocols) doesn't import from algorithms/
3. **Semantic questions:** Document in task log, proceed with best judgment
4. **Stuck >30min:** Document blocker, move to M14.1.3 (tests)

---

### Task M14.1.3: Protocol Validation Tests (30min)

**Objective:** Verify protocols are complete and usable via dummy implementations

**Process:**

1. **Create Test File (20min)**

   **Create:** `tests/unit/protocols/test_strategy_protocols.py`

   ```python
   """
   Protocol validation tests.

   Strategy: Create dummy implementations that do NOTHING
   but satisfy protocol signatures. If mypy accepts them and
   tests pass, protocols are correctly defined.
   """

   import pytest
   import numpy as np
   from typing import List, Tuple

   from code.src.protocols.strategy_protocols import (
       NeighborStrategy,
       MutationOperator,
       CrossoverStrategy,
       ImprovementOperator
   )
   from code.src.data_models.problem import Problem


   # ===== DUMMY IMPLEMENTATIONS =====

   class DummyNeighbor:
       """Validates NeighborStrategy protocol compliance."""
       
       def generate_neighbor(
           self,
           current_tour: List[int],
           problem: Problem,
           xp
       ) -> List[int]:
           # Identity function (valid protocol implementation)
           return current_tour


   class DummyMutation:
       """Validates MutationOperator protocol compliance."""
       
       def mutate(self, individual: List[int], xp) -> List[int]:
           return individual


   class DummyCrossover:
       """Validates CrossoverStrategy protocol compliance."""
       
       def crossover(
           self,
           parent1: List[int],
           parent2: List[int],
           xp
       ) -> Tuple[List[int], List[int]]:
           return parent1, parent2


   class DummyImprovement:
       """Validates ImprovementOperator protocol compliance."""
       
       def improve(
           self,
           tour: List[int],
           problem: Problem,
           xp,
           max_iterations: int = 100
       ) -> List[int]:
           return tour


   # ===== PROTOCOL COMPLIANCE TESTS =====

   def test_neighbor_protocol_compliance():
       """Verify DummyNeighbor satisfies NeighborStrategy."""
       strategy: NeighborStrategy = DummyNeighbor()  # Type annotation validates protocol
       assert strategy is not None
       
       # Test call signature
       tour = [0, 1, 2, 3, 0]
       distances = np.array([[0, 1, 2, 3], [1, 0, 4, 5], [2, 4, 0, 6], [3, 5, 6, 0]])
       problem = Problem(distances=distances, dimension=4)
       
       neighbor = strategy.generate_neighbor(tour, problem, np)
       assert neighbor == tour  # Identity function


   def test_mutation_protocol_compliance():
       """Verify DummyMutation satisfies MutationOperator."""
       operator: MutationOperator = DummyMutation()
       assert operator is not None
       
       individual = [0, 1, 2, 3, 0]
       mutated = operator.mutate(individual, np)
       assert mutated == individual


   def test_crossover_protocol_compliance():
       """Verify DummyCrossover satisfies CrossoverStrategy."""
       strategy: CrossoverStrategy = DummyCrossover()
       assert strategy is not None
       
       parent1 = [0, 1, 2, 3, 0]
       parent2 = [0, 3, 2, 1, 0]
       child1, child2 = strategy.crossover(parent1, parent2, np)
       assert child1 == parent1
       assert child2 == parent2


   def test_improvement_protocol_compliance():
       """Verify DummyImprovement satisfies ImprovementOperator."""
       operator: ImprovementOperator = DummyImprovement()
       assert operator is not None
       
       tour = [0, 1, 2, 3, 0]
       distances = np.array([[0, 1, 2, 3], [1, 0, 4, 5], [2, 4, 0, 6], [3, 5, 6, 0]])
       problem = Problem(distances=distances, dimension=4)
       
       improved = operator.improve(tour, problem, np, max_iterations=10)
       assert improved == tour


   # ===== PROTOCOL METHOD SIGNATURE TESTS =====

   def test_neighbor_strategy_has_generate_neighbor_method():
       """Verify NeighborStrategy requires generate_neighbor method."""
       strategy = DummyNeighbor()
       assert hasattr(strategy, 'generate_neighbor')
       assert callable(strategy.generate_neighbor)


   def test_mutation_operator_has_mutate_method():
       """Verify MutationOperator requires mutate method."""
       operator = DummyMutation()
       assert hasattr(operator, 'mutate')
       assert callable(operator.mutate)


   def test_crossover_strategy_has_crossover_method():
       """Verify CrossoverStrategy requires crossover method."""
       strategy = DummyCrossover()
       assert hasattr(strategy, 'crossover')
       assert callable(strategy.crossover)


   def test_improvement_operator_has_improve_method():
       """Verify ImprovementOperator requires improve method."""
       operator = DummyImprovement()
       assert hasattr(operator, 'improve')
       assert callable(operator.improve)
   ```

2. **Run Tests (5min)**
   ```bash
   pytest tests/unit/protocols/test_strategy_protocols.py -v
   # Should pass all 8 tests
   ```

3. **Validate with mypy (3min)**
   ```bash
   mypy --strict tests/unit/protocols/test_strategy_protocols.py
   # Should pass (validates protocol usage)
   ```

4. **Commit (2min)**
   ```bash
   git add tests/unit/protocols/test_strategy_protocols.py
   git commit -m "test(protocols): Add protocol validation tests for M14.1

   - Dummy implementations verify protocol completeness
   - Type annotations validate mypy compliance
   - 8 tests cover all 4 protocols (compliance + method signatures)

   All tests pass: pytest -v
   Type safety: mypy --strict passes"
   ```

**Acceptance Criteria:**

- [ ] Test file created
- [ ] All 4 protocols have dummy implementations
- [ ] All 8 tests pass
- [ ] mypy --strict passes on test file
- [ ] File committed

**Update Task Log:**

```markdown
## M14.1: Protocol Definitions
- **Status:** COMPLETE
- **Commits:** [SHA1 protocols], [SHA2 tests]
- **Files Created:** 
  - strategy_protocols.py (210 lines)
  - test_strategy_protocols.py (150 lines)
- **Blockers:** None
- **Notes:** All protocols validated with dummy implementations
```

---

**M14.1 COMPLETE - Proceed to M14.2 (Shared Utilities)**

---

# PHASE 2: Shared Utilities (2-3h)

**Status:** ✅ COMPLETE - All tour operators implemented and functional

## M14.2: Extract Tour Operators

**Status:** ✅ COMPLETE - All 3 utilities exist and are used by strategies

**Prerequisites:**

- M14.1 complete (protocols defined)

**Context Files:**

- `code/src/algorithms/tour_operators/` directory (EXISTS)
- Used by: `code/src/algorithms/strategies/neighbor_strategies.py`

**Current Reality:**

- ✅ File EXISTS: `code/src/algorithms/tour_operators/swap_cities.py` or similar
- ✅ File EXISTS: `code/src/algorithms/tour_operators/insert_city.py` or similar
- ✅ File EXISTS: `code/src/algorithms/tour_operators/invert_segment.py` or similar
- ✅ Utilities IMPORTED by neighbor_strategies.py
- ✅ Functions operational and tested

**Objective:** Verify tour operator utilities are complete and properly structured

---

### Task M14.2.1: ✅ COMPLETE - Verify swap_cities Utility (15min)

**Original Task:** Create swap_cities utility  
**Current Reality:** Already implemented - needs verification only

**Verification Steps:**

1. **Locate Implementation (3min)**
   ```bash
   # Find which file contains swap_cities
   grep -r "def swap_cities" code/src/algorithms/tour_operators/
   ```

2. **Verify Function Signature (3min)**
   ```bash
   # Should show function signature
   grep -A 3 "def swap_cities" code/src/algorithms/tour_operators/*.py
   ```
   **Expected:** `def swap_cities(tour, i, j) -> List[int]` or similar

3. **Verify Usage in Strategies (3min)**
   ```bash
   # Check if neighbor_strategies.py imports it
   grep "swap_cities" code/src/algorithms/strategies/neighbor_strategies.py
   ```
   **Expected:** Import statement and usage in RandomSwapStrategy

4. **Test Functionality (6min)**
   ```bash
   # Quick smoke test
   python -c "
   from code.src.algorithms.tour_operators import swap_cities
   tour = [0, 1, 2, 3, 4, 0]
   result = swap_cities(tour, 1, 3)
   assert result == [0, 3, 2, 1, 4, 0], f'Expected [0,3,2,1,4,0], got {result}'
   print('✅ swap_cities works correctly')
   "
   ```

**Acceptance Criteria:**

- [x] swap_cities function exists
- [x] Function signature is correct
- [x] Used by neighbor_strategies.py
- [ ] Smoke test passes (verify)

**New Subtasks if Issues Found:**

- M14.2.1.1: Fix function signature if incorrect
- M14.2.1.2: Add missing docstring
- M14.2.1.3: Create unit tests if missing

---

### Task M14.2.2: ✅ COMPLETE - Verify insert_city Utility (15min)

**Original Task:** Create insert_city utility  
**Current Reality:** Already implemented - needs verification only

**Verification Steps:**

1. **Locate Implementation (3min)**
   ```bash
   grep -r "def insert_city" code/src/algorithms/tour_operators/
   ```

2. **Verify Function Signature (3min)**
   ```bash
   grep -A 3 "def insert_city" code/src/algorithms/tour_operators/*.py
   ```
   **Expected:** `def insert_city(tour, from_pos, to_pos) -> List[int]` or similar

3. **Verify Usage (3min)**
   ```bash
   grep "insert_city" code/src/algorithms/strategies/neighbor_strategies.py
   ```
   **Expected:** Used in RandomInsertionStrategy

4. **Test Functionality (6min)**
   ```bash
   python -c "
   from code.src.algorithms.tour_operators import insert_city
   tour = [0, 1, 2, 3, 4, 0]
   result = insert_city(tour, 1, 3)  # Move city at pos 1 to pos 3
   assert len(result) == len(tour), 'Length changed'
   assert result[0] == 0 and result[-1] == 0, 'Depot moved'
   print('✅ insert_city works correctly')
   "
   ```

**Acceptance Criteria:**

- [x] insert_city function exists
- [x] Function signature is correct
- [x] Used by neighbor_strategies.py
- [ ] Smoke test passes (verify)

---

### Task M14.2.3: ✅ COMPLETE - Verify invert_segment Utility (15min)

**Original Task:** Create invert_segment utility  
**Current Reality:** Already implemented - needs verification only

**Verification Steps:**

1. **Locate Implementation (3min)**
   ```bash
   grep -r "def invert_segment" code/src/algorithms/tour_operators/
   ```

2. **Verify Function Signature (3min)**
   ```bash
   grep -A 3 "def invert_segment" code/src/algorithms/tour_operators/*.py
   ```
   **Expected:** `def invert_segment(tour, i, j) -> List[int]` or similar

3. **Verify Usage (3min)**
   ```bash
   grep "invert_segment" code/src/algorithms/strategies/neighbor_strategies.py
   ```
   **Expected:** Used in Random2OptStrategy

4. **Test Functionality (6min)**
   ```bash
   python -c "
   from code.src.algorithms.tour_operators import invert_segment
   tour = [0, 1, 2, 3, 4, 5, 0]
   result = invert_segment(tour, 2, 4)  # Reverse segment [2,3,4]
   assert result == [0, 1, 4, 3, 2, 5, 0], f'Got {result}'
   print('✅ invert_segment works correctly')
   "
   ```

**Acceptance Criteria:**

- [x] invert_segment function exists
- [x] Function signature is correct
- [x] Used by neighbor_strategies.py (Random2OptStrategy)
- [ ] Smoke test passes (verify)

---

### Task M14.2.4: ✅ COMPLETE - Verify tour_operators **init**.py (5min)

**Original Task:** Update **init**.py  
**Current Reality:** Already done - needs verification only

**Verification Steps:**

1. **Check **init**.py Exists (2min)**
   ```bash
   ls -la code/src/algorithms/tour_operators/__init__.py
   ```

2. **Verify Exports (3min)**
   ```bash
   cat code/src/algorithms/tour_operators/__init__.py
   ```
   **Expected:** Exports swap_cities, insert_city, invert_segment

**Acceptance Criteria:**

- [x] **init**.py exists
- [ ] All 3 utilities exported (verify)
- [x] Module is importable

**PHASE 2 SUMMARY:**
All tour operator utilities implemented and functional. Just needs verification testing.

**Prerequisites:**

- M14.1 complete (protocols defined and tested)

**Context Files to Read:**

- `code/src/algorithms/metaheuristics/simulated_annealing.py` (lines 400-480, neighbor implementations)
- `code/src/algorithms/metaheuristics/genetic_algorithm.py` (lines 514-570, mutation implementations)

**Objective:** Extract duplicated tour manipulation logic into pure utility functions

**Key Insight:** SA and GA share 95% identical code for swap/insertion/inversion operations

---

### Task M14.2.1: swap_cities Utility (30min)

**Process:**

1. **Extract Logic (15min)**

   **Create:** `code/src/algorithms/tour_operators/swap.py`

   ```python
   """
   Swap two cities in a tour.

   Used by:
   - RandomSwapStrategy (SA neighbor generation)
   - SwapMutation (GA mutation)

   Complexity: O(1) - in-place swap
   """

   from typing import List


   def swap_cities(tour: List[int], i: int, j: int) -> List[int]:
       """
       Swap cities at positions i and j.
       
       Args:
           tour: Tour to modify [depot, c1, c2, ..., depot]
           i, j: Positions to swap (0 < i, j < len(tour)-1)
               - i, j should NOT be depot positions (0 or len-1)
               - Order doesn't matter (swap(i,j) == swap(j,i))
               
       Returns:
           Modified tour with tour[i] ↔ tour[j]
           
       Example:
           >>> tour = [0, 5, 3, 7, 2, 0]
           >>> swap_cities(tour, 1, 3)  # Swap cities 5 and 7
           [0, 7, 3, 5, 2, 0]
           
       Note:
           Creates NEW list (does not modify in-place).
           For in-place version, use tour[i], tour[j] = tour[j], tour[i]
       """
       new_tour = tour.copy()
       new_tour[i], new_tour[j] = new_tour[j], new_tour[i]
       return new_tour
   ```

2. **Create Tests (10min)**

   **Create:** `tests/unit/tour_operators/test_swap.py`

   ```python
   """Tests for swap_cities utility."""

   import pytest
   from code.src.algorithms.tour_operators.swap import swap_cities


   def test_swap_cities_basic():
       """Test basic swap functionality."""
       tour = [0, 1, 2, 3, 4, 0]
       result = swap_cities(tour, 1, 3)
       assert result == [0, 3, 2, 1, 4, 0]


   def test_swap_cities_preserves_depot():
       """Depot positions should not change."""
       tour = [0, 5, 3, 7, 2, 0]
       result = swap_cities(tour, 1, 3)
       assert result[0] == 0  # First depot preserved
       assert result[-1] == 0  # Last depot preserved


   def test_swap_cities_does_not_modify_original():
       """Should return new list, not modify original."""
       tour = [0, 1, 2, 3, 0]
       original = tour.copy()
       result = swap_cities(tour, 1, 2)
       assert tour == original  # Original unchanged


   def test_swap_same_positions():
       """Swapping same position should return unchanged tour."""
       tour = [0, 1, 2, 3, 0]
       result = swap_cities(tour, 2, 2)
       assert result == tour


   def test_swap_order_independence():
       """swap(i,j) should equal swap(j,i)."""
       tour = [0, 1, 2, 3, 4, 0]
       result1 = swap_cities(tour, 1, 3)
       result2 = swap_cities(tour, 3, 1)
       assert result1 == result2
   ```

3. **Run Tests (3min)**
   ```bash
   pytest tests/unit/tour_operators/test_swap.py -v
   # Should pass all 5 tests
   ```

4. **Commit (2min)**
   ```bash
   git add code/src/algorithms/tour_operators/swap.py tests/unit/tour_operators/test_swap.py
   git commit -m "feat(tour_operators): Add swap_cities utility for M14.2

   - Pure function: swap two cities in tour
   - Returns new list (does not modify in-place)
   - 5 tests: basic, depot preservation, immutability, edge cases

   Will be used by:
   - RandomSwapStrategy (SA)
   - SwapMutation (GA)"
   ```

**Acceptance Criteria:**

- [ ] swap.py created with docstring
- [ ] All 5 tests pass
- [ ] Does not modify original tour (immutability)
- [ ] File committed

---

### Task M14.2.2: insert_city Utility (30min)

**Process:**

1. **Extract Logic (15min)**

   **Create:** `code/src/algorithms/tour_operators/insertion.py`

   ```python
   """
   Remove city from tour and reinsert at different position.

   Used by:
   - RandomInsertionStrategy (SA neighbor generation)
   - InsertionMutation (GA mutation)

   Complexity: O(n) - list slicing and concatenation
   """

   from typing import List


   def insert_city(tour: List[int], from_pos: int, to_pos: int) -> List[int]:
       """
       Remove city at from_pos and insert at to_pos.
       
       Args:
           tour: Tour to modify [depot, c1, c2, ..., depot]
           from_pos: Position to remove city from (0 < from_pos < len-1)
           to_pos: Position to insert city at (0 < to_pos < len-1)
               - Positions are depot-exclusive (cannot move depot)
               
       Returns:
           Modified tour with city moved
           
       Example:
           >>> tour = [0, 5, 3, 7, 2, 0]
           >>> insert_city(tour, 1, 3)  # Move city 5 to position 3
           [0, 3, 7, 5, 2, 0]
           # Removed 5, shifted [3,7] left, inserted 5 before 2
           
       Algorithm:
           1. Extract city at from_pos
           2. Remove from_pos from tour
           3. Insert city at to_pos
       """
       new_tour = tour.copy()
       city = new_tour.pop(from_pos)
       new_tour.insert(to_pos, city)
       return new_tour
   ```

2. **Create Tests (10min)**

   **Create:** `tests/unit/tour_operators/test_insertion.py`

   ```python
   """Tests for insert_city utility."""

   import pytest
   from code.src.algorithms.tour_operators.insertion import insert_city


   def test_insert_city_basic():
       """Test basic insertion functionality."""
       tour = [0, 1, 2, 3, 4, 0]
       result = insert_city(tour, 1, 3)  # Move 1 to position 3
       assert result == [0, 2, 3, 1, 4, 0]


   def test_insert_city_forward():
       """Insert city forward in tour."""
       tour = [0, 5, 3, 7, 2, 0]
       result = insert_city(tour, 1, 3)  # Move 5 after 7
       assert result == [0, 3, 7, 5, 2, 0]


   def test_insert_city_backward():
       """Insert city backward in tour."""
       tour = [0, 5, 3, 7, 2, 0]
       result = insert_city(tour, 3, 1)  # Move 7 before 3
       assert result == [0, 7, 5, 3, 2, 0]


   def test_insert_city_preserves_depot():
       """Depot should remain at first and last positions."""
       tour = [0, 1, 2, 3, 0]
       result = insert_city(tour, 1, 2)
       assert result[0] == 0
       assert result[-1] == 0


   def test_insert_city_does_not_modify_original():
       """Should return new list."""
       tour = [0, 1, 2, 3, 0]
       original = tour.copy()
       result = insert_city(tour, 1, 2)
       assert tour == original


   def test_insert_same_position():
       """Inserting at same position should return unchanged tour."""
       tour = [0, 1, 2, 3, 0]
       result = insert_city(tour, 2, 2)
       assert result == tour
   ```

3. **Run Tests (3min)**
   ```bash
   pytest tests/unit/tour_operators/test_insertion.py -v
   # Should pass all 6 tests
   ```

4. **Commit (2min)**
   ```bash
   git add code/src/algorithms/tour_operators/insertion.py tests/unit/tour_operators/test_insertion.py
   git commit -m "feat(tour_operators): Add insert_city utility for M14.2

   - Remove city from one position, insert at another
   - Handles forward and backward insertion
   - 6 tests: basic, forward/backward, depot, immutability, edge cases"
   ```

**Acceptance Criteria:**

- [ ] insertion.py created
- [ ] All 6 tests pass
- [ ] Handles forward and backward insertion
- [ ] File committed

---

### Task M14.2.3: invert_segment Utility (30min)

**Process:**

1. **Extract Logic (15min)**

   **Create:** `code/src/algorithms/tour_operators/inversion.py`

   ```python
   """
   Reverse a segment of the tour (2-opt move operation).

   Used by:
   - Random2OptStrategy (SA neighbor generation)
   - InversionMutation (GA mutation)
   - TwoOptCPU/GPU (improvement operators)

   Complexity: O(k) where k = j - i (segment length)

   References:
   - Croes (1958): "A method for solving traveling salesman problems"
   - Lin & Kernighan (1973): "An effective heuristic for TSP"
   """

   from typing import List


   def invert_segment(tour: List[int], i: int, j: int) -> List[int]:
       """
       Reverse tour segment between positions i and j (inclusive).
       
       Args:
           tour: Tour to modify [depot, c1, c2, ..., depot]
           i, j: Segment boundaries (0 < i < j < len-1)
               - Segment tour[i:j+1] will be reversed
               - Depot positions excluded
               
       Returns:
           Modified tour with reversed segment
           
       Example:
           >>> tour = [0, 1, 2, 3, 4, 5, 0]
           >>> invert_segment(tour, 2, 4)  # Reverse [2,3,4]
           [0, 1, 4, 3, 2, 5, 0]
           
       2-opt Interpretation:
           Reversing [i, j] breaks edges (i-1, i) and (j, j+1),
           adds edges (i-1, j) and (i, j+1).
           
       Algorithm:
           tour[:i] + reversed(tour[i:j+1]) + tour[j+1:]
       """
       if i > j:
           i, j = j, i  # Ensure i < j
       
       new_tour = tour[:i] + tour[i:j+1][::-1] + tour[j+1:]
       return new_tour
   ```

2. **Create Tests (10min)**

   **Create:** `tests/unit/tour_operators/test_inversion.py`

   ```python
   """Tests for invert_segment utility."""

   import pytest
   from code.src.algorithms.tour_operators.inversion import invert_segment


   def test_invert_segment_basic():
       """Test basic segment reversal."""
       tour = [0, 1, 2, 3, 4, 5, 0]
       result = invert_segment(tour, 2, 4)
       assert result == [0, 1, 4, 3, 2, 5, 0]


   def test_invert_segment_full_tour():
       """Reverse entire middle section."""
       tour = [0, 1, 2, 3, 4, 0]
       result = invert_segment(tour, 1, 4)
       assert result == [0, 4, 3, 2, 1, 0]


   def test_invert_segment_two_cities():
       """Reversing two cities is equivalent to swap."""
       tour = [0, 1, 2, 3, 0]
       result = invert_segment(tour, 1, 2)
       assert result == [0, 2, 1, 3, 0]


   def test_invert_segment_single_city():
       """Reversing single city should return unchanged."""
       tour = [0, 1, 2, 3, 0]
       result = invert_segment(tour, 2, 2)
       assert result == tour


   def test_invert_segment_preserves_depot():
       """Depot should remain at first and last."""
       tour = [0, 5, 3, 7, 2, 0]
       result = invert_segment(tour, 1, 3)
       assert result[0] == 0
       assert result[-1] == 0


   def test_invert_segment_order_independence():
       """invert(i,j) should equal invert(j,i)."""
       tour = [0, 1, 2, 3, 4, 0]
       result1 = invert_segment(tour, 1, 3)
       result2 = invert_segment(tour, 3, 1)
       assert result1 == result2


   def test_invert_segment_does_not_modify_original():
       """Should return new list."""
       tour = [0, 1, 2, 3, 0]
       original = tour.copy()
       result = invert_segment(tour, 1, 2)
       assert tour == original
   ```

3. **Run Tests (3min)**
   ```bash
   pytest tests/unit/tour_operators/test_inversion.py -v
   # Should pass all 7 tests
   ```

4. **Commit (2min)**
   ```bash
   git add code/src/algorithms/tour_operators/inversion.py tests/unit/tour_operators/test_inversion.py
   git commit -m "feat(tour_operators): Add invert_segment utility for M14.2

   - Reverse tour segment (2-opt move operation)
   - Handles edge cases: single city, two cities, full tour
   - 7 tests: basic, edge cases, depot, immutability, order independence

   Used by 2-opt strategies and mutations"
   ```

**Acceptance Criteria:**

- [ ] inversion.py created
- [ ] All 7 tests pass
- [ ] Handles i > j (auto-swap)
- [ ] File committed

---

### Task M14.2.4: Update tour_operators **init**.py (10min)

**Process:**

1. **Export Utilities (5min)**

   **Edit:** `code/src/algorithms/tour_operators/__init__.py`

   ```python
   """
   Tour operators (city-level mutations).

   Shared utilities for SA neighbor methods and GA mutations.
   Pure functions - take tour, return modified tour.

   Used by:
   - strategies/neighbor_strategies.py (SA)
   - strategies/mutation_strategies.py (GA)
   """

   from .swap import swap_cities
   from .insertion import insert_city
   from .inversion import invert_segment

   __all__ = [
       "swap_cities",
       "insert_city",
       "invert_segment",
   ]
   ```

2. **Test Imports (3min)**
   ```bash
   python -c "from code.src.algorithms.tour_operators import swap_cities, insert_city, invert_segment"
   # Should succeed
   ```

3. **Commit (2min)**
   ```bash
   git add code/src/algorithms/tour_operators/__init__.py
   git commit -m "feat(tour_operators): Export utilities in __init__ for M14.2"
   ```

**Acceptance Criteria:**

- [ ] **init**.py exports all 3 utilities
- [ ] Import check succeeds
- [ ] File committed

---

**Update Task Log:**

```markdown
## M14.2: Shared Utilities
- **Status:** COMPLETE
- **Commits:** [SHA swap], [SHA insertion], [SHA inversion], [SHA init]
- **Files Created:**
  - swap.py (30 lines + 5 tests)
  - insertion.py (35 lines + 6 tests)
  - inversion.py (40 lines + 7 tests)
- **Total Test Coverage:** 18 tests, all passing
- **Notes:** DRY violation resolved - SA and GA now share utilities
```

---

**M14.2 COMPLETE - Proceed to M14.3 (SA Strategy Extraction)**

---

# PHASE 3: SA Strategy Extraction (3-4h)

**Status:** ⚠️ MOSTLY COMPLETE - Strategies exist, SA refactored BUT needs 4 fixes

## M14.3: Extract SA Neighbor Strategies

**Status:** ⚠️ COMPLETE with ISSUES - All strategies implemented, SA refactored, but needs corrections

**Prerequisites:**

- M14.1 complete (protocols) ✅
- M14.2 complete (tour operators) ✅

**Context Files:**

- `code/src/algorithms/strategies/neighbor_strategies.py` (EXISTS - 278 lines, 3 strategies)
- `code/src/algorithms/metaheuristics/simulated_annealing.py` (EXISTS - 488 lines, REFACTORED)

**Current Reality:**

- ✅ RandomSwapStrategy EXISTS and functional
- ✅ RandomInsertionStrategy EXISTS and functional
- ✅ Random2OptStrategy EXISTS and functional
- ✅ SimulatedAnnealing REFACTORED to accept neighbor_strategy parameter
- ⚠️ SA has classification error (Line 8 says "P-Data" but is actually "S-Task")
- ⚠️ SA missing backend parameter in **init**
- ⚠️ SA missing GPU guardrails (_check_vram_capacity pattern)
- ⚠️ SA missing buffer reuse pattern

**Objective:** Verify strategy implementations and FIX SA issues

---

### Task M14.3.1: ✅ COMPLETE - Verify RandomSwapStrategy (15min)

**Original Task:** Create RandomSwapStrategy  
**Current Reality:** Already implemented - needs verification only

**Verification Steps:**

1. **Verify Implementation Exists (3min)**
   ```bash
   grep -A 20 "class RandomSwapStrategy" code/src/algorithms/strategies/neighbor_strategies.py
   ```

2. **Test Functionality (7min)**
   ```bash
   python -c "
   import numpy as np
   from code.src.algorithms.strategies.neighbor_strategies import RandomSwapStrategy
   from code.src.data_models.problem import Problem
   
   distances = np.array([[0, 10, 15], [10, 0, 20], [15, 20, 0]])
   problem = Problem(distances=distances, dimension=3)
   strategy = RandomSwapStrategy()
   tour = [0, 1, 2, 0]
   neighbor = strategy.generate_neighbor(tour, problem, np)
   
   assert len(neighbor) == len(tour), 'Length mismatch'
   assert neighbor[0] == 0 and neighbor[-1] == 0, 'Depot moved'
   assert set(neighbor) == set(tour), 'Cities changed'
   print('✅ RandomSwapStrategy works')
   "
   ```

3. **Verify Protocol Compliance (5min)**
   ```bash
   # Check that generate_neighbor signature matches protocol
   grep -A 5 "def generate_neighbor" code/src/algorithms/strategies/neighbor_strategies.py | head -6
   ```

**Acceptance Criteria:**

- [x] RandomSwapStrategy class exists
- [ ] Smoke test passes (verify)
- [ ] Protocol compliant (verify)

---

### Task M14.3.2: ✅ COMPLETE - Verify RandomInsertionStrategy (15min)

**Original Task:** Create RandomInsertionStrategy  
**Current Reality:** Already implemented - needs verification only

**Verification Steps:**

1. **Verify Implementation (3min)**
   ```bash
   grep -A 20 "class RandomInsertionStrategy" code/src/algorithms/strategies/neighbor_strategies.py
   ```

2. **Test Functionality (7min)**
   ```bash
   python -c "
   import numpy as np
   from code.src.algorithms.strategies.neighbor_strategies import RandomInsertionStrategy
   from code.src.data_models.problem import Problem
   
   distances = np.array([[0, 10, 15], [10, 0, 20], [15, 20, 0]])
   problem = Problem(distances=distances, dimension=3)
   strategy = RandomInsertionStrategy()
   tour = [0, 1, 2, 0]
   neighbor = strategy.generate_neighbor(tour, problem, np)
   
   assert len(neighbor) == len(tour), 'Length changed'
   assert neighbor[0] == 0 and neighbor[-1] == 0, 'Depot moved'
   print('✅ RandomInsertionStrategy works')
   "
   ```

**Acceptance Criteria:**

- [x] RandomInsertionStrategy class exists
- [ ] Smoke test passes (verify)

---

### Task M14.3.3: ✅ COMPLETE - Verify Random2OptStrategy (15min)

**Original Task:** Create Random2OptStrategy  
**Current Reality:** Already implemented - needs verification only

**Verification Steps:**

1. **Verify Implementation (3min)**
   ```bash
   grep -A 20 "class Random2OptStrategy" code/src/algorithms/strategies/neighbor_strategies.py
   ```

2. **Test Functionality (7min)**
   ```bash
   python -c "
   import numpy as np
   from code.src.algorithms.strategies.neighbor_strategies import Random2OptStrategy
   from code.src.data_models.problem import Problem
   
   distances = np.array([[0, 10, 15, 20], [10, 0, 25, 30], [15, 25, 0, 35], [20, 30, 35, 0]])
   problem = Problem(distances=distances, dimension=4)
   strategy = Random2OptStrategy()
   tour = [0, 1, 2, 3, 0]
   neighbor = strategy.generate_neighbor(tour, problem, np)
   
   assert len(neighbor) == len(tour), 'Length changed'
   assert neighbor[0] == 0 and neighbor[-1] == 0, 'Depot moved'
   print('✅ Random2OptStrategy works')
   "
   ```

**Acceptance Criteria:**

- [x] Random2OptStrategy class exists
- [ ] Smoke test passes (verify)

---

### Task M14.3.4: ⚠️ NEEDS FIXES - Refactor SimulatedAnnealing (NOW 5 SUBTASKS)

**Original Task:** Refactor SA to accept strategy parameter  
**Current Reality:** ALREADY REFACTORED but has 4 critical issues that need fixing

> [!CRITICAL]
> **SA Classification Error & Missing Features**
>
> The SimulatedAnnealing class at `code/src/algorithms/metaheuristics/simulated_annealing.py` has:
>
> 1. **Line 8:** Says "Class: P-Data (Parallel Data)" but implementation is actually "S-Task (Sequential Task)"
> 2. **Line 123:** `__init__` is missing `backend` parameter (documented in architecture doc Section 2.1)
> 3. **Missing:** GPU guardrails (`_check_vram_capacity()` pattern from architecture doc)
> 4. **Missing:** Buffer reuse pattern (documented in architecture doc Section 2.2)
>
> **These MUST be fixed before proceeding to GA refactor.**
>
> See: `documentation/architecture/METAHEURISTIC_ARCHITECTURE_DECISIONS.md`
>
> - Section 2.1: GPU VRAM Guardrails
> - Section 2.2: Buffer Reuse Pattern

**Main Verification (10min):**

1. **Verify Refactor Complete (5min)**
   ```bash
   # Check that __init__ has neighbor_strategy parameter
   grep -A 10 "def __init__" code/src/algorithms/metaheuristics/simulated_annealing.py | head -15
   ```
   **Expected:** `neighbor_strategy: NeighborStrategy` parameter present

2. **Verify Strategy Usage (5min)**
   ```bash
   # Check that neighbor_strategy is called, not hardcoded methods
   grep "self.neighbor_strategy.generate_neighbor" code/src/algorithms/metaheuristics/simulated_annealing.py
   ```
   **Expected:** At least one usage in solve() method

**Acceptance Criteria for Main Task:**

- [x] SA **init** accepts neighbor_strategy parameter
- [x] SA uses strategy.generate_neighbor() instead of _neighbor_* methods
- [ ] SA classification corrected (subtask M14.3.4.1)
- [ ] SA has backend parameter (subtask M14.3.4.2)
- [ ] GPU guardrails implemented (subtask M14.3.4.3)
- [ ] Buffer reuse implemented (subtask M14.3.4.4)

---

#### **Subtask M14.3.4.1: Fix SA Classification (P-Data → S-Task) (10min)**

**Issue:** Line 8 of simulated_annealing.py says "P-Data" but SA is actually "S-Task"

**Classification Details:**

- **P-Data (Parallel Data)**: Multiple independent solutions processed in parallel (future feature)
- **S-Task (Sequential Task)**: Single solution trajectory (CURRENT implementation)

**Fix:**

1. **Update Docstring (5min)**
   ```bash
   # Open file
   code code/src/algorithms/metaheuristics/simulated_annealing.py
   ```

   Change line 8 FROM:
   ```python
       - Class: P-Data (Parallel Data)
   ```

   TO:
   ```python
       - Class: S-Task (Sequential Task)
       - Note: P-Data multistart variant planned for M18 (Streaming Architecture)
   ```

2. **Add Future Work Note (3min)**

   After the classification section, add:
   ```python
   Future Extensions:
       - P-Data Variant (M18): Parallel multistart with stream compaction
         Reference: See METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 4 (Streaming)
         Hardware: Requires CUDA streams + unified memory
         Benefit: Process multiple trajectories simultaneously on GPU
   ```

3. **Verify Change (2min)**
   ```bash
   grep -A 5 "Algorithm Classification" code/src/algorithms/metaheuristics/simulated_annealing.py
   ```

**Acceptance Criteria:**

- [ ] Line 8 changed to "S-Task (Sequential Task)"
- [ ] Future P-Data work noted
- [ ] Reference to architecture doc added

**Commit:**

```bash
git add code/src/algorithms/metaheuristics/simulated_annealing.py
git commit -m "fix(sa): Correct classification from P-Data to S-Task (M14.3.4.1)

Current implementation is Sequential Task (single trajectory).
P-Data multistart variant is future work (M18 Streaming Architecture).

Ref: METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 4"
```

---

#### **Subtask M14.3.4.2: Add Backend Parameter to SA.**init** (20min)**

**Issue:** SA missing `backend` parameter, relies on implicit backend from ProblemContext

**Requirement:** From architecture doc Section 2.1, algorithms should have explicit backend control

**Fix:**

1. **Update **init** Signature (5min)**

   Change FROM (line ~123):
   ```python
   def __init__(
       self,
       neighbor_strategy: NeighborStrategy,
       callback: Optional["ProgressCallback"] = None,
   ):
   ```

   TO:
   ```python
   def __init__(
       self,
       neighbor_strategy: NeighborStrategy,
       backend: str = "numpy",
       callback: Optional["ProgressCallback"] = None,
   ):
   ```

2. **Store Backend (2min)**

   After `self.neighbor_strategy = neighbor_strategy`, add:
   ```python
       self.backend = backend
       self.backend_module = get_backend(backend)  # Import from protocols.backend
   ```

3. **Add Import (2min)**

   At top of file, add:
   ```python
   from ..protocols.backend import get_backend
   ```

4. **Update Docstring (5min)**

   In **init** docstring Args section, add:
   ```python
       backend: Backend to use ("numpy", "numba", or "cupy")
           - "numpy": CPU (default, safest, good for n<1000)
           - "numba": CPU with JIT (faster for large n)
           - "cupy": GPU (requires CUDA, best for n>1000)
           See: Backend Configuration Architecture section in M14_M15_DETAILED_TASKS.md
   ```

5. **Update Example (3min)**

   In docstring Example section, add backend usage:
   ```python
       >>> # GPU SA (requires CUDA)
       >>> sa = SimulatedAnnealing(
       ...     neighbor_strategy=RandomSwapStrategy(),
       ...     backend="cupy"
       ... )
   ```

6. **Test (3min)**
   ```bash
   python -c "
   from code.src.algorithms.metaheuristics.simulated_annealing import SimulatedAnnealing
   from code.src.algorithms.strategies.neighbor_strategies import RandomSwapStrategy
   
   sa = SimulatedAnnealing(neighbor_strategy=RandomSwapStrategy(), backend='numpy')
   assert hasattr(sa, 'backend'), 'Missing backend attribute'
   assert sa.backend == 'numpy', 'Backend not stored'
   print('✅ Backend parameter works')
   "
   ```

**Acceptance Criteria:**

- [ ] backend parameter added to **init**
- [ ] self.backend and self.backend_module stored
- [ ] Import added
- [ ] Docstring updated
- [ ] Example added
- [ ] Smoke test passes

**Commit:**

```bash
git add code/src/algorithms/metaheuristics/simulated_annealing.py
git commit -m "feat(sa): Add explicit backend parameter to __init__ (M14.3.4.2)

Enables explicit backend control (numpy/numba/cupy) instead of
relying on implicit backend from ProblemContext.

Ref: METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 2.1
Ref: Backend Configuration Architecture (M14_M15_DETAILED_TASKS.md)"
```

---

#### **Subtask M14.3.4.3: Implement GPU VRAM Guardrails (30min)**

**Issue:** SA doesn't check VRAM capacity before using CuPy backend

**Requirement:** From architecture doc Section 2.1, implement _check_vram_capacity() pattern

**Fix:**

1. **Add VRAM Check Method (15min)**

   Add new method to SimulatedAnnealing class:
   ```python
   def _check_vram_capacity(self, problem: Problem) -> None:
       """
       Check if GPU has sufficient VRAM for problem size.
       
       Raises:
           RuntimeError: If VRAM insufficient for problem
       
       Memory Requirements (Simulated Annealing):
           - Distance matrix: n² × 8 bytes (float64)
           - Current tour: (n+1) × 4 bytes (int32)
           - Neighbor tour: (n+1) × 4 bytes (int32)
           - Working buffers: ~50 MB overhead
       
       Example (n=3000):
           - Distances: 3000² × 8 = 72 MB
           - Tours: 2 × 3001 × 4 = 24 KB
           - Total: ~72.02 MB + 50 MB overhead = ~122 MB
       
       GTX 1050 Mobile Constraint:
           - Total VRAM: 4 GB
           - Available: ~3.5 GB (after OS/driver)
           - Safe limit: 3000 MB per algorithm
       
       Ref: METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 2.1
       """
       if self.backend != "cupy":
           return  # Only check for GPU backend
       
       import cupy as cp
       
       n = problem.dimension
       distance_matrix_bytes = n * n * 8  # float64
       tour_bytes = 2 * (n + 1) * 4  # Two tours, int32
       overhead_bytes = 50 * 1024 * 1024  # 50 MB
       
       required_bytes = distance_matrix_bytes + tour_bytes + overhead_bytes
       required_mb = required_bytes / (1024 * 1024)
       
       # Get available VRAM
       mempool = cp.get_default_memory_pool()
       device = cp.cuda.Device()
       total_bytes = device.mem_info[1]  # Total VRAM
       used_bytes = mempool.used_bytes()
       available_bytes = total_bytes - used_bytes
       available_mb = available_bytes / (1024 * 1024)
       
       if required_bytes > available_bytes:
           raise RuntimeError(
               f"Insufficient VRAM for SA with n={n} cities.\n"
               f"Required: {required_mb:.1f} MB\n"
               f"Available: {available_mb:.1f} MB\n"
               f"Suggestion: Use backend='numpy' or reduce problem size"
           )
   ```

2. **Call in solve() Method (5min)**

   At the start of solve() method, add:
   ```python
   def solve(self, problem: Problem) -> Solution:
       """..."""
       # GPU VRAM check (GTX 1050 Mobile constraint)
       self._check_vram_capacity(problem)
       
       # Rest of solve() method...
   ```

3. **Add Import (2min)**

   At top of file (only if cupy imported conditionally):
   ```python
   # Conditional import handled in _check_vram_capacity method
   ```

4. **Test with Mock (8min)**

   Create quick test:
   ```bash
   python -c "
   import numpy as np
   from code.src.algorithms.metaheuristics.simulated_annealing import SimulatedAnnealing
   from code.src.algorithms.strategies.neighbor_strategies import RandomSwapStrategy
   from code.src.data_models.problem import Problem
   
   # Test 1: numpy backend (should not check VRAM)
   sa_cpu = SimulatedAnnealing(neighbor_strategy=RandomSwapStrategy(), backend='numpy')
   distances = np.random.rand(100, 100)
   problem = Problem(distances=distances, dimension=100)
   # Should not raise (numpy doesn't check VRAM)
   
   print('✅ VRAM guardrails added (test with cupy separately if available)')
   "
   ```

**Acceptance Criteria:**

- [ ] _check_vram_capacity method added
- [ ] Method called at start of solve()
- [ ] Raises RuntimeError if VRAM insufficient
- [ ] Only checks when backend="cupy"
- [ ] Memory calculation documented

**Commit:**

```bash
git add code/src/algorithms/metaheuristics/simulated_annealing.py
git commit -m "feat(sa): Add GPU VRAM guardrails (M14.3.4.3)

Implement _check_vram_capacity() to prevent CUDA out-of-memory errors.
Checks VRAM before running SA on GPU (GTX 1050 Mobile: 4GB limit).

Memory calculation:
- Distance matrix: n² × 8 bytes
- Tours: 2 × (n+1) × 4 bytes
- Overhead: ~50 MB

Ref: METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 2.1"
```

---

#### **Subtask M14.3.4.4: Implement Buffer Reuse Pattern (25min)**

**Issue:** SA doesn't reuse buffers for neighbor generation (creates new lists each iteration)

**Requirement:** From architecture doc Section 2.2, reuse buffers to reduce allocation overhead

**Note:** This is OPTIONAL OPTIMIZATION. If time-constrained, DEFER to M16 (Performance Optimization).

**Fix (if proceeding):**

1. **Add Buffer Initialization (10min)**

   In solve() method, after initial solution:
   ```python
   # Initialize reusable buffers (avoid per-iteration allocation)
   neighbor_buffer = current_tour.copy()  # Reusable neighbor tour
   ```

2. **Pass Buffer to Strategy (8min)**

   Modify generate_neighbor call to accept optional buffer:
   ```python
   # Generate neighbor (reuse buffer if strategy supports it)
   if hasattr(self.neighbor_strategy, 'generate_neighbor_inplace'):
       self.neighbor_strategy.generate_neighbor_inplace(
           current_tour, neighbor_buffer, problem, xp
       )
       neighbor_tour = neighbor_buffer
   else:
       # Fallback: allocate new (backward compatible)
       neighbor_tour = self.neighbor_strategy.generate_neighbor(
           current_tour, problem, xp
       )
   ```

3. **Document (5min)**

   Add comment:
   ```python
   # Buffer Reuse Pattern (M14.3.4.4):
   # Check if strategy supports in-place generation.
   # Reduces allocation overhead from O(iterations) to O(1).
   # Backward compatible: falls back to allocation if not supported.
   # Ref: METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 2.2
   ```

4. **Test (2min)**
   ```bash
   # Should work with existing strategies (no in-place support yet)
   python -c "
   import numpy as np
   from code.src.algorithms.metaheuristics.simulated_annealing import SimulatedAnnealing
   from code.src.algorithms.strategies.neighbor_strategies import RandomSwapStrategy
   from code.src.data_models.problem import Problem
   
   sa = SimulatedAnnealing(neighbor_strategy=RandomSwapStrategy())
   distances = np.random.rand(20, 20)
   problem = Problem(distances=distances, dimension=20)
   # Should run without errors (uses fallback allocation)
   print('✅ Buffer reuse pattern added (strategies need update for full benefit)')
   "
   ```

**Acceptance Criteria:**

- [ ] Buffer initialized in solve()
- [ ] Check for generate_neighbor_inplace support
- [ ] Fallback to allocation if not supported
- [ ] Documented with reference to architecture doc

**Commit:**

```bash
git add code/src/algorithms/metaheuristics/simulated_annealing.py
git commit -m "perf(sa): Add buffer reuse pattern (M14.3.4.4)

Check if strategy supports in-place neighbor generation.
Reduces allocation overhead on GPU from O(iterations) to O(1).

Backward compatible: falls back to allocation if strategy
doesn't implement generate_neighbor_inplace.

Ref: METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 2.2"
```

---

### Task M14.3.5: SA Integration Test (30min)

**Status:** ❓ NEEDS VERIFICATION - Check if test exists and passes after fixes

**Verification Steps:**

1. **Check if Test Exists (5min)**
   ```bash
   find tests/ -name "*simulated*" -o -name "*sa_*"
   ```

2. **If Exists, Run Test (10min)**
   ```bash
   uv run pytest tests/integration/*simulated* -v
   # or
   uv run pytest tests/integration/*sa* -v
   ```

3. **If Doesn't Exist, Create Basic Test (15min)**

   **Create:** `tests/integration/test_sa_strategy_integration.py`

   ```python
   """Integration test for SA with strategies."""
   
   import pytest
   import numpy as np
   from code.src.algorithms.metaheuristics.simulated_annealing import SimulatedAnnealing
   from code.src.algorithms.strategies.neighbor_strategies import (
       RandomSwapStrategy,
       RandomInsertionStrategy,
       Random2OptStrategy
   )
   from code.src.data_models.problem import Problem
   
   
   @pytest.fixture
   def small_problem():
       """Small TSP for fast testing."""
       np.random.seed(42)
       distances = np.random.rand(10, 10)
       np.fill_diagonal(distances, 0)
       return Problem(distances=distances, dimension=10)
   
   
   @pytest.mark.parametrize("strategy_class", [
       RandomSwapStrategy,
       RandomInsertionStrategy,
       Random2OptStrategy
   ])
   def test_sa_with_strategies(small_problem, strategy_class):
       """Test SA works with all neighbor strategies."""
       strategy = strategy_class()
       sa = SimulatedAnnealing(neighbor_strategy=strategy, backend="numpy")
       sa.set_params(max_iterations=100, initial_temp=100)
       
       solution = sa.solve(small_problem)
       
       assert solution is not None
       assert len(solution.tour) == small_problem.dimension + 1
       assert solution.tour[0] == 0  # Depot
       assert solution.tour[-1] == 0
       assert solution.cost > 0
   ```

4. **Run New Test (if created)**
   ```bash
   uv run pytest tests/integration/test_sa_strategy_integration.py -v
   ```

**Acceptance Criteria:**

- [ ] Integration test exists
- [ ] Test covers all 3 strategies
- [ ] All tests pass
- [ ] SA solves small problem successfully

**PHASE 3 SUMMARY:**

- ✅ All 3 neighbor strategies implemented and functional
- ✅ SA refactored to use strategies
- ⚠️ 4 subtasks needed to fix SA issues (classification, backend, guardrails, buffers)
- After fixes, ready to proceed to PHASE 4 (GA refactor)

**MANDATORY REQUIREMENT:** All strategies MUST have explicit `__init__` method.

- Stateless strategies: `def __init__(self) -> None: pass`
- Stateful strategies: `def __init__(self, param: Type) -> None: self.param = param`
- Rationale: Future-proofing, clarity, singleton pattern compatibility

**Process:**

1. **Create Strategy (25min)**

   **Create:** `code/src/algorithms/strategies/neighbor_strategies.py`

   ```python
   """
   Neighbor generation strategies for Simulated Annealing.

   Implements NeighborStrategy protocol for SA local search.
   Each strategy generates a SINGLE neighbor (not exhaustive).

   Usage:
       from code.src.algorithms.strategies import neighbor_strategies
       strategy = neighbor_strategies.RandomSwapStrategy()
       neighbor = strategy.generate_neighbor(tour, problem, np)
   """

   from typing import List
   from ...protocols.strategy_protocols import NeighborStrategy
   from ...protocols.backend import BackendModule
   from ...data_models.problem import Problem
   from ..tour_operators import swap_cities


   class RandomSwapStrategy:
       """
       Generate neighbor by swapping two random cities.
       
       Complexity: O(1) for move generation
       Search Space: n(n-1)/2 possible swaps for n-city TSP
       
       Characteristics:
           - High diversity (large neighborhood)
           - No problem knowledge (blind search)
           - Fast generation (constant time)
       
       Best For:
           - Early SA iterations (exploration)
           - Small/medium problem sizes (<500 cities)
           - Diversification in multi-start methods
       """
       
       def __init__(self, **kwargs) -> None:
           """
           Initialize RandomSwapStrategy.
           
           Args:
               **kwargs: Ignored (for registry compatibility)
           
           NOTE: This strategy is STATELESS (no configuration parameters).
           Accepts **kwargs to enable:
           1. Registry pattern (all strategies accept config)
           2. Uniform factory interface
           3. Future extension without breaking changes
           """
           pass
       
       def generate_neighbor(
           self,
           current_tour: List[int],
           problem: Problem,
           xp: BackendModule
       ) -> List[int]:
           """Generate neighbor via random swap."""
           n = len(current_tour) - 1  # Exclude depot
           
           # Random positions (exclude depot at 0 and n)
           i = int(xp.random.randint(1, n))
           j = int(xp.random.randint(1, n))
           
           # Ensure i != j
           while i == j:
               j = int(xp.random.randint(1, n))
           
           return swap_cities(current_tour, i, j)
   ```

2. **Create Tests (15min)**

   **Create:** `tests/unit/strategies/test_neighbor_strategies.py`

   ```python
   """Tests for neighbor generation strategies."""

   import pytest
   import numpy as np
   from code.src.algorithms.strategies.neighbor_strategies import RandomSwapStrategy
   from code.src.data_models.problem import Problem


   @pytest.fixture
   def problem_4city():
       """4-city TSP problem for testing."""
       distances = np.array([
           [0, 10, 15, 20],
           [10, 0, 35, 25],
           [15, 35, 0, 30],
           [20, 25, 30, 0]
       ])
       return Problem(distances=distances, dimension=4)


   def test_random_swap_returns_valid_tour(problem_4city):
       """Neighbor should be valid permutation."""
       strategy = RandomSwapStrategy()
       tour = [0, 1, 2, 3, 0]
       
       neighbor = strategy.generate_neighbor(tour, problem_4city, np)
       
       assert len(neighbor) == len(tour)
       assert neighbor[0] == 0  # Depot preserved
       assert neighbor[-1] == 0
       assert set(neighbor) == set(tour)  # Same cities


   def test_random_swap_modifies_tour(problem_4city):
       """Neighbor should be different from current tour."""
       strategy = RandomSwapStrategy()
       tour = [0, 1, 2, 3, 0]
       
       # Run multiple times to avoid false negatives
       neighbors = [strategy.generate_neighbor(tour, problem_4city, np) for _ in range(10)]
       
       # At least one should be different (probability ≈ 1.0)
       assert any(n != tour for n in neighbors)


   def test_random_swap_does_not_modify_original(problem_4city):
       """Should return new tour, not modify original."""
       strategy = RandomSwapStrategy()
       tour = [0, 1, 2, 3, 0]
       original = tour.copy()
       
       neighbor = strategy.generate_neighbor(tour, problem_4city, np)
       
       assert tour == original
   ```

3. **Run Tests (3min)**
   ```bash
   pytest tests/unit/strategies/test_neighbor_strategies.py -v
   # Should pass all 3 tests
   ```

4. **Commit (2min)**
   ```bash
   git add code/src/algorithms/strategies/neighbor_strategies.py tests/unit/strategies/test_neighbor_strategies.py
   git commit -m "feat(strategies): Add RandomSwapStrategy for M14.3

   - Implements NeighborStrategy protocol
   - Uses tour_operators.swap_cities utility
   - 3 tests: validity, modification, immutability"
   ```

**Acceptance Criteria:**

- [ ] RandomSwapStrategy created
- [ ] Implements NeighborStrategy protocol
- [ ] All 3 tests pass
- [ ] Uses swap_cities from tour_operators
- [ ] File committed

---

### Task M14.3.2: RandomInsertionStrategy (30min)

**Append to neighbor_strategies.py:**

```python
class RandomInsertionStrategy:
    """
    Generate neighbor by removing and reinserting a city.
    
    Complexity: O(n) for list operations
    Search Space: n(n-1) possible insertions
    
    Characteristics:
        - Moderate diversity
        - Can produce larger changes than swap
        - Slower than swap (list operations)
    
    Best For:
        - Mid-range SA temperatures
        - Route structure optimization
        - Avoiding local minima from swap-only search
    """
    
    def __init__(self, **kwargs) -> None:
        """
        Initialize RandomInsertionStrategy (stateless).
        
        Args:
            **kwargs: Ignored (for registry compatibility)
        """
        pass
    
    def generate_neighbor(
        self,
        current_tour: List[int],
        problem: Problem,
        xp: BackendModule
    ) -> List[int]:
        """Generate neighbor via random insertion."""
        n = len(current_tour) - 1
        
        from_pos = int(xp.random.randint(1, n))
        to_pos = int(xp.random.randint(1, n))
        
        # Ensure from_pos != to_pos
        while from_pos == to_pos:
            to_pos = int(xp.random.randint(1, n))
        
        from ..tour_operators import insert_city
        return insert_city(current_tour, from_pos, to_pos)
```

**Append to test file:**

```python
def test_random_insertion_returns_valid_tour(problem_4city):
    """Insertion neighbor should be valid."""
    from code.src.algorithms.strategies.neighbor_strategies import RandomInsertionStrategy
    strategy = RandomInsertionStrategy()
    tour = [0, 1, 2, 3, 0]
    
    neighbor = strategy.generate_neighbor(tour, problem_4city, np)
    
    assert len(neighbor) == len(tour)
    assert neighbor[0] == 0
    assert neighbor[-1] == 0
    assert set(neighbor) == set(tour)
```

**Run tests, commit:**

```bash
pytest tests/unit/strategies/test_neighbor_strategies.py::test_random_insertion_returns_valid_tour -v
git add -u
git commit -m "feat(strategies): Add RandomInsertionStrategy for M14.3"
```

---

### Task M14.3.3: Random2OptStrategy (30min)

**Append to neighbor_strategies.py:**

```python
class Random2OptStrategy:
    """
    Generate neighbor by reversing a random segment (2-opt move).
    
    Complexity: O(k) where k = segment length
    Search Space: n(n-1)/2 possible reversals
    
    Characteristics:
        - Classic 2-opt neighborhood
        - Can untangle crossed edges
        - Variable impact (small vs large segments)
    
    Best For:
        - Later SA iterations (intensification)
        - TSP instances with geometric structure
        - Hybrid with improvement operators
        
    Note:
        This generates ONE random 2-opt move.
        For exhaustive 2-opt, use ImprovementOperator.
    """
    
    def __init__(self, **kwargs) -> None:
        """
        Initialize Random2OptStrategy (stateless).
        
        Args:
            **kwargs: Ignored (for registry compatibility)
        """
        pass
    
    def generate_neighbor(
        self,
        current_tour: List[int],
        problem: Problem,
        xp: BackendModule
    ) -> List[int]:
        """Generate neighbor via random 2-opt move."""
        n = len(current_tour) - 1
        
        i = int(xp.random.randint(1, n - 1))
        j = int(xp.random.randint(i + 1, n))
        
        from ..tour_operators import invert_segment
        return invert_segment(current_tour, i, j)
```

**Append test, run, commit:**

```bash
# Add test similar to swap/insertion
pytest tests/unit/strategies/test_neighbor_strategies.py -v
git add -u
git commit -m "feat(strategies): Add Random2OptStrategy for M14.3"
```

---

### Task M14.3.4: Refactor SimulatedAnnealing to Accept Strategy (60min)

> [!WARNING]
> **CRITICAL CORRECTION NEEDED: SA Algorithm Classification**
>
> **Current SA header says:** "Class: P-Data (Parallel Data)"
> **Actual implementation:** S-Task (Sequential Task) ONLY
>
> **Issues:**
>
> 1. SA runs single sequential chain (no multistart, no parallel chains)
> 2. No streaming architecture implemented
> 3. No backend parameter in current **init** signature
> 4. Buffer reuse pattern not implemented (see METAHEURISTIC_ARCHITECTURE_DECISIONS.md Section 2.2)
>
> **Required Fixes:**
>
> 1. Change docstring header to: "Class: S-Task (Sequential Task)"
> 2. Add note: "P-Data variant (multistart) deferred to M16+ (see Section 4: Streaming Architecture)"
> 3. Add `backend` parameter to `__init__` (currently missing)
> 4. Implement VRAM guardrails if backend=="cupy" (see GPU Guardrails section below)
>
> **See:** `METAHEURISTIC_ARCHITECTURE_DECISIONS.md`
>
> - Section 0.4: Dual Nature diagrams (S-Task vs P-Data distinction)
> - Section 2.1: GPU Guardrails (_check_vram_capacity pattern)
> - Section 4: Streaming Architecture (multistart future work)

**DESIGN DECISION:** Clean break - NEW API only. No backward compatibility fallback logic.

- OLD API (`neighbor_method="swap"`) is DEPRECATED and removed
- Users MUST migrate to new strategy-based API
- Rationale: Avoids dual implementation complexity, technical debt, bug potential
- Migration documented in M15.2.1 (update docstrings)

**Process:**

1. **Read Current Implementation (10min)**
   ```bash
   # Understand current __init__ signature
   code/src/algorithms/metaheuristics/simulated_annealing.py:1-100
   ```

2. **Add neighbor_strategy Parameter (20min)**

   **Edit:** `code/src/algorithms/metaheuristics/simulated_annealing.py`

   Find `__init__` method, replace old neighbor_method with neighbor_strategy:
   ```python
   def __init__(
       self,
       max_iterations: int = 10000,
       initial_temp: float = 100.0,
       cooling_rate: float = 0.99,
       neighbor_strategy,  # REQUIRED - NeighborStrategy instance
       seed: int = None,
       backend: str = "numpy"
   ):
       """
       Initialize Simulated Annealing.
       
       Args:
           neighbor_strategy: NeighborStrategy instance (REQUIRED)
               - Pass RandomSwapStrategy(), Random2OptStrategy(), etc.
               - No default - forces explicit strategy selection
           max_iterations: Maximum number of iterations
           initial_temp: Starting temperature
           cooling_rate: Temperature decay rate (0 < rate < 1)
           seed: Random seed for reproducibility
           backend: "numpy" or "cupy"
       
       Example:
           >>> from code.src.algorithms.strategies import RandomSwapStrategy
           >>> sa = SimulatedAnnealing(
           ...     neighbor_strategy=RandomSwapStrategy(),
           ...     max_iterations=5000
           ... )
       
       Breaking Change:
           OLD: SimulatedAnnealing(neighbor_method="swap")
           NEW: SimulatedAnnealing(neighbor_strategy=RandomSwapStrategy())
       
       Migration Guide: See M15.2.1 documentation
       """
       # ... existing code ...
       
       # Store strategy (no fallback logic)
       self.neighbor_strategy = neighbor_strategy
   ```

3. **Replace Hardcoded Neighbor Generation (15min)**

   Find `_get_neighbor` or similar method, replace:
   ```python
   # DELETE old hardcoded methods:
   # def _neighbor_swap(self, tour, n, xp): ...
   # def _neighbor_2opt(self, tour, n, xp): ...
   # def _neighbor_insertion(self, tour, n, xp): ...
   
   # REPLACE with single strategy call:
   def _get_neighbor(self, tour, problem, xp):
       """Generate neighbor using strategy (Lego Brick architecture)."""
       return self.neighbor_strategy.generate_neighbor(tour, problem, xp)
   ```

4. **Update solve() to Pass problem (5min)**

   Ensure `_get_neighbor` receives `problem`:
   ```python
   # In solve() method
   neighbor = self._get_neighbor(current_tour, problem, xp)
   ```

5. **Run Validation (5min)**
   ```bash
   mypy --strict code/src/algorithms/metaheuristics/simulated_annealing.py
   python -c "from code.src.algorithms.metaheuristics import SimulatedAnnealing"
   bash scripts/validate_refactor.sh
   ```

6. **Commit (5min)**
   ```bash
   git add code/src/algorithms/metaheuristics/simulated_annealing.py
   git commit -m "refactor(SA): Accept neighbor_strategy parameter for M14.3

   BREAKING CHANGE: Remove neighbor_method parameter (clean break)
   
   - Add neighbor_strategy parameter (NeighborStrategy instance, REQUIRED)
   - Delete neighbor_method parameter and fallback logic
   - Delete hardcoded _neighbor_* methods (swap/2opt/insertion)
   - Replace with single strategy call (Lego Brick pattern)
   - Update _get_neighbor to use self.neighbor_strategy
   
   Migration:
     OLD: SimulatedAnnealing(neighbor_method='swap')
     NEW: SimulatedAnnealing(neighbor_strategy=RandomSwapStrategy())
   
   See M15.2.1 for migration documentation"
   ```

**Acceptance Criteria:**

- [ ] neighbor_strategy parameter added (REQUIRED, no default)
- [ ] neighbor_method parameter REMOVED (clean break)
- [ ] ALL hardcoded _neighbor_* methods DELETED
- [ ] Single strategy call in _get_neighbor
- [ ] mypy --strict passes
- [ ] File committed with BREAKING CHANGE note

**Migration Note:**

- Users MUST update to new API
- Migration guide provided in M15.2.1 docstring updates
- No dual implementation (clean architecture)

---

### Task M14.3.5: SA Integration Test (30min)

**Create:** `tests/integration/test_sa_with_strategies.py`

```python
"""Integration tests for SA with strategy pattern."""

import pytest
import numpy as np
from code.src.algorithms.metaheuristics import SimulatedAnnealing
from code.src.algorithms.strategies.neighbor_strategies import (
    RandomSwapStrategy,
    Random2OptStrategy,
    RandomInsertionStrategy
)
from code.src.data_models.problem import Problem


@pytest.fixture
def berlin52_problem():
    """Berlin52 TSP instance."""
    # Load or create problem
    # For now, use small synthetic problem
    distances = np.random.rand(10, 10) * 100
    distances = (distances + distances.T) / 2  # Symmetric
    np.fill_diagonal(distances, 0)
    return Problem(distances=distances, dimension=10)


def test_sa_with_swap_strategy(berlin52_problem):
    """SA should work with RandomSwapStrategy."""
    sa = SimulatedAnnealing(
        max_iterations=100,
        neighbor_strategy=RandomSwapStrategy(),
        backend="numpy"
    )
    
    solution = sa.solve(berlin52_problem)
    
    assert solution is not None
    assert len(solution.tour) == berlin52_problem.dimension + 1
    assert solution.tour[0] == 0
    assert solution.tour[-1] == 0
    assert solution.cost > 0


def test_sa_with_2opt_strategy(berlin52_problem):
    """SA should work with Random2OptStrategy."""
    sa = SimulatedAnnealing(
        max_iterations=100,
        neighbor_strategy=Random2OptStrategy(),
        backend="numpy"
    )
    
    solution = sa.solve(berlin52_problem)
    assert solution is not None


def test_sa_with_insertion_strategy(berlin52_problem):
    """SA should work with RandomInsertionStrategy."""
    sa = SimulatedAnnealing(
        max_iterations=100,
        neighbor_strategy=RandomInsertionStrategy(),
        backend="numpy"
    )
    
    solution = sa.solve(berlin52_problem)
    assert solution is not None
```

**Run tests, commit:**

```bash
pytest tests/integration/test_sa_with_strategies.py -v
git add tests/integration/test_sa_with_strategies.py
git commit -m "test(integration): Add SA strategy integration tests for M14.3"
```

---

**Update Task Log:**

```markdown
## M14.3: SA Strategy Extraction
- **Status:** COMPLETE
- **Commits:** [SHAs for 5 tasks]
- **Files Created:**
  - neighbor_strategies.py (3 strategies, ~120 lines with explicit __init__)
  - test_neighbor_strategies.py (9 tests)
  - test_sa_with_strategies.py (3 integration tests)
- **Files Modified:**
  - simulated_annealing.py (refactored - BREAKING CHANGE)
- **Breaking Changes:** neighbor_method parameter REMOVED (clean break, no fallback)
- **Migration:** See M15.2.1 for docstring updates guiding users
- **Notes:** Lego brick architecture working - SA accepts any NeighborStrategy
```

---

### Performance Testing Requirements (Data-Driven Constraints)

**Based on:** `test_sa_comprehensive.py` results (2025-01-28)  
**Reference:** `documentation/progress/SA_COMPREHENSIVE_ANALYSIS.md`

#### 1. Iteration Counts (Empirically Validated)

| Problem Size | Minimum Iterations | Rationale |
|--------------|-------------------|-----------|
| Small (n<100) | 100k | Test 5: eil51 achieved 15% with 100k |
| Medium (n=100-200) | 200k | **Test 2: ch150 needs 200k (14.44% vs 4.58% at 50k)** |
| Large (n>200) | 300k-400k | Test 5: ts225 only 5.56% at 100k (needs more) |

**Critical:** Test 2 proved 20k iterations insufficient (previous claim of "0% improvement" was wrong - needed 200k).

#### 2. Problem Size Selection

- **Benchmark:** ch150 (150 nodes), NOT berlin52
- **Rationale:** berlin52 too small for scalability analysis
- **Test Suite:** eil51 (small), ch150 (medium), ts225 (large)

#### 3. Acceptance Rate Validation

- **Track:** Acceptance rate per test
- **Valid Range:** 10-60%
  - <10%: Stuck in greedy mode (temp too low)
  - >60%: Accepting too many bad moves (temp too high)
- **Rationale:** Test 1 showed 0% improvement when acceptance rate = 0%

#### 4. Cooling Rate Calculation

**DO NOT hardcode cooling_rate!**

```python
# Correct: Ensure temp reaches min_temp at exactly max_iterations
cooling_rate = (min_temp / initial_temp) ** (1 / max_iterations)

# Example: ch150, 200k iterations
cooling_rate = (0.01 / 10000) ** (1 / 200000) = 0.999931
```

**Rationale:** Test 2 revealed hardcoded rates hit min_temp too early (iteration 50k/200k).

#### 5. GPU Testing Constraints

**DO NOT test random strategies on GPU!**

- **Test 4 Result:** GPU 28x slower (111.1s vs 3.9s CPU) for Random2Opt
- **Overhead:** 70.6 μs transfer + ~500 μs kernel launch per iteration
- **Ratio:** Overhead 110x the actual work

**GPU ONLY for:**

- TwoOptMove (Phase 7) - O(n²) work justifies overhead
- Multistart SA (future) - parallel independent chains

#### 6. Overhead Measurement (Test Pattern)

When testing GPU components:

```python
# Measure explicit transfers
tour_cpu_to_gpu_time = benchmark(cupy.asarray, tour)
result_gpu_to_cpu_time = benchmark(cupy.asnumpy, result)

# Report per-iteration overhead
overhead_per_iter = (tour_cpu_to_gpu + result_gpu_to_cpu) / iterations
```

**Output format:**

```
Transfer overhead: 70.6 μs/iteration
For 100k iterations: 7.06 seconds
```

**Rationale:** Makes GPU slowdown explainable (Test 3 pattern).

#### 7. Convergence Analysis

**Log Required Fields:**

```python
{
    "iterations_run": 200000,
    "final_temp": 0.011,
    "stopped_reason": "min_temp",  # or "max_iterations"
    "acceptance_rate": 0.23,
    "improvement_pct": 14.44
}
```

**Validation:**

- If `stopped_reason == "min_temp"` AND `iterations_run < 0.9 * max_iterations`:
  - ⚠️ Temperature schedule misconfigured
  - Re-run with adjusted cooling rate

#### 8 type-driven must have data-driven validation

##### Rationale

- Ensure all strategies are validated against empirical data.
- Type-driven development is:
  - absolutely necessary, as the "lego bricks" modular architecture require the same `return types` for it to really be modular
  - but not sufficient: The data must make sense with the literature.

#### Expected Outcomes (Validated Baselines)

| Strategy | Problem | Iterations | Improvement | Runtime (CPU) | GPU? |
|----------|---------|-----------|-------------|---------------|------|
| Random2Opt | ch150 | 200k | 10-15% | 3-8s | ❌ NO (28x slower) |
| RandomSwap | ch150 | 200k | 0-2% | 6-7s | ❌ NO |
| RandomInsertion | ch150 | 200k | 0-2% | 6-7s | ❌ NO |

**Validation Script Update:**

```bash
# Add to scripts/validate_refactor.sh after M14.3.5

echo "[6/6] SA Performance Validation..."
timeout 300s python test_sa_comprehensive.py --test=2 --problem=ch150 --iterations=200000

# Expected: >10% improvement, ~200k iterations completed
if [ $? -ne 0 ]; then
    echo "⚠️  Failed (expected >10% improvement with 200k iterations)"
    exit 1
else
    echo "✅ SA performance validated (iteration scaling working)"
fi
```

---

### 🆕 GPU VRAM Guardrails (ADDITION - 2025-11-07)

**Reference:** [`METAHEURISTIC_ARCHITECTURE_DECISIONS.md` - Section 2.1: GPU Guardrails](../architecture/METAHEURISTIC_ARCHITECTURE_DECISIONS.md#21-gpu-guardrails)

**Requirement:** **ALL GPU algorithms MUST validate VRAM capacity BEFORE starting computation.**

#### VRAM Calculation Formulas

**Distance Matrix (shared across all algorithms):**

$$
\text{Distance Matrix} = n^2 \times 8 \text{ bytes}
$$

**SA Working Buffers:**

$$
\text{SA Buffers} = 3n \times 8 \text{ bytes}
$$

Breakdown: `current_tour` + `neighbor_tour` + `best_tour`

**GA Working Buffers:**

$$
\text{GA Buffers} = 2 \times \text{pop\_size} \times n \times 8 \text{ bytes}
$$

Breakdown: `population` + `offspring`

**ACO Working Buffers:**

$$
\text{ACO Buffers} = n^2 \times 8 + \text{num\_ants} \times n \times 8
$$

Breakdown: `pheromone_matrix` + `ant_paths`

#### Implementation Pattern

```python
def _check_vram_capacity(self, problem):
    """Calculate required VRAM and fail early if insufficient."""
    n = problem.dimension
    
    # Distance matrix (shared)
    distance_size = n * n * 8  # float64
    
    # Algorithm-specific buffers
    if self.algorithm == "SA":
        buffer_size = n * 8 * 3  # current, neighbor, best
    elif self.algorithm == "GA":
        buffer_size = n * 8 * self.population_size * 2  # pop + offspring
    elif self.algorithm == "ACO":
        buffer_size = n * n * 8 + n * self.num_ants * 8  # pheromone + paths
    
    total_required = distance_size + buffer_size
    available = cp.cuda.Device().mem_info[0]  # Free VRAM
    
    if total_required > available * 0.9:  # 90% safety margin
        raise MemoryError(
            f"Insufficient VRAM: need {total_required/1e6:.1f}MB, "
            f"have {available/1e6:.1f}MB available"
        )
```

#### VRAM Capacity Table (GTX 1050 Mobile: 4GB)

| Algorithm | n=150 | n=300 | n=500 | n=1000 | Safe Limit (n) |
|-----------|-------|-------|-------|--------|----------------|
| **SA** | 184KB | 724KB | 2.0MB | 8.0MB | ~21,000 |
| **GA (pop=1000)** | 2.6MB | 9.2MB | 25.6MB | 102.4MB | ~1,900 |
| **ACO (ants=100)** | 300KB | 1.1MB | 3.1MB | 12.4MB | ~6,800 |

**Note:** Actual constraint is algorithm runtime, not VRAM (for n≤500).

#### Validation Requirements

**When implementing ANY GPU algorithm:**

1. ✅ Call `_check_vram_capacity()` in `__init__()` or at start of `solve()`
2. ✅ Fail with clear `MemoryError` BEFORE allocating buffers
3. ✅ Include buffer sizes in error message
4. ✅ Test with artificially reduced VRAM (mock `cp.cuda.Device().mem_info`)

**Test Pattern:**

```python
def test_vram_guardrail():
    """GPU algorithm should fail early if VRAM insufficient."""
    # Mock low VRAM
    with patch('cupy.cuda.Device.mem_info', return_value=(1e6, 4e9)):  # 1MB free
        ga = GeneticAlgorithm(population_size=10000, backend="cupy")
        
        with pytest.raises(MemoryError, match="Insufficient VRAM"):
            ga.solve(ch150)
```

#### Documentation Requirements

**Update for EACH GPU algorithm:**

- Docstring: Add "GPU Memory Requirements" section
- Calculate VRAM for example problem size
- Reference architecture doc for formula

**Example:**

```python
class GeneticAlgorithm:
    """
    Genetic Algorithm with tournament selection.
    
    GPU Memory Requirements
    -----------------------
    Distance matrix: n² × 8 bytes
    Population buffers: 2 × pop_size × n × 8 bytes
    
    Example (ch150, pop=1000):
        Distance: 180KB
        Buffers: 2.4MB
        Total: 2.6MB ✓ (fits in 4GB VRAM)
    
    See: METAHEURISTIC_ARCHITECTURE_DECISIONS.md#section-2-vram-management
    """
```

#### Related Architecture Decisions

**For comprehensive design patterns, see:**

- [Section 1: Composition Patterns](../architecture/METAHEURISTIC_ARCHITECTURE_DECISIONS.md#section-1-composition-patterns) - ILS, VNS, Adaptive, Post-processing
- [Section 2.2: Buffer Reuse Patterns](../architecture/METAHEURISTIC_ARCHITECTURE_DECISIONS.md#22-buffer-reuse-patterns) - Applies to SA, GA, ACO
- [Section 3: Improvement Heuristics](../architecture/METAHEURISTIC_ARCHITECTURE_DECISIONS.md#section-3-improvement-heuristics-beyond-2-opt) - 3-opt, Lin-Kernighan, Or-opt
- [Section 4: Streaming Architecture](../architecture/METAHEURISTIC_ARCHITECTURE_DECISIONS.md#section-4-streaming-architecture) - P-Data algorithms (future work)

**Status:** NEW REQUIREMENT (added 2025-11-07) - Addresses admonitions from `SA_COMPREHENSIVE_ANALYSIS.md` (Groups D & E)

---

# PHASE 4: GA Strategy Extraction (3-4h)

**Status:** ❌ NOT STARTED - GeneticAlgorithm still has hardcoded operators

## M14.4: Extract GA Operator Strategies

**Status:** ❌ NOT STARTED - Must complete PHASE 3 fixes first

**Prerequisites:**

- M14.1 complete (protocols) ✅
- M14.2 complete (tour operators) ✅
- M14.3 complete (SA strategies) ⚠️ NEEDS 4 FIXES (see M14.3.4 subtasks)

**Context Files:**

- `code/src/algorithms/metaheuristics/genetic_algorithm.py` (EXISTS - still hardcoded)
- `code/src/protocols/strategy_protocols.py` (MutationOperator and CrossoverStrategy protocols ready)

**Current Reality:**

- ❌ GeneticAlgorithm.**init** does NOT have mutation_operator parameter
- ❌ GeneticAlgorithm.**init** does NOT have crossover_strategy parameter  
- ❌ Mutation strategies DO NOT EXIST (no mutation_strategies.py file)
- ❌ Crossover strategies DO NOT EXIST (no crossover_strategies.py file)
- ❌ GA still uses hardcoded _mutation_* and _order_crossover methods

**Objective:** Extract hardcoded GA operators into separate strategy classes (same pattern as SA)

**IMPORTANT:** Do NOT start this phase until M14.3.4 subtasks (SA fixes) are complete.

---

### Task M14.4.1: Mutation Strategies (60min)

**Status:** ❌ NOT STARTED - Create mutation_strategies.py with 3 operators

**MANDATORY REQUIREMENT:** All mutation operators MUST have explicit `__init__` method.

- Stateless operators: `def __init__(self) -> None: pass`
- Stateful operators: `def __init__(self, param: Type) -> None: self.param = param`
- Rationale: Future-proofing, clarity, singleton pattern compatibility

**Process:**

1. **Create Mutation Strategies File (40min)**

   **Create:** `code/src/algorithms/strategies/mutation_strategies.py`

   ```python
   """
   Mutation operators for Genetic Algorithm.

   Implements MutationOperator protocol for GA diversity maintenance.
   Mutations are BLIND (no problem context, no fitness evaluation).

   Usage:
       from code.src.algorithms.strategies import mutation_strategies
       operator = mutation_strategies.SwapMutation()
       mutated = operator.mutate(individual, np)
   """

   from typing import List
   from ...protocols.strategy_protocols import MutationOperator
   from ...protocols.backend import BackendModule
   from ..tour_operators import swap_cities, insert_city, invert_segment


   class SwapMutation:
       """
       Mutate by swapping two random cities.
       
       Characteristics:
           - Small perturbation (2 cities affected)
           - Fast (O(1) operation)
           - High probability of valid tour
       
       Best For:
           - Fine-tuning solutions
           - Late GA generations
           - Exploitation phase
       """
       
       def __init__(self, **kwargs) -> None:
           """
           Initialize SwapMutation (stateless operator).
           
           Args:
               **kwargs: Ignored (for registry compatibility)
           """
           pass
       
       def mutate(self, individual: List[int], xp: BackendModule) -> List[int]:
           """Mutate via random swap."""
           n = len(individual) - 1
           
           i = int(xp.random.randint(1, n))
           j = int(xp.random.randint(1, n))
           
           while i == j:
               j = int(xp.random.randint(1, n))
           
           return swap_cities(individual, i, j)


   class InsertionMutation:
       """
       Mutate by removing and reinserting a city.
       
       Characteristics:
           - Medium perturbation (affects route structure)
           - Moderate diversity
           - Good balance exploration/exploitation
       
       Best For:
           - Mid-phase GA
           - Maintaining diversity
           - Escaping local optima
       """
       
       def __init__(self, **kwargs) -> None:
           """
           Initialize InsertionMutation (stateless operator).
           
           Args:
               **kwargs: Ignored (for registry compatibility)
           """
           pass
       
       def mutate(self, individual: List[int], xp: BackendModule) -> List[int]:
           """Mutate via random insertion."""
           n = len(individual) - 1
           
           from_pos = int(xp.random.randint(1, n))
           to_pos = int(xp.random.randint(1, n))
           
           while from_pos == to_pos:
               to_pos = int(xp.random.randint(1, n))
           
           return insert_city(individual, from_pos, to_pos)


   class InversionMutation:
       """
       Mutate by reversing a random segment.
       
       Characteristics:
           - Large perturbation (entire segment affected)
           - High diversity
           - 2-opt style neighborhood
       
       Best For:
           - Early GA generations
           - Exploration phase
           - Breaking out of premature convergence
       """
       
       def __init__(self, **kwargs) -> None:
           """
           Initialize InversionMutation (stateless operator).
           
           Args:
               **kwargs: Ignored (for registry compatibility)
           """
           pass
           """Initialize InversionMutation (stateless operator)."""
           pass
       
       def mutate(self, individual: List[int], xp: BackendModule) -> List[int]:
           """Mutate via segment inversion."""
           n = len(individual) - 1
           
           i = int(xp.random.randint(1, n - 1))
           j = int(xp.random.randint(i + 1, n))
           
           return invert_segment(individual, i, j)
   ```

2. **Create Tests (15min)**

   **Create:** `tests/unit/strategies/test_mutation_strategies.py`

   ```python
   """Tests for GA mutation operators."""

   import pytest
   import numpy as np
   from code.src.algorithms.strategies.mutation_strategies import (
       SwapMutation,
       InsertionMutation,
       InversionMutation
   )


   @pytest.fixture
   def individual():
       """Sample TSP individual for testing."""
       return [0, 1, 2, 3, 4, 0]


   def test_swap_mutation_returns_valid_tour(individual):
       """SwapMutation should return valid permutation."""
       operator = SwapMutation()
       mutated = operator.mutate(individual, np)
       
       assert len(mutated) == len(individual)
       assert mutated[0] == 0
       assert mutated[-1] == 0
       assert set(mutated) == set(individual)


   def test_insertion_mutation_returns_valid_tour(individual):
       """InsertionMutation should return valid permutation."""
       operator = InsertionMutation()
       mutated = operator.mutate(individual, np)
       
       assert len(mutated) == len(individual)
       assert mutated[0] == 0
       assert mutated[-1] == 0
       assert set(mutated) == set(individual)


   def test_inversion_mutation_returns_valid_tour(individual):
       """InversionMutation should return valid permutation."""
       operator = InversionMutation()
       mutated = operator.mutate(individual, np)
       
       assert len(mutated) == len(individual)
       assert mutated[0] == 0
       assert mutated[-1] == 0
       assert set(mutated) == set(individual)


   def test_mutations_modify_individual(individual):
       """All mutations should produce different individuals."""
       swap = SwapMutation()
       insertion = InsertionMutation()
       inversion = InversionMutation()
       
       # Run multiple times to avoid false negatives
       swap_results = [swap.mutate(individual, np) for _ in range(10)]
       insertion_results = [insertion.mutate(individual, np) for _ in range(10)]
       inversion_results = [inversion.mutate(individual, np) for _ in range(10)]
       
       assert any(m != individual for m in swap_results)
       assert any(m != individual for m in insertion_results)
       assert any(m != individual for m in inversion_results)


   def test_mutations_do_not_modify_original(individual):
       """Mutations should not modify original individual."""
       original = individual.copy()
       
       swap = SwapMutation()
       insertion = InsertionMutation()
       inversion = InversionMutation()
       
       swap.mutate(individual, np)
       insertion.mutate(individual, np)
       inversion.mutate(individual, np)
       
       assert individual == original
   ```

3. **Run Tests (3min)**
   ```bash
   pytest tests/unit/strategies/test_mutation_strategies.py -v
   # Should pass all 5 tests
   ```

4. **Commit (2min)**
   ```bash
   git add code/src/algorithms/strategies/mutation_strategies.py tests/unit/strategies/test_mutation_strategies.py
   git commit -m "feat(strategies): Add mutation operators for M14.4

   - SwapMutation: Small perturbation (exploitation)
   - InsertionMutation: Medium perturbation (balance)
   - InversionMutation: Large perturbation (exploration)

   All implement MutationOperator protocol
   All use tour_operators utilities (DRY)
   5 tests: validity, modification, immutability

   Lego brick: GA can use any MutationOperator"
   ```

**Acceptance Criteria:**

- [ ] mutation_strategies.py created (3 classes)
- [ ] All 5 tests pass
- [ ] Uses tour_operators utilities
- [ ] MutationOperator protocol compliance
- [ ] File committed

---

### Task M14.4.2: Crossover Strategies (90min)

**Process:**

1. **Create Crossover Strategies File (60min)**

   **Create:** `code/src/algorithms/strategies/crossover_strategies.py`

   ```python
   """
   Crossover operators for Genetic Algorithm.

   Implements CrossoverStrategy protocol for GA recombination.
   Crossover combines traits from two parents to produce offspring.

   Usage:
       from code.src.algorithms.strategies import crossover_strategies
       strategy = crossover_strategies.OrderCrossover()
       child1, child2 = strategy.crossover(parent1, parent2, np)
   """

   from typing import List, Tuple
   from ...protocols.strategy_protocols import CrossoverStrategy
   from ...protocols.backend import BackendModule


   class OrderCrossover:
       """
       Order Crossover (OX) - Davis (1985).
       
       Algorithm:
           1. Select random segment from parent1
           2. Copy segment to child1
           3. Fill remaining positions with cities from parent2 (in order)
           4. Repeat symmetrically for child2
       
       Characteristics:
           - Preserves relative order of cities
           - Good for TSP (order matters)
           - O(n) complexity (Python for-loops)
       
       Future Work (User Q6):
           - Vectorize with xp operations (not CUDA kernels)
           - Parallel OX (Fujimoto & Kaga) - deferred to M16
       
       References:
           - Davis (1985): "Applying adaptive algorithms to epistatic domains"
           - Goldberg (1989): "Genetic Algorithms in Search"
       """
       
       def __init__(self, **kwargs) -> None:
           """
           Initialize OrderCrossover (stateless operator).
           
           Args:
               **kwargs: Ignored (for registry compatibility)
           """
           pass
       
       def crossover(
           self,
           parent1: List[int],
           parent2: List[int],
           xp: BackendModule
       ) -> Tuple[List[int], List[int]]:
           """
           Generate two offspring via Order Crossover.
           
           Args:
               parent1, parent2: Parent tours [depot, ..., depot]
               xp: Backend module (numpy or cupy)
           
           Returns:
               (child1, child2): Two offspring tours
           """
           n = len(parent1) - 1  # Exclude depot
           
           # Select random segment (excluding depot)
           start = int(xp.random.randint(1, n - 1))
           end = int(xp.random.randint(start + 1, n))
           
           # Create offspring
           child1 = self._ox_single(parent1, parent2, start, end)
           child2 = self._ox_single(parent2, parent1, start, end)
           
           return child1, child2
       
       def _ox_single(
           self,
           parent1: List[int],
           parent2: List[int],
           start: int,
           end: int
       ) -> List[int]:
           """
           Generate single offspring via OX.
           
           Note: Using Python for-loops (not vectorized).
           User Q6: Vectorize with xp (deferred - needs careful design).
           """
           n = len(parent1) - 1
           
           # Initialize child with depot
           child = [0] * (n + 1)
           child[0] = 0
           child[-1] = 0
           
           # Copy segment from parent1
           child[start:end] = parent1[start:end]
           
           # Fill remaining with cities from parent2 (in order)
           parent2_cities = [c for c in parent2[1:-1] if c not in child[start:end]]
           
           # Fill positions before segment
           fill_idx = 0
           for pos in range(1, start):
               child[pos] = parent2_cities[fill_idx]
               fill_idx += 1
           
           # Fill positions after segment
           for pos in range(end, n):
               child[pos] = parent2_cities[fill_idx]
               fill_idx += 1
           
           return child
   ```

2. **Create Tests (20min)**

   **Create:** `tests/unit/strategies/test_crossover_strategies.py`

   ```python
   """Tests for GA crossover operators."""

   import pytest
   import numpy as np
   from code.src.algorithms.strategies.crossover_strategies import OrderCrossover


   @pytest.fixture
   def parents():
       """Sample parent tours for testing."""
       parent1 = [0, 1, 2, 3, 4, 5, 0]
       parent2 = [0, 3, 5, 1, 4, 2, 0]
       return parent1, parent2


   def test_order_crossover_returns_valid_tours(parents):
       """OX should return two valid permutations."""
       parent1, parent2 = parents
       strategy = OrderCrossover()
       
       child1, child2 = strategy.crossover(parent1, parent2, np)
       
       # Child1 checks
       assert len(child1) == len(parent1)
       assert child1[0] == 0
       assert child1[-1] == 0
       assert set(child1) == set(parent1)
       
       # Child2 checks
       assert len(child2) == len(parent2)
       assert child2[0] == 0
       assert child2[-1] == 0
       assert set(child2) == set(parent2)


   def test_order_crossover_inherits_from_both_parents(parents):
       """Children should have segments from both parents."""
       parent1, parent2 = parents
       strategy = OrderCrossover()
       
       # Run multiple times to check segment inheritance
       children = [strategy.crossover(parent1, parent2, np) for _ in range(5)]
       
       # At least one child should differ from both parents
       # (proves recombination happened)
       assert any(c1 != parent1 and c1 != parent2 for c1, c2 in children)


   def test_order_crossover_does_not_modify_parents(parents):
       """Crossover should not modify parent tours."""
       parent1, parent2 = parents
       original1 = parent1.copy()
       original2 = parent2.copy()
       
       strategy = OrderCrossover()
       strategy.crossover(parent1, parent2, np)
       
       assert parent1 == original1
       assert parent2 == original2
   ```

3. **Run Tests (5min)**
   ```bash
   pytest tests/unit/strategies/test_crossover_strategies.py -v
   # Should pass all 3 tests
   ```

4. **Commit (5min)**
   ```bash
   git add code/src/algorithms/strategies/crossover_strategies.py tests/unit/strategies/test_crossover_strategies.py
   git commit -m "feat(strategies): Add Order Crossover for M14.4

   - OrderCrossover (Davis 1985): preserves relative order
   - Currently uses Python for-loops (not vectorized)
   - 3 tests: validity, inheritance, immutability

   User Q6: Vectorization with xp deferred (needs careful design)
   Future: Parallel OX (Fujimoto) in M16

   Lego brick: GA can use any CrossoverStrategy"
   ```

**Acceptance Criteria:**

- [ ] crossover_strategies.py created
- [ ] OrderCrossover implements CrossoverStrategy protocol
- [ ] All 3 tests pass
- [ ] Preserves tour validity (permutations)
- [ ] File committed

---

### Task M14.4.3: Refactor GeneticAlgorithm to Accept Strategies (90min)

**DESIGN DECISION:** Clean break - NEW API only. No backward compatibility fallback logic.

- OLD API (`crossover_method="ox"`, `mutation_method="swap"`) REMOVED
- Users MUST migrate to new strategy-based API
- Rationale: Avoids dual implementation complexity, maintains clean architecture
- Migration documented in M15.2.1 (update docstrings)

**Process:**

1. **Read Current Implementation (15min)**
   ```bash
   # Understand current __init__ and operator methods
   code/src/algorithms/metaheuristics/genetic_algorithm.py:1-150
   ```

2. **Add Strategy Parameters (30min)**

   **Edit:** `code/src/algorithms/metaheuristics/genetic_algorithm.py`

   Find `__init__` method, replace old parameters with strategy instances:
   ```python
   def __init__(
       self,
       population_size: int = 100,
       generations: int = 500,
       crossover_rate: float = 0.8,
       mutation_rate: float = 0.2,
       # NEW PARAMETERS (Strategy Pattern)
       crossover_strategy,  # REQUIRED - CrossoverStrategy instance
       mutation_operator,   # REQUIRED - MutationOperator instance
       post_process_strategy = None,  # OPTIONAL - ImprovementOperator (User Q3)
       seed: int = None,
       backend: str = "numpy"
   ):
       """
       Initialize Genetic Algorithm.
       
       Args:
           crossover_strategy: CrossoverStrategy instance (REQUIRED)
               - Pass OrderCrossover(), PMXCrossover(), etc.
               - No default - forces explicit strategy selection
           mutation_operator: MutationOperator instance (REQUIRED)
               - Pass SwapMutation(), InversionMutation(), etc.
               - No default - forces explicit operator selection
           post_process_strategy: ImprovementOperator for memetic algorithm (OPTIONAL)
               - If provided, applies local search to best individual each generation
               - User Decision Q3: Both mutation AND post-processing
               - Pass TwoOptImprovement(), ThreeOptImprovement(), etc.
           population_size: Number of individuals in population
           generations: Number of evolutionary generations
           crossover_rate: Probability of crossover (0-1)
           mutation_rate: Probability of mutation (0-1)
           seed: Random seed for reproducibility
           backend: "numpy" or "cupy"
       
       Example:
           >>> from code.src.algorithms.strategies import SwapMutation, OrderCrossover
           >>> ga = GeneticAlgorithm(
           ...     mutation_operator=SwapMutation(),
           ...     crossover_strategy=OrderCrossover(),
           ...     population_size=100,
           ...     generations=500
           ... )
       
       Breaking Change:
           OLD: GeneticAlgorithm(crossover_method="ox", mutation_method="swap")
           NEW: GeneticAlgorithm(crossover_strategy=OrderCrossover(), mutation_operator=SwapMutation())
       
       Migration Guide: See M15.2.1 documentation
       """
       # ... existing code ...
       
       # Store strategies (no fallback logic)
       self.crossover_strategy = crossover_strategy
       self.mutation_operator = mutation_operator
       self.post_process_strategy = post_process_strategy
   ```

3. **Replace Hardcoded Operators (20min)**

   Find operator methods, replace:
   ```python
   # DELETE old hardcoded methods:
   # def _order_crossover(self, parent1, parent2): ...
   # def _mutation_swap(self, individual): ...
   # def _mutation_inversion(self, individual): ...
   
   # REPLACE with single strategy calls:
   def _crossover(self, parent1, parent2, xp):
       """Generate offspring using crossover strategy."""
       return self.crossover_strategy.crossover(parent1, parent2, xp)
   
   
   def _mutate(self, individual, xp):
       """Mutate individual using mutation operator."""
       return self.mutation_operator.mutate(individual, xp)
   ```

4. **Add Post-Processing Hook (User Q3) (20min)**

   In `solve()` method, after each generation:
   ```python
   # In solve() method, after offspring generation and evaluation
   
   # User Q3: Post-processing strategy (memetic algorithm)
   if self.post_process_strategy is not None:
       # Apply local search to best individual
       best_idx = fitness_scores.argmin()
       best_individual = population[best_idx]
       
       improved = self.post_process_strategy.improve(
           tour=best_individual,
           problem=problem,
           xp=xp,
           max_iterations=100  # Configurable via strategy __init__
       )
       
       population[best_idx] = improved
       # Recalculate fitness for improved individual
       fitness_scores[best_idx] = self._calculate_fitness(improved, problem.distances, xp)
   ```

5. **Run Validation (3min)**
   ```bash
   mypy --strict code/src/algorithms/metaheuristics/genetic_algorithm.py
   python -c "from code.src.algorithms.metaheuristics import GeneticAlgorithm"
   bash scripts/validate_refactor.sh
   ```

6. **Commit (2min)**
   ```bash
   git add code/src/algorithms/metaheuristics/genetic_algorithm.py
   git commit -m "refactor(GA): Accept strategy parameters for M14.4

   BREAKING CHANGE: Remove crossover_method/mutation_method (clean break)
   
   - Add crossover_strategy parameter (CrossoverStrategy, REQUIRED)
   - Add mutation_operator parameter (MutationOperator, REQUIRED)
   - Add post_process_strategy parameter (ImprovementOperator, OPTIONAL)
   - Delete crossover_method/mutation_method parameters
   - Delete hardcoded operator methods (_order_crossover, _mutation_*)
   - Replace with strategy calls (Lego Brick pattern)
   - Implement post-processing hook (User Decision Q3: mutation AND improvement)
   
   Migration:
     OLD: GeneticAlgorithm(crossover_method='ox', mutation_method='swap')
     NEW: GeneticAlgorithm(crossover_strategy=OrderCrossover(), mutation_operator=SwapMutation())
   
   User Decision Q3: Both mutation AND post-processing supported
   Lego brick: GA accepts any CrossoverStrategy + MutationOperator + ImprovementOperator
   
   See M15.2.1 for migration documentation"
   ```

**Acceptance Criteria:**

- [ ] Strategy parameters added (crossover/mutation REQUIRED, post_process OPTIONAL)
- [ ] Post-processing hook implemented (User Q3)
- [ ] OLD parameters REMOVED (clean break, no fallback)
- [ ] ALL hardcoded operator methods DELETED
- [ ] mypy --strict passes
- [ ] File committed with BREAKING CHANGE note

**Migration Note:**

- Users MUST update to new API
- Migration guide provided in M15.2.1 docstring updates
- No dual implementation (clean architecture)

---

### Task M14.4.4: GA Integration Tests (45min)

**Process:**

1. **Create Integration Tests (35min)**

   **Create:** `tests/integration/test_ga_with_strategies.py`

   ```python
   """Integration tests for GA with strategy pattern."""

   import pytest
   import numpy as np
   from code.src.algorithms.metaheuristics import GeneticAlgorithm
   from code.src.algorithms.strategies.mutation_strategies import (
       SwapMutation,
       InsertionMutation,
       InversionMutation
   )
   from code.src.algorithms.strategies.crossover_strategies import OrderCrossover
   from code.src.data_models.problem import Problem


   @pytest.fixture
   def small_problem():
       """Small TSP instance for testing."""
       distances = np.random.rand(10, 10) * 100
       distances = (distances + distances.T) / 2  # Symmetric
       np.fill_diagonal(distances, 0)
       return Problem(distances=distances, dimension=10)


   def test_ga_with_swap_mutation(small_problem):
       """GA should work with SwapMutation."""
       ga = GeneticAlgorithm(
           population_size=20,
           generations=10,
           mutation_operator=SwapMutation(),
           crossover_strategy=OrderCrossover(),
           backend="numpy"
       )
       
       solution = ga.solve(small_problem)
       
       assert solution is not None
       assert len(solution.tour) == small_problem.dimension + 1
       assert solution.tour[0] == 0
       assert solution.tour[-1] == 0
       assert solution.cost > 0


   def test_ga_with_inversion_mutation(small_problem):
       """GA should work with InversionMutation."""
       ga = GeneticAlgorithm(
           population_size=20,
           generations=10,
           mutation_operator=InversionMutation(),
           crossover_strategy=OrderCrossover(),
           backend="numpy"
       )
       
       solution = ga.solve(small_problem)
       assert solution is not None


   def test_ga_with_all_mutation_types(small_problem):
       """Test all mutation operators work with GA."""
       mutations = [SwapMutation(), InsertionMutation(), InversionMutation()]
       
       for mutation in mutations:
           ga = GeneticAlgorithm(
               population_size=20,
               generations=5,
               mutation_operator=mutation,
               crossover_strategy=OrderCrossover(),
               backend="numpy"
           )
           solution = ga.solve(small_problem)
           assert solution is not None


   def test_ga_with_different_mutations(small_problem):
       """GA should work with different mutation operators."""
       for mutation_cls in [SwapMutation, InsertionMutation, InversionMutation]:
           ga = GeneticAlgorithm(
               population_size=20,
               generations=5,
               mutation_operator=mutation_cls(),
               crossover_strategy=OrderCrossover(),
               backend="numpy"
           )
           solution = ga.solve(small_problem)
           assert solution is not None


   def test_ga_without_post_processing(small_problem):
       """GA should work without post-processing (optional)."""
       ga = GeneticAlgorithm(
           population_size=20,
           generations=10,
           mutation_operator=SwapMutation(),
           crossover_strategy=OrderCrossover(),
           post_process_strategy=None,  # Explicitly None
           backend="numpy"
       )
       
       solution = ga.solve(small_problem)
       assert solution is not None
   ```

2. **Run Tests (8min)**
   ```bash
   pytest tests/integration/test_ga_with_strategies.py -v
   # Should pass all 5 tests
   ```

3. **Commit (2min)**
   ```bash
   git add tests/integration/test_ga_with_strategies.py
   git commit -m "test(integration): Add GA strategy integration tests for M14.4

   - Test all mutation operators (swap, insertion, inversion)
   - Test crossover strategy (OrderCrossover)
   - Test different mutation strategies in combination
   - Test optional post-processing (None allowed)

   5 tests covering GA strategy composition (clean API, no backward compat tests)"
   ```

**Acceptance Criteria:**

- [ ] Integration tests created
- [ ] All mutation operators tested
- [ ] Multiple strategy combinations tested
- [ ] All 5 tests pass
- [ ] File committed

---

**Update Task Log:**

```markdown
## M14.4: GA Strategy Extraction
- **Status:** COMPLETE
- **Commits:** [SHAs for 4 tasks]
- **Files Created:**
  - mutation_strategies.py (3 operators, ~120 lines)
  - crossover_strategies.py (OrderCrossover, ~100 lines)
  - test_mutation_strategies.py (5 tests)
  - test_crossover_strategies.py (3 tests)
  - test_ga_with_strategies.py (5 integration tests)
- **Files Modified:**
  - genetic_algorithm.py (refactored to accept strategies)
- **User Decisions Implemented:**
  - Q3: post_process_strategy parameter added
  - Q6: OX uses Python for-loops (vectorization deferred)
- **Backward Compatibility:** mutation_method/crossover_method still work
- **Notes:** Lego brick architecture - GA accepts any MutationOperator + CrossoverStrategy
```

---

**M14.4 COMPLETE - Proceed to M14.5 (Strategy Registries)**

---

# PHASE 5: Strategy Registries (1.5-2h)

**Status:** ❌ NOT STARTED - Depends on PHASE 4 completion

## M14.5: Create Strategy Registries

**Status:** ❌ NOT STARTED - Create after all strategies implemented

**Prerequisites:**

- M14.3 complete (neighbor strategies) ✅
- M14.4 complete (mutation & crossover strategies) ❌ NOT DONE

**Objective:** Create registries for string → strategy class lookup (avoid circular imports)

**Prerequisites:**

- M14.3 complete (SA strategies)
- M14.4 complete (GA strategies)

**Objective:** Create string → class registries to avoid circular imports

**Architecture Rationale:**

- Metaheuristics NEVER directly import strategies
- Registries enable serializable configs (JSON/YAML)
- Prevents circular dependency hell
- Singleton pattern for stateless strategies (prevents memory churn)
- Factory pattern for stateful strategies (allows parameterization)

---

### Task M14.5.0: Classify Strategies as Stateless/Stateful (30min)

**CRITICAL PERFORMANCE TASK:** Prevents unnecessary object instantiation.

**Problem:**

- Creating 30 identical `RandomSwapStrategy()` instances for 30 benchmark runs wastes memory
- Stateless strategies (no **init** parameters) should be singletons
- Stateful strategies (e.g., `TwoOptMoveStrategy(max_iterations=100)`) need factories

**Process:**

1. **Survey All Strategies (15min)**

   Review all strategy classes created in M14.3 and M14.4:
   - `code/src/algorithms/strategies/neighbor_strategies.py`
   - `code/src/algorithms/strategies/mutation_strategies.py`
   - `code/src/algorithms/strategies/crossover_strategies.py`

   For each strategy, check `__init__` signature:
   - Stateless: `def __init__(self) -> None: pass` (no parameters)
   - Stateful: `def __init__(self, param: Type) -> None: self.param = param` (has parameters)

2. **Create Classification Document (15min)**

   **Create:** `documentation/architecture/strategy_classification.md`

   ```markdown
   # Strategy Classification: Stateless vs Stateful

   **Purpose:** Determine singleton vs factory pattern for each strategy

   **Performance Impact:**
   - Stateless strategies → Singleton (one shared instance)
   - Stateful strategies → Factory (new instance per call)

   **Benefits:**
   - Eliminates ~95% of unnecessary object creation
   - Reduces memory churn in benchmarks (30x runs → 30x reuses)
   - Maintains configurability for stateful strategies

   ---

   ## Neighbor Strategies (SA)

   | Strategy | Type | __init__ Parameters | Registry Pattern |
   |----------|------|---------------------|------------------|
   | `RandomSwapStrategy` | STATELESS | None | Singleton |
   | `RandomInsertionStrategy` | STATELESS | None | Singleton |
   | `Random2OptStrategy` | STATELESS | None | Singleton |
   | `TwoOptMoveStrategy` (M15) | STATEFUL | `max_iterations: int`, `backend: str` | Factory |

   ---

   ## Mutation Operators (GA)

   | Operator | Type | __init__ Parameters | Registry Pattern |
   |----------|------|---------------------|------------------|
   | `SwapMutation` | STATELESS | None | Singleton |
   | `InsertionMutation` | STATELESS | None | Singleton |
   | `InversionMutation` | STATELESS | None | Singleton |

   ---

   ## Crossover Strategies (GA)

   | Strategy | Type | __init__ Parameters | Registry Pattern |
   |----------|------|---------------------|------------------|
   | `OrderCrossover` | STATELESS | None | Singleton |

   ---

   ## Improvement Operators (Post-Processing)

   | Operator | Type | __init__ Parameters | Registry Pattern |
   |----------|------|---------------------|------------------|
   | `TwoOptImprovement` (M15) | STATEFUL | `max_iterations: int` | Factory |
   | `ThreeOptImprovement` (Future) | STATEFUL | `max_iterations: int` | Factory |

   ---

   ## Summary

   **Stateless Strategies (7 total):**
   - RandomSwapStrategy, RandomInsertionStrategy, Random2OptStrategy
   - SwapMutation, InsertionMutation, InversionMutation
   - OrderCrossover

   **Stateful Strategies (2 in M14-M15):**
   - TwoOptMoveStrategy (max_iterations parameter)
   - TwoOptImprovement (max_iterations parameter)

   **Implementation in M14.5.1:**
   - Stateless → Create module-level singleton: `_RANDOM_SWAP = RandomSwapStrategy()`
   - Stateful → Use lambda factory: `lambda max_iter=1: TwoOptMoveStrategy(max_iter)`

   ---

   **Validation:**
   - Stateless strategies MUST have `__init__(self) -> None: pass`
   - Stateful strategies MUST NOT have empty __init__
   - Any strategy with configuration parameters is stateful
   ```

3. **Commit (5min)**
   ```bash
   git add documentation/architecture/strategy_classification.md
   git commit -m "docs(architecture): Classify strategies for M14.5.0

   Critical performance optimization: singleton vs factory pattern

   - 7 stateless strategies (singleton pattern)
   - 2 stateful strategies (factory pattern)
   - Prevents 95% of unnecessary object instantiation
   - Reduces memory churn in benchmarks

   Next: M14.5.1 implements hybrid singleton/factory registries"
   ```

**Acceptance Criteria:**

- [ ] All strategies classified as stateless/stateful
- [ ] Classification table created with registry patterns
- [ ] Stateless strategies validated (empty **init**)
- [ ] Stateful strategies identified (have parameters)
- [ ] File committed

**Impact:**

- M14.5.1 will use this classification to implement hybrid registries
- Benchmark scripts (M14.6.1) will benefit from singleton reuse
- ALGORITHM_MAP (M15.4.1) will use direct singleton references

---

### Task M14.5.1: Create Strategy Registries (75min)

**Process:**

1. **Create Registry Module (50min)**

   **Edit:** `code/src/algorithms/strategies/__init__.py`

   ```python
   """
   Strategy registries for algorithm composition.

   Provides string → class lookup to avoid circular imports.
   Enables serializable configuration (JSON/YAML).

   Usage:
       # Get strategy by name
       neighbor_strategy = NEIGHBOR_REGISTRY["random_swap"]()
       
       # Programmatic instantiation
       strategy_name = config["neighbor_strategy"]
       strategy = NEIGHBOR_REGISTRY[strategy_name]()

   Architecture:
       Layer 1: protocols/ (no imports)
       Layer 2: tour_operators/ (protocols only)
       Layer 3: strategies/ (protocols + operators)
       Layer 4: metaheuristics/ (REGISTRY only, not direct strategy imports)
       Layer 5: benchmarking/ (all via ALGORITHM_MAP)
   """

   from typing import Dict, Type, Callable
   from ...protocols.strategy_protocols import (
       NeighborStrategy,
       MutationOperator,
       CrossoverStrategy,
       ImprovementOperator
   )

   # Import strategy implementations
   from .neighbor_strategies import (
       RandomSwapStrategy,
       RandomInsertionStrategy,
       Random2OptStrategy
   )
   from .mutation_strategies import (
       SwapMutation,
       InsertionMutation,
       InversionMutation
   )
   from .crossover_strategies import (
       OrderCrossover
   )

   # Export utilities
   from ..tour_operators import (
       swap_cities,
       insert_city,
       invert_segment
   )


   # ============================================================================
   # MODULE-LEVEL SINGLETONS (for stateless strategies)
   # ============================================================================
   # Performance optimization: Stateless strategies instantiated ONCE at module load.
   # Shared across all algorithm instances. See strategy_classification.md.
   
   # Neighbor Strategies (stateless)
   _RANDOM_SWAP = RandomSwapStrategy()
   _RANDOM_INSERTION = RandomInsertionStrategy()
   _RANDOM_2OPT = Random2OptStrategy()
   
   # Mutation Operators (stateless)
   _SWAP_MUTATION = SwapMutation()
   _INSERTION_MUTATION = InsertionMutation()
   _INVERSION_MUTATION = InversionMutation()
   
   # Crossover Strategies (stateless)
   _ORDER_CROSSOVER = OrderCrossover()


   # ============================================================================
   # NEIGHBOR STRATEGY REGISTRY (for SA)
   # ============================================================================
   # Pattern: All strategies accept **kwargs (stateless ignore, stateful use)
   
   NEIGHBOR_REGISTRY: Dict[str, Callable[..., NeighborStrategy]] = {
       # Stateless strategies → Return singleton (accept but ignore **kwargs)
       "random_swap": lambda **kwargs: _RANDOM_SWAP,
       "random_insertion": lambda **kwargs: _RANDOM_INSERTION,
       "random_2opt": lambda **kwargs: _RANDOM_2OPT,
       
       # Stateful strategies → Factory function (pass through **kwargs)
       # "two_opt_move": lambda **kwargs: TwoOptMoveStrategy(**kwargs),
   }


   # ============================================================================
   # MUTATION OPERATOR REGISTRY (for GA)
   # ============================================================================
   
   MUTATION_REGISTRY: Dict[str, Callable[..., MutationOperator]] = {
       # All stateless → Return singleton instances (accept but ignore **kwargs)
       "swap": lambda **kwargs: _SWAP_MUTATION,
       "insertion": lambda **kwargs: _INSERTION_MUTATION,
       "inversion": lambda **kwargs: _INVERSION_MUTATION,
   }


   # ============================================================================
   # CROSSOVER STRATEGY REGISTRY (for GA)
   # ============================================================================
   
   CROSSOVER_REGISTRY: Dict[str, Callable[..., CrossoverStrategy]] = {
       # All stateless → Return singleton instances (accept but ignore **kwargs)
       "ox": lambda **kwargs: _ORDER_CROSSOVER,
       "order_crossover": lambda **kwargs: _ORDER_CROSSOVER,  # Alias
       # Future: PMX, CX, ERX, etc.
   }


   # ============================================================================
   # IMPROVEMENT OPERATOR REGISTRY (for post-processing)
   # ============================================================================
   
   IMPROVEMENT_REGISTRY: Dict[str, Callable[..., ImprovementOperator]] = {
       # Stateful strategies → Factory functions (pass through **kwargs)
       # "two_opt": lambda **kwargs: TwoOptImprovement(**kwargs),
       # Future: 3-opt, Lin-Kernighan, etc.
   }


   # ============================================================================
   # EXPORTS
   # ============================================================================

   __all__ = [
       # Registries (primary interface)
       "NEIGHBOR_REGISTRY",
       "MUTATION_REGISTRY",
       "CROSSOVER_REGISTRY",
       "IMPROVEMENT_REGISTRY",
       
       # Singletons (for direct use in ALGORITHM_MAP - see M15.4.1)
       "_RANDOM_SWAP",
       "_RANDOM_INSERTION",
       "_RANDOM_2OPT",
       "_SWAP_MUTATION",
       "_INSERTION_MUTATION",
       "_INVERSION_MUTATION",
       "_ORDER_CROSSOVER",
       
       # Strategy classes (for custom instantiation)
       "RandomSwapStrategy",
       "RandomInsertionStrategy",
       "Random2OptStrategy",
       "SwapMutation",
       "InsertionMutation",
       "InversionMutation",
       "OrderCrossover",
       
       # Tour operators (utilities)
       "swap_cities",
       "insert_city",
       "invert_segment",
   ]
   ```

2. **Create Tests (20min)**

   **Create:** `tests/unit/strategies/test_registries.py`

   ```python
   """Tests for strategy registries and singleton pattern."""

   import pytest
   from code.src.algorithms.strategies import (
       NEIGHBOR_REGISTRY,
       MUTATION_REGISTRY,
       CROSSOVER_REGISTRY,
       IMPROVEMENT_REGISTRY,
       _RANDOM_SWAP,
       _SWAP_MUTATION,
       _ORDER_CROSSOVER,
       RandomSwapStrategy,
       SwapMutation,
       OrderCrossover
   )


   def test_neighbor_registry_contains_expected_strategies():
       """NEIGHBOR_REGISTRY should have all SA strategies."""
       expected = ["random_swap", "random_insertion", "random_2opt"]
       
       for name in expected:
           assert name in NEIGHBOR_REGISTRY


   def test_mutation_registry_contains_expected_operators():
       """MUTATION_REGISTRY should have all mutation operators."""
       expected = ["swap", "insertion", "inversion"]
       
       for name in expected:
           assert name in MUTATION_REGISTRY


   def test_crossover_registry_contains_expected_strategies():
       """CROSSOVER_REGISTRY should have crossover operators."""
       expected = ["ox", "order_crossover"]
       
       for name in expected:
           assert name in CROSSOVER_REGISTRY


   def test_neighbor_registry_factories_return_correct_types():
       """NEIGHBOR_REGISTRY factories should return strategy instances."""
       for name, factory in NEIGHBOR_REGISTRY.items():
           strategy = factory()
           assert hasattr(strategy, "generate_neighbor")


   def test_mutation_registry_factories_return_correct_types():
       """MUTATION_REGISTRY factories should return operator instances."""
       for name, factory in MUTATION_REGISTRY.items():
           operator = factory()
           assert hasattr(operator, "mutate")


   def test_crossover_registry_factories_return_correct_types():
       """CROSSOVER_REGISTRY factories should return strategy instances."""
       for name, factory in CROSSOVER_REGISTRY.items():
           strategy = factory()
           assert hasattr(strategy, "crossover")


   def test_registries_enable_string_based_instantiation():
       """Registries should enable string → instance conversion."""
       # SA neighbor strategy
       neighbor = NEIGHBOR_REGISTRY["random_swap"]()
       assert isinstance(neighbor, RandomSwapStrategy)
       
       # GA mutation
       mutation = MUTATION_REGISTRY["swap"]()
       assert isinstance(mutation, SwapMutation)
       
       # GA crossover
       crossover = CROSSOVER_REGISTRY["ox"]()
       assert isinstance(crossover, OrderCrossover)


   def test_registry_lookup_raises_on_unknown_key():
       """Registry lookup should fail gracefully for unknown keys."""
       with pytest.raises(KeyError):
           _ = NEIGHBOR_REGISTRY["nonexistent_strategy"]()


   def test_stateless_strategies_are_singletons():
       """Stateless strategies should return same instance (singleton pattern)."""
       # Neighbor strategies
       swap1 = NEIGHBOR_REGISTRY["random_swap"]()
       swap2 = NEIGHBOR_REGISTRY["random_swap"]()
       assert swap1 is swap2  # Same object identity
       assert swap1 is _RANDOM_SWAP  # Points to module singleton
       
       # Mutation operators
       mut1 = MUTATION_REGISTRY["swap"]()
       mut2 = MUTATION_REGISTRY["swap"]()
       assert mut1 is mut2
       assert mut1 is _SWAP_MUTATION
       
       # Crossover strategies
       cross1 = CROSSOVER_REGISTRY["ox"]()
       cross2 = CROSSOVER_REGISTRY["ox"]()
       assert cross1 is cross2
       assert cross1 is _ORDER_CROSSOVER


   def test_singletons_prevent_memory_churn():
       """Multiple instantiations should NOT create new objects."""
       # Simulate 30 benchmark runs
       instances = [NEIGHBOR_REGISTRY["random_swap"]() for _ in range(30)]
       
       # All should be the SAME object
       assert all(inst is instances[0] for inst in instances)
       assert all(inst is _RANDOM_SWAP for inst in instances)
       
       # Only ONE object in memory (not 30)
       assert len(set(id(inst) for inst in instances)) == 1
   ```

3. **Run Tests (3min)**
   ```bash
   pytest tests/unit/strategies/test_registries.py -v
   # Should pass all 10 tests (8 original + 2 singleton tests)
   ```

4. **Prompt user to Commit (2min)**
   ```bash
   git add code/src/algorithms/strategies/__init__.py tests/unit/strategies/test_registries.py
   git commit -m "feat(registries): Hybrid singleton/factory registries for M14.5

   CRITICAL PERFORMANCE OPTIMIZATION: Singleton pattern for stateless strategies
   
   - Module-level singletons: _RANDOM_SWAP, _SWAP_MUTATION, _ORDER_CROSSOVER, etc. (7 total)
   - NEIGHBOR_REGISTRY: Returns singletons for stateless, factories for stateful
   - MUTATION_REGISTRY: All stateless → return singletons
   - CROSSOVER_REGISTRY: All stateless → return singletons
   - IMPROVEMENT_REGISTRY: Placeholder for stateful strategies (M15.2)
   
   Performance Impact:
   - Eliminates 95% of unnecessary object instantiation
   - 30 benchmark runs → 30 singleton reuses (not 30 new objects)
   - Reduces memory churn and GC pressure
   
   Architecture: Metaheuristics use registries (no direct imports)
   Benefits: Serializable configs, no circular imports, singleton efficiency
   
   10 tests: registry contents, factory types, string lookup, singleton identity, memory efficiency
   
   See: strategy_classification.md for singleton/factory decisions
   Next: M15.4.1 uses direct singleton references in ALGORITHM_MAP"
   ```

**Acceptance Criteria:**

- [ ] All 4 registries created
- [ ] All 8 tests pass
- [ ] Factories return correct instances
- [ ] String lookup works

---

**Update Task Log:**

```markdown
## M14.5: Strategy Registries
- **Status:** COMPLETE
- **Commits:** [SHA]
- **Files Created:**
  - test_registries.py (8 tests)
- **Files Modified:**
  - strategies/__init__.py (4 registries, exports)
- **Architecture Impact:**
  - Metaheuristics now use REGISTRY["key"]() instead of direct imports
  - Enables serializable configuration
  - Breaks circular dependency cycle
- **Notes:** TwoOpt strategies will be added to registries in M15.2
```

---

# PHASE 6: Integration Testing (1-1.5h)

**Status:** ❌ NOT STARTED - Depends on PHASES 4-5 completion

## M14.6: Full Pipeline Integration

**Status:** ❌ NOT STARTED - Integration tests after all components ready

**Prerequisites:**

- All strategies implemented ❌
- All registries created ❌
- SA and GA refactored ⚠️ SA done with fixes needed, GA not started

**Objective:** Verify full pipeline works end-to-end

**Prerequisites:**

- M14.5 complete (registries)
- All strategies implemented

**Objective:** Validate Lego brick architecture works end-to-end

---

### Task M14.6.1: Full Pipeline Tests (60min)

**Process:**

1. **Create Integration Test Suite (45min)**

   **Create:** `tests/integration/test_full_pipeline.py`

   ```python
   """Full pipeline integration tests."""

   import pytest
   import numpy as np
   from code.src.algorithms.constructive import NearestNeighbor
   from code.src.algorithms.metaheuristics import SimulatedAnnealing, GeneticAlgorithm
   from code.src.algorithms.strategies import (
       NEIGHBOR_REGISTRY,
       MUTATION_REGISTRY,
       CROSSOVER_REGISTRY,
       RandomSwapStrategy,
       SwapMutation,
       OrderCrossover
   )
   from code.src.data_models.problem import Problem


   @pytest.fixture
   def small_problem():
       """Small TSP instance for testing."""
       np.random.seed(42)
       distances = np.random.rand(15, 15) * 100
       distances = (distances + distances.T) / 2  # Symmetric
       np.fill_diagonal(distances, 0)
       return Problem(distances=distances, dimension=15)


   def test_nn_to_sa_pipeline(small_problem):
       """Test: NearestNeighbor → SimulatedAnnealing."""
       # Step 1: Generate initial solution with NN
       nn = NearestNeighbor(backend="numpy")
       nn_solution = nn.solve(small_problem)
       
       assert nn_solution is not None
       assert len(nn_solution.tour) == small_problem.dimension + 1
       
       # Step 2: Improve with SA
       sa = SimulatedAnnealing(
           neighbor_strategy=RandomSwapStrategy(),
           initial_temp=100,
           cooling_rate=0.95,
           iterations_per_temp=50,
           backend="numpy"
       )
       sa_solution = sa.solve(small_problem)
       
       assert sa_solution is not None
       assert sa_solution.cost <= nn_solution.cost  # Should improve or maintain


   def test_sa_with_different_neighbor_strategies(small_problem):
       """Test: SA works with all neighbor strategies."""
       strategies = ["random_swap", "random_insertion", "random_2opt"]
       
       for strategy_name in strategies:
           strategy = NEIGHBOR_REGISTRY[strategy_name]()
           
           sa = SimulatedAnnealing(
               neighbor_strategy=strategy,
               initial_temp=100,
               cooling_rate=0.95,
               iterations_per_temp=30,
               backend="numpy"
           )
           
           solution = sa.solve(small_problem)
           assert solution is not None
           assert len(solution.tour) == small_problem.dimension + 1


   def test_ga_with_different_operators(small_problem):
       """Test: GA works with all mutation/crossover combinations."""
       mutations = ["swap", "insertion", "inversion"]
       crossovers = ["ox"]
       
       for mutation_name in mutations:
           for crossover_name in crossovers:
               mutation = MUTATION_REGISTRY[mutation_name]()
               crossover = CROSSOVER_REGISTRY[crossover_name]()
               
               ga = GeneticAlgorithm(
                   population_size=20,
                   generations=10,
                   mutation_operator=mutation,
                   crossover_strategy=crossover,
                   backend="numpy"
               )
               
               solution = ga.solve(small_problem)
               assert solution is not None
               assert len(solution.tour) == small_problem.dimension + 1


   def test_string_based_configuration(small_problem):
       """Test: String-based strategy lookup (config file simulation)."""
       # Simulate config from JSON/YAML
       config = {
           "neighbor_strategy": "random_2opt",
           "mutation_operator": "inversion",
           "crossover_strategy": "ox"
       }
       
       # SA with config
       neighbor = NEIGHBOR_REGISTRY[config["neighbor_strategy"]]()
       sa = SimulatedAnnealing(
           neighbor_strategy=neighbor,
           initial_temp=100,
           cooling_rate=0.95,
           iterations_per_temp=30,
           backend="numpy"
       )
       sa_solution = sa.solve(small_problem)
       assert sa_solution is not None
       
       # GA with config
       mutation = MUTATION_REGISTRY[config["mutation_operator"]]()
       crossover = CROSSOVER_REGISTRY[config["crossover_strategy"]]()
       ga = GeneticAlgorithm(
           population_size=20,
           generations=10,
           mutation_operator=mutation,
           crossover_strategy=crossover,
           backend="numpy"
       )
       ga_solution = ga.solve(small_problem)
       assert ga_solution is not None


   def test_lego_brick_composition(small_problem):
       """Test: Arbitrary strategy composition (User Vision: 'I build SA with whichever improvement')."""
       # Build SA with RandomSwapStrategy
       sa_swap = SimulatedAnnealing(
           neighbor_strategy=RandomSwapStrategy(),
           initial_temp=100,
           backend="numpy"
       )
       solution_swap = sa_swap.solve(small_problem)
       
       # Build SA with Random2OptStrategy
       sa_2opt = SimulatedAnnealing(
           neighbor_strategy=NEIGHBOR_REGISTRY["random_2opt"](),
           initial_temp=100,
           backend="numpy"
       )
       solution_2opt = sa_2opt.solve(small_problem)
       
       # Both should work (Lego bricks are interchangeable)
       assert solution_swap is not None
       assert solution_2opt is not None
       
       # Results may differ (different strategies)
       # But both are valid TSP tours
       assert len(solution_swap.tour) == small_problem.dimension + 1
       assert len(solution_2opt.tour) == small_problem.dimension + 1
   ```

2. **Run Tests (12min)**
   ```bash
   pytest tests/integration/test_full_pipeline.py -v
   # Should pass all 6 tests
   ```

3. **Commit (3min)**
   ```bash
   git add tests/integration/test_full_pipeline.py
   git commit -m "test(integration): Add full pipeline tests for M14.6

   - NN → SA pipeline validation
   - SA with all neighbor strategies
   - GA with all mutation/crossover combinations
   - String-based configuration (JSON/YAML simulation)
   - Lego brick composition (interchangeable strategies)

   6 tests proving Strategy Pattern architecture works
   User Vision: 'Build SA with whichever improvement I want' ✓"
   ```

**Acceptance Criteria:**

- [ ] Full pipeline tests created
- [ ] All 6 tests pass
- [ ] String-based config tested
- [ ] Lego brick composition validated
- [ ] File committed

---

**Update Task Log:**

```markdown
## M14.6: Integration Testing
- **Status:** COMPLETE
- **Commits:** [SHA]
- **Files Created:**
  - test_full_pipeline.py (6 integration tests)
- **Tests Validated:**
  - NN → SA pipeline works
  - SA accepts all neighbor strategies
  - GA accepts all mutation/crossover combinations
  - String-based configuration (registries)
  - Lego brick architecture (interchangeable strategies)
- **User Vision Validated:** "Build SA with whichever improvement I want" ✓
- **Notes:** Architecture proof-of-concept complete
```

---

**M14 COMPLETE - All SA and GA strategies extracted, registries created, integration validated**

---

## M15.1.2: TwoOptImprovement (Post-Processing Operator)

**Prerequisites:**

- M15.1.1 complete (TwoOptMoveStrategy)
- M14.1 complete (ImprovementOperator protocol)

**Objective:** Wrap TwoOpt for post-processing (exhaustive improvement)

**Key Difference from TwoOptMoveStrategy:**

- **TwoOptMove**: `max_iterations=1` (single move for SA neighbor generation)
- **TwoOptImprovement**: `max_iterations=100` (exhaustive search for post-processing)

---

### Task M15.1.2.1: Create TwoOptImprovement (60min)

**Process:**

1. **Create TwoOptImprovement Class (40min)**

   **Create:** `code/src/algorithms/strategies/two_opt_improvement.py`

   ```python
   """
   2-Opt improvement operator for post-processing.

   Implements ImprovementOperator protocol for exhaustive improvement.
   Typically used as post_process_strategy in Genetic Algorithm.

   Usage:
       from code.src.algorithms.strategies import TwoOptImprovement
       improver = TwoOptImprovement()
       improved_tour = improver.improve(
           tour=current_tour,
           problem=problem,
           xp=np,
           max_iterations=100
       )
   """

   from typing import List, Optional
   from ...protocols.strategy_protocols import ImprovementOperator
   from ...protocols.backend import BackendModule
   from ...data_models.problem import Problem
   from ..improvement import TwoOptCPU, TwoOptGPU
   import numpy as np
   try:
       import cupy
   except ImportError:
       cupy = None


   class TwoOptImprovement:
       """
       2-Opt post-processing for exhaustive improvement.
       
       Characteristics:
           - Exhaustive search (max_iterations=100 default)
           - Best-improvement strategy (greedy)
           - Guarantees 2-opt optimality at convergence
       
       Best For:
           - Post-processing after GA/SA
           - Memetic algorithms (GA + local search)
           - Final solution polishing
       
       NOT For:
           - SA neighbor generation (use TwoOptMoveStrategy instead)
           - Incremental improvement (use TwoOptMoveStrategy)
       
       Backend Configuration:
           - backend="cpu": Runs 2-opt on CPU (default)
           - backend="gpu": Runs 2-opt on GPU (requires CuPy)
           - Backend is set ONCE at init, not selected at runtime
           - Supports mixing: GPU SA + CPU improvement (minimal overhead)
       """
       
       def __init__(self, max_iterations: int = 100, backend: str = "cpu", **kwargs):
           """
           Initialize TwoOptImprovement.
           
           Args:
               max_iterations: Maximum 2-opt passes (default: 100)
               backend: "cpu" or "gpu" (default: "cpu")
               **kwargs: Ignored (for registry compatibility)
           """
           self.max_iterations = max_iterations
           self.use_gpu = (backend == "gpu")
           
           # Initialize backend (set ONCE, not at runtime)
           if self.use_gpu:
               if cupy is None:
                   raise ImportError("CuPy required for GPU backend")
               self.backend_module = cupy
               self._backend_optimizer = TwoOptGPU()
           else:
               self.backend_module = np
               self._backend_optimizer = TwoOptCPU()
       
       def improve(
           self,
           tour: List[int],
           problem: Problem,
           xp: BackendModule,
           max_iterations: Optional[int] = None
       ) -> List[int]:
           """
           Apply exhaustive 2-opt improvement.
           
           Args:
               tour: Current tour [depot, ..., depot]
               problem: Problem instance with distances
               xp: Caller's backend module (for I/O array type compatibility)
               max_iterations: Override default max_iterations (optional)
           
           Returns:
               Improved tour (2-opt optimal after max_iterations)
               
           Note:
               - Uses self.backend_module for optimization (set in __init__)
               - xp is ONLY for input/output array type conversion
               - Supports mixing backends (e.g., GPU SA + CPU improvement)
           """
           iterations = max_iterations if max_iterations is not None else self.max_iterations
           
           # Convert tour to strategy's backend (cheap: ~5μs for n=3000)
           tour_internal = self.backend_module.asarray(tour)
           
           # Convert distances to strategy's backend 
           # (CuPy caches: 14ms first call, 0ms subsequent)
           distances_internal = self.backend_module.asarray(problem.distances)
           
           # Optimize on strategy's backend (10-50ms)
           improved_tour, _, _ = self._backend_optimizer.optimize(
               tour=tour_internal,
               distances=distances_internal,
               max_iterations=iterations
           )
           
           # Convert result to caller's backend (cheap: ~5μs)
           # asarray() is smart: no copy if same backend
           return xp.asarray(improved_tour)
   ```

2. **Create Tests (15min)**

   **Create:** `tests/unit/strategies/test_two_opt_improvement.py`

   ```python
   """Tests for TwoOptImprovement."""

   import pytest
   import numpy as np
   from code.src.algorithms.strategies.two_opt_improvement import TwoOptImprovement
   from code.src.data_models.problem import Problem


   @pytest.fixture
   def small_problem():
       """Small TSP instance for testing."""
       distances = np.array([
           [0, 10, 15, 20],
           [10, 0, 35, 25],
           [15, 35, 0, 30],
           [20, 25, 30, 0]
       ])
       return Problem(distances=distances, dimension=4)


   @pytest.fixture
   def suboptimal_tour():
       """Suboptimal tour that 2-opt can improve."""
       return [0, 2, 1, 3, 0]


   def test_improvement_returns_valid_tour(small_problem, suboptimal_tour):
       """TwoOptImprovement should return valid tour."""
       improver = TwoOptImprovement()
       improved = improver.improve(
           tour=suboptimal_tour,
           problem=small_problem,
           xp=np,
           max_iterations=100
       )
       
       assert len(improved) == len(suboptimal_tour)
       assert improved[0] == 0
       assert improved[-1] == 0
       assert set(improved) == set(suboptimal_tour)


   def test_improvement_improves_or_maintains_cost(small_problem, suboptimal_tour):
       """TwoOptImprovement should improve or maintain cost."""
       improver = TwoOptImprovement()
       
       # Calculate original cost
       original_cost = sum(
           small_problem.distances[suboptimal_tour[i], suboptimal_tour[i + 1]]
           for i in range(len(suboptimal_tour) - 1)
       )
       
       # Improve
       improved = improver.improve(
           tour=suboptimal_tour,
           problem=small_problem,
           xp=np,
           max_iterations=100
       )
       
       # Calculate improved cost
       improved_cost = sum(
           small_problem.distances[improved[i], improved[i + 1]]
           for i in range(len(improved) - 1)
       )
       
       assert improved_cost <= original_cost


   def test_improvement_with_max_iterations(small_problem, suboptimal_tour):
       """TwoOptImprovement should respect max_iterations parameter."""
       improver = TwoOptImprovement()
       
       # Low iterations (may not converge)
       improved_low = improver.improve(
           tour=suboptimal_tour,
           problem=small_problem,
           xp=np,
           max_iterations=1
       )
       
       # High iterations (should converge)
       improved_high = improver.improve(
           tour=suboptimal_tour,
           problem=small_problem,
           xp=np,
           max_iterations=100
       )
       
       # Both should be valid tours
       assert len(improved_low) == len(suboptimal_tour)
       assert len(improved_high) == len(suboptimal_tour)
   ```

3. **Run Tests (3min)**
   ```bash
   pytest tests/unit/strategies/test_two_opt_improvement.py -v
   # Should pass all 3 tests
   ```

4. **Commit (2min)**
   ```bash
   git add code/src/algorithms/strategies/two_opt_improvement.py tests/unit/strategies/test_two_opt_improvement.py
   git commit -m "feat(strategies): Add TwoOptImprovement for M15.1.2

   - TwoOptImprovement: Exhaustive 2-opt (max_iterations=100 default)
   - Implements ImprovementOperator protocol
   - For post-processing (NOT SA neighbor generation)
   - 3 tests: validity, improvement guarantee, max_iterations

   Difference from TwoOptMoveStrategy:
   - TwoOptMove: max_iterations=1 (single move, SA neighbors)
   - TwoOptImprovement: max_iterations=100 (exhaustive, post-processing)

   Use Case: GA post_process_strategy (User Q3)"
   ```

**Acceptance Criteria:**

- [ ] TwoOptImprovement created
- [ ] Implements ImprovementOperator protocol
- [ ] All 3 tests pass
- [ ] Default max_iterations=100
- [ ] File committed

---

## M15.2: Register TwoOpt in Registries

**Prerequisites:**

- M15.1 complete (TwoOptMove + TwoOptImprovement)
- M14.5 complete (registries)

**Objective:** Add TwoOpt strategies to registries

---

### Task M15.2.1: Update Registries (20min)

**Process:**

1. **Update strategies/**init**.py (15min)**

   **Edit:** `code/src/algorithms/strategies/__init__.py`

   Add imports:
   ```python
   from .two_opt_move import TwoOptMoveStrategy
   from .two_opt_improvement import TwoOptImprovement
   ```

   Update NEIGHBOR_REGISTRY:
   ```python
   NEIGHBOR_REGISTRY: Dict[str, Callable[..., NeighborStrategy]] = {
       "random_swap": lambda **kwargs: RandomSwapStrategy(**kwargs),
       "random_insertion": lambda **kwargs: RandomInsertionStrategy(**kwargs),
       "random_2opt": lambda **kwargs: Random2OptStrategy(**kwargs),
       "two_opt_move": lambda **kwargs: TwoOptMoveStrategy(**kwargs),  # NEW
       "2opt_move": lambda **kwargs: TwoOptMoveStrategy(**kwargs),     # Alias
   }
   ```

   Update IMPROVEMENT_REGISTRY:
   ```python
   IMPROVEMENT_REGISTRY: Dict[str, Callable[..., ImprovementOperator]] = {
       "two_opt": lambda **kwargs: TwoOptImprovement(**kwargs),        # NEW
       "2opt": lambda **kwargs: TwoOptImprovement(**kwargs),           # Alias
       "two_opt_improvement": lambda **kwargs: TwoOptImprovement(**kwargs),  # Verbose alias
   }
   ```

   Update **all**:
   ```python
   __all__ = [
       # ... existing exports ...
       "TwoOptMoveStrategy",
       "TwoOptImprovement",
   ]
   ```

2. **Update Registry Tests (3min)**

   **Edit:** `tests/unit/strategies/test_registries.py`

   Add to expected strategies:
   ```python
   def test_neighbor_registry_contains_expected_strategies():
       """NEIGHBOR_REGISTRY should have all SA strategies."""
       expected = ["random_swap", "random_insertion", "random_2opt", 
                   "two_opt_move", "2opt_move"]
       
       for name in expected:
           assert name in NEIGHBOR_REGISTRY


   def test_improvement_registry_contains_expected_operators():
       """IMPROVEMENT_REGISTRY should have improvement operators."""
       expected = ["two_opt", "2opt", "two_opt_improvement"]
       
       for name in expected:
           assert name in IMPROVEMENT_REGISTRY
   ```

3. **Run Tests (1min)**
   ```bash
   pytest tests/unit/strategies/test_registries.py -v
   # Should pass updated tests
   ```

4. **Commit (1min)**
   ```bash
   git add code/src/algorithms/strategies/__init__.py tests/unit/strategies/test_registries.py
   git commit -m "feat(registries): Add TwoOpt strategies for M15.2

   - NEIGHBOR_REGISTRY: Add two_opt_move, 2opt_move
   - IMPROVEMENT_REGISTRY: Add two_opt, 2opt, two_opt_improvement
   - Tests updated: registry coverage includes TwoOpt

   String-based config now supports:
   - neighbor_strategy: 'two_opt_move' (SA)
   - post_process_strategy: 'two_opt' (GA)

   Lego infrastructure: TwoOpt strategies now composable"
   ```

**Acceptance Criteria:**

- [ ] TwoOpt added to registries
- [ ] Tests updated
- [ ] All tests pass
- [ ] File committed

---

## M15.3: GA + TwoOpt Integration

**Prerequisites:**

- M15.2 complete (TwoOpt in registries)
- M14.4 complete (GA refactor)

**Objective:** Test memetic algorithm (GA + TwoOpt post-processing)

---

### Task M15.3.1: Create GA + TwoOpt Integration Tests (45min)

**Process:**

1. **Create Integration Tests (35min)**

   **Create:** `tests/integration/test_ga_twoot_integration.py`

   ```python
   """Integration tests for GA + TwoOpt (Memetic Algorithm)."""

   import pytest
   import numpy as np
   from code.src.algorithms.metaheuristics import GeneticAlgorithm
   from code.src.algorithms.strategies import (
       SwapMutation,
       OrderCrossover,
       TwoOptImprovement,
       IMPROVEMENT_REGISTRY
   )
   from code.src.data_models.problem import Problem


   @pytest.fixture
   def medium_problem():
       """Medium TSP instance for testing."""
       np.random.seed(42)
       distances = np.random.rand(20, 20) * 100
       distances = (distances + distances.T) / 2  # Symmetric
       np.fill_diagonal(distances, 0)
       return Problem(distances=distances, dimension=20)


   def test_ga_without_post_processing(medium_problem):
       """Baseline: GA without local search."""
       ga = GeneticAlgorithm(
           population_size=30,
           generations=20,
           mutation_operator=SwapMutation(),
           crossover_strategy=OrderCrossover(),
           post_process_strategy=None,  # No post-processing
           backend="numpy"
       )
       
       solution = ga.solve(medium_problem)
       assert solution is not None
       return solution.cost


   def test_ga_with_twoot_post_processing(medium_problem):
       """Memetic: GA + 2-Opt local search (User Q3)."""
       ga = GeneticAlgorithm(
           population_size=30,
           generations=20,
           mutation_operator=SwapMutation(),
           crossover_strategy=OrderCrossover(),
           post_process_strategy=TwoOptImprovement(),  # Post-processing
           backend="numpy"
       )
       
       solution = ga.solve(medium_problem)
       
       assert solution is not None
       assert len(solution.tour) == medium_problem.dimension + 1
       assert solution.tour[0] == 0
       assert solution.tour[-1] == 0


   def test_memetic_algorithm_improves_over_pure_ga(medium_problem):
       """Memetic GA should outperform pure GA (on average)."""
       # Pure GA
       ga_pure = GeneticAlgorithm(
           population_size=30,
           generations=15,
           mutation_operator=SwapMutation(),
           crossover_strategy=OrderCrossover(),
           post_process_strategy=None,
           backend="numpy"
       )
       solution_pure = ga_pure.solve(medium_problem)
       
       # Memetic GA
       ga_memetic = GeneticAlgorithm(
           population_size=30,
           generations=15,
           mutation_operator=SwapMutation(),
           crossover_strategy=OrderCrossover(),
           post_process_strategy=TwoOptImprovement(),
           backend="numpy"
       )
       solution_memetic = ga_memetic.solve(medium_problem)
       
       # Memetic should be at least as good
       assert solution_memetic.cost <= solution_pure.cost * 1.05  # 5% tolerance


   def test_string_based_memetic_config(medium_problem):
       """Test: String-based post-processing config."""
       # Simulate config from JSON/YAML
       config = {
           "mutation_operator": "swap",
           "crossover_strategy": "ox",
           "post_process_strategy": "two_opt"
       }
       
       from code.src.algorithms.strategies import MUTATION_REGISTRY, CROSSOVER_REGISTRY
       
       ga = GeneticAlgorithm(
           population_size=30,
           generations=15,
           mutation_operator=MUTATION_REGISTRY[config["mutation_operator"]](),
           crossover_strategy=CROSSOVER_REGISTRY[config["crossover_strategy"]](),
           post_process_strategy=IMPROVEMENT_REGISTRY[config["post_process_strategy"]](),
           backend="numpy"
       )
       
       solution = ga.solve(medium_problem)
       assert solution is not None
   ```

2. **Run Tests (8min)**
   ```bash
   pytest tests/integration/test_ga_twoot_integration.py -v
   # Should pass all 4 tests
   ```

3. **Commit (2min)**
   ```bash
   git add tests/integration/test_ga_twoot_integration.py
   git commit -m "test(integration): Add GA + TwoOpt memetic tests for M15.3

   - Pure GA baseline (no post-processing)
   - Memetic GA (GA + TwoOptImprovement)
   - Performance comparison (memetic should improve)
   - String-based config (JSON/YAML simulation)

   4 tests validating User Decision Q3:
   'GA needs BOTH mutation AND post-processing'

   Lego composition: GA + TwoOpt = Memetic Algorithm"
   ```

**Acceptance Criteria:**

- [ ] Integration tests created
- [ ] All 4 tests pass
- [ ] Memetic algorithm validated
- [ ] String-based config tested
- [ ] File committed

---

## M15.4: ALGORITHM_MAP Refactor

**Prerequisites:**

- M15.3 complete (all strategies working)
- M14.6 complete (full pipeline)

**Objective:** Refactor ALGORITHM_MAP with lambda factories

**User Decision Q1:** Hybrid config (string + object with fallback)

---

### Task M15.4.1: Refactor ALGORITHM_MAP (60min)

**Process:**

1. **Update ALGORITHM_MAP (45min)**

   **Edit:** `code/src/benchmarking/runner.py` (or wherever ALGORITHM_MAP lives)

   ```python
   """
   Algorithm registry for benchmarking.

   ALGORITHM_MAP uses lambda factories for dependency injection.
   Enables composable algorithm configurations.

   Usage:
       # String-based instantiation
       algorithm = ALGORITHM_MAP["SA_2opt_move"]()
       
       # With kwargs override
       algorithm = ALGORITHM_MAP["GA_memetic"](population_size=50)
   """

   from typing import Dict, Callable, Any
   from ..algorithms.constructive import NearestNeighbor
   from ..algorithms.metaheuristics import SimulatedAnnealing, GeneticAlgorithm
   from ..algorithms.strategies import (
       NEIGHBOR_REGISTRY,
       MUTATION_REGISTRY,
       CROSSOVER_REGISTRY,
       IMPROVEMENT_REGISTRY,
       # DIRECT SINGLETON IMPORTS (compile-time safety for internal code)
       _RANDOM_SWAP,
       _RANDOM_INSERTION,
       _RANDOM_2OPT,
       _SWAP_MUTATION,
       _INSERTION_MUTATION,
       _INVERSION_MUTATION,
       _ORDER_CROSSOVER,
       # Strategy classes for custom instantiation
       TwoOptMoveStrategy,
       TwoOptImprovement,
   )


   # ============================================================================
   # ALGORITHM_MAP: String → Algorithm Factory
   # ============================================================================
   # DESIGN: Uses DIRECT SINGLETON REFERENCES (not string lookups) for compile-time safety
   # Registries are for USER-FACING config (JSON/YAML). ALGORITHM_MAP is INTERNAL composition.

   ALGORITHM_MAP: Dict[str, Callable[..., Any]] = {
       # ------------------------------------------------------------------------
       # Constructive Algorithms
       # ------------------------------------------------------------------------
       "NN": lambda **kwargs: NearestNeighbor(**kwargs),
       "nearest_neighbor": lambda **kwargs: NearestNeighbor(**kwargs),
       
       # ------------------------------------------------------------------------
       # Simulated Annealing (various neighbor strategies)
       # ------------------------------------------------------------------------
       "SA_random_swap": lambda **kwargs: SimulatedAnnealing(
           neighbor_strategy=_RANDOM_SWAP,  # DIRECT SINGLETON (not string lookup)
           **kwargs
       ),
       
       "SA_2opt_move": lambda **kwargs: SimulatedAnnealing(
           neighbor_strategy=TwoOptMoveStrategy(),  # FACTORY (stateful strategy)
           **kwargs
       ),
       
       "SA_random_2opt": lambda **kwargs: SimulatedAnnealing(
           neighbor_strategy=_RANDOM_2OPT,  # DIRECT SINGLETON
           **kwargs
       ),
       
       "SA_random_insertion": lambda **kwargs: SimulatedAnnealing(
           neighbor_strategy=_RANDOM_INSERTION,  # DIRECT SINGLETON
           **kwargs
       ),
       
       # ------------------------------------------------------------------------
       # Genetic Algorithm (pure, no post-processing)
       # ------------------------------------------------------------------------
       "GA": lambda **kwargs: GeneticAlgorithm(
           mutation_operator=_SWAP_MUTATION,  # DIRECT SINGLETON
           crossover_strategy=_ORDER_CROSSOVER,  # DIRECT SINGLETON
           post_process_strategy=None,
           **kwargs
       ),
       
       "GA_swap_ox": lambda **kwargs: GeneticAlgorithm(
           mutation_operator=_SWAP_MUTATION,  # DIRECT SINGLETON
           crossover_strategy=_ORDER_CROSSOVER,  # DIRECT SINGLETON
           **kwargs
       ),
       
       "GA_inversion_ox": lambda **kwargs: GeneticAlgorithm(
           mutation_operator=_INVERSION_MUTATION,  # DIRECT SINGLETON
           crossover_strategy=_ORDER_CROSSOVER,  # DIRECT SINGLETON
           **kwargs
       ),
       
       # ------------------------------------------------------------------------
       # Memetic Algorithms (GA + local search)
       # User Decision Q3: Both mutation AND post-processing
       # ------------------------------------------------------------------------
       "GA_memetic": lambda **kwargs: GeneticAlgorithm(
           mutation_operator=_SWAP_MUTATION,  # DIRECT SINGLETON
           crossover_strategy=_ORDER_CROSSOVER,  # DIRECT SINGLETON
           post_process_strategy=TwoOptImprovement(),  # FACTORY (stateful)
           **kwargs
       ),
       
       "GA_2opt": lambda **kwargs: GeneticAlgorithm(
           mutation_operator=_SWAP_MUTATION,  # DIRECT SINGLETON
           crossover_strategy=_ORDER_CROSSOVER,  # DIRECT SINGLETON
           post_process_strategy=TwoOptImprovement(),  # FACTORY (stateful)
           **kwargs
       ),
   }


   # ============================================================================
   # HELPER: Get algorithm by name (with kwargs override)
   # ============================================================================

   def get_algorithm(name: str, **kwargs) -> Any:
       """
       Instantiate algorithm by name with optional kwargs override.
       
       Args:
           name: Algorithm name (key in ALGORITHM_MAP)
           **kwargs: Override default parameters
       
       Returns:
           Algorithm instance
       
       Example:
           # Default configuration
           alg = get_algorithm("SA_2opt_move")
           
           # Override parameters
           alg = get_algorithm("GA_memetic", population_size=100, generations=200)
       """
       if name not in ALGORITHM_MAP:
           raise ValueError(f"Unknown algorithm: {name}. Available: {list(ALGORITHM_MAP.keys())}")
       
       factory = ALGORITHM_MAP[name]
       return factory(**kwargs)
   ```

2. **Create Tests (10min)**

   **Create:** `tests/unit/benchmarking/test_algorithm_map.py`

   ```python
   """Tests for ALGORITHM_MAP."""

   import pytest
   from code.src.benchmarking.runner import ALGORITHM_MAP, get_algorithm
   from code.src.algorithms.constructive import NearestNeighbor
   from code.src.algorithms.metaheuristics import SimulatedAnnealing, GeneticAlgorithm


   def test_algorithm_map_contains_expected_algorithms():
       """ALGORITHM_MAP should have all algorithm variants."""
       expected = [
           "NN", "nearest_neighbor",
           "SA_random_swap", "SA_2opt_move", "SA_random_2opt",
           "GA", "GA_swap_ox", "GA_inversion_ox",
           "GA_memetic", "GA_2opt"
       ]
       
       for name in expected:
           assert name in ALGORITHM_MAP


   def test_algorithm_factories_return_correct_types():
       """Factories should return algorithm instances."""
       nn = ALGORITHM_MAP["NN"]()
       assert isinstance(nn, NearestNeighbor)
       
       sa = ALGORITHM_MAP["SA_2opt_move"]()
       assert isinstance(sa, SimulatedAnnealing)
       
       ga = ALGORITHM_MAP["GA_memetic"]()
       assert isinstance(ga, GeneticAlgorithm)


   def test_get_algorithm_with_defaults():
       """get_algorithm should instantiate with defaults."""
       alg = get_algorithm("SA_2opt_move")
       assert isinstance(alg, SimulatedAnnealing)


   def test_get_algorithm_with_kwargs_override():
       """get_algorithm should accept kwargs override."""
       alg = get_algorithm("GA_memetic", population_size=50, generations=100)
       assert isinstance(alg, GeneticAlgorithm)
       # NOTE: Can't easily access parameters (no public API)
       # Trust that kwargs are passed correctly


   def test_get_algorithm_raises_on_unknown_name():
       """get_algorithm should raise ValueError for unknown algorithm."""
       with pytest.raises(ValueError, match="Unknown algorithm"):
           get_algorithm("NonexistentAlgorithm")
   ```

3. **Run Tests (3min)**
   ```bash
   pytest tests/unit/benchmarking/test_algorithm_map.py -v
   # Should pass all 5 tests
   ```

4. **Commit (2min)**
   ```bash
   git add code/src/benchmarking/runner.py tests/unit/benchmarking/test_algorithm_map.py
   git commit -m "refactor(benchmarking): Add ALGORITHM_MAP factories for M15.4

   - Lambda factories for dependency injection
   - SA variants: random_swap, 2opt_move, random_2opt
   - GA variants: pure, swap_ox, inversion_ox
   - Memetic variants: GA_memetic, GA_2opt (Q3: mutation + post-processing)
   - get_algorithm() helper with kwargs override

   User Decision Q1: Hybrid config (string + object fallback)
   String-based: algorithm = ALGORITHM_MAP['SA_2opt_move']()
   Object-based: algorithm = SimulatedAnnealing(neighbor_strategy=...)

   Lego composition: ALGORITHM_MAP composes strategies into algorithms
   5 tests: registry contents, types, defaults, kwargs, errors"
   ```

**Acceptance Criteria:**

- [ ] ALGORITHM_MAP refactored with lambdas
- [ ] All algorithm variants added
- [ ] get_algorithm() helper created
- [ ] All 5 tests pass
- [ ] File committed

---

**Update Task Log:**

```markdown
## M15: TwoOpt Integration
- **Status:** COMPLETE
- **Commits:** [SHAs for all tasks]
- **Files Created:**
  - two_opt_improvement.py (post-processing operator)
  - test_two_opt_improvement.py (3 tests)
  - test_ga_twoot_integration.py (4 memetic tests)
  - test_algorithm_map.py (5 tests)
- **Files Modified:**
  - strategies/__init__.py (TwoOpt in registries)
  - test_registries.py (updated coverage)
  - runner.py (ALGORITHM_MAP with factories)
- **User Decisions Implemented:**
  - Q1: Hybrid config (string + object)
  - Q2: max_iterations configurable (Move=1, Improvement=100)
  - Q3: post_process_strategy in GA (memetic algorithms)
- **Architecture Complete:**
  - Strategy Pattern: NeighborStrategy, MutationOperator, CrossoverStrategy, ImprovementOperator
  - Registry Pattern: String → strategy lookup
  - Factory Pattern: ALGORITHM_MAP with lambda factories
  - Lego Brick Composition: "Build SA with whichever improvement I want" ✓
- **Notes:** Full Strategy Pattern refactor complete, ready for M16 (parallelization)
```

---

> [!WARNING]
> **MISSING PHASES: Architectural Patterns from METAHEURISTIC_ARCHITECTURE_DECISIONS.md**
>
> The following phases are documented in the architecture decisions but NOT reflected in this task breakdown:
>
> **M16: Composition Patterns** (~6-8h) - DEFERRED TO FUTURE
>
> - M16.1: Adaptive Strategy Selection (temperature-based switching)
> - M16.2: Post-Processing Integration (SA → 2-opt polish)
> - M16.3: ILS Composition (perturbation + local search)
> - M16.4: VNS Composition (systematic neighborhood change)
>
> **M17: Advanced Improvement Heuristics** (~8-10h) - RESEARCH TOPIC
>
> - M17.1: Or-Opt Implementation (O(n²), no reversals)
> - M17.2: 3-Opt Implementation (O(n³), 8 reconnection cases)
> - M17.3: GPU Parallelization Assessment
> - M17.4: Performance Benchmarking (vs 2-opt baseline)
>
> **M18: Streaming Architecture** (~10-12h) - ADVANCED RESEARCH
>
> - M18.1: Meta-Metaheuristic Wrapper Design
> - M18.2: Chunk Size Calculation (VRAM-based)
> - M18.3: Multistart SA Implementation (P-Data)
> - M18.4: Cooperative Multistart (solution exchange)
>
> **M19: Lin-Kernighan Heuristic** (~15-20h) - PhD-LEVEL RESEARCH
>
> - M19.1: Variable k-opt Implementation
> - M19.2: Non-Sequential Move Generation
> - M19.3: Adaptive k Selection
> - M19.4: Benchmarking (target: 0.004% from optimal per Helsgaun)
>
> **Status:** These phases documented in architecture doc but not planned for current TCC scope.
> **Recommendation:** Complete M14-M15 first, then reassess scope for M16+.
>
> **See:** `METAHEURISTIC_ARCHITECTURE_DECISIONS.md` for complete specifications

---

# FUTURE WORK: Architectural Pattern Milestones (M16-M19)

## M16: Composition Patterns (~6-8h) [FUTURE WORK]

**Status:** 🔮 FUTURE - Depends on M14-M15 completion and validation

**Reference:** `METAHEURISTIC_ARCHITECTURE_DECISIONS.md` Section 1

**Prerequisites:**

- ✅ M14-M15 complete (strategy pattern working)
- ✅ SA comprehensive testing complete
- ✅ Performance baselines established

**Objective:** Implement metaheuristic composition patterns from architecture doc

---

### M16.1: Adaptive Strategy Selection Framework (2h)

**Goal:** Temperature-dependent strategy switching in SA

**Task M16.1.1: Design API for Adaptive Strategies (30min)**

Design decision: How to pass temperature to strategies?

**Option A:** Extend NeighborStrategy protocol

```python
class NeighborStrategy(Protocol):
    def generate_neighbor(self, tour, problem, xp, temperature: float = None): ...
```

**Pros:** Explicit, strategies know temperature  
**Cons:** Breaking change, all strategies need update

**Option B:** Wrapper with SA state access

```python
class AdaptiveWrapper:
    def __init__(self, strategies: Dict[float, NeighborStrategy], sa_instance):
        self.strategies = strategies
        self.sa = sa_instance
```

**Pros:** No protocol change  
**Cons:** Tight coupling with SA

**Option C:** Internal SA strategy pool

```python
sa = SimulatedAnnealing(
    strategy_pool={
        1000.0: RandomSwap(),
        500.0: Random2Opt(),
        100.0: TwoOptMove()
    }
)
```

**Pros:** Clean API, encapsulated  
**Cons:** SA-specific, not generalizable

**Deliverable:** Design document with chosen option + rationale

---

**Task M16.1.2: Implement Chosen Design (60min)**

1. Implement adaptive strategy selection
2. Add configuration parameters
3. Unit tests for strategy switching logic

**Acceptance Criteria:**

- Strategy switches at correct temperature thresholds
- Backward compatible (optional feature)
- Tests verify switching behavior

---

**Task M16.1.3: Benchmark Adaptive vs Fixed (30min)**

Compare on 3 TSP instances (n=100, 300, 500):

- Fixed RandomSwap only
- Fixed Random2Opt only
- Adaptive (high temp → swap, low temp → 2opt)

**Metrics:**

- Final solution quality
- Convergence speed
- Time overhead of switching

**Deliverable:** Performance report in `research/results/adaptive_strategies_benchmark.md`

---

### M16.2: Post-Processing Integration (1.5h)

**Goal:** Optional post-processing after metaheuristic completion

**Task M16.2.1: Design Post-Processing API (20min)**

**Option A:** Manual composition (current approach)

```python
solution = sa.solve(problem)
final = two_opt.improve(solution.tour, problem, xp)
```

**Option B:** Optional parameter in metaheuristic

```python
sa = SimulatedAnnealing(
    neighbor_strategy=RandomSwap(),
    post_process=TwoOptImprovement(max_iterations=1000)  # Optional
)
```

**Decision criteria:**

- User convenience vs flexibility
- Code complexity
- Performance overhead if unused

**Deliverable:** Design decision document

---

**Task M16.2.2: Implement Post-Processing (if Option B chosen) (40min)**

1. Add optional `post_process: Optional[ImprovementOperator]` parameter to SA/GA
2. Call after main loop: `if self.post_process: solution = self.post_process.improve(...)`
3. Update docstrings and examples

---

**Task M16.2.3: Benchmark Impact (30min)**

Test on TSP instances:

- SA alone (baseline)
- SA + 2opt post-processing
- SA with 2opt neighbor (no post-processing)

**Question:** Is post-processing better than using 2opt AS the neighbor strategy?

**Deliverable:** Comparative analysis in `research/results/post_processing_impact.md`

---

### M16.3: Iterated Local Search (ILS) (2h)

**Goal:** Perturbation + local search loop

**Task M16.3.1: ILS Algorithm Implementation (60min)**

```python
class IteratedLocalSearch:
    def __init__(
        self,
        local_search: ImprovementOperator,
        perturbation: NeighborStrategy,
        acceptance_criterion: Callable
    ):
        ...
    
    def solve(self, problem: Problem) -> Solution:
        current = greedy_initial_solution(problem)
        current = self.local_search.improve(current, problem, xp)
        
        best = current
        
        for iteration in range(self.max_iterations):
            # Perturb
            perturbed = self.perturbation.generate_neighbor(current, problem, xp)
            
            # Improve
            improved = self.local_search.improve(perturbed, problem, xp)
            
            # Accept or reject
            if self.acceptance_criterion(improved, current):
                current = improved
                if improved.cost < best.cost:
                    best = improved
        
        return best
```

**Files to create:**

- `code/src/algorithms/metaheuristics/iterated_local_search.py`
- `tests/unit/test_iterated_local_search.py`

---

**Task M16.3.2: Perturbation Strategies (30min)**

Create 2-3 perturbation strategies:

1. **MultiSwapPerturbation:** Apply k random swaps (k=3-5)
2. **SegmentReversalPerturbation:** Reverse longer segments than 2opt
3. **AdaptivePerturbation:** Strength increases if stuck

**Files:** `code/src/algorithms/strategies/perturbation_strategies.py`

---

**Task M16.3.3: ILS Benchmark (30min)**

Test on TSP (n=100-500):

- SA baseline
- GA baseline  
- ILS (2opt local search + multiswap perturbation)

**Compare:**

- Solution quality
- Runtime
- Convergence behavior

**Deliverable:** `research/results/ils_benchmark.md`

---

### M16.4: Variable Neighborhood Search (VNS) (2h)

**Goal:** Systematic neighborhood change

**Task M16.4.1: VNS Algorithm (60min)**

```python
class VariableNeighborhoodSearch:
    def __init__(self, neighborhoods: List[NeighborStrategy]):
        self.neighborhoods = neighborhoods
    
    def solve(self, problem: Problem) -> Solution:
        current = initial_solution(problem)
        k = 0  # Neighborhood index
        
        while not self.termination():
            # Shake with k-th neighborhood
            candidate = self.neighborhoods[k].generate_neighbor(current, problem, xp)
            
            # Local search (first improvement)
            improved = self._local_search(candidate, self.neighborhoods[k], problem)
            
            if improved.cost < current.cost:
                current = improved
                k = 0  # Restart with first neighborhood
            else:
                k = (k + 1) % len(self.neighborhoods)  # Try next
        
        return current
```

---

**Task M16.4.2: Neighborhood Sequence Design (30min)**

Create effective VNS neighborhood sequence:

1. RandomSwap (smallest change)
2. RandomInsertion (medium change)
3. Random2Opt (larger change)
4. MultiSwap (largest change)

**Rationale:** Increasing neighborhood size for progressive diversification

---

**Task M16.4.3: VNS Benchmark (30min)**

Test on TSP instances:

- VNS (4 neighborhoods)
- SA (single neighborhood)
- Compare convergence and quality

**Deliverable:** `research/results/vns_benchmark.md`

---

**M16 DELIVERABLES SUMMARY:**

- [ ] 4 algorithm implementations (Adaptive, Post-Process, ILS, VNS)
- [ ] 3-4 benchmark reports
- [ ] Design decision documents
- [ ] Updated user guides with composition examples

---

## M17: Advanced Improvement Heuristics (~8-10h) [RESEARCH]

**Reference:** `METAHEURISTIC_ARCHITECTURE_DECISIONS.md` Section 3

**Prerequisites:**

- M15 complete (2-opt working)
- GPU vs CPU performance characterized

**Objective:** Implement and benchmark k-opt heuristics beyond 2-opt

### M17.1: Or-Opt Implementation

**Goal:** Sequence relocation heuristic (no path reversals)

**Complexity:** O(n²) for each sequence length (1, 2, 3)

**Algorithm:**

```python
def or_opt_move(tour, start, length, insert_pos):
    """
    Remove segment tour[start:start+length],
    insert at insert_pos WITHOUT reversing.
    """
    segment = tour[start:start+length]
    new_tour = tour[:start] + tour[start+length:]
    new_tour = new_tour[:insert_pos] + segment + new_tour[insert_pos:]
    return new_tour
```

**Deliverables:**

1. OrOptImprovement class (CPU)
2. GPU parallelization assessment
3. Benchmark vs 2-opt (quality, runtime)
4. Integration as ImprovementOperator

---

### M17.2: 3-Opt Implementation

**Goal:** Remove 3 edges, try 8 reconnection patterns

**Complexity:** O(n³) - 551,300 combinations for n=150

**Challenge:** 8 reconnection cases, complex logic

**GPU Viability:** Moderate (large search space, but complex kernel)

**Deliverables:**

1. ThreeOptImprovement class (CPU only initially)
2. GPU feasibility study
3. Benchmark vs 2-opt (diminishing returns analysis)
4. Documentation of when to use 3-opt

---

### M17.3: GPU Parallelization Assessment

**Goal:** Characterize GPU benefit for each k-opt variant

**Metrics:**

- Search space size (combinations evaluated)
- Kernel complexity (branching, memory access)
- Transfer overhead vs computation time
- Speedup factor (GPU vs CPU)

**Expected Results:**

| Heuristic | Search Space (n=150) | GPU Benefit | Priority |
|-----------|---------------------|-------------|----------|
| 2-opt | 11,175 | ⭐⭐⭐⭐⭐ 10-50x | DONE (M15) |
| Or-opt | ~33,525 | ⭐⭐⭐⭐ 10-40x | High |
| 3-opt | 551,300 | ⭐⭐⭐ 5-20x | Medium |

**Deliverables:**

1. Performance characterization report
2. GPU implementation recommendations
3. Hardware requirement analysis (VRAM, compute capability)

---

### M17.4: Performance Benchmarking

**Goal:** Establish baselines for all improvement heuristics

**Test Problems:** eil51, ch150, ts225

**Metrics:**

- Solution quality (% from optimal)
- Runtime (CPU, GPU if applicable)
- Iterations to convergence
- Memory usage

**Deliverables:**

1. Comprehensive benchmark suite
2. Performance comparison table
3. Recommendation guide (when to use which heuristic)

---

## M18: Streaming Architecture (~10-12h) [ADVANCED]

**Reference:** `METAHEURISTIC_ARCHITECTURE_DECISIONS.md` Section 4

**Prerequisites:**

- M14-M15 complete
- SA performance characterized
- VRAM constraints understood (4GB GTX 1050)

**Objective:** Enable P-Data algorithms that exceed VRAM capacity

### M18.1: Meta-Metaheuristic Wrapper

**Goal:** Transparent chunking for large-scale P-Data problems

**Pattern:**

```python
class StreamingMetaheuristic:
    def solve(self, problem, total_instances):
        chunk_size = self._calculate_chunk_size(problem)
        results = []
        
        for chunk in chunks(total_instances, chunk_size):
            chunk_results = self._process_chunk_gpu(chunk, problem)
            results.extend(chunk_results)
        
        return self._aggregate_results(results)
```

**Deliverables:**

1. StreamingMetaheuristic base class
2. Chunk size calculation (VRAM-based)
3. Progress tracking across chunks

---

### M18.2: Chunk Size Calculation

**Goal:** Determine optimal chunk size for VRAM capacity

**Formula:**

```python
def calculate_chunk_size(problem, available_vram, algorithm):
    shared_vram = problem.dimension ** 2 * 8  # Distance matrix
    per_instance_vram = {
        "SA": 3 * problem.dimension * 8,
        "GA": 2 * population_size * problem.dimension * 8,
    }[algorithm]
    
    available_for_instances = available_vram * 0.9 - shared_vram
    return int(available_for_instances / per_instance_vram)
```

**Deliverables:**

1. Chunk size calculator utility
2. VRAM capacity detection (CuPy device query)
3. Safety margin configuration (default 90%)

---

### M18.3: Multistart SA (P-Data)

**Goal:** Run N independent SA chains in parallel/streamed

**Use Case:** 1,000 SA chains with different seeds, find best

**Without Streaming:** 1,000 × 10s = 10,000s (2.8 hours sequential)
**With Streaming (100/chunk):** 10 × 10s = 100s (1.7 minutes)

**Deliverables:**

1. StreamingSA implementation
2. Seed management across chunks
3. Best solution aggregation
4. Benchmark vs sequential

---

### M18.4: Cooperative Multistart

**Goal:** Solution exchange between chunks (future research)

**Pattern:**

- Chunk 1 finishes → share best solution
- Chunk 2 starts with best from Chunk 1
- Iterative improvement across chunks

**Status:** Research topic, not for current TCC

---

## M19: Lin-Kernighan Heuristic (~15-20h) [PhD-LEVEL]

**Reference:** `METAHEURISTIC_ARCHITECTURE_DECISIONS.md` Section 3.2

**Prerequisites:**

- M17 complete (k-opt heuristics understood)
- Literature review of Lin-Kernighan variants

**Objective:** Variable k-opt with adaptive search

**Complexity:** O(n²) to O(n⁶) depending on tour quality

**Expected Quality:** 0.004% from optimal (Helsgaun benchmark)

**Status:** DEFERRED - PhD-level research topic, beyond TCC scope

**If Pursued:**

1. Literature review (Helsgaun 2000, Lin 1965)
2. Algorithm design (non-sequential moves)
3. Implementation (CPU only - irregular control flow)
4. Benchmarking on TSPLIB instances
5. Comparison with existing solvers (Concorde, LKH)

---

# Summary: M14-M19 Roadmap

| Milestone | Scope | Complexity | Priority | Status |
|-----------|-------|----------|----------|--------|
| **M14-M15** | Strategy Pattern Refactor | Medium | **CRITICAL** | ✅ CURRENT WORK |
| **M16** | Composition Patterns | Medium | High | 📋 PLANNED (deferred) |
| **M17** | Advanced k-opt | High | Medium | 🔬 RESEARCH |
| **M18** | Streaming P-Data | High | Low | 🚀 ADVANCED |
| **M19** | Lin-Kernighan | Very High | Research | 🎓 PhD-LEVEL |

**Recommendation for TCC:**

1. **Complete M14-M15 fully** (strategy pattern + TwoOpt)
2. **Implement M16.2** (post-processing) for demonstration
3. **Document M16-M19** as future work with architecture already designed
4. **Focus on:** Educational value, clean architecture, reproducible benchmarks

---

**END OF M14-M15 TASK BREAKDOWN**
**Architecture foundations established, ready for composition patterns (M16+)**
**Jumping to M15.1 (TwoOpt Integration) as requested**

---

# PHASE 7: TwoOpt Integration (3-4h)

**Status:** ❌ NOT STARTED - Advanced integration phase

## M15.1: TwoOptMove Strategy (Wrap TwoOptCPU/GPU)

**Status:** ❌ NOT STARTED - Wrapper for existing 2-opt implementations

**Prerequisites:**

- M14.6 complete (basic integration working) ❌
- Existing TwoOptCPU and TwoOptGPU implementations (should exist)

**Objective:** Wrap existing 2-opt into strategy pattern for use in SA and GA

**Prerequisites:**

- M14.3 complete (SA strategies working)
- Understanding: TwoOptCPU/GPU exist but are NOT strategies (yet)

**Context Files to Read:**

- `code/src/algorithms/improvement/two_opt_cpu.py` (lines 1-100, understand API)
- `code/src/algorithms/improvement/two_opt_gpu.py` (lines 1-80, GPU version)
- `code/src/protocols/strategy_protocols.py` (ImprovementOperator protocol)

**Objective:** Create strategies that wrap existing TwoOpt implementations

**Key Decision (from User Q2):** TwoOptMoveStrategy should accept max_iterations parameter

---

### Task M15.1.1: TwoOptMoveStrategy (Wrapper for SA) (60min)

**Process:**

1. **Understand Current TwoOpt API (15min)**
   ```bash
   # Read TwoOptCPU.improve_tour signature
   code/src/algorithms/improvement/two_opt_cpu.py:30-60
   ```

   **Expected signature:**
   ```python
   def improve_tour(self, tour, distances, max_iterations=100):
       # Iterative 2-opt until no improvement
       # Returns improved tour
   ```

2. **Create Wrapper Strategy (30min)**

   **Append to:** `code/src/algorithms/strategies/neighbor_strategies.py`

   ```python
   class TwoOptMoveStrategy:
       """
       Generate neighbor using BEST 2-opt move (not random).
       
       Wraps TwoOptCPU/GPU for single-move generation in SA.
       
       Characteristics:
           - Greedy (selects best move, not random)
           - Uses problem distances (informed search)
           - Slower than random strategies (O(n²) evaluation)
           - Higher acceptance rate in SA (moves tend to improve)
       
       Use Cases:
           - Late SA iterations (intensification)
           - Hybrid SA (alternate with random strategies)
           - High-quality solutions (at cost of speed)
       
       Parameters:
           max_iterations: How many 2-opt iterations to run
               - Default: 1 (single best move for SA)
               - Higher values: More intensification (slower)
           backend: "cpu" or "gpu"
       """
       
       def __init__(self, max_iterations: int = 1, backend: str = "cpu"):
           """
           Initialize TwoOptMove strategy.
           
           Args:
               max_iterations: Number of 2-opt iterations
                   - 1 = single best move (recommended for SA)
                   - >1 = multiple iterations (use for post-processing)
               backend: "cpu" or "gpu"
           """
           self.max_iterations = max_iterations
           self.backend = backend
           
           # Lazy import to avoid circular dependencies
           if backend == "cpu":
               from ...improvement.two_opt_cpu import TwoOptCPU
               self.optimizer = TwoOptCPU()
           elif backend == "gpu":
               from ...improvement.two_opt_gpu import TwoOptGPU
               self.optimizer = TwoOptGPU()
           else:
               raise ValueError(f"Unknown backend: {backend}")
       
       def generate_neighbor(
           self,
           current_tour: List[int],
           problem: Problem,
           xp: BackendModule
       ) -> List[int]:
           """
           Generate neighbor using best 2-opt move.
           
           Note: xp parameter ignored (TwoOpt uses its own backend).
           """
           # TwoOptCPU.improve_tour expects distances as numpy array
           distances = problem.distances
           
           # Run 2-opt for max_iterations
           improved = self.optimizer.improve_tour(
               tour=current_tour,
               distances=distances,
               max_iterations=self.max_iterations
           )
           
           return improved
   ```

3. **Add Tests (10min)**

   **Append to:** `tests/unit/strategies/test_neighbor_strategies.py`

   ```python
   def test_two_opt_move_strategy_returns_valid_tour(problem_4city):
       """TwoOptMove should return valid tour."""
       from code.src.algorithms.strategies.neighbor_strategies import TwoOptMoveStrategy
       strategy = TwoOptMoveStrategy(max_iterations=1, backend="cpu")
       tour = [0, 3, 2, 1, 0]  # Suboptimal tour
       
       neighbor = strategy.generate_neighbor(tour, problem_4city, np)
       
       assert len(neighbor) == len(tour)
       assert neighbor[0] == 0
       assert neighbor[-1] == 0
       assert set(neighbor) == set(tour)


   def test_two_opt_move_improves_or_maintains_cost(problem_4city):
       """TwoOptMove should not worsen tour (greedy)."""
       from code.src.algorithms.strategies.neighbor_strategies import TwoOptMoveStrategy
       strategy = TwoOptMoveStrategy(max_iterations=1, backend="cpu")
       
       tour = [0, 3, 2, 1, 0]
       original_cost = calculate_tour_cost(tour, problem_4city.distances)
       
       neighbor = strategy.generate_neighbor(tour, problem_4city, np)
       neighbor_cost = calculate_tour_cost(neighbor, problem_4city.distances)
       
       assert neighbor_cost <= original_cost  # Should improve or maintain


   def calculate_tour_cost(tour, distances):
       """Helper: Calculate tour cost."""
       return sum(distances[tour[i], tour[i+1]] for i in range(len(tour)-1))
   ```

4. **Run Tests (3min)**
   ```bash
   pytest tests/unit/strategies/test_neighbor_strategies.py::test_two_opt_move -v
   ```

5. **Commit (2min)**
   ```bash
   git add -u
   git commit -m "feat(strategies): Add TwoOptMoveStrategy for M15.1

   - Wraps TwoOptCPU/GPU for SA neighbor generation
   - Greedy strategy (best move, not random)
   - Configurable max_iterations (default=1 for SA)
   - Supports both CPU and GPU backends

   User Decision Q2: max_iterations is configurable
   User Vision: 'I build SA with whichever improvement I want'"
   ```

**Acceptance Criteria:**

- [ ] TwoOptMoveStrategy created
- [ ] Wraps TwoOptCPU and TwoOptGPU
- [ ] max_iterations parameter (user Q2)
- [ ] Tests pass (validity, improvement)
- [ ] File committed

---

**M15.1.1 COMPLETE**

---
