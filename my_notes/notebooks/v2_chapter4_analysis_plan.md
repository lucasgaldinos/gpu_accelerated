# V2 Chapter 4 Statistical Analysis Notebook Plan

**Notebook**: `results_and_stats_v2_chapter4.ipynb`  
**Purpose**: Complete statistical validation of V2 benchmark results for thesis Chapter 4  
**Data Source**: `results_v2/` (problem_statistics JSONs + checkpoints)  
**Target**: Publication-ready tables, plots, and statistical tests matching `how-to-tcc.md` §4.1–4.5

---

## Part 0: Setup & Configuration

### Cell 1: Title and Overview (Markdown)

- **Notebook title**: "Chapter 4 Results: V2 Benchmark Statistical Validation"
- **Purpose statement**:
  - Analyze 38 TSPLIB instances × 4 iso-algorithmic GA+2-opt variants
  - V2 data with adaptive patience, complete metadata, $n_{reps}$ runs per (problem, algorithm)
- **Key outputs**:
  - Per-problem paired comparisons (§4.2)
  - Stratified cross-problem tests (§4.3)
  - Speedup and scaling analysis (§4.4)
  - Quality and significance validation (§4.5)

### Cell 2: Table of Contents (Markdown)

- Auto-generated TOC with anchor links

### Cell 3: Imports (Code)

```python
# Standard library
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import warnings

# Data processing
import numpy as np
import pandas as pd

# Statistical tests
from scipy import stats
from scipy.stats import shapiro, ttest_rel, wilcoxon

# Visualization
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns

# Local utilities
from src.benchmarking_v2.stats_utils import (
    calculate_r2,
    cohens_d,
    holm_bonferroni_correction
)
from src.benchmarking_v2.statistics import StatisticalAnalyzer
```

### Cell 4: Configuration (Code)

```python
# Paths
RESULTS_DIR = Path("../../results_v2")
PROBLEM_STATS_DIR = RESULTS_DIR / "problem_statistics"
CHECKPOINTS_DIR = RESULTS_DIR / "checkpoints"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"  # Create if needed

# Create output directories
FIGURES_DIR.mkdir(exist_ok=True)

# Analysis parameters
ALPHA = 0.05  # Significance level
CPU_SIZE_THRESHOLD = 100  # Match benchmark.json
N_REPS = 26  # Actual repetitions (update after checking data)

# Plotting style
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("colorblind")
sns.set_context("notebook", font_scale=1.2)

print("✓ Configuration loaded")
print(f"  Problem statistics: {PROBLEM_STATS_DIR}")
print(f"  Checkpoints: {CHECKPOINTS_DIR}")
print(f"  Output tables: {TABLES_DIR}")
print(f"  Output figures: {FIGURES_DIR}")
```

### Cell 5: Utility Functions (Code)

```python
def load_problem_stats(problem_name: str) -> Dict[str, Any]:
    """Load problem_statistics JSON for a single problem."""
    filepath = PROBLEM_STATS_DIR / f"{problem_name}_stats.json"
    with open(filepath) as f:
        return json.load(f)

def load_all_problem_stats() -> Dict[str, Dict[str, Any]]:
    """Load all problem statistics JSONs."""
    stats = {}
    for filepath in sorted(PROBLEM_STATS_DIR.glob("*_stats.json")):
        problem_name = filepath.stem.replace("_stats", "")
        stats[problem_name] = load_problem_stats(problem_name)
    return stats

def load_checkpoint(problem_name: str, algorithm: str) -> Dict[str, Any]:
    """Load raw checkpoint data for detailed analysis."""
    filepath = CHECKPOINTS_DIR / f"{problem_name}_{algorithm}.json"
    if not filepath.exists():
        return None
    with open(filepath) as f:
        return json.load(f)

print("✓ Utility functions defined")
```

### Cell 6: Data Loading & Validation (Code)

```python
# Load all problem statistics
all_stats = load_all_problem_stats()

print(f"✓ Loaded statistics for {len(all_stats)} problems")
print(f"\nProblems: {', '.join(sorted(all_stats.keys())[:10])}{'...' if len(all_stats) > 10 else ''}")

# Identify algorithms present
all_algorithms = set()
for problem_stats in all_stats.values():
    all_algorithms.update(problem_stats["algorithms"].keys())
all_algorithms = sorted(all_algorithms)

print(f"\nAlgorithms: {', '.join(all_algorithms)}")

# Check size distribution
sizes = [stats["problem_info"]["size"] for stats in all_stats.values()]
print(f"\nProblem sizes: min={min(sizes)}, max={max(sizes)}, median={np.median(sizes):.0f}")

# Count problems by size category
small = sum(1 for s in sizes if s < CPU_SIZE_THRESHOLD)
medium = sum(1 for s in sizes if CPU_SIZE_THRESHOLD <= s < 500)
large = sum(1 for s in sizes if s >= 500)
print(f"\nSize categories:")
print(f"  Small (n<{CPU_SIZE_THRESHOLD}): {small} problems")
print(f"  Medium ({CPU_SIZE_THRESHOLD}≤n<500): {medium} problems")
print(f"  Large (n≥500): {large} problems")
```

---

## Part 1: Per-Problem Statistical Analysis (§4.2)

### Cell 7: Section Header (Markdown)

- **Title**: "Part 1: Per-Problem Analysis"
- Explain:
  - Each of 38 problems analyzed independently
  - Normality checks (Shapiro-Wilk)
  - Paired comparisons between algorithms (t-test or Wilcoxon)
  - Effect sizes (Cohen's d)
  - Multiple comparison correction (Holm-Bonferroni)

### Cell 8: Per-Problem Analysis Loop (Code)

```python
def analyze_single_problem(problem_name: str, stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive statistical analysis for one problem.
    
    Returns:
        Dict with normality_tests, pairwise_comparisons, effect_sizes, etc.
    """
    # Extract data
    algorithms = stats["algorithms"]
    algo_names = list(algorithms.keys())
    
    # Load raw checkpoint data for detailed tests
    raw_data = {}
    for algo in algo_names:
        checkpoint = load_checkpoint(problem_name, algo)
        if checkpoint:
            raw_data[algo] = {
                "times": checkpoint["raw_times"],
                "costs": checkpoint["raw_costs"],
                "gaps": [(c - stats["problem_info"]["optimal_cost"]) / stats["problem_info"]["optimal_cost"] * 100 
                         for c in checkpoint["raw_costs"]],
            }
    
    # 1. Normality tests (Shapiro-Wilk on gaps)
    normality_tests = {}
    for algo in algo_names:
        if algo in raw_data:
            gaps = raw_data[algo]["gaps"]
            stat, p_value = shapiro(gaps)
            normality_tests[algo] = {
                "statistic": stat,
                "p_value": p_value,
                "is_normal": p_value >= ALPHA
            }
    
    # 2. Pairwise comparisons (all pairs)
    pairwise_comparisons = []
    p_values_for_correction = []
    
    for i, algo1 in enumerate(algo_names):
        for algo2 in algo_names[i+1:]:
            if algo1 in raw_data and algo2 in raw_data:
                gaps1 = raw_data[algo1]["gaps"]
                gaps2 = raw_data[algo2]["gaps"]
                
                # Choose test based on normality
                both_normal = (normality_tests.get(algo1, {}).get("is_normal", False) and 
                              normality_tests.get(algo2, {}).get("is_normal", False))
                
                if both_normal and len(gaps1) == len(gaps2):
                    # Paired t-test
                    stat, p_value = ttest_rel(gaps1, gaps2)
                    test_type = "t-test"
                else:
                    # Wilcoxon signed-rank
                    stat, p_value = wilcoxon(gaps1, gaps2)
                    test_type = "Wilcoxon"
                
                # Cohen's d
                d = cohens_d(gaps1, gaps2)
                
                pairwise_comparisons.append({
                    "algo1": algo1,
                    "algo2": algo2,
                    "test_type": test_type,
                    "statistic": stat,
                    "p_value": p_value,
                    "cohens_d": d,
                    "significant_uncorrected": p_value < ALPHA
                })
                p_values_for_correction.append(p_value)
    
    # 3. Holm-Bonferroni correction
    if p_values_for_correction:
        corrected_results = holm_bonferroni_correction(p_values_for_correction, alpha=ALPHA)
        for comparison, corrected in zip(pairwise_comparisons, corrected_results):
            comparison["significant_corrected"] = corrected["reject"]
            comparison["adjusted_alpha"] = corrected["alpha_adj"]
    
    return {
        "problem_name": problem_name,
        "problem_size": stats["problem_info"]["size"],
        "optimal_cost": stats["problem_info"]["optimal_cost"],
        "algorithms": algo_names,
        "normality_tests": normality_tests,
        "pairwise_comparisons": pairwise_comparisons,
        "n_comparisons": len(pairwise_comparisons)
    }

# Run analysis for all problems
per_problem_results = {}
for problem_name, stats in all_stats.items():
    per_problem_results[problem_name] = analyze_single_problem(problem_name, stats)

print(f"✓ Analyzed {len(per_problem_results)} problems")
```

### Cell 9: Summary Table – Normality Tests (Code)

```python
# Create summary DataFrame for normality tests
normality_summary = []
for problem, results in per_problem_results.items():
    for algo, test in results["normality_tests"].items():
        normality_summary.append({
            "Problem": problem,
            "Size": results["problem_size"],
            "Algorithm": algo,
            "W": test["statistic"],
            "p-value": test["p_value"],
            "Normal?": "✓" if test["is_normal"] else "✗"
        })

normality_df = pd.DataFrame(normality_summary)
print("Normality Test Summary (first 20 rows):")
print(normality_df.head(20).to_string(index=False))

# Count violations
n_violations = (~normality_df["Normal?"].str.contains("✓")).sum()
print(f"\n⚠️ Normality violations: {n_violations}/{len(normality_df)} ({100*n_violations/len(normality_df):.1f}%)")
```

### Cell 10: Summary Table – Pairwise Comparisons (Code)

```python
# Create summary DataFrame for significant differences
significant_diffs = []
for problem, results in per_problem_results.items():
    for comp in results["pairwise_comparisons"]:
        if comp["significant_corrected"]:
            significant_diffs.append({
                "Problem": problem,
                "Size": results["problem_size"],
                "Comparison": f"{comp['algo1']} vs {comp['algo2']}",
                "Test": comp["test_type"],
                "p-value": comp["p_value"],
                "Cohen's d": comp["cohens_d"],
                "Effect": "Large" if abs(comp["cohens_d"]) > 0.8 else 
                         ("Medium" if abs(comp["cohens_d"]) > 0.5 else "Small")
            })

if significant_diffs:
    sig_df = pd.DataFrame(significant_diffs)
    print(f"Significant Pairwise Differences (after Holm-Bonferroni correction):")
    print(f"Total: {len(sig_df)} out of {sum(len(r['pairwise_comparisons']) for r in per_problem_results.values())} comparisons")
    print(sig_df.head(20).to_string(index=False))
else:
    print("⚠️ No significant pairwise differences detected after correction")
```

### Cell 11: Visualization – Distribution of Effect Sizes (Code)

```python
# Plot Cohen's d distribution across all comparisons
all_cohens_d = []
for results in per_problem_results.values():
    for comp in results["pairwise_comparisons"]:
        all_cohens_d.append(comp["cohens_d"])

fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(all_cohens_d, bins=30, edgecolor='black', alpha=0.7)
ax.axvline(0.2, color='orange', linestyle='--', label='Small effect (|d|=0.2)')
ax.axvline(0.5, color='red', linestyle='--', label='Medium effect (|d|=0.5)')
ax.axvline(0.8, color='darkred', linestyle='--', label='Large effect (|d|=0.8)')
ax.axvline(-0.2, color='orange', linestyle='--')
ax.axvline(-0.5, color='red', linestyle='--')
ax.axvline(-0.8, color='darkred', linestyle='--')
ax.set_xlabel("Cohen's d")
ax.set_ylabel("Frequency")
ax.set_title("Distribution of Effect Sizes Across All Pairwise Comparisons")
ax.legend()
plt.tight_layout()
plt.savefig(FIGURES_DIR / "effect_sizes_distribution.png", dpi=300)
plt.show()

print(f"Mean |d|: {np.mean(np.abs(all_cohens_d)):.3f}")
print(f"Median |d|: {np.median(np.abs(all_cohens_d)):.3f}")
```

---

## Part 2: Stratified Cross-Problem Analysis (§4.3)

### Cell 12: Section Header (Markdown)

- **Title**: "Part 2: Stratified Cross-Problem Analysis"
- Explain:
  - Stratum 1: Small problems (n<100) with CPU + all GPU algorithms
  - Stratum 2: All problems (n≤1002) with GPU-only algorithms
  - Friedman test for global differences
  - Nemenyi post-hoc for pairwise rankings

### Cell 13: Load Aggregate Statistics (Code)

```python
# The aggregate statistics were already computed by orchestration.py
# and are stored in each problem_statistics JSON under "statistical_tests"

# Extract Friedman/Nemenyi results per problem (if present)
per_problem_friedman = {}
for problem, stats in all_stats.items():
    if "statistical_tests" in stats:
        per_problem_friedman[problem] = stats["statistical_tests"]

print(f"✓ Found Friedman test results for {len(per_problem_friedman)} problems")

# Example: inspect one problem
if per_problem_friedman:
    example = list(per_problem_friedman.keys())[0]
    print(f"\nExample (problem={example}):")
    print(json.dumps(per_problem_friedman[example], indent=2))
```

### Cell 14: Stratum 1 – Small Problems Analysis (Code)

```python
# Identify small problems (n < CPU_SIZE_THRESHOLD)
small_problems = [p for p, s in all_stats.items() if s["problem_info"]["size"] < CPU_SIZE_THRESHOLD]
print(f"Stratum 1: {len(small_problems)} small problems (n<{CPU_SIZE_THRESHOLD})")
print(f"  Problems: {', '.join(sorted(small_problems))}")

# Collect gap data for Friedman test
# Format: List of arrays, one per algorithm, each array has gaps for all small problems
algorithms_in_stratum1 = ["CPU", "HybridNaive", "HybridOptimized", "FullGPU"]
stratum1_data = {algo: [] for algo in algorithms_in_stratum1}

for problem in sorted(small_problems):
    stats = all_stats[problem]
    for algo in algorithms_in_stratum1:
        if algo in stats["algorithms"]:
            stratum1_data[algo].append(stats["algorithms"][algo]["mean_gap"])

# Convert to arrays
stratum1_arrays = [np.array(stratum1_data[algo]) for algo in algorithms_in_stratum1]

# Friedman test
analyzer = StatisticalAnalyzer()
friedman_stratum1 = analyzer.friedman_test(stratum1_arrays)

print(f"\nFriedman Test (Stratum 1):")
print(f"  Statistic: {friedman_stratum1['statistic']:.4f}")
print(f"  p-value: {friedman_stratum1['p_value']:.6f}")
print(f"  Significant: {friedman_stratum1['significant']}")

# Nemenyi post-hoc if significant
if friedman_stratum1["post_hoc_required"]:
    nemenyi_stratum1 = analyzer.nemenyi_posthoc(stratum1_arrays, algorithms_in_stratum1)
    print(f"\nNemenyi Post-Hoc (Stratum 1):")
    print(f"  Critical distance: {nemenyi_stratum1['critical_distance']:.4f}")
    print(f"  Mean ranks: {nemenyi_stratum1['mean_ranks']}")
    
    if nemenyi_stratum1["significant_pairs"]:
        print(f"  Significant pairs:")
        for i, j, p_val in nemenyi_stratum1["significant_pairs"]:
            print(f"    {algorithms_in_stratum1[i]} vs {algorithms_in_stratum1[j]}: p={p_val:.4f}")
```

### Cell 15: Stratum 2 – All Problems GPU-Only Analysis (Code)

```python
# All problems, GPU algorithms only
gpu_algorithms = ["HybridNaive", "HybridOptimized", "FullGPU"]
all_problem_names = sorted(all_stats.keys())

print(f"Stratum 2: {len(all_problem_names)} problems (all sizes)")
print(f"  Algorithms: {', '.join(gpu_algorithms)}")

# Collect gap data
stratum2_data = {algo: [] for algo in gpu_algorithms}
for problem in all_problem_names:
    stats = all_stats[problem]
    for algo in gpu_algorithms:
        if algo in stats["algorithms"]:
            stratum2_data[algo].append(stats["algorithms"][algo]["mean_gap"])

stratum2_arrays = [np.array(stratum2_data[algo]) for algo in gpu_algorithms]

# Friedman test
friedman_stratum2 = analyzer.friedman_test(stratum2_arrays)

print(f"\nFriedman Test (Stratum 2):")
print(f"  Statistic: {friedman_stratum2['statistic']:.4f}")
print(f"  p-value: {friedman_stratum2['p_value']:.6f}")
print(f"  Significant: {friedman_stratum2['significant']}")

# Nemenyi post-hoc
if friedman_stratum2["post_hoc_required"]:
    nemenyi_stratum2 = analyzer.nemenyi_posthoc(stratum2_arrays, gpu_algorithms)
    print(f"\nNemenyi Post-Hoc (Stratum 2):")
    print(f"  Critical distance: {nemenyi_stratum2['critical_distance']:.4f}")
    print(f"  Mean ranks: {nemenyi_stratum2['mean_ranks']}")
    
    if nemenyi_stratum2["significant_pairs"]:
        print(f"  Significant pairs:")
        for i, j, p_val in nemenyi_stratum2["significant_pairs"]:
            print(f"    {gpu_algorithms[i]} vs {gpu_algorithms[j]}: p={p_val:.4f}")
```

### Cell 16: Visualization – Critical Difference Diagrams (Code)

```python
# Create CD diagram for each stratum
def plot_cd_diagram(mean_ranks, algorithm_names, critical_distance, title, save_path):
    """Plot Nemenyi critical difference diagram."""
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Sort by rank
    sorted_indices = np.argsort(list(mean_ranks.values()))
    sorted_names = [algorithm_names[i] for i in sorted_indices]
    sorted_ranks = [list(mean_ranks.values())[i] for i in sorted_indices]
    
    # Plot ranks
    y_pos = np.arange(len(sorted_names))
    ax.barh(y_pos, sorted_ranks, align='center', alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_names)
    ax.set_xlabel('Mean Rank')
    ax.set_title(title)
    ax.axvline(critical_distance, color='red', linestyle='--', label=f'CD={critical_distance:.3f}')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()

# Stratum 1 CD diagram
if friedman_stratum1["post_hoc_required"]:
    plot_cd_diagram(
        nemenyi_stratum1["mean_ranks"],
        algorithms_in_stratum1,
        nemenyi_stratum1["critical_distance"],
        "Stratum 1: Small Problems (n<100) - Algorithm Rankings",
        FIGURES_DIR / "cd_diagram_stratum1.png"
    )

# Stratum 2 CD diagram
if friedman_stratum2["post_hoc_required"]:
    plot_cd_diagram(
        nemenyi_stratum2["mean_ranks"],
        gpu_algorithms,
        nemenyi_stratum2["critical_distance"],
        "Stratum 2: All Problems (GPU Only) - Algorithm Rankings",
        FIGURES_DIR / "cd_diagram_stratum2.png"
    )
```

---

## Part 3: Speedup and Scaling Analysis (§4.4)

### Cell 17: Section Header (Markdown)

- **Title**: "Part 3: Speedup and Scaling Analysis"
- Explain:
  - Time vs problem size for each algorithm
  - Speedup curves relative to baseline (HybridNaive)
  - Power-law or polynomial regression fits
  - Confidence intervals and extrapolation limits

### Cell 18: Collect Time and Speedup Data (Code)

```python
# Build DataFrame with problem size, algorithm, mean time, speedup
scaling_data = []

for problem, stats in all_stats.items():
    size = stats["problem_info"]["size"]
    algorithms = stats["algorithms"]
    
    # Get baseline time (HybridNaive)
    baseline_time = algorithms.get("HybridNaive", {}).get("mean_time", None)
    
    for algo, metrics in algorithms.items():
        mean_time = metrics["mean_time"]
        std_time = metrics["std_time"]
        
        # Compute speedup
        speedup = baseline_time / mean_time if baseline_time and mean_time else 1.0
        
        scaling_data.append({
            "problem": problem,
            "size": size,
            "algorithm": algo,
            "mean_time": mean_time,
            "std_time": std_time,
            "speedup": speedup
        })

scaling_df = pd.DataFrame(scaling_data)
print(f"✓ Compiled scaling data: {len(scaling_df)} rows")
print(scaling_df.head(10))
```

### Cell 19: Visualization – Time vs Size (Log-Log) (Code)

```python
fig, ax = plt.subplots(figsize=(12, 8))

for algo in all_algorithms:
    algo_data = scaling_df[scaling_df["algorithm"] == algo]
    if len(algo_data) > 0:
        ax.scatter(algo_data["size"], algo_data["mean_time"], label=algo, s=50, alpha=0.7)
        
        # Fit power-law (log-log linear regression)
        log_n = np.log(algo_data["size"])
        log_t = np.log(algo_data["mean_time"])
        coeffs = np.polyfit(log_n, log_t, 1)
        b, log_a = coeffs
        a = np.exp(log_a)
        
        # Plot fitted line
        n_range = np.linspace(algo_data["size"].min(), algo_data["size"].max(), 100)
        t_fit = a * n_range**b
        ax.plot(n_range, t_fit, linestyle='--', alpha=0.6, 
                label=f'{algo} fit: T={a:.2e}·n^{b:.2f}')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Problem Size (n)')
ax.set_ylabel('Mean Time (s)')
ax.set_title('Scaling Analysis: Time vs Problem Size (Log-Log)')
ax.legend(loc='upper left', fontsize=9)
ax.grid(True, which='both', alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "scaling_time_vs_size.png", dpi=300)
plt.show()
```

### Cell 20: Visualization – Speedup vs Size (Code)

```python
fig, ax = plt.subplots(figsize=(12, 8))

for algo in all_algorithms:
    if algo == "HybridNaive":
        continue  # Baseline, speedup=1.0
    
    algo_data = scaling_df[scaling_df["algorithm"] == algo]
    if len(algo_data) > 0:
        ax.scatter(algo_data["size"], algo_data["speedup"], label=algo, s=50, alpha=0.7)
        
        # Trend line (optional: polynomial fit)
        z = np.polyfit(algo_data["size"], algo_data["speedup"], 2)
        p = np.poly1d(z)
        n_range = np.linspace(algo_data["size"].min(), algo_data["size"].max(), 100)
        ax.plot(n_range, p(n_range), linestyle='--', alpha=0.6)

ax.axhline(1.0, color='black', linestyle=':', label='Baseline (HybridNaive)')
ax.set_xlabel('Problem Size (n)')
ax.set_ylabel('Speedup vs HybridNaive')
ax.set_title('Speedup Analysis: Relative Performance vs Problem Size')
ax.legend(loc='best')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "speedup_vs_size.png", dpi=300)
plt.show()
```

### Cell 21: Speedup Summary Table (Code)

```python
# Compute average speedup per algorithm across all problems
speedup_summary = scaling_df.groupby("algorithm").agg({
    "speedup": ["mean", "std", "min", "max"]
}).round(3)

speedup_summary.columns = ["Mean Speedup", "Std Dev", "Min", "Max"]
print("Speedup Summary (vs HybridNaive):")
print(speedup_summary.to_string())

# Export to CSV
speedup_summary.to_csv(TABLES_DIR / "speedup_summary.csv")
```

---

## Part 4: Success Rate and Conditional Metrics (§4.5)

### Cell 22: Section Header (Markdown)

- **Title**: "Part 4: Success Rate and Conditional Time-to-Optimal"
- Explain:
  - Success rate: fraction of runs that hit optimal (within 1% tolerance)
  - Conditional time: mean time for successful runs only
  - Comparison of unconditional vs conditional metrics

### Cell 23: Compute Success Rates (Code)

```python
# Load raw checkpoint data to extract stop_reasons
success_rates = []

for problem, stats in all_stats.items():
    size = stats["problem_info"]["size"]
    optimal = stats["problem_info"]["optimal_cost"]
    
    for algo in stats["algorithms"].keys():
        checkpoint = load_checkpoint(problem, algo)
        if checkpoint:
            # Count runs that achieved optimal (or near-optimal)
            raw_costs = checkpoint["raw_costs"]
            tolerance = 1.01  # 1% tolerance
            n_successful = sum(1 for c in raw_costs if c <= optimal * tolerance)
            success_rate = n_successful / len(raw_costs)
            
            # Conditional time (only successful runs)
            raw_times = checkpoint["raw_times"]
            successful_times = [t for c, t in zip(raw_costs, raw_times) if c <= optimal * tolerance]
            conditional_time = np.mean(successful_times) if successful_times else np.nan
            
            success_rates.append({
                "problem": problem,
                "size": size,
                "algorithm": algo,
                "success_rate": success_rate,
                "n_successful": n_successful,
                "n_total": len(raw_costs),
                "conditional_time": conditional_time,
                "unconditional_time": stats["algorithms"][algo]["mean_time"]
            })

success_df = pd.DataFrame(success_rates)
print(f"✓ Computed success rates for {len(success_df)} (problem, algorithm) pairs")
print(success_df.head(15))
```

### Cell 24: Visualization – Success Rate Heatmap (Code)

```python
# Pivot to create heatmap
success_pivot = success_df.pivot(index="problem", columns="algorithm", values="success_rate")
success_pivot = success_pivot.sort_index()

fig, ax = plt.subplots(figsize=(10, 14))
sns.heatmap(success_pivot, annot=True, fmt=".2f", cmap="RdYlGn", vmin=0, vmax=1, 
            cbar_kws={"label": "Success Rate"}, ax=ax)
ax.set_title("Success Rate Heatmap: Fraction of Runs Achieving ≤1% of Optimal")
ax.set_xlabel("Algorithm")
ax.set_ylabel("Problem")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "success_rate_heatmap.png", dpi=300)
plt.show()
```

### Cell 25: Conditional vs Unconditional Time Comparison (Code)

```python
# Compare unconditional vs conditional times
fig, axes = plt.subplots(1, len(all_algorithms), figsize=(16, 5), sharey=True)

for i, algo in enumerate(all_algorithms):
    algo_data = success_df[success_df["algorithm"] == algo].dropna(subset=["conditional_time"])
    
    if len(algo_data) > 0:
        axes[i].scatter(algo_data["unconditional_time"], algo_data["conditional_time"], 
                       s=50, alpha=0.7, c=algo_data["size"], cmap="viridis")
        
        # 45-degree line (unconditional == conditional)
        max_val = max(algo_data["unconditional_time"].max(), algo_data["conditional_time"].max())
        axes[i].plot([0, max_val], [0, max_val], 'r--', alpha=0.5, label='y=x')
        
        axes[i].set_xlabel("Unconditional Time (s)")
        if i == 0:
            axes[i].set_ylabel("Conditional Time (s)")
        axes[i].set_title(algo)
        axes[i].legend()
        axes[i].grid(True, alpha=0.3)

fig.suptitle("Unconditional vs Conditional Time-to-Optimal", fontsize=14)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "conditional_vs_unconditional_time.png", dpi=300)
plt.show()
```

---

## Part 5: Export and Summary

### Cell 26: Export Comprehensive Results Table (Code)

```python
# Build master results table for Chapter 4
master_table = []

for problem, stats in all_stats.items():
    size = stats["problem_info"]["size"]
    optimal = stats["problem_info"]["optimal_cost"]
    
    for algo, metrics in stats["algorithms"].items():
        # Find success rate
        success_info = success_df[
            (success_df["problem"] == problem) & (success_df["algorithm"] == algo)
        ]
        
        success_rate = success_info["success_rate"].values[0] if len(success_info) > 0 else np.nan
        
        master_table.append({
            "Problem": problem,
            "Size": size,
            "Optimal": optimal,
            "Algorithm": algo,
            "Mean Cost": metrics["mean_cost"],
            "Std Cost": metrics["std_cost"],
            "Mean Gap (%)": metrics["mean_gap"],
            "Std Gap (%)": metrics["std_gap"],
            "Mean Time (s)": metrics["mean_time"],
            "Std Time (s)": metrics["std_time"],
            "Mean Generations": metrics["mean_generations"],
            "Success Rate": success_rate
        })

master_df = pd.DataFrame(master_table)

# Save to CSV
master_csv_path = TABLES_DIR / "chapter4_master_results.csv"
master_df.to_csv(master_csv_path, index=False)
print(f"✓ Exported master results table: {master_csv_path}")

# Display sample
print(master_df.head(20).to_string(index=False))
```

### Cell 27: Summary Statistics (Markdown + Code)

```python
print("=" * 80)
print("CHAPTER 4 RESULTS SUMMARY")
print("=" * 80)
print()

print(f"Total Problems Analyzed: {len(all_stats)}")
print(f"  Small (n<{CPU_SIZE_THRESHOLD}): {len(small_problems)}")
print(f"  Medium/Large (n≥{CPU_SIZE_THRESHOLD}): {len(all_stats) - len(small_problems)}")
print()

print(f"Algorithms: {', '.join(all_algorithms)}")
print()

print("Statistical Tests Performed:")
print(f"  • Per-problem normality tests: {len(normality_df)}")
print(f"  • Per-problem pairwise comparisons: {sum(len(r['pairwise_comparisons']) for r in per_problem_results.values())}")
print(f"  • Stratified Friedman tests: 2 (Stratum 1 + Stratum 2)")
print(f"  • Nemenyi post-hoc tests: {int(friedman_stratum1['post_hoc_required']) + int(friedman_stratum2['post_hoc_required'])}")
print()

print("Key Findings:")
print(f"  • Mean speedup (HybridOptimized vs HybridNaive): {speedup_summary.loc['HybridOptimized', 'Mean Speedup']:.2f}×")
print(f"  • Mean speedup (FullGPU vs HybridNaive): {speedup_summary.loc['FullGPU', 'Mean Speedup']:.2f}×")
print(f"  • Overall success rate (all algorithms): {success_df['success_rate'].mean():.1%}")
print()

print("Output Files Generated:")
print(f"  • Master results table: {master_csv_path}")
print(f"  • Speedup summary: {TABLES_DIR / 'speedup_summary.csv'}")
print(f"  • Figures: {len(list(FIGURES_DIR.glob('*.png')))} PNG files in {FIGURES_DIR}")
print()
print("=" * 80)
```

### Cell 28: Final Notes and Recommendations (Markdown)

- **Interpretation guidelines**:
  - Normality violations: Use non-parametric tests (Wilcoxon) for those cases
  - Multiple comparisons: Holm-Bonferroni controls FWER conservatively
  - Stratified analysis: Avoids CPU/GPU coverage mismatch, maintains statistical power
- **Thesis integration**:
  - Use `master_df` for Table 1 (§4.2)
  - Use Friedman/Nemenyi results for §4.3 text
  - Use scaling plots for §4.4 figures
  - Cite success rates and conditional metrics in §4.5 discussion
- **Limitations to document**:
  - Fixed tolerance (1%) for "success" – discuss in §5
  - Power-law fits assume smoothness; individual instances may vary
  - Extrapolation beyond measured sizes not recommended

---

## End of Notebook Plan

**Next Steps**:

1. Implement this notebook structure as `results_and_stats_v2_chapter4.ipynb`
2. Run all cells sequentially, fixing any data loading issues
3. Validate outputs against expected sample sizes and statistical assumptions
4. Generate final tables and figures for thesis Chapter 4
5. Document any deviations or additional findings in notebook markdown cells
