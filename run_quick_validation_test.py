#!/usr/bin/env python3
"""
Quick test of chapter4_validation with statistical analysis and table generation.
Runs only 3 small problems to demonstrate complete functionality.
"""

import sys
import subprocess
from pathlib import Path

# Temporarily modify PROBLEM_SET to only 3 problems
script_content = """
# Quick test - modify PROBLEM_SET temporarily
import sys
sys.path.insert(0, 'code/src')

# Import and run with modified problem set
import code.benchmarks.chapter4_validation as benchmark

# Backup original and replace with 3 problems for testing
original_problems = benchmark.PROBLEM_SET.copy()
benchmark.PROBLEM_SET = [
    {"name": "eil51", "optimal": 426, "size": 51},
    {"name": "berlin52", "optimal": 7542, "size": 52},
    {"name": "st70", "optimal": 675, "size": 70},
]

# Run benchmark
if __name__ == "__main__":
    benchmark.main()
"""

# Write temporary test script
test_file = Path("code/benchmarks/quick_test_chapter4.py")
with open(test_file, "w") as f:
    f.write(script_content)

print("Running quick test (3 problems × 3 algorithms × 2 reps = 18 runs)")
print("This demonstrates:")
print("  ✓ Complete statistical analysis (Shapiro-Wilk, Cohen's d, 95% CI)")
print("  ✓ Holm-Bonferroni multiple comparison correction")
print("  ✓ Table generation (Markdown + LaTeX)")
print()

# Run with 2 repetitions for speed
result = subprocess.run(
    ["python", str(test_file), "--repetitions", "2"], cwd=".", capture_output=False
)

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print()
print("Results saved to:")
print("  • results/tables/chapter4_validation.md  (GitHub tables)")
print("  • results/tables/chapter4_validation.tex (LaTeX thesis)")
print()
print("To run full benchmark (38 problems × 30 reps):")
print("  python code/benchmarks/chapter4_validation.py")
print()

# Cleanup
test_file.unlink()
sys.exit(result.returncode)
