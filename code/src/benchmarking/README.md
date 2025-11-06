# Benchmarking Infrastructure

**Purpose:** Statistically rigorous performance evaluation following Section 3.5 experimental design.

## Architecture

```
src/benchmarking/
├── __init__.py           # Public API exports
├── config.py             # BenchmarkConfig, BenchmarkResult data models
├── runner.py             # BenchmarkRunner orchestrator
├── collectors.py         # ConvergenceTracker, MetricsCollector
├── statistics.py         # StatisticalAnalyzer (scipy integration)
└── reporting.py          # ReportGenerator (tables, summaries)
```

## Module Responsibilities

### 1. `config.py` - Data Structures

**BenchmarkConfig:**

- Captures experimental parameters (algorithm, backend, instance)
- Manages reproducibility (seed generation, repetitions)
- Validates configuration consistency

**BenchmarkResult:**

- Stores single-run outcomes (runtime, quality, convergence)
- JSON serialization for persistence
- Memory-efficient (convergence history as list, not full arrays)

**ComparisonPair:**

- Pairs configurations for statistical comparison (CPU vs GPU)
- Validates pairing (same instance, vary in one dimension)

### 2. `runner.py` - Orchestration

**BenchmarkRunner:**

- Multi-run execution with seed management
- Progress tracking (prints % complete, ETA)
- Result streaming (yields results, doesn't hold all in memory)
- Export to CSV/JSON

**Key Features:**

- Automatic seed sequence: `s_i = s_0 + i` for run `i`
- GPU memory cleanup between runs
- Backend-agnostic (works with NumPy/CuPy)

### 3. `collectors.py` - Metrics Collection

**ConvergenceTracker:**

- Implements `ProgressCallback` protocol
- Logs quality every N iterations
- Tracks time-to-target (5% gap from optimum)
- Real-time monitoring during execution

**MetricsCollector:**

- Coordinates tracking and result packaging
- Memory usage monitoring (GPU VRAM)
- Target gap calculation from known optimal

### 4. `statistics.py` - Statistical Analysis

**StatisticalAnalyzer:**

- Shapiro-Wilk normality testing
- Test selection (t-test vs Wilcoxon, ANOVA vs Kruskal-Wallis)
- Effect size calculation (Cohen's d)
- Bootstrap confidence intervals
- Holm-Bonferroni multiple comparison correction

**StatisticalSummary:**

- Complete statistics for paired comparison
- Speedup calculation with CI
- Significance testing (p-values, effect sizes)

### 5. `reporting.py` - Report Generation

**ReportGenerator:**

- Markdown table formatting (Section 4 format)
- LaTeX export (future)
- Summary statistics (text format)
- Plot generation (future: matplotlib integration)

## Usage Example

```python
from src.benchmarking import BenchmarkConfig, BenchmarkRunner, StatisticalAnalyzer
from src.data_models.problem import Problem
from src.protocols.problem_context import ProblemContext
from src.algorithms.metaheuristics import SimulatedAnnealing
import numpy as np

# 1. Configure benchmark
config = BenchmarkConfig(
    algorithm="SA",
    backend="numpy",
    instance_name="berlin52",
    num_repetitions=30,  # Section 3.5: n=30 for CLT
    time_budget=60.0,     # Section 3.5.2: 60 seconds
    target_gap=0.05,      # Section 3.5.2: 5% from optimal
)

# 2. Load problem and create context
problem = Problem(...)  # Load from database
context = ProblemContext(problem, xp=np)

# 3. Run benchmark
runner = BenchmarkRunner()
results = list(runner.run_benchmark(config, context, SimulatedAnnealing))

# 4. Export results
runner.export_csv(results, "results/sa_cpu_berlin52.csv")
runner.export_json(results, "results/sa_cpu_berlin52.json")

# 5. Statistical analysis (CPU vs GPU)
analyzer = StatisticalAnalyzer(alpha=0.05)
cpu_times = np.array([r.runtime_seconds for r in cpu_results])
gpu_times = np.array([r.runtime_seconds for r in gpu_results])

summary = analyzer.paired_comparison(
    cpu_times, gpu_times,
    label="SA: NumPy vs CuPy (berlin52)",
    metric_name="runtime_seconds"
)

print(f"Speedup: {summary.get_speedup():.2f}x")
print(f"p-value: {summary.p_value:.4f}")
print(f"Effect size: {summary.effect_size:.2f}")
```

## Statistical Methodology (Section 3.5.3)

### Normality Testing

```python
analyzer = StatisticalAnalyzer(alpha=0.05)
p_value, is_normal = analyzer.test_normality(data)
```

### Paired Comparison

```python
summary = analyzer.paired_comparison(data_a, data_b, label, metric)
# Automatically selects:
# - Paired t-test (if both normal)
# - Wilcoxon signed-rank (if non-normal)
```

### Bootstrap CI

```python
ci_low, ci_high, samples = analyzer.bootstrap_ci(
    data, np.mean,
    confidence_level=0.95,
    n_resamples=10000
)
```

### Multiple Comparison Correction

```python
p_values = [0.001, 0.02, 0.03, 0.15]
results = analyzer.holm_bonferroni_correction(p_values, alpha=0.05)
for idx, p, is_sig in results:
    print(f"Comparison {idx}: p={p:.3f}, significant={is_sig}")
```

## Experimental Design Compliance

### Section 3.5.1 (Deterministic 2-opt)

- ✅ Time-to-convergence metric
- ✅ 30 repetitions for CLT
- ✅ Identical solutions validation

### Section 3.5.2 (Stochastic Metaheuristics)

- ✅ Fixed-time quality (60s budget)
- ✅ Time-to-target (5% gap)
- ✅ Convergence logging (every 100 iterations)
- ✅ 30 independent runs with different seeds

### Section 3.5.3 (Statistical Methodology)

- ✅ Shapiro-Wilk normality test
- ✅ Parametric/non-parametric test selection
- ✅ 95% confidence intervals
- ✅ Effect size (Cohen's d)
- ✅ Holm-Bonferroni correction

### Section 3.5.4 (Reproducibility)

- ✅ Seed management (s_i = 42 + i)
- ✅ Configuration serialization (JSON)
- ✅ Result persistence (CSV + JSON with convergence)
- ✅ Hardware/software documentation

## Data Flow

```
Problem → ProblemContext → BenchmarkConfig
                                ↓
                        BenchmarkRunner
                                ↓
                    ┌───────────┴───────────┐
                    ↓                       ↓
            ConvergenceTracker      MetricsCollector
                    ↓                       ↓
                BenchmarkResult (×30 runs)
                                ↓
                        StatisticalAnalyzer
                                ↓
                        StatisticalSummary
                                ↓
                        ReportGenerator
                                ↓
                    Tables, Plots, LaTeX
```

## Memory Management

- **Streaming Results:** Runner yields results (doesn't hold all 30 in memory)
- **Convergence History:** Sparse logging (every 100 iterations, not every step)
- **GPU Memory:** Automatic cleanup between runs (`free_all_blocks()`)
- **Export Options:** CSV (summary only) or JSON (with convergence data)

## Testing

Run demo to verify installation:

```bash
cd /home/lucas_galdino/TCC-name_to_define/gpu_accelerated
uv run python code/examples/benchmark_sa_demo.py
```

Expected output:

- 5 CPU runs (with progress %)
- 5 GPU runs (if CuPy available)
- Statistical comparison
- Markdown table
- CSV exports in `data/benchmarks/demo/`

## Future Enhancements (Post-Milestone 5)

- [ ] Matplotlib integration for convergence plots
- [ ] LaTeX table export for thesis
- [ ] Multi-instance batch processing
- [ ] Parallel execution (multiple GPUs)
- [ ] Real-time dashboard (web UI)
- [ ] Integration with TSPLIB database loader

## References

- Section 3.5: Experimental Design (first_draft.md)
- Section 4: RESULTADOS (first_draft.md)
- Hoefler & Belli (2015): DOI: 10.1145/2807591.2807644
- Hothorn et al. (2005): Benchmark experimental design
- gpu_cpu_comparison_methodology.md: Statistical best practices

---

**Status:** Milestone 5 - Core implementation complete  
**Next:** Integration testing, TSPLIB dataset integration, plot generation
