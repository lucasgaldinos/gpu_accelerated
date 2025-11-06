#!/usr/bin/env python3
"""
Fix Problem() calls in test_lazy_problem_context.py.

Adds missing coordinates=None or distances=None parameters to all Problem() constructor calls.
"""

import re

# Read the file
with open("code/tests/integration/test_lazy_problem_context.py", "r") as f:
    content = f.read()

# Pattern to match Problem( blocks
# Replace patterns that are missing the required parameters

# For coordinate-based problems (EUC_2D), add distances=None if not present
content = re.sub(
    r'(edge_type="EUC_2D",\s*\n\s*coordinates=np\.array\([^\)]+\),)',
    r"\1\n            distances=None,",
    content,
)

# For explicit distance problems, add coordinates=None if not present
content = re.sub(
    r'(edge_type="EXPLICIT",\s*\n\s*)(distances=)',
    r"\1coordinates=None,\n            \2",
    content,
)

# For CVRP problems, ensure both coordinates and demands have proper structure
content = re.sub(r"(coordinates=np\.array\([^\)]+\),\s*\n\s*demands=)", r"\1", content)

# Write back
with open("code/tests/integration/test_lazy_problem_context.py", "w") as f:
    f.write(content)

print("✅ Fixed Problem() calls in test_lazy_problem_context.py")
