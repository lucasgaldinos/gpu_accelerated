# Answer 1

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

# User assessment

#actor-critic-thinking You may run multiple #runSubagent to investigate

1. #file:critics.md:26-27 the notebook is currentlng. There's also a new correction, showing what I did wrong and what should really be done.
2. #file:critics.md:28-45 we shall implement this. But currently, the db only has v1 the hype, after we adjust data and extrapolate the cpu findings, can't we update this data?
3. #file:critics.md:47-62 read the full #file:results_and_stats_v3.json to properly understand them. But I agree with the approach. The current v2 results are much more consistent. #runSubagent in #file:checkpoints and #file:checkpoints_treated . But we can only affirm it after the notebook is ran.
4. #file:critics.md:76-97 Yes, though I still have the results in separate `json` files and may recreate them.
5. #file:critics.md:98-124
   - the proposed correction is empirically based, not really academic. BUT could be used in the TCC at #sym:### 3.7 Ameaças à validade e evolução metodológica step creation
   - #file:critics.md:106-106 yes, but this is just for cpu/gpu adjustment. Also, the main statistics I should use to compare should be better described in #sym:### 3.5 Metodologia estatística with as shown in #file:statistical_tests_comprehensive_guide.md
   - #file:critics.md:110-112 totally agreed. But I don't have time for more runs. This seems a better solution, since it's ready.
   - #file:critics.md:114-120 also agree that the proper detailed explanation should be shown in an appendix, but contextualized in the final document
   - #file:critics.md:121-123 kinda disagree. With the v2, only 16 runs will be used (which will be the case IF the analysis from #file:results_and_stats_v3.ipynb returns false for extrapolation and adjustments). If I have both v1 and v2 I'll have 46 runs to compare, since most of my runs were done in `v1`. Remember, this is not production, it's an academical document.
6. #file:critics.md:137-154 I do agree as well. Though this is not a hyperparams comparison, but cost and speedup comparison between different algorithms. IF my findings, after #file:results_and_stats_v3.ipynb is properly working and running, it may not be that risk, or am I tripping? After all, the statistics being applied join knowledge from different sources. If adjustment and extrapolation based on my hypothesis work, would this be that big of a problem?
   - Additionaly, as your subagent may analyze (please confirm), for small problems $2\sqrt{n}$ seems a good approximation for the "corrected" number of gens.
7. #file:critics.md:155-170 Also, kinda agree only.
   - My focus isn't on hyperparams. These were set based on literature from for example #file:refs.bib:547-547 , which focus purely on GA. The fact that it recommends $2n\sqrt{n}$ as generation number is overkill at my case, since the 2-opt passes make the algorithm slower BUT reduces drastically the number of references until convergence
8. #file:critics.md:172-192 already talked about it. I want to use all runs available, since I don't have much time. If I need to rerun, given my hardware, that'll be more $1\frac{1}{2}$ days. It's faster to debug and adjust.
   - My idea is making a disclaimer about the runs at the document, if the results are true. I do think v2 with it's 16 runs are kinda sufficient. I may also keep running and adding more data. BUT an appendix with this proper statistical methods applied would be a cool extra.
9. #file:critics.md:193-260 Totally agree. I would like a cleanup, keeping only the proper logic. Currently, the mess is too big. I also won't be using the v1 anymore. But I needed it before. All results now will come from v2 and the v1 results are already in a separate folder. I'll add them to a legacy folder. But there's still clutter everywhere, like unused or irrelevant markdown files. Outdated Readmes, outdated docs. I cannot even know anymore what is and what isn't important.
   - first_draft is not really a source of truthe anymore. That is the second_draft. But I needed it to create second_draft. Also, it had some parts that could be reused. But I agree with you. The others are just old files that should be removed (not even moved or archived).
   - #file:problems.json is already the canonical version.
   - #file:critics.md:241-259 I totally agree with you on this. I could modularize it. The notebook was kinda experimental. As I said, it currently do not run properly.

Please, deeply critique and assess my concerns at first.

At the end, create a detailed plan, with clear actionable steps, following a semi 5wh model (why change, what to change, how to change, when to change, where to change, which files to change/remove/move/keep) for us to properly proceed.

# Answer 2

## A. Deep critique of your points

### 1. Notebook status and “new correction” (critics.md:26–27)

Your current results_and_stats_v3.ipynb is:

- Statistically solid as an **audit** of V1 bias (fixed patience).
- Too heavy and “after‑the‑fact” to be the **production** engine for Chapter 4.

The “new correction” in critics.md is not saying the method is wrong; it is saying:

- This style of correction belongs in:
  - Methods / “Ameaças à validade” (e.g. §3.7 in documents_tcc/how-to-tcc.md),
  - Possibly an appendix,
- But your *final* GA CPU vs GPU results should lean on **V2’s built‑in adaptive patience** (`benchmarking_v2.algorithm_runner`) and on `benchmarking_v2.problem_statistics` + `benchmarking_v2.aggregate_statistics`.

So: keep the notebook, but demote it to “auditoria histórica”, not the canonical speedup pipeline.

### 2. “Only V1 in DB; after extrapolation, can I update the data?” (critics.md:28–45)

You *can* update the DB with corrected/extrapolated values, but:

- You **must not overwrite raw V1** in place as if it were measured data.
- Two acceptable, academically defensible options:

  1. **Separate DBs**  
     - Legacy: results.duckdb (V1 raw).  
     - New: e.g. results_v2/results.duckdb containing:
       - Measured V2 runs (from `results_v2/checkpoints`),
       - Optional *corrected* V1 entries, flagged with `source='V1_corrected'` and `measurement='model'`.
  2. **Single DB + metadata table** as sketched in `critics.md`:
     - Add e.g. `benchmark_run_sources(run_id, source, patience_scheme, measurement_type)` and populate it in import_checkpoints.py or in a one‑off post‑processing script.

      Then your analysis can explicitly filter:

      - Measured V2 only:
        ```sql
        SELECT * FROM benchmark_runs br
        JOIN benchmark_run_sources s USING (run_id)
        WHERE s.source = 'V2' AND s.measurement_type = 'measured';
        ```
      - Or “V1 corrected” where appropriate.

From a design‑of‑experiments perspective (Montgomery, Demšar), this is the key: **protocol is part of the data**. Updating the DB is fine if you keep provenance.

Given your current time constraints and that V2 will be the canonical Chapter 4 pipeline, I’d recommend:

- Do **not** retrofit V1‑corrected into the V1 DB for core results.
- If you put corrected/extrapolated values into any DB, use them only in:
  - CPU scaling/extrapolation sections,
  - “Ameaças à validade” narrative,
  - Not in the core GA algorithm comparison tables.

### 3. “We can only affirm consistency after the notebook is run” (critics.md:47–62)

You’re right: the **only** way to claim “V2 and corrected V1 are consistent” is:

- Run `results_and_stats_v3.ipynb` successfully,
- Compare:

  - V1‑corrected CPU times vs V2 CPU times on overlapping problems (eil51, berlin52, kroA100…),
  - Check that discrepancies are within, say, a few percent and structurally similar (not systematically higher/lower).

If they line up:

- You can **safely say**: “V2’s adaptive patience reproduces the corrected V1 behavior.”
- Then, V1 becomes “training ground” for your methodological story; V2 becomes your **evidence** for GA results.

But even if you *don’t* finish full extrapolation:

- For GA/TSP, V2 alone (16–20 CPU‑eligible problems × 30 reps) is statistically sufficient.  
  Demšar’s guidance for multi‑problem comparisons is satisfied with 10–20 problems.

So: yes, it’s good to run the notebook once more for validation, but **you do not need V1 to rescue statistical power**. V2 alone is adequate for Chapter 4.

### 4. “Results in separate JSON files; can recreate them” (critics.md:76–97)

Your own categorization is already correct:

1. **Checkpoints** under checkpoints: canonical, not trivially reproducible; keep.
2. **Per‑problem stats / tables** under problem_statistics and tables: derived, reproducible caches.
3. **Notebook‑level JSONs** like results_and_stats_v3.json: archival, not source of truth.

This aligns with good practice (Efron & Tibshirani):

- One implementation of core math (in library code),
- Notebooks and ad‑hoc JSONs as **views** over that.

So your instinct is correct: keep the raw V2 JSONs and configs; everything else is regenerable.

### 5. Empirical nature of correction; use in §3.7 + §3.5 (critics.md:98–124)

> “the proposed correction is empirically based, not really academic”

It *is* academic enough, provided you:

- Are explicit: this is an **empirically validated heuristic correction**, not a theorem.
- Show the validation steps (which you already do in `results_and_stats_v3`):

  - Linearity of $T$ vs generations ($R^2 > 0.95$),
  - Variance reduction / bimodal → unimodal,
  - Wilcoxon + Cohen’s $d$ quantifying impact.

This fits perfectly under:

- §3.7 “Ameaças à validade e evolução metodológica” in how-to-tcc.md,
- With precise cross‑references to the formal statistical machinery summarized in:

  - §3.5 “Metodologia estatística” in how-to-tcc.md,
  - statistical_tests_comprehensive_guide.md.

On your sub‑points:

- Using the correction **only** for CPU/GPU adjustment is fine, as long as you:
  - Separate “legacy GA results” vs “final GA V2 results”.
  - Clearly mark where extrapolation enters (and where it doesn’t).
- You are right that for the core GA comparison you want to lean on the tests in §3.5 (Shapiro–Wilk, paired t/Wilcoxon, Friedman/Nemenyi, Holm–Bonferroni, Cohen’s $d$).

Regarding your disagreement on limiting to V2 (16 runs) vs pooling V1+V2 (46 runs):

- Pooling V1+V2 **after correction** is acceptable **for modeling CPU scaling** (Section on extrapolation), if you:
  - Treat “protocol” as an explicit factor in the modeling narrative,
  - Show that corrected V1 and V2 do not differ systematically.
- For **algorithm comparison tables** (Chapter 4 GA results), using *only V2* is cleaner and sufficient.  
  Extra V1‑based runs buy you little there and complicate the story.

So: use the extra V1 runs as modeling evidence and methodological narrative, not as extra “replicates” in the core GA comparison.

### 6–7. Hyperparameters, $2\sqrt{n}$, and risk of hyperparameter fishing (critics.md:137–170)

Your actual setup:

- GA parameters are **fixed across the four isoalgorítmic variants**, via algorithms.json.
- Patience / stopping is handled uniformly in `benchmarking_v2.algorithm_runner.adaptive_generations` and the implicit `adaptive_patience(n) = 2\sqrt{n}` logic.
- You’re not tuning per instance, per variant, or per size in the benchmark runs; tuning docs are background.

Under Demšar and Eiben & Smith:

- That’s acceptable: you **chose a single configuration**, motivated by literature (Goldberg, GA‑only papers in your documentation/refs.bib), and you keep it fixed for all comparisons.
- Hyperparameter‑fishing risk arises if you:
  - Retune differently for CPU vs GPU variants, or
  - Tune per instance and then compare across algorithms.

You’re not doing that.

About $2\sqrt{n}$:

- Your notebook’s corrected analysis empirically supports it as a reasonable patience scale for small/mid TSP instances.
- GA literature doesn’t give $p(n)=2\sqrt{n}$ directly, but similar “sublinear patience / neighborhood” heuristics exist; citing it as *empirically chosen and validated in Section X* is fine.

About the paper recommending $2n\sqrt{n}$ generations:

- You’re right that for **memetic GA + 2‑opt**, such a huge generation count is practically overkill (each generation is more expensive).
- It’s academically fine to say:
  - “We adopt a budget smaller than $2n\sqrt{n}$ because each generation includes intensive 2‑opt passes, which accelerates convergence per generation; this matches our empirical convergence plots.”

So on 6–7: your concern is mostly answered by being explicit:

- Hyperparameters are chosen once (via `algorithms.json`) and fixed for all 4 variants.
- Patience is adaptive but uniform across variants.
- Tuning doc is “background + future work”, not live optimization during Chapter 4.

### 8. Use all runs vs rerunning; disclaimers (critics.md:172–192)

Here your constraints are strong:

- Re‑running everything costs $\approx 1.5$ days.
- You already have a rich V1 history and a clean V2 benchmark.

Given that:

- For **GA Chapter 4 results**, V2 alone is statistically adequate:
  - 38 problems in problems.json,
  - $\approx 30$ repetitions per (problem, algorithm),
  - CPU on $\leq$ threshold problems only, with stratified analysis in `benchmarking_v2.aggregate_statistics.perform_cross_problem_analysis_stratified`.
- For **legacy GA and CPU scaling**, using all V1 runs (after correction) is justified with a strong disclaimer.

Your idea:

- “Make a disclaimer about the runs, if the results are true. Use V2 as main; V1+correction as appendix/extra.”

is exactly what Montgomery, Demšar, and Field would recommend under time/resource constraints.

So:

- Don’t rerun just to be “pure”;
- Be transparent about:

  - Which analyses use V1 (clearly flagged),
  - Which use V2 only (core GA results),
  - Where extrapolation enters and where it doesn’t.

### 9. Cleanup, canonical configs, and duplicated logic (critics.md:193–260)

You’re already thinking along the right lines:

- V1 code: keep but move to “legacy” area:
  - E.g. chapter4_validation.py remains,
  - But move old scripts / one‑off benchmarks into `code/benchmarks_legacy/` or `code/experiments/`.
- `first_draft.md`: no longer source of truth; keep only if there are reusable paragraphs, otherwise delete or move to `documents_tcc/archive/`.
- problems.json is already canonical; good. Other instance lists should explicitly say “copied from problems.json as of YYYY‑MM‑DD”.

On notebooks vs library code:

- `results_and_stats_v3` defines:

  - Statistical utilities like `calculate_r2`, `mean_absolute_error`, `loocv_regression`,
  - Domain‑specific corrections (`adaptive_patience`, `parse_stop_reason_and_calculate_effective_gen`),
  - Database utilities `query_cpu_timing_data`, `query_algorithm_data`, etc.

- This duplicates logic that belongs in:

  - db_operations.py for DB access, or
  - A small `stats_utils.py` under `code/src/benchmarking_v2` for generic stats.

Efron & Tibshirani’s point (and your own critics.md) stands: **one canonical implementation** of these utilities is safer and more maintainable.

You don’t need to fix the entire repository to get TCC done, but:

- Extracting the shared stats utilities into `benchmarking_v2.stats_utils` (or similar),
- Refactoring `results_and_stats_v3` to import them,

is a high‑impact, low‑risk improvement.

---

## B. Action plan (5W+H: why/what/how/when/where/which)

### 1. Data & Database Strategy

#### Why

- Avoid protocol mixing (V1 vs V2) in core GA results and statistical tests.
- Preserve raw data while allowing corrected/extrapolated CPU views for the thesis narrative without overwriting history.

#### What

- Declare **V2** as the canonical dataset for **GA Chapter 4 results**.
- Treat **V1** como dado **histórico / metodológico**, usado apenas para:
  - análises de GA e outros experimentos legados,
  - diagnóstico de viés de tempo de CPU e extrapolação (Apêndice / §3.7),
  - modelo opcional de escalonamento de CPU, **apenas se** as validações de §3.7 mostrarem que V1 corrigido e V2 concordam suficientemente bem,
  - e, de forma bem delimitada, como fonte de amostras "somente qualidade" em problemas pequenos: execuções de V1 em que o GA atingiu exatamente o ótimo conhecido podem ser reaproveitadas apenas para estatísticas de qualidade de solução (gap final, probabilidade de atingir o ótimo), nunca para métricas de tempo, gerações ou speedup.
- Keep **V1 and V2 physically separated at the DB level**.

#### How

1. **Keep DBs logically separate**:

   - Leave `results/benchmark_results/results.duckdb/results.duckdb` as the **V1 legacy DB**.
   - Create a **separate DB for V2**, e.g. `results_v2/results_v2.duckdb`, using:

     ```bash
     uv run python code/benchmarks/result_database/import_checkpoints.py \
       -i results_v2/checkpoints \
       -o results_v2/results_v2.duckdb
     ```

   - Do **not** import V2 into the V1 DB unless/until there is a clear, source-tagging scheme.

2. **If you decide to persist corrected/extrapolated V1 values** (optional, for §3.7 / Appendix only):

   - Add a **new table** (not new columns) such as:

     - `corrected_cpu_timing(problem_name, problem_size, source, t_raw, t_corrected, model_used, is_extrapolated)`.

   - Populate it from `results_and_stats_v3.ipynb`.
   - Never overwrite the original `benchmark_runs` rows; keep all raw V1 imports intact.

#### When

- **Before** writing Chapter 4 analysis code that queries any DB.
- After `results_and_stats_v3.ipynb` has run end-to-end at least once and you have decided whether the correction is strong enough to justify storing a corrected table.

#### Where / Which files

- DB operations: `code/benchmarks/result_database/db_operations.py`
- Import script: `code/benchmarks/result_database/import_checkpoints.py`
- Notebook corrections: `my_notes/notebooks/results_and_stats_v3.ipynb` (and its `.json` export)

---

### 2. Core Analysis Pipeline for Chapter 4 (GA, V2 only)

#### Why

- Provide a clean, reproducible pipeline that matches §3.5 in how-to-tcc.md and the statistical guide.
- Ensure Chapter 4 comparisons are based purely on **V2** data.
- Focus GPU analysis on **observed runtimes and speedups**, not speculative asymptotic models.

#### What

- Use the **Benchmark V2 architecture** como fonte principal para:
  - estatísticas por instância de GA (custos, tempos, gerações, motivos de parada) e
  - comparações de speedup entre algoritmos.
- Para métricas de **tempo, gerações e speedup**, utilizar **exclusivamente dados de V2**.
- Para métricas de **qualidade de solução** em problemas pequenos (por exemplo, distribuição de gaps e probabilidade de atingir o ótimo), permitir um modo opcional em que execuções de V1 que atingiram exatamente o ótimo sejam agregadas às repetições de V2 como amostras adicionais "somente qualidade", claramente etiquetadas na análise e sem alterar o conjunto de dados usado para estatísticas de tempo.
- For CPU:
  - Use results only on problems with `n <= cpu_size_threshold`.
- For GPU:
  - Report per-instance runtimes and speedups vs CPU when available.
  - Use nonparametric, rank-based tests across problems (Demšar-style) on per-problem summaries (e.g. medians).

#### How

1. Run benchmarks with:

   ```bash
   uv run python code/benchmarks_v2/run_chapter4_benchmark.py
   ```
   (respecting `cpu_size_threshold` and algorithm list in `benchmark.json` and `algorithms.json`).

2. Per‑problem analysis:

   - Use `src.benchmarking_v2.problem_statistics.perform_statistical_analysis` for each problem, obtaining:

- Shapiro–Wilk diagnostics when needed,
- Friedman, Nemenyi, pairwise tests, Holm–Bonferroni, effect sizes, speedups.

3. Cross‑problem analysis:

   - Use `src.benchmarking_v2.aggregate_statistics.perform_cross_problem_analysis_stratified` with the problem configs from problems.json.

4. Reporting:

   - Generate LaTeX/Markdown tables via `src.benchmarking_v2.report_generator` into tables.

#### When

- As soon as you are satisfied with GA configs in algorithms.json and `benchmark.json`.
- Before heavy thesis writing so you can “freeze” the tables.

#### Where / Which files

- Entrypoint: `code/benchmarks_v2/run_chapter4_benchmark.py`
- Orchestration: `code/src/benchmarking_v2/orchestration.py`
- Stats: `code/src/benchmarking_v2/problem_statistics.py`, `code/src/benchmarking_v2/aggregate_statistics.py`
- Outputs: `results_v2/checkpoints`, `results_v2/problem_statistics`, `results_v2/tables`

---

### 3. Legacy Correction Notebook: role and refactor

#### Why

- You need `results_and_stats_v3` to:
  - Document the 66% CPU bias,
  - Justify adaptive patience $p(n) = 2\sqrt{n}$,
  - Provide extrapolation methodology for discussion.
- But you should not let it drive final GA tables.

#### What

- Treat results_and_stats_v3.ipynb as:
  - **Appendix / Methods chapter artifact**, not “production analysis”.
- Refactor its utility functions into a shared module.

#### How

1. Create `stats_utils` under V2:

   - New module: `code/src/benchmarking_v2/stats_utils.py` containing:

     - `calculate_r2`, `adjusted_r2`, `calculate_aic_bic`,
     - `mean_absolute_error`, `root_mean_squared_error`, `mean_absolute_percentage_error`,
     - `loocv_regression`,
     - Possibly `adaptive_patience`, `parse_stop_reason_and_calculate_effective_gen` if you want to reuse those.

2. Update the notebook to import from this module instead of defining functions inline:

   ```python
   from src.benchmarking_v2.stats_utils import (
       calculate_r2,
       adjusted_r2,
       calculate_aic_bic,
       mean_absolute_error,
       root_mean_squared_error,
       mean_absolute_percentage_error,
       loocv_regression,
       adaptive_patience,
       parse_stop_reason_and_calculate_effective_gen,
   )
   ```

3. Leave the rest of the notebook as-is, except:

- Ensure `RESULTS_DB` points to the **V1 legacy DB** for GA / CPU bias / extrapolation. Do **not** use this notebook as the primary engine for Chapter 4 GA comparisons.

#### When

- After V2 benchmark is running and before you rely on `results_and_stats_v3` for any plots or numbers.
- This is a 1–2 evening task and yields big maintainability gains.

#### Where / Which files

- New module: `code/src/benchmarking_v2/stats_utils.py`
- Notebook: `my_notes/notebooks/results_and_stats_v3.ipynb`

---

### 4. Hyperparameters & Methodology in TCC

#### Why

- Avoid accusations of hyperparameter fishing.
- Align applied hyperparameters with literature in an explicit, honest way.

#### What

- Fix a single GA configuration across all 4 variants, as already encoded in:
  - algorithms.json,
  - `benchmark.json` (population, max_generations, 2‑opt iterations, etc.).
- Document this in §3.4 and §3.2.4 of how-to-tcc.md, tying back to GA literature (e.g. @goldberg1989genetic and your GA‑only refs).
- Include in that configuration the stopping rules used in V2:
  - Maximum generations as a function of problem size, e.g. $G_{\max}(n) = 2 n \sqrt{n}$,
  - Early-stopping patience $p(n) = 2\sqrt{n}$,
  chosen empirically and applied identically to all GA variants.

#### How

1. In §3.4 “Parâmetros experimentais”, explicitly link each chosen value to:

   - A range recommended in the literature (e.g. population 100–500),
   - Your constraints (GPU memory, per‑generation cost due to 2‑opt),
   - The fact that it is **identical across algorithms**.

2. In §3.7 “Ameaças à validade”, mention:

   - Potential sensitivity of results to hyperparameters,
   - But emphasize that:
     - Parameters were fixed *a priori*,
     - Analysis focuses on **relative speedups under a fixed configuration**, not on finding the globally optimal GA configuration.

#### When

- While drafting Chapters 3–4; no code changes required here if configs are stable.

#### Where / Which files

- GA config: `code/benchmarks_v2/configs/algorithms.json`, `code/benchmarks_v2/configs/benchmark.json`
- Thesis text: `documents_tcc/how-to-tcc.md`, esp. §§3.2.4, 3.4, 3.7
- GA tuning doc: `documentation/technical_decisions/GA_HYPERPARAMETER_TUNING_AND_PERFORMANCE_BENCHMARKS.md` (cited, but not controlling)

---

### 5. Repository Cleanup & Canonical Sources

#### Why

- Reduce cognitive load.
- Make it obvious what produces final GA results vs what is legacy/exploratory.
- Support reproducibility: “one true pipeline”.

#### What

- Mark and/or move legacy code and drafts.
- Clearly identify canonical configs & scripts.

#### How

1. **Benchmark scripts**

   - Keep as canonical:

     - run_chapter4_benchmark.py,
     - `src.benchmarking_v2` modules.

   - Move to `code/benchmarks_legacy/`:

     - chapter4_validation.py,
     - code/comprehensive_benchmark.py,
     - code/benchmark_2opt_cpu_vs_gpu.py,
     - Any other exploratory scripts not needed for final GA TCC.

2. **Docs**

   - Mark first_draft.md as deprecated:
     - Add a short note at top: “Superseded by second_draft on YYYY‑MM‑DD. Kept only for reference.”
     - Or move to `documents_tcc/archive/`.
   - Keep how-to-tcc.md and the second draft as canonical.
   - Remove or archive markdowns that you know are obsolete and not cited in the TCC.

3. **Problem set**

   - Treat problems.json as canonical.
   - In any doc that lists instances (e.g. BENCHMARK_INSTANCES_30_SELECTED.md), insert a line:
     - “Lista gerada a partir de problems.json em DD/MM/AAAA.”

4. **Notebook exports**

   - Move JSON exports like results_and_stats_v3.json into `my_notes/notebooks/exports/` or an `archive/` subfolder to make it clear they are not live notebooks.

#### When

- Incrementally, but before final code freeze and TCC submission.
- Start with moving legacy benchmarks (low risk), then docs.

#### Where / Which files

- Scripts to move: under `code/benchmarks`, `code/` root (older benchmark scripts)
- Docs: `documents_tcc/first_draft.md` and other outdated markdowns in `documentation/`
- Problems: `code/benchmarks_v2/configs/problems.json`

---

### 6. Statistical Methods and TCC Integration

#### Why

- Ensure Chapter 3.5 and Chapter 4 align with:
  - statistical_tests_comprehensive_guide.md,
  - What your actual code does in `benchmarking_v2.problem_statistics` and `benchmarking_v2.aggregate_statistics`.

#### What

- Make §3.5 “Metodologia estatística” the *textual mirror* of the implemented pipeline.
- Use `results_and_stats_v3` mainly to illustrate bias correction, not to define the main test suite.

#### How

1. In §3.5 (already drafted), link each step explicitly to:

   - Shapiro–Wilk → normality of cost/time per algorithm/problem.
   - Paired t/Wilcoxon → per‑problem pairwise comparisons.
   - Friedman + Nemenyi → cross‑problem multi‑algorithm comparison.
   - Holm–Bonferroni, Cohen’s $d$ → as in `src.benchmarking_v2.problem_statistics.holm_bonferroni_correction` and `src.benchmarking.statistics.StatisticalAnalyzer`.

2. Add a short subsection in §3.7 explaining:

   - The *additional* tests used in `results_and_stats_v3` (LOOCV, bootstrap intervals, Spearman covariate analysis),
   - That these are specifically for bias correction and CPU extrapolation, not for core GA comparison.

#### When

- While stabilizing Chapter 3 text, in parallel with small code cleanups.

#### Where / Which files

- Text: `documents_tcc/how-to-tcc.md` §§3.5, 3.7
- Stats code: `code/src/benchmarking_v2/problem_statistics.py`, `code/src/benchmarking_v2/aggregate_statistics.py`, `code/src/benchmarking/statistics.py`

## C. Plan: Ordered V1 correction & V2 GA benchmark pipeline

High‑level flow: first tame and modularize the V1 correction notebook, then (optionally) materialize corrected CPU data, then build the V2 DB and aggregate notebook, and only after that rely on V2 for Chapter 4 and do repo/TCC cleanup.

### Steps

1. **Refactor `results_and_stats_v3` utilities and rewire to V1 DB (first gate)**  
   - **Why**: Make the V1 correction notebook robust, DRY, and explicitly tied to the legacy DB before touching anything else.  
   - **What**:  
     - Design and create `stats_utils` in benchmarking_v2 with the statistical helpers currently defined inline in results_and_stats_v3.ipynb / results_and_stats_v3.json (e.g. `calculate_r2`, `adjusted_r2`, `calculate_aic_bic`, MAE/RMSE/MAPE, `loocv_regression`, plus any tiny helpers you reuse).  
     - Optionally group DB query helpers there too, or in a small `db_utils_v1` companion if it’s cleaner.  
     - In results_and_stats_v3.ipynb, replace duplicated function definitions by imports from `stats_utils`.  
     - Change the **DB configuration cell** in results_and_stats_v3.ipynb (currently pointing to `../results_v2/checkpoints` and `../results_v2/results.duckdb`) so that:
       - `RESULTS_DB` points to the canonical **V1 legacy DB** (results.duckdb),  
       - any `CHECKPOINT_DIR` / dataset paths point to the correct V1 locations.  
   - **How**:  
     - Use results_and_stats_v3.json as a map of exactly which functions and constants to move.  
     - Keep function names and signatures unchanged to minimize notebook edits; only swap definitions for imports.  
     - After wiring imports and DB paths, run the notebook top‑to‑bottom on V1 data and fix any path/import issues.  
   - **When**: Before touching results_and_stats_all.ipynb, before creating any V2 DB, before updating any TCC text.  
   - **Where / Which**:  
     - Notebook: results_and_stats_v3.ipynb (+ `.json` as reference).  
     - New module: `code/src/benchmarking_v2/stats_utils.py` (and optionally a `db_utils_v1.py` if needed).  
     - DB: results.duckdb as the canonical V1 connection.

2. **Validate the V1 correction model and decide on corrected CPU materialization (second gate)**  
   - **Why**: You need to know whether the V1 correction is strong enough to justify any pooled CPU scaling or storing a corrected table.  
   - **What**:  
     - With the refactored results_and_stats_v3.ipynb now running on **V1**, execute all phases (legacy vs corrected, diagnostics, regression, speedup recalculation) and collect:  
       - Fit quality (log–log power law) on corrected CPU times,  
       - Per‑problem errors, bimodality → unimodality checks,  
       - Comparisons between corrected V1 predictions and any available V2 CPU points for overlapping sizes (if you already have some).  
     - Decide explicitly:  
       - **If** the correction behaves well (agreement with V2 where available, no systematic protocol shift): plan to materialize a **`corrected_cpu_timing` table**.  
       - **If not**: keep correction purely inside the notebook as a methodological audit and do **not** write it back to the DB.  
      - **Decision taken for this project**: on the final V1 snapshot used in `results_and_stats_v3.1.ipynb`, the correction behaves well statistically (improved R², lower residual variance, stable exponent) but its **dataset-level impact is modest** (mean CPU time reduction of only ≈7% and essentially unchanged scaling exponent), and this slice of the V1 DB contains **no GPU rows**. Given that Chapter 4 will rely on **V2-only** results, we chose **not** to materialize a `corrected_cpu_timing` table and to keep the correction as a notebook-level methodological audit only.  
   - **How**:  
     - Use the validation and comparison logic already present in `results_and_stats_v3` (Wilcoxon, effect sizes, LOOCV, residual analysis) but now on the proper V1 DB.  
     - Document the decision (yes/no materialization + rationale) in both the notebook and critics.md.  
   - **When**: Immediately after Step 1, before creating any new DuckDB tables or touching V2 notebooks.  
   - **Where / Which**:  
     - Notebook: results_and_stats_v3.ipynb.  
     - DB: results.duckdb.  
     - Doc: critics.md (§3.7 part of the answer, already sketched).

3. **Implement V1 DB changes (optional corrected table) and freeze V1’s role**  
   - **Why**: Make V1’s content and role explicit before you start building on V2, so later analyses know exactly what comes from where.  
   - **What**:  
     - **If** you decided “yes” in Step 2:  
       - Create a new table (e.g. `corrected_cpu_timing`) in the **V1 DB** with fields like `(problem_name, problem_size, algorithm, source, t_raw, t_corrected, model_used, is_extrapolated, notes)`, populated from `results_and_stats_v3`.  
    - **If no**: explicitly note in critics.md and in the notebook that no corrected table was materialized e que V1 é usado apenas via notebook **e** como fonte de amostras "somente qualidade" para problemas pequenos (execuções que atingiram exatamente o ótimo conhecido).  
     - Esta é a ramificação realmente adotada aqui: **nenhuma** tabela `corrected_cpu_timing` é criada; o banco V1 permanece um registro legado inalterado, e todas as correções de tempo de V1 vivem apenas em `results_and_stats_v3.1.ipynb`. Quando for necessário reaproveitar execuções de V1 na análise V2, isso será feito lendo diretamente os checkpoints/linhas relevantes (por exemplo, via scripts em `benchmarking_v2`) e usando apenas os campos de qualidade de solução (custo final, gap, indicador de "hit_optimal"), ignorando tempos e gerações.  
     - Em qualquer dos casos, marcar claramente o DB V1 como **legado + metodológico + fonte de amostras somente qualidade** em comentários e documentação (nenhuma nova análise de tempo ou speedup do Capítulo 4 deve depender dele).  
   - **How**:  
     - Use either a small Python script or a controlled notebook cell that connects to `results.duckdb` and performs `CREATE TABLE` + `INSERT` based on DataFrames produced in `results_and_stats_v3`.  
     - Do **not** modify the original `benchmark_runs` rows; only add a new table.  
   - **When**: Only after Step 2 has given a clear “yes/no” decision; before you start querying V1 from any new place.  
   - **Where / Which**:  
     - DB: results.duckdb.  
     - Code: helper cell/script (can later be factored into a small utility under `code/benchmarks/result_database/` if you want).  
     - Docs: critics.md (B.1) and Chapter 3.7 in how-to-tcc.md.

4. **Create V2 DuckDB and refit results_and_stats_all.ipynb around shared utilities (third gate)**  
   - **Why**: You need a clean, canonical V2 DB and a single aggregated notebook wired to it (and to `stats_utils`) before freezing Chapter 4 results.  
   - **What**:  
     - Use the V2 checkpoints under checkpoints (current state: partial runs, as described in test_benchmark.log) to create a **new V2 DB** (e.g. `results_v2/results_v2.duckdb`).  
     - In results_and_stats_all.ipynb:
       - Replace the hardcoded `DB_PATH` (`my_notes/results.duckdb`) by a configuration that points to `results_v2/results_v2.duckdb` for GA results (and, if needed, optionally also connects to V1 DB in separate sections).  
       - Replace any duplicated stats/DB helpers with imports from `code/src/benchmarking_v2/stats_utils.py` (and any shared DB utilities you created).  
       - Keep this notebook focused on **V2 GA results + cross‑problem summaries**, não em correção de V1; a única exceção é um modo explícito em que, para métricas de qualidade de solução em problemas pequenos, ele possa carregar também as execuções de V1 que atingiram exatamente o ótimo como amostras adicionais "somente qualidade", expressamente etiquetadas como tal e nunca usadas em estatísticas de tempo ou speedup.  
   - **How**:  
     - Run the existing import script (`code/benchmarks/result_database/import_checkpoints.py`) with checkpoints as input, writing to a new DB path, and verify some simple queries (counts, distinct problems × algorithms).  
     - In results_and_stats_all.ipynb, systematically search for:
       - Any references to `my_notes/results.duckdb` or local DBs,  
       - Locally defined error metrics / regression logic,  
       - And swap them out for shared utilities and new DB paths.  
     - Run the notebook with the **partial V2 data** you already have to ensure it behaves correctly; later reruns will only add more rows.  
   - **When**: After Step 3 (so V1 is settled), while your V2 benchmark is still finishing (partial data is fine for debugging structure).  
   - **Where / Which**:  
     - V2 DB: `results_v2/results_v2.duckdb`.  
     - Import script: `code/benchmarks/result_database/import_checkpoints.py`.  
     - Notebook: results_and_stats_all.ipynb.  
     - Utilities: `code/src/benchmarking_v2/stats_utils.py` (and possibly a small shared `db_utils` module).

5. **Complete V2 benchmark runs and freeze Chapter 4 tables (fourth gate)**  
   - **Why**: Final GA comparisons and GPU speedups require the full planned set of V2 runs, not just partial logs.  
   - **What**:  
     - Let the benchmark in test_benchmark.log finish according to your plan (20 repetitions on CPU‑eligible problems, 16–20 on larger GPU‑only ones).  
     - Re‑import or incrementally import updated V2 checkpoints into `results_v2/results_v2.duckdb`.  
     - Use orchestration.py, `problem_statistics.py`, and `aggregate_statistics.py` to regenerate:
       - Per‑problem stats JSONs and tables,  
       - Cross‑problem stratified analyses,  
       - Final Markdown/LaTeX tables for Chapter 4.  
     - Optionally update results_and_stats_all.ipynb to reflect the final tables and to pull in any additional cross‑checks you want.  
   - **How**:  
     - Rerun the benchmark CLI as needed (run_chapter4_benchmark.py), ensuring configs in `algorithms.json`, `benchmark.json`, and `problems.json` are final.  
     - Run the orchestration/statistics pipeline end‑to‑end once data is complete.  
   - **When**: Only after Steps 1–4 are stable, and after the long benchmark run reaches the desired repetition counts (you can still test the pipeline earlier, but don’t “freeze” results until here).  
   - **Where / Which**:  
     - Benchmark runner: run_chapter4_benchmark.py.  
     - Orchestration: orchestration.py.  
     - Stats: problem_statistics.py, aggregate_statistics.py.  
     - Outputs: checkpoints, problem_statistics, tables, `results_v2/results_v2.duckdb`.

6. **Align TCC text and repository structure with the finalized pipeline (final gate)**  
   - **Why**: Ensure that what the thesis claims matches the actual code and DB structure, and that future you (or a reviewer) can reproduce the pipeline with minimal confusion.  
   - **What**:  
     - Update how-to-tcc.md and the main draft (e.g. `second_draft.md`) so that:  
       - Chapter 3.5 and 3.7 clearly describe the **V1 correction notebook** and its role,  
       - Chapter 3.6 e 3.7 explicitem o reaproveitamento limitado de execuções de V1 que atingiram exatamente o ótimo em problemas pequenos, deixando claro que elas são usadas apenas como amostras "somente qualidade" e não entram em estatísticas de tempo ou speedup,  
       - Chapter 4 describes the **V2 benchmark pipeline** and the final GA results,  
       - The $G_{\max}(n) = 2 n \sqrt{n}$ and $p(n) = 2\sqrt{n}$ rules are introduced as empirically chosen and uniformly applied.  
     - Perform repository cleanup consistent with the now‑canonical pipeline:  
       - Move old benchmark scripts into a `code/benchmarks_legacy/` area,  
       - Mark `documents_tcc/first_draft.md` and obsolete docs as archived,  
       - Explicitly point to problems.json as the canonical instance list.  
   - **How**:  
     - Use critics.md (Section B) as your checklist while editing the thesis text.  
     - For each claim in the thesis, point to the corresponding code path/notebook/DB.  
   - **When**: After Steps 1–5 are complete and you are satisfied with both V1 correction and V2 GA results.  
   - **Where / Which**:  
     - Text: how-to-tcc.md, second_draft.md.  
     - Docs: critics.md (now updated), `GA_HYPERPARAMETER_TUNING_AND_PERFORMANCE_BENCHMARKS.md`.  
     - Repo layout: benchmarks_v2, benchmarking_v2, benchmark_results, results_v2.

### Further Considerations

1. You can optionally insert a tiny **Step 0** where you quickly run the current results_and_stats_v3.ipynb as‑is to capture any failing cells before refactor; but execution‑wise, the main ordering above should be respected.  
2. For results_and_stats_all.ipynb, decide early whether it will ever touch V1 at all; if not, simplify and make it **V2-only** to avoid confusion.

# Final plan

"Planned approach for V2-only implementation:\n\n1) Scope and constraints\n- Use only V2 data (problem_statistics + checkpoints under results_v2/).\n- Do NOT touch or reference V1 anywhere in the notebook text or code.\n- Treat the TXT representation of the notebook (results_and_stats_v2_chapter4.txt) as the editing surface.\n- When changing code/markdown, I will:\n  • Refer to cells by number (1, 2, 3, ...) based on their order in the TXT file.\n  • Modify existing cells in-place when the change is small (fix imports, fix paths, clarify markdown).\n  • For larger logical additions (e.g., new analysis sections), I will propose new cells in TXT form and clearly state “insert after Cell N / before Cell N+1”.\n- You remain in control of copying updated cells from TXT into the .ipynb; I will not bulk-edit the .ipynb directly.\n\n2) Data and metrics (V2 only)\n- Inputs:\n  • Per-problem aggregates from results_v2/problem_statistics/*.json.\n  • Raw per-run arrays from results_v2/checkpoints/*.json when needed (gaps, times, generations, stop reasons).\n- Metrics:\n  • Per-problem: mean/median gap, time, success_rate, conditional time-to-optimal.\n  • Cross-problem: average ranks, Friedman/Nemenyi (Demšar).\n  • Scaling: power-law fits for mean time vs n; speedup curves using V2 baselines only.\n\n3) Notebook logical structure (kept, but V2-only and tightened)\n- Part 0: Setup & configuration (already present; clean up imports/paths if needed, V2-only language).\n- Part 1: Per-problem statistical analysis\n  • Use only V2 checkpoints for raw arrays.\n  • Shapiro–Wilk on per-problem paired differences (gap/time) between algorithms.\n  • Choose t-test vs Wilcoxon based on normality; compute Cohen’s d where appropriate.\n  • Apply Holm–Bonferroni per problem; produce per-problem summaries.\n- Part 2: Cross-problem Demšar analysis\n  • Use only V2 problem_statistics (mean_gap or similar) to build problem × algorithm matrix.\n  • Perform Friedman + Iman–Davenport, then Nemenyi and CD diagrams.\n- Part 3: Scaling analysis\n  • Use only V2 mean_total_time and problem sizes.\n  • Fit power-law models T = a·n^b per algorithm; plot log–log time vs n and speedup vs baseline.\n- Part 4: Success rate & conditional analyses\n  • Use only V2 success_rate and/or compute from V2 raw gaps.\n  • Build success rate heatmaps, conditional vs unconditional time plots.\n- Part 5: Export & summary\n  • Export master CSVs and summary tables (all V2 only).\n  • Final markdown summary referencing ONLY V2 data and methodologies.\n\n4) Implementation steps on the TXT file\n- Step A: Read the current results_and_stats_v2_chapter4.txt to map all cells and verify numbering.\n- Step B: Identify and clean any stray V1 references in markdown (e.g., legacy wording) so narrative is strictly V2.\n- Step C: Verify the Import/Config cells (Cells 1–4) compile and match V2 paths only; adjust if needed.\n- Step D: Review the existing Parts 1–5 cells in TXT and:\n  • Ensure all data loading and analysis functions point exclusively to results_v2.\n  • Tighten or slightly adjust code where necessary (one cell at a time) to align with the plan above.\n  • If we identify missing pieces (e.g., a distribution summary or a small helper), I will propose a NEW cell in TXT with a clear “insert after Cell N” instruction.\n- Step E: After each logical block (e.g., Part 1 or Part 2), I will:\n  • Ensure the code is syntactically valid in TXT form.\n  • Optionally, you can paste it into the .ipynb and run it; if there are runtime issues, we iterate cell-by-cell.\n- Step F: Once the whole TXT matches the V2-only plan, we freeze it as the canonical source for the Chapter 4 stats notebook.\n\nQuestion: Do you confirm this plan as written (yes/no)? If no, please state what you want changed.",
