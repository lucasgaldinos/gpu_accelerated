# BenchmarkRunner Architecture

**Status:** ✅ Complete (Milestone 5)  
**Location:** `code/src/benchmarking/`  
**Purpose:** Statistical performance evaluation infrastructure for routing algorithms

---

## Overview

The `benchmarking` module provides a **modular, academically rigorous** framework for comparing CPU and GPU algorithm implementations. It follows the statistical methodology defined in Section 3.5 of the TCC thesis.

### Core Design Principles

1. **Separation of Concerns:** Config, collection, analysis, and reporting are independent modules
2. **Protocol-Based Integration:** Algorithms implement `ProgressCallback` for real-time metrics
3. **Statistical Rigor:** Automatic normality testing, paired test selection, effect size calculation
4. **Reproducibility:** Deterministic seed management, JSON serialization of configs and results
5. **Streaming Architecture:** Iterator pattern prevents memory overflow on large benchmarks

---

## Component Architecture

```
┌─────────────────┐
│ BenchmarkConfig │ ──→ Defines experiment parameters
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ BenchmarkRunner │ ──→ Orchestrates multiple runs
└────────┬────────┘
         │
         ├──→ MetricsCollector ──→ Creates ConvergenceTracker
         │                         (implements ProgressCallback)
         │
         ├──→ Algorithm.solve() ──→ Executes with callback
         │
         └──→ BenchmarkResult ──→ Packages metrics
                 │
                 ▼
┌──────────────────────┐
│ StatisticalAnalyzer  │ ──→ Performs normality tests,
└──────────┬───────────┘     paired comparisons,
           │                 effect size calculation
           ▼
┌──────────────────────┐
│ ReportGenerator      │ ──→ Formats Markdown tables
└──────────────────────┘
```

---

## Module Breakdown

### 1. `config.py` - Data Models

**Purpose:** Define experiment configurations and results with JSON serialization.

#### BenchmarkConfig

```python
@dataclass(frozen=True)
class BenchmarkConfig:
    algorithm: str                 # "SA", "GA", "2opt", "nearest_neighbor"
    backend: str                   # "numpy" (CPU) or "cupy" (GPU)
    instance_name: str             # Problem identifier
    num_repetitions: int = 30      # Statistical power (n ≥ 30 for CLT)
    time_budget: float = 60.0      # Seconds (stochastic algorithms)
    target_gap: float = 0.05       # Quality target (5% from optimal)
    convergence_log_interval: int = 100  # Logging frequency
    algorithm_params: dict = field(default_factory=dict)
```

**What to Measure:**

- `runtime_seconds`: Total execution time
- `final_tour_cost`: Solution quality
- `time_to_target`: Convergence speed (time to reach target_gap)
- `convergence_history`: Quality over iterations
- `memory_peak_mb`: GPU VRAM usage

**Algorithm Compatibility:**

- **All algorithms:** runtime, final_cost, convergence_history
- **Stochastic only (SA, GA):** time_budget, target_gap, time_to_target
- **Deterministic (2opt, NN):** Use time_to_convergence as metric

#### BenchmarkResult

```python
@dataclass(frozen=True)
class BenchmarkResult:
    config: BenchmarkConfig
    run_index: int
    seed: int                      # Seed used (42 + run_index)
    runtime_seconds: float
    final_tour_cost: float
    time_to_target: Optional[float]  # None if target not reached
    convergence_history: List[Tuple[float, float]]  # (time, cost)
    memory_peak_mb: float
```

**The Result Flow:**

1. `BenchmarkRunner` creates `MetricsCollector`
2. `MetricsCollector` creates `ConvergenceTracker` (callback)
3. Callback passed to algorithm: `Algorithm(context, callback=tracker)`
4. Algorithm executes, tracker logs quality at intervals
5. Runner calls `collector.create_result()` → packages everything
6. Returns complete `BenchmarkResult` with all metrics

#### ComparisonPair

```python
@dataclass(frozen=True)
class ComparisonPair:
    cpu_results: List[BenchmarkResult]
    gpu_results: List[BenchmarkResult]
    
    def validate(self) -> None:
        # Ensures CPU/GPU configs match (algorithm, instance, params)
        # Ensures same number of runs
```

---

### 2. `collectors.py` - Real-Time Metrics Collection

**Purpose:** Track convergence and resource usage during algorithm execution.

#### ConvergenceTracker

**Type:** Implements `ProgressCallback` protocol  
**Integration:** Passed as **optional parameter** (NOT decorator)

```python
class ConvergenceTracker:
    def __init__(self, log_interval: int = 100):
        self.history: List[Tuple[float, float]] = []  # (time, cost)
        
    def on_start(self, initial_cost: float) -> None:
        # Called once at algorithm start
        self.start_time = time.time()
        
    def on_iteration(self, iteration: int, current_cost: float) -> None:
        # Called every iteration (logs every log_interval iterations)
        if iteration % self.log_interval == 0:
            elapsed = time.time() - self.start_time
            self.history.append((elapsed, current_cost))
            
    def on_complete(self, final_cost: float) -> None:
        # Called once at algorithm completion
        elapsed = time.time() - self.start_time
        self.history.append((elapsed, final_cost))
```

**Usage Pattern:**

```python
# In algorithm __init__:
def __init__(self, context: ProblemContext, callback: Optional[ProgressCallback] = None):
    self.callback = callback
    
# In algorithm.solve():
if self.callback:
    self.callback.on_start(initial_cost)
    
for iteration in range(max_iterations):
    # ... algorithm logic ...
    if self.callback:
        self.callback.on_iteration(iteration, current_cost)
        
if self.callback:
    self.callback.on_complete(final_cost)
```

**Key Properties:**

- **Optional:** Algorithms work without callbacks
- **Single:** One callback per algorithm instance
- **Protocol-Based:** Not decorator-based (explicit parameter passing)
- **State:** Callback maintains history internally

#### MetricsCollector

**Purpose:** Coordinate tracking and package results.

```python
class MetricsCollector:
    def create_tracker(self, log_interval: int) -> ConvergenceTracker:
        # Factory method for callback creation
        
    def create_result(self, config: BenchmarkConfig, run_index: int, 
                      runtime: float, final_cost: float, 
                      tracker: ConvergenceTracker) -> BenchmarkResult:
        # Packages metrics into BenchmarkResult
        # Calculates time_to_target from convergence_history
        # Measures GPU memory via cupy.get_default_memory_pool()
```

---

### 3. `statistics.py` - Statistical Analysis

**Purpose:** Implement Section 3.5 methodology with scipy integration.

#### StatisticalAnalyzer

**Methods:**

1. **`test_normality(data: List[float]) -> Tuple[bool, float]`**
   - Shapiro-Wilk test (Shapiro & Wilk, 1965)
   - Returns: (is_normal, p_value)
   - Threshold: α = 0.05

2. **`paired_comparison(cpu_data: List[float], gpu_data: List[float]) -> StatisticalSummary`**
   - **Automatic test selection:**
     - If both normal → Paired t-test (Student, 1908)
     - If non-normal → Wilcoxon signed-rank (Wilcoxon, 1945)
   - Returns: test statistic, p-value, CI, effect size

3. **`cohens_d(cpu_data: List[float], gpu_data: List[float]) -> Tuple[float, str]`**
   - Cohen's d effect size (Cohen, 1988)
   - Interpretation: small (0.2), medium (0.5), large (0.8)

4. **`bootstrap_ci(data: List[float], confidence: float = 0.95, n_bootstrap: int = 10000) -> Tuple[float, float]`**
   - Percentile method (Efron & Tibshirani, 1993)
   - Returns: (lower_bound, upper_bound)

5. **`holm_bonferroni_correction(p_values: List[float], alpha: float = 0.05) -> List[bool]`**
   - Multiple comparison correction (Holm, 1979)
   - Returns: List of rejection decisions

#### StatisticalSummary

```python
@dataclass
class StatisticalSummary:
    cpu_mean: float
    gpu_mean: float
    cpu_std: float
    gpu_std: float
    cpu_normality_p: float      # Shapiro-Wilk p-value
    gpu_normality_p: float
    test_name: str              # "paired_t" or "wilcoxon"
    test_statistic: float
    p_value: float
    confidence_interval: Tuple[float, float]  # For mean difference
    effect_size: float          # Cohen's d
    effect_interpretation: str  # "small", "medium", "large"
```

---

### 4. `runner.py` - Orchestration

**Purpose:** Execute benchmarks with seed management and progress tracking.

#### BenchmarkRunner

**Key Method:** `run_benchmark(config: BenchmarkConfig) -> Iterator[BenchmarkResult]`

**Implementation:**

```python
def run_benchmark(self, config: BenchmarkConfig) -> Iterator[BenchmarkResult]:
    """Streaming iterator to avoid memory overflow."""
    
    for run_idx in range(config.num_repetitions):
        # 1. Seed management (deterministic reproducibility)
        seed = config.get_run_seed(run_idx)  # seed = 42 + run_idx
        np.random.seed(seed)
        if config.backend == "cupy":
            cp.random.seed(seed)
        
        # 2. Create metrics collector
        collector = MetricsCollector()
        tracker = collector.create_tracker(config.convergence_log_interval)
        
        # 3. Initialize algorithm with callback
        context = ProblemContext(...)
        algorithm = ALGORITHM_MAP[config.algorithm](context, callback=tracker)
        
        # 4. Execute
        start_time = time.time()
        solution = algorithm.solve()
        runtime = time.time() - start_time
        
        # 5. Package result
        result = collector.create_result(config, run_idx, runtime, 
                                          solution.tour_cost, tracker)
        
        # 6. GPU cleanup
        if config.backend == "cupy":
            cp.get_default_memory_pool().free_all_blocks()
        
        yield result  # Streaming!
```

**Progress Tracking:**

```python
# In user code:
results = []
for i, result in enumerate(runner.run_benchmark(config)):
    progress = (i + 1) / config.num_repetitions * 100
    print(f"Progress: {progress:.1f}% - Run {i+1} runtime: {result.runtime_seconds:.2f}s")
    results.append(result)
```

---

### 5. `reporting.py` - Markdown Table Generation

**Purpose:** Format results for Section 4 (Results) of TCC thesis.

#### ReportGenerator

**Key Method:** `format_markdown_table(summary: StatisticalSummary, algorithm: str) -> str`

**Output Example:**

```markdown
| Algorithm | Backend | Mean Runtime (s) | Std Dev | Mean Cost | Std Dev | Effect Size | p-value |
|-----------|---------|------------------|---------|-----------|---------|-------------|---------|
| SA        | CPU     | 45.32            | 3.21    | 7580.12   | 12.45   | -            | -       |
| SA        | GPU     | 12.45            | 1.87    | 7582.34   | 11.98   | d=0.82 (large) | 0.0023 |
```

**Interpretation:**

```python
def _interpret_effect_size(cohens_d: float) -> str:
    if abs(cohens_d) < 0.2:
        return "negligible"
    elif abs(cohens_d) < 0.5:
        return "small"
    elif abs(cohens_d) < 0.8:
        return "medium"
    else:
        return "large"
```

---

## Callback System Deep Dive

### Why Optional Parameters (Not Decorators)?

**Decision Rationale:**

- **Explicit Integration:** Algorithm knows about callback, can choose when to notify
- **Single Callback:** One tracker per algorithm instance (clear ownership)
- **Protocol-Based:** Interface defined via `ProgressCallback` protocol (type-safe)
- **No Magic:** No hidden state, no decorator overhead, no metaclass complexity

### Lifecycle Hooks

```python
class ProgressCallback(Protocol):
    def on_start(self, initial_cost: float) -> None:
        """Called once at algorithm initialization."""
        
    def on_iteration(self, iteration: int, current_cost: float) -> None:
        """Called every iteration (implementation may throttle)."""
        
    def on_complete(self, final_cost: float) -> None:
        """Called once at algorithm completion."""
```

**Contract:**

- `on_start` called BEFORE first iteration
- `on_iteration` called DURING iteration (throttled by log_interval)
- `on_complete` called AFTER last iteration
- Callback maintains internal state (history, timers)

### Integration Example (Simulated Annealing)

```python
class SimulatedAnnealing:
    def __init__(self, context: ProblemContext, 
                 callback: Optional[ProgressCallback] = None):
        self.context = context
        self.callback = callback
        
    def solve(self) -> Solution:
        current_solution = self._random_solution()
        
        # Lifecycle: START
        if self.callback:
            self.callback.on_start(current_solution.tour_cost)
        
        for iteration in range(self.max_iterations):
            # ... SA logic ...
            
            # Lifecycle: ITERATION
            if self.callback:
                self.callback.on_iteration(iteration, current_solution.tour_cost)
        
        # Lifecycle: COMPLETE
        if self.callback:
            self.callback.on_complete(current_solution.tour_cost)
        
        return current_solution
```

---

## Future Extensibility

### Backend Abstraction for scipy

**Current Limitation:** `statistics.py` uses NumPy exclusively.

**Future Enhancement:** CuPy has `cupyx.scipy` with most statistical functions:

- `cupyx.scipy.stats.shapiro` (GPU-accelerated normality testing)
- `cupyx.scipy.stats.ttest_rel` (GPU-accelerated paired t-test)
- `cupyx.scipy.stats.wilcoxon` (GPU-accelerated Wilcoxon test)

**Proposed Architecture:**

```python
class StatisticalAnalyzer:
    def __init__(self, backend: BackendProtocol):
        self.xp = backend  # numpy or cupy
        self.stats = self._get_stats_module()
        
    def _get_stats_module(self):
        if self.xp.__name__ == "cupy":
            import cupyx.scipy.stats as stats
        else:
            import scipy.stats as stats
        return stats
```

**Benefits:**

- Accelerate statistical analysis for large result sets
- Maintain API compatibility (scipy and cupyx.scipy have similar interfaces)
- Enable GPU-to-GPU workflow (no CPU transfers)

---

## Usage Workflow

### 1. Define Configuration

```python
from benchmarking import BenchmarkConfig

config = BenchmarkConfig(
    algorithm="SA",
    backend="cupy",
    instance_name="berlin52",
    num_repetitions=30,
    time_budget=60.0,
    target_gap=0.05,
    convergence_log_interval=100,
    algorithm_params={
        "initial_temperature": 1000.0,
        "cooling_rate": 0.95,
        "min_temperature": 1e-3
    }
)
```

### 2. Run Benchmark

```python
from benchmarking import BenchmarkRunner

runner = BenchmarkRunner()
results = list(runner.run_benchmark(config))  # Collect all results
```

### 3. Analyze Results

```python
from benchmarking import StatisticalAnalyzer, ComparisonPair

# Run CPU version
config_cpu = config.replace(backend="numpy")
cpu_results = list(runner.run_benchmark(config_cpu))

# Create comparison
pair = ComparisonPair(cpu_results=cpu_results, gpu_results=results)
pair.validate()  # Ensures configs match

# Statistical analysis
analyzer = StatisticalAnalyzer()
summary = analyzer.paired_comparison(
    [r.runtime_seconds for r in cpu_results],
    [r.runtime_seconds for r in results]
)
```

### 4. Generate Report

```python
from benchmarking import ReportGenerator

generator = ReportGenerator()
markdown = generator.format_markdown_table(summary, "SA")
print(markdown)
```

---

## Validation Checklist

When adding new algorithms or modifying benchmarking:

- [ ] Algorithm implements `ProgressCallback` lifecycle hooks
- [ ] `BenchmarkConfig.algorithm` added to `ALGORITHM_MAP`
- [ ] Seed management respects backend (numpy vs cupy)
- [ ] GPU memory cleanup in runner (free_all_blocks)
- [ ] Convergence history is monotonic for minimization
- [ ] Time-to-target calculation handles "never reached" case
- [ ] Statistical tests validate normality before test selection
- [ ] Effect size calculated and interpreted correctly
- [ ] Report formatting matches Section 4 table structure

---

## References

- Hoefler, T., & Belli, R. (2015). Scientific benchmarking of parallel computing systems. *SC'15 Proceedings*. DOI: 10.1145/2807591.2807644
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum Associates.
- Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality. *Biometrika*, 52(3-4), 591-611.
- Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin*, 1(6), 80-83.
- Efron, B., & Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman and Hall/CRC.
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6(2), 65-70.
