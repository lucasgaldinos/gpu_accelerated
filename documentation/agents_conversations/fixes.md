Using "Fetch Web Page"

Fetched <https://www.statisticshowto.com/probability-and-statistics/statistical-tests/>

Searching the web for 'importance of statistical tests in research'
Completed with input: {
  "query": "importance of statistical tests in research"
}

Ran `actor-critic-thinking`
Completed with input: {
  "content": "### Plan to Address Critiques in Statistical Tests Comprehensive Guide\n\n1. **Introduction to Statistical Concepts**  \n   - **What**: Provide a foundational overview of statistical concepts, including definitions of key terms like p-values, means, medians, standard deviations, and the importance of effect sizes.  \n   - **Why**: To ensure readers understand the basic terminology and concepts before delving into specific tests.  \n   - **How**: Create a dedicated section at the beginning of the document that explains these concepts in simple terms, using examples relevant to the benchmark context.  \n   - **Who**: Targeted at readers with limited statistical background.  \n   - **When**: Before the detailed analysis of statistical tests.  \n   - **Where**: In the introduction or a separate foundational concepts section.  \n   - **How Much**: A few paragraphs for each concept, ensuring clarity and accessibility.\n\n2. **Historical Context of Statistical Tests**  \n   - **What**: Include a brief history of each statistical test, explaining its development and significance in the field of statistics.  \n   - **Why**: To provide context and show the evolution of statistical methods, enhancing understanding of their application.  \n   - **How**: Add historical notes alongside each test description.  \n   - **Who**: Readers interested in the background of statistical methods.  \n   - **When**: During the explanation of each statistical test.  \n   - **Where**: Inline with the test descriptions.  \n   - **How Much**: A few sentences summarizing the history of each test.\n\n3. **Detailed Explanation of Non-Parametric Tests**  \n   - **What**: Explain what non-parametric tests are, their advantages, and when to use them compared to parametric tests.  \n   - **Why**: To clarify the role of non-parametric tests in statistical analysis and their applicability in various scenarios.  \n   - **How**: Create a section dedicated to non-parametric tests, including definitions, examples, and comparisons with parametric tests.  \n   - **Who**: Readers needing clarity on test selection.  \n   - **When**: Before discussing specific non-parametric tests.  \n   - **Where**: In the section on statistical tests.  \n   - **How Much**: A few paragraphs summarizing key points.\n\n4. **Clarification of Normality and Its Importance**  \n   - **What**: Define normality in the context of statistical tests and explain why it matters.  \n   - **Why**: To help readers understand the assumptions behind many statistical tests and the implications of violating these assumptions.  \n   - **How**: Add a section explaining normality, its testing (e.g., Shapiro-Wilk), and its relevance to test selection.  \n   - **Who**: All readers, especially those new to statistics.  \n   - **When**: Before discussing tests that assume normality.  \n   - **Where**: In the section on assumptions of statistical tests.  \n   - **How Much**: A few paragraphs with examples.\n\n5. **Mathematical Notation and Symbols**  \n   - **What**: Standardize the use of mathematical symbols and notation throughout the document, ensuring clarity and consistency.  \n   - **Why**: To improve readability and comprehension of mathematical concepts.  \n   - **How**: Review the document for inconsistent notation and replace with standardized symbols, using KaTeX for formatting.  \n   - **Who**: All readers, particularly those with a mathematical background.  \n   - **When**: During the editing phase.  \n   - **Where**: Throughout the document.  \n   - **How Much**: As needed to ensure consistency.\n\n6. **Detailed Explanations of Statistical Tests**  \n   - **What**: Provide in-depth explanations of each statistical test, including assumptions, calculations, and interpretations.  \n   - **Why**: To ensure readers understand not just how to perform tests, but also how to interpret results meaningfully.  \n   - **How**: Expand sections on each test to include detailed explanations, examples, and visual aids where applicable.  \n   - **Who**: Readers looking to deepen their understanding of statistical analysis.  \n   - **When**: During the revision of each test section.  \n   - **Where**: In the sections dedicated to each statistical test.  \n   - **How Much**: Several paragraphs for each test, including examples and interpretations.\n\n7. **Holm-Bonferroni and Other Corrections**  \n   - **What**: Explain the Holm-Bonferroni method in detail, including its purpose, how it differs from other corrections, and when to use it.  \n   - **Why**: To clarify the importance of controlling for Type I errors in multiple comparisons.  \n   - **How**: Add a section dedicated to multiple comparison corrections, including examples and visual aids.  \n   - **Who**: Readers conducting multiple hypothesis tests.  \n   - **When**: Before discussing specific applications of the Holm-Bonferroni method.  \n   - **Where**: In the section on multiple comparisons.  \n   - **How Much**: A few paragraphs with examples.\n\n8. **Pipeline Explanation**  \n   - **What**: Describe how the statistical analysis pipeline works, including the flow from data collection to interpretation of results.  \n   - **Why**: To provide a clear understanding of the overall process and how each step relates to the others.  \n   - **How**: Create a flowchart or diagram illustrating the pipeline, accompanied by a narrative explanation.  \n   - **Who**: All readers, especially those new to statistical analysis.  \n   - **When**: At the beginning of the analysis section.  \n   - **Where**: In the introduction to the analysis section.  \n   - **How Much**: A concise overview with a visual aid.\n\n9. **Standardization of Formatting**  \n   - **What**: Ensure consistent formatting throughout the document, including headers, bullet points, and mathematical notation.  \n   - **Why**: To improve the overall readability and professionalism of the document.  \n   - **How**: Review and revise formatting according to a standardized style guide.  \n   - **Who**: All readers.  \n   - **When**: During the final editing phase.  \n   - **Where**: Throughout the document.  \n   - **How Much**: As needed to ensure consistency.\n\n### Current Document Status\n- **Base structure created**: ✅\n- **Shapiro-Wilk section researched**: ❌\n- **Paired t-test section researched**: ❌\n- **Wilcoxon section researched**: ❌\n- **Friedman section researched**: ❌\n- **Nemenyi section researched**: ❌\n- **Holm-Bonferroni section researched**: ❌\n- **Cohen's d section researched**: ❌\n- **Bootstrap section researched**: ❌\n- **References compiled**: ❌\n- **Diagrams finalized**: ❌\n- **Real benchmark examples added**: ❌",
  "nextRoundNeeded": true,
  "role": "actor",
  "thoughtNumber": 1,
  "totalThoughts": 3
}

# Actor-Critic Analysis: Statistical Guide Comprehensive Revision Plan

## Critic Assessment: Current Document Quality

### **SEVERITY: CRITICAL** - Document fails to serve educational purpose

**Major structural flaws identified:**

1. ❌ **No foundational concepts** - Jumps directly into tests without explaining p-values, hypothesis testing, distributions
2. ❌ **Inconsistent LaTeX formatting** - Mix of Unicode (≤, ×), ASCII (sqrt, sum), and proper KaTeX
3. ❌ **Missing symbol glossary** - Readers don't know what $\bar{x}$, $s_d$, $\alpha$ mean
4. ❌ **Poor mathematical exposition** - Formulas lack intuition, derivations, or visual aids
5. ❌ **No pedagogical scaffolding** - Assumes graduate-level statistics knowledge
6. ❌ **Weak historical context** - Doesn't explain WHY these tests were developed
7. ❌ **Inconsistent headers** - Uses `**bold**` instead of proper `#`, `##` `###`, `####`, `#####`, `######` hierarchy
8. ❌ **Missing decision framework** - No clear guidance on parametric vs non-parametric choice

---

## Revision Strategy: Complete Restructure Required

### Phase 1: Foundation Layer (NEW sections to add)

#### **Section 0: Statistical Foundations** (NEW)

Add BEFORE all test descriptions:

##### **0.1 Fundamental Concepts**

- **What is probability?** (Frequentist vs Bayesian)
  - Frequentist: Long-run relative frequency (our approach)
  - Bayesian: Degree of belief (alternative paradigm)
  - **Why frequentist for benchmarks?** Objective, reproducible, industry standard
  
- **What is a p-value?**
  - Formal definition: P(data | H₀ true)
  - Common misconceptions (NOT probability of hypothesis)
  - Interpretation ladder: <0.001 (very strong) → 0.05 (threshold) → >0.1 (weak)
  
- **Hypothesis testing framework**
  - Null hypothesis (H₀): Status quo assumption
  - Alternative hypothesis (H₁): What we want to prove
  - Type I error (α): False positive rate
  - Type II error (β): False negative rate
  - Power (1-β): Probability of detecting real effect

- **Descriptive statistics**
  - **Mean** ($\bar{x}$): Average, sensitive to outliers
  - **Median**: Middle value, robust to outliers
  - **Standard deviation** ($s$): Spread around mean
  - **Why mean for parametric tests?** Algebraically tractable, maximizes information use
  - **Why median for non-parametric?** Robust, works with ordinal data

- **Distributions**
  - Normal (Gaussian): Bell curve, foundation of parametric tests
  - Student's t: Normal with uncertainty in variance
  - Chi-squared: Sum of squared normals, used in rank tests
  - Why distributions matter: Determine valid inference procedures

##### **0.2 Parametric vs Non-Parametric Tests**

**Visual comparison table:**

| Aspect | Parametric | Non-Parametric |
|--------|------------|----------------|
| **Assumptions** | Normal distribution | Distribution-free |
| **Data type** | Interval/ratio | Ordinal/ranked |
| **Power** | Higher (if assumptions met) | Lower (~95% efficiency) |
| **Robustness** | Sensitive to violations | Robust to outliers |
| **Examples** | t-test, ANOVA | Wilcoxon, Friedman |
| **When to use** | Large n, verified normality | Small n, non-normal, ordinal |

**Decision flowchart** (ASCII art for now, convert to Mermaid):

```ascii
Data collected
    ↓
Check normality (Shapiro-Wilk)
    ↓
    ├─→ Normal? YES → Parametric (t-test)
    │                  ├─ Pros: More power, precise estimates
    │                  └─ Requires: n≥20, no severe outliers
    │
    └─→ Normal? NO → Non-Parametric (Wilcoxon)
                      ├─ Pros: Robust, fewer assumptions
                      └─ Cost: ~5% power loss if truly normal
```

##### **0.3 Symbol Glossary** (Table at document start)

| Symbol | Name | Meaning | Context |
|--------|------|---------|---------|
| $\alpha$ | Alpha | Significance level | Usually 0.05 (5% false positive rate) |
| $p$ | P-value | Probability of data given H₀ | Reject H₀ if $p < \alpha$ |
| $n$ | Sample size | Number of observations | Larger n → more power |
| $\bar{x}$ | X-bar | Sample mean | $\frac{1}{n}\sum_{i=1}^{n} x_i$ |
| $s$ | Sample std dev | Spread of data | $\sqrt{\frac{1}{n-1}\sum(x_i - \bar{x})^2}$ |
| $s_d$ | Std dev of differences | Paired data variability | For paired tests only |
| $t$ | T-statistic | Standardized mean difference | Follows t-distribution |
| $df$ | Degrees of freedom | Sample size minus parameters | For t-distribution shape |
| $d$ | Cohen's d | Standardized effect size | Mean difference in SD units |
| $R_i$ | Rank | Position in sorted list | 1 (smallest) to n (largest) |
| $\chi^2$ | Chi-squared | Sum of squared Z-scores | Non-parametric test statistic |
| $W$ | Shapiro-Wilk stat | Normality measure | 0 < W ≤ 1, closer to 1 = normal |

---

### Phase 2: Fix Existing Sections (All 8 tests)

#### **Universal Fixes for ALL Test Sections:**

**Template structure for each test:**

```markdown
### [Test Name]

#### Historical Context & Motivation
**Developed by**: [Name] ([Year])
**Problem it solved**: [Why was this test needed?]
**Impact**: [How it changed the field]

#### What This Test Does (Plain Language)
[One paragraph explaining in simple terms]

Example: "Shapiro-Wilk answers: 'Does my data look like a bell curve?' 
This matters because many powerful tests (t-test, ANOVA) assume normality."

#### Mathematical Formulation
[Properly formatted KaTeX with ALL symbols defined]

**Step-by-step derivation:**
1. [Intuitive step 1 with explanation]
   $$[Formula with inline commentary]$$
   Where: [Define every symbol]

2. [Intuitive step 2]
   ...

**Visual representation:**
[ASCII art or description of what formula computes]

#### When to Use (Decision Matrix)
**✅ Use when:**
- [Specific scenario 1] - **Why**: [Rationale]
- [Specific scenario 2] - **Why**: [Rationale]

**❌ Don't use when:**
- [Violation 1] - **Use instead**: [Alternative test]
- [Violation 2] - **Use instead**: [Alternative]

**Our benchmark context:**
[Specific application to GPU comparison]

#### Interpretation Guide
**P-value ladder:**
| P-value | Evidence strength | Action |
|---------|-------------------|--------|
| < 0.001 | Very strong | Confidently reject H₀ |
| 0.001-0.01 | Strong | Reject H₀ |
| 0.01-0.05 | Moderate | Reject H₀ (marginally) |
| 0.05-0.10 | Weak | Borderline (consider context) |
| > 0.10 | None | Fail to reject H₀ |

**Effect size interpretation:**
[Contextualized benchmarks]

#### Worked Example (Step-by-Step)
**Raw data:**
[Show actual numbers]

**Calculation:**
[Show intermediate steps with explanations]

**Interpretation:**
[What does result mean practically?]

#### Assumptions & Diagnostics
[How to check if test is valid]

#### Common Pitfalls
[Mistakes researchers make]

#### References
[Academic papers with DOI links]
```

---

### Phase 3: Specific Fixes by Section

#### **Shapiro-Wilk Test** (Lines 80-300)

**Critical additions needed:**

1. **What is normality?** (NEW subsection)
   ````markdown
   #### Understanding Normality
   
   **Visual definition:**
   - Bell-shaped curve (symmetric around mean)
   - 68% of data within 1 SD of mean
   - 95% within 2 SD, 99.7% within 3 SD
   
   **Why it matters:**
   - Parametric tests assume errors ~ N(0, σ²)
   - If violated: p-values unreliable, CIs incorrect
   - Central Limit Theorem: Means become normal as n→∞
   ```
   **ASCII visualization:**
   ```ascii
          *
        * * *
      * * * * *
    * * * * * * *
   *-----------*-----------*
    μ-σ    μ    μ+σ
    (68% of data here)
   ```
   
   **Q-Q plot interpretation:**
   - Points on diagonal line → normal
   - S-curve → skewed distribution
   - Heavy tails → outliers present
   ````

2. **Fix coefficient calculation** (Lines 120-139)
   ```markdown
   **Coefficient Calculation** (Intuitive Explanation):
   
   The $a_i$ coefficients weight each order statistic based on how much information 
   it provides about normality. Extreme values (smallest/largest) get highest weights.
   
   $$\mathbf{a} = (a_1, \ldots, a_n) = \frac{\mathbf{m}^T \mathbf{V}^{-1}}{C}$$
   
   **Symbol definitions:**
   - $\mathbf{m}$: Expected values if data were truly normal
     - Computed from standard normal order statistics
     - Example: For n=3, m ≈ [-0.85, 0, 0.85]
   
   - $\mathbf{V}$: Covariance matrix of order statistics
     - Captures correlation between ranks
     - V[i,j] = Cov(X_{(i)}, X_{(j)}) under normality
   
   - $C = \sqrt{\mathbf{m}^T\mathbf{V}^{-1}\mathbf{m}}$: Normalization constant
     - Ensures $\sum a_i^2 = 1$ (weights sum to 1)
   
   **Intuition:** If data deviates from expected normal order statistics, 
   the weighted sum in numerator will be smaller than denominator, making W < 1.
   ```

3. **Fix W statistic interpretation** (Lines 256-265)
   ```markdown
   #### W Statistic Interpretation (Detailed)
   
   **Range:** $0 < W \leq 1$
   
   **Extreme cases:**
   - $W = 1$: Perfect normal distribution
     - Observed order statistics exactly match expected
     - Example: Sample from N(0,1) with large n
   
   - $W = 0$: Impossible in practice
     - Would mean numerator = 0 (degenerate case)
     - Real-world minimum: W ≈ 0.7 (very non-normal)
   
   **Practical thresholds:**
   | W value | Assessment | Action |
   |---------|------------|--------|
   | W > 0.95 | Excellent normality | Use parametric tests |
   | 0.90 < W ≤ 0.95 | Good normality | Parametric OK for n>30 |
   | 0.85 < W ≤ 0.90 | Moderate departure | Check Q-Q plot |
   | W ≤ 0.85 | Severe non-normality | Use non-parametric |
   
   **Visual analogy:**
   W = 1.00: Perfect circle fitting data points
   W = 0.95: Slightly oval (still good)
   W = 0.80: Clearly stretched (problematic)
   ```

#### **Paired t-Test** (Lines 302-500)

**Critical additions:**

1. **Why differences?** (NEW subsection before formula)
   ````markdown
   #### Why Analyze Differences? (Paired Design Logic)
   
   **Unpaired approach (WRONG for our data):**
   - Treats CPU and GPU runs as independent samples
   - Ignores problem difficulty: eil51 vs pr1002 very different
   - High variance → low power
   
   **Paired approach (CORRECT):**
   - Computes $d_i = \text{CPU}_i - \text{GPU}_i$ for same problem
   - Removes problem difficulty from equation
   - Lower variance → higher power
   
   **Visual example:**
   ```
   Problem  CPU   GPU   Difference
   eil51    22s   5s    17s  ← Signal
   pr1002   450s  12s   438s ← Signal

   Unpaired variance: SD(22,450,5,12) = huge!
   Paired variance:   SD(17,438) = only problem-to-problem variation
   ```
   
   **Power gain:** Paired design typically 2-10× more powerful than unpaired
   ````

2. **`Degrees of freedom explanation** (Lines 370-372)
   ````markdown
   **Degrees of Freedom: $df = n - 1$**
   
   **What it means:**
   - Number of "free" values after estimating mean
   - Example: If you know mean of 3 numbers and 2 values, 
     the 3rd is determined (not "free")
   
   **Why it matters:**
   - Determines t-distribution shape (affects critical values)
   - Small df (n<30): Thicker tails, larger critical values
   - Large df (n≥100): Approaches normal distribution
   
   **Visual comparison:**
   ```ascii
        t(df=5)    t(df=30)    Normal
          *           *           *
         * *         ***         ***
        *   *       *****       *****
       *     *     *******     *******
      -4  -2  0  2  4 (z-score scale)
      └─ Thicker tails (more conservative)
   ```

   ````

3. **Fix confidence interval interpretation** (Lines 389-390)
   ```markdown
   #### Confidence Interval Deep Dive
   
   **Formula:**
   $$\text{CI}_{95\%} = \bar{d} \pm t_{0.975, n-1} \times \frac{s_d}{\sqrt{n}}$$
   
   **Component breakdown:**
   - $\bar{d}$: Point estimate (sample mean difference)
   - $t_{0.975, n-1}$: Critical value from t-table
     - For n=30 (df=29): t ≈ 2.045
     - For n=100 (df=99): t ≈ 1.984 (closer to z=1.96)
   - $\frac{s_d}{\sqrt{n}}$: Standard error of mean
     - Larger n → smaller SE → narrower CI
   
   **Interpretation (CORRECT):**
   "If we repeated this experiment infinitely, 95% of computed CIs 
   would contain the true population mean difference."
   
   **Interpretation (WRONG - common mistake):**
   ~~"There's a 95% probability the true mean is in this interval"~~
   (The true mean is fixed, not probabilistic in frequentist framework)
   
   **Practical use:**
   - If CI excludes 0 → significant difference (same as p<0.05)
   - CI width indicates precision: Narrow=precise, Wide=uncertain
   
   **Example:**
   CI = [17.2, 18.1] seconds
   → We're 95% confident CPU is 17.2-18.1s slower than GPU
   → Excludes 0, so difference is significant
   ```

#### **Wilcoxon Test** (Lines 511-700)

**Critical fixes:**

1. **W`hat are ranks?** (NEW subsection)
   ```markdown
   #### Understanding Ranks (Foundation of Non-Parametric Tests)
   
   **Ranking process:**
   ```
   Original data:    [12.5, 7.2, 19.8, 7.2, 15.1]
   Sorted:           [7.2,  7.2, 12.5, 15.1, 19.8]
   Positions:        [1,    2,   3,    4,    5]
   Handle ties:      [1.5,  1.5, 3,    4,    5]  ← Average ranks
   Restore order:    [3, 1.5, 5, 1.5, 4]
   ```
   
   **Why ranks instead of raw values?**
   1. **Robust to outliers:**
      - Raw: [10, 12, 15, 100] → mean = 34.25 (skewed by 100)
      - Ranks: [1, 2, 3, 4] → all contribute equally
   
   2. **Works with ordinal data:**
      - "Small, Medium, Large" → [1, 2, 3] (valid)
      - Can't compute mean of categories!
   
   3. **Distribution-free:**
      - Normal: mean=10, sd=2 → specific distribution
      - Ranks: Always uniform-ish (by construction)
   
   **Cost:** Discards magnitude information
   - Can't tell if ranks [1,2,3,4] came from [1,2,3,4] or [1,2,3,1000]
   ````

2. **Fix signed ranks explanation** (Lines 618-628)
   ````markdown
   #### Signed Ranks: Combining Direction and Magnitude
   
   **Step-by-step with real data:**
   ```
   Problem   CPU   GPU   d=CPU-GPU   |d|   Rank(|d|)   Sign   Signed Rank
   eil51     22s   5s    +17s        17    3           +      +3
   berlin52  24s   6s    +18s        18    4           +      +4
   eil76     45s   48s   -3s         3     1           -      -1
   pr76      50s   46s   +4s         4     2           +      +2
   ```
   
   **Rank computation:**
   1. Compute differences: CPU - GPU
   2. Ignore zeros (no difference to test)
   3. Rank absolute values: |d|
   4. Restore signs: sgn(d) × R
   
   **Intuition:**
   - Large positive ranks: CPU much slower (many cases)
   - Large negative ranks: GPU much slower (rare in our case)
   - Balanced ranks: No consistent difference
   
   **Test statistic $T^+$:**
   $$T^+ = \sum_{\text{positive differences}} \text{Rank}$$
   In example: T⁺ = 3 + 4 + 2 = 9
   
   **Null expectation:**
   If H₀ true (no difference), expect T⁺ ≈ T⁻ ≈ n(n+1)/4
   Here: E[T⁺] = 4×5/4 = 5, but observed 9 → skewed positive
   ````

3. **Fix null distribution explanation** (Lines 642-650)
   ````markdown
   #### Null Distribution of Signed Ranks (Why This Works)
   
   **Under H₀ (no true difference):**
   - Each rank R equally likely to be + or -
   - Like flipping n coins: each arrangement has probability (1/2)ⁿ
   
   **Enumeration example (n=3):**
   Ranks: 1, 2, 3 (from sorted |d₁|, |d₂|, |d₃|)
   
   Possible sign assignments (2³ = 8 outcomes):
   | Signs | T⁺ | Probability |
   |-------|-----|-------------|
   | +++ | 6 | 1/8 = 0.125 |
   | ++- | 3 | 1/8 = 0.125 |
   | +-+ | 4 | 1/8 = 0.125 |
   | +-- | 1 | 1/8 = 0.125 |
   | -++ | 5 | 1/8 = 0.125 |
   | -+- | 2 | 1/8 = 0.125 |
   | --+ | 3 | 1/8 = 0.125 |
   | --- | 0 | 1/8 = 0.125 |
   
   **Distribution of T⁺:**
   T⁺ = 0: 1/8 (12.5%)
   T⁺ = 1: 1/8 (12.5%)
   T⁺ = 2: 1/8 (12.5%)
   T⁺ = 3: 2/8 (25.0%) ← Most common
   T⁺ = 4: 1/8 (12.5%)
   T⁺ = 5: 1/8 (12.5%)
   T⁺ = 6: 1/8 (12.5%)
   
   **Mean:** E[T⁺] = 3 = n(n+1)/4 ✓
   **Variance:** Var(T⁺) = 3.5 = n(n+1)(2n+1)/24 ✓
   
   **For large n:** T⁺ ~ Normal(n(n+1)/4, n(n+1)(2n+1)/24)
   (Central Limit Theorem for sum of random signs)
   ````

#### **Friedman Test** (Lines 704-850)

**Critical additions:**

1. **What are rank sums?** (Lines 651-652 - needs full section)
   ````markdown
   #### Rank Sums: The Core of Friedman Test
   
   **Setup:**
   - n blocks (problems)
   - k treatments (algorithms)
   - Rank within each block: 1 (best) to k (worst)
   
   **Example with 3 problems, 4 algorithms:**
   ```
   Problem   CPU  HybridNaive  HybridOpt  FullGPU
   eil51     426  426          426        426     → Ranks: [2.5, 2.5, 2.5, 2.5] (all tied)
   berlin52  7545 7542         7542       7542    → Ranks: [4, 2, 2, 2] (CPU worst)
   pr76      110k 108k         107k       106k    → Ranks: [4, 3, 2, 1] (FullGPU best)
   ```
   
   **Rank sums (Rⱼ):**
   ```
   R_CPU         = 2.5 + 4 + 4   = 10.5
   R_HybridNaive = 2.5 + 2 + 3   = 7.5
   R_HybridOpt   = 2.5 + 2 + 2   = 6.5
   R_FullGPU     = 2.5 + 2 + 1   = 5.5
   ```
   
   **Expected under H₀ (all algorithms equal):**
   $$E[R_j] = n \times \frac{k+1}{2} = 3 \times \frac{4+1}{2} = 7.5$$
   
   **Observed deviations:**
   - CPU: 10.5 - 7.5 = +3.0 (consistently worse)
   - HybridNaive: 7.5 - 7.5 = 0.0 (average)
   - HybridOpt: 6.5 - 7.5 = -1.0 (slightly better)
   - FullGPU: 5.5 - 7.5 = -2.0 (consistently better)
   
   **Friedman statistic measures:** Sum of squared deviations
   (Large deviations → algorithms differ → reject H₀)
   ````

2. **Fix formula derivation** (Lines 651-677)
   ````markdown
   #### Friedman Statistic: Step-by-Step Derivation
   
   **Goal:** Detect if rank sums differ more than expected by chance
   
   **Step 1: Compute deviations from expected rank**
   $$d_j = \bar{r}_{\cdot j} - \frac{k+1}{2}$$
   
   Where:
   - $\bar{r}_{\cdot j} = \frac{1}{n}\sum_{i=1}^{n} r_{ij}$ (mean rank for algorithm j)
   - $\frac{k+1}{2}$ = expected rank if all equal (midpoint of 1..k)
   
   **Step 2: Sum squared deviations (weighted by sample size)**
   $$\text{SS}_{\text{treatments}} = n \sum_{j=1}^{k} d_j^2 = n \sum_{j=1}^{k} \left(\bar{r}_{\cdot j} - \frac{k+1}{2}\right)^2$$
   
   **Step 3: Normalize to get chi-squared distribution**
   $$Q = \frac{12n}{k(k+1)} \sum_{j=1}^{k} \left(\bar{r}_{\cdot j} - \frac{k+1}{2}\right)^2$$
   
   **Where does 12/[k(k+1)] come from?**
   - Variance of uniform ranks: $\frac{k^2-1}{12}$
   - Standardization factor: $\frac{12}{k(k+1)} = \frac{12}{k^2 + k}$
   
   **Alternative formulation (equivalent):**
   $$Q = \frac{12}{nk(k+1)} \sum_{j=1}^{k} R_j^2 - 3n(k+1)$$
   
   **Derivation:**
   $$\sum_{j=1}^{k} R_j^2 = n^2 \sum_{j=1}^{k} \bar{r}_{\cdot j}^2$$
   Expanding and simplifying using $\sum \bar{r}_j = nk(k+1)/2$ yields the formula.
   
   **Distribution under H₀:**
   - Small samples: Use exact tables (permutation-based)
   - Large samples (n>15 or k>4): $Q \sim \chi^2_{k-1}$
     - Asymptotic result from CLT for rank sums
   ````

3. **Add Kendall's W interpretation** (Line 736)
   ````markdown
   #### Kendall's W: Effect Size for Friedman Test
   
   **Formula:**
   $$W = \frac{Q}{n(k-1)} = \frac{12 \sum_j \bar{r}_{\cdot j}^2 - 3n^2k(k+1)^2}{n^2k(k-1)}$$
   
   **Range:** $0 \leq W \leq 1$
   
   **Interpretation:**
   - W = 0: Perfect disagreement (ranks completely random)
     - Each algorithm ranks 1st, 2nd, ..., kth equally often
   - W = 1: Perfect agreement (same rank order across all problems)
     - Algorithm A always 1st, B always 2nd, etc.
   
   **Practical benchmarks:**
   | W value | Interpretation | Meaning for algorithms |
   |---------|----------------|------------------------|
   | 0.0-0.1 | No consensus | Algorithms perform inconsistently |
   | 0.1-0.3 | Weak agreement | Some patterns emerge |
   | 0.3-0.5 | Moderate agreement | Clear performance tiers |
   | 0.5-0.7 | Strong agreement | Consistent ranking across problems |
   | 0.7-1.0 | Very strong | One algorithm dominates |
   
   **Example from benchmark:**
   ```
   W = 0.68 for GPU algorithms
   → Strong agreement: FullGPU consistently outperforms others
   → Not perfect (W<1): Some problems favor HybridOpt
   ```
   
   **Relationship to ICC:**
   Kendall's W = Intraclass Correlation Coefficient for ranks
   (Measures reliability of algorithm rankings)
   ````

#### **Nemenyi Test** (Lines 858-1000)

**Critical additions:**

1. **Critical difference visualization** (Lines 858-866)
   ````markdown
   #### Critical Difference: Visual Interpretation
   
   **Formula reminder:**
   $$CD = q_{\alpha} \sqrt{\frac{k(k+1)}{6n}}$$
   
   **Component explanation:**
   - $q_{\alpha}$: Studentized range critical value
     - From Tukey's HSD (Honestly Significant Difference)
     - Accounts for multiple comparisons
     - Example: k=4, α=0.05 → q ≈ 2.639
   
   - $\sqrt{\frac{k(k+1)}{6n}}$: Standard error of rank difference
     - Larger n → smaller SE → smaller CD (easier to detect differences)
     - More algorithms k → larger CD (harder to differentiate)
   
   **ASCII Diagram:**
   ```
   Mean Ranks:
   FullGPU    HybridOpt  HybridNaive    CPU
      1.2        2.4         2.8        4.0
      |-----------|-----------|-----------|
      └─ 1.2 ──┘  └─ 0.4 ─┘  └─ 1.2 ──┘
         (CD=0.85)

   Significant differences:
   - FullGPU vs CPU: |1.2 - 4.0| = 2.8 > 0.85 ✓
   - FullGPU vs HybridNaive: |1.2 - 2.8| = 1.6 > 0.85 ✓
   - HybridNaive vs HybridOpt: |2.8 - 2.4| = 0.4 < 0.85 ✗
   ```
   
   **Critical Difference Diagram (Standard in ML):**
   ```
       1.0      1.5      2.0      2.5      3.0      3.5      4.0
   FullGPU ●━━━━━━━━━━┓
   HybridOpt        ●━━┫━━━━━━━━┓
   HybridNaive         ●━━━━━━━━┫
   CPU                              ●
                     └─ CD ─┘

   Legend:
   ● = Mean rank
   ━ = 95% CI (± CD/2)
   Overlapping bars = NOT significantly different
   ````

2. **P-value matrix interpretation** (NEW subsection)
   ````markdown
   #### Nemenyi P-Value Matrix: Reading the Results
   
   **Example matrix:**
   ```
                    CPU   HybridNaive  HybridOpt  FullGPU
   CPU              1.000    0.012       0.003     <0.001
   HybridNaive      0.012    1.000       0.582      0.004
   HybridOptimized  0.003    0.582       1.000      0.008
   FullGPU         <0.001    0.004       0.008      1.000
   ```
   
   **How to read:**
   1. **Diagonal (1.000):** Algorithm vs itself (always identical)
   
   2. **Symmetric:** P(A vs B) = P(B vs A)
      - Only need to read upper/lower triangle
   
   3. **Significance (α=0.05):**
      - p < 0.05 → Algorithms differ significantly
      - p ≥ 0.05 → No evidence of difference
   
   4. **Color-coded interpretation:**
      - 🟢 p ≥ 0.05: Not significantly different
      - 🟡 0.01 ≤ p < 0.05: Marginally significant
      - 🟠 0.001 ≤ p < 0.01: Strongly significant
      - 🔴 p < 0.001: Very strongly significant
   
   **Summary from example:**
   ```
   CPU differs from: All 3 GPU variants (all p<0.05)
   GPU variants among themselves:
     - HybridNaive ≈ HybridOpt (p=0.582, not significant)
     - HybridNaive vs FullGPU (p=0.004, significant)
     - HybridOpt vs FullGPU (p=0.008, significant)

   Conclusion: 3 performance tiers exist:
     Tier 1 (best): FullGPU
     Tier 2 (middle): HybridNaive, HybridOptimized (tied)
     Tier 3 (worst): CPU
   ```
   ````

#### **Holm-Bonferroni** (Lines 1002-1150)

**Critical fix:**

1. **Why multiple comparison correction?** (NEW opening section)
   ````markdown
   #### The Multiple Comparison Problem
   
   **Scenario without correction:**
   ```
   6 pairwise tests, each at α=0.05
   P(at least 1 false positive) = 1 - (1-0.05)⁶ = 0.265 (26.5%!)

   Expected: 5% error rate
   Actual: 26.5% error rate (5× worse)
   ```
   
   **Visual demonstration:**
   ```
   Test 1: [████████████████████░░] p=0.03 → Significant
   Test 2: [███████████████████████] p=0.01 → Significant
   Test 3: [█████████████████░░░░░░] p=0.06 → Not significant
   Test 4: [████████████░░░░░░░░░░░] p=0.12 → Not significant
   Test 5: [████████████████░░░░░░░] p=0.048 → Significant (barely!)
   Test 6: [███████████████████░░░░] p=0.04 → Significant

   4/6 tests significant by chance alone!
   ```
   
   **Family-Wise Error Rate (FWER):**
   $$\text{FWER} = P(\text{at least 1 Type I error in family})$$
   
   **Goal:** Keep FWER ≤ α (e.g., 0.05) across ALL tests
   
   **Methods comparison:**
   | Method | Correction | FWER control | Power |
   |--------|------------|--------------|-------|
   | None | p₍ᵢ₎ | NO | Highest (but invalid) |
   | Bonferroni | p₍ᵢ₎ × m | YES | Low |
   | Holm | p₍ᵢ₎ × (m-i+1) | YES | Medium |
   | Hochberg | (step-up) | YES* | Higher |
   | FDR (BH) | (controls FDR) | NO | Highest (valid) |
   
   *Requires positive dependence
   ````

2. **Fix step-down procedure explanation** (Lines 1048-1060)
   ````markdown
   #### Step-Down Procedure: Why It Works
   
   **Key insight:** Test most significant hypotheses first with strictest threshold
   
   **Step-by-step logic:**
   
   **Step 1:** Sort p-values ascending
   ```
   p₍₁₎ ≤ p₍₂₎ ≤ ... ≤ p₍ₘ₎
   ```
   
   **Step 2:** Test sequentially with adjusted thresholds
   ```
   Test 1: Compare p₍₁₎ to α/m
     ├─ If p₍₁₎ > α/m: STOP (all H₀ retained)
     └─ If p₍₁₎ ≤ α/m: Reject H₍₁₎, continue to test 2

   Test 2: Compare p₍₂₎ to α/(m-1)  [Less strict!]
     ├─ If p₍₂₎ > α/(m-1): STOP
     └─ If p₍₂₎ ≤ α/(m-1): Reject H₍₂₎, continue

   ...

   Test i: Compare p₍ᵢ₎ to α/(m-i+1)
   ```
   
   **Mathematical proof (sketch):**
   Under global H₀ (all null hypotheses true):
   
   $$P(\text{any rejection}) = P(p_{(1)} \leq \alpha/m)$$
   
   By Bonferroni inequality:
   $$P(p_{(1)} \leq \alpha/m) \leq m \times P(p_i \leq \alpha/m) = m \times \frac{\alpha}{m} = \alpha$$
   
   Therefore: FWER ≤ α ✓
   
   **Why more powerful than Bonferroni?**
   - Bonferroni: Uses α/m for ALL tests (overly conservative)
   - Holm: Uses α/m only for first test, then α/(m-1), α/(m-2), ...
   - Later tests have more "room" to reject (higher thresholds)
   
   **Concrete example:**
   ```
   m = 6 tests, α = 0.05

   Bonferroni (single-step):
     All 6 tests use α/6 = 0.0083

   Holm (step-down):
     Test 1: α/6 = 0.0083
     Test 2: α/5 = 0.0100  [+20% increase]
     Test 3: α/4 = 0.0125  [+50% increase]
     Test 4: α/3 = 0.0167  [+100% increase]
     Test 5: α/2 = 0.0250  [+200% increase]
     Test 6: α/1 = 0.0500  [+500% increase]

   → Holm rejects more hypotheses (higher power) while maintaining same FWER
   ```
   ````

#### **Cohen's d** (Lines 1152-1350)

**Critical additions:**

1. **Why standardize?** (NEW opening section)
   ````markdown
   #### Why Effect Sizes Matter: The p-value Paradox
   
   **Problem with p-values alone:**
   
   **Example 1: Large sample (n=10,000)**
   ```
   CPU: mean=100.5ms, sd=10ms
   GPU: mean=100.0ms, sd=10ms
   Difference: 0.5ms (trivial!)

   t-test: t=35.4, p<0.001 (highly significant!)
   Conclusion: Statistically significant but practically worthless
   ```
   
   **Example 2: Small sample (n=10)**
   ```
   CPU: mean=100ms, sd=10ms
   GPU: mean=50ms, sd=15ms
   Difference: 50ms (huge!)

   t-test: t=1.95, p=0.08 (not significant)
   Conclusion: Not statistically significant but massive practical difference
   ```
   
   **P-value depends on:**
   1. Effect size (what we care about)
   2. Sample size (often arbitrary)
   3. Variance (can be reduced by better measurement)
   
   **Cohen's d isolates effect size:**
   $$d = \frac{\text{Mean difference}}{\text{Standard deviation}}$$
   
   **Interpretation:** "Means differ by d standard deviations"
   
   **Example 1 revisited:**
   ```
   d = (100.5 - 100.0) / 10 = 0.05 (negligible)
   → p<0.001 misleading due to huge n
   ```
   
   **Example 2 revisited:**
   ```
   d = (100 - 50) / 12.5 = 4.0 (extremely large)
   → p=0.08 misleading due to small n
   ```
   
   **Bottom line:** Always report BOTH p-value AND effect size!
   ````

2. **Fix overlap/percentile interpretation** (Lines 1280-1290)
   ````markdown
   #### Cohen's d Visualized: Distribution Overlap
   
   **ASCII visualization of effect sizes:**
   
   **d = 0.2 (small effect):**
   ```
         Group 1          Group 2
            *                *
          * * *            * * *
         * * * *          * * * *
        * * * * *        * * * * *
       * * * * * *      * * * * * *
      |--------●--------|--------●--------|
             μ₁                 μ₂
      └──── 85% overlap ────┘

   Interpretation: 58% of Group 1 scores exceed median of Group 2
   ```
   
   **d = 0.8 (large effect):**
   ```
         Group 1                  Group 2
            *                        *
          * * *                    * * *
         * * * *                  * * * *
        * * * * *                * * * * *
       * * * * * *              * * * * * *
      |--------●----------------|--------●--|
             μ₁                         μ₂
      └────── 53% overlap ──────┘

   Interpretation: 79% of Group 1 exceeds median of Group 2
   ```
   
   **d = 2.0 (huge effect):**
   ```
       Group 1                                Group 2
          *                                      *
        * * *                                  * * *
       * * * *                                * * * *
      * * * * *                              * * * * *
     * * * * * *                            * * * * * *
    |----●----|                        |----●----|
         μ₁                                   μ₂
    └─ 19% overlap ─┘

   Interpretation: 98% of Group 1 exceeds median of Group 2
   Nearly non-overlapping distributions!
   ```
   
   **Percentile interpretation formula:**
   If d = 1.0, mean of Group 1 is at 84th percentile of Group 2
   
   $$\text{Percentile} = \Phi(d) \times 100\%$$
   
   Where Φ is standard normal CDF:
   - d=0.5 → Φ(0.5)=0.69 → 69th percentile
   - d=1.0 → Φ(1.0)=0.84 → 84th percentile
   - d=2.0 → Φ(2.0)=0.98 → 98th percentile
   ````

#### **Bootstrap** (Lines 1400-1580)

**Critical fix:**

1. **Fix LaTeX escaping** (Lines 1353-1377)
   ````markdown
   # CURRENT (BROKEN):
   $$[\\text{CI}_{\\alpha/2}, \\text{CI}_{1-\\alpha/2}]$$
   
   # FIXED:
   $$[\text{CI}_{\alpha/2}, \text{CI}_{1-\alpha/2}]$$
   
   # Pattern throughout Bootstrap section:
   - Replace `\\{` with `\{`
   - Replace `\\theta` with `\theta`
   - Replace `\\Phi` with `\Phi`
   - Replace `\\hat{\\theta}` with `\hat{\theta}`
   ````

2. **Why resampling works** (NEW intuitive section)
   ````markdown
   #### Bootstrap Magic: Why Does Resampling Work?
   
   **Key principle:** The sample approximates the population
   
   **Analogy:**
   ```
   Population (unknown)    Sample (observed)    Bootstrap samples
   ┌─────────────┐        ┌─────────┐          ┌───────┐┌───────┐
   │ ● ● ● ● ● ●│        │ ● ● ● ●│          │● ● ●││ ● ●│
   │ ● ● ● ● ● ●│  →     │ ● ● ● ●│    →    │● ● ●││● ●││...
   │ ● ● ● ● ● ●│        │ ● ● ● ●│          │● ● ●││● ●││
   │ ● ● ● ● ● ●│        └─────────┘          └───────┘└───────┘
   └─────────────┘          n=12                B=10,000
       N=∞                                      (each size n)
   ```
   
   **Step 1: Sample from population**
   - Real world: Draw n=30 observations
   - Get sample distribution
   
   **Step 2: Treat sample as mini-population**
   - Pretend sample IS the population
   - Resample with replacement B times
   
   **Step 3: Bootstrap distribution approximates sampling distribution**
   ```
   True sampling distribution    Bootstrap distribution
   (what we want, can't access)  (approximation we compute)

       *                             *
     * * *                         * * *
    * * * *                       * * * *
   * * * * *                     * * * * *
   |---●---|                     |---●---|
      μ_true                        μ_sample

   As n→∞ and B→∞, bootstrap → truth (Efron, 1979 proof)
   ```
   
   **Mathematical justification:**
   
   Let F = true population CDF, F̂ = empirical CDF (sample)
   
   **Traditional inference:**
   $$\text{CI} = \hat{\theta} \pm z_{\alpha/2} \times SE(\hat{\theta})$$
   Requires: Know SE formula (often complex/unknown)
   
   **Bootstrap inference:**
   $$\text{CI} = [\text{quantiles of } \{\hat{\theta}^*_1, ..., \hat{\theta}^*_B\}]$$
   Requires: Only ability to compute θ̂ (works for ANY statistic!)
   
   **Why with replacement?**
   - Without replacement: Each bootstrap sample = original sample (useless!)
   - With replacement: Each bootstrap sample varies (captures sampling uncertainty)
   ````

---

### Phase 4: New Comprehensive Sections

#### **Add: Statistical Power Analysis** (NEW section)

````markdown
### Statistical Power: Detecting Real Effects

**What is power?**
$$\text{Power} = P(\text{reject } H_0 | H_1 \text{ true}) = 1 - \beta$$

**Factors affecting power:**
1. Effect size (d): Larger → more power
2. Sample size (n): Larger → more power
3. Significance level (α): Larger → more power (but more Type I errors)
4. Test choice: Parametric > non-parametric (if assumptions met)

**Power curves for paired t-test:**
[ASCII graph showing power vs n for different effect sizes]

**Practical implications for benchmarking:**
- Need n=30 to detect d=0.5 with 80% power at α=0.05
- GPU speedups (d>2.0) detectable with n=10
- Small optimizations (d=0.2) require n>200 for reliable detection
````

#### **Add: Bayesian vs Frequentist** (NEW section in Foundations)

````markdown
### Two Paradigms: Frequentist vs Bayesian

**Frequentist (our approach):**
- Probability = long-run frequency
- Parameters fixed (unknown)
- Data random (sampled)
- P-value: P(data | H₀)
- **Advantages:** Objective, no prior needed, standard in industry
- **Disadvantages:** Doesn't answer "what's probable?" directly

**Bayesian alternative:**
- Probability = degree of belief
- Parameters random (have distribution)
- Data fixed (observed)
- Posterior: P(hypothesis | data)
- **Advantages:** Direct probability statements, incorporates prior knowledge
- **Disadvantages:** Requires prior specification, computationally intensive

**Why frequentist for GPU benchmarks?**
1. Reproducibility: No subjective priors
2. Industry standard: Easier peer review
3. Simpler computation: t-test vs MCMC
4. Conservative: Harder to claim false positives

**When Bayesian would be better:**
- Small n (prior helps stabilize)
- Sequential testing (early stopping)
- Prior knowledge available (e.g., from literature)
````

---

## Implementation Plan

### **Phase 1: Foundations (Days 1-2)**

1. Write Section 0: Statistical Foundations
2. Create comprehensive symbol glossary
3. Add parametric vs non-parametric decision framework
4. Standardize all headers (remove `**bold**` emphasis)

### **Phase 2: Fix Existing Tests (Days 3-7)**

**Per test (1 day each):**

1. Historical context + motivation
2. Plain language "what/why"
3. Step-by-step math with ALL symbols defined
4. Fix LaTeX formatting (standardize on KaTeX)
5. Decision matrix (when/why use)
6. Worked example with real benchmark data
7. Visual aids (ASCII art, tables)
8. Common pitfalls section

**Order:**

- Day 3: Shapiro-Wilk (foundation for all others)
- Day 4: Paired t-test + Wilcoxon (pairwise comparisons)
- Day 5: Friedman + Nemenyi (k-sample + post-hoc)
- Day 6: Holm-Bonferroni + Cohen's d (corrections + effect sizes)
- Day 7: Bootstrap (confidence intervals)

### **Phase 3: New Sections (Days 8-9)**

- Power analysis
- Bayesian vs Frequentist
- Complete worked example (full pipeline)

### **Phase 4: Polish (Day 10)**

- Verify all LaTeX renders correctly
- Check internal consistency
- Add cross-references between sections
- Final proofreading

---

## Current Document Status

**Completion by section:**

| Section | Content | Formatting | Math | Examples | Status |
|---------|---------|------------|------|----------|--------|
| **0. Foundations** | ❌ Missing | N/A | N/A | N/A | **NOT STARTED** |
| 1. Shapiro-Wilk | ⚠️ Partial | ❌ Poor | ⚠️ Some | ⚠️ Some | **40% COMPLETE** |
| 2. Paired t-test | ⚠️ Partial | ❌ Poor | ⚠️ Some | ✅ Good | **50% COMPLETE** |
| 3. Wilcoxon | ⚠️ Partial | ❌ Poor | ❌ Poor | ⚠️ Some | **35% COMPLETE** |
| 4. Friedman | ⚠️ Partial | ❌ Poor | ❌ Poor | ⚠️ Some | **35% COMPLETE** |
| 5. Nemenyi | ⚠️ Partial | ❌ Poor | ⚠️ Some | ⚠️ Some | **40% COMPLETE** |
| 6. Holm-Bonferroni | ⚠️ Partial | ❌ Poor | ⚠️ Some | ✅ Good | **45% COMPLETE** |
| 7. Cohen's d | ✅ Good | ⚠️ Fair | ✅ Good | ✅ Good | **70% COMPLETE** |
| 8. Bootstrap | ⚠️ Partial | ❌ Broken | ❌ Broken LaTeX | ⚠️ Some | **30% COMPLETE** |
| **Power Analysis** | ❌ Missing | N/A | N/A | N/A | **NOT STARTED** |
| **Bayesian vs Freq** | ❌ Missing | N/A | N/A | N/A | **NOT STARTED** |

**Overall status: ~30% complete** (vs original estimate of 80%)

**Critical gaps:**

- No foundational concepts (reader cannot understand tests)
- Inconsistent formatting (mix of Unicode, ASCII, KaTeX)
- Missing intuition (formulas without explanation)
- Poor visual aids (few diagrams, no clear decision trees)
- Broken LaTeX in Bootstrap section

**Time estimate:** 10 days of focused work to complete to thesis-defense quality

---

## Next Steps (Awaiting Approval)

**Do you want me to:**

1. ✅ **Proceed with Phase 1** (Foundations + symbol glossary)?
2. ✅ **Fix all LaTeX formatting first** (quick win, document readable)?
3. ✅ **Focus on specific test** (e.g., "Fix Wilcoxon completely first")?
4. ❓ **Other priority**?

I'm ready to execute once you approve the plan. Each phase is modular, so we can iterate section-by-section with your feedback.
