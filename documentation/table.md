# Algorithm Summary Tables

## Overview

These tables provide a comprehensive classification of solver methodologies for **Bin Packing** and **TSP/VRP** problems, with special emphasis on **GPU parallelizability** for the project's acceleration goals. The tables distinguish between construction heuristics (build solutions from scratch), improvement heuristics (refine existing solutions), exact algorithms, and hybrid/metaheuristic methods.

This consolidated reference includes algorithms from multiple sources including:

- Classical algorithms (Johnson et al., Lin-Kernighan, etc.)
- Simchi-Levi et al. "The Logic of Logistics" (2014)
- Modern metaheuristics and GPU-accelerated variants

### Key GPU Parallelization Insights

**Very High Parallelizability (Ideal for GPU):**

- **MATCH** (Bin Packing): Parallel sorting + parallel pairing operations
- **Region-Partitioning** (TSP): Divide-and-conquer with independent subproblems
- **k-opt Local Search** (TSP): Embarrassingly parallel neighborhood evaluation
- **Memetic Algorithms** (TSP): Population-based parallelism (each individual independent)
- **Strips Method** (TSP): Independent strip processing
- **Held-Karp DP** (TSP): Parallel state computation at each stage

**High Parallelizability:**

- **Clarke-Wright** (VRP): Parallel savings computation + parallel route merging
- **Location-Based** (VRP): Partition-based with independent route solving

**Moderate Parallelizability:**

- **FFD/BFD** (Bin Packing): Parallel sorting, sequential packing
- **MST Heuristic** (TSP): Parallel MST construction (Borůvka's algorithm)
  > [!note] Add the algorithms reference url
  > Search the paper which this algorithm is proposed (the url)
- **Christofides'** (TSP): Limited by sequential matching phase
- **Harmonic H(M)** (Bin Packing): Parallel partitioning, semi-sequential packing

**Low/No Parallelizability:**

- **Online algorithms** (NF, FF, BF): Inherently sequential decision-making
- **Nearest Insertion** (TSP): Sequential tour growth
- **Nearest Neighbor** (TSP): Sequential tour construction (multi-start is parallelizable)

---

## **Bin Packing Algorithms**

This table classifies bin packing algorithms with emphasis on online vs. offline models, GPU parallelization potential, and practical applications.

| Method Name | Author(s) / Year | Method Family | Core Paradigm | Key Subroutine(s) | Problem Model | Deterministic? | GPU Parallelizability | Complexity | Performance Guarantee | Strengths | Weaknesses | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Next-Fit (NF)** | Johnson et al. / 1974 | Construction Heuristic | Greedy | None (single bin check) | Online | Yes | **None** (Inherently sequential) | $O(n)$ | Worst-Case Ratio: 2.0 | **Fastest possible heuristic** with minimal memory (only one open bin). | Very poor solution quality; extremely inefficient packing. | **True Streaming Data:** When memory is severely constrained and decisions must be instant (e.g., simple hardware). |
| **First-Fit (FF)** | Johnson et al. / 1974 | Construction Heuristic | Greedy | Bin Search (Linear Scan or Tree) | Online | Yes | **Low** (Bin search parallelizable, updates sequential) | $O(n \log n)$ | Worst-Case Ratio: ~1.7 | Simple and fast; much better quality than Next-Fit. | Makes shortsighted decisions that create wasted space. | General-purpose online packing where speed is important. |
| **Best-Fit (BF)** | Johnson et al. / 1974 | Construction Heuristic | Greedy | Bin Search (Linear Scan or Tree) | Online | Yes | **Low** (Bin search parallelizable, updates sequential) | $O(n \log n)$ | Worst-Case Ratio: ~1.7 | Tries to preserve large gaps for future large items. | Can be tricked into leaving spaces that are "too perfect," preventing better global arrangements. | **Dynamic Memory Allocation**, where preserving large contiguous blocks is a primary goal. |
| **First-Fit Decreasing (FFD)** | Johnson et al. / 1974 | Construction Heuristic | Greedy + Sorting | **Sorting** | **Offline** | Yes | **Medium** (Sorting: High; Packing: Low) | $O(n \log n)$ | Worst-Case Ratio: **1.5**; Asymptotically Optimal | **Excellent balance of speed and quality**; asymptotically optimal on average. | Requires all items to be known in advance for sorting. | **The industry standard** for most practical offline packing tasks (e.g., loading trucks). |
| **Best-Fit Decreasing (BFD)** | Johnson et al. / 1974 | Construction Heuristic | Greedy + Sorting | **Sorting**, Bin Search | **Offline** | Yes | **Medium** (Sorting: High; Packing: Low) | $O(n \log n)$ | Worst-Case Ratio: **1.5**; Asymptotically Optimal | Similar performance to FFD; slightly different bin selection logic. | Minimal practical advantage over FFD. | Alternative to FFD when preserving larger gaps is theoretically preferred. |
| **MATCH** | Coffman, Lueker / 1991 | Construction Heuristic | Pairing | **Sorting**, Two-Pointer Scan | **Offline** | Yes | **Very High** (Both sorting and pairing parallelizable) | $O(n \log n)$ | Worst-Case Ratio: ~1.5; **Asymptotically Optimal** | Provably **asymptotically optimal** on average; elegant theoretical properties; **pairing phase is data-parallel**. | Less commonly implemented in practice compared to simpler FFD. | Academic study; **excellent GPU candidate**: parallel sort + parallel pairing. |
| **Harmonic $H(M)$** | Lee, Lee / 1985 | Construction Heuristic | Size Partitioning | Item Partitioning by Size Classes, First-Fit | **Offline** | Yes | **Medium** (Parallel partitioning, semi-sequential packing within classes) | $O(n \log n)$ | Worst-Case Ratio: Bounded (~1.69 for large $M$) | Mathematically elegant; provides theoretical bounds on bin packing constant $\gamma$. | Complex parameter tuning; not optimal in practice. | **Theoretical analysis tool**; establishes asymptotic bounds for bin packing. |
| **SIP(r)** | Simchi-Levi et al. / 2014 | Construction Heuristic | Size Partitioning | Item Partitioning (by size) | **Offline** | Yes | **High** (Partitions are independent) | $O(n \log n)$ | **Unbounded** worst-case | Mathematically simple, making it easy to analyze average-case behavior. | Terrible practical performance; rigid and inefficient. | A **theoretical tool for proofs**; used to establish bounds on bin-packing constant $\gamma$. |

---

## **TSP & VRP Algorithms**

This table details TSP/VRP methods, organized by problem type (TSP vs. VRP) and solution approach (construction, improvement, exact, metaheuristic).

### **TSP Construction Heuristics**

| Method Name | Author(s) / Year | Method Family | Core Paradigm | Key Subroutine(s) | Problem Model | Deterministic? | GPU Parallelizability | Complexity | Performance Guarantee | Strengths | Weaknesses | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Nearest Neighbor (NN)** | Classic / N/A | Construction Heuristic | Greedy | Linear Scan (for nearest) | Online-like | Yes (depends on start) | **Low-Medium** (Multi-start parallelizable; distance calculations parallel) | $O(n^2)$ | Unbounded | Extremely simple to implement and understand. | Very poor quality; highly sensitive to starting point. | **Educational:** Canonical example of a flawed greedy strategy. **GPU: Parallel multi-start NN**. |
| **MST Heuristic** | Classic / N/A | Construction Heuristic | Graph Conversion | MST Algorithm, Eulerian Tour, Shortcutting | **Offline** | Yes | **Medium** (Parallel MST algorithms exist: Borůvka's) | $O(n^2)$ | Worst-Case Ratio: **2.0** | Simple graph-based logic; provides worst-case guarantee. | Can produce very inefficient tours on certain geometries. | Educational; baseline for graph-based TSP heuristics. **GPU: Parallel MST (Borůvka's)**. |
| **Strips Method** | Karp, Steele / 1985 | Construction Heuristic | Geometric Partitioning | Point Sorting, Zigzag Traversal | **Offline** | Yes | **Very High** (Sorting parallel; strip traversals independent) | $O(n \log n)$ | No constant worst-case ratio; Avg-case $\approx 1.16 \beta_{TSP}$ | Simple geometric logic; **highly parallelizable**; used to establish upper bounds on $\beta_{TSP}$. | Not competitive in quality with other heuristics. | **Theoretical Tool & GPU Demo:** Used in proofs about TSP constant $\beta_{TSP}$. |
| **Nearest Insertion (NI)** | Rosenkrantz et al. / 1977 | Construction Heuristic | Incremental | Find Closest Pair, Find Best Insertion | **Offline** | Yes | **Low** (Sequential tour growth; distance matrix parallel) | $O(n^2)$ | Worst-Case Ratio: **2.0** | Intuitive "growing loop" logic; solid worst-case guarantee. | Sensitive to early insertion choices; **tour construction sequential**. | Generate **high-quality initial solution** for metaheuristics. **GPU: Limited to distance preprocessing**. |
| **Christofides' Algorithm** | Christofides / 1976 | Construction Heuristic | Graph Reinforcement | MST, **Min-Weight Perfect Matching**, Eulerian Tour, Shortcutting | **Offline** | Yes | **Medium** (MST parallel; matching low; tour sequential) | $O(n^3)$ | Worst-Case Ratio: **1.5** | **Best-known worst-case ratio** for polynomial-time construction heuristic. | $O(n^3)$ complexity from matching is bottleneck; **matching hard to parallelize**. | **High-Value Strategic Problems** where solution quality is paramount (e.g., VLSI design). |
| **Region-Partitioning** | Karp / 1977 | Construction Heuristic | Divide & Conquer | Geometric Partitioning, **Exact TSP Solver (Held-Karp)**, Tour Stitching | **Offline** | Yes | **Very High** (Recursive partitioning embarrassingly parallel; subproblems independent) | $O(n \log n)$ | No constant worst-case ratio; **Asymptotically Optimal** (avg-case) | Provably converges to optimal for random data; **exceptionally parallelizable**. | High implementation overhead; worse than simpler heuristics on small/medium instances. | **Academic Research & GPU Showcase:** Foundational algorithm for very large-scale TSPs ($n > 10,000$). |

### **TSP Exact Algorithm**

| Method Name | Author(s) / Year | Method Family | Core Paradigm | Key Subroutine(s) | Problem Model | Deterministic? | GPU Parallelizability | Complexity | Performance Guarantee | Strengths | Weaknesses | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dynamic Programming (Held-Karp)** | Held, Karp / 1962 | **Exact Algorithm** | Dynamic Programming | Bitmasking, Memoization, State Computation | **Offline** | Yes | **Medium-High** (Parallel state computation at each DP stage) | $O(n^2 2^n)$ | **Optimal** (Ratio = 1.0) | **Finds provably optimal solution**; best-known exact algorithm for TSP. | Exponential complexity limits to ~20-25 cities practically; enormous memory requirements. | **Small TSP instances** requiring guaranteed optimality; **GPU: Parallel DP state evaluation**. |

### **VRP Construction Heuristics**

| Method Name | Author(s) / Year | Method Family | Core Paradigm | Key Subroutine(s) | Problem Model | Deterministic? | GPU Parallelizability | Complexity | Performance Guarantee | Strengths | Weaknesses | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Clarke-Wright Savings** | Clarke, Wright / 1964 | Construction Heuristic | Route Merging | Savings Calculation, Route Merging | **Offline** | Yes | **High** (Parallel savings computation; parallel merge evaluation) | $O(n^2 \log n)$ | No formal worst-case ratio | Classic VRP heuristic; intuitive savings-based logic; **well-suited for GPU**. | Greedy merging can miss better global solutions; quality depends on problem structure. | **Standard VRP baseline**; widely used in practice. **GPU: Multiple parallel implementations exist**. |
| **Location-Based Heuristic** | Bramel, Simchi-Levi / 1995 | Construction Heuristic | Partition + Solve | Customer Partitioning, Per-Partition Route Solving | **Offline** | Yes | **High** (Partitions solved independently) | Varies (depends on partition solver) | Asymptotically optimal (certain distributions) | General framework for routing; **partition independence enables parallelism**; theoretical guarantees. | Requires careful partition strategy; quality depends on partition quality. | **General routing framework**; academic tool for proving asymptotic bounds. **GPU: Natural partition parallelism**. |

### **TSP/VRP Improvement Heuristics & Metaheuristics**

| Method Name | Author(s) / Year | Method Family | Core Paradigm | Key Subroutine(s) | Problem Model | Deterministic? | GPU Parallelizability | Complexity | Performance Guarantee | Strengths | Weaknesses | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **k-opt (2-opt, 3-opt)** | Lin, Kernighan / 1965+ | **Improvement Heuristic** | Local Search | Neighborhood Generation (edge swaps) | **Offline** | Yes | **Very High** (Neighborhood evaluation embarrassingly parallel) | $O(n^2)$ for 2-opt, $O(n^3)$ for 3-opt | None (Local Optimum) | Very fast at finding local optimum; **neighborhood search is data-parallel**. | Gets stuck in first local optimum; no global perspective. | The **workhorse operator** in almost all modern metaheuristics. **GPU: Massively parallel neighborhood evaluation**. |
| **Guided Local Search (GLS)** | Voudouris, Tsang / 1998 | **Metaheuristic** | Guided Search | Local Search Operator (e.g., 2-opt), Penalty Updates | **Offline** | Typically Yes | **High** (Inherits parallelism from local search; penalty calculations parallel) | High (Varies) | None | Excellent at escaping local optima by penalizing solution features. | Performance depends on underlying local search operator quality. | **Strategic 'brain'** wrapped around improvement heuristic for powerful global search. |
| **Memetic Algorithm** | Moscato / 1989 | **Hybrid Method** | Evolutionary + Local Search | Genetic Operators (Crossover, Selection), Local Search (e.g., k-opt) | **Offline** | **No** (Stochastic) | **Very High** (Population embarrassingly parallel; each individual independent) | High (Varies) | None | **State-of-the-art performance** combining global exploration (GA) with local exploitation (k-opt). | Complex to implement; many parameters to tune. | **High-Performance Optimization:** Top-tier choice for near-optimal solutions. **GPU: Ideal for population parallelism**. |

---

## Notes

**¹ GPU Parallelizability Ratings:**

- **None**: Inherently sequential; no parallelization possible
- **Low**: Minor components can be parallelized (e.g., distance calculations)
- **Medium**: Significant portions parallelizable but key phases remain sequential
- **High**: Most operations parallelizable with some sequential coordination
- **Very High**: Embarrassingly parallel or naturally parallel structure (ideal for GPU)

**² Complexity:**

- $n$ = number of items (bin packing) or cities/customers (TSP/VRP)
- Complexities listed are for standard implementations; GPU versions may have different characteristics

**³ Performance Guarantees:**

- Worst-case ratios shown are for approximation quality relative to optimal
- "Asymptotically Optimal" means converges to optimal as problem size grows (for certain distributions)
- "Unbounded" means no constant-factor worst-case guarantee exists
