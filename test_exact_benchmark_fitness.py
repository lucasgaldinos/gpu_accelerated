#!/usr/bin/env python3
"""Test to replicate exact benchmark fitness calculation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "code"))

import numpy as np
import cupy as cp
from src.loaders.database_loader import DatabaseLoader
from src.protocols.problem_context import ProblemContext

# Load kroA100
db_path = Path("datasets/routing.duckdb")
with DatabaseLoader(str(db_path)) as loader:
    problem = loader.load("kroA100")

# Create context with GPU backend (as benchmark does)
context = ProblemContext(problem, xp=cp)

# Get distances THE SAME WAY GA does
distances_cpu = context.get_cpu_distances()

print(f"Distance matrix type: {type(distances_cpu)}")
print(f"Distance matrix dtype: {distances_cpu.dtype}")
print(f"Distance matrix shape: {distances_cpu.shape}")
print(f"Sample distances [0, 1:6]: {distances_cpu[0, 1:6]}")
print()

# Test tour cost calculation EXACTLY as GA does
np.random.seed(42)
n = problem.dimension
tour = np.random.permutation(n).astype(np.int32)

# Method 1: Exactly as GA fitness function
cost_ga_method = 0.0
for j in range(len(tour)):
    city_from = tour[j]
    city_to = tour[(j + 1) % len(tour)]
    cost_ga_method += distances_cpu[city_from, city_to]

print(f"Tour cost (GA method): {cost_ga_method}")
print(f"TSPLIB optimal: 21282")
print(f"Below optimal?: {cost_ga_method < 21282} ← Should be FALSE!")
print()

# Check if distances are actually floats or ints
print(f"Are distances integers?: {np.all(distances_cpu == distances_cpu.astype(int))}")
print(f"Min distance: {distances_cpu[distances_cpu > 0].min()}")
print(f"Max distance: {distances_cpu.max()}")
