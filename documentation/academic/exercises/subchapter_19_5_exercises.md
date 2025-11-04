---
title: "Chapter 19.5 Exercises: Set-Partitioning and Column Generation"
subtitle: "Exercises, proofs, and GPU-accelerated implementations"
author: "TCC Research Project - GPU-Accelerated Optimization"
date: "September 2025"
marimo-version: 0.16.1
academic-context: "Exact Methods & Mathematical Programming"
keywords: ["set_partitioning","column_generation","convergence_analysis","dynamic_programming","GPU"]
---

# Chapter 19.5 Exercises - Set-Partitioning and Column Generation

> **Executive Summary**: Section 19.5 presents advanced exercises that reinforce understanding of set-partitioning formulations, column generation techniques, and convergence analysis for VRP optimization. These exercises bridge theoretical concepts with practical implementation challenges, covering convergence rate analysis, formulation extensions, and connections to combinatorial optimization.

---

## references

- [19.1–19.5 summary](../../subchapters_summary/195_Exercises_deep_summary.md)
- [Chapter 19 deep summary](../../subchapters_summary/19_Chapter_deep_summary.md)
- [complete textbook](../../complete_textbook_markdown)

---

## 🔷 Exercise 19.1: Convergence Rate Analysis

**Problem Statement**: Prove upper bound on convergence rate $E[Z^*] \leq E[Z_{LP}] + O(n^{3/4})$.

**Theoretical Foundation**: Extension of Theorem 19.4.1 proof techniques to establish finite-sample convergence rates.

```python
def gpu_convergence_rate_analysis(vrp_instance, discretization_levels, backend='cupy'):
    """Analyze convergence rates for set-partitioning formulation."""
    if backend == 'cupy':
        import cupy as cp
        n_customers = len(vrp_instance['customers'])
        convergence_analysis = []
        for k in discretization_levels:
            delta = 1.0 / k
            discretized_problem = create_discretized_vrp_gpu(vrp_instance, delta, backend)
            lp_solution = solve_lp_relaxation_gpu(discretized_problem, backend)
            probabilistic_bounds = estimate_probabilistic_bounds_gpu(discretized_problem, k, backend)
            theoretical_rate = compute_theoretical_convergence_rate_gpu(n_customers, k, probabilistic_bounds, backend)
            convergence_analysis.append({'discretization_level': k, 'theoretical_bound': theoretical_rate})
        return {'convergence_analysis': convergence_analysis}

```

---

## 🔷 Exercise 19.2: Prize-Collecting TSP Formulation

**Problem Statement**: Formulate PCTSP as longest-path problem in augmented network.

**Mathematical Transformation**: Given graph $G = (V, E)$ with edge costs $c_{ij}$ and vertex penalties $\pi_i$, PCTSP minimizes:

$$\min \left\{ \sum_{(i,j) \in \text{tour}} c_{ij} + \sum_{i \notin \text{tour}} \pi_i \right\}$$

```python
def gpu_pctsp_to_longest_path_transformation(pctsp_instance, backend='cupy'):
    """Transform Prize-Collecting TSP to longest-path problem."""
    if backend == 'cupy':
        import cupy as cp
        vertices = pctsp_instance['vertices']
        edge_costs = pctsp_instance['edge_costs']
        vertex_penalties = pctsp_instance['vertex_penalties']
        n_vertices = len(vertices)
        augmented_vertices = list(vertices) + ['source', 'sink'] + [f'penalty_{i}' for i in vertices]
        n_augmented = len(augmented_vertices)
        augmented_adjacency = cp.full((n_augmented, n_augmented), -cp.inf)
        for i in range(n_vertices):
            for j in range(n_vertices):
                if i != j and (i, j) in edge_costs:
                    augmented_adjacency[i, j] = -edge_costs[(i, j)]
        source_idx = n_vertices
        for i in range(n_vertices):
            augmented_adjacency[source_idx, i] = 0
        return {'augmented_network': {'adjacency_matrix': augmented_adjacency}}

```

---

## 🔷 Exercise 19.3: Bin-Packing Set-Covering Formulation

**Problem Statement**: Express bin-packing as set-covering problem.

**Mathematical Framework**: Let $\mathcal{F} = \{S : \sum_{i \in S} w_i \leq 1\}$ be collection of all feasible item subsets.

Set-covering formulation:
$$\min \sum_{S \in \mathcal{F}} y_S$$
$$\sum_{S \in \mathcal{F}} \alpha_{iS} y_S \geq 1, \quad \forall i = 1, 2, \ldots, n$$

```python
def gpu_bin_packing_set_covering_analysis(bin_packing_instance, backend='cupy'):
    """Analyze bin-packing through set-covering formulation."""
    if backend == 'cupy':
        import cupy as cp
        item_weights = cp.array(bin_packing_instance['item_weights'])
        bin_capacity = bin_packing_instance['bin_capacity']
        n_items = len(item_weights)
        feasible_subsets = generate_feasible_subsets_gpu(item_weights, bin_capacity, backend)
        covering_matrix = build_covering_matrix_gpu(feasible_subsets, n_items, backend)
        return {'set_covering_formulation': {'feasible_subsets': feasible_subsets, 'covering_matrix': covering_matrix}}

```

---

## 🔷 Exercise 19.4: Dynamic Programming Equivalence

**Problem Statement**: For dynamic program (19.6), prove $f = g$ where:

- $f = \min_{i \in N} \min_{w_i \leq q \leq Q} f_q(i)$
- $g_q(i) = \min_{w_i \leq q' \leq q} \{f_{q'}(i) + f_{q-q'+w_i}(i)\}$

**Proof Strategy**: Apply Bellman's optimality principle to both formulations.

---

## 🔷 Exercise 19.5: Two-Loop Avoidance in Dynamic Programming

**Problem**: Develop DP procedure for column generation avoiding two-loops (patterns like ...i, j, i...).

**Algorithm Design**: Track last visited customer in state representation and maintain forbidden customer sets.

---

## 🔷 Exercise 19.6: Time Window Constraints in Column Generation

**Problem**: Develop DP procedure for column generation with time windows.

**Enhanced DP Formulation**: State definition (position, time, capacity_used) with recursion:

$$f(i, t, q) = \min\{c_{ji} + f(j, t + s_j + t_{ji}, q + w_i)\}$$

subject to: $t + s_j + t_{ji} \in [e_i, l_i]$

---

## 🔷 Exercise 19.7: Distance Constraints in Column Generation

**Problem**: Develop DP for column generation with maximum route distance constraints.

**DP with Distance Tracking**: State (position, remaining_capacity, remaining_distance) with transition:

$$f(i, q, d) = \min\{c_{ji} + f(j, q - w_i, d - d_{ji})\}$$

---

## 🔷 Exercise 19.8: VRPTW Integrality Gap Analysis

**Problem**: Construct VRPTW instance where fractional and integer LP solutions don't converge asymptotically.

**Construction Strategy**: Design geometric structure and time windows to create persistent LP relaxation gaps.

---

## Conclusion

Section 19.5 exercises provide essential reinforcement of set-partitioning theory and practice, bridging mathematical foundations with computational implementation challenges. The exercises develop comprehensive understanding of exact VRP methods while highlighting connections to broader combinatorial optimization theory.

**Next steps**: Implement GPU tests for convergence rate validation and formulation comparisons.
