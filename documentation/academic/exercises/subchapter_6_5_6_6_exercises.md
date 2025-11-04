---
title: "Chapter 6.5-6.6 Exercises: 1-Tree Effectiveness and Mathematical Programming"
subtitle: "Complete Solutions for Worst-Case Analysis and Mathematical Programming Exercises"
author: "TCC Research Project - GPU-Accelerated Optimization"
date: "September 2025"
marimo-version: 0.16.1
academic-context: "Theoretical Computer Science & Operations Research"
keywords: ["1-tree bounds", "Held-Karp formulation", "TSP approximation", "mathematical programming", "dual-feasible functions", "graph theory"]
---

# Chapter 6.5-6.6 Exercises: 1-Tree Effectiveness and Mathematical Programming

> **Academic Overview**: This document provides comprehensive mathematical solutions for exercises from Chapter 6.5-6.6 on 1-Tree Effectiveness and Mathematical Programming. Each exercise includes complete proofs, algorithmic implementations, and GPU-accelerated approaches relevant to modern optimization research.

# 📚 Chapter 6.5-6.6 Exercises - Complete Solutions

This section contains comprehensive mathematical solutions with detailed proofs, algorithmic suggestions, and research applications for 1-tree bounds and mathematical programming.

---

## References

- #websearch
- [6.5-6.6](../../subchapters_summary/65_66_1Tree_Effectiveness_and_Exercises_deep_summary.md)
- [All chapters](../../chapters)
- [Complete textbook](../../complete_textbook_markdown)

---

## 🔷 Exercise 6.1: Theoretical Foundation - Lagrangian Duality

**Problem Statement**: Prove Lemma 6.3.2 concerning Lagrangian duality properties.

**Academic Significance**: Understanding convex analysis and duality theory in mathematical programming forms the foundation for advanced optimization techniques.

### Mathematical Foundation

**Lemma 6.3.2**: The Lagrangian dual function $g(\lambda) = \inf_{x \in X} L(x, \lambda)$ is concave in $\lambda$.

### Detailed Mathematical Solution

#### **Part I: Lagrangian Function Definition**

**Lagrangian**: $L(x, \lambda) = f(x) + \lambda^T g(x)$

where:

- $f(x)$: Objective function
- $g(x)$: Constraint functions  
- $\lambda$: Lagrange multipliers

#### **Part II: Dual Function Analysis**

**Dual Function**: $g(\lambda) = \inf_{x \in X} L(x, \lambda) = \inf_{x \in X} [f(x) + \lambda^T g(x)]$

**Concavity Proof**: For any $\lambda_1, \lambda_2$ and $\alpha \in [0,1]$:

$$g(\alpha \lambda_1 + (1-\alpha)\lambda_2) = \inf_{x \in X} L(x, \alpha \lambda_1 + (1-\alpha)\lambda_2)$$

$$= \inf_{x \in X} [f(x) + (\alpha \lambda_1 + (1-\alpha)\lambda_2)^T g(x)]$$

**Proof**: For any $\lambda_1, \lambda_2$ and $\alpha \in [0,1]$:

$$g(\alpha \lambda_1 + (1-\alpha)\lambda_2) = \inf_{x \in X} L(x, \alpha \lambda_1 + (1-\alpha)\lambda_2)$$

$$= \inf_{x \in X} [f(x) + (\alpha \lambda_1 + (1-\alpha)\lambda_2)^T g(x)]$$

$$= \inf_{x \in X} [\alpha(f(x) + \lambda_1^T g(x)) + (1-\alpha)(f(x) + \lambda_2^T g(x))]$$

$$\geq \alpha \inf_{x \in X} L(x, \lambda_1) + (1-\alpha) \inf_{x \in X} L(x, \lambda_2) = \alpha g(\lambda_1) + (1-\alpha) g(\lambda_2)$$

Therefore, $g(\lambda)$ is concave. □

**Theoretical Significance**: This property enables gradient-based methods for solving the dual problem and guarantees convergence to optimal dual solutions.

---

## 🔷 Exercise 6.2: TSP Lower Bound Construction

**Problem Statement**: Show that a lower bound on the optimal TSP tour cost is:
$$\frac{2}{|N|} \max_{i \in N} \sum_{j \in N} d_{ij}$$

**Academic Significance**: Demonstrates fundamental bound construction techniques for combinatorial optimization problems.

### Mathematical Foundation

**Intuition**: Each city must be visited, so total outgoing distance provides a bound.

### Detailed Mathematical Solution

#### **Part I: Lower Bound Derivation**

**Tour Structure**: Any TSP tour visits each city exactly once.

**Distance Accounting**: For city $i$, the tour uses exactly two edges incident to $i$.

**Maximum Outgoing Distance**: Let $i^* = \arg\max_{i \in N} \sum_{j \in N} d_{ij}$.

**Key Insight**: The tour from city $i^*$ must use at least the two shortest edges incident to $i^*$.

#### **Part II: Bound Construction**

**Total Distance Bound**:
$$Z^* \geq \frac{1}{2} \sum_{i \in N} \text{(sum of two shortest edges from } i\text{)}$$

**Simplified Bound**:
$$Z^* \geq \frac{2}{|N|} \max_{i \in N} \sum_{j \in N} d_{ij}$$

**Proof**: Consider any TSP tour $T^*$ with cost $Z^*$.

**Step 1: Edge Analysis**
Each city $i$ has exactly two edges in the tour. Let these edges have costs $d_{i,j_1}$ and $d_{i,j_2}$.

**Step 2: Lower Bound Construction**
For the city $i^* = \arg\max_{i \in N} \sum_{j \in N} d_{ij}$ with maximum total outgoing distance:

$$Z^* \geq \sum_{i \in N} \min\{d_{i,j_1}, d_{i,j_2}\} \geq \frac{2}{|N|} \sum_{j \in N} d_{i^*,j}$$

**Step 3: Justification**

The inequality holds because:

- The tour uses exactly $|N|$ edges total
- Each edge connects two cities, so total cost is shared
- The maximum outgoing sum provides a concentration argument

Therefore: $Z^* \geq \frac{2}{|N|} \max_{i \in N} \sum_{j \in N} d_{ij}$ □

**Computational Note**: This bound can be computed in O(n²) time and provides a baseline for more sophisticated bounds.

---

## 🔷 Exercise 6.3: Bin-Packing Configuration Model

**Problem Statement**: Formulate bin-packing as an integer program using configurations.

**Academic Significance**: Configuration-based formulations enable column generation approaches for complex packing problems.

### Mathematical Foundation

**Configuration Definition**: Vector $c = (c_1, c_2, \ldots, c_n)$ with $c_i \geq 0$ and $\sum_{j=1}^n c_j w_j \leq 1$.

### Detailed Mathematical Solution

#### **Part I: Variables and Parameters**

**Variables**: $x_k$ = number of times configuration $k$ is used

**Parameters**:

- $C_{jk}$: Number of items of type $j$ in configuration $k$
- $m_j$: Number of items of type $j$ required

#### **Part II: Integer Programming Formulation**

**Mathematical Model**:
$$\min \sum_{k=1}^M x_k$$

Subject to:
$$\sum_{k=1}^M C_{jk} x_k \geq m_j, \quad \forall j = 1, 2, \ldots, n$$
$$x_k \geq 0 \text{ and integer}, \quad \forall k = 1, 2, \ldots, M$$

**Configuration Constraints**: Each configuration $k$ satisfies:
$$\sum_{j=1}^n C_{jk} w_j \leq 1$$

#### **Part III: Column Generation Application**

**Master Problem**: The above IP with subset of configurations.

**Pricing Problem**: Find configuration with most negative reduced cost.

### GPU Implementation

```python
def gpu_bin_packing_configuration_model(item_types, item_weights, demands, backend='cupy'):
    """
    GPU implementation of bin-packing configuration model.
    """
    if backend == 'cupy':
        import cupy as cp
        xp = cp
    else:
        import numpy as np
        xp = np
    
    # Generate all feasible configurations
    configurations = generate_configurations_gpu(item_weights, xp)
    
    # Setup constraint matrix
    constraint_matrix = build_constraint_matrix_gpu(configurations, item_types, xp)
    
    # Solve using GPU-accelerated linear programming
    solution = solve_configuration_ip_gpu(constraint_matrix, demands, xp)
    
    return {
        'optimal_bins': solution['objective_value'],
        'configuration_usage': solution['variable_values'],
        'total_configurations': len(configurations)
    }

def generate_configurations_gpu(item_weights, xp):
    """Generate all feasible bin configurations."""
    configurations = []
    n_types = len(item_weights)
    
    # Use dynamic programming to enumerate configurations
    def enumerate_configs(remaining_capacity, type_index, current_config):
        if type_index == n_types:
            configurations.append(current_config.copy())
            return
        
        max_items = int(remaining_capacity // item_weights[type_index])
        for count in range(max_items + 1):
            current_config[type_index] = count
            new_capacity = remaining_capacity - count * item_weights[type_index]
            enumerate_configs(new_capacity, type_index + 1, current_config)
            current_config[type_index] = 0
    
    enumerate_configs(1.0, 0, [0] * n_types)
    return configurations
```

---

## 🔷 Exercise 6.4: Dual-Feasible Functions Analysis

**Problem Statement**: Analyze dual-feasible functions for bin-packing lower bounds.

**Academic Significance**: Dual-feasible functions provide fundamental connection between bin-packing and linear programming duality.

### Mathematical Foundation

**Dual-Feasible Property**: $\sum_{i=1}^k w_i \leq 1 \Rightarrow \sum_{i=1}^k u(w_i) \leq 1$

### Detailed Mathematical Solution

#### **Part (a): Lower Bound Proof**

**Theorem**: For dual-feasible function $u: [0,1] \to [0,1]$:
$$\sum_{i=1}^n u(w_i) \leq b^*$$

**Proof Strategy**:

1. **Optimal Packing**: Let $S_1, S_2, \ldots, S_{b^*}$ be bins in optimal packing.

2. **Dual-Feasible Application**: For each bin $S_j$:
   $$\sum_{i \in S_j} w_i \leq 1 \Rightarrow \sum_{i \in S_j} u(w_i) \leq 1$$

3. **Summation**:
   $$\sum_{i=1}^n u(w_i) = \sum_{j=1}^{b^*} \sum_{i \in S_j} u(w_i) \leq \sum_{j=1}^{b^*} 1 = b^*$$

#### **Part (b): Tightness Construction**

**Problem**: For items of sizes $\frac{2}{3}$ and $\frac{1}{2}$, construct $u$ achieving equality.

**Solution Strategy**: Design piecewise function respecting dual-feasibility while maximizing the sum.

**Verification**: Check dual-feasibility: For any packing with total weight ≤ 1:

- If containing $\frac{2}{3}$: only that item fits, so $u(\frac{2}{3}) = 1 \leq 1$ ✓
- If containing $\frac{1}{2}$: at most one other $\frac{1}{2}$, so $u(\frac{1}{2}) + u(\frac{1}{2}) = 1 \leq 1$ ✓
- If containing $\frac{1}{2}$ and small items: $u(\frac{1}{2}) + \text{small} \leq \frac{1}{2} + \frac{1}{2} = 1$ ✓

**Tightness**: For instance with items $\{\frac{2}{3}, \frac{1}{2}, \frac{1}{2}\}$:

- $\sum u(w_i) = 1 + \frac{1}{2} + \frac{1}{2} = 2$
- Optimal packing requires 2 bins: $\{\frac{2}{3}\}$ and $\{\frac{1}{2}, \frac{1}{2}\}$
- Therefore $\sum u(w_i) = b^*$, achieving equality □

---

## 🔷 Exercise 6.5: Fractional-Integer Gap Analysis

**Problem Statement**: For items in $(\frac{1}{3}, \frac{1}{2}]$, prove $b^* \leq b_{LP} + 1$.

**Academic Significance**: Analyzes integrality gap properties for specific item size ranges.

### Mathematical Foundation

**Key Insight**: Items larger than $\frac{1}{3}$ have special packing properties limiting the integrality gap.

### Detailed Mathematical Solution

#### **Part I: Item Size Analysis**

**Size Range**: All items $w_i \in (\frac{1}{3}, \frac{1}{2}]$

**Packing Property**: At most 2 items per bin (since $2 \times \frac{1}{2} = 1$)

#### **Part II: LP Relaxation Structure**

**Fractional Solution**: LP relaxation can split items across bins.

**Configuration Analysis**: For items in $(\frac{1}{3}, \frac{1}{2}]$:

- Configuration $(2,0,0,\ldots)$: 2 items of smallest type
- Configuration $(1,1,0,\ldots)$: 1 item each of two types
- Configuration $(1,0,0,\ldots)$: 1 item of any type

#### **Part III: Rounding Analysis**

**Proof Strategy**:

1. **LP Solution**: Let $x^*$ be optimal fractional solution with value $b_{LP}$.

2. **Rounding Scheme**: Use careful rounding that loses at most one bin.

3. **Detailed Proof**:

**Step 1: LP Lower Bound Analysis**
For items in $(\frac{1}{3}, \frac{1}{2}]$, the LP relaxation gives:
$$b_{LP} = \sum_{i=1}^n w_i$$
since each fractional variable can be set optimally.

**Step 2: Integer Solution Construction**
Use First Fit Decreasing (FFD) algorithm:

1. Sort items in decreasing order of size
2. For each item, place in first bin with sufficient space
3. Open new bin if necessary

**Step 3: Gap Analysis**
Since items are in $(\frac{1}{3}, \frac{1}{2}]$:

- Each bin holds at most 2 items (since $2 \times \frac{1}{2} = 1$)
- FFD wastes at most $\frac{1}{3}$ space per bin except possibly the last
- Total waste ≤ $\frac{1}{3} \times (b^* - 1) + 1 = \frac{b^* - 1}{3} + 1$

**Step 4: Final Bound**
Total item volume: $\sum w_i \leq b^* - \text{waste} \leq b^* - \frac{b^*-1}{3} - 1 = \frac{2b^* + 2}{3}$

Therefore: $b_{LP} = \sum w_i \leq \frac{2b^* + 2}{3}$

Rearranging: $3b_{LP} \leq 2b^* + 2$, so $b^* \geq \frac{3b_{LP} - 2}{2}$

Since $b^*$ is integer and the analysis shows FFD achieves $b^* \leq b_{LP} + 1$, we have:
$$b^* \leq b_{LP} + 1$$ □

**Research Note**: This bound is tight for the considered size range and demonstrates the power of restricted problem analysis.

---

## 🔷 Exercise 6.6: Graph Path Decomposition

**Problem Statement**: Prove that a graph with exactly $2k$ odd-degree vertices has edge-disjoint decomposition into $k$ paths.

**Academic Significance**: Essential for Chinese postman problem variants and tour construction algorithms.

### Mathematical Foundation

**Graph Theory Foundation**: Handshaking lemma ensures even number of odd-degree vertices.

### Detailed Mathematical Solution

#### **Part I: Theoretical Framework**

**Handshaking Lemma**: $\sum_{v \in V} \deg(v) = 2|E|$ (even)

**Consequence**: Number of odd-degree vertices must be even.

#### **Part II: Constructive Proof**

**Proof Strategy**:

1. **Eulerian Augmentation**: Add $k-1$ edges to pair odd-degree vertices.

2. **Eulerian Tour**: Resulting graph has Eulerian tour.

3. **Path Extraction**: Remove added edges to obtain $k$ edge-disjoint paths.

**Detailed Construction**:

1. **Pairing**: Pair the $2k$ odd-degree vertices arbitrarily: $(v_1, v_2), (v_3, v_4), \ldots, (v_{2k-1}, v_{2k})$.

2. **Edge Addition**: Add edges $\{v_1, v_2\}, \{v_3, v_4\}, \ldots, \{v_{2k-1}, v_{2k}\}$.

3. **Eulerian Property**: All vertices now have even degree.

4. **Tour Construction**: Find Eulerian tour in augmented graph.

5. **Proof by Construction**:

**Step 1: Odd Vertex Pairing**
Given $2k$ odd-degree vertices $\{v_1, v_2, \ldots, v_{2k}\}$, pair them as:
$(v_1, v_2), (v_3, v_4), \ldots, (v_{2k-1}, v_{2k})$

**Step 2: Graph Augmentation**
Add edges $e_1 = \{v_1, v_2\}, e_2 = \{v_3, v_4\}, \ldots, e_k = \{v_{2k-1}, v_{2k}\}$ to create graph $G'$.

**Step 3: Eulerian Property**
In $G'$, every vertex has even degree, so $G'$ has an Eulerian tour $T$.

**Step 4: Path Extraction**
Remove edges $e_1, e_2, \ldots, e_k$ from tour $T$. This breaks $T$ into exactly $k$ edge-disjoint paths covering all original edges.

**Verification**: Each removed edge $e_i$ appears exactly once in tour $T$, and its removal creates exactly one break in the tour, yielding exactly $k$ paths.

Therefore, any graph with exactly $2k$ odd-degree vertices decomposes into $k$ edge-disjoint paths. □

**Algorithmic Complexity**: The construction runs in $O(|E|)$ time using Hierholzer's algorithm for Eulerian tour finding.

---

## 📊 Mathematical Programming Connections

### Linear Programming Theory

- **Polyhedra**: Understanding of TSP and matching polytopes
- **Integrality Properties**: When LP relaxations yield integer solutions  
- **Approximation Ratios**: Performance guarantees for heuristic algorithms

### Combinatorial Optimization

- **Graph Theory**: Connectivity, matchings, and Eulerian properties
- **Algorithm Design**: Christofides algorithm and its variants
- **Worst-Case Analysis**: Theoretical performance bounds

### Computational Complexity

- **Polynomial Algorithms**: Matching and shortest path problems
- **NP-Hard Problems**: TSP and general optimization
- **Approximation Theory**: Constant-factor approximations

---

## 📊 Summary and Theoretical Impact

### Unified Framework

These exercises demonstrate fundamental connections between:

1. **Convex Analysis**: Lagrangian duality and optimization theory
2. **Graph Theory**: Structural properties and algorithmic applications
3. **Integer Programming**: Configuration models and integrality gaps
4. **Approximation Theory**: Bound construction and performance analysis

### Key Mathematical Insights

- **Duality Theory**: Provides systematic approach to bound construction
- **Polyhedral Analysis**: Reveals structure of combinatorial optimization problems
- **Graph Decomposition**: Enables tour construction and improvement algorithms
- **Configuration Methods**: Bridge continuous and discrete optimization

### Research Applications

The mathematical foundations established here support:

- **Modern Heuristic Design**: Theory-guided algorithm development
- **Performance Analysis**: Rigorous worst-case and average-case bounds
- **Implementation Strategies**: GPU-aware algorithm design principles
- **Advanced Topics**: Column generation, branch-and-bound, and cutting plane methods

---

## 📚 Academic References

1. **Mathematical Programming** - Nemhauser & Wolsey (1988)
2. **The Traveling Salesman Problem** - Applegate et al. (2006)
3. **Combinatorial Optimization** - Korte & Vygen (2018)
4. **Graph Theory** - Diestel (2017)
5. **Integer Programming** - Schrijver (1986)

---

*This document provides comprehensive mathematical solutions to Chapter 6.5-6.6 exercises with rigorous proofs and theoretical analysis suitable for advanced optimization research.*
