# TCC Project Tracking Document

**Project:** GPU-Accelerated Heuristics for Vehicle Routing Problems  
**Student:** Lucas Galdino  
**Institution:** UFSC  
**Timeline:** 2-3 weeks implementation + 1 week documentation  
**Last Updated:** 2025-10-16
---

## 🎯 **PROJECT SCOPE DEFINITION (FINAL)**

### **What This TCC IS:**

- ✅ **Primary Focus:** CPU vs GPU performance comparison for routing heuristics
- ✅ **Core Algorithms:** Nearest Neighbor + 2-opt + OR-opt + Simulated Annealing
- ✅ **Backend:** Simple `xp = cupy if use_gpu else numpy` abstraction
- ✅ **Instances:** 5-8 carefully selected CVRP/TSP instances via Routing_data
- ✅ **Contribution:** Demonstrating GPU acceleration potential for local search operators

### **What This TCC IS NOT:**

- ❌ Comprehensive algorithm catalog (Christofides, MST, 3-opt, etc.)
- ❌ Enterprise-level modular framework with protocols/interfaces
- ❌ Statistical Ph.D.-level analysis (30+ runs per instance)
- ❌ Custom TSPLIB95 parser implementation (use Routing_data)
- ❌ Support for all 10+ distance calculation types
- ❌ JIRA integration, 80% test coverage, formal CI/CD

---

## 📋 **KEY DECISIONS MADE**

| Decision | Rationale | Date |
|----------|-----------|------|
| Use Routing_data for instances | Already handles JSON/DuckDB, multiple formats | 2025-10-16 |
| Skip TSPLIB95 library | Routing_data provides cleaner interface | 2025-10-16 |
| Focus on 2-opt + Or-opt | Highly parallelizable, well-documented | 2025-10-16 |
| ONE metaheuristic (SA) | SA + 2-opt is standard, sufficient for TCC | 2025-10-16 |
| 5-8 instances total | Enough to show scaling trend, fits 20-30min presentation | 2025-10-16 |
| Simple xp backend | No protocol architecture - just numpy/cupy swap | 2025-10-16 |
| Skip small instances (<100 nodes) | GPU overhead dominates, focus on 100+ for advantage | 2025-10-16 |

---

## 🔬 **EXPERIMENTAL DESIGN (SIMPLIFIED FOR TCC)**

### **Research Question:**
>
> "How much speedup does GPU acceleration provide for local search operators in routing problems, and does it maintain solution quality?"

### **Hypothesis:**

- GPU provides 6-8x speedup for instances with n > 500 nodes
- Solution quality remains identical (same algorithm logic)
- Speedup scales with problem size (larger = better GPU advantage)

### **Instances (5-8 total):**

| Instance | Size | Type | Purpose |
|----------|------|------|---------|
| kroA100 | 100 | TSP | Small baseline |
| ch130 | 130 | TSP | Medium (GPU starts helping) |
| kroA200 | 200 | TSP | Medium-large |
| rat783 | 783 | TSP | Large (significant speedup expected) |
| A-n65-k9 | 65 | CVRP | CVRP baseline |
| E-n76-k10 | 76 | CVRP | CVRP medium |
| P-n101-k4 | 101 | CVRP | CVRP large |

**Total: 7 instances** (4 TSP + 3 CVRP)

### **Algorithms to Implement:**

| Algorithm | Type | Purpose |
|-----------|------|---------|
| Nearest Neighbor | Construction | Generate initial solution (CPU only) |
| 2-opt First Improvement | Local Search | Baseline improvement heuristic (CPU + GPU) |
| Or-opt | Local Search | Alternative operator (CPU + GPU) |
| SA + 2-opt | Metaheuristic | Hybrid approach (CPU + GPU) |

**Total: 4 algorithms** (1 construction + 3 improvement)

### **Metrics:**

**Primary (Essential):**

- Runtime (seconds)
- Speedup (GPU_time / CPU_time)
- Solution quality (tour length)
- Quality validation (CPU solution == GPU solution)

**Secondary (Nice-to-have):**

- Iterations per second
- Memory usage (GPU VRAM)

### **Experimental Procedure:**

```python
for instance in instances:
    # 1. Load instance from Routing_data
    problem = load_instance(instance_name)
    
    # 2. Generate initial solution (CPU)
    initial_solution = nearest_neighbor(problem)
    
    # 3. CPU improvement
    cpu_start = time.time()
    cpu_solution = improve_with_2opt(initial_solution, backend='numpy')
    cpu_time = time.time() - cpu_start
    
    # 4. GPU improvement (same initial solution)
    gpu_start = time.time()
    gpu_solution = improve_with_2opt(initial_solution, backend='cupy')
    gpu_time = time.time() - gpu_start
    
    # 5. Validate
    assert abs(cpu_solution.cost - gpu_solution.cost) < 1e-6
    
    # 6. Report
    speedup = cpu_time / gpu_time
    print(f"{instance}: CPU={cpu_time:.2f}s, GPU={gpu_time:.2f}s, Speedup={speedup:.2f}x")
```

**Runs per instance:**

- Deterministic algorithms (2-opt): 1 run (same result every time)
- Stochastic (SA): 10 runs with different seeds (sufficient for TCC)

---

## 📊 **RESULTS PRESENTATION PLAN**

### **Tables:**

**Table 1: Instance Characteristics**

| Instance | Nodes | Type | Best Known | Source |
|----------|-------|------|------------|--------|
| kroA100 | 100 | TSP | 21282 | TSPLIB |
| ... | ... | ... | ... | ... |

**Table 2: Runtime Comparison**

| Instance | CPU (s) | GPU (s) | Speedup | Quality Match |
|----------|---------|---------|---------|---------------|
| kroA100 | 2.4 | 0.8 | 3.0x | ✓ |
| ... | ... | ... | ... | ... |

**Table 3: Solution Quality**

| Instance | Initial | CPU Final | GPU Final | Gap to Best Known |
|----------|---------|-----------|-----------|-------------------|
| kroA100 | 25000 | 21500 | 21500 | 1.02% |
| ... | ... | ... | ... | ... |

### **Graphs:**

1. **Speedup vs Problem Size:** Line plot showing GPU advantage scales with n
2. **Quality vs Time:** Convergence curves for SA (10 runs, show mean ± std)
3. **Comparison Bar Chart:** CPU vs GPU runtime for all instances side-by-side

---

## 🚀 **IMPLEMENTATION PLAN (2-3 WEEKS)**

### **Week 1: MVP (Core Functionality)**

**Day 1-2 (12-16 hours):**

- [ ] Setup: Install Routing_data, test data loading
- [ ] Implement Nearest Neighbor construction heuristic (CPU)
- [ ] Implement distance matrix calculation
- [ ] Test on kroA100, ch130

**Day 3-4 (12-16 hours):**

- [ ] Implement 2-opt (CPU version with NumPy)
- [ ] Implement 2-opt (GPU version with CuPy) - vectorized
- [ ] Basic runtime comparison on 2 instances
- [ ] Validate: CPU solution == GPU solution

**Day 5 (6-8 hours):**

- [ ] Test on remaining 5 instances
- [ ] Generate initial results table
- [ ] Checkpoint: Can answer "Does GPU provide speedup?"

### **Week 2: Complete Implementation**

**Day 6-7 (12-16 hours):**

- [ ] Implement Or-opt operator (CPU + GPU)
- [ ] Implement Simulated Annealing framework
- [ ] SA + 2-opt hybrid (CPU + GPU)

**Day 8-9 (12-16 hours):**

- [ ] Run complete experiments (all instances, all algorithms)
- [ ] Collect data: runtimes, solution quality, speedups
- [ ] Generate all tables and graphs

**Day 10 (6-8 hours):**

- [ ] Code cleanup and documentation
- [ ] Validate all results
- [ ] Write Materiais e Métodos section

### **Week 3: Documentation & Analysis**

**Day 11-12 (12-16 hours):**

- [ ] Write Revisão Bibliográfica
- [ ] Write Resultados section with tables/graphs
- [ ] Write Discussão section

**Day 13-14 (12-16 hours):**

- [ ] Write Introdução and Conclusão
- [ ] Review and polish entire document
- [ ] Generate final PDF

**Day 15 (6-8 hours):**

- [ ] Prepare presentation (20-30min)
- [ ] Practice presentation
- [ ] Final review

---

## ❓ **OPEN QUESTIONS TO RESOLVE**

### **Technical:**

1. ~~Should we use TSPLIB95 library?~~ **RESOLVED:** No, use Routing_data
2. ~~How many algorithms to implement?~~ **RESOLVED:** 4 total (1 construction + 3 improvement)
3. ~~How many instances to test?~~ **RESOLVED:** 5-8 instances
4. **TODO:** What SA parameters to use? (initial temp, cooling schedule)
5. **TODO:** What stopping criteria for 2-opt? (no improvement or max iterations?)

### **Methodological:**

1. **TODO:** Literature review - which 2-3 papers to focus on?
   - Suggested: fujimoto2011highly (GPU distance matrix), tsp_gpu papers
2. **TODO:** How to present vectorization strategy in document? (Appendix or main text?)
3. **TODO:** Statistical analysis needed? (mean ± std for SA is sufficient?)

### **Presentation:**

1. **TODO:** What are the 3-4 key slides for 20-30min presentation?
2. **TODO:** What demo to show? (live GPU vs CPU comparison?)

---

## 📚 **LITERATURE REVIEW TODO**

**Priority Papers (Read first - 2-3 hours):**

1. Fujimoto et al. (2011) - GPU-accelerated distance matrix calculation
2. TSP GPU implementation papers - vectorization strategies
3. Simulated Annealing surveys - parameter tuning guidelines

**Supporting References:**

- Clarke & Wright (1964) - Original savings algorithm
- Lin & Kernighan (1973) - Local search foundations
- Kirkpatrick et al. (1983) - Original SA paper

---

## 🎓 **TCC REQUIREMENTS CHECKLIST**

From `roteiro_analise_critica.md`:

- [ ] **Problema posto:** Routing problems are computationally expensive, GPU acceleration underexplored
- [ ] **Questão a responder:** How much speedup does GPU provide while maintaining quality?
- [ ] **Objetivos claros:** See section 1.2 of first_draft.md
- [ ] **Revisão bibliográfica:** 2-3 key papers + supporting references
- [ ] **Materiais e métodos:** Hardware specs, algorithms, instances, experimental procedure
- [ ] **Resultados válidos:** Multiple instances, quality validation, speedup measurements
- [ ] **Discussão:** Analysis of GPU advantage, scaling behavior, limitations
- [ ] **Conclusão:** Summary of findings, future work recommendations

---

## 🔄 **RISK MITIGATION**

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GPU memory overflow (>4GB) | Medium | High | Limit to n<1000 instances, use chunked processing |
| CuPy installation issues | Low | High | ~~Already resolved~~ ✓ |
| Algorithm correctness bugs | Medium | High | Validate against known solutions, CPU==GPU check |
| Time overrun | Medium | Medium | MVP-first approach, cut SA if needed |
| Poor GPU speedup | Low | Medium | Focus on large instances (n>500) where advantage is clear |

---

## 📈 **SUCCESS METRICS**

**Minimum Viable Success (Pass TCC):**

- ✅ 4 algorithms implemented (1 construction + 3 improvement)
- ✅ 5 instances tested
- ✅ GPU provides >3x speedup on large instances
- ✅ Solution quality matches CPU
- ✅ 50+ page document with methodology and results

**Target Success (Good Grade):**

- ✅ All 7 instances tested
- ✅ GPU provides 6-8x speedup on n>500
- ✅ Clear scaling trend demonstrated
- ✅ 55-60 page document with complete analysis
- ✅ Professional presentation with graphs

**Stretch Success (Excellence):**

- ✅ Additional algorithm (SA with Or-opt)
- ✅ Comparison on more powerful GPU (if available)
- ✅ Published code repository with documentation
- ✅ Conference paper submission potential

---

## 📝 **NEXT IMMEDIATE ACTIONS**

1. **TODO (Today):**
   - Read fujimoto2011highly paper (2 hours)
   - Download 7 instances from Routing_data
   - Verify instances load correctly

2. **TODO (Tomorrow):**
   - Implement Nearest Neighbor construction heuristic
   - Test on kroA100 and ch130
   - Verify initial solution quality

3. **TODO (Day 3):**
   - Implement 2-opt CPU version
   - Implement 2-opt GPU version
   - First speedup comparison

---

## 🎯 **PROJECT MOTTO**

> **"Focus on ONE clear contribution (GPU acceleration) with solid experimental validation. Everything else is secondary."**

---

**Document Version:** 1.0  
**Status:** Scoping Complete, Ready for Implementation
