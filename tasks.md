Thinking

You're absolutely right - that plan was way too ambitious for a TCC timeline! Let me create a **realistic MVP plan** focused on delivering a working GPU-accelerated implementation for your thesis.

# 🎯 GPU-ACCELERATED TSP/CVRP - **MVP IMPLEMENTATION PLAN**

## 🎓 **TCC CONSTRAINTS & REALITY CHECK**

**Timeline**: 10-12 weeks of implementation  
**Goal**: Working GPU implementation demonstrating speedup  
**Academic Focus**: Results for TCC chapters > Production-grade code  
**Test Dataset**: 10-15 representative TSPLIB instances (NOT all 113!)  
**Memory Constraint**: Max d15112 (15,112 nodes, 1.91GB)

---

## 📋 **MVP EPIC BREAKDOWN** (3 Core Epics)

### **EPIC 1: Foundation - Get It Working** ⚙️

*Duration: 2 weeks | Priority: CRITICAL | Story Points: 18*

**Description**: Minimal infrastructure to load problems and switch backends.

---

#### **Story 1.1: Database Integration (Minimal)**

*Story Points: 5 | Priority: Critical*  
*Implementation Time: 3-4 hours | Analysis Complete: `/documentation/reports/STORY_1.1_IMPLEMENTATION_ANALYSIS.md`*

**Tasks:**

**Task 1.1.1: Problem Loader** ⚡ **READY TO IMPLEMENT**

> **PLANNING COMPLETED**: 2025-01-28
>
> - ✅ Analyzed routing.duckdb (266 problems: 110 TSP, 19 ATSP, 35 CVRP)
> - ✅ Selected 30 instances (18 TSP, 6 ATSP, 6 CVRP) spanning 7 → 15,112 nodes
> - ✅ Research questions mapped (Q1: overhead, Q2: scaling, Q3: memory, Q4: structure, Q5: type comparison)
> - ✅ Memory analysis validated (d15112 = 1.70GB = 42.5% VRAM, maximum feasible)
> - ✅ Documentation complete: `/documentation/reports/BENCHMARK_INSTANCES_30_SELECTED.md`
> - ✅ Implementation plan complete: `/documentation/reports/STORY_1.1_IMPLEMENTATION_ANALYSIS.md`
> - ✅ first_draft.md Section 3.4 updated with selection strategy and expected results
>
> **NEXT**: Implement actual loading code (subtasks below)

**Subtask 1.1.1.1: Connect to routing.duckdb** *(15 min)*

- **File**: `code/src/utils/problem_loader.py`
- **Function**: `get_database_connection(db_path: str | Path) -> duckdb.DuckDBPyConnection`
- **Implementation**:
  - Read-only connection to routing.duckdb
  - FileNotFoundError if database missing
  - Returns DuckDB connection object
- **Testing**: Verify connection opens, error handling for missing file
- **Value**: CRITICAL - Foundation for all data loading

**Subtask 1.1.1.2: Load 30 Selected Instances** *(45 min)*

- **File**: `code/src/utils/problem_loader.py`
- **Functions**:
  - `load_instance_metadata(conn, name) -> dict`: Load problem metadata (dimension, type, optimal_cost)
  - `load_instance_nodes(conn, name) -> pd.DataFrame`: Load node coordinates, demands
  - Uses `SELECTED_INSTANCES` constant (30 instance names from analysis)
- **Implementation**:
  - SQL queries to problems/nodes tables
  - Extract metadata (name, dimension, type, capacity, vehicles, optimal_cost)
  - Extract coordinates, demands, depot flag
- **Testing**: Verify all 30 instances load, check data types
- **Value**: CRITICAL - Core data loading logic

**Subtask 1.1.1.3: Create `Problem` Dataclass** *(1 hour)*

- **File**: `code/src/utils/problem_loader.py`
- **Class**: `Problem` (dataclass)
- **Attributes**:
  - Core: `name`, `dimension`, `type`, `coordinates`, `distances`
  - Optional: `optimal_cost`
  - CVRP: `capacity`, `demands`, `depot_index`, `num_vehicles`
  - Metadata: `edge_weight_type`
- **Methods**:
  - `__post_init__()`: Validate dimensions, check CVRP requirements
  - `is_symmetric() -> bool`: Check TSP vs ATSP
  - `get_gap_to_optimal(solution_cost) -> float`: Calculate % gap
- **Testing**: Create instance, validate all attributes, test validation logic
- **Value**: CRITICAL - Unified data structure for all algorithms

**Subtask 1.1.1.4: Compute Distance Matrix (Euclidean 2D)** *(1 hour)*

- **File**: `code/src/utils/problem_loader.py`
- **Functions**:
  - `compute_euclidean_distances(coordinates) -> np.ndarray`: Vectorized distance calculation
  - `load_problem(name, conn) -> Problem`: Complete problem loading pipeline
  - `load_all_selected_instances(conn) -> dict[str, Problem]`: Load all 30 instances
- **Implementation**:
  - Vectorized NumPy distance matrix: `sqrt(sum((coords[:, None, :] - coords[None, :, :])^2))`
  - Time complexity: O(n²)
  - Space complexity: O(n²)
- **Testing**: Verify symmetric for TSP, correct values (manual check for berlin52)
- **Value**: CRITICAL - Distance matrix used by all algorithms

> [!important] Even though other types of problem like geo3d are in the database, for MVP we only implement Euclidean 2D distance calculation. This keeps scope manageable.
> But for future work, we MUST add more distance types (Manhattan, geo3d, etc).

**Skip for MVP** (5-8 hours saved):

- ❌ [BACKLOG] **Caching** (memory/disk): Loading 30 instances takes ~5s (negligible), TCC experiments run once, adds complexity
  - *When to implement*: If loading becomes bottleneck (100+ instances, expensive preprocessing)
  - *Cost*: 2-3 hours
- ❌ [BACKLOG] **Lazy loading**: All 30 instances needed for experiments, upfront loading simpler
  - *When to implement*: Interactive notebook exploration, memory-constrained environments
  - *Cost*: 1-2 hours
- ❌ [BACKLOG] **Batch processing** (parallel loading): Sequential ~5s acceptable, parallel saves ~2s (minimal benefit)
  - *When to implement*: Loading 100+ instances (10+ seconds sequential)
  - *Cost*: 2-3 hours

**Task 1.1.2: TSPLIB Instance Selection** ❌ **[DEPRECATED]**

> **Status**: OBSOLETE - Superseded by Task 1.1.1
>
> **Issue**: This task mentions "~10 instances" but Task 1.1.1 already selected **30 instances**. Selection criteria, documentation, and optimal cost verification are already complete (see `/documentation/reports/BENCHMARK_INSTANCES_30_SELECTED.md`).
>
> **Action**: DELETE this task - all objectives achieved in Task 1.1.1

**Acceptance Criteria:**

- ✓ Database connection established successfully (subtask 1.1.1.1)
- ✓ All 30 selected instances load correctly (subtask 1.1.1.2)
- ✓ `Problem` dataclass created with validation (subtask 1.1.1.3)
- ✓ Distance matrices computed correctly (Euclidean 2D) (subtask 1.1.1.4)
- ✓ Symmetric distance matrices for TSP/CVRP (d[i,j] == d[j,i])
- ✓ CVRP instances include capacity, demands, depot
- ✓ Optimal costs loaded where available
- ✓ Loading time <10 seconds for all 30 instances
- ✓ Code documented with NumPy-style docstrings
- ✓ Basic unit tests pass (load berlin52, verify distance matrix)

---

#### **Story 1.2: Backend Abstraction (Just NumPy ↔ CuPy)**

*Story Points: 8 | Priority: Critical*

**Tasks:**

**Task 1.2.1: Simple Backend Protocol**

- Subtask: Define `Backend` protocol with `array()`, `zeros()`, `sqrt()`, `sum()`
- Subtask: Implement `NumPyBackend` (thin wrapper)
- Subtask: Implement `CuPyBackend` (thin wrapper + GPU check)
- **Skip**: Complex memory management, profiling tools

**Task 1.2.2: Distance Matrix Function**

- Subtask: Implement `compute_distance_matrix(coords, backend)`
- Subtask: Works with both NumPy and CuPy arrays
- Subtask: Validate results identical (CPU vs GPU)
- **Skip**: Tiled computation, sparse matrices, on-demand calculation

**Task 1.2.3: Backend Factory**

- Subtask: `get_backend(use_gpu=True)` → returns CuPy or NumPy
- Subtask: Graceful fallback if no GPU
- **Skip**: Auto-selection, capability checking, benchmarking

**Acceptance Criteria:**

- ✓ Switch backend with one parameter
- ✓ Distance matrix calculation works on both
- ✓ GPU detected correctly (or falls back to CPU)
- ✓ Code: ~150 lines total

---

#### **Story 1.3: Validation Framework (Minimal Testing)**

*Story Points: 3 | Priority: High*

**Tasks:**

**Task 1.3.1: Basic Test Suite**

- Subtask: Tour validity checker (Hamiltonian path)
- Subtask: Cost calculation validator
- Subtask: Backend equivalence tests (CPU == GPU results)
- **Skip**: Property-based testing, parametrized tests, coverage metrics

**Task 1.3.2: Known-Optimal Checker**

- Subtask: Load optimal costs from database
- Subtask: Calculate gap percentage
- **Skip**: Statistical tests, confidence intervals

**Acceptance Criteria:**

- ✓ Validates tours are legal
- ✓ Checks cost calculation correct
- ✓ Compares CPU vs GPU (5 test cases is enough!)
- ✓ **No coverage target** - just validate correctness

---

#### **Story 1.4: Solution Data Structure**

*Story Points: 2 | Priority: Medium*

**Tasks:**

**Task 1.4.1: Solution Class**

- Subtask: `Solution` dataclass: `tour: list[int]`, `cost: float`, `time: float`
- Subtask: Simple `is_valid()` method
- **Skip**: Metadata, export functions, comparison operators

**Acceptance Criteria:**

- ✓ Stores solution data
- ✓ Basic validation
- ✓ ~30 lines of code

---

### **EPIC 2: Core Algorithms - The Essentials** 🧮

*Duration: 4 weeks | Priority: CRITICAL | Story Points: 30*

**Description**: ONE constructive + 2-opt (CPU & GPU) + ONE metaheuristic.

---

#### **Story 2.1: Nearest Neighbor Heuristic**

*Story Points: 5 | Priority: Critical*

**Tasks:**

**Task 2.1.1: CPU Implementation**

- Subtask: Classic NN algorithm (greedy nearest)
- Subtask: Works with backend-agnostic distance matrix
- Subtask: Test on berlin52 (known solution)
- **Skip**: Multiple starting points, GPU parallelization, CVRP variant

**Acceptance Criteria:**

- ✓ Generates valid tours
- ✓ Within 30-50% of optimal (expected for NN)
- ✓ Works on all 10 test instances
- ✓ ~50 lines of code

---

#### **Story 2.2: 2-opt Local Search (CPU Baseline)**

*Story Points: 8 | Priority: CRITICAL*

**Tasks:**

**Task 2.2.1: First-Improvement 2-opt**

- Subtask: Implement edge swap with delta cost
- Subtask: Stop when no improvement found
- Subtask: Test improves NN solutions
- **Skip**: Best-improvement, don't-look-bits, 3-opt

**Task 2.2.2: CPU Performance Baseline**

- Subtask: Measure execution time on all 10 instances
- Subtask: Document time complexity empirically
- Subtask: Record for GPU comparison
- **Skip**: Detailed profiling, optimization

**Acceptance Criteria:**

- ✓ Improves NN solutions by 10-30%
- ✓ Baseline times established
- ✓ ~80 lines of code

---

#### **Story 2.3: GPU 2-opt (THE CORE CONTRIBUTION)** 🚀

*Story Points: 13 | Priority: CRITICAL*

**Tasks:**

**Task 2.3.1: Parallel Neighborhood Evaluation**

- Subtask: CuPy kernel for delta cost calculation (all pairs)
- Subtask: Reduction to find best swap
- Subtask: Validate matches CPU results
- **Reference**: fujimoto2011 paper

**Task 2.3.2: Memory Management for Large Instances**

- Subtask: Tiled evaluation for d15112 (15,112 nodes)
- Subtask: Monitor GPU memory usage
- Subtask: Stay within 4GB constraint
- **Skip**: Out-of-core processing, dynamic batch sizing

**Task 2.3.3: Performance Measurement**

- Subtask: Measure GPU vs CPU speedup
- Subtask: Plot speedup vs problem size
- Subtask: **Target**: 20-50x speedup on 5000+ nodes
- Subtask: Document results for TCC

**Task 2.3.4: Edge Cases & Debugging**

- Subtask: Handle convergence (no improvement)
- Subtask: Fix memory issues on d15112
- Subtask: Ensure correct tour updates

**Acceptance Criteria:**

- ✓ GPU 2-opt produces identical solutions to CPU
- ✓ 20x+ speedup on 5000+ node instances
- ✓ Handles d15112 within 4GB memory (79.8% usage)
- ✓ Results table ready for TCC Chapter 4
- ✓ **THIS IS YOUR THESIS CONTRIBUTION**

---

#### **Story 2.4: Simulated Annealing (Simple Version)**

*Story Points: 5 | Priority: High*

**Tasks:**

**Task 2.4.1: SA Framework**

- Subtask: Temperature schedule (geometric cooling)
- Subtask: Metropolis acceptance
- Subtask: 2-opt as neighbor generator
- **Skip**: Adaptive cooling, parallel chains, parameter tuning

**Task 2.4.2: Integration with GPU 2-opt**

- Subtask: Use GPU 2-opt for local search
- Subtask: CPU SA framework + GPU operators
- Subtask: Compare SA vs pure 2-opt
- **Skip**: Multiple parallel SA instances

**Acceptance Criteria:**

- ✓ SA escapes local optima
- ✓ Improves solution quality by 5-10% vs pure 2-opt
- ✓ ~100 lines of code

---

### **EPIC 3: Validation & Documentation** 📊

*Duration: 3 weeks | Priority: HIGH | Story Points: 22*

**Description**: Benchmark results + TCC documentation.

---

#### **Story 3.1: Benchmark Experiments**

*Story Points: 8 | Priority: Critical*

**Tasks:**

**Task 3.1.1: Solution Quality Validation**

- Subtask: Run all algorithms on 10 test instances
- Subtask: Calculate gap to optimal (%)
- Subtask: Create results table (Algorithm | Instance | Gap | Time)
- **Skip**: 30 runs, statistical tests, confidence intervals

**Task 3.1.2: Speedup Analysis**

- Subtask: GPU vs CPU time comparison
- Subtask: Plot speedup curve vs problem size
- Subtask: Identify memory bottlenecks
- **Target**: Show 20-50x on 5000+ nodes

**Task 3.1.3: Scalability Test**

- Subtask: Run on berlin52, kroA100, d493, d1291, d2103, d15112
- Subtask: Measure time vs problem size
- Subtask: Validate memory usage stays <4GB
- **Skip**: Throughput tests, batch processing

**Acceptance Criteria:**

- ✓ Results table for TCC Chapter 4
- ✓ Speedup plot ready
- ✓ Scalability demonstrated (100 → 15,000 nodes)
- ✓ All results reproducible

---

#### **Story 3.2: Comparison with Baselines**

*Story Points: 5 | Priority: High*

**Tasks:**

**Task 3.2.1: OR-Tools Comparison (Optional)**

- Subtask: Install Google OR-Tools
- Subtask: Run on same 10 instances
- Subtask: Compare quality and time
- **Skip if time-constrained** - focus on GPU speedup

**Task 3.2.2: Literature Comparison**

- Subtask: Compare with fujimoto2011 results (if instances overlap)
- Subtask: Position results vs osaba2020 survey
- Subtask: Document where your work fits
- **Skip**: Exhaustive comparison with all papers

**Acceptance Criteria:**

- ✓ Comparison table for TCC (your method vs 1-2 baselines)
- ✓ Discussion points for related work section

---

#### **Story 3.3: TCC Documentation**

*Story Points: 8 | Priority: Critical*

**Tasks:**

**Task 3.3.1: Results Chapter**

- Subtask: Write results presentation (tables, figures)
- Subtask: Create analysis section (speedup discussion)
- Subtask: Add scalability analysis
- Subtask: Include memory usage discussion

**Task 3.3.2: Methodology Chapter**

- Subtask: Describe algorithm implementations
- Subtask: Explain GPU parallelization strategy
- Subtask: Document backend abstraction
- **Skip**: Extensive architecture diagrams

**Task 3.3.3: Code Documentation**

- Subtask: Add NumPy-style docstrings to main functions
- Subtask: Create 1-2 usage examples (Jupyter notebooks)
- Subtask: Write README with setup instructions
- **Skip**: Sphinx API docs, comprehensive tutorials

**Acceptance Criteria:**

- ✓ TCC Chapters 3-4 drafted
- ✓ Code understandable by advisor
- ✓ Reproducibility instructions clear

---

#### **Story 3.4: Experiment Automation**

*Story Points: 3 | Priority: Medium*

**Tasks:**

**Task 3.4.1: Run All Script**

- Subtask: Single script runs all experiments
- Subtask: Saves results to CSV/JSON
- Subtask: Logs progress
- **Skip**: YAML configs, checkpointing, dashboards

**Task 3.4.2: Plot Generation**

- Subtask: Script generates speedup plot
- Subtask: Script generates results table
- **Skip**: Interactive dashboards, LaTeX integration

**Acceptance Criteria:**

- ✓ One command runs all benchmarks
- ✓ Results automatically exported
- ✓ Plots generated for TCC

---

## 📊 **MVP SUMMARY METRICS**

| Epic | Stories | Story Points | Duration | Priority |
|------|---------|--------------|----------|----------|
| **EPIC 1: Foundation** | 4 | 18 | 2 weeks | CRITICAL |
| **EPIC 2: Core Algorithms** | 4 | 30 | 4 weeks | CRITICAL |
| **EPIC 3: Validation & Docs** | 4 | 22 | 3 weeks | HIGH |
| **TOTAL** | **12 Stories** | **70 Points** | **9-10 weeks** | - |

**Estimated Effort**: 70 points ≈ **140-180 hours** (+ 70-95h reading = **210-275 total hours**)

---

## 🗓️ **REALISTIC 10-WEEK TIMELINE**

### **Weeks 1-2: Foundation** ⚙️

- ✅ Database loader (10 instances)
- ✅ Backend abstraction (NumPy ↔ CuPy)
- ✅ Basic validation
- 📚 **Reading**: Logic of Logistics Ch 16-17

### **Weeks 3-4: CPU Baseline** 🖥️

- ✅ Nearest Neighbor
- ✅ 2-opt CPU
- ✅ Baseline measurements
- 📚 **Reading**: fujimoto2011

### **Weeks 5-6: GPU 2-opt (CORE!)** 🚀

- ✅ GPU kernel implementation
- ✅ Memory optimization for d15112
- ✅ Speedup measurements
- 📚 **Reading**: benaini2018

### **Weeks 7-8: SA + Integration** 🔥

- ✅ Simulated Annealing
- ✅ SA + GPU 2-opt hybrid
- ✅ Quality improvements
- 📚 **Reading**: osaba2020

### **Weeks 9-10: Results & Documentation** 📊

- ✅ Benchmark experiments
- ✅ Results tables and plots
- ✅ TCC Chapters 3-4 draft
- 📚 **Reading**: nazari2018

### **Week 11-12: Buffer & TCC Polish** ✨

- ✅ Fix bugs discovered in testing
- ✅ Complete TCC writing
- ✅ Advisor review iterations

---

## ✅ **EXPLICIT OUT-OF-SCOPE (For MVP)**

**Removed from original plan:**

- ❌ All 113 TSPLIB instances (use 10)
- ❌ 95% test coverage (validation only)
- ❌ Genetic Algorithm (too complex)
- ❌ 3-opt, Tabu Search (nice-to-have)
- ❌ Full CVRP implementation (TSP MVP first)
- ❌ Batch processing, streams, multi-GPU
- ❌ Extensive profiling tools
- ❌ Comprehensive API documentation
- ❌ Docker containers, reproducibility packages
- ❌ OR-Tools comparison (if time-constrained)
- ❌ Statistical validation (30 runs, t-tests)

**Can be added AFTER MVP if time permits!**

---

## 🎯 **SUCCESS CRITERIA (MVP)**

### **Technical**

✓ GPU 2-opt works correctly (matches CPU results)  
✓ 20x+ speedup demonstrated on 5000+ nodes  
✓ Handles d15112 (max instance) within 4GB  
✓ 10 TSPLIB instances solved and validated  

### **Academic**

✓ Results chapter with tables and plots  
✓ Methodology chapter explaining approach  
✓ Comparison with 1-2 literature baselines  
✓ Code documented enough for advisor review  

### **TCC Contribution**

✓ **"GPU-accelerated 2-opt achieves 20-50x speedup on TSP instances up to 15,000 nodes within 4GB memory constraint"**  
✓ This is your thesis statement - everything else supports it!

---

## 🚀 **IMMEDIATE NEXT STEPS** (This Week!)

1. **Create project structure**:

```bash
gpu_accelerated/
├── code/src/
│   ├── backends/      # NumPy/CuPy abstraction
│   ├── algorithms/    # NN, 2-opt, SA
│   ├── utils/         # Distance, validation
│   └── protocols.py   # Type hints
└── scripts/
    ├── run_experiments.py
    └── generate_plots.py
```

2. **Start Story 1.1**: Database loader (3-4 hours)
3. **Select 10 TSPLIB instances** from routing.duckdb
4. **Set up Git repo** with simple README

**This plan fits your 3-month TCC timeline!** 🎓✨
