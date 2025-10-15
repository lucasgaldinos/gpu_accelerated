# Logistics Foundation - Academic Materials

This directory contains academic materials related to logistics, supply chain management, and optimization from foundational texts such as "The Logic of Logistics" by Simchi-Levi et al.

## Directory Structure

```
logistics_foundation/
├── pdfs/                    # Original PDF files with exercises and chapters
├── solutions/               # Solution manuals for exercises
│   └── sample_solution_manual.md  # Example solution format
├── notes/                   # Study notes and summaries
└── README.md               # This file
```

## Solution Manual Format

Exercise solutions follow a comprehensive format that includes:

1. **Mathematical Solution** - Formal solution using KaTeX notation
2. **Clear Explanation** - Accessible explanation for learners
3. **Python Implementation** - Working code where applicable
4. **Citations** - References to source material
5. **Notes** - Additional insights and extensions

See `solutions/sample_solution_manual.md` for a complete example.

## Generating Solutions

### Prerequisites

Install required dependencies:

```bash
pip install pymupdf4llm
```

### Usage

The `generate_exercise_solutions.py` script in the `scripts/` directory can:

1. **Create sample solutions** (to see the expected format):
```bash
python scripts/generate_exercise_solutions.py --create-sample \
  --output-dir documentation/academic/logistics_foundation/solutions
```

2. **Extract exercises from PDF**:
```bash
python scripts/generate_exercise_solutions.py \
  --pdf-path documentation/academic/logistics_foundation/pdfs/chapter4.pdf \
  --output-dir documentation/academic/logistics_foundation/solutions \
  --extract-only
```

This will:
- Extract exercises from the PDF
- Save exercise data to `extracted_exercises.json`
- Create markdown templates for each exercise

3. **Fill in the templates** with solutions manually, including:
   - Mathematical proofs using KaTeX
   - Clear explanations
   - Python implementations
   - Citations from the book

### Example Workflow

1. Place your PDF in `pdfs/` directory
2. Extract exercises: `python scripts/generate_exercise_solutions.py --pdf-path pdfs/chapter.pdf --extract-only`
3. Edit the generated templates with solutions
4. Optionally compile into a single solution manual

## Solution Template

Each exercise solution should include:

```markdown
## Exercise X.Y - Title

**Page:** XX | **Section:** Section Name | **Difficulty:** Easy/Medium/Hard

**Tags:** `tag1`, `tag2`, `tag3`

### Problem Statement

[Exercise text from the book]

### Mathematical Solution

**Given:** 
- ...

**Step 1:** ...
$$
mathematical notation
$$

### Explanation

Clear, non-technical explanation...

### Python Implementation

\`\`\`python
def solve_exercise():
    """Implementation with comments"""
    pass
\`\`\`

### References

- Source material citations
- Additional resources

### Notes

- Key insights
- Extensions
- Related concepts
```

## Topics Covered

Common topics in logistics and optimization:

- **Worst-Case Analysis** - Performance guarantees for algorithms
- **Bin Packing** - Resource allocation and packing problems
- **Vehicle Routing** - TSP, VRP, and variants
- **Network Flows** - Transportation and distribution
- **Inventory Management** - Stock optimization
- **Facility Location** - Warehouse and depot placement

## Contributing Solutions

When adding new solutions:

1. Follow the established format (see sample)
2. Include all five sections (Mathematical Solution, Explanation, Python Code, References, Notes)
3. Use KaTeX for mathematical notation
4. Provide working Python code with test cases
5. Cite specific pages and sections from the source material
6. Add explanations that would help someone learning the topic

## KaTeX Reference

Common mathematical notation:

- Inline math: `$x^2 + y^2 = r^2$`
- Display math: `$$\frac{a}{b}$$`
- Summations: `$\sum_{i=1}^{n} x_i$`
- Sets: `$S = \{1, 2, 3\}$`
- Greek letters: `$\alpha, \beta, \gamma$`
- Fractions: `$\frac{numerator}{denominator}$`

See [KaTeX documentation](https://katex.org/docs/supported.html) for complete syntax.

## Quality Standards

Solutions should:

- ✅ Be mathematically rigorous and correct
- ✅ Include step-by-step derivations
- ✅ Provide intuitive explanations for key steps
- ✅ Include working, tested Python code
- ✅ Reference specific sections from the book
- ✅ Highlight key insights and practical applications
- ✅ Be accessible to students learning the material

## Resources

- **Primary Text**: Simchi-Levi, D., Chen, X., & Bramel, J. (2014). *The Logic of Logistics: Theory, Algorithms, and Applications for Logistics Management*.
- **KaTeX**: https://katex.org/
- **Python**: https://www.python.org/
- **NumPy**: For numerical computations
- **NetworkX**: For graph algorithms
- **SciPy**: For optimization

---

*This directory structure supports academic learning and research in logistics and optimization.*
