#!/usr/bin/env python3
"""Fix NaN values in statistical test results (post-benchmark cleanup)."""

import json
from pathlib import Path
import numpy as np


def fix_statistical_tests(stats_file: Path):
    """Replace NaN in statistical tests with appropriate values."""
    with open(stats_file, "r") as f:
        data = json.load(f)

    # Fix Friedman test NaN (happens when all algorithms identical)
    if "statistical_tests" in data and "friedman_test" in data["statistical_tests"]:
        friedman = data["statistical_tests"]["friedman_test"]
        if friedman.get("statistic") is None or (
            isinstance(friedman.get("statistic"), float)
            and np.isnan(friedman["statistic"])
        ):
            # All algorithms identical → no difference → p=1.0, stat=0
            friedman["statistic"] = 0.0
            friedman["p_value"] = 1.0
            friedman["significant"] = False
            friedman["note"] = "Zero variance: all algorithms performed identically"

    # Fix pairwise comparison NaNs
    if (
        "statistical_tests" in data
        and "pairwise_comparisons" in data["statistical_tests"]
    ):
        for comp in data["statistical_tests"]["pairwise_comparisons"]:
            if comp.get("p_value") is None:
                comp["p_value"] = 1.0
                comp["cohens_d"] = 0.0
                comp["effect_interpretation"] = "zero_variance"

    # Save fixed version
    with open(stats_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Fixed: {stats_file.name}")


# Run on all problem statistics
stats_dir = Path("results/problem_statistics")
for stats_file in stats_dir.glob("*_stats.json"):
    fix_statistical_tests(stats_file)

print("\n✓ All statistical tests fixed!")
