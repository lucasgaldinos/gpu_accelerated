Searching the web for 'Genetic Algorithm hyperparameter tuning best practices'
Completed with input: {
  "query": "Genetic Algorithm hyperparameter tuning best practices"
}

Collecting workspace informationYou’re in a good place conceptually (V2 is much cleaner), but you’re one step away from creating a statistical/methodological mess if you just “pour everything into one DuckDB”. I’ll split this into:

1. How to integrate V2 into results.duckdb without corrupting your analysis  
2. Critique of your current analysis pipeline (results_and_stats_v3.ipynb)  
3. Critique of GA hyperparameter/tuning strategy vs your actual benchmark design  
4. Critique of repository organization and “sources of truth”

---

## 1. Integrating V2 into results.duckdb (without poisoning it)

### 1.1. Core problem: incompatible measurement protocols

V1 (checkpoints in results/benchmark_results/checkpoints_treated) and V2 (checkpoints in results_v2/checkpoints) differ on a *fundamental* axis:

- V1 CPU: fixed patience, biased timing (documented ~66% overestimation in results_and_stats_v3.ipynb)  
- V2 CPU: adaptive patience via `benchmarking_v2.algorithm_runner.adaptive_generations` / `adaptive_patience`, stop‑reason aware, `raw_generations` + labeled `raw_stop_reasons` in checkpoints.

Pooling these in a single table with no explicit “protocol” indicator violates basic experimental design principles (Montgomery [@montgomery2017design]) and algorithm-comparison guidelines (Demšar, 2006 [@demsar2006statistical]): you’d be comparing runs collected under *different measurement instruments*.

Your own notebook quantifies this: mean CPU time inflation $\approx 66\%$; since speedup is $S = T_\text{CPU}/T_\text{GPU}$, legacy speedups are inflated by the same factor. This is exactly the kind of systematic bias Field [@field2009discovering] and Montgomery warn you *not* to mix with corrected data.

### 1.2. Recommendation: keep V2 logically separate

**Best practice (and the least work):**

1. Keep results.duckdb as the **“V1+legacy” DB**.  
2. Use results.duckdb (your notebook’s `RESULTS_DB`) as the **authoritative corrected V2 DB**.  
3. For any cross-version comparison, make the “source” explicit in the query, e.g.:

```sql
-- Example: union legacy+corrected with explicit source flag
SELECT 'V1' AS source, * FROM benchmark_runs  -- in legacy DB
UNION ALL
SELECT 'V2' AS source, * FROM benchmark_runs  -- in V2 DB
```

You already follow this pattern conceptually in results_and_stats_v3.ipynb: V1 vs corrected data are analyzed *side by side*, not silently mixed.

This is completely aligned with Demšar (2006): algorithm comparison across multiple datasets must ensure identical evaluation protocols; when protocols differ, treat results as separate conditions, not interchangeable samples.

### 1.3. If you *must* reuse the main DB

If you insist on having a single physical file for convenience, you still should **separate logical populations**:

- Keep the existing `benchmark_runs` table schema (backwards compatible, as required).
- Add a *new* metadata table, e.g. `benchmark_run_sources(run_id, source, patience_scheme)` and populate it in the importer.

Minimal change in `benchmarks.result_database.import_checkpoints`:

- When importing from checkpoints, insert:
  - `source = 'V2'`
  - `patience_scheme = 'adaptive_2sqrt(n)'`
- When importing from checkpoints_treated, insert:
  - `source = 'V1'`
  - `patience_scheme = 'fixed_50'` (or whatever legacy used)

Then analysis always joins:

```sql
SELECT br.*, s.source, s.patience_scheme
FROM benchmark_runs br
LEFT JOIN benchmark_run_sources s USING (run_id);
```

That’s a small, localized change (one extra table and one extra insert) and buys you:

- Clean separation for statistics (e.g. restrict to `source='V2'` when computing final speedup curves).
- Ability to *explicitly* test “legacy vs corrected” as two treatments (recommended by @montgomery2017design and @conover1999practical).

### 1.4. How to actually import V2

Given your own instructions, the *mechanical* import is straightforward:

- Use `benchmarks.result_database.import_checkpoints` with V2:

```bash
uv run python code/benchmarks/result_database/import_checkpoints.py \
  -i results_v2/checkpoints \
  -o results/benchmark_results/results.duckdb
```

Critique: running this *blindly* right now will silently mix biased V1 and corrected V2 entries in the same `benchmark_runs` table, and **you will not be able to cleanly untangle them later** (you have no `source` column, and timestamps overlap once you re-run). That’s exactly the “no explicit version/source column” risk you documented in schema.sql / `.md`.

From a statistical-design standpoint, mixing these violates the assumption of identically measured observations in:

- Regression fits of $T_\text{CPU}(n)$ and derived predictions (your notebook’s power-law model)
- Nonparametric tests (Wilcoxon, Friedman) recommended by Demšar and Conover

So: **add some minimal form of source tagging before doing the import** (either via a new table as above, or by putting V2 into a separate DB and explicitly labeling it in queries).

---

## 2. Critique of results_and_stats_v3.ipynb and analysis strategy

Your notebook in results_and_stats_v3.ipynb is, frankly, much more statistically rigorous than most theses:

- Identifies a concrete measurement bias (fixed patience)  
- Proposes a correction ($p(n) = 2\sqrt{n}$, $T_\text{corr} = T_\text{raw} \cdot g_\text{eff}/g_\text{raw}$)  
- Validates assumptions (linearity of $T$ vs generations, variance reduction, stop-reason impact)  
- Uses LOOCV, bootstrap intervals, Wilcoxon, Cohen’s $d$ (all textbook [@montgomery2017design; @cohen1988statistical; @efron1979bootstrap])

**Criticisms (science-backed):**

1. **The correction pipeline is too “after-the-fact” for production use.**  
   - You’re reconstructing “effective” CPU times from *legacy* V1 DuckDB entries using heuristic parsing of `raw_stop_reasons` and a model-based correction. This is analogous to post-hoc batch-effect correction in experimental design (see Field [@field2009discovering]): acceptable once, but not something you want as part of the core pipeline forever.
   - Now that V2 benchmarks already encode `raw_generations` and standardized `raw_stop_reasons` at the checkpoint level and use adaptive patience inside `benchmarking_v2.algorithm_runner.run_single_algorithm`, you shouldn’t *rebuild* timing corrections from DuckDB; you should **compute the right statistics at import time** (or in `benchmarking_v2/aggregate_statistics`) and store them explicitly (e.g. `mean_time_corrected`).

2. **You are mixing two roles into a single artifact:**
   - A *scientific audit* of legacy bias (which is excellent and should be Appendix material).
   - A de-facto *production* analysis utility (all your final speedup plots go through it).
   Literature (Montgomery, Efron, Demšar) strongly recommends a clean separation between:
   - “Methods development / diagnostics” vs
   - “Final, one-click reproducible analysis”.

3. **The model-based extrapolation step is overkill for your final V2-only analysis.**  
   - For final TCC results you now have **direct V2 measurements at all relevant $n$** (or can cheaply run them via `benchmarking_v2.orchestration.run_benchmark`).  
   - Using a power-law model $T(n)=a n^b$ and bootstrap extrapolation was scientifically justified when you only had sparse legacy CPU baselines (small $n$) and GPU at larger $n$. With V2 you can *just measure* CPU+GPU up to your `cpu_size_threshold` and then switch to GPU-only (as in `benchmarking_v2.aggregate_statistics`).

**Concrete recommendation:**

- Keep results_and_stats_v3.ipynb as a **historical/audit notebook** (valuable for the thesis “Methods” chapter).  
- For V2, implement a *minimal* analysis layer in Python that:
  - Reads only V2 runs from DuckDB (tagged as above), or directly parses checkpoints via `benchmarking_v2.checkpoint_io`.
  - Computes per-(problem, algorithm) statistics (means, CIs, stop-reason proportions) using the *already corrected* `raw_generations` and early stopping semantics from V2.
  - Aggregates speedups per your stratified rules in `benchmarking_v2.aggregate_statistics`.

That’s closer to Demšar’s recommended pipeline: consistent, protocol-homogeneous measurements, then nonparametric cross-problem tests (Wilcoxon/Friedman) and effect sizes.

---

## 3. Critique of GA hyperparameter tuning vs your benchmark design

GA_HYPERPARAMETER_TUNING_AND_PERFORMANCE_BENCHMARKS.md is excellent as a literature survey (Goldberg [@goldberg1989genetic], Eiben & Smith [@eiben2015introduction], Larrañaga [@larranaga1999genetic], Lima [@lima2018hybrid], Vidal [@vidal2013hybrid], etc.), but from the *benchmarking* perspective I see three problems:

### 3.1. Risk of “hyperparameter fishing” relative to your thesis goals

- The document advocates size-dependent scaling laws (e.g. $N_\text{pop} = \max(50, 10\sqrt{n})$, $G_\text{max} = \max(1000, 20n)$, adaptive mutation, etc.).
- But your benchmark V2 architecture fixes GA parameters through JSON in algorithms.json and runs **four ISO‑algorithmic variants** under *identical* settings.

From Demšar [2006] and Eiben & Smith [@eiben2015introduction]:

- When comparing algorithms across multiple problems, **hyperparameters must be chosen *once* and then fixed**, or chosen via a nested tuning protocol that is the *same* for all algorithms.
- If you tune GA parameters more aggressively for GPU variants (e.g. larger populations enabled by faster hardware) than for CPU, you conflate “algorithmic advantage” with “harsher tuning”, violating fairness.

**Critique**: GA hyperparameter tuning document is in danger of pushing you toward per-size, per-variant tuning that’s great for “best possible GA on each instance” but *bad* for your main research question: “What is the speedup and quality impact of moving the same GA to GPU?”  

You should treat tuning as **pre-registered and shared** across all four variants.

### 3.2. Literature references are mostly VRP / giant-tour / hybrid GAs

Many of the strongest tuning examples (Prins [@prins2004simple], Vidal [@vidal2013hybrid], Lima [@lima2018hybrid]) are for:

- CVRP or VRP with time windows,
- Giant-tour representations,
- Very heavy local search (ALNS, large neighborhoods).

Your current GA benchmark is **TSP with 2-opt**, not a full VRP/ALNS hybrid. That matters because:

- These papers accept very high evaluation budgets (millions of evaluations, minutes of runtime) to reach “world class” gaps.
- For your TCC GPU vs CPU *hardware* comparison, you care more about **relative speedups under a fixed, realistic budget** (Schulz et al. [@schulz2013gpu]; Rocki & Suda [@tsp_gpu]; Fujimoto & Tsutsui [@fujimoto2011highly]).

**Critique**: You are importing hyperparameter scales from heavy VRP hybrids that might be overkill for your TSP GA; that inflates runtimes and can obscure the hardware comparison you actually want to highlight.

Eiben & Smith explicitly caution against blindly transferring “best” parameters across problem classes; they recommend problem-specific tuning *but* under a clearly stated budget constraint.

### 3.3. Interaction with early stopping / patience

Your V2 GA runs rely on early stopping (adaptive patience) implemented in `benchmarking_v2.algorithm_runner`. The tuning document focuses on $G_\text{max}$, $N_\text{pop}$, $p_c$, $p_m$, and 2‑opt iterations, but doesn’t fully account for:

- Patience as an *implicit* budget controller.
- How early stopping interacts with your stop-reason-aware correction and speedup computation.

GA theory (Eiben & Smith, Goldberg) and your own results-and-stats notebook both emphasize:

- Stopping criteria are part of the **algorithmic definition**; changing them changes the underlying process.
- Mixing different patience rules across experiments reintroduces the same kind of bias you just worked hard to remove.

**Critique**: The tuning doc should be explicitly reconciled with your current, validated early-stopping design (adaptive patience $p(n) = 2\sqrt{n}$). Right now they live in parallel worlds: one in code, one in documentation.

**Recommendation**: For TCC:

- Fix a single, literature-backed, *size-aware* configuration once (e.g. modest scaling of population with $n$, constant 2‑opt effort per individual, adaptive patience as already implemented).
- Document it succinctly in methods (with citations to @goldberg1989genetic, @eiben2015introduction, @larranaga1999genetic) and **do not retune GA per problem**. Use the detailed GA tuning doc as a “future work / extension” reference, not as the controlling spec for Chapter 4.

---

## 4. Repository organization critique

You already know this is messy; here are the main issues from a reproducibility/scientific point of view.

### 4.1. Too many “benchmark scripts” and unclear canonical path

Benchmarks and analyses are spread across:

- Legacy GA benchmark: chapter4_validation.py  
- New GA benchmark V2: run_chapter4_benchmark.py + `benchmarking_v2.orchestration`  
- Early CVRP “lego” benchmarks: comprehensive_benchmark.py, benchmark_2opt_cpu_vs_gpu.py  
- Ad-hoc integration tests: test_real_world_integration.py, test_alternative_approaches.py

From the outside, it is not obvious:

- Which scripts produce **thesis-grade** results, and
- Which are **exploratory** or legacy.

Demšar and Montgomery emphasize that for scientific reporting you need a *single, well-documented pipeline* per reported experiment. Multiple overlapping scripts invite “garden of forking paths” / selective reporting problems.

**Recommendation (minimal change):**

- In README.md and/or project_status.md, add a short “Authoritative benchmark entrypoint” section:

  - “For Chapter 4 GA speedups, use: run_chapter4_benchmark.py.”
  - “Legacy scripts comprehensive_benchmark.py, benchmark_2opt_cpu_vs_gpu.py are exploratory and **not** part of the final experimental pipeline.”

- Optionally move legacy scripts under a `code/benchmarks_legacy/` or `code/experiments/` folder to visually separate them, without deleting anything.

### 4.2. Too many “sources of truth” for benchmarks and instances

Benchmark instance selection appears in at least:

- first_draft.md Section 3.4  
- BENCHMARK_INSTANCES_30_SELECTED.md  
- extracting-problems.ipynb  
- project_status.md task descriptions  
- `benchmark.json` / `problems.json` in configs

Montgomery and Field both stress the importance of a **single experimental design spec** to avoid unconscious cherry‑picking or mismatched instance sets between reported tables and actual code.

**Recommendation:**

- Treat problems.json as the **canonical source** for which TSP problems are in the V2 GA benchmark.  
- In the docs (first_draft, BENCHMARK_INSTANCES_30_SELECTED, project_status), reference that file explicitly and avoid restating full lists in multiple places, or clearly label long tables as “copied from config as of YYYY-MM-DD”.

This matches typical software/statistics practice (single config, docs reference it) and reduces the risk of misalignment between text and actual experiments.

### 4.3. Notebooks vs library code: duplicated logic

Your analysis notebook results_and_stats_v3.ipynb re‑implements:

- Database utilities (`query_cpu_timing_data`, `query_algorithm_data`), which overlap with what should live in `benchmarks.result_database.db_operations`.
- Statistical utilities (MAE, RMSE, LOOCV, etc.), which could be shared in a small module (e.g. `code/src/benchmarking_v2/stats_utils.py`).

From a reproducibility standpoint:

- Duplicated logic in notebooks is a well-known anti-pattern (Efron & Tibshirani stress the importance of a single, tested implementation for bootstrap and model fitting [@efron1979bootstrap; @davison1997bootstrap]).
- Bugs fixed in the library will not propagate to notebooks.

**Minimal, science-aligned improvement:**

- Move your *core* statistical utilities (those not specific to a one-off experiment) into a small module under benchmarking_v2 (e.g. `stats_utils.py`), and have both the import script and notebooks import from there.
- Keep notebooks focused on *analysis scripts* and plots, not on re-implementing data access and core math.

This aligns with the “DRY + testable core + thin notebooks” pattern recommended in reproducible research guidelines.

---

### 4.4. Overall assessment

Scientifically, you’re doing a lot of things right:

- You identified a serious measurement bias and corrected it in a statistically sound way.
- You adopted adaptive patience consistent with GA literature.
- You have a modular V2 benchmark architecture (`benchmarking_v2`) that is conceptually clean.

The main risks now are **organizational and integration**:

- Accidentally mixing biased V1 and corrected V2 data in results.duckdb without labeling.
- Letting a large, exploratory notebook (results_and_stats_v3.ipynb) effectively become “the production analysis”.
- Overcomplicating GA tuning relative to your actual goal (CPU vs GPU comparison of four fixed GA variants).

If you:

1. Tag or separate V2 in DuckDB before importing,  
2. Move core correction/stats logic into small, tested modules, and  
3. Fix one GA configuration consistent with your V2 benchmark configs and literature,

you’ll have a pipeline that is both **scientifically rigorous** and **much easier to explain and maintain**.
