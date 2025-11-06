"""
Report generation for benchmark results.

Generates publication-ready tables and plots following Section 4 (RESULTADOS)
format specifications.
"""

from typing import List
import numpy as np
from .statistics import StatisticalSummary


class ReportGenerator:
    """
    Generates tables and summaries from statistical analyses.

    Produces Markdown and LaTeX output compatible with Section 4 tables.

    Example:
        >>> from benchmarking import StatisticalAnalyzer, ReportGenerator
        >>> analyzer = StatisticalAnalyzer()
        >>> summary = analyzer.paired_comparison(cpu_times, gpu_times, ...)
        >>> reporter = ReportGenerator()
        >>> print(reporter.format_markdown_table([summary]))
    """

    def format_markdown_table(
        self, summaries: List[StatisticalSummary], show_speedup: bool = True
    ) -> str:
        """
        Generate Markdown table for statistical summaries.

        Format matches Section 4.1 (Table 4.1: 2-opt Time-to-Convergence).

        Args:
            summaries: List of statistical summaries
            show_speedup: Include speedup column (for runtime metrics)

        Returns:
            Formatted Markdown table string

        Example:
            >>> table = reporter.format_markdown_table(summaries)
            >>> print(table)
            | Instance | CPU (Mean ± CI) | GPU (Mean ± CI) | Speedup | p-value | Effect Size |
            |:---------|:----------------|:----------------|:--------|:--------|:------------|
            | berlin52 | 12.5 ± 0.3      | 1.3 ± 0.1       | 9.6x    | <0.001  | 2.45 (large)|
        """
        if not summaries:
            return "No data available."

        lines = []

        # Header
        header_row = "| Instance | CPU (Mean ± CI) | GPU (Mean ± CI) |"
        if show_speedup:
            header_row += " Speedup |"
        header_row += " p-value | Effect Size |"
        lines.append(header_row)

        # Separator
        sep_row = "|:---------|:----------------|:----------------|"
        if show_speedup:
            sep_row += ":--------|"
        sep_row += ":--------|:------------|"
        lines.append(sep_row)

        # Data rows
        for summary in summaries:
            # Instance name (from comparison label)
            instance = summary.comparison_label.split(":")[-1].strip()

            # Format means and CIs
            mean_a_str = f"{summary.mean_a:.2f}"
            ci_a_width = summary.ci_95_a[1] - summary.ci_95_a[0]
            ci_a_str = f"± {ci_a_width / 2:.2f}"

            mean_b_str = f"{summary.mean_b:.2f}"
            ci_b_width = summary.ci_95_b[1] - summary.ci_95_b[0]
            ci_b_str = f"± {ci_b_width / 2:.2f}"

            row = f"| {instance} | {mean_a_str} {ci_a_str} | {mean_b_str} {ci_b_str} |"

            if show_speedup:
                speedup = summary.get_speedup()
                row += f" {speedup:.1f}x |"

            # p-value
            if summary.p_value < 0.001:
                p_str = "< 0.001"
            else:
                p_str = f"{summary.p_value:.3f}"
            row += f" {p_str} |"

            # Effect size with interpretation
            effect_size_interp = self._interpret_effect_size(summary.effect_size)
            row += f" {summary.effect_size:.2f} ({effect_size_interp}) |"

            lines.append(row)

        return "\n".join(lines)

    def _interpret_effect_size(self, d: float) -> str:
        """
        Interpret Cohen's d effect size.

        Following Section 3.5.3 footnote [^cohens_d]:
        - |d| < 0.2: negligible
        - 0.2 ≤ |d| < 0.5: small
        - 0.5 ≤ |d| < 0.8: medium
        - |d| ≥ 0.8: large

        Args:
            d: Cohen's d value

        Returns:
            Interpretation string
        """
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"

    def summary_statistics(self, summaries: List[StatisticalSummary]) -> str:
        """
        Generate text summary of statistical results.

        Args:
            summaries: List of statistical summaries

        Returns:
            Formatted text summary

        Example:
            >>> print(reporter.summary_statistics(summaries))
            Statistical Summary (n=3 comparisons):
            - Significant differences: 3/3 (100.0%)
            - Mean effect size: 2.34 (large)
            - Tests used: wilcoxon_signed_rank (3)
        """
        if not summaries:
            return "No data available."

        n = len(summaries)
        significant_count = sum(1 for s in summaries if s.is_significant())
        mean_effect = np.mean([s.effect_size for s in summaries])

        # Count test types used
        test_counts = {}
        for s in summaries:
            test_counts[s.test_used] = test_counts.get(s.test_used, 0) + 1

        lines = [
            f"Statistical Summary (n={n} comparisons):",
            f"- Significant differences: {significant_count}/{n} ({100 * significant_count / n:.1f}%)",
            f"- Mean effect size: {mean_effect:.2f} ({self._interpret_effect_size(mean_effect)})",
            f"- Tests used: {', '.join(f'{k} ({v})' for k, v in test_counts.items())}",
        ]

        return "\n".join(lines)
