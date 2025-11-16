# SA Comprehensive Testing - Summary

**Date:** 2025-01-28  
**Session:** Post-Implementation Analysis  
**Comprehensive Document:** `SA_COMPREHENSIVE_ANALYSIS.md`

---

## Quick Summary

### What Changed

**Previous Claim (WRONG):**
> "SA shows 0% improvement with random strategies (expected behavior)"

**New Finding (CORRECT):**
> "Random2Opt shows **12-15% improvement** with sufficient iterations (200k for ch150)"

**Root Cause:** Only tested with 20k iterations (10x too few)

---

## Key Findings (6 Questions Answered)

### Q1: Why is GPU 111.1s but only 7s overhead?

**Answer:** Kernel launch overhead (500 μs per iteration) dominates

**Breakdown (100k iterations):**

```
Transfer overhead:     7.06s (6.4%)
Kernel launch:        ~50s   (45%) ← DOMINANT
Actual GPU work:       0.5s  (0.4%)
Distance evaluation:   25s   (22.5%)
SA logic:             20s   (18%)
Python overhead:       8s    (7.2%)
Total:                111.1s
```

**See:** ASCII sequence diagram in `SA_COMPREHENSIVE_ANALYSIS.md`

### Q2: Test 5 - CPU or GPU?

**Answer:** **CPU ONLY**

After Test 4 proved 28x GPU slowdown, no point testing GPU on multiple sizes.

### Q3: How to Parallelize SA?

**Answer:** Three levels:

1. **Level 1 (Current):** Sequential SA with random moves  
   → GPU benefit: NONE (28x slower)

2. **Level 2 (Phase 7):** Parallel neighbor search (TwoOptMove)  
   → GPU benefit: 10-50x (O(n²) work justifies overhead)

3. **Level 3 (Future):** Multiple independent chains (Multistart SA)  
   → GPU benefit: 10-100x (linear with chains)

**See:** Research citations (Ferreiro et al. 2024, Wikipedia MST) in comprehensive doc

### Q4: SA is P-Data or S-Task?

**Answer:** **BOTH**

- **Temperature schedule:** S-Task (sequential dependency)
- **Multiple runs:** P-Data (independent chains)
- **Neighbor search:** Can be P-Task (TwoOptMove)

**Iteration count scales with problem size:**

```
eil51:   100k iterations
ch150:   200k iterations
ts225:   300k-400k iterations
```

### Q5: Keep Random2Opt or dead code?

**Answer:** **KEEP** - not dead code, complementary to TwoOptMove

| Use Case | Random2Opt | TwoOptMove |
|----------|-----------|------------|
| **Small problems (n<100)** | ✅ Fast (5 μs) | ❌ Overkill |
| **High temp SA (60% acceptance)** | ✅ Good enough | ❌ Wasted work |
| **Large problems (n>200)** | ⚠️ Lower quality | ✅ Best move |
| **Low temp SA (5% acceptance)** | ⚠️ Random pick | ✅ Greedy best |

**Trade-off:** Speed (O(1)) vs Quality (O(n²) search)

### Q6: VRAM Bottleneck - Why?

**Answer:** **Working buffers**, NOT distance matrix

| Data | ch150 | ch3000 | Bottleneck? |
|------|-------|--------|-------------|
| Distance matrix | 180KB | 68.7MB | ❌ NO (cached) |
| Tour array | 604B | 12KB | ❌ NO (transferred) |
| Working buffers (naive) | 5MB | **6.86GB** | ✅ **YES!** |
| Working buffers (reused) | 5MB | 68.6MB | ❌ NO |

**Solution:** Reuse buffers in `__init__` (pattern already implemented in TwoOptGPU)

---

## Test Results

### Test 1: Strategy Comparison

| Strategy | Improvement | Winner |
|----------|-------------|--------|
| Random2Opt | **12.62%** | ✅ |
| RandomSwap | 0.00% | ❌ |
| RandomInsertion | 0.00% | ❌ |

### Test 2: Iteration Scaling (ch150)

| Iterations | Improvement | Status |
|-----------|-------------|--------|
| 50k | 4.58% | Too few |
| 100k | 8.62% | Good |
| **200k** | **14.44%** | **Optimal** ✅ |
| 400k | 11.22% | Diminishing returns |

### Test 3: GPU Overhead

- Per-iteration transfer: **70.6 μs**
- For 100k iterations: **7.06 seconds**

### Test 4: CPU vs GPU

- CPU: 3.9s ✅
- GPU: 111.1s ❌ (28x slower)

### Test 5: Problem Size Scaling (CPU)

| Problem | Nodes | Improvement |
|---------|-------|-------------|
| eil51 | 51 | 15.07% |
| ch150 | 150 | 7.37% |
| ts225 | 225 | 5.56% |

**Insight:** Needs more iterations as problem size grows

---

## Updated Constraints (Added to M14_M15_DETAILED_TASKS.md)

1. **Iteration Counts:**
   - Small (n<100): 100k minimum
   - Medium (n=100-200): 200k minimum
   - Large (n>200): 300k-400k

2. **Problem Selection:**
   - Use ch150 (NOT berlin52) for benchmarks

3. **Acceptance Rate:**
   - Valid range: 10-60%

4. **Cooling Rate:**
   - Calculate, don't hardcode: `(min_temp/init_temp)**(1/max_iter)`

5. **GPU Testing:**
   - DO NOT test random strategies on GPU
   - GPU ONLY for TwoOptMove (Phase 7) or Multistart

6. **Overhead Measurement:**
   - Report per-iteration overhead (μs)
   - Use Test 3 pattern

7. **Convergence Logging:**
   - iterations_run, final_temp, stopped_reason, acceptance_rate

---

## References

**Full Analysis:** `documentation/progress/SA_COMPREHENSIVE_ANALYSIS.md`

**Test Script:** `test_sa_comprehensive.py` (472 lines, 5 test suites)

**Academic Sources:**

- Ferreiro et al. (2024) - arXiv:2408.00018 (Parallel SA on GPU)
- Wikipedia - Parallel MST algorithms (proves "sequential" can be parallelized)
- 4 additional GPU SA papers

**Updated Spec:** `M14_M15_DETAILED_TASKS.md` (Performance Testing Requirements section)

---

## Next Steps

**Immediate (Current Session):**

- ✅ Comprehensive analysis documented (500+ lines)
- ✅ Task constraints updated (7 requirements added)
- ⏳ Commit findings

**Phase 4 (GA Strategy Extraction):**

- Apply lessons learned (iteration scaling, GPU constraints)
- Expected GPU benefit for GA: 10-50x (population parallelism)
- Use Test 3 overhead measurement pattern

---

**Type-Driven Development requires Data-Driven Validation.**

This testing revealed critical oversights in initial claims. All future work must include empirical validation at appropriate scales.
