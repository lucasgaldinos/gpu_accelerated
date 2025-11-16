# Metaheuristic Architecture Decisions

**Date:** 2025-01-28 (Updated: 2025-11-07)  
**Context:** M14-M15 Strategy Pattern Refactor - Architectural Design Decisions  
**Status:** Active Design Document  
**Related:** `SA_COMPREHENSIVE_ANALYSIS.md`, `M14_M15_DETAILED_TASKS.md`

---

## Table of contents

- [Metaheuristic Architecture Decisions](#metaheuristic-architecture-decisions)
  - [Table of contents](#table-of-contents)
  - [Purpose](#purpose)
  - [Table of Contents](#table-of-contents-1)
  - [Section 1: Composition Patterns](#section-1-composition-patterns)
    - [1.1 Post-Processing (Memetic Algorithms)](#11-post-processing-memetic-algorithms)
    - [1.2 Iterated Local Search (ILS)](#12-iterated-local-search-ils)
    - [1.3 Variable Neighborhood Search (VNS)](#13-variable-neighborhood-search-vns)
    - [1.4 Adaptive Strategy Selection](#14-adaptive-strategy-selection)
  - [Section 2: VRAM Management](#section-2-vram-management)
    - [2.1 GPU Guardrails](#21-gpu-guardrails)
      - [Distance Matrix (All Algorithms)](#distance-matrix-all-algorithms)
      - [SA Working Buffers](#sa-working-buffers)
      - [GA Working Buffers](#ga-working-buffers)
      - [ACO Working Buffers](#aco-working-buffers)
      - [Summary Table](#summary-table)
    - [2.2 Buffer Reuse Patterns](#22-buffer-reuse-patterns)
    - [2.3 Memory Layout Considerations](#23-memory-layout-considerations)
  - [Section 3: Improvement Heuristics Beyond 2-Opt](#section-3-improvement-heuristics-beyond-2-opt)
    - [3.1 3-Opt Moves](#31-3-opt-moves)
    - [3.2 Lin-Kernighan Heuristic](#32-lin-kernighan-heuristic)
    - [3.3 Or-Opt Moves](#33-or-opt-moves)
    - [3.4 GPU Parallelization Viability](#34-gpu-parallelization-viability)
  - [Section 4: Streaming Architecture](#section-4-streaming-architecture)
    - [4.1 Meta-Metaheuristic Wrapper](#41-meta-metaheuristic-wrapper)
    - [4.2 P-Data Chunking Strategy](#42-p-data-chunking-strategy)
    - [4.3 Future Work](#43-future-work)
  - [References](#references)
    - [Academic Papers](#academic-papers)
    - [Online Resources (PHASE 1 Research)](#online-resources-phase-1-research)
  - [Document Maintenance](#document-maintenance)


## Purpose

This document consolidates architectural decisions for metaheuristic algorithm design, addressing questions that arose during SA comprehensive testing and strategy pattern refactoring. It serves as the **authoritative reference** for:

1. **Composition Patterns**: How to combine metaheuristics (ILS, VNS, Adaptive, Post-processing)
2. **VRAM Management**: GPU memory constraints and buffer allocation strategies
3. **Improvement Heuristics**: Beyond 2-opt (3-opt, Lin-Kernighan, Or-opt)
4. **Streaming Architecture**: Meta-metaheuristic layer for P-Data algorithms

**Audience:** Developers implementing M14-M16 milestones, future algorithm extensions

**Scope:** Cross-cutting architectural concerns affecting SA, GA, ACO, and future metaheuristics

---

## Table of Contents

- [Metaheuristic Architecture Decisions](#metaheuristic-architecture-decisions)
  - [Table of contents](#table-of-contents)
  - [Purpose](#purpose)
  - [Table of Contents](#table-of-contents-1)
  - [Section 1: Composition Patterns](#section-1-composition-patterns)
    - [1.1 Post-Processing (Memetic Algorithms)](#11-post-processing-memetic-algorithms)
    - [1.2 Iterated Local Search (ILS)](#12-iterated-local-search-ils)
    - [1.3 Variable Neighborhood Search (VNS)](#13-variable-neighborhood-search-vns)
    - [1.4 Adaptive Strategy Selection](#14-adaptive-strategy-selection)
  - [Section 2: VRAM Management](#section-2-vram-management)
    - [2.1 GPU Guardrails](#21-gpu-guardrails)
      - [Distance Matrix (All Algorithms)](#distance-matrix-all-algorithms)
      - [SA Working Buffers](#sa-working-buffers)
      - [GA Working Buffers](#ga-working-buffers)
      - [ACO Working Buffers](#aco-working-buffers)
      - [Summary Table](#summary-table)
    - [2.2 Buffer Reuse Patterns](#22-buffer-reuse-patterns)
    - [2.3 Memory Layout Considerations](#23-memory-layout-considerations)
  - [Section 3: Improvement Heuristics Beyond 2-Opt](#section-3-improvement-heuristics-beyond-2-opt)
    - [3.1 3-Opt Moves](#31-3-opt-moves)
    - [3.2 Lin-Kernighan Heuristic](#32-lin-kernighan-heuristic)
    - [3.3 Or-Opt Moves](#33-or-opt-moves)
    - [3.4 GPU Parallelization Viability](#34-gpu-parallelization-viability)
  - [Section 4: Streaming Architecture](#section-4-streaming-architecture)
    - [4.1 Meta-Metaheuristic Wrapper](#41-meta-metaheuristic-wrapper)
    - [4.2 P-Data Chunking Strategy](#42-p-data-chunking-strategy)
    - [4.3 Future Work](#43-future-work)
  - [References](#references)
    - [Academic Papers](#academic-papers)
    - [Online Resources (PHASE 1 Research)](#online-resources-phase-1-research)
  - [Document Maintenance](#document-maintenance)

---

## Section 1: Composition Patterns

**Question (SA_COMPREHENSIVE_ANALYSIS.md, Lines 624, 633, 676):**
> "What does post-processing mean? Why ILS and not another algorithm? Where is VNS? Is there an adaptive strategy?"

**Answer:** Metaheuristics can be **composed** using multiple patterns. This section defines each pattern with academic grounding.

---

### 1.1 Post-Processing (Memetic Algorithms)

**Definition:** Apply a local search **after** the main metaheuristic to polish the solution.

**Pattern:**

```python
# Hybrid approach: SA + Greedy Polish
solution = SimulatedAnnealing(
    neighbor_strategy=Random2OptStrategy(),
    max_iterations=200000
).solve(problem)

# Post-processing: Greedy 2-opt until no improvement
final_solution = TwoOptImprovement(
    max_iterations=1000  # Or until convergence
).improve(solution, problem)
```

**Academic Term:** **Memetic Algorithm** (Moscato, 1989)
> "Memetic algorithms combine population-based search with local improvement procedures applied to each individual."

**For SA (single solution, not population):**

- SA explores broadly (stochastic)
- 2-opt improvement exploits locally (deterministic)
- **Result:** Better solution quality, minimal additional time

**Use Cases:**

| Algorithm | Post-Processing | Benefit |
|-----------|----------------|---------|
| **SA** | 2-opt/3-opt improvement | Refine final basin (5-10% better) |
| **GA** | Apply to best individual each generation | Memetic GA (30-50% better) |
| **ACO** | Polish best-so-far tour | Remove pheromone artifacts |

**Implementation:**

```python
# GA example (User Question: Q3 from SA doc)
ga = GeneticAlgorithm(
    mutation_operator=SwapMutation(),
    crossover_strategy=OrderCrossover(),
    post_process_strategy=TwoOptImprovement(max_iterations=100)  # OPTIONAL
)

# After each generation, best individual is improved
solution = ga.solve(problem)
```

**Key Decision (from M14.4.3):**

- `post_process_strategy` parameter is **OPTIONAL** in GA
- SA does NOT have this parameter (apply manually after `solve()`)
- **Rationale:** GA iterates generations (natural hook), SA is single run

**References:**

- Moscato, P. (1989). "On Evolution, Search, Optimization, Genetic Algorithms and Martial Arts: Towards Memetic Algorithms"
- Merz, P., & Freisleben, B. (2000). "Fitness landscape analysis and memetic algorithms for the quadratic assignment problem"

---

### 1.2 Iterated Local Search (ILS)

**Definition:** Escape local optima via **perturbation** + **restart** from perturbed solution.

**Pattern:**

```python
# ILS = Local Search + Perturbation + Acceptance
current = greedy_initial_solution(problem)

for iteration in range(max_iterations):
    # 1. Local search to local optimum
    local_optimum = local_search(current, problem)
    
    # 2. PERTURBATION: Kick out of basin
    perturbed = perturbation(local_optimum, strength=5)
    
    # 3. Acceptance criterion (similar to SA)
    if accept(perturbed, current, criterion):
        current = perturbed
```

**Relationship to SA:**

From UPF repository (PHASE 1 research):
> "Much like simulated annealing, ILS escapes from local optima by applying perturbations to the current local minimum."

**Key Differences:**

| Aspect | SA | ILS |
|--------|----|----|
| **Starting point** | Random | Greedy local optimum |
| **Move type** | Small random neighbor | **Perturbation** (large disruption) |
| **Acceptance** | Metropolis (probabilistic) | Deterministic or threshold |
| **Temperature** | Gradually decreasing | None (or fixed threshold) |

**ILS Algorithm (IRIDIA slides):**

```
1. s₀ = GenerateInitialSolution()
2. s* = LocalSearch(s₀)           ← Find first local optimum
3. repeat:
     s' = Perturbation(s*, history)  ← KICK (not random neighbor!)
     s'' = LocalSearch(s')            ← Search from perturbed state
     s* = AcceptanceCriterion(s*, s'', history)
   until termination
```

**Perturbation Strategies:**

```python
# Weak perturbation (3-5 moves)
def weak_perturbation(tour):
    for _ in range(3):
        tour = random_swap(tour)
    return tour

# Strong perturbation (n/4 moves)
def strong_perturbation(tour, n):
    for _ in range(n // 4):
        tour = random_2opt(tour)
    return tour

# Adaptive perturbation (based on history)
def adaptive_perturbation(tour, stuck_iterations):
    strength = min(10, stuck_iterations // 100)
    for _ in range(strength):
        tour = random_insertion(tour)
    return tour
```

**Use Cases:**

- **Problem:** SA stuck in local optimum despite high iterations
- **Solution:** ILS with stronger perturbations than SA's random neighbors
- **Example:** TSP with clustered cities (need to break cluster structure)

**Why ILS and not another algorithm?**

**Answer:** ILS is **complementary** to SA:

- SA: Probabilistic acceptance, gradual cooling
- ILS: Deterministic acceptance, fixed perturbation strength
- **Both escape local optima**, but ILS uses **larger kicks**

**Implementation Status:** Not implemented. Future work (M16+).

**Would fit in strategy pattern:**

```python
# Hypothetical composition
class ILS_Strategy:
    def __init__(self, local_search: ImprovementOperator, perturbation_strength: int):
        self.local_search = local_search
        self.perturbation_strength = perturbation_strength
    
    def solve(self, problem):
        current = self.local_search.improve(initial_solution(problem), problem)
        for _ in range(iterations):
            perturbed = self._perturbation(current, self.perturbation_strength)
            improved = self.local_search.improve(perturbed, problem)
            if improved.cost < current.cost:
                current = improved
        return current
```

**References:**

- Lourenço, H. R., Martin, O. C., & Stützle, T. (2003). "Iterated Local Search" (Handbook of Metaheuristics)
- IRIDIA: "ILS - Iterated Local Search" (slides from PHASE 1 research)

---

### 1.3 Variable Neighborhood Search (VNS)

**Definition:** Systematically explore different **neighborhood structures** to escape local optima.

**Pattern:**

```python
# VNS = Shake + Local Search + Neighborhood Change
neighborhoods = [SwapNeighborhood(), InsertionNeighborhood(), TwoOptNeighborhood()]

current = initial_solution(problem)
k = 0  # Neighborhood index

while not termination:
    # 1. SHAKE: Perturb with k-th neighborhood
    perturbed = shake(current, neighborhoods[k])
    
    # 2. LOCAL SEARCH: Improve with SAME neighborhood
    improved = local_search(perturbed, neighborhoods[k], problem)
    
    # 3. MOVE OR CHANGE NEIGHBORHOOD
    if improved.cost < current.cost:
        current = improved
        k = 0  # Restart from first neighborhood
    else:
        k = (k + 1) % len(neighborhoods)  # Try next neighborhood
```

**From Wikipedia (PHASE 1 research):**
> "VNS systematically changes neighborhood in two phases: descent to local optimum, then perturbation to escape."

**From Medium TSP Tutorial:**
> "After perturbing with shaking, VNS applies local search to find better solution in new region."

**Key Insight:** **Dual process** - Shake AND Search use different neighborhoods.

**VNS Algorithm (SciSpace tutorial):**

```
1. Initialization: Select neighborhood structures Nₖ (k=1...kₘₐₓ)
2. repeat:
     k ← 1
     while k ≤ kₘₐₓ:
         (a) Shaking: Generate x' ∈ Nₖ(x) randomly
         (b) Local search: x'' ← LocalSearch(x')
         (c) Move or not:
             if f(x'') < f(x):
                 x ← x''
                 k ← 1  # Success: restart
             else:
                 k ← k+1  # Failure: try next neighborhood
   until termination
```

**Neighborhood Structures for TSP:**

```python
# Example VNS configuration
neighborhoods = [
    # k=1: Small perturbations
    SwapNeighborhood(),           # 2 cities
    
    # k=2: Medium perturbations  
    InsertionNeighborhood(),      # Remove + reinsert
    
    # k=3: Large perturbations
    TwoOptNeighborhood(),         # Segment reversal
    
    # k=4: Very large perturbations
    ThreeOptNeighborhood(),       # 3 edges removed
    
    # k=5: Structural changes
    OrOptNeighborhood(size=2),    # Relocate 2-city sequence
]
```

**VNS vs SA vs ILS:**

| Aspect | SA | ILS | VNS |
|--------|----|----|-----|
| **Escape mechanism** | Temperature | Perturbation | **Neighborhood change** |
| **Neighborhoods** | Fixed (1 type) | Fixed (1 perturbation) | **Multiple systematic** |
| **Acceptance** | Probabilistic | Threshold | **Deterministic (if better)** |
| **Search direction** | Random walk | Restart | **Systematic exploration** |

**Use Cases:**

- **Problem:** Unknown which neighborhood structure is best
- **Solution:** VNS tries all systematically
- **Example:** TSP with mixed structure (clusters + random)

**Why not in `perturbation_strategies.py`?**

**Answer:** Good observation! Could be organized as:

```
strategies/
├── neighbor_strategies.py       # SA: single neighborhood
├── perturbation_strategies.py   # ILS: kick functions
└── vns_strategies.py            # VNS: neighborhood sequences
```

**However:** VNS is **meta-strategy** (uses multiple neighbor strategies), not atomic strategy.

**Better design:**

```python
# VNS as algorithm, not strategy
class VariableNeighborhoodSearch:
    def __init__(self, neighborhoods: List[NeighborStrategy]):
        self.neighborhoods = neighborhoods
    
    def solve(self, problem):
        # Uses neighbor_strategies as COMPONENTS
        current = initial_solution(problem)
        k = 0
        while not done:
            perturbed = self.neighborhoods[k].generate_neighbor(current, problem, xp)
            improved = local_search(perturbed, self.neighborhoods[k])
            if improved < current:
                current = improved
                k = 0
            else:
                k += 1
        return current
```

**Implementation Status:** Not implemented. Future work (M16+).

**References:**

- Hansen, P., & Mladenović, N. (2001). "Variable neighborhood search: Principles and applications"
- Wikipedia: "Variable neighborhood search" (PHASE 1 research)
- Medium: "Solving the Traveling Salesman Problem with VNS" (PHASE 1 research)

---

### 1.4 Adaptive Strategy Selection

**Definition:** **Dynamically switch** neighbor strategies based on **algorithm state** (temperature, iteration, success rate).

**Pattern:**

```python
class AdaptiveNeighborStrategy:
    """
    Switch strategy based on temperature or iteration count.
    
    Rationale:
    - High temp: Fast random exploration (RandomSwap)
    - Mid temp: Balanced search (RandomInsertion)  
    - Low temp: Quality improvement (TwoOptMove)
    """
    
    def __init__(self, backend: str = "numpy"):
        self.backend = backend
        self.fast_strategy = RandomSwapStrategy()
        self.balanced_strategy = RandomInsertionStrategy()
        self.quality_strategy = TwoOptMoveStrategy(backend=backend)
    
    def generate_neighbor(self, current_tour, problem, xp, temperature: float):
        """Select strategy based on temperature."""
        if temperature > 1000:
            # High temp: Accept 60%+ of moves anyway, use fast strategy
            return self.fast_strategy.generate_neighbor(current_tour, problem, xp)
        
        elif temperature > 100:
            # Mid temp: Balance exploration/exploitation
            return self.balanced_strategy.generate_neighbor(current_tour, problem, xp)
        
        else:
            # Low temp: Accept ~5% of moves, NEED best neighbor
            return self.quality_strategy.generate_neighbor(current_tour, problem, xp)
```

**Rationale (from SA_COMPREHENSIVE_ANALYSIS.md, Q5):**

**High Temperature (T > 1000):**

```
Acceptance rate: 60-90%
Why waste 400x time finding "best" when accepting random bad moves 60%?

Random2Opt: 5 μs  → FAST
TwoOptMove: 2000 μs → OVERKILL
```

**Low Temperature (T < 100):**

```
Acceptance rate: 5%
Need BEST neighbor (only 5% chance for worse)

Random2Opt: Likely mediocre → WASTEFUL
TwoOptMove: Guaranteed best 2-opt → NECESSARY
```

**Adaptive Algorithm:**

```python
def solve(self, problem):
    current = initial_solution(problem)
    temp = self.initial_temp
    
    for iteration in range(self.max_iterations):
        # ADAPTIVE: Strategy changes with temperature
        neighbor = self.neighbor_strategy.generate_neighbor(
            current, problem, xp, temperature=temp  # Pass temp!
        )
        
        cost = evaluate(neighbor, problem)
        if accept(cost, current_cost, temp):
            current = neighbor
        
        temp *= self.cooling_rate
    
    return current
```

**Performance Benefit:**

```
ch150, 200k iterations:

Non-adaptive (always TwoOptMove):
- Runtime: 200k × 2000 μs = 400s
- Improvement: 18% (hypothetical)

Adaptive (switch at T=100):
- Iter 1-150k: RandomSwap (5 μs) = 0.75s
- Iter 150k-200k: TwoOptMove (2000 μs) = 100s
- Total: ~101s (4x FASTER)
- Improvement: 17% (similar quality)
```

**Threshold Selection:**

| Temperature Threshold | Acceptance Rate | Strategy | Reason |
|----------------------|----------------|----------|--------|
| T > 5000 | >90% | RandomSwap | Pure exploration, speed matters |
| 1000 < T < 5000 | 60-90% | RandomInsertion | Balanced, moderate cost |
| 100 < T < 1000 | 10-60% | Random2Opt | Quality matters more |
| T < 100 | <10% | TwoOptMove | Pure greedy, need best |

**Implementation:**

```python
# In neighbor_strategies.py (future)
class AdaptiveNeighborStrategy:
    def __init__(self, thresholds: Dict[float, NeighborStrategy]):
        self.thresholds = sorted(thresholds.items(), reverse=True)
    
    def generate_neighbor(self, tour, problem, xp, temperature: float):
        for threshold, strategy in self.thresholds:
            if temperature >= threshold:
                return strategy.generate_neighbor(tour, problem, xp)
        # Fallback: lowest threshold strategy
        return self.thresholds[-1][1].generate_neighbor(tour, problem, xp)

# Usage
adaptive = AdaptiveNeighborStrategy({
    5000: RandomSwapStrategy(),
    1000: RandomInsertionStrategy(),
    100: Random2OptStrategy(),
    0: TwoOptMoveStrategy(backend="cupy")  # GPU only when needed!
})

sa = SimulatedAnnealing(
    neighbor_strategy=adaptive,
    max_iterations=200_000
)
```

**Challenge:** `generate_neighbor` protocol doesn't include `temperature` parameter!

**Design Decision Required:**

**Option A:** Extend protocol (breaking change)

```python
class NeighborStrategy(Protocol):
    def generate_neighbor(
        self, tour, problem, xp, temperature: float = None  # NEW
    ) -> List[int]: ...
```

**Option B:** Separate adaptive layer (wrapper)

```python
class AdaptiveWrapper:
    def __init__(self, strategies: Dict[float, NeighborStrategy], sa_instance):
        self.strategies = strategies
        self.sa = sa_instance  # Access to current temperature
    
    def generate_neighbor(self, tour, problem, xp):
        temp = self.sa.current_temperature  # Read state
        return self._select_strategy(temp).generate_neighbor(tour, problem, xp)
```

**Option C:** State-based strategy (SA tracks internally)

```python
# In SimulatedAnnealing.solve()
if self.adaptive and self.current_temp < 100:
    self.neighbor_strategy = self.low_temp_strategy  # Switch!
```

**Recommendation:** **Option C** for M15, **Option A** for M16+ (proper refactor).

**Implementation Status:** Not implemented. Deferred to M15.2 or M16.

**References:**

- Adaptive SA: Smith, K., & Fogarty, T. (1997). "Adaptive simulated annealing"
- Multi-stage SA: Huang, M., Romeo, F., & Sangiovanni-Vincentelli, A. (1986)

---

## Section 2: VRAM Management

**Question (SA_COMPREHENSIVE_ANALYSIS.md, Lines 800, 826, 902, 907):**
> "GPU guardrail before run? Buffer reuse for GA/ACO? Where are the 68.6MB buffers?"

**Answer:** VRAM is constrained (4GB on GTX 1050). Must calculate and allocate efficiently.

---

### 2.1 GPU Guardrails

**Definition:** Calculate total GPU memory required **BEFORE** algorithm starts. Fail early if insufficient.

**Problem:**

```python
# BAD: Allocate during solve() - crashes mid-run!
def solve(self, problem):
    distances_gpu = cp.array(problem.distances)  # 180KB
    # ... 100k iterations later ...
    population_gpu = cp.array(population)  # CRASH! Out of VRAM
```

**Solution:**

```python
# GOOD: Check before solve()
def _check_vram_capacity(self, problem):
    """Calculate required VRAM and fail early if insufficient."""
    n = problem.dimension
    
    # Distance matrix
    distance_size = n * n * 8  # float64
    
    # Working buffers (problem-specific)
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

**VRAM Calculation Formulas:**

#### Distance Matrix (All Algorithms)

$$
\text{Distance Matrix} = n^2 \times 8 \text{ bytes}
$$

**Example (ch150):**

```
150² × 8 = 180,000 bytes = 180KB ✓ (tiny!)
```

#### SA Working Buffers

$$
\text{SA Buffers} = 3n \times 8 \text{ bytes}
$$

**Breakdown:**

- `current_tour`: n × 8 bytes
- `neighbor_tour`: n × 8 bytes  
- `best_tour`: n × 8 bytes

**Example (ch150):**

```
3 × 150 × 8 = 3,600 bytes = 3.6KB ✓ (negligible!)
```

**Note:** SA VRAM usage is TINY. Distance matrix dominates, but still only 180KB.

#### GA Working Buffers

$$
\text{GA Buffers} = 2 \times \text{pop\_size} \times n \times 8 \text{ bytes}
$$

**Breakdown:**

- `population`: pop_size × n × 8 bytes
- `offspring`: pop_size × n × 8 bytes

**Example (ch150, pop=1000):**

```
2 × 1000 × 150 × 8 = 2,400,000 bytes = 2.4MB ✓ (manageable)
```

#### ACO Working Buffers

$$
\text{ACO Buffers} = n^2 \times 8 + \text{num\_ants} \times n \times 8
$$

**Breakdown:**

- `pheromone_matrix`: n² × 8 bytes
- `ant_paths`: num_ants × n × 8 bytes

**Example (ch150, ants=100):**

```
Pheromone: 150² × 8 = 180KB
Ant paths: 100 × 150 × 8 = 120KB
Total: 300KB ✓ (small)
```

#### Summary Table

| Algorithm | n=150 | n=300 | n=500 | n=1000 |
|-----------|-------|-------|-------|--------|
| **SA** | 184KB | 724KB | 2.0MB | 8.0MB |
| **GA (pop=1000)** | 2.6MB | 9.2MB | 25.6MB | 102.4MB |
| **ACO (ants=100)** | 300KB | 1.1MB | 3.1MB | 12.4MB |

**GTX 1050 Mobile: 4GB VRAM**

**Safe limits (90% = 3.6GB):**

- SA: Up to n ≈ 21,000 nodes (impractical for other reasons)
- GA: Up to n ≈ 1,900 nodes (with pop=1000)
- ACO: Up to n ≈ 6,800 nodes (with ants=100)

**Actual constraint:** Algorithm runtime, not VRAM!

**Where are the 68.6MB buffers mentioned in SA doc?**

**Answer:** **Error in original calculation!** SA buffers for ch150 are only 3.6KB, not 68MB.

**Likely confusion:**

- Test 4 measured 70.6 μs/iteration **transfer time**
- 100k iterations × 70.6 μs = 7.06 **seconds**
- NOT 68.6MB of **memory**

**Correct breakdown (ch150 on GPU):**

- Distance matrix: 180KB (one-time transfer)
- Tour buffer: 1.2KB per iteration (transfers CPU↔GPU)
- **Time cost:** 7 seconds for transfers
- **Space cost:** 181KB total VRAM

---

### 2.2 Buffer Reuse Patterns

**Question (Line 826):** "Does buffer reuse apply to GA and ACO too?"

**Answer:** **YES!** Buffer reuse is a **universal GPU pattern** for all algorithms.

**Pattern:**

```python
class GeneticAlgorithm:
    def __init__(self, ..., backend="numpy"):
        self.xp = cupy if backend == "cupy" else numpy
        
        # Allocate buffers in __init__ (ONCE)
        self._population_buffer = None
        self._offspring_buffer = None
        self._fitness_buffer = None
    
    def solve(self, problem):
        n = problem.dimension
        
        # FIRST TIME: Allocate on GPU
        if self._population_buffer is None:
            self._population_buffer = self.xp.empty(
                (self.pop_size, n), dtype=self.xp.int32
            )
            self._offspring_buffer = self.xp.empty(
                (self.pop_size, n), dtype=self.xp.int32
            )
            self._fitness_buffer = self.xp.empty(
                self.pop_size, dtype=self.xp.float64
            )
        
        # REUSE buffers across 500 generations
        for generation in range(500):
            # Fill buffers (no new allocation!)
            self._population_buffer[:] = ...
            self._fitness_buffer[:] = evaluate_gpu(self._population_buffer)
            
            # Crossover/mutation into offspring buffer
            self._offspring_buffer[:] = crossover_gpu(self._population_buffer)
        
        return best_solution
```

**Benefits:**

| Metric | Without Reuse | With Reuse | Improvement |
|--------|--------------|-----------|-------------|
| **Allocations** | 500 generations × 3 buffers = 1500 | 3 (one-time) | **500x fewer** |
| **Memory overhead** | Fragmentation from 1500 allocs | None | **Stable VRAM** |
| **Runtime** | +50ms per generation (alloc time) | 0ms | **25s saved** (500 gen) |

**Buffer Lifecycle:**

```
__init__():
    ├─ Set backend (numpy/cupy)
    └─ Initialize buffer variables (None)

solve(problem):
    ├─ First call: Allocate buffers (VRAM commit)
    ├─ Generations 1-500: REUSE buffers
    └─ Return best solution
    
(Buffers persist in GPU until object deleted)
```

**Applies to:**

✅ **SA:** current_tour, neighbor_tour, best_tour  
✅ **GA:** population, offspring, fitness  
✅ **ACO:** pheromone_matrix, ant_paths, heuristic_info  
✅ **Any GPU algorithm:** Allocate once in `__init__`, reuse in `solve()`

**Implementation:**

```python
# Universal pattern for all algorithms
class GPUAlgorithmBase:
    def __init__(self, backend="numpy"):
        self.xp = cupy if backend == "cupy" else numpy
        self._buffers_allocated = False
    
    def _allocate_buffers(self, problem):
        """Allocate GPU buffers once. Override in subclasses."""
        if self._buffers_allocated:
            return  # Already allocated
        
        # Subclass-specific allocations
        self._distance_matrix_gpu = self.xp.array(problem.distances)
        # ... other buffers ...
        
        self._buffers_allocated = True
    
    def solve(self, problem):
        self._allocate_buffers(problem)  # First call only
        # ... algorithm logic using self._buffers ...
```

---

### 2.3 Memory Layout Considerations

**Coalesced Access (GPU Performance):**

```python
# BAD: Row-major access (non-coalesced)
for i in range(n):
    for j in range(n):
        distance = distances_gpu[i, j]  # Each thread reads different row

# GOOD: Column-major access (coalesced)
distances_gpu_T = distances_gpu.T  # Transpose once
for i in range(n):
    for j in range(n):
        distance = distances_gpu_T[j, i]  # Threads read same column (coalesced)
```

**Padding for Alignment:**

```python
# GPU prefers aligned memory (multiples of 128 bytes)
n = 150
padded_n = ((n + 15) // 16) * 16  # Round up to multiple of 16

# Allocate with padding
distances_padded = cp.zeros((padded_n, padded_n), dtype=cp.float64)
distances_padded[:n, :n] = problem.distances

# ~10% speedup from aligned access
```

**Pinned Memory for Transfers:**

```python
# Use pinned (page-locked) memory for faster CPU↔GPU transfers
import cupy as cp

# Allocate pinned memory on CPU
tour_pinned = cp.cuda.alloc_pinned_memory(n * 8)

# Transfer is ~2x faster
cp.cuda.runtime.memcpy(tour_gpu, tour_pinned, n * 8, cp.cuda.runtime.memcpyHostToDevice)
```

**Implementation Status:** Memory layout optimizations deferred to M17+ (optimization phase).

---

### 2.4 Backend Parameter and P-Data Compatibility

**Question:** "When P-Data multistart (M18) is implemented, will the `backend='numpy'` default in SA still make sense?"

**Answer:** **YES!** The current design is FORWARD-COMPATIBLE with P-Data.

**Current Architecture (S-Task):**

```python
class SimulatedAnnealing:  # S-Task: Sequential Task
    def __init__(self, neighbor_strategy, backend="numpy", ...):
        """Single trajectory Simulated Annealing."""
        self.backend = backend
        self.backend_module = get_backend(backend)
        # ... SA logic ...
```

**Future Architecture (P-Data - M18):**

```python
class ParallelMultistartSA:  # P-Data: Parallel Data
    """
    Multiple independent S-Task instances running in parallel.
    Each S-Task can use different backend (numpy or cupy).
    """
    def __init__(self, n_starts=10, backend="cupy"):
        """
        Launch N parallel S-Task instances.
        
        Args:
            n_starts: Number of independent SA runs
            backend: Backend for ALL S-Tasks (or per-task if list)
        """
        # Option A: All S-Tasks use same backend
        self.workers = [
            SimulatedAnnealing(strategy=..., backend=backend)
            for _ in range(n_starts)
        ]
        
        # Option B: Different backends per S-Task (experimental)
        backends = ["numpy"] * 5 + ["cupy"] * 5  # Hybrid CPU/GPU
        self.workers = [
            SimulatedAnnealing(strategy=..., backend=b)
            for b in backends
        ]
```

**Key Insight:**

- **S-Task (SA):** Single trajectory, needs ONE backend choice
- **P-Data (Multistart):** Multiple S-Tasks, each with OWN backend
- **No conflict:** P-Data orchestrates S-Tasks, doesn't replace them

**Why `backend="numpy"` default is correct:**

1. **Safe default:** NumPy works on all systems (no CUDA required)
2. **S-Task semantics:** Single trajectory doesn't need GPU parallelism
3. **P-Data compatibility:** When M18 is implemented, it will simply:
   - Create N S-Task instances
   - Pass chosen backend to each instance
   - No changes to S-Task `__init__` signature needed

**Execution Models:**

```python
# Model 1: Sequential execution (current)
sa = SimulatedAnnealing(strategy=..., backend="numpy")
result = sa.solve(problem)  # Runs on CPU

# Model 2: GPU acceleration (current)
sa = SimulatedAnnealing(strategy=..., backend="cupy")
result = sa.solve(problem)  # Runs on GPU (single trajectory)

# Model 3: P-Data multistart (future M18)
pdata = ParallelMultistartSA(n_starts=10, backend="cupy")
results = pdata.solve(problem)  # 10 GPU trajectories in parallel
# Internally: pdata creates 10 SA instances with backend="cupy"
```

**Implementation Status:** 
- ✅ S-Task backend parameter (M14.3.4.2 - complete)
- ✅ Architecture validated for P-Data (this section)
- ⏸️ P-Data implementation (scheduled for M18)

**Reference:** SimulatedAnnealing docstring lines 175-194 (P-Data Compatibility note)

---

## Section 3: Improvement Heuristics Beyond 2-Opt

**Question (Line 849):** "What about 3-opt, Lin-Kernighan, Or-opt?"

**Answer:** Multiple k-opt heuristics exist. Each has trade-offs (complexity vs quality vs GPU viability).

---

### 3.1 3-Opt Moves

**Definition:** Remove **3 edges** from tour, reconnect in best of 8 possible ways.

**Complexity:** $O(n^3)$ - evaluate all $\binom{n}{3}$ combinations

**From DM865 Handout (PHASE 1 research):**
> "3-opt: 6 possible 3-exchanges with path reversals"

**Algorithm:**

```python
def three_opt_move(tour, i, j, k):
    """
    Remove edges (i, i+1), (j, j+1), (k, k+1).
    Try 8 reconnection patterns, return best.
    
    Args:
        tour: Current tour
        i, j, k: Edge positions (i < j < k)
    
    Returns:
        best_tour, best_delta
    """
    # 8 possible reconnections (including original)
    cases = [
        tour,  # 0: No change
        tour[:i+1] + tour[j+1:k+1][::-1] + tour[i+1:j+1] + tour[k+1:],  # 1
        tour[:i+1] + tour[j+1:k+1] + tour[i+1:j+1][::-1] + tour[k+1:],  # 2
        # ... 5 more cases ...
    ]
    
    best_tour = min(cases, key=lambda t: tour_cost(t, distances))
    return best_tour, delta_cost
```

**Search Space:**

For n=150:
$$
\binom{150}{3} = \frac{150 \times 149 \times 148}{6} = 551,300 \text{ combinations}
$$

**Compared to 2-opt:**
$$
\binom{150}{2} = 11,175 \text{ combinations (50x smaller!)}
$$

**Quality vs Runtime:**

| Heuristic | Combinations | CPU Time (ch150) | Improvement over 2-opt |
|-----------|-------------|------------------|------------------------|
| **2-opt** | 11,175 | 100ms | Baseline |
| **3-opt** | 551,300 | ~5,000ms (50x slower) | +2-5% |

**Diminishing returns:** 50x more work for 2-5% better solutions.

**GPU Viability:**

**YES, potentially valuable:**

- 551k evaluations >> GPU overhead (500 μs)
- Parallel evaluation across all $(i,j,k)$ triplets
- Expected speedup: 10-30x (similar to 2-opt)

**Implementation:**

```python
# Pseudocode for GPU 3-opt
@cp.fuse()
def evaluate_all_3opt_moves_gpu(tour_gpu, distances_gpu):
    """Evaluate all O(n³) 3-opt moves in parallel."""
    n = len(tour_gpu)
    results = cp.empty((n, n, n), dtype=cp.float64)
    
    # Each GPU thread evaluates one (i,j,k) combination
    for i in range(n):
        for j in range(i+2, n):
            for k in range(j+2, n):
                results[i, j, k] = evaluate_3opt_delta(tour_gpu, i, j, k, distances_gpu)
    
    # Parallel reduction to find best
    best_idx = cp.argmin(results)
    return best_idx, results.flat[best_idx]
```

**Challenge:** 8 reconnection cases per $(i,j,k)$ → complex kernel logic.

**Implementation Status:** Not implemented. Deferred to M17+ (advanced heuristics).

**References:**

- DM865: "Local Search for TSP" (PHASE 1 research)
- Lin, S. (1965). "Computer solutions of the traveling salesman problem"

---

### 3.2 Lin-Kernighan Heuristic

**Definition:** **Variable k-opt** - adaptively choose $k$ (number of edges to remove) based on improvements found.

**From Keld Helsgaun (PHASE 1 research):**
> "K=6 with full patching deviates only 0.004% from best tour"
> "Non-sequential moves result in better tours AND reduce running time"

**Algorithm (Simplified):**

```python
def lin_kernighan(tour, distances):
    """
    Variable k-opt improvement.
    
    Start with k=2, increase k if improvements found,
    decrease k if stuck.
    """
    k = 2  # Start with 2-opt
    improved = True
    
    while improved:
        improved = False
        
        # Try k-opt moves
        best_move = find_best_k_opt_move(tour, k, distances)
        
        if best_move.delta < 0:  # Improvement
            tour = apply_move(tour, best_move)
            improved = True
            k = min(k + 1, 6)  # Increase k (up to 6)
        else:
            k = max(k - 1, 2)  # Decrease k (down to 2)
    
    return tour
```

**Complexity:** **Adaptive** - between $O(n^2)$ and $O(n^6)$ depending on tour quality

**Key Innovation:** "Non-sequential moves"

**Sequential 3-opt:**

```
Remove edges: (i, i+1), (j, j+1), (k, k+1)
Constraint: i < j < k (sequential)
```

**Non-sequential k-opt:**

```
Remove edges: (a, b), (c, d), (e, f), ...
Constraint: NONE (can be anywhere in tour!)
Search space: MUCH larger, but often finds better moves faster
```

**Quality:**

From Helsgaun report:

- **TSP instances up to 85,900 cities**
- **Deviation from optimal: 0.004%** (practically optimal!)
- Runtime: Comparable to simpler heuristics due to adaptive $k$

**GPU Viability:**

**DIFFICULT:**

- Adaptive $k$ → irregular control flow (bad for SIMD)
- Non-sequential moves → complex indexing
- Variable search space → load imbalance across threads

**Recommendation:** CPU implementation only (M17+), not GPU.

**Implementation Status:** Not implemented. Complex algorithm, deferred to M18+ (research topic).

**References:**

- Helsgaun, K. (2000). "An effective implementation of the Lin-Kernighan traveling salesman heuristic"
- webhotel4.ruc.dk: "K-opt moves for the Lin-Kernighan TSP Heuristic" (PHASE 1 research)

---

### 3.3 Or-Opt Moves

**Definition:** **Relocate sequences** of 1, 2, or 3 consecutive cities. **NO path reversals.**

**From DM865 Handout (PHASE 1 research):**
> "Or-opt (Or 1976): Sequences of 1,2,3 consecutive vertices relocated, NO paths reversed"

**Difference from 2-opt/3-opt:**

| Heuristic | Operation | Path Reversal? |
|-----------|-----------|----------------|
| **2-opt** | Reverse segment [i, j] | YES |
| **3-opt** | Reconnect 3 segments | YES (some cases) |
| **Or-opt** | Move segment [i, i+k] | **NO** |

**Algorithm:**

```python
def or_opt_move(tour, start, length, insert_pos):
    """
    Remove segment tour[start:start+length],
    insert at insert_pos WITHOUT reversing.
    
    Args:
        tour: Current tour
        start: Start of segment to move
        length: 1, 2, or 3 cities
        insert_pos: Where to insert segment
    """
    segment = tour[start:start+length]
    
    # Remove segment
    new_tour = tour[:start] + tour[start+length:]
    
    # Insert at new position (NO REVERSAL!)
    new_tour = new_tour[:insert_pos] + segment + new_tour[insert_pos:]
    
    return new_tour
```

**Complexity:** $O(n^2)$ - for each segment, try all insertion positions

**Search Space (for length=1):**

$$
n \times (n-1) = n^2 - n \approx O(n^2)
$$

**For lengths 1, 2, 3:** $3n^2$ total moves (still $O(n^2)$)

**Quality vs 2-opt:**

- **Or-opt:** Finds different local optima (no reversals)
- **2-opt:** Finds different local optima (reversals)
- **Combined:** Or-opt + 2-opt often better than either alone

**Use Case:**

**Problem:** Tour has good overall structure but clusters in wrong positions

```
Tour: [0, cluster_A, 5, cluster_B, 10, cluster_C, 0]
Better: [0, cluster_A, cluster_B, cluster_C, 5, 10, 0]

Or-opt: Move cluster_B next to cluster_A (no reversal needed)
2-opt: Would reverse cluster_B (changes internal structure)
```

**GPU Viability:**

**YES, similar to 2-opt:**

- $O(n^2)$ moves → 11,175 evaluations (ch150)
- No complex logic (just removal + insertion)
- Expected speedup: 10-50x

**Implementation:**

```python
@cp.fuse()
def evaluate_all_or_opt_moves_gpu(tour_gpu, distances_gpu, length):
    """Evaluate all Or-opt moves for given segment length."""
    n = len(tour_gpu)
    results = cp.empty((n, n), dtype=cp.float64)
    
    # Each GPU thread evaluates one (start, insert_pos) combination
    for start in range(n):
        for insert_pos in range(n):
            if abs(start - insert_pos) <= length:
                results[start, insert_pos] = 0  # Invalid move
            else:
                results[start, insert_pos] = evaluate_or_opt_delta(
                    tour_gpu, start, length, insert_pos, distances_gpu
                )
    
    # Find best move
    best_idx = cp.argmin(results)
    return best_idx, results.flat[best_idx]
```

**Implementation Status:** Not implemented. Deferred to M16+ (alternative to 3-opt).

**Priority:** **Lower than 2-opt** (2-opt is more standard and understood).

**References:**

- Or, I. (1976). "Traveling Salesman-Type Combinatorial Problems and Their Relation to the Logistics of Blood Banking"
- DM865: "Local Search for TSP" (PHASE 1 research)

---

### 3.4 GPU Parallelization Viability

**Summary Table:**

| Heuristic | Complexity | Search Space (n=150) | GPU Benefit | Priority | Status |
|-----------|-----------|---------------------|-------------|----------|--------|
| **2-opt** | $O(n^2)$ | 11,175 | ⭐⭐⭐⭐⭐ 10-50x | **HIGHEST** | ✅ M15 |
| **Or-opt** | $O(n^2)$ | ~33,525 (×3 lengths) | ⭐⭐⭐⭐ 10-40x | Medium | M16 |
| **3-opt** | $O(n^3)$ | 551,300 | ⭐⭐⭐ 5-20x | Low | M17+ |
| **Lin-Kernighan** | $O(n^{2-6})$ | Adaptive | ⭐ Difficult | Research | M18+ |

**GPU Viability Criteria:**

✅ **Good for GPU:**

- Fixed, regular computation per move
- $O(n^2)$ or larger search space
- Simple evaluation logic
- **Examples:** 2-opt, Or-opt

⚠️ **Challenging for GPU:**

- Irregular control flow (if-else chains)
- Adaptive search space
- Complex reconnection logic
- **Examples:** 3-opt (8 cases), Lin-Kernighan (variable k)

❌ **Not suitable for GPU:**

- $O(n)$ or smaller search space (overhead dominates)
- Highly sequential algorithms
- **Examples:** RandomSwap, RandomInsertion

**Implementation Roadmap:**

```
M15 (Current):
├─ TwoOptMove (CPU + GPU)
└─ Comprehensive testing

M16 (Future):
├─ OrOptMove (CPU + GPU)
└─ Hybrid 2-opt + Or-opt strategies

M17+ (Research):
├─ ThreeOptMove (CPU only, maybe GPU)
└─ Adaptive k-opt strategies

M18+ (Advanced):
└─ Lin-Kernighan (CPU only)
```

---

## Section 4: Streaming Architecture

**Question (Line 876):** "What is streaming architecture? Meta-metaheuristic?"

**Answer:** For **P-Data algorithms** (GA populations, Multistart SA), process data in **chunks** to fit VRAM.

---

### 4.1 Meta-Metaheuristic Wrapper

**Definition:** **Wrapper** that chunks large datasets for GPU processing, transparent to algorithm.

**Problem:**

```python
# GA with population=10,000 (large!)
ga = GeneticAlgorithm(population_size=10_000, backend="cupy")

# VRAM required (ch150):
# 2 × 10,000 × 150 × 8 = 24MB (fits in 4GB ✓)

# But for n=500:
# 2 × 10,000 × 500 × 8 = 80MB (fits ✓)

# For n=1000:
# 2 × 10,000 × 1000 × 8 = 160MB (fits ✓)

# For n=2000:
# 2 × 10,000 × 2000 × 8 = 320MB (fits ✓)

# For n=5000:
# 2 × 10,000 × 5000 × 8 = 800MB (fits ✓)

# For population=100,000 (extreme):
# 2 × 100,000 × 150 × 8 = 240MB (still fits!)
```

**Actually:** VRAM is rarely the bottleneck for GA!

**BUT:** Streaming still useful for **Multistart SA** with many chains.

**Streaming Pattern:**

```python
class StreamingSA:
    """
    Run N SA chains in chunks to fit VRAM.
    
    Example: 10,000 chains, chunk_size=100
    → 100 iterations of 100 chains each
    → Each chunk fits in VRAM
    """
    
    def __init__(self, num_chains, chunk_size, sa_params):
        self.num_chains = num_chains
        self.chunk_size = chunk_size
        self.sa_params = sa_params
    
    def solve(self, problem):
        results = []
        
        # Process in chunks
        for chunk_start in range(0, self.num_chains, self.chunk_size):
            chunk_end = min(chunk_start + self.chunk_size, self.num_chains)
            chunk_size_actual = chunk_end - chunk_start
            
            # Launch chunk_size SA chains on GPU
            chunk_results = self._run_chunk(
                problem, chunk_start, chunk_size_actual
            )
            
            results.extend(chunk_results)
        
        # Return best across all chunks
        return min(results, key=lambda r: r.cost)
    
    def _run_chunk(self, problem, offset, chunk_size):
        """Run chunk_size SA chains in parallel on GPU."""
        # Each SA chain is independent (P-Data)
        chains = []
        for i in range(chunk_size):
            seed = offset + i
            sa = SimulatedAnnealing(**self.sa_params, seed=seed, backend="cupy")
            chains.append(sa.solve(problem))
        
        return chains
```

**Chunk Size Calculation:**

```python
def calculate_optimal_chunk_size(problem, available_vram):
    """Determine how many SA chains fit in VRAM simultaneously."""
    n = problem.dimension
    
    # Per-chain VRAM:
    # - Distance matrix: n² × 8 (shared across all chains!)
    # - Tour buffers: 3n × 8 per chain
    
    shared_vram = n * n * 8
    per_chain_vram = 3 * n * 8
    
    # Available for chains (90% safety margin)
    available_for_chains = available_vram * 0.9 - shared_vram
    
    chunk_size = int(available_for_chains / per_chain_vram)
    
    return max(1, chunk_size)

# Example (ch150, 4GB VRAM)
chunk_size = calculate_optimal_chunk_size(ch150, 4e9)
# Result: ~1,000,000 chains fit! (VRAM is not the constraint)

# Actual constraint: Runtime!
# 1,000,000 chains × 10s each = 10,000,000s = 115 days!
```

**Practical Use Case:**

**Not VRAM-limited, but THROUGHPUT-limited:**

```python
# Run 1,000 SA chains in parallel
# Goal: Find best solution across 1,000 random seeds
# Time: 10s per chain on CPU

# Without GPU: 1,000 × 10s = 10,000s = 2.8 hours (sequential)

# With GPU (100 chains/chunk, streaming):
# 10 chunks × 10s = 100s = 1.7 minutes (100x speedup!)
```

---

### 4.2 P-Data Chunking Strategy

**Applicable Algorithms:**

| Algorithm | P-Data Aspect | Chunk Size Calculation |
|-----------|--------------|------------------------|
| **Multistart SA** | N independent chains | `available_VRAM / (3n × 8)` |
| **GA** | Population | `available_VRAM / (2n × 8 × pop_size)` |
| **Particle Swarm** | Swarm | `available_VRAM / (num_particles × n × 8)` |

**Design Pattern:**

```python
class StreamingMetaheuristic:
    """Abstract base for streaming P-Data algorithms."""
    
    def solve(self, problem, total_instances):
        chunk_size = self._calculate_chunk_size(problem)
        results = []
        
        for chunk in chunks(total_instances, chunk_size):
            # Process chunk on GPU
            chunk_results = self._process_chunk_gpu(chunk, problem)
            results.extend(chunk_results)
        
        return self._aggregate_results(results)
    
    @abstractmethod
    def _calculate_chunk_size(self, problem):
        """Determine optimal chunk size for VRAM."""
        pass
    
    @abstractmethod
    def _process_chunk_gpu(self, chunk, problem):
        """Process one chunk on GPU."""
        pass
```

**Implementation Status:** Not implemented. Deferred to M17+ (P-Data parallelization milestone).

---

### 4.3 Future Work

**M17: P-Data Parallelization**

Objectives:

- Implement `StreamingSA` for multistart
- Implement true parallel GA (population on GPU)
- Benchmark streaming vs non-streaming

**M18: Distributed Streaming**

Objectives:

- Multi-GPU support (split chunks across GPUs)
- CPU-GPU hybrid streaming (CPU processes while GPU computes)

**Current Priority:** **LOW** (VRAM not limiting factor for n≤500)

---

## References

### Academic Papers

**Composition Patterns:**

1. Moscato, P. (1989). "On Evolution, Search, Optimization, Genetic Algorithms and Martial Arts: Towards Memetic Algorithms"
2. Lourenço, H. R., Martin, O. C., & Stützle, T. (2003). "Iterated Local Search" (Handbook of Metaheuristics)
3. Hansen, P., & Mladenović, N. (2001). "Variable neighborhood search: Principles and applications"

**Improvement Heuristics:**
4. Lin, S. (1965). "Computer solutions of the traveling salesman problem"
5. Helsgaun, K. (2000). "An effective implementation of the Lin-Kernighan traveling salesman heuristic"
6. Or, I. (1976). "Traveling Salesman-Type Combinatorial Problems and Their Relation to the Logistics of Blood Banking"

**GPU Algorithms:**
7. Ferreiro et al. (2024). "An efficient implementation of parallel simulated annealing algorithm in GPUs" (arXiv:2408.00018)
8. Fujimoto, K., & Kaga, T. (2011). "Two-opt Local Search for the Traveling Salesman Problem with GPU"

### Online Resources (PHASE 1 Research)

**ILS:**

- IRIDIA: "ILS - Iterated Local Search" (slides)
- repositori.upf.edu: ILS Framework PDF
- SciSpace: ILS Framework and Applications

**VNS:**

- Wikipedia: "Variable neighborhood search"
- Medium: "Solving the Traveling Salesman Problem with VNS"
- jamoreno.webs.ull.es: VNS Chapter 5 PDF

**k-opt Heuristics:**

- webhotel4.ruc.dk (Keld Helsgaun): "K-opt moves for the Lin-Kernighan TSP Heuristic"
- dm865.github.io: "Local Search for TSP" (DM865 handout)
- stemlounge.com: "11 Animated TSP Algorithms"

**SA Fundamentals:**

- enac.hal.science: HAL-ENAC PDF (Boltzmann distribution, Metropolis theorem)
- Wikipedia: "Simulated Annealing"

---

## Document Maintenance

**Last Updated:** 2025-11-07  
**Next Review:** After M15 completion (TwoOptMove implementation)

**Change Log:**

- 2025-01-28: Initial creation (deferred from SA_COMPREHENSIVE_ANALYSIS.md)
- 2025-11-07: Complete draft with all 4 sections, research citations
- 2025-11-07: Added Section 2.4 (Backend & P-Data Compatibility)
- 2025-11-07: Added strategy refactoring deferral note

**Related Documents:**

- `documentation/progress/SA_COMPREHENSIVE_ANALYSIS.md` (testing results, admonitions source)
- `documentation/progress/M14_M15_DETAILED_TASKS.md` (implementation roadmap)
- `knowledge_base/methodology/TEACHING_ORIENTED_REBUILD_SPECIFICATION.md` (educational context)

**Approval Status:** DRAFT - Awaiting user validation (PHASE 5)

---

### Deferred Decisions

#### Strategy Folder Reorganization (DEFERRED to post-M15)

**Question:** "Should strategies be reorganized into `strategies/` folder with proper protocol separation?"

**Proposed Structure:**
```
protocols/
  strategies/
    algorithm_strategies_protocol.py
    neighbor_strategies_protocol.py
strategies/
  neighbor_strategies/
    random_swap.py
    random_2opt.py
  mutation_strategies/
  crossover_strategies/
```

**Decision: DEFER until after M14-M15 complete**

**Rationale:**
1. **Current structure is functional** - No bugs or architectural issues
2. **High risk during TCC deadline** - Would require updating 20-30 import paths
3. **Aesthetic change, not functional** - Improves organization but doesn't solve problems
4. **Time estimate:** 2-3 hours for complete refactoring + testing
5. **Priority:** Should focus on NEW features (GA, registries, tests) not reorganization

**When to revisit:**
- After M14-M15 (metaheuristic refactor) complete
- Before final benchmarking phase (if time permits)
- During code freeze before TCC defense (optional polish)

**Alternative:** Use static type checker (mypy) to automatically fix import paths if reorganization becomes necessary.

**Status:** Documented as intentional deferral, not forgotten task.

