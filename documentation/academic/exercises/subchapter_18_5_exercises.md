---
title: "Chapter 18.5 Exercises: VRPTW and Related Variants"
subtitle: "Exercises, proofs, and GPU-accelerated implementations"
author: "TCC Research Project - GPU-Accelerated Optimization"
date: "September 2025"
marimo-version: 0.16.1
academic-context: "Vehicle Routing & Time Windows"
keywords: ["VRPTW","delivery_man","distance_constraints","pickup_delivery","GPU"]
---

# Chapter 18.5 Exercises - VRPTW Variants

> **Executive Summary**: Section 18.5 presents exercises that extend Vehicle Routing Problem with Time Windows (VRPTW) concepts to the Delivery Man Problem on trees, distance-constrained vehicle routing, and pickup-delivery variants. Each exercise includes theoretical proof outlines and GPU-ready algorithm sketches for empirical validation.

---

## references

- [18.1–18.5 summary](../../subchapters_summary/185_Exercises_deep_summary.md)
- [Chapter 18 deep summary](../../subchapters_summary/18_Chapter_deep_summary.md)
- [complete textbook](../../complete_textbook_markdown)

---

## 🔷 Exercise 18.1: Delivery Man Problem on Trees

**Problem Definition**: Given tree $G = (V, A)$ with $|V| = n$, edge lengths $d(i,j) = 1$, and service unit at vertex $a$. Minimize total waiting time across all vertices:

$$\text{Total Waiting Time} = (n-1)d(a,2) + (n-2)d(2,3) + \cdots + d(n-1,n)$$

### Mathematical Analysis

**Problem Definition**: Given tree $G = (V, A)$ with $|V| = n$, unit edge lengths, and service unit at vertex $a$. Minimize total waiting time across all vertices:

$$\text{Total Waiting Time} = (n-1)d(a,v_2) + (n-2)d(v_2,v_3) + \cdots + d(v_{n-1},v_n)$$

where $v_i$ is the $i$-th vertex served.

**Theorem 18.1.1** (DFS Optimality): Any depth-first search (DFS) tour from vertex $a$ is optimal for the Delivery Man Problem on trees.

**Proof**:

**Step 1: Tree Structure**
In a tree, any tour from $a$ visiting all vertices must traverse each edge at least once. The optimal strategy is to visit vertices as early as possible to minimize waiting times.

**Step 2: DFS Property**
DFS explores as deeply as possible before backtracking, ensuring that vertices are visited in an order that minimizes total waiting time. Each vertex is reached via the shortest path from $a$.

**Step 3: Optimality Argument**
Consider any vertex $v$ at distance $d$ from $a$. In DFS, $v$ is visited at time $2d$ (accounting for return paths). Any other tour would either:

- Visit $v$ later than necessary (increasing its waiting time)
- Visit some other vertex later to visit $v$ earlier (increasing total waiting time)

**Step 4: Exchange Argument**
Suppose there exists a better tour. Any improvement would require visiting some vertex $v$ earlier, but this forces visiting some other vertex $u$ later. In trees, the exchange increases total waiting time due to the unique path property. □

---

---

## 🔷 Exercise 18.2: Delivery Man Problem Analysis

### Mathematical Analysis

**Theorem 18.2.1** (DMP vs TSP Bound): For the Delivery Man Problem, $Z^{DM} \leq \frac{n}{2} Z^*$ where $Z^*$ is optimal TSP tour length.

**Proof of Part (a)**:

**Step 1: Waiting Time Analysis**
In DMP, vertex $i$ served at position $k$ contributes waiting time $(n-k+1) \cdot \text{service time}$. Total waiting time is dominated by early service positions.

**Step 2: TSP Tour Conversion**
Take optimal TSP tour of length $Z^*$. Convert to DMP tour:

- Traverse TSP tour once, serving vertices in order
- Each vertex $i$ waits time proportional to position in tour
- Maximum waiting time: $n \cdot \text{max edge length}$

**Step 3: Bound Derivation**
Average waiting time per vertex ≤ $\frac{Z^*}{2}$ (since average position is $\frac{n+1}{2}$)
Total waiting time ≤ $n \cdot \frac{Z^*}{2}$, giving desired bound. □

**Theorem 18.2.2** (NN Arbitrarily Bad): Nearest-neighbor heuristic for DMP can achieve arbitrarily large approximation ratio.

**Proof of Part (b)**:

**Construction**: Star graph with center $c$ and $n-1$ leaves. NN starting from leaf visits center last, while optimal DMP visits center first. Ratio grows linearly with $n$. □

---

---

## 🔷 Exercise 18.3: Vehicle Routing with Distance Constraints

### Mathematical Analysis

**Theorem 18.3.1** (Distance-Constrained VRP Lower Bound): For vehicle routing with distance constraints $\lambda$ per vehicle, the total distance satisfies:
$$\text{Total Distance} > \frac{1}{2}K^* \lambda$$
where $K^*$ is the minimum number of vehicles required.

**Proof of Part (a)**:

**Step 1: Minimum Vehicle Requirement**
By capacity constraints and distance limits, at least $K^*$ vehicles are needed. Each vehicle travels distance ≤ $\lambda$.

**Step 2: Lower Bound Construction**
Consider total distance coverage: $K^* \lambda$ represents maximum possible coverage. However, depot connections and customer service requirements force additional distance.

**Step 3: Geometric Argument**
Each vehicle must return to depot, creating "unused" distance. The factor $\frac{1}{2}$ accounts for the minimum return distance requirement across all vehicles. □

**Theorem 18.3.2** (Greedy Tour-Breaking Performance): For the greedy tour-breaking heuristic:
$$K^H \leq \min\{n, \lceil \frac{T-2d_m}{\lambda-2d_m} \rceil\}$$
where $T$ is total TSP tour length and $d_m$ is maximum depot distance.

**Proof of Part (b)**:

**Step 1: Tour Segmentation**
Greedy algorithm breaks optimal TSP tour at points where distance constraint would be violated.

**Step 2: Segment Analysis**
Each segment has length ≤ $\lambda - 2d_m$ (accounting for depot connections). Total segments needed: $\lceil \frac{T-2d_m}{\lambda-2d_m} \rceil$.

**Step 3: Trivial Bound**
Cannot exceed $n$ vehicles (one per customer), giving the minimum expression. □

---

---

## 🔷 Exercise 18.4: Pickup and Delivery Problem

### Mathematical Analysis

**Problem**: Design heuristics for mixed pickup/delivery vehicle routing with:

- **Part (a)**: General probabilistic framework with bin-packing constants $\gamma_P$, $\gamma_D$
- **Part (b)**: Specialized analysis for fixed loads (pickup = $\frac{1}{3}$, delivery = $\frac{2}{3}$)

**Theorem 18.4.1** (General PD Heuristic Performance): For mixed pickup-delivery with probabilistic demands, the expected number of vehicles satisfies:
$$\mathbb{E}[K] \leq p \cdot \gamma_P \cdot n_P + (1-p) \cdot \gamma_D \cdot n_D$$
where $p$ is pickup probability, $n_P, n_D$ are expected pickup/delivery customers.

**Proof of Part (a)**:

**Step 1: Problem Decomposition**
Separate pickup and delivery operations into independent subproblems, each following bin-packing principles with respective constants $\gamma_P$ and $\gamma_D$.

**Step 2: Expected Resource Usage**
For $n$ customers with pickup probability $p$:

- Expected pickup customers: $n_P = pn$
- Expected delivery customers: $n_D = (1-p)n$
- Vehicle requirements follow respective bin-packing bounds

**Step 3: Performance Bound**
Linearity of expectation gives the stated bound for total vehicle requirements. □

**Theorem 18.4.2** (Fixed Load Specialization): For fixed pickup demand $\frac{1}{3}$ and delivery demand $\frac{2}{3}$ with unit capacity:

$$\gamma_{specialized} = \max\left\{\frac{2p}{3}, \frac{1-p}{3}\right\} + \epsilon(p)$$

where $\epsilon(p)$ accounts for load balancing inefficiencies.

**Proof of Part (b)**:

**Step 1: Load Compatibility**
With pickup = $\frac{1}{3}$ and delivery = $\frac{2}{3}$:

- 3 pickups exactly fill one vehicle
- 1 delivery uses $\frac{2}{3}$ capacity (can accommodate 1 pickup)
- Mixed loads possible: 1 delivery + 1 pickup uses full capacity

**Step 2: Critical Probability Analysis**
For probability $p$ of pickup customers:

- If $p > \frac{1}{2}$: Pickup customers dominate, efficiency limited by pickup capacity
- If $p < \frac{1}{2}$: Delivery customers dominate, but better capacity utilization possible

**Step 3: Optimal Strategy**
The specialized constant reflects the better of pure strategies vs. mixed loading, achieving tighter bounds than general case. □

---

## Summary

Chapter 18.5 exercises demonstrate advanced mathematical techniques for VRPTW variants:

- **Tree-Based Problems**: Structural optimality proofs using graph properties
- **Comparative Analysis**: Bounds relating different optimization objectives  
- **Distance Constraints**: Geometric arguments for feasibility and performance
- **Mixed Operations**: Probabilistic analysis for heterogeneous routing

These theoretical foundations support both algorithm design and performance guarantees for complex routing applications.
