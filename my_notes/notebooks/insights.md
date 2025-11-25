# Results

## ✅ Fixed - Notebook Reorganized with Proper Data Handling

### Investigation Findings

**1. Understanding "_1" and "_2" Files:**
- ✅ They are **independent experimental runs**, NOT duplicates
- Evidence: Different repetitions (15 vs 17), different mean times (46.79s vs 68.37s for eil51)
- Example: `berlin52` has run_id 1 (25.74s) and run_id 126 (20.01s)

**2. Database Structure:**
- 24 CPU benchmark rows in database (12 problems × 2 runs each)
- Each run represents independent experimental conditions
- Variability ranges from 23% (berlin52) to 89% (rat99)

**3. Previous Error:**
- My ROW_NUMBER filter arbitrarily selected first run by run_id
- This discarded 50% of data and introduced bias
- Violated scientific principles

### Changes Implemented

**1. Fixed Database Query** (`query_cpu_timing_data()`):
- ✅ Removed ROW_NUMBER filter
- ✅ Returns ALL 24 observations (was 12)
- ✅ Added detailed docstring explaining independent runs
- ✅ Added `run_id` column for traceability

**2. Added Explanatory Markdown Cells**:
- **Section 4.1**: Explains dataset structure (12 problems × 2 runs)
- **Section 5**: Reorganized regression analysis with clear subsections
- **Section 4 Summary**: Honest critical analysis of poor fit

**3. Enhanced Data Loading Cell**:
- Shows all 24 observations with run_ids
- Calculates variability statistics (run-to-run variance)
- Example output: `eil51: 68.37s vs 46.79s (±31.6% variation)`

**4. Reorganized Notebook Structure**:
```
1. Setup & Imports
2. Utility Functions
3. Database Configuration
4. Data Preparation & Exploration
   4.1 Understanding Dataset Structure (NEW)
5. Regression Analysis
   5.1 Model Specification
   5.2 Model Comparison
   5.3 Cross-Validation (LOOCV)
   5.4 Residual Diagnostics
   5.5 Visualization
Section 4 Summary & Critical Analysis (NEW)
```

**5. Added Honest Limitations Section**:
- Explains why MAPE is high (38% >> 5% threshold)
- Identifies root causes: problem-specific hardness, missing variables
- Documents high run-to-run variance
- States implications for extrapolation
- Justifies proceeding with uncertainty quantification

### Statistical Results (24 observations)

**Model Fit**:
- R² = 0.64 (moderate, slightly worse than before due to more variance)
- Quasi-linear has lower AIC/BIC (preferred)

**Cross-Validation**:
- LOOCV MAPE = 37.98% (quadratic) / 35.21% (quasi-linear)
- **Slight improvement** from 44.72% with 12 observations
- Still FAR above 5% threshold (extrapolation risky)

**Why Results Aren't Better**:
- Different problems at same n have vastly different times:
  - kroC100: 197s vs kroE100: 400s (both n=100!)
- Model assumes T = f(n only), reality is T = f(n, problem_hardness, ...)
- More data helped slightly, but fundamental issue is missing variable

### Next Steps

✅ **Phase 3 truly complete** - notebook is now properly organized and documented

Ready to proceed to Phase 4 (bootstrap prediction intervals) with realistic expectations about wide uncertainty bounds.

## User insights

Why results vary so much: bimodality due to raw_stop_reasons, number of generations until convergence, etc. Since the number of generations for patience is 50, it means the problem run for 50 generations more. 

### Questions

1. A similar number of generations has approximately the same time? If so, one could estimate again, a reasonable amount of time for the "true" generation time (time until finding the best optimal) which would be the time-50 gen times?
2. How can one problem be "harder" than other? they have the same logics. We must properly analyze this data.
3. This was already talked about at [results_and_stats](./results_and_stats_all.ipynb)
