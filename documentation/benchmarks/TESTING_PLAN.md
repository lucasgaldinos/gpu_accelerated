# Benchmark Testing Plan

**Status:** 🔄 Pre-Execution  
**Purpose:** Validate BenchmarkRunner with SA+2opt and GA+2opt on CPU/GPU

---

## Critical Finding

⚠️ **Callback Support Missing in Algorithms**

The current SA and GA implementations do NOT support the `ProgressCallback` protocol. This means:

- ✅ BenchmarkRunner infrastructure is complete
- ❌ Algorithms cannot integrate with ConvergenceTracker
- 🔧 Need to add callback support to SA and GA before testing

**Impact:**

- Cannot test convergence tracking
- Cannot measure time-to-target
- Cannot collect convergence_history

**Resolution Path:**

1. Add callback support to SA (`metaheuristics/simulated_annealing.py`)
2. Add callback support to GA (`metaheuristics/genetic_algorithm.py`)
3. Update tests to validate callback integration
4. Then proceed with benchmark testing

---

## Test Configurations

### Test 1: SA+2opt CPU Benchmark

```python
config_sa_cpu = BenchmarkConfig(
    algorithm="SA",
    backend="numpy",
    instance_name="berlin52",
    num_repetitions=30,
    time_budget=60.0,
    target_gap=0.05,
    convergence_log_interval=100,
    algorithm_params={
        "initial_temp": 1000.0,
        "cooling_rate": 0.95,
        "min_temp": 1e-3,
        "neighbor_method": "2-opt"
    }
)
```

**Expected Outcomes:**

- All 30 runs complete successfully
- Runtime: ~40-60 seconds per run
- Final cost: Near 7542 (berlin52 optimal)
- Convergence history: Monotonic decrease
- No exceptions or NaN values

### Test 2: SA+2opt GPU Benchmark

```python
config_sa_gpu = config_sa_cpu.replace(backend="cupy")
```

**Expected Outcomes:**

- All 30 runs complete successfully
- Runtime: Faster than CPU (if problem size justifies GPU overhead)
- Final cost: Similar quality to CPU (± 1%)
- Memory usage: < 4GB VRAM (GTX 1050 limit)
- GPU memory cleanup working (no leaks)

### Test 3: GA+2opt CPU Benchmark

```python
config_ga_cpu = BenchmarkConfig(
    algorithm="GA",
    backend="numpy",
    instance_name="berlin52",
    num_repetitions=30,
    time_budget=60.0,
    target_gap=0.05,
    convergence_log_interval=10,  # Log every 10 generations
    algorithm_params={
        "population_size": 60,
        "max_generations": 1000,
        "crossover_rate": 0.9,
        "mutation_rate": 0.1,
        "use_2opt": True,
        "selection_method": "crowding"
    }
)
```

**Expected Outcomes:**

- All 30 runs complete successfully
- Runtime: ~50-70 seconds per run (population overhead)
- Final cost: Competitive with SA (berlin52 optimal ± 2%)
- Higher variance than SA (stochastic population)
- Convergence history: Stepwise improvements

### Test 4: GA+2opt GPU Benchmark

```python
config_ga_gpu = config_ga_cpu.replace(backend="cupy")
```

**Expected Outcomes:**

- All 30 runs complete successfully
- Runtime: Significant speedup (batch fitness evaluation on GPU)
- Final cost: Similar quality to CPU (± 1%)
- Memory usage: < 4GB VRAM
- GPU speedup more pronounced than SA (vectorized population operations)

---

## Validation Checklist

### Execution Validation

- [ ] No exceptions during any run
- [ ] All 30 repetitions complete for each config
- [ ] Seed management works (reproducible results)
- [ ] GPU memory cleanup prevents VRAM leaks
- [ ] Progress tracking displays correctly

### Data Quality Validation

- [ ] No NaN or Inf values in costs
- [ ] Convergence history is monotonic (minimization)
- [ ] Final costs within reasonable range of optimal
- [ ] Time-to-target calculated correctly (or None if unreached)
- [ ] Memory usage tracking works (especially GPU)

### Statistical Validation

- [ ] StatisticalAnalyzer normality tests run without errors
- [ ] Paired comparison selects correct test (t-test vs Wilcoxon)
- [ ] Cohen's d calculated and interpreted correctly
- [ ] Confidence intervals are sensible (not NaN, not infinite)
- [ ] Holm-Bonferroni correction works for multiple comparisons

### Report Validation

- [ ] Markdown table formats correctly
- [ ] No formatting errors in output
- [ ] Effect size interpretation matches Cohen's thresholds
- [ ] p-values formatted with appropriate precision
- [ ] Summary statistics match manual calculations

---

## Bug Detection Protocol

### Runtime Errors

**If exception occurs:**

1. Log full traceback
2. Identify failure point (algorithm, collector, analyzer, reporter)
3. Record input configuration that caused failure
4. Create JIRA issue with "Bug" label
5. Add to post-milestones fix list

### Quality Anomalies

**If costs are anomalous:**

1. Check for NaN/Inf propagation
2. Verify distance matrix correctness
3. Compare CPU vs GPU outputs (should be similar)
4. Investigate convergence history for sudden jumps
5. Record as technical debt if systematic

### Performance Issues

**If runtime/memory unexpected:**

1. Profile GPU VRAM usage (cupy.get_default_memory_pool())
2. Check for memory leaks (free_all_blocks working?)
3. Compare against baseline (simple 2opt without SA/GA)
4. Identify bottlenecks (fitness evaluation? neighbor generation?)
5. Document optimization opportunities

### Statistical Failures

**If statistical tests fail:**

1. Check for insufficient sample size (n < 30)
2. Verify normality test assumptions
3. Investigate extreme outliers
4. Record data distribution characteristics
5. Consider robust alternatives (bootstrap, permutation)

---

## Current Status: BLOCKED

**Blocker:** Algorithms lack callback support

**Next Steps:**

1. Add `ProgressCallback` integration to SA
2. Add `ProgressCallback` integration to GA
3. Write unit tests for callback lifecycle
4. Then execute benchmark tests

**Alternative Path:**

- Test BenchmarkRunner with mock algorithms
- Validate infrastructure independently
- Add callback support as separate task (Milestone 10?)

---

## Actor-Critic Evaluation Criteria

### For Each Milestone (M2, M3, M5)

**Code Quality Dimensions:**

- Adherence to Class P-Data pattern
- Backend abstraction correctness (xp usage)
- Type hint completeness
- Documentation quality (docstrings)
- Error handling robustness

**Architectural Quality:**

- Single Responsibility Principle
- Protocol compliance
- Modularity and separation of concerns
- Extensibility for new backends/algorithms

**Testing Quality:**

- Test coverage (unit, integration)
- Edge case handling
- CPU/GPU parity validation
- Statistical rigor

**Identified Flaws:**

- Record as JIRA "Technical Debt" issues
- Prioritize: Correctness > Performance > Style
- Create step-by-step fix plan for post-milestones
- No immediate fixes (stay focused on milestones)

---

## Notes

**Berlin52 Optimal:** 7542  
**System Constraints:** 4GB VRAM (GTX 1050 Mobile)  
**Statistical Power:** n=30 (CLT applies)  
**Significance Level:** α=0.05  
**Effect Size Thresholds:** small=0.2, medium=0.5, large=0.8 (Cohen's d)
