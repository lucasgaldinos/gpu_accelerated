# Visual Guide: Before and After

This guide shows you what to expect when processing exercises from a PDF.

## Before: Raw PDF Exercise

```
Page 85

Exercise 4.1

Consider a simple bin packing problem where we have items of sizes 
{0.5, 0.3, 0.4, 0.2, 0.6} and bins of capacity 1.0. Analyze the 
worst-case performance of the First Fit Decreasing (FFD) algorithm.
```

## After: Complete Solution Manual

### Part 1: Problem Statement
```markdown
## Exercise 4.1 - Worst-Case Analysis

**Page:** 85 | **Section:** 4. Worst-Case Analysis | **Difficulty:** Medium

**Tags:** `bin-packing`, `worst-case-analysis`, `approximation-algorithms`

### Problem Statement

Consider a simple bin packing problem where we have items of sizes 
{0.5, 0.3, 0.4, 0.2, 0.6} and bins of capacity 1.0. 
Analyze the worst-case performance of the First Fit Decreasing (FFD) algorithm.
```

### Part 2: Mathematical Solution (with KaTeX)
```markdown
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

**Analysis:**

$$
\frac{FFD(S)}{OPT(S)} = \frac{2}{2} = 1.0
$$
```

**How it renders:**

Given:
- Items: $S = \{0.5, 0.3, 0.4, 0.2, 0.6\}$

$$
S_{sorted} = \{0.6, 0.5, 0.4, 0.3, 0.2\}
$$

### Part 3: Clear Explanation
```markdown
### Explanation

**What's happening here?**

The First Fit Decreasing (FFD) algorithm is a simple strategy for packing items into bins:

1. **Sort first:** Arrange items from largest to smallest. Pack big things first!

2. **First fit rule:** For each item, try to put it in the first bin where it fits.

**Why did FFD find the optimal solution?**

In this example, FFD made excellent choices:
- Started with 0.6, leaving 0.4 space in Bin 1
- When trying 0.5, it didn't fit in Bin 1, so opened Bin 2
- Then 0.4 perfectly filled the remaining space in Bin 1
- Finally, 0.3 and 0.2 both fit nicely in Bin 2

**Real-world context:**

Think of this like packing boxes into shipping containers!
```

### Part 4: Python Implementation
```markdown
### Python Implementation

\`\`\`python
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


# Example: Exercise 4.1
items = [0.5, 0.3, 0.4, 0.2, 0.6]
bins = first_fit_decreasing(items)

print(f"Number of bins used: {len(bins)}")
for i, bin in enumerate(bins, 1):
    print(f"  Bin {i}: {bin} (total: {sum(bin):.1f})")

# Output:
# Number of bins used: 2
#   Bin 1: [0.6, 0.4] (total: 1.0)
#   Bin 2: [0.5, 0.3, 0.2] (total: 1.0)
\`\`\`
```

### Part 5: Citations and Notes
```markdown
### References

- Simchi-Levi, D., Chen, X., & Bramel, J. (2014). *The Logic of Logistics*. 
  Section 4.2: Worst-Case Analysis of FFD Algorithm.
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
```

## The Complete Flow

### Input: PDF File
```
📄 085_4_Worst_Case_Analysis.pdf
   Contains: Exercises 4.1 through 4.15
```

### Step 1: Extract
```bash
$ python scripts/generate_exercise_solutions.py --pdf-path pdfs/file.pdf --extract-only
```

### Output: Templates
```
📁 solutions/
  ├── extracted_exercises.json
  ├── exercise_4.1_template.md
  ├── exercise_4.2_template.md
  ├── ...
  └── exercise_4.15_template.md
```

### Step 2: Fill in Solutions
Edit each template to add:
- ✍️ Mathematical solutions
- ✍️ Clear explanations
- ✍️ Python code
- ✍️ Citations
- ✍️ Notes

### Final Output: Solution Manual
```markdown
# Solution Manual - Chapter 4: Worst-Case Analysis

**Source:** The Logic of Logistics

**Total Solutions:** 15

---

## Exercise 4.1 - Worst-Case Analysis
[Complete solution with all 5 sections]

---

## Exercise 4.2 - FFD Lower Bound
[Complete solution with all 5 sections]

---

... (all exercises)
```

## What Makes a Good Solution?

### ✅ Good Mathematical Solution
```markdown
**Given:** $x \in \mathbb{R}$, $x > 0$

**Prove:** $x + \frac{1}{x} \geq 2$

**Proof:**
By AM-GM inequality:

$$
\frac{x + \frac{1}{x}}{2} \geq \sqrt{x \cdot \frac{1}{x}} = 1
$$

Therefore:
$$
x + \frac{1}{x} \geq 2
$$

Equality holds when $x = \frac{1}{x}$, i.e., $x = 1$. ∎
```

### ✅ Good Explanation
```markdown
**What's happening?**

We're proving that a positive number plus its reciprocal is always at least 2.

**Intuition:**
- If $x = 1$: we get $1 + 1 = 2$ (minimum)
- If $x > 1$: $x$ is big, but $\frac{1}{x}$ is small
- If $x < 1$: $x$ is small, but $\frac{1}{x}$ is big
- The sum is minimized when they're balanced at $x = 1$

**Real-world:**
Think of traveling somewhere and back. If you go fast one way and slow the other,
your average speed is worse than going the same speed both ways!
```

### ✅ Good Python Code
```python
def verify_am_gm_inequality(x):
    """
    Verify that x + 1/x >= 2 for x > 0
    
    Args:
        x: Positive real number
        
    Returns:
        tuple: (sum value, is valid)
    """
    if x <= 0:
        raise ValueError("x must be positive")
    
    sum_value = x + 1/x
    is_valid = sum_value >= 2 - 1e-10  # Small tolerance for floating point
    
    return sum_value, is_valid

# Test with various values
test_values = [0.5, 1.0, 2.0, 10.0]
for x in test_values:
    value, valid = verify_am_gm_inequality(x)
    print(f"x={x}: {x} + {1/x:.2f} = {value:.2f} ✓" if valid else "✗")

# Output:
# x=0.5: 0.5 + 2.00 = 2.50 ✓
# x=1.0: 1.0 + 1.00 = 2.00 ✓
# x=2.0: 2.0 + 0.50 = 2.50 ✓
# x=10.0: 10.0 + 0.10 = 10.10 ✓
```

## Tips for Visual Appeal

### Use Headers Effectively
```markdown
## Main Exercise Title
### Major Section (Mathematical Solution, Explanation, etc.)
**Bold for emphasis**
*Italic for terms*
`Code/technical terms`
```

### Format Math Beautifully
```markdown
Inline: The value $x^2$ represents...
Display: 
$$
\sum_{i=1}^{n} x_i = X
$$
```

### Structure Code Clearly
```python
# 1. Setup
data = prepare_data()

# 2. Process
result = process(data)

# 3. Output
display(result)
```

### Add Visual Breaks
```markdown
---

**Key Point:** This is important!

💡 **Tip:** Try this approach...

⚠️ **Warning:** Watch out for...
```

## Quality Checklist

Before considering a solution complete:

- [ ] All math is correct and properly formatted
- [ ] Explanations are clear and accessible
- [ ] Code runs without errors
- [ ] Code produces expected output
- [ ] Citations are accurate and specific
- [ ] Notes add value
- [ ] No typos or formatting issues
- [ ] Follows the established format

---

**The goal:** Create solution manuals that help students truly understand the material, not just see the answer!
