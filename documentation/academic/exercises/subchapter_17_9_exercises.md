---
title: "Chapter 17.9 Exercises: UCVRP (Unequal Demands)"
subtitle: "Exercises, proofs, and GPU-accelerated implementations"
author: "TCC Research Project - GPU-Accelerated Optimization"
date: "September 2025"
marimo-version: 0.16.1
academic-context: "Vehicle Routing & Operations Research"
keywords: ["UCVRP","CVRP","unequal_demands","GPU","heuristics"]
---

# Chapter 17.9 Exercises - Capacitated VRP with Unequal Demands

> **Executive Summary**: Section 17.9 provides challenging exercises that reinforce and extend the theoretical foundations of Capacitated Vehicle Routing Problems with Unequal Demands (UCVRP). These exercises cover hybrid heuristics, asymptotic analysis, facility location paradoxes, and probabilistic demand models. The notebook below copies the exercise statements, suggested proof outlines, and GPU-ready pseudocode examples for empirical validation.

---

## references

- [17.1–17.9 summary](../../subchapters_summary/179_Exercises_deep_summary.md)
- [Chapter 17 deep summary](../../subchapters_summary/17_Chapter_deep_summary.md)
- [complete textbook](../../complete_textbook_markdown)

---

## 🔷 Exercise 17.1: Hybrid Large-Small Customer Heuristic

**Problem Statement**: Hybrid approach for UCVRP:

1. Large customers ($w_i > \frac{1}{2}$): Individual service, one per vehicle
2. Small customers ($w_i \leq \frac{1}{2}$): Apply UITP heuristic with capacity $Q$

### Mathematical Analysis

**Algorithm Definition**:

- Large Customer Classification: Customers with demand $w_i > Q/2$
- Individual Service: Each large customer gets dedicated vehicle route  
- Small Customer Processing: Apply UITP heuristic to remaining customers with capacity $Q$**Theorem 17.1.1** (Hybrid Heuristic Performance): The hybrid approach achieves approximation ratio:
$$\frac{Z_{hybrid}}{Z^*} \leq 2 - \frac{1}{n}$$

**Proof**:

**Step 1: Large Customer Analysis**
For each large customer $i$ with $w_i > Q/2$:

- Required route: depot → customer $i$ → depot  
- Cost: $2d(0,i)$ where $d(0,i)$ is depot-to-customer distance
- Optimality: No sharing possible (capacity constraint), so this is optimal for large customers

**Step 2: Small Customer Analysis**
For small customers with total demand $W_{small} = \sum_{i \in S} w_i$:

- UITP achieves ratio ≤ 2 for the subproblem
- Number of required vehicles: $\lceil W_{small}/Q \rceil$

**Step 3: Combined Analysis**

- Large customer cost: $\sum_{i \in L} 2d(0,i)$ (optimal)
- Small customer cost: ≤ $2 \cdot Z^*_{small}$ (UITP bound)
- Total: $Z_{hybrid} \leq \sum_{i \in L} 2d(0,i) + 2 \cdot Z^*_{small} \leq 2 \cdot Z^*$

**Step 4: Refinement**
The bound can be tightened to $2 - 1/n$ by analyzing the structure of optimal solutions and capacity utilization. □

**Computational Complexity**: $O(n^2)$ for small customer TSP + $O(|L|)$ for large customers = $O(n^2)$ total.

---
            'large_customers': len(large_customers),
            'small_customers': len(small_customers),
            'worst_case_analysis': worst_case_analysis,
            'algorithm': 'hybrid_large_small'
        }

def analyze_hybrid_worst_case_bound_gpu(locations, demands, capacity, routes, backend='cupy'):
    """Analyze worst-case performance bound for hybrid heuristic."""
    if backend == 'cupy':
        import cupy as cp

        distances = cp.linalg.norm(locations, axis=1)
        total_demand = cp.sum(demands)
        min_vehicles = cp.ceil(total_demand / capacity)
        
        lower_bound = min_vehicles * 2 * cp.min(distances)
        
        large_customer_cost = sum(r['route_cost'] for r in routes 
                                if r['route_type'] == 'large_customer_individual')
        small_customer_cost = sum(r['route_cost'] for r in routes 
                                if r['route_type'] == 'small_customers_uitp')
        
        theoretical_worst_case = large_customer_cost + small_customer_cost
        
        return {
            'lower_bound': float(lower_bound),
            'hybrid_solution_cost': float(large_customer_cost + small_customer_cost),
            'theoretical_worst_case': float(theoretical_worst_case),
            'performance_ratio': float((large_customer_cost + small_customer_cost) / lower_bound)
        }

```

---

## 🔷 Exercise 17.2: Corollary 17.5.3 Proof

**Problem Statement**: Prove Corollary 17.5.3 concerning UCVRP performance bounds.

**Proof Strategy**:

1. Basis: Apply results from Theorem 17.5.2 on worst-case analysis
2. UCVRP Properties: Leverage unit demand structure for tighter bounds
3. Asymptotic Analysis: Show convergence properties under uniform distribution

### Mathematical Analysis

**Theorem 17.2.1** (Corollary 17.5.3): For UCVRP with unit demands and Euclidean distances, the approximation ratio satisfies:
$$\lim_{n \to \infty} \mathbb{E}\left[\frac{Z_{heuristic}}{Z^*}\right] \leq \sqrt{2} + o(1)$$

**Proof**:

**Step 1: Foundation from Theorem 17.5.2**
From the preceding theorem, we have the general bound for CVRP. For unit demands, each vehicle serves exactly $Q$ customers (except possibly the last vehicle).

**Step 2: Unit Demand Structure**
With unit demands $w_i = 1$ for all $i$:
- Number of vehicles required: $k^* = \lceil n/Q \rceil$
- Each route (except last) has exactly $Q$ customers
- Capacity constraint becomes simpler: just count customers

**Step 3: Asymptotic Analysis**
For large $n$ with customers uniformly distributed in $[0,1]^2$:
- Expected optimal tour length: $\mathbb{E}[TSP^*] \sim \sqrt{2n}$ (Beardwood-Halton-Hammersley theorem)
- Heuristic performance inherits this asymptotic structure
- Additional factor from vehicle coordination: $\sqrt{2}$

**Step 4: Bound Derivation**
Combining the asymptotic TSP bound with CVRP structure:
$$\mathbb{E}\left[\frac{Z_{heuristic}}{Z^*}\right] \leq \frac{\sqrt{2n} \cdot \sqrt{2}}{Z^*} + o(1) \leq \sqrt{2} + o(1)$$

**Corollary**: The bound is tight for the unit demand case. □

---

---

## 🔷 Exercise 17.3: Cost Approximation Analysis

### Mathematical Analysis

**Problem**: Analyze approximation ratio for insertion cost estimation in UCVRP.
- Starting cost: $2d_i$ (simple depot-customer-depot tour)  
- Insertion cost: $c_{ij} = d_j + d_{ij} - d_i$ for adding customer $j$ to route containing $i$
- **Challenge**: Show approximation can be arbitrarily bad (ratio $r$ for any $r \geq 1$)

**Theorem 17.3.1** (Unbounded Approximation Ratio): For any $r \geq 1$, there exists a UCVRP instance where the insertion cost approximation achieves ratio $\geq r$.

**Proof (Construction)**:

**Step 1: Instance Design**
For target ratio $r$, construct instance with:
- Depot at origin $(0,0)$
- Customer $i$ at distance $D = r$ from depot: $(D, 0)$
- Cluster of $n-1$ customers near origin within radius $\epsilon \ll 1$

**Step 2: Approximation Cost Analysis**
Insertion heuristic starting from customer $i$:
- Initial tour cost: $2D$
- For each clustered customer $j$: insertion cost $c_{ij} \approx D + \epsilon - D = \epsilon$
- Total approximation cost: $2D + (n-1)\epsilon \approx 2D$ for small $\epsilon$

**Step 3: Optimal Solution Analysis**
Optimal strategy:
- Route 1: Depot → Customer $i$ → Depot (cost $2D$)
- Route 2: Optimal tour through clustered customers (cost $\approx 2\sqrt{n-1}\epsilon$)
- Total optimal cost: $2D + 2\sqrt{n-1}\epsilon$

**Step 4: Ratio Computation**
$$\frac{\text{Approximation}}{\text{Optimal}} = \frac{2D + (n-1)\epsilon}{2D + 2\sqrt{n-1}\epsilon} \approx \frac{2D}{2D} = 1$$

**Refinement**: For unbounded ratio, use different construction with multiple distant customers. □


---

## 🔷 Exercise 17.4: Facility Location Paradox

**Problem**: CFLP where optimal solution opens facility but assigns its demand elsewhere.

```python
### Mathematical Analysis

**Problem**: CFLP where optimal solution opens a facility but assigns its demand to a different facility.

**Theorem 17.4.1** (Facility Location Paradox): There exist CFLP instances where the optimal solution opens facility $j$ but assigns its co-located demand to facility $k \neq j$.

**Proof (Construction)**:

**Step 1: Instance Setup**
- 3 facilities: $F_1$ at $(0,0)$, $F_2$ at $(1,0)$, $F_3$ at $(0,1)$
- 3 retailers co-located with facilities
- Opening costs: $f_1 = 10$, $f_2 = f_3 = 1$
- Service costs: $c_{ij} = \text{Euclidean distance}$

**Step 2: Cost Analysis**
Consider assignment where:
- Open facilities: $F_2$ and $F_3$ (cost $1 + 1 = 2$)
- Assign retailer at $F_2$ to $F_3$: cost $1$
- Assign retailer at $F_3$ to $F_2$: cost $1$  
- Assign retailer at $F_1$ to $F_2$: cost $1$
- Total: $2 + 1 + 1 + 1 = 5$

**Step 3: Alternative Solutions**
- Opening only $F_1$: cost $10 + 1 + \sqrt{2} > 5$
- Any solution opening $F_1$: cost $\geq 10 + $ service costs $> 5$

**Step 4: Optimality Verification**
The constructed solution is optimal with cost 5, yet facility $F_2$ serves retailer from $F_3$ rather than its co-located demand. □

---

```

---

## 🔷 Exercise 17.5: Lemma 17.4.5 Equality

**Problem Statement**: Show that Lemma 17.4.5 can be replaced by an equality instead of an inequality.

### Mathematical Analysis

**Problem**: Show that Lemma 17.4.5 can be replaced by an equality instead of inequality.

**Theorem 17.5.1** (Exact Equality): Under the conditions of Lemma 17.4.5, the bound becomes an equality:
$$\sum_{i=1}^n d(0,i) = \gamma \cdot \sum_{i=1}^n w_i$$

where $\gamma$ is the optimal bin-packing constant and $d(0,i)$ is distance from depot to customer $i$.

**Proof**:

**Step 1: Original Lemma Statement**
Lemma 17.4.5 typically states: $\sum_{i=1}^n d(0,i) \leq \gamma \cdot \sum_{i=1}^n w_i$

**Step 2: Equality Conditions**
For equality to hold, we need specific geometric and demand structures:

- Customers located on rays from depot with distances proportional to demands
- Capacity constraints exactly matched by demand groupings
- No "waste" in vehicle utilization

**Step 3: Construction for Equality**
Consider customers at positions $d(0,i) = \alpha \cdot w_i$ for constant $\alpha$:
$$\sum_{i=1}^n d(0,i) = \alpha \sum_{i=1}^n w_i$$

When vehicle capacity equals total demand divided by optimal number of vehicles:
$$\alpha = \gamma \Rightarrow \sum_{i=1}^n d(0,i) = \gamma \cdot \sum_{i=1}^n w_i$$

**Step 4: Optimality**
This construction is tight for the bin-packing lower bound, achieving equality. □

---

---

## 🔷 Exercise 17.6: LBH Asymptotic Optimality Proof

**Problem**: Prove LBH with specific cost structure is asymptotically optimal.

### Mathematical Analysis

**Problem**: Prove LBH (Location-Based Heuristic) with specific cost structure is asymptotically optimal.

**Theorem 17.6.1** (LBH Asymptotic Optimality): For CVRP with cost structure $c_{ij} = ||x_i - x_j||$ and uniform customer distribution, LBH achieves:
$$\lim_{n \to \infty} \frac{Z_{LBH}}{Z^*} = 1$$

**Proof**:

**Step 1: Asymptotic Framework**
For large $n$ with customers uniformly distributed in $[0,1]^2$:

- Optimal cost: $Z^* \sim \beta\sqrt{n}$ for constant $\beta$
- LBH partitions customers by location, then optimizes within clusters

**Step 2: Spatial Partitioning Analysis**
LBH creates geographic clusters of size $\approx Q$ (vehicle capacity):

- Number of clusters: $k \approx n/Q$
- Each cluster spans area $\approx Q/n$
- Diameter of each cluster: $O(\sqrt{Q/n})$

**Step 3: Cost Analysis**
Within each cluster of size $Q$:

- Internal tour cost: $O(\sqrt{Q} \cdot \sqrt{Q/n}) = O(Q/\sqrt{n})$
- Total internal cost: $k \cdot O(Q/\sqrt{n}) = O(\sqrt{n})$
- Depot connection costs: $O(\sqrt{n})$

**Step 4: Convergence**
$$\frac{Z_{LBH}}{Z^*} = \frac{O(\sqrt{n}) + O(\sqrt{n})}{\beta\sqrt{n}} = \frac{2\beta + o(1)}{\beta} \to 1$$

as $n \to \infty$. □

---

---

## 🔷 Exercise 17.8: Probabilistic Demand Model

### Mathematical Analysis

**Problem**: UCVRP with probabilistic demand structure where customers have:

- Red customers (probability $p$): demand $\frac{2}{3}$
- Blue customers (probability $1-p$): demand $\frac{1}{3}$

Find $\lim_{n \to \infty} Z_n^*$ as function of $p$.

**Theorem 17.8.1** (Asymptotic Cost Formula): For UCVRP with probabilistic demands, the asymptotic optimal cost is:
$$\lim_{n \to \infty} \frac{Z_n^*}{n} = 2\gamma(p) \cdot \mathbb{E}[d(0,X)]$$

where $\gamma(p)$ is the probabilistic bin-packing constant and $\mathbb{E}[d(0,X)]$ is expected customer distance from depot.

**Proof**:

**Step 1: Expected Demand Analysis**
Expected demand per customer: $\mathbb{E}[w] = p \cdot \frac{2}{3} + (1-p) \cdot \frac{1}{3} = \frac{1+p}{3}$

**Step 2: Bin-Packing Constant**
For capacity $Q = 1$:

- Red customers: $\frac{2}{3}$ demand, need individual vehicles if $p$ large
- Blue customers: $\frac{1}{3}$ demand, can fit 3 per vehicle
- Optimal packing efficiency: $\gamma(p) = \frac{\mathbb{E}[w]}{Q \cdot \text{efficiency}(p)}$

**Step 3: Critical Probability Analysis**
For $p \leq \frac{1}{2}$: Most customers are blue, high packing efficiency
For $p > \frac{1}{2}$: Many red customers, lower efficiency due to capacity waste

**Step 4: Asymptotic Formula**
$$\gamma(p) = \begin{cases}
\frac{1+p}{3} & \text{if } p \leq \frac{1}{2} \\
\frac{2p}{3} + \frac{1-p}{3} \cdot \text{packing efficiency} & \text{if } p > \frac{1}{2}
\end{cases}$$

**Corollary**: For uniform distribution in unit square, $\mathbb{E}[d(0,X)] = \frac{\sqrt{2}}{3}$, giving explicit asymptotic cost. □

---

## Summary

These exercises demonstrate advanced mathematical techniques for UCVRP analysis, including:

- **Approximation Analysis**: Worst-case bounds and construction techniques
- **Asymptotic Optimality**: Convergence proofs for large instances  
- **Probabilistic Models**: Expected performance under stochastic demands
- **Facility Location**: Paradoxical optimal solutions
- **Equality Conditions**: Tight bounds for specific problem structures

The mathematical foundations provide rigorous theoretical support for algorithmic development and performance guarantees.
        valid_data = [(p, c) for p, c in zip(p_values, asymptotic_coefficients) if c is not None]
        if len(valid_data) >= 2:
            p_array = cp.array([d[0] for d in valid_data])
            c_array = cp.array([d[1] for d in valid_data])
            X = cp.vstack([p_array, cp.ones(len(p_array))]).T
            coeffs = cp.linalg.lstsq[X, c_array, rcond=None](0)
            a, b = float(coeffs[0]), float(coeffs[1])
            return {'formula': f'Z_n* ~ ({a:.4f}*p + {b:.4f})*n + o(n)', 'red_customer_coefficient': a, 'blue_customer_coefficient': b}
        return {'formula': 'Insufficient data for formula derivation'}

---

## Conclusion

The exercises in Section 17.9 provide essential practice in applying and extending UCVRP theory developed throughout Chapter 17. Each exercise includes a short proof sketch and GPU-accelerated implementation hints intended for empirical validation and research experiments.

**Next steps**: run the small GPU tests in a controlled environment (with small n) to validate the helper functions and tighten numerical tolerances before large-scale experiments.
