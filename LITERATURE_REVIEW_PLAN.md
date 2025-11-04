# Literature Review Plan - GPU-Accelerated Routing Optimization TCC

**Purpose:** Strategic reading plan for TCC literature review section  
**Time Budget:** 8-12 hours total (2-3 hours per priority tier)  
**Last Updated:** 2025-10-16

---

## 📚 **READING PRIORITY STRUCTURE**

### **Tier 1: ESSENTIAL (Must Read - 4-6 hours)**

Papers that directly support your core contribution (GPU acceleration for routing heuristics)

#### **1.1 GPU Computing for Optimization**

| Paper | Authors/Year | Why Essential | Reading Time | Notes Location |
|-------|--------------|---------------|--------------|----------------|
| GPU-accelerated distance matrix computation | Fujimoto et al. (2011) | Direct GPU application to TSP/VRP | 2 hours | Section 2.5 |
| CUDA-based local search for TSP | [Find in refs.bib] | GPU local search vectorization | 1.5 hours | Section 2.5 |

**Reading Strategy:**

- Focus on **methodology sections** (how they vectorized algorithms)
- Extract **performance metrics** (speedup values, problem sizes tested)
- Note **limitations** (memory constraints, breakeven points)
- **Actionable output:** Justify your vectorization approach, cite expected speedup ranges

#### **1.2 Simulated Annealing Fundamentals**

| Resource | Authors/Year | Why Essential | Reading Time | Notes Location |
|----------|--------------|---------------|--------------|----------------|
| Original SA paper | Kirkpatrick et al. (1983) | Foundational reference | 1 hour | Section 2.3.2 |
| SA cooling schedules survey | [Survey paper] | Parameter tuning guidelines | 1.5 hours | Section 2.3.2 |

**Reading Strategy:**

- Extract **cooling schedule formulas** (geometric: $T_{k+1} = \\alpha T_k$)
- Note **parameter ranges** from successful implementations
- Identify **stopping criteria** used in literature
- **Actionable output:** Justify your SA parameter choices in methodology

---

### **Tier 2: IMPORTANT (Should Read - 3-4 hours)**

Papers that provide context and validate your approach

#### **2.1 TSP/VRP Complexity and Approximations**

| Paper | Authors/Year | Purpose | Reading Time | Citation Use |
|-------|--------------|---------|--------------|--------------|
| TSP complexity fundamentals | [Classic reference] | NP-hardness justification | 30 min | Section 2.1 |
| Christofides 1.5-approximation | Christofides (1976) | Theoretical baseline | 45 min | Sections 2.1, 2.2.1 |
| VRP survey paper | [Recent survey] | CVRP variant overview | 1 hour | Section 2.1 |

**Reading Strategy:**

- **Skim proofs**, focus on results and implications
- Extract key **complexity bounds** (TSP is NP-hard, Christofides guarantee)
- Note **standard notation** for consistency
- **Actionable output:** Provide theoretical context for why heuristics are necessary

#### **2.2 Local Search Heuristics**

| Paper | Authors/Year | Purpose | Reading Time | Citation Use |
|-------|--------------|---------|--------------|--------------|
| 2-opt original paper | Croes (1958) | Algorithm attribution | 30 min | Section 2.2.2 |
| Or-opt for TSP | Or (1976) | Algorithm attribution | 30 min | Section 2.2.2 |
| Local search survey | [Survey paper] | Neighborhood structures | 1 hour | Section 2.2.2 |

**Reading Strategy:**

- Focus on **algorithm descriptions** (pseudocode, complexity analysis)
- Note **performance characteristics** (solution quality, runtime)
- Identify **standard implementations** for validation
- **Actionable output:** Cite original papers for each implemented heuristic

---

### **Tier 3: SUPPORTING (Optional Read - 2-3 hours)**

Papers for additional context if time permits

#### **3.1 Hybrid Metaheuristics**

| Paper | Authors/Year | Purpose | Reading Time | Citation Use |
|-------|--------------|---------|--------------|--------------|
| Memetic algorithms survey | Moscato & Cotta (survey) | Hybrid approach context | 1 hour | Section 2.4 |
| GA for routing problems | [GA application paper] | Crossover operators | 1 hour | Section 2.3.1 |

**Reading Strategy:**

- **Skim for concepts**, don't implement details
- Extract **hybrid strategy taxonomy**
- Note **performance comparison studies**
- **Actionable output:** Justify SA+2-opt as established hybrid approach

#### **3.2 GPU Optimization Surveys**

| Paper | Authors/Year | Purpose | Reading Time | Citation Use |
|-------|--------------|---------|--------------|--------------|
| GPU computing survey | [Recent survey] | General GPU optimization | 1 hour | Section 2.5 |
| Parallel metaheuristics | [Survey paper] | Parallelization strategies | 1 hour | Section 2.5 |

**Reading Strategy:**

- Focus on **parallelization patterns** (data parallel, task parallel)
- Note **memory management strategies**
- Extract **performance modeling** (Amdahl's law, memory bandwidth)
- **Actionable output:** Cite general GPU benefits, explain why local search is good fit

---

### **Tier 4: REFERENCE ONLY (Cite, Don't Read - 0 hours)**

Classic papers to cite for completeness

| Paper | Authors/Year | Citation Purpose |
|-------|--------------|------------------|
| Clarke-Wright Savings | Clarke & Wright (1964) | Construction heuristic attribution |
| Lin-Kernighan | Lin & Kernighan (1973) | Advanced local search mention |
| Genetic Algorithms book | Goldberg (1989) | GA foundational reference |
| Tabu Search original | Glover (1986) | TS foundational reference |

**Strategy:** Cite in bibliography, no reading needed (standard references)

---

## 📖 **BOOK REFERENCES**

### **Essential Books (Strategic Reading)**

| Book | Authors/Year | Relevant Chapters | Reading Strategy | Time Budget |
|------|--------------|-------------------|------------------|-------------|
| **"In Pursuit of the Traveling Salesman"** | Cook (2012) | Ch. 3 (Heuristics), Ch. 6 (Implementations) | Read selected chapters for TSP context | 2 hours |
| **"Vehicle Routing: Problems, Methods, and Applications"** | Toth & Vigo (2014) | Ch. 4 (Heuristics), Ch. 6 (Metaheuristics) | Reference for CVRP algorithms | 1.5 hours |
| **"Handbook of Metaheuristics"** | Gendreau & Potvin (2019) | Ch. on SA, Ch. on Hybrid Methods | Parameter tuning guidelines | 2 hours |

**Book Reading Strategy:**

1. **Read introductions** to understand scope
2. **Focus on pseudocode** sections (algorithm details)
3. **Skim mathematical proofs** (cite results, skip derivations)
4. **Extract tables** (performance comparisons, parameter ranges)

---

## 🎯 **LITERATURE REVIEW WRITING STRATEGY**

### **Section 2.1: Combinatorial Optimization Problems (1 page)**

**Structure:**

- TSP definition and NP-hardness (cite complexity paper)
- CVRP variant description (cite Toth & Vigo)
- Approximation results (cite Christofides for 1.5-approx)
- Justify heuristic approach necessity

**Key Citations:**

- Cook (2012) - TSP overview
- Toth & Vigo (2014) - CVRP definition
- Christofides (1976) - Approximation guarantee

**Writing Time:** 2 hours

---

### **Section 2.2: Heuristic Approaches (2 pages)**

**Structure:**

- **2.2.1 Construction Heuristics** (0.5 page)
  - Clarke-Wright for CVRP (cite Clarke & Wright 1964)
  - Nearest Neighbor for TSP (cite standard reference)
  - Brief mention of insertion heuristics
  
- **2.2.2 Improvement Heuristics** (1.5 pages)
  - 2-opt: algorithm description, complexity O(n²) (cite Croes 1958)
  - Or-opt: sequence moves, O(n²) (cite Or 1976)
  - Brief mention: 3-opt, Cross-exchange, Lin-Kernighan
  - Neighborhood evaluation cost analysis

**Key Citations:**

- Croes (1958) - 2-opt
- Or (1976) - Or-opt  
- Local search survey paper - comprehensive overview

**Writing Time:** 3-4 hours

---

### **Section 2.3: Metaheuristic Strategies (2 pages)**

**Structure:**

- **2.3.1 Genetic Algorithms** (0.5 page)
  - Population-based search principles
  - Crossover operators for routing (PMX, OX)
  - Brief overview (not implemented, but context)
  
- **2.3.2 Simulated Annealing** (1 page) **← DETAILED**
  - Acceptance probability: $P = e^{-\\Delta E / T}$
  - Cooling schedules: geometric, linear, adaptive
  - Parameter tuning from literature (initial temp, cooling rate)
  - SA + local search hybrid approach
  
- **2.3.3 Tabu Search** (0.5 page)
  - Memory-based search
  - Tabu list concept
  - Brief overview (completeness)

**Key Citations:**

- Kirkpatrick et al. (1983) - SA fundamentals
- SA survey paper - cooling schedules and parameters
- Goldberg (1989) - GA reference
- Glover (1986) - TS reference

**Writing Time:** 3-4 hours

---

### **Section 2.4: Hybrid Approaches (1 page)**

**Structure:**

- Memetic algorithms concept (GA + LS)
- Benefits of hybridization (exploration + exploitation)
- Literature examples: SA+2-opt, GA+2-opt studies
- Justify SA+2-opt choice for this TCC

**Key Citations:**

- Moscato & Cotta - Memetic algorithms survey
- Hybrid metaheuristics applications

**Writing Time:** 2 hours

---

### **Section 2.5: GPU Computing for Optimization (2 pages)**

**Structure:**

- **CUDA/CuPy basics** (0.5 page)
  - Thread hierarchy, memory model
  - CuPy as NumPy-compatible interface
  
- **Vectorization strategies** (1 page)
  - Array operations vs loops
  - Parallel neighborhood evaluation
  - Memory transfer considerations
  
- **Routing-specific GPU applications** (0.5 page)
  - Distance matrix computations (cite Fujimoto et al.)
  - Local search acceleration
  - Performance characteristics (problem size, speedup)

**Key Citations:**

- Fujimoto et al. (2011) - GPU distance matrix **← CRITICAL**
- GPU TSP papers - local search vectorization
- GPU computing survey - general optimization context

**Writing Time:** 3-4 hours

---

## 📋 **CITATION ORGANIZATION**

### **Citation Matrix: Where to Cite What**

| Reference Type | Section 2.1 | Section 2.2 | Section 2.3 | Section 2.4 | Section 2.5 |
|----------------|-------------|-------------|-------------|-------------|-------------|
| **TSP/VRP Complexity** | ✓✓✓ | ✓ | | | |
| **Approximation Algorithms** | ✓✓ | ✓✓ | | | |
| **Construction Heuristics** | | ✓✓✓ | | | |
| **Local Search** | | ✓✓✓ | ✓ | ✓✓ | ✓ |
| **Simulated Annealing** | | | ✓✓✓ | ✓✓ | |
| **Other Metaheuristics** | | | ✓✓ | ✓ | |
| **Hybrid Methods** | | | ✓ | ✓✓✓ | |
| **GPU Computing** | | | | | ✓✓✓ |

**Legend:**

- ✓✓✓ = Primary citations (3-5 papers)
- ✓✓ = Supporting citations (1-2 papers)
- ✓ = Brief mention (cite for completeness)

---

## 🔍 **READING WORKFLOW**

### **Week 1 (Before Implementation):**

**Day 1 (3 hours):**

- [ ] Read Fujimoto et al. GPU distance matrix paper
- [ ] Extract vectorization strategies
- [ ] Note speedup values and problem sizes tested

**Day 2 (2 hours):**

- [ ] Read Kirkpatrick SA paper
- [ ] Read SA cooling schedule survey
- [ ] Extract parameter tuning guidelines

**Day 3 (2 hours):**

- [ ] Read 2-opt, Or-opt original papers
- [ ] Review local search survey
- [ ] Extract complexity analysis

**Day 4 (1.5 hours):**

- [ ] Skim TSP/VRP complexity papers
- [ ] Read Christofides approximation paper
- [ ] Extract key theoretical results

**Total Week 1:** 8-9 hours of focused reading

---

### **Week 2-3 (During Implementation):**

**Optional supporting reading:**

- [ ] Hybrid metaheuristics survey (2 hours)
- [ ] GPU computing survey (1.5 hours)
- [ ] GA/TS overview papers (1 hour)

**Total Optional:** 4-5 additional hours if time permits

---

## 📝 **NOTE-TAKING TEMPLATE**

For each paper read, create notes file: `literature_notes/[author]_[year].md`

### **Template Structure:**

```markdown
# [Paper Title]

**Authors:** [Names]  
**Year:** [Year]  
**Relevance:** [Which TCC section uses this]  
**Reading Time:** [Actual time spent]

## Key Findings

- Finding 1 (cite page/section)
- Finding 2 (cite page/section)

## Methodology

- Algorithm description
- Experimental setup
- Performance metrics

## Results Relevant to TCC

- Speedup values: [X]x for problem size n=[Y]
- Parameter values used: [cooling rate, temperature, etc.]
- Limitations noted: [memory constraints, overhead, etc.]

## Citation Use

**In Section 2.X:**  
"Fujimoto et al. (2011) demonstrated GPU acceleration of distance matrix computations, achieving 10-15x speedup for instances with n>500 nodes."

**Direct Quotes (if needed):**  
> "Quote with page number"

## Implementation Ideas

- Actionable insights for my code
- Parameter ranges to try
- Validation approaches
```

---

## 🎯 **LITERATURE REVIEW COMPLETION CRITERIA**

### **Minimum (Pass TCC):**

- [ ] Section 2.1: 3+ citations (TSP/VRP complexity)
- [ ] Section 2.2: 4+ citations (construction + improvement heuristics)
- [ ] Section 2.3: 5+ citations (SA detailed, GA/TS mentioned)
- [ ] Section 2.4: 2+ citations (hybrid approaches)
- [ ] Section 2.5: 3+ citations (GPU computing, **including Fujimoto**)
- [ ] Total: 15-20 unique references

### **Target (Good Grade):**

- [ ] All sections have 5-7 citations each
- [ ] Include 2-3 book references
- [ ] Mix of classic papers + recent surveys
- [ ] Total: 25-30 unique references

### **Excellence:**

- [ ] Comprehensive coverage of each topic
- [ ] Recent papers (2018-2024) included
- [ ] Comparative analysis of approaches
- [ ] Total: 35-40 unique references

---

## 📚 **BIBLIOGRAPHY MANAGEMENT**

### **refs.bib Organization:**

```bibtex
% ============================================
% TSP/VRP COMPLEXITY AND THEORY
% ============================================

@article{christofides1976,
  author = {Christofides, N.},
  title = {Worst-case analysis of a new heuristic for the TSP},
  journal = {Operations Research},
  year = {1976},
  note = {Section 2.1, 2.2.1}
}

% ============================================
% LOCAL SEARCH HEURISTICS
% ============================================

@article{croes1958,
  author = {Croes, G. A.},
  title = {A method for solving TSP},
  journal = {Operations Research},
  year = {1958},
  note = {Section 2.2.2}
}

% ============================================
% SIMULATED ANNEALING
% ============================================

@article{kirkpatrick1983,
  author = {Kirkpatrick, S. and Gelatt, C. D. and Vecchi, M. P.},
  title = {Optimization by simulated annealing},
  journal = {Science},
  year = {1983},
  note = {Section 2.3.2}
}

% ============================================
% GPU COMPUTING (CRITICAL)
% ============================================

@article{fujimoto2011,
  author = {Fujimoto, N. and ...},
  title = {GPU-accelerated distance matrix computation},
  journal = {...},
  year = {2011},
  note = {Section 2.5 - PRIMARY GPU REFERENCE}
}
```

---

## ⏱️ **TIME BUDGET SUMMARY**

| Activity | Time Estimate |
|----------|---------------|
| **Tier 1 Reading (Essential)** | 4-6 hours |
| **Tier 2 Reading (Important)** | 3-4 hours |
| **Tier 3 Reading (Optional)** | 2-3 hours |
| **Writing Section 2** | 13-18 hours |
| **Bibliography Management** | 2 hours |
| **Review and Editing** | 2-3 hours |
| **TOTAL** | 26-36 hours |

**Spread over 2 weeks:**

- Week 1 (pre-implementation): 12-15 hours (reading + outline)
- Week 3 (post-implementation): 14-21 hours (writing + polishing)

---

## 🚀 **NEXT STEPS**

1. **Locate refs.bib file** or create one with Tier 1 papers
2. **Download PDF copies** of Tier 1 papers (Fujimoto, Kirkpatrick, SA survey)
3. **Create `literature_notes/` directory** for reading notes
4. **Start with Fujimoto et al.** (most relevant to GPU implementation)
5. **Extract GPU vectorization strategies** before starting MVP coding

---

**Status:** Plan complete, ready to begin systematic literature review
