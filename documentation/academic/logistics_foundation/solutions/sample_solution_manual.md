# Solution Manual

**Source:** The Logic of Logistics

**Total Solutions:** 1

---

## Table of Contents

- [Exercise 4.1 - Worst-Case Analysis](#exercise-41---worst-case-analysis)

---

## Exercise 4.1 - Worst-Case Analysis

**Page:** 85 | **Section:** 4. Worst-Case Analysis | **Difficulty:** Medium

**Tags:** `bin-packing`, `worst-case-analysis`, `approximation-algorithms`

### Problem Statement

Consider a simple bin packing problem where we have items of sizes 
{0.5, 0.3, 0.4, 0.2, 0.6} and bins of capacity 1.0. 
Analyze the worst-case performance of the First Fit Decreasing (FFD) algorithm.

### Mathematical Solution


**Given:**
- Items: $S = \{0.5, 0.3, 0.4, 0.2, 0.6\}$
- Bin capacity: $C = 1.0$
- Algorithm: First Fit Decreasing (FFD)

**Step 1:** Sort items in decreasing order

$$
S_{sorted} = \{0.6, 0.5, 0.4, 0.3, 0.2\}
$$

**Step 2:** Apply FFD algorithm

- **Bin 1:** Place 0.6 (remaining: 0.4)
  - Try 0.5: doesn't fit
  - Try 0.4: fits! Place 0.4 (remaining: 0.0)
  
- **Bin 2:** Place 0.5 (remaining: 0.5)
  - Try 0.3: fits! Place 0.3 (remaining: 0.2)
  - Try 0.2: fits! Place 0.2 (remaining: 0.0)

Final packing: **2 bins**
- Bin 1: {0.6, 0.4} = 1.0
- Bin 2: {0.5, 0.3, 0.2} = 1.0

This matches the **optimal solution**: **2 bins**

**Analysis:**

$$
\frac{FFD(S)}{OPT(S)} = \frac{2}{2} = 1.0
$$

FFD found the optimal solution for this instance!

**General FFD bound:** For any instance, FFD satisfies:

$$
FFD(S) \leq \frac{11}{9}OPT(S) + \frac{6}{9}
$$

**Note:** While FFD found the optimal solution here, this doesn't always happen. The 11/9 bound 
tells us the worst case - FFD will never use more than 11/9 times optimal (plus a small constant).


### Explanation


**What's happening here?**

The First Fit Decreasing (FFD) algorithm is a simple strategy for packing items into bins:

1. **Sort first:** Arrange items from largest to smallest. This is intuitive - pack big things first!

2. **First fit rule:** For each item, try to put it in the first bin where it fits. If it doesn't fit anywhere, open a new bin.

**Why did FFD find the optimal solution?**

In this example, FFD made excellent choices:
- Started with 0.6, leaving 0.4 space in Bin 1
- When trying to place 0.5, it didn't fit in Bin 1, so opened Bin 2
- Then 0.4 perfectly filled the remaining space in Bin 1
- Finally, 0.3 and 0.2 both fit nicely in Bin 2

The sorted order helped FFD naturally group items optimally: {0.6, 0.4} and {0.5, 0.3, 0.2}.

**The worst-case guarantee:**

While FFD found the optimal solution here, this doesn't always happen. FFD is guaranteed to use 
at most 11/9 times the optimal number of bins (plus a small constant). This means:
- If optimal uses 9 bins, FFD will use at most 11 bins
- The algorithm gives a 1.22x approximation guarantee
- In practice, FFD often performs much better than this worst-case bound

**Real-world context:**

Think of this like packing boxes into shipping containers, or scheduling tasks with time limits. 
FFD is fast (O(n log n) time) and gives excellent results - often optimal or near-optimal!

**When does FFD struggle?**

FFD can produce suboptimal solutions when:
- Many items are just over half the bin capacity
- The instance is specifically constructed to fool the greedy approach
- Items have complex interdependencies that greedy sorting misses


### Python Implementation

```python

def first_fit_decreasing(items, bin_capacity=1.0):
    """
    Implement the First Fit Decreasing algorithm for bin packing.
    
    Args:
        items: List of item sizes
        bin_capacity: Maximum capacity of each bin
        
    Returns:
        List of bins, where each bin is a list of items
    """
    # Step 1: Sort items in decreasing order
    sorted_items = sorted(items, reverse=True)
    
    # Step 2: Initialize bins
    bins = []
    bin_remaining = []
    
    # Step 3: Place each item
    for item in sorted_items:
        # Try to fit in existing bins
        placed = False
        for i in range(len(bins)):
            if bin_remaining[i] >= item:
                bins[i].append(item)
                bin_remaining[i] -= item
                placed = True
                break
        
        # If doesn't fit anywhere, create new bin
        if not placed:
            bins.append([item])
            bin_remaining.append(bin_capacity - item)
    
    return bins


def calculate_bin_utilization(bins, bin_capacity=1.0):
    """Calculate the utilization of bins."""
    total_used = sum(sum(bin) for bin in bins)
    total_capacity = len(bins) * bin_capacity
    return total_used / total_capacity


# Example: Exercise 4.1
items = [0.5, 0.3, 0.4, 0.2, 0.6]
bins = first_fit_decreasing(items)

print(f"Number of bins used: {len(bins)}")
print(f"\nBin contents:")
for i, bin in enumerate(bins, 1):
    print(f"  Bin {i}: {bin} (total: {sum(bin):.1f})")

utilization = calculate_bin_utilization(bins)
print(f"\nOverall utilization: {utilization:.1%}")

# Optimal solution for comparison
optimal_bins = [[0.6, 0.4], [0.5, 0.3, 0.2]]
print(f"\nOptimal solution: {len(optimal_bins)} bins")
print(f"FFD/OPT ratio: {len(bins)/len(optimal_bins):.2f}")

# Output:
# Number of bins used: 2
# Bin contents:
#   Bin 1: [0.6, 0.4] (total: 1.0)
#   Bin 2: [0.5, 0.3, 0.2] (total: 1.0)
# Overall utilization: 100.0%
# Optimal solution: 2 bins
# FFD/OPT ratio: 1.00

```

### References

- Simchi-Levi, D., Chen, X., & Bramel, J. (2014). *The Logic of Logistics*. Section 4.2: Worst-Case Analysis of FFD Algorithm.
- The 11/9 bound for FFD was proven by Johnson (1973) and is tight.

### Notes


**Key Insights:**

1. FFD performs better than First Fit (FF) on average
2. The worst-case bound of 11/9 is asymptotically tight
3. For practical instances, FFD often achieves near-optimal solutions
4. The algorithm runs in O(n log n) time due to sorting

**Extensions:**

- Best Fit Decreasing (BFD) has the same worst-case bound
- Online algorithms (where items arrive one at a time) have worse bounds
- 2D and 3D bin packing are significantly harder problems


---

