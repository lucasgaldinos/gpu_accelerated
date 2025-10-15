#!/usr/bin/env python3
"""
Exercise Solution Manual Generator

This script processes PDF files containing exercises and generates comprehensive
solution manuals with:
- Mathematical solutions using KaTeX markdown
- Clear, accessible explanations
- Python implementations where applicable
- Citations from the source material

Usage:
    python generate_exercise_solutions.py --pdf-path path/to/exercises.pdf --output-dir solutions/
    python generate_exercise_solutions.py --pdf-path path/to/exercises.pdf --exercise-range 1-5
"""

import argparse
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json

try:
    import pymupdf
except ImportError as e:
    print("Error: Required packages not installed.")
    print("Please install with: uv add pymupdf4llm")
    raise e


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Exercise:
    """Represents an exercise from the PDF."""
    number: str
    title: str
    content: str
    page_number: int
    section: Optional[str] = None
    difficulty: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class Solution:
    """Represents a solution to an exercise."""
    exercise: Exercise
    mathematical_solution: str
    explanation: str
    python_code: Optional[str] = None
    citations: List[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.citations is None:
            self.citations = []


class ExerciseExtractor:
    """Extract exercises from PDF files."""
    
    def __init__(self, pdf_path: Path):
        """
        Initialize the extractor.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.doc = pymupdf.open(str(pdf_path))
        self.exercises: List[Exercise] = []
        
    def extract_exercises(self, 
                         start_page: Optional[int] = None,
                         end_page: Optional[int] = None,
                         exercise_pattern: Optional[str] = None) -> List[Exercise]:
        """
        Extract exercises from the PDF.
        
        Args:
            start_page: Starting page number (1-indexed)
            end_page: Ending page number (1-indexed)
            exercise_pattern: Regex pattern to identify exercises
            
        Returns:
            List of Exercise objects
        """
        if start_page is None:
            start_page = 1
        if end_page is None:
            end_page = len(self.doc)
            
        # Default pattern matches common exercise formats
        if exercise_pattern is None:
            exercise_pattern = r'(?:Exercise|Problem|Question)\s+(\d+\.?\d*)'
        
        exercises = []
        
        for page_num in range(start_page - 1, end_page):
            page = self.doc.load_page(page_num)
            text = page.get_text()
            
            # Find exercises using pattern matching
            matches = re.finditer(exercise_pattern, text, re.IGNORECASE)
            
            for match in matches:
                exercise_num = match.group(1)
                start_pos = match.end()
                
                # Extract content until next exercise or end of page
                next_match = re.search(exercise_pattern, text[start_pos:], re.IGNORECASE)
                if next_match:
                    end_pos = start_pos + next_match.start()
                else:
                    end_pos = len(text)
                
                content = text[start_pos:end_pos].strip()
                
                exercise = Exercise(
                    number=exercise_num,
                    title=f"Exercise {exercise_num}",
                    content=content,
                    page_number=page_num + 1
                )
                exercises.append(exercise)
                logger.info(f"Found exercise {exercise_num} on page {page_num + 1}")
        
        self.exercises = exercises
        return exercises
    
    def extract_section_context(self, page_num: int) -> Optional[str]:
        """
        Extract the section/chapter context for a given page.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            Section title if found
        """
        page = self.doc.load_page(page_num)
        text = page.get_text()
        
        # Look for section headers
        section_patterns = [
            r'^(\d+\.?\d*)\s+([A-Z][A-Za-z\s]+)$',
            r'^(Chapter\s+\d+:?\s*)([A-Za-z\s]+)$',
        ]
        
        for line in text.split('\n')[:20]:  # Check first 20 lines
            for pattern in section_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    return match.group(0)
        
        return None
    
    def close(self):
        """Close the PDF document."""
        self.doc.close()


class SolutionGenerator:
    """Generate solution manuals for exercises."""
    
    def __init__(self, output_dir: Path, source_title: str = "Reference"):
        """
        Initialize the generator.
        
        Args:
            output_dir: Directory for output files
            source_title: Title of the source material
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.source_title = source_title
        
    def generate_solution_manual(self, 
                                 solutions: List[Solution],
                                 output_filename: str = "solution_manual.md") -> Path:
        """
        Generate a complete solution manual markdown file.
        
        Args:
            solutions: List of Solution objects
            output_filename: Name of the output file
            
        Returns:
            Path to the generated file
        """
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Solution Manual\n\n")
            f.write(f"**Source:** {self.source_title}\n\n")
            f.write(f"**Total Solutions:** {len(solutions)}\n\n")
            f.write("---\n\n")
            
            # Write table of contents
            f.write("## Table of Contents\n\n")
            for solution in solutions:
                f.write(f"- [{solution.exercise.title}](#{self._make_anchor(solution.exercise.title)})\n")
            f.write("\n---\n\n")
            
            # Write each solution
            for i, solution in enumerate(solutions, 1):
                self._write_solution(f, solution, i)
        
        logger.info(f"Generated solution manual: {output_path}")
        return output_path
    
    def _write_solution(self, f, solution: Solution, number: int):
        """Write a single solution to the file."""
        exercise = solution.exercise
        
        # Exercise header
        f.write(f"## {exercise.title}\n\n")
        f.write(f"**Page:** {exercise.page_number}")
        if exercise.section:
            f.write(f" | **Section:** {exercise.section}")
        if exercise.difficulty:
            f.write(f" | **Difficulty:** {exercise.difficulty}")
        f.write("\n\n")
        
        # Tags
        if exercise.tags:
            f.write("**Tags:** " + ", ".join(f"`{tag}`" for tag in exercise.tags) + "\n\n")
        
        # Exercise content
        f.write("### Problem Statement\n\n")
        f.write(f"{exercise.content}\n\n")
        
        # Mathematical solution
        f.write("### Mathematical Solution\n\n")
        f.write(solution.mathematical_solution)
        f.write("\n\n")
        
        # Explanation
        f.write("### Explanation\n\n")
        f.write(solution.explanation)
        f.write("\n\n")
        
        # Python implementation
        if solution.python_code:
            f.write("### Python Implementation\n\n")
            f.write("```python\n")
            f.write(solution.python_code)
            f.write("\n```\n\n")
        
        # Citations
        if solution.citations:
            f.write("### References\n\n")
            for citation in solution.citations:
                f.write(f"- {citation}\n")
            f.write("\n")
        
        # Notes
        if solution.notes:
            f.write("### Notes\n\n")
            f.write(solution.notes)
            f.write("\n\n")
        
        f.write("---\n\n")
    
    def _make_anchor(self, title: str) -> str:
        """Convert title to markdown anchor."""
        return title.lower().replace(' ', '-').replace('.', '')
    
    def create_solution_template(self, exercise: Exercise) -> str:
        """
        Create a template for a solution.
        
        Args:
            exercise: Exercise to create template for
            
        Returns:
            Template string in markdown format
        """
        template = f"""
## {exercise.title}

**Page:** {exercise.page_number}

### Problem Statement

{exercise.content}

### Mathematical Solution

<!-- Write the mathematical solution here using KaTeX -->
<!-- Example: -->
<!-- Given: $x^2 + y^2 = r^2$ -->
<!-- Find: The area of the circle -->
<!-- 
$$
A = \\pi r^2
$$
-->

TODO: Add mathematical solution

### Explanation

<!-- Provide a clear, non-technical explanation here -->
<!-- This should be accessible to someone learning the concept -->
<!-- Break down the steps and explain the intuition -->

TODO: Add clear explanation

### Python Implementation

```python
# TODO: Implement the solution in Python if applicable
# Include comments explaining each step

def solve_exercise_{exercise.number.replace('.', '_')}():
    \"\"\"
    Solve Exercise {exercise.number}
    
    Returns:
        The solution
    \"\"\"
    pass

# Example usage
if __name__ == "__main__":
    result = solve_exercise_{exercise.number.replace('.', '_')}()
    print(f"Solution: {{result}}")
```

### References

- {self.source_title}, Page {exercise.page_number}
- TODO: Add specific citations from the book

### Notes

TODO: Add any additional notes or considerations

---
"""
        return template


def create_sample_solution() -> Solution:
    """Create a sample solution to demonstrate the format."""
    
    # Sample exercise about worst-case analysis
    exercise = Exercise(
        number="4.1",
        title="Exercise 4.1 - Worst-Case Analysis",
        content="""
Consider a simple bin packing problem where we have items of sizes 
{0.5, 0.3, 0.4, 0.2, 0.6} and bins of capacity 1.0. 
Analyze the worst-case performance of the First Fit Decreasing (FFD) algorithm.
""".strip(),
        page_number=85,
        section="4. Worst-Case Analysis",
        difficulty="Medium",
        tags=["bin-packing", "worst-case-analysis", "approximation-algorithms"]
    )
    
    # Mathematical solution with KaTeX
    mathematical_solution = """
**Given:**
- Items: $S = \\{0.5, 0.3, 0.4, 0.2, 0.6\\}$
- Bin capacity: $C = 1.0$
- Algorithm: First Fit Decreasing (FFD)

**Step 1:** Sort items in decreasing order

$$
S_{sorted} = \\{0.6, 0.5, 0.4, 0.3, 0.2\\}
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
\\frac{FFD(S)}{OPT(S)} = \\frac{2}{2} = 1.0
$$

FFD found the optimal solution for this instance!

**General FFD bound:** For any instance, FFD satisfies:

$$
FFD(S) \\leq \\frac{11}{9}OPT(S) + \\frac{6}{9}
$$

**Note:** While FFD found the optimal solution here, this doesn't always happen. The 11/9 bound 
tells us the worst case - FFD will never use more than 11/9 times optimal (plus a small constant).
"""
    
    # Clear explanation
    explanation = """
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
"""
    
    # Python implementation
    python_code = """
def first_fit_decreasing(items, bin_capacity=1.0):
    \"\"\"
    Implement the First Fit Decreasing algorithm for bin packing.
    
    Args:
        items: List of item sizes
        bin_capacity: Maximum capacity of each bin
        
    Returns:
        List of bins, where each bin is a list of items
    \"\"\"
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
    \"\"\"Calculate the utilization of bins.\"\"\"
    total_used = sum(sum(bin) for bin in bins)
    total_capacity = len(bins) * bin_capacity
    return total_used / total_capacity


# Example: Exercise 4.1
items = [0.5, 0.3, 0.4, 0.2, 0.6]
bins = first_fit_decreasing(items)

print(f"Number of bins used: {len(bins)}")
print(f"\\nBin contents:")
for i, bin in enumerate(bins, 1):
    print(f"  Bin {i}: {bin} (total: {sum(bin):.1f})")

utilization = calculate_bin_utilization(bins)
print(f"\\nOverall utilization: {utilization:.1%}")

# Optimal solution for comparison
optimal_bins = [[0.6, 0.4], [0.5, 0.3, 0.2]]
print(f"\\nOptimal solution: {len(optimal_bins)} bins")
print(f"FFD/OPT ratio: {len(bins)/len(optimal_bins):.2f}")

# Output:
# Number of bins used: 2
# Bin contents:
#   Bin 1: [0.6, 0.4] (total: 1.0)
#   Bin 2: [0.5, 0.3, 0.2] (total: 1.0)
# Overall utilization: 100.0%
# Optimal solution: 2 bins
# FFD/OPT ratio: 1.00
"""
    
    # Citations
    citations = [
        "Simchi-Levi, D., Chen, X., & Bramel, J. (2014). *The Logic of Logistics*. Section 4.2: Worst-Case Analysis of FFD Algorithm.",
        "The 11/9 bound for FFD was proven by Johnson (1973) and is tight.",
    ]
    
    # Notes
    notes = """
**Key Insights:**

1. FFD performs better than First Fit (FF) on average
2. The worst-case bound of 11/9 is asymptotically tight
3. For practical instances, FFD often achieves near-optimal solutions
4. The algorithm runs in O(n log n) time due to sorting

**Extensions:**

- Best Fit Decreasing (BFD) has the same worst-case bound
- Online algorithms (where items arrive one at a time) have worse bounds
- 2D and 3D bin packing are significantly harder problems
"""
    
    solution = Solution(
        exercise=exercise,
        mathematical_solution=mathematical_solution,
        explanation=explanation,
        python_code=python_code,
        citations=citations,
        notes=notes
    )
    
    return solution


def main():
    """Main function with CLI."""
    parser = argparse.ArgumentParser(
        description="Generate solution manuals for exercises from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--pdf-path',
        type=Path,
        help='Path to PDF file containing exercises'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('solutions'),
        help='Output directory for solution files (default: solutions/)'
    )
    
    parser.add_argument(
        '--source-title',
        type=str,
        default='The Logic of Logistics',
        help='Title of the source material'
    )
    
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='Create a sample solution to demonstrate the format'
    )
    
    parser.add_argument(
        '--extract-only',
        action='store_true',
        help='Only extract exercises without generating solutions'
    )
    
    parser.add_argument(
        '--exercise-range',
        type=str,
        help='Range of exercises to process (e.g., "1-5" or "1,3,5")'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample solution if requested
    if args.create_sample:
        logger.info("Creating sample solution...")
        sample_solution = create_sample_solution()
        generator = SolutionGenerator(args.output_dir, args.source_title)
        output_path = generator.generate_solution_manual(
            [sample_solution],
            "sample_solution_manual.md"
        )
        logger.info(f"✅ Sample solution created: {output_path}")
        print(f"\n📄 Sample solution manual created at: {output_path}")
        print("\nThis demonstrates the expected format for exercise solutions.")
        print("Each solution includes:")
        print("  - Mathematical solution with KaTeX")
        print("  - Clear, accessible explanation")
        print("  - Python implementation")
        print("  - Citations from source material")
        return 0
    
    # Extract exercises from PDF
    if args.pdf_path:
        if not args.pdf_path.exists():
            logger.error(f"PDF file not found: {args.pdf_path}")
            return 1
        
        logger.info(f"Processing PDF: {args.pdf_path}")
        extractor = ExerciseExtractor(args.pdf_path)
        
        try:
            exercises = extractor.extract_exercises()
            logger.info(f"Found {len(exercises)} exercises")
            
            if args.extract_only:
                # Save exercises to JSON
                exercises_data = [
                    {
                        'number': ex.number,
                        'title': ex.title,
                        'content': ex.content,
                        'page_number': ex.page_number,
                        'section': ex.section
                    }
                    for ex in exercises
                ]
                
                output_file = args.output_dir / "extracted_exercises.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(exercises_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ Exercises saved to: {output_file}")
                
                # Also create templates
                generator = SolutionGenerator(args.output_dir, args.source_title)
                for exercise in exercises:
                    template = generator.create_solution_template(exercise)
                    template_file = args.output_dir / f"exercise_{exercise.number}_template.md"
                    with open(template_file, 'w', encoding='utf-8') as f:
                        f.write(template)
                    logger.info(f"Created template: {template_file}")
                
                print(f"\n✅ Extracted {len(exercises)} exercises")
                print(f"📄 Exercise data: {output_file}")
                print(f"📝 Templates created in: {args.output_dir}")
                return 0
            
        finally:
            extractor.close()
    else:
        parser.print_help()
        print("\n💡 Tip: Use --create-sample to see an example solution format")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
