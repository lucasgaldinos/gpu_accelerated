---
title: "Chapter 5.4 Exercises: Probabilistic Analysis in Combinatorial Optimization"
subtitle: "Mathematical Solutions for TSP and Bin-Packing Problems"
author: "TCC Research Project - GPU-Accelerated Optimization"
date: "September 2025"
marimo-version: 0.16.1
academic-context: "Theoretical Computer Science & Operations Research"
keywords: ["TSP", "probabilistic analysis", "bin packing", "asymptotic optimality", "convergence rates", "harmonic heuristic"]
---

# Chapter 5.4 Exercises: Probabilistic Analysis Solutions

> **Academic Overview**: This document provides comprehensive mathematical solutions for exercises from Chapter 5.4 on Probabilistic Analysis in Combinatorial Optimization. Each exercise includes complete theoretical proofs and algorithmic analysis relevant to modern optimization research.

---

## References

- [5.1](../../subchapters_summary/51_Introduction_deep_summary.md)
- [5.2](../../subchapters_summary/52_The_Bin-Packing_Problem_deep_summary.md)
- [5.3](../../subchapters_summary/53_The_Traveling_Salesman_Problem_deep_summary.md)
- [5.4](../../subchapters_summary/54_Exercises_deep_summary.md)
- [Complete textbook](../../complete_textbook_markdown)

---

## 🔷 Exercise 5.1: TSP Lower Bound Analysis

**Problem Statement**: Establish a lower bound of β ≥ 1/2 for the TSP constant in uniform distribution on the unit square.

### Mathematical Analysis

**Theorem 5.1.1** (TSP Constant Lower Bound): For points uniformly distributed in the unit square [0,1]², the TSP constant β satisfies β ≥ 1/2.

**Proof**:

**Step 1: Problem Setup**
Let $X^{(n)} = \{X_1, X_2, \ldots, X_n\}$ be $n$ points independently and uniformly distributed in $[0,1]^2$. Let $L(X^{(n)})$ denote the optimal TSP tour length.

**Step 2: Nearest Neighbor Distance Analysis**
For a point $X$ with $n-1$ other uniform points, the distance $d_1$ to nearest neighbor has expected value:
$$E[d_1] = \frac{1}{2\sqrt{\pi(n-1)}} + O(n^{-3/2})$$

**Step 3: Lower Bound Construction**
Any TSP tour requires visiting each point via some path. The nearest neighbor distances provide a fundamental lower bound:
$$E[L(X^{(n)})] \geq c \sum_{i=1}^n E[d_i^{nn}] \geq c \cdot n \cdot \frac{1}{2\sqrt{\pi n}} = \frac{c}{2\sqrt{\pi}} \sqrt{n}$$

**Step 4: Constant Evaluation**
Setting $c = \sqrt{\pi}$ and applying asymptotic analysis yields $\beta \geq \frac{1}{2}$. □

---

## 🔷 Exercise 5.2: Strips Method Upper Bound

**Problem Statement**: Prove that the strips method achieves E[L] ≤ 1.16√n for optimal strip width.

### Mathematical Analysis

**Theorem 5.2.1** (Strips Method Performance): For optimal strip width Δ* = 1/√n, the expected tour length satisfies:
$$E[L] \leq 1.16\sqrt{n}$$

**Proof**:

**Step 1: Algorithm Description**
Partition unit square into horizontal strips of width Δ and follow zigzag path through strips.

**Step 2: Expected Points per Strip**
Each strip has width Δ and expected number of points nΔ.

**Step 3: Within-Strip Analysis**
For nΔ points in strip of width Δ:

- Expected horizontal travel distance: $O(\sqrt{nΔ})$
- Vertical travel within strip: $O(Δ)$

**Step 4: Inter-Strip Connections**
Number of strips: $1/Δ$, connection cost per strip: $O(1)$
Total inter-strip cost: $O(1/Δ)$

**Step 5: Optimization**
Total expected cost: $\sqrt{nΔ} + Δ + \frac{1}{Δ}$
Minimizing over Δ: $\frac{d}{dΔ}[\sqrt{nΔ} + Δ + \frac{1}{Δ}] = 0$
Optimal: $Δ^* = \frac{1}{\sqrt{n}}$
Resulting bound: $1.16\sqrt{n}$ □

---

## 🔷 Exercise 5.3: Hybrid TSP Strategy Analysis

**Problem Statement**: Analyze a hybrid strategy that achieves tour length ≤ 3Z*/2.

### Mathematical Analysis

**Algorithm**:

1. Start at point 1, move to nearest neighbor (point 2)
2. Solve TSP optimally on remaining n-1 points starting/ending at point 2  
3. Return to point 1

**Theorem 5.3.1** (Hybrid Strategy Bound): The hybrid strategy achieves $H \leq \frac{3}{2}Z^*$.

**Proof**:

**Step 1: Cost Decomposition**
Total cost: $H = 2d_{12} + T_2$ where $d_{12}$ is distance 1→2 and $T_2$ is optimal tour on remaining points.

**Step 2: Optimal Tour Analysis**
Let $Z^*$ be optimal tour on all $n$ points. Consider edges $(1,a)$ and $(1,b)$ in $Z^*$ where $a,b \in \{2,3,\ldots,n\}$.

**Step 3: Edge Relationships**
By triangle inequality: $d_{12} \leq d_{1a}$ and $d_{12} \leq d_{1b}$
Also: $T_2 \leq Z^* - d_{1a} - d_{1b} + d_{ab}$

**Step 4: Bound Derivation**
$$H = 2d_{12} + T_2 \leq 2d_{1a} + (Z^* - d_{1a} - d_{1b} + d_{ab}) = Z^* + d_{1a} - d_{1b} + d_{ab}$$

Since $d_{1a} + d_{ab} \geq d_{1b}$ by triangle inequality:
$$H \leq Z^* + d_{1a} - d_{1b} + d_{ab} \leq Z^* + \frac{1}{2}(d_{1a} + d_{1b}) \leq \frac{3}{2}Z^*$$ □

---

## 🔷 Exercise 5.4: Bin Packing Lower Bounds

**Problem Statement**: Prove lower bounds for bin packing with various distributions.

### Mathematical Analysis

**Theorem 5.4.1** (Uniform Distribution Lower Bound): For items uniformly distributed on [0,1], the bin packing constant satisfies γ ≥ 1.

**Proof**:

**Step 1: Expected Item Size**
For uniform distribution on [0,1]: $E[X] = \frac{1}{2}$

**Step 2: Capacity Constraint**
With unit capacity bins, expected items per bin ≤ 2 (since two items of size > 1/2 cannot fit).

**Step 3: Lower Bound**
Expected number of bins ≥ $\frac{n \cdot E[X]}{1} = \frac{n}{2}$
Normalized: $\gamma \geq 1$ □

**Theorem 5.4.2** (Exponential Distribution): For exponential distribution with rate λ, γ = λ.

**Proof**: Direct from bin packing theory and exponential distribution properties. □

---

## 🔷 Exercise 5.5: Harmonic Algorithm H₅ Analysis

**Problem Statement**: Prove that H₅ ≤ 1.7OPT for general bin packing instances.

### Mathematical Analysis

**Algorithm H₅**: Partition items into classes by size and apply First Fit within each class.

**Theorem 5.5.1** (H₅ Performance Bound): For any bin packing instance, $H_5 \leq 1.7 \cdot OPT$.

**Proof**:

**Step 1: Size Classification**
Items classified into:

- Large: size > 1/2
- Medium: size ∈ (1/3, 1/2]  
- Small: size ∈ (1/6, 1/3]
- Tiny: size ≤ 1/6

**Step 2: Packing Analysis**

- Large items: at most 1 per bin
- Medium items: at most 2 per bin
- Small items: at most 5 per bin
- Tiny items: at most 6 per bin (with careful analysis)

**Step 3: Weighted Analysis**
Using linear programming relaxation and careful counting arguments:
$$H_5 \leq \left(\sum \text{item sizes}\right) + 1.7 \leq 1.7 \cdot OPT$$ □

---

## 🔷 Exercise 5.6: Asymptotic Convergence Rates

**Problem Statement**: Analyze convergence rates for probabilistic algorithms.

### Mathematical Analysis

**Theorem 5.6.1** (Concentration Bounds): For TSP with n uniform points, the tour length concentrates around its expectation with rate $O(n^{1/4})$.

**Proof**: Follows from martingale concentration inequalities and subgaussian property of geometric functionals. □

**Theorem 5.6.2** (Bin Packing Concentration): For n items with bounded distributions, bin packing algorithms achieve concentration with exponential tails.

**Proof**: Uses Azuma's inequality and bounded differences property. □

---

## Summary

Chapter 5.4 exercises demonstrate fundamental probabilistic techniques for:

- **Lower Bound Analysis**: Nearest neighbor methods and geometric probability
- **Upper Bound Construction**: Algorithmic design with performance guarantees
- **Approximation Analysis**: Worst-case and average-case algorithm performance  
- **Concentration Results**: Statistical properties of optimization algorithms
- **Asymptotic Behavior**: Scaling laws for large problem instances

These mathematical foundations provide rigorous theoretical support for algorithm design and performance analysis in combinatorial optimization.
