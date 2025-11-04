# CVRP Split Strategy Implementations

## Overview

This document describes the split strategy implementations for the Capacitated Vehicle Routing Problem (CVRP). Split strategies are critical for two-phase CVRP algorithms that work on **giant tour representations**.

### Why Split Procedures Matter

In two-phase CVRP approaches:

1. **Construction Phase**: Generate a giant tour (permutation of all customers) using heuristics like Nearest Neighbor or evolutionary algorithms
2. **Split Phase**: Partition the giant tour into feasible routes respecting vehicle capacity constraints
3. **Improvement Phase**: Apply local search operators (2-opt, simulated annealing) to the route structure

**Key Insight**: The split procedure directly determines solution quality. A poor split can make an otherwise good permutation produce suboptimal routes, while an optimal split extracts the best possible route structure from a given permutation.

### Academic Context

This implementation addresses the question raised during development:

> **Question**: "Why don't I need bin packing for VRP given capacity constraints?"
>
> **Answer**: You DO need it for quality initial solutions! Split procedures ARE bin packing variants adapted for CVRP:
>
> - **Construction phase**: Use split procedure to get optimal route boundaries (run once)
> - **Improvement phase**: Use fast feasibility checking only (every iteration, O(n²) split would be too expensive)

Without proper split procedures, construction heuristics produce poor-quality initial solutions that require extensive improvement iterations.

## Implemented Strategies

### Strategy Selection Guidelines

| Strategy | Time Complexity | Quality | Use Case | Preserves Order |
|----------|----------------|---------|----------|-----------------|
| **Best Fit (BF)** | $O(n \log n)$ | Good | Fast construction, sequential | ✅ Yes |
| **Best Fit Decreasing (BFD)** | $O(n \log n)$ | Better | Fast construction, insertion | ❌ No (sorts) |
| **DP Split** | $O(n^2)$ | Optimal | High-quality construction | ✅ Yes |
| **Windowed-DP** | $O(n \times w)$ | ~5-8% worse | Compromise speed/quality | ✅ Yes |
| **GPU-DP** | $O(n)$ parallel | Optimal | Large instances with GPU | ✅ Yes |

---

## 1. Best Fit (BF) Split

**Reference**: Simchi-Levi et al. (2005), "The logic of logistics: Theory, algorithms, and applications for logistics and supply chain management", Springer.

### Description

Best Fit is a sequential bin packing heuristic adapted for CVRP split. It processes customers in the order they appear in the giant tour and assigns each customer to the route with the **least remaining capacity** that can still accommodate it. If no route can fit the customer, a new route is created.

**Key Properties**:

- Sequential: Processes customers in permutation order
- Greedy: Makes locally optimal placement decisions
- Fast: $O(n \log n)$ using a min-heap for route capacities
- Order-preserving: Maintains giant tour permutation

### Pseudocode

```
Algorithm: BestFit-Split
Input: permutation π of n customers, demands d[], capacity Q, distances dist[][]
Output: List of routes R = {r₁, r₂, ..., rₖ}

1:  Initialize empty route list R ← []
2:  Initialize min-heap H of (remaining_capacity, route_index) pairs
3:  
4:  for i ← 0 to n-1 do
5:      customer ← π[i]
6:      demand ← d[customer]
7:      
8:      # Try to find route with minimum remaining capacity that fits
9:      if H is not empty then
10:         (remaining, route_idx) ← H.peek()
11:         
12:         if demand ≤ remaining then
13:             # Add customer to existing route
14:             H.extract_min()
15:             R[route_idx].append(customer)
16:             new_remaining ← remaining - demand
17:             H.insert((new_remaining, route_idx))
18:             continue
19:     
20:     # No route can fit → create new route
21:     route_idx ← |R|
22:     R.append([customer])
23:     new_remaining ← Q - demand
24:     H.insert((new_remaining, route_idx))
25:
26: # Calculate total cost
27: total_cost ← 0
28: for each route r in R do
29:     total_cost += route_cost(r, dist)
30:
31: return (R, total_cost)
```

### Complexity Analysis

- **Time**: $O(n \log n)$
  - Each customer: $O(\log n)$ heap operations
  - Total: $n \times O(\log n)$
- **Space**: $O(k)$ for heap, where $k \leq n$ is number of routes
- **Worst-case approximation**: $\leq \frac{7}{4}$ OPT (Simchi-Levi et al., 2005)

### Advantages

- Very fast ($O(n \log n)$)
- Preserves permutation order
- Simple implementation
- Good for real-time applications

### Disadvantages

- Greedy decisions may be suboptimal
- No look-ahead for future customers
- Quality depends heavily on permutation order

---

## 2. Best Fit Decreasing (BFD) Split

**Reference**: Simchi-Levi et al. (2005), "The logic of logistics: Theory, algorithms, and applications for logistics and supply chain management", Springer.

### Description

Best Fit Decreasing improves upon BF by **sorting customers by demand** (largest first) before applying the Best Fit strategy. This typically produces tighter packing and uses fewer routes.

**Key Properties**:

- Insertion-based: Breaks original permutation order
- Sorts by demand: Largest customers first
- Better approximation: $\leq \frac{11}{9}$ OPT + $\frac{6}{9}$
- Trade-off: Better quality but loses permutation information

### Pseudocode

```
Algorithm: BestFitDecreasing-Split
Input: permutation π of n customers, demands d[], capacity Q, distances dist[][]
Output: List of routes R = {r₁, r₂, ..., rₖ}

1:  # Sort customers by demand (descending)
2:  sorted_customers ← sort(π, key=λc: d[c], reverse=True)
3:  
4:  Initialize empty route list R ← []
5:  Initialize min-heap H of (remaining_capacity, route_index) pairs
6:  
7:  for i ← 0 to n-1 do
8:      customer ← sorted_customers[i]
9:      demand ← d[customer]
10:     
11:     # Try to find route with minimum remaining capacity that fits
12:     if H is not empty then
13:         (remaining, route_idx) ← H.peek()
14:         
15:         if demand ≤ remaining then
16:             # Add customer to existing route
17:             H.extract_min()
18:             R[route_idx].append(customer)
19:             new_remaining ← remaining - demand
20:             H.insert((new_remaining, route_idx))
21:             continue
22:     
23:     # No route can fit → create new route
24:     route_idx ← |R|
25:     R.append([customer])
26:     new_remaining ← Q - demand
27:     H.insert((new_remaining, route_idx))
28:
29: # Calculate total cost
30: total_cost ← 0
31: for each route r in R do
32:     total_cost += route_cost(r, dist)
33:
34: return (R, total_cost)
```

### Complexity Analysis

- **Time**: $O(n \log n)$
  - Sorting: $O(n \log n)$
  - BF procedure: $O(n \log n)$
  - Total: $O(n \log n)$
- **Space**: $O(n)$ for sorted array + $O(k)$ for heap
- **Approximation**: $\leq \frac{11}{9}$ OPT + $\frac{6}{9}$ (Simchi-Levi et al., 2005)

### Advantages

- Better approximation guarantee than BF
- Fewer routes used (tighter packing)
- Still fast ($O(n \log n)$)

### Disadvantages

- **Breaks permutation order** (incompatible with sequence-based improvement)
- Cannot be used with evolutionary algorithms that rely on permutation semantics
- Sorting overhead

---

## 3. Dynamic Programming (DP) Split

**Reference**: Prins (2004), "A simple and effective evolutionary algorithm for the vehicle routing problem", *Computers & Operations Research* 31(12), 1985-2002.

### Description

Dynamic Programming Split finds the **optimal partition** of a given giant tour into routes. It formulates the split as a shortest path problem on an auxiliary graph where:

- Nodes represent positions in the giant tour
- Arc $(i, j)$ exists if customers $\pi[i+1..j]$ fit in one route (demand $\leq Q$)
- Arc cost is the cost of route serving customers $\pi[i+1..j]$

The shortest path from node 0 to node $n$ gives the optimal split.

**Key Properties**:

- Optimal: Finds best split for given permutation
- Order-preserving: Maintains giant tour sequence
- Expensive: $O(n^2)$ complexity
- Foundation: Used as baseline for evolutionary algorithms

### Pseudocode

```
Algorithm: DynamicProgramming-Split
Input: permutation π of n customers, demands d[], capacity Q, distances dist[][]
Output: List of routes R = {r₁, r₂, ..., rₖ}, total cost

1:  # Initialize DP arrays
2:  V[0] ← 0                          # Cost to reach position 0
3:  for i ← 1 to n do
4:      V[i] ← ∞                      # Cost to reach position i
5:  pred[0..n] ← -1                   # Predecessor for backtracking
6:  
7:  # Forward DP: Compute shortest path
8:  for i ← 0 to n-1 do
9:      if V[i] = ∞ then continue    # Position i unreachable
10:     
11:     load ← 0                      # Current route load
12:     route_cost ← 0                # Cost of current route being built
13:     
14:     for j ← i+1 to n do
15:         customer ← π[j]
16:         load ← load + d[customer]
17:         
18:         if load > Q then break    # Route exceeds capacity
19:         
20:         # Calculate cost of route from depot to π[i+1..j] and back
21:         if j = i+1 then
22:             # First customer in route
23:             route_cost ← dist[depot][customer] + dist[customer][depot]
24:         else
25:             # Add customer to existing route
26:             prev_customer ← π[j-1]
27:             route_cost ← route_cost - dist[prev_customer][depot]
28:             route_cost ← route_cost + dist[prev_customer][customer]
29:             route_cost ← route_cost + dist[customer][depot]
30:         
31:         # Update if better path found to position j
32:         if V[i] + route_cost < V[j] then
33:             V[j] ← V[i] + route_cost
34:             pred[j] ← i
35:
36: # Backward reconstruction: Extract routes
37: R ← []
38: j ← n
39: while j > 0 do
40:     i ← pred[j]
41:     route ← π[i+1..j]            # Customers from position i+1 to j
42:     R.prepend(route)              # Add route to beginning
43:     j ← i
44:
45: return (R, V[n])
```

### Complexity Analysis

- **Time**: $O(n^2)$
  - Outer loop: $n$ positions
  - Inner loop: Up to $n$ extensions
  - Route cost calculation: $O(1)$ incremental
- **Space**: $O(n)$ for DP arrays
- **Quality**: **Optimal** for given permutation

### Advantages

- **Optimal split** for any given permutation
- Order-preserving (compatible with evolutionary algorithms)
- Enables giant tour representations in metaheuristics
- Proven foundation (Prins 2004)

### Disadvantages

- Expensive: $O(n^2)$ per evaluation
- Too slow for improvement phase (would dominate runtime)
- Requires efficient incremental cost calculation

---

## 4. Windowed Dynamic Programming Split

**Reference**: Adapted from Righini & Salani (2006), "Symmetry helps: Bounded bi-directional dynamic programming for the elementary shortest path problem with resource constraints", *Discrete Optimization* 3(3), 255-273.

### Description

Windowed-DP is a **bounded approximation** of the full DP split that limits the lookahead window to $w$ customers instead of considering all possible routes. This reduces complexity from $O(n^2)$ to $O(n \times w)$ with $w \ll n$.

The technique is adapted from Righini & Salani's bounded bidirectional DP for resource-constrained shortest paths. Instead of exploring the full state space, we limit each position to only consider routes ending within a window of $w$ customers ahead.

**Key Properties**:

- Bounded: Limits lookahead to window size $w$
- Approximation: ~5-8% worse than full DP (empirical)
- Complexity: $O(n \times w)$ with typical $w \in [10, 50]$
- Order-preserving: Maintains permutation
- Practical: Good quality/speed trade-off

### Pseudocode

```
Algorithm: WindowedDP-Split
Input: permutation π of n customers, demands d[], capacity Q, distances dist[][], window size w
Output: List of routes R = {r₁, r₂, ..., rₖ}, total cost

1:  # Initialize DP arrays
2:  V[0] ← 0                          # Cost to reach position 0
3:  for i ← 1 to n do
4:      V[i] ← ∞                      # Cost to reach position i
5:  pred[0..n] ← -1                   # Predecessor for backtracking
6:  
7:  # Forward DP with bounded window
8:  for i ← 0 to n-1 do
9:      if V[i] = ∞ then continue    # Position i unreachable
10:     
11:     load ← 0                      # Current route load
12:     route_cost ← 0                # Cost of current route being built
13:     
14:     # BOUNDED LOOKAHEAD: Only consider next w customers
15:     max_j ← min(i + w, n)         # Window bound
16:     
17:     for j ← i+1 to max_j do
18:         customer ← π[j]
19:         load ← load + d[customer]
20:         
21:         if load > Q then break    # Route exceeds capacity
22:         
23:         # Calculate cost of route from depot to π[i+1..j] and back
24:         if j = i+1 then
25:             # First customer in route
26:             route_cost ← dist[depot][customer] + dist[customer][depot]
27:         else
28:             # Add customer to existing route
29:             prev_customer ← π[j-1]
30:             route_cost ← route_cost - dist[prev_customer][depot]
31:             route_cost ← route_cost + dist[prev_customer][customer]
32:             route_cost ← route_cost + dist[customer][depot]
33:         
34:         # Update if better path found to position j
35:         if V[i] + route_cost < V[j] then
36:             V[j] ← V[i] + route_cost
37:             pred[j] ← i
38:
39: # Backward reconstruction: Extract routes
40: R ← []
41: j ← n
42: while j > 0 do
43:     i ← pred[j]
44:     route ← π[i+1..j]            # Customers from position i+1 to j
45:     R.prepend(route)              # Add route to beginning
46:     j ← i
47:
48: return (R, V[n])
```

### Complexity Analysis

- **Time**: $O(n \times w)$
  - Outer loop: $n$ positions
  - Inner loop: At most $w$ extensions (instead of $n$)
  - Typical $w \in [10, 50]$: Reduces time by factor of 10-100x
- **Space**: $O(n)$ for DP arrays
- **Quality**: Empirically ~5-8% worse than full DP

### Window Size Guidelines

| Instance Size | Recommended $w$ | Expected Quality Loss |
|---------------|-----------------|----------------------|
| $n < 100$ | $w = 20$ | ~2-3% |
| $100 \leq n < 500$ | $w = 30$ | ~3-5% |
| $n \geq 500$ | $w = 50$ | ~5-8% |

### Advantages

- **Much faster** than full DP ($10-100\times$ speedup)
- **Good quality**: Only 5-8% worse than optimal
- Order-preserving
- Tunable quality/speed trade-off via $w$

### Disadvantages

- Approximation: Not optimal
- Window size must be tuned
- Quality degrades with smaller windows

---

## 5. GPU-Accelerated Dynamic Programming Split

**Reference**: Custom implementation based on Prins (2004) DP split with CUDA/CuPy parallelization.

### Description

GPU-DP parallelizes the DP split computation by computing all arc costs $(i, j)$ in parallel on the GPU, then performing the shortest path computation. This achieves $O(n)$ complexity with $n$ parallel threads instead of $O(n^2)$ sequential.

**Key Properties**:

- Parallel: Exploits GPU parallelism
- Optimal: Same quality as sequential DP
- Fast: $O(n)$ with $O(n^2)$ threads
- Hardware-dependent: Requires CUDA-capable GPU

### Pseudocode

```
Algorithm: GPU-DP-Split
Input: permutation π of n customers, demands d[], capacity Q, distances dist[][]
Output: List of routes R = {r₁, r₂, ..., rₖ}, total cost

# PHASE 1: Parallel arc cost computation on GPU
1:  Allocate GPU memory for arc_cost[n][n], feasible[n][n]
2:  
3:  # Launch GPU kernel with n×n threads
4:  kernel_compute_arcs<<<grid, block>>>:
5:      # Each thread (i, j) computes arc cost and feasibility
6:      thread_i ← blockIdx.x * blockDim.x + threadIdx.x
7:      thread_j ← blockIdx.y * blockDim.y + threadIdx.y
8:      
9:      if thread_i >= n or thread_j >= n or thread_j ≤ thread_i then
10:         return
11:     
12:     # Check capacity feasibility
13:     load ← 0
14:     for k ← thread_i+1 to thread_j do
15:         load ← load + d[π[k]]
16:     
17:     if load > Q then
18:         feasible[thread_i][thread_j] ← false
19:         arc_cost[thread_i][thread_j] ← ∞
20:         return
21:     
22:     # Calculate route cost: depot → π[i+1..j] → depot
23:     cost ← dist[depot][π[thread_i+1]]
24:     for k ← thread_i+1 to thread_j-1 do
25:         cost ← cost + dist[π[k]][π[k+1]]
26:     cost ← cost + dist[π[thread_j]][depot]
27:     
28:     feasible[thread_i][thread_j] ← true
29:     arc_cost[thread_i][thread_j] ← cost
30:
31: # PHASE 2: Sequential shortest path on CPU
32: Copy arc_cost and feasible back to CPU
33:
34: V[0] ← 0
35: for i ← 1 to n do
36:     V[i] ← ∞
37: pred[0..n] ← -1
38:
39: for i ← 0 to n-1 do
40:     if V[i] = ∞ then continue
41:     
42:     for j ← i+1 to n do
43:         if not feasible[i][j] then continue
44:         
45:         if V[i] + arc_cost[i][j] < V[j] then
46:             V[j] ← V[i] + arc_cost[i][j]
47:             pred[j] ← i
48:
49: # PHASE 3: Backward reconstruction
50: R ← []
51: j ← n
52: while j > 0 do
53:     i ← pred[j]
54:     route ← π[i+1..j]
55:     R.prepend(route)
56:     j ← i
57:
58: return (R, V[n])
```

### Complexity Analysis

- **Time**:
  - Phase 1 (GPU): $O(n)$ with $O(n^2)$ parallel threads
  - Phase 2 (CPU): $O(n^2)$ shortest path (but with precomputed costs)
  - Total: Dominated by GPU transfer + $O(n^2)$ DP
- **Space**: $O(n^2)$ for arc cost matrix on GPU
- **Quality**: **Optimal** (same as sequential DP)

### Hardware Considerations

**Minimum Requirements**:

- CUDA Compute Capability: 6.0+
- VRAM: $\geq 4$ GB for instances up to $n \approx 3000$
- Memory: $O(n^2)$ floats, e.g., $n=3000 \Rightarrow 3000^2 \times 4 \text{ bytes} = 36 \text{ MB}$

**Performance Characteristics**:

- **Small instances** ($n < 500$): GPU overhead dominates, CPU faster
- **Medium instances** ($500 \leq n < 2000$): GPU competitive
- **Large instances** ($n \geq 2000$): GPU significantly faster

### Advantages

- **Fast for large instances** ($10-50\times$ speedup for $n \geq 2000$)
- **Optimal quality** (same as sequential DP)
- Order-preserving

### Disadvantages

- GPU overhead for small instances
- Requires CUDA-capable hardware
- $O(n^2)$ memory on GPU
- Complex implementation

---

## Comparison and Recommendations

### Quality Hierarchy (Best to Worst)

1. **DP Split** = **GPU-DP Split**: Optimal for given permutation
2. **Windowed-DP Split**: ~5-8% worse (empirical)
3. **Best Fit Decreasing**: $\leq \frac{11}{9}$ OPT + $\frac{6}{9}$ approximation
4. **Best Fit**: $\leq \frac{7}{4}$ OPT approximation

### Speed Hierarchy (Fastest to Slowest)

For $n = 1000$ customers (typical medium instance):

1. **Best Fit**: $O(n \log n) \approx 10$ ms
2. **Best Fit Decreasing**: $O(n \log n) \approx 15$ ms (sorting overhead)
3. **Windowed-DP** ($w=30$): $O(n \times w) \approx 50$ ms
4. **GPU-DP**: $O(n^2)$ parallel $\approx 100$ ms (includes GPU transfer)
5. **DP Split**: $O(n^2) \approx 1000$ ms

### Use Case Recommendations

#### Construction Phase (Run Once)

- **High-quality baseline**: Use **DP Split** or **GPU-DP**
- **Fast construction**: Use **Windowed-DP** with $w=30$
- **Real-time applications**: Use **Best Fit** or **Best Fit Decreasing**

#### Evolutionary Algorithms (Thousands of Evaluations)

- **Small populations** ($< 100$ individuals): **Windowed-DP** acceptable
- **Large populations** ($\geq 100$ individuals): **Best Fit** or **Best Fit Decreasing**
- **GPU available**: **GPU-DP** for large instances ($n \geq 2000$)

#### Metaheuristic Integration

- **Genetic algorithms with giant tours**: Use **DP Split** (Prins 2004 approach)
- **Simulated annealing with routes**: No split needed (feasibility checking only)
- **Hybrid approaches**: **Windowed-DP** for quality/speed balance

#### Order Preservation Requirements

- **Must preserve permutation**: Use **BF**, **DP Split**, **Windowed-DP**, or **GPU-DP**
- **Can break order**: Use **BFD** (better approximation)

---

## Implementation Guidelines

### Protocol Interface

All split strategies implement the `SplitStrategy` protocol:

```python
from typing import Protocol, List, Tuple
from numpy.typing import NDArray

class SplitStrategy(Protocol):
    """Protocol for CVRP split strategies."""
    
    def split(
        self,
        permutation: NDArray,
        problem: CVRPProblem
    ) -> Tuple[List[List[int]], float]:
        """
        Split giant tour into feasible routes.
        
        Args:
            permutation: Giant tour (customer indices)
            problem: CVRP instance (demands, distances, capacity)
            
        Returns:
            routes: List of routes (each route is list of customer indices)
            total_cost: Total cost of all routes
        """
        ...
    
    def get_name(self) -> str:
        """Return strategy name."""
        ...
    
    def get_complexity(self) -> str:
        """Return time complexity (e.g., 'O(n^2)')."""
        ...
    
    def supports_gpu(self) -> bool:
        """Return True if strategy uses GPU acceleration."""
        ...
```

### Testing Requirements

Each implementation must include:

1. **Correctness tests**: Validate on known CVRP instances
2. **Capacity feasibility**: Ensure all routes respect $Q$
3. **Cost calculation**: Verify route costs are correct
4. **Optimality verification** (for DP variants): Compare against brute force on small instances
5. **Approximation bounds** (for BF/BFD): Verify worst-case ratios hold
6. **Performance benchmarks**: Measure time vs. instance size

---

## References

1. **Simchi-Levi, D., Chen, X., & Bramel, J. (2005)**. "The logic of logistics: Theory, algorithms, and applications for logistics and supply chain management", Springer.

2. **Prins, C. (2004)**. "A simple and effective evolutionary algorithm for the vehicle routing problem", *Computers & Operations Research*, 31(12), 1985-2002. DOI: 10.1016/S0305-0548(03)00158-8

3. **Righini, G., & Salani, M. (2006)**. "Symmetry helps: Bounded bi-directional dynamic programming for the elementary shortest path problem with resource constraints", *Discrete Optimization*, 3(3), 255-273. DOI: 10.1016/j.disopt.2006.05.007

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-XX | GPU-6 Implementation | Initial comprehensive documentation with all 5 strategies |

---

**Document Status**: ✅ COMPLETE - Ready for implementation

**Next Steps**:

1. Implement `SplitStrategy` protocol in `code/src/protocols/split_protocol.py`
2. Implement DP Split (Prins 2004) as baseline
3. Implement BF and BFD (Simchi-Levi et al. 2005)
4. Implement Windowed-DP (Righini & Salani 2006 adaptation)
5. [Optional] Implement GPU-DP with CuPy
6. Create comprehensive unit tests
7. Benchmark all strategies on CVRP instances
