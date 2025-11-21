# Kernel Migration Plan: Manual Reduction → CUB Library

**Date**: 2025-01-28  
**Status**: 🟡 In Progress  
**Estimated Time**: 2-3 hours  
**Priority**: HIGH (saves 5-7 hours per future kernel)

---

## 📋 Executive Summary

After spending 9.5 hours debugging manual parallel reduction (see `GPU_REDUCTION_PATTERNS_AND_LESSONS.md`), we're migrating to NVIDIA CUB library for:

- ✅ Production-tested correctness (handles non-power-of-2 automatically)
- ✅ Better maintainability (50 lines → 5 lines)
- ✅ Future-proofing (CUB is industry standard)

## 🔍 Current State Analysis

### Environment

- **CUDA Version**: 12.6.20 ✅
- **CUB Headers**: `/usr/local/cuda/include/cub/` ✅
- **CuPy**: Supports `RawKernel` with `-I` flag ✅

### Existing Kernels (Manual Reduction)

| Kernel | Location | Used By | LOC | Status |
|--------|----------|---------|-----|--------|
| `two_opt_single.cu` | `code/src/algorithms/kernels/` | HybridNaive | 170 | ✅ Works (after 9.5h debug) |
| `two_opt_batch.cu` | `code/src/algorithms/kernels/` | HybridOptimized | 220 | ✅ Works (after 9.5h debug) |
| `ga_fujimoto.cu` | `code/src/algorithms/kernels/` | FullGPU | 800+ | ✅ Different algorithm (no change) |
| `cost_calculator.cu` | `code/src/algorithms/kernels/` | HybridOptimized | 50 | ✅ Simple (no reduction) |

### Python Files Loading Kernels

1. **`genetic_algorithm_hybrid_naive.py`** (line 59)
   ```python
   self.two_opt_kernel = cp.RawKernel(kernel_source, "two_opt_kernel")
   ```
   - Loads: `two_opt_single.cu`
   - Change needed: Add compilation options for CUB

2. **`genetic_algorithm_hybrid_optimized.py`** (lines 73, 81)
   ```python
   self.two_opt_kernel = cp.RawKernel(two_opt_source, "two_opt_batch_kernel")
   self.cost_kernel = cp.RawKernel(cost_source, "cost_calculator_kernel")
   ```
   - Loads: `two_opt_batch.cu`, `cost_calculator.cu`
   - Change needed: Add compilation options for CUB

3. **Diagnostic Scripts** (testing only, low priority)
   - `diagnostic_single_2opt.py`
   - `debug_reduction.py`
   - `test_reduction_logic.py`

### ISO-Algorithmic Validation Context

**Research Goal**: Chapter 4 validates 4 ISO-algorithmic GA variants:

1. **GeneticAlgorithmCPU**: Pure NumPy baseline
2. **GeneticAlgorithmHybridNaive**: GPU 2-opt, single kernel calls
3. **GeneticAlgorithmHybridOptimized**: GPU 2-opt batch + cost calculator
4. **GeneticAlgorithmFullGPU**: Entire GA on GPU (Fujimoto 2011)

**"ISO-Algorithmic"** = Same algorithm logic, different execution backends. Critical for fair CPU vs GPU comparison.

**Current Validation Status**:

- ✅ All variants implemented
- ✅ Manual 2-opt kernels debugged (0.00% error)
- ⏳ Chapter 4 benchmarks need to run (30 repetitions × 3 instances)
- ⏳ Statistical validation pending

---

## 🎯 Migration Goals

### Must Have ✅

1. CUB kernels produce **identical results** to manual kernels (0.00% error)
2. Performance **maintained or improved** (5-13x speedup vs CPU)
3. Python integration **seamless** (minimal code changes)
4. Old kernels **preserved** for reference (debug/legacy/)

### Nice to Have ⭐

1. Compile-time optimizations (CUB may generate better assembly)
2. Documentation for future kernel development
3. Benchmarks showing CUB vs manual performance

### Out of Scope ❌

1. Rewriting `ga_fujimoto.cu` (different algorithm, works fine)
2. Migrating all diagnostic scripts (low priority)
3. Performance tuning beyond CUB defaults (research focus, not optimization)

---

## 📐 Implementation Plan

### Phase 1: Create CUB Kernels ⏱️ 30 min

**Task 1.1**: Create `two_opt_single_cub.cu`

```cuda
// File: code/src/algorithms/kernels/two_opt_single_cub.cu
#include <cub/cub.cuh>

extern "C" __global__ void two_opt_kernel(
    const double* __restrict__ distances,
    const int* __restrict__ tour,
    int n,
    int* best_i,
    int* best_j,
    double* best_delta) {
    
    int tid = threadIdx.x;
    int i = blockIdx.x;
    
    if (i >= n - 2) return;
    
    // Compute delta for this i (same as manual kernel)
    int city_i = tour[i];
    int city_i1 = tour[i + 1];
    
    double min_delta = 0.0;
    int min_j = -1;
    
    for (int j = i + 2; j < n; j++) {
        int city_j = tour[j];
        int city_j1 = tour[(j + 1) % n];
        
        double old_cost = distances[city_i * n + city_i1] + 
                          distances[city_j * n + city_j1];
        double new_cost = distances[city_i * n + city_j] + 
                          distances[city_i1 * n + city_j1];
        double delta = new_cost - old_cost;
        
        if (delta < min_delta) {
            min_delta = delta;
            min_j = j;
        }
    }
    
    // CUB BlockReduce (replaces 50 lines of manual reduction!)
    typedef cub::BlockReduce<double, 256> BlockReduceT;
    __shared__ typename BlockReduceT::TempStorage temp_storage;
    
    double block_min = BlockReduceT(temp_storage).Reduce(min_delta, cub::Min());
    
    if (tid == 0 && min_delta == block_min) {
        *best_i = i;
        *best_j = min_j;
        *best_delta = min_delta;
    }
}
```

**Task 1.2**: Create `two_opt_batch_cub.cu`

- Similar structure, handle batch dimension
- Use CUB for per-tour reduction

**Task 1.3**: Test compilation

```python
# test_cub_kernel.py
import cupy as cp
import os

cuda_include = '/usr/local/cuda/include'
with open('two_opt_single_cub.cu', 'r') as f:
    code = f.read()

kernel = cp.RawKernel(
    code, 
    'two_opt_kernel',
    options=('-std=c++14', f'-I{cuda_include}')
)
print("✅ CUB kernel compiled successfully!")
```

### Phase 2: Reorganize Structure ⏱️ 15 min

**Task 2.1**: Create folder structure

```bash
cd code/src/algorithms/kernels
mkdir -p debug/legacy_manual
```

**Task 2.2**: Move old kernels

```bash
# Preserve manual kernels for reference
mv two_opt_single.cu debug/legacy_manual/two_opt_single_manual.cu
mv two_opt_batch.cu debug/legacy_manual/two_opt_batch_manual.cu

# Move debugging scripts
mv ../../../diagnostic_single_2opt.py debug/
mv ../../../debug_reduction.py debug/
mv ../../../test_reduction_logic.py debug/
```

**Task 2.3**: Move new CUB kernels to main location

```bash
mv two_opt_single_cub.cu two_opt_single.cu
mv two_opt_batch_cub.cu two_opt_batch.cu
```

**Task 2.4**: Update kernels README

```markdown
# Kernels Directory

## Production Kernels (CUB-based)
- `two_opt_single.cu`: Single-tour 2-opt with CUB BlockReduce
- `two_opt_batch.cu`: Batch 2-opt with CUB BlockReduce
- `ga_fujimoto.cu`: Full GPU GA (Fujimoto 2011, no changes)
- `cost_calculator.cu`: Tour cost calculation

## Debug / Legacy
See `debug/legacy_manual/` for original manual reduction implementations.
Preserved for educational reference after 9.5h debugging journey.
```

### Phase 3: Update Python Loaders ⏱️ 30 min

**Task 3.1**: Update `genetic_algorithm_hybrid_naive.py`

```python
# Line 48-60 (approximate)
def _load_kernel(self):
    """Load two_opt_single.cu kernel with CUB support."""
    kernel_dir = Path(__file__).parent.parent / "kernels"
    kernel_path = kernel_dir / "two_opt_single.cu"
    
    if not kernel_path.exists():
        raise FileNotFoundError(f"Kernel not found: {kernel_path}")
    
    with open(kernel_path, "r") as f:
        kernel_source = f.read()
    
    # Add CUB include path for compilation
    import os
    cuda_include = os.environ.get('CUDA_PATH', '/usr/local/cuda')
    include_path = f'{cuda_include}/include'
    
    self.two_opt_kernel = cp.RawKernel(
        kernel_source, 
        "two_opt_kernel",
        options=('-std=c++14', f'-I{include_path}')  # 🆕 CUB support
    )
    logging.info("Loaded two_opt_kernel (CUB) for naive hybrid")
```

**Task 3.2**: Update `genetic_algorithm_hybrid_optimized.py`

- Same pattern for `two_opt_batch.cu`
- `cost_calculator.cu` doesn't need changes (no reduction)

**Task 3.3**: Test imports

```bash
cd code
python -c "from src.algorithms.metaheuristics import GeneticAlgorithmHybridNaive; print('✅ HybridNaive imports')"
python -c "from src.algorithms.metaheuristics import GeneticAlgorithmHybridOptimized; print('✅ HybridOptimized imports')"
```

### Phase 4: Validate Correctness ⏱️ 20 min

**Task 4.1**: Run single 2-opt diagnostic

```bash
cd code
python diagnostic_single_2opt.py
# Expected: GPU cost matches CPU cost exactly (0.00% error)
```

**Task 4.2**: Run all variants diagnostic

```bash
python diagnostic_all_variants.py
# Expected: 
# - HybridNaive: 0.00% error ✅
# - HybridOptimized: 0.00% error ✅
```

**Task 4.3**: Quick GA run (1 generation)

```bash
python -c "
from src.algorithms.metaheuristics import GeneticAlgorithmHybridNaive
from src.loaders.database_loader import DatabaseLoader
import numpy as np

loader = DatabaseLoader()
problem = loader.get_problem('kroA100')
distances = problem.get_distance_matrix()

ga = GeneticAlgorithmHybridNaive(
    population_size=10,
    max_generations=1,
    problem=problem
)

result = ga.evolve()
print(f'✅ GA ran successfully: {result.best_cost:.2f}')
"
```

### Phase 5: Performance Benchmark ⏱️ 30 min

**Task 5.1**: Benchmark CUB vs manual (A/B test)

```bash
# First, restore manual kernel temporarily
cd code/src/algorithms/kernels
cp debug/legacy_manual/two_opt_single_manual.cu two_opt_single_manual_temp.cu

# Benchmark both
python benchmark_2opt_cub_vs_manual.py
# Expected: CUB matches or exceeds manual (5-13x vs CPU)
```

**Task 5.2**: Document results

- Create `BENCHMARK_CUB_MIGRATION.md`
- Record speedups, memory usage, compile time
- Compare assembly if curious (optional)

### Phase 6: Validation Roadmap ⏱️ 15 min

**Task 6.1**: Review Chapter 4 requirements

```bash
cd code
head -100 benchmark_chapter4_validation.py
# Check: What's already implemented?
# Check: What tests are needed?
```

**Task 6.2**: Create validation checklist

```markdown
# Chapter 4 ISO-Algorithmic Validation Checklist

## Prerequisites ✅
- [x] All 4 GA variants implemented
- [x] Manual 2-opt debugged (0.00% error)
- [ ] CUB 2-opt validated (Phase 4)
- [ ] Performance benchmarked (Phase 5)

## Chapter 4 Benchmarks
- [ ] kroA100: 30 reps × 4 algorithms = 120 runs
- [ ] lin318: 30 reps × 4 algorithms = 120 runs
- [ ] pr1002: 30 reps × 4 algorithms = 120 runs
- [ ] Total: 360 GA runs (~2-4 hours GPU time)

## Statistical Analysis
- [ ] Friedman test (non-parametric ANOVA)
- [ ] Nemenyi post-hoc (pairwise comparison)
- [ ] Effect size (Cohen's d or rank-biserial)
- [ ] Gap to optimum (solution quality)

## Deliverables
- [ ] Table: Mean cost ± std, time ± std per variant
- [ ] Graph: Solution convergence curves
- [ ] Graph: Memory transfer breakdown (H2D, D2H, D2D)
- [ ] Statistical report: p-values, effect sizes
```

**Task 6.3**: Estimate time to completion

- CUB migration: 2-3 hours
- Chapter 4 benchmarks: 2-4 hours GPU time + 2 hours analysis
- **Total to thesis validation**: 6-9 hours

---

## 🚨 Rollback Plan

If CUB migration fails (compilation errors, performance regression, incorrect results):

```bash
cd code/src/algorithms/kernels

# Restore manual kernels
cp debug/legacy_manual/two_opt_single_manual.cu two_opt_single.cu
cp debug/legacy_manual/two_opt_batch_manual.cu two_opt_batch.cu

# Revert Python changes
git checkout genetic_algorithm_hybrid_naive.py
git checkout genetic_algorithm_hybrid_optimized.py

# Test restoration
cd ../../../
python diagnostic_all_variants.py
# Should show 0.00% error with manual kernels
```

**Rollback Time**: < 5 minutes (git has history)

---

## 📊 Success Criteria

| Criterion | Target | Test Method |
|-----------|--------|-------------|
| **Correctness** | 0.00% error vs CPU | `diagnostic_single_2opt.py` |
| **Performance** | ≥ 5x speedup (HybridNaive) | `benchmark_2opt_cpu_vs_gpu.py` |
| **Performance** | ≥ 3x speedup (HybridOptimized) | `benchmark_2opt_cpu_vs_gpu.py` |
| **Maintainability** | < 200 LOC per kernel | `wc -l *.cu` |
| **Compilation** | No warnings | CuPy RawKernel output |
| **Integration** | All imports work | `python -c "import ..."` |

---

## 📚 References

- **CUB Documentation**: <https://nvlabs.github.io/cub/>
- **CuPy RawKernel Guide**: <https://docs.cupy.dev/en/stable/reference/generated/cupy.RawKernel.html>
- **Our Experience**: `documentation/technical_decisions/GPU_REDUCTION_PATTERNS_AND_LESSONS.md`
- **Fujimoto 2011**: "A Highly-Parallel TSP Solver for a GPU Computing Platform"
- **Chapter 4 Draft**: `first_draft.md` section 4.x (memory transfer optimization)

---

## ✅ Next Steps

1. **Review this plan** with user
2. **Get approval** to proceed (or defer if thesis deadline is tight)
3. **Execute Phase 1** (create CUB kernels)
4. **Validate Phase 4** (correctness before proceeding)
5. **Complete migration** if Phase 4 passes
6. **Return to research** (Chapter 4 validation)

**Decision Point**: Is 2-3 hours of infrastructure work worth it NOW, or should we complete Chapter 4 validation first and migrate later?
