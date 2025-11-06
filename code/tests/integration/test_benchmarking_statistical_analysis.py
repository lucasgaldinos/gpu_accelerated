"""Integration tests for benchmarking statistical analysis pipeline.

Tests the complete statistical analysis infrastructure including:
- Normality testing (Shapiro-Wilk)
- Paired comparison tests (t-test, Wilcoxon)
- Effect size calculation (Cohen's d)
- Bootstrap confidence intervals
- Multiple comparison correction (Holm-Bonferroni)
- Report generation (Markdown, LaTeX)
- Data export (CSV, JSON)
- End-to-end integration
"""

import pytest
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from src.benchmarking.statistics import StatisticalAnalyzer, StatisticalSummary
from src.benchmarking.reporting import ReportGenerator
from src.benchmarking.runner import BenchmarkRunner, ALGORITHM_MAP
from src.benchmarking.config import BenchmarkConfig, BenchmarkResult
from src.protocols.problem_context import ProblemContext


# ============================================================================
# Test Data Generators
# ============================================================================


def generate_normal_data(mean: float, std: float, n: int, seed: int = 42) -> np.ndarray:
    """Generate normally distributed data with known parameters.

    Args:
        mean: Population mean
        std: Population standard deviation
        n: Sample size
        seed: Random seed for reproducibility

    Returns:
        Array of n samples from N(mean, std²)
    """
    np.random.seed(seed)
    return np.random.normal(mean, std, n)


def generate_nonnormal_data(scale: float, n: int, seed: int = 42) -> np.ndarray:
    """Generate non-normally distributed data (exponential).

    Args:
        scale: Exponential scale parameter (mean = scale)
        n: Sample size
        seed: Random seed for reproducibility

    Returns:
        Array of n samples from Exp(1/scale)
    """
    np.random.seed(seed)
    return np.random.exponential(scale, n)


def generate_constant_data(value: float, n: int) -> np.ndarray:
    """Generate constant array (zero variance edge case).

    Args:
        value: Constant value
        n: Sample size

    Returns:
        Array of n identical values
    """
    return np.full(n, value)


@dataclass(frozen=True)
class Problem:
    """Minimal problem dataclass for testing."""

    name: str
    dimension: int
    problem_type: str
    edge_type: str
    coordinates: Optional[np.ndarray]
    distances: Optional[np.ndarray]
    capacity: Optional[int] = None
    demands: Optional[np.ndarray] = None


def create_test_problem(n: int, seed: int = 42) -> Problem:
    """Create small random TSP problem for integration tests."""
    np.random.seed(seed)
    coords = np.random.rand(n, 2) * 100
    coords[0] = [0, 0]

    distances = np.sqrt(
        ((coords[:, np.newaxis] - coords[np.newaxis, :]) ** 2).sum(axis=2)
    )

    return Problem(
        name=f"test_{n}",
        dimension=n,
        problem_type="TSP",
        edge_type="EUC_2D",
        coordinates=coords,
        distances=distances,
    )


# ============================================================================
# Test Class 1: Normality Testing
# ============================================================================


class TestStatisticalAnalyzerNormality:
    """Test Shapiro-Wilk normality detection."""

    def test_detects_normal_data(self):
        """Verify Shapiro-Wilk accepts normally distributed data."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # Generate large normal sample (should pass normality test)
        data = generate_normal_data(mean=10.0, std=2.0, n=100, seed=42)

        p_value, is_normal = analyzer.test_normality(data)

        # With n=100 from normal distribution, p-value should be > 0.05
        assert p_value > 0.05, f"Expected p > 0.05 for normal data, got {p_value:.4f}"
        assert is_normal == True, "Should classify as normal distribution"

    def test_detects_nonnormal_data(self):
        """Verify Shapiro-Wilk rejects non-normally distributed data."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # Generate exponential sample (should fail normality test)
        data = generate_nonnormal_data(scale=5.0, n=100, seed=42)

        p_value, is_normal = analyzer.test_normality(data)

        # Exponential is highly non-normal, p-value should be < 0.05
        assert p_value < 0.05, (
            f"Expected p < 0.05 for non-normal data, got {p_value:.4f}"
        )
        assert is_normal == False, "Should classify as non-normal distribution"

    def test_handles_small_sample_size(self):
        """Verify graceful handling of n < 3 (Shapiro-Wilk requirement)."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # n=2 is below Shapiro-Wilk minimum
        data = np.array([1.0, 2.0])

        p_value, is_normal = analyzer.test_normality(data)

        # Should return (0.0, False) for small samples
        assert p_value == 0.0, "Should return 0.0 for n < 3"
        assert is_normal == False, "Should return False for n < 3"


# ============================================================================
# Test Class 2: Paired Comparison Tests
# ============================================================================


class TestStatisticalAnalyzerPairedComparison:
    """Test paired comparison with automatic test selection."""

    def test_selects_t_test_for_normal_data(self):
        """Verify paired t-test selected when both samples are normal."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # Generate paired normal data
        cpu_times = generate_normal_data(mean=12.0, std=2.0, n=30, seed=42)
        gpu_times = generate_normal_data(mean=1.5, std=0.3, n=30, seed=43)

        summary = analyzer.paired_comparison(
            cpu_times,
            gpu_times,
            label="Test: CPU vs GPU",
            metric_name="runtime_seconds",
        )

        # Should use parametric test
        assert summary.test_used == "paired_t_test", (
            "Should select t-test for normal data"
        )
        assert summary.is_normal == True, "Both samples should be classified as normal"
        assert summary.sample_size == 30, "Should preserve sample size"

        # Should detect significant difference (large effect)
        assert summary.p_value < 0.001, "Should detect highly significant difference"
        assert summary.effect_size > 2.0, "Should show large effect size"

    def test_selects_wilcoxon_for_nonnormal_data(self):
        """Verify Wilcoxon selected when data is non-normal."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # Generate paired non-normal data (exponential)
        cpu_times = generate_nonnormal_data(scale=10.0, n=30, seed=42)
        gpu_times = generate_nonnormal_data(scale=1.0, n=30, seed=43)

        summary = analyzer.paired_comparison(
            cpu_times,
            gpu_times,
            label="Test: CPU vs GPU",
            metric_name="runtime_seconds",
        )

        # Should use non-parametric test
        assert summary.test_used == "wilcoxon_signed_rank", (
            "Should select Wilcoxon for non-normal data"
        )
        assert summary.is_normal == False, "Should classify as non-normal"

        # Should still detect significant difference
        assert summary.p_value < 0.05, "Should detect significant difference"

    def test_calculates_confidence_intervals(self):
        """Verify 95% CI construction for means and differences."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # Generate data with known parameters
        data_a = generate_normal_data(mean=10.0, std=2.0, n=100, seed=42)
        data_b = generate_normal_data(mean=5.0, std=2.0, n=100, seed=43)

        summary = analyzer.paired_comparison(
            data_a, data_b, label="Test", metric_name="test_metric"
        )

        # CI for A should contain true mean (10.0)
        ci_a_low, ci_a_high = summary.ci_95_a
        assert ci_a_low < 10.0 < ci_a_high, (
            f"CI [{ci_a_low:.2f}, {ci_a_high:.2f}] should contain 10.0"
        )

        # CI for B should contain true mean (5.0)
        ci_b_low, ci_b_high = summary.ci_95_b
        assert ci_b_low < 5.0 < ci_b_high, (
            f"CI [{ci_b_low:.2f}, {ci_b_high:.2f}] should contain 5.0"
        )

        # CI for difference should contain true difference (5.0)
        ci_diff_low, ci_diff_high = summary.ci_95_difference
        assert ci_diff_low < 5.0 < ci_diff_high, (
            f"CI [{ci_diff_low:.2f}, {ci_diff_high:.2f}] should contain 5.0"
        )

    def test_raises_error_on_length_mismatch(self):
        """Verify error when paired arrays have different lengths."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        data_a = np.array([1.0, 2.0, 3.0])
        data_b = np.array([1.0, 2.0])  # Different length

        with pytest.raises(ValueError, match="Arrays must have same length"):
            analyzer.paired_comparison(data_a, data_b, "Test", "metric")


# ============================================================================
# Test Class 3: Effect Size Calculation
# ============================================================================


class TestStatisticalAnalyzerEffectSize:
    """Test Cohen's d effect size calculation."""

    def test_cohens_d_large_effect(self):
        """Verify Cohen's d detects large effect (d >= 0.8)."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # Generate data with large separation (5 standard deviations apart)
        data_a = generate_normal_data(mean=10.0, std=1.0, n=30, seed=42)
        data_b = generate_normal_data(mean=0.0, std=1.0, n=30, seed=43)

        d = analyzer.cohens_d(data_a, data_b)

        # Should detect large effect
        assert d > 0.8, f"Expected large effect (d > 0.8), got d={d:.2f}"
        assert d >= 5.0, f"With 5 SD separation, d should be ~10, got {d:.2f}"

    def test_cohens_d_zero_when_equal(self):
        """Verify Cohen's d = 0 when means are equal."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # Same distribution for both samples
        data_a = generate_normal_data(mean=5.0, std=1.0, n=30, seed=42)
        data_b = generate_normal_data(mean=5.0, std=1.0, n=30, seed=42)  # Same seed!

        d = analyzer.cohens_d(data_a, data_b)

        # Should be very close to zero
        assert abs(d) < 0.01, f"Expected d ≈ 0 for identical samples, got d={d:.4f}"

    def test_cohens_d_handles_zero_variance(self):
        """Verify graceful handling when both samples have zero variance."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # Constant arrays (zero variance)
        data_a = generate_constant_data(5.0, n=30)
        data_b = generate_constant_data(5.0, n=30)

        d = analyzer.cohens_d(data_a, data_b)

        # Should return 0.0 (pooled_std = 0)
        assert d == 0.0, "Should return 0.0 for zero variance samples"


# ============================================================================
# Test Class 4: Bootstrap Confidence Intervals
# ============================================================================


class TestStatisticalAnalyzerBootstrap:
    """Test bootstrap CI construction."""

    def test_bootstrap_ci_contains_true_mean(self):
        """Verify bootstrap CI contains true population mean."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # Generate data with known mean
        true_mean = 10.0
        data = generate_normal_data(mean=true_mean, std=2.0, n=100, seed=42)

        # Bootstrap 95% CI for mean
        ci_low, ci_high, samples = analyzer.bootstrap_ci(
            data, np.mean, confidence_level=0.95, n_resamples=1000
        )

        # CI should contain true mean
        assert ci_low < true_mean < ci_high, (
            f"CI [{ci_low:.2f}, {ci_high:.2f}] should contain true mean {true_mean}"
        )

        # Bootstrap samples should have correct shape
        assert samples.shape == (1000,), "Should return 1000 bootstrap samples"

    def test_bootstrap_ci_for_speedup_ratio(self):
        """Verify bootstrap CI for speedup ratio (A/B)."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # CPU and GPU times
        cpu_times = generate_normal_data(mean=10.0, std=1.0, n=50, seed=42)
        gpu_times = generate_normal_data(mean=1.0, std=0.2, n=50, seed=43)

        # Speedup ratios
        speedups = cpu_times / gpu_times

        # Bootstrap CI for mean speedup
        ci_low, ci_high, samples = analyzer.bootstrap_ci(
            speedups, np.mean, confidence_level=0.95, n_resamples=1000
        )

        # Expected speedup around 10x
        mean_speedup = np.mean(speedups)
        assert 8.0 < mean_speedup < 12.0, (
            f"Expected speedup ~10x, got {mean_speedup:.2f}x"
        )

        # CI should be reasonable
        assert ci_low > 0, "Speedup CI lower bound should be positive"
        assert ci_low < mean_speedup < ci_high, "CI should contain mean speedup"


# ============================================================================
# Test Class 5: Multiple Comparison Correction
# ============================================================================


class TestStatisticalAnalyzerMultipleComparisons:
    """Test Holm-Bonferroni correction."""

    def test_holm_bonferroni_correction(self):
        """Verify Holm-Bonferroni controls family-wise error rate."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # 4 p-values: 2 significant, 2 not significant
        p_values = [0.001, 0.02, 0.03, 0.15]

        results = analyzer.holm_bonferroni_correction(p_values, alpha=0.05)

        # Should return 4 results
        assert len(results) == 4, "Should return result for each p-value"

        # Check structure: (original_index, p_value, is_significant)
        for idx, p_val, is_sig in results:
            assert 0 <= idx < 4, f"Index {idx} out of range"
            assert p_val in p_values, f"p-value {p_val} not in original list"
            assert isinstance(is_sig, bool), "is_significant should be boolean"

        # First p-value (0.001) should be significant even after correction
        # Threshold: 0.05 / 4 = 0.0125
        first_result = [r for r in results if r[1] == 0.001][0]
        assert first_result[2] is True, "p=0.001 should be significant (< 0.0125)"

        # Last p-value (0.15) should not be significant
        last_result = [r for r in results if r[1] == 0.15][0]
        assert last_result[2] is False, "p=0.15 should not be significant"


# ============================================================================
# Test Class 6: Report Generation
# ============================================================================


class TestReportGeneration:
    """Test Markdown and LaTeX table generation."""

    def test_markdown_table_format(self):
        """Verify Markdown table has correct structure."""
        reporter = ReportGenerator()

        # Create sample summary
        summary = StatisticalSummary(
            comparison_label="berlin52",
            metric_name="runtime_seconds",
            sample_size=30,
            mean_a=12.5,
            mean_b=1.3,
            std_a=0.5,
            std_b=0.1,
            ci_95_a=(12.0, 13.0),
            ci_95_b=(1.2, 1.4),
            mean_difference=11.2,
            ci_95_difference=(10.8, 11.6),
            p_value=0.001,
            effect_size=2.45,
            test_used="paired_t_test",
            normality_p_value_a=0.8,
            normality_p_value_b=0.7,
            is_normal=True,
        )

        table = reporter.format_markdown_table([summary], show_speedup=True)

        # Check table structure
        lines = table.strip().split("\n")
        assert len(lines) >= 3, "Should have header, separator, and data row"

        # Check header row
        assert "Instance" in lines[0], "Should have Instance column"
        assert "CPU" in lines[0], "Should have CPU column"
        assert "GPU" in lines[0], "Should have GPU column"
        assert "Speedup" in lines[0], "Should have Speedup column"
        assert "p-value" in lines[0], "Should have p-value column"

        # Check data row contains key values
        data_row = lines[2]
        assert "berlin52" in data_row, "Should contain instance name"
        assert "12.5" in data_row or "12.50" in data_row, "Should contain mean_a"
        assert "1.3" in data_row or "1.30" in data_row, "Should contain mean_b"

    def test_speedup_calculation(self):
        """Verify speedup ratio calculation (A/B)."""
        summary = StatisticalSummary(
            comparison_label="test",
            metric_name="runtime",
            sample_size=10,
            mean_a=10.0,  # CPU
            mean_b=1.0,  # GPU
            std_a=1.0,
            std_b=0.1,
            ci_95_a=(9.0, 11.0),
            ci_95_b=(0.9, 1.1),
            mean_difference=9.0,
            ci_95_difference=(8.0, 10.0),
            p_value=0.001,
            effect_size=10.0,
            test_used="wilcoxon_signed_rank",
            normality_p_value_a=0.01,
            normality_p_value_b=0.02,
            is_normal=False,
        )

        speedup = summary.get_speedup()

        # Should be 10.0x
        assert speedup == pytest.approx(10.0, rel=0.01), (
            f"Expected speedup 10.0x, got {speedup:.2f}x"
        )


# ============================================================================
# Test Class 7: Data Export
# ============================================================================


class TestBenchmarkExport:
    """Test CSV and JSON export functionality."""

    def test_csv_export_format(self, tmp_path):
        """Verify CSV export creates correct file structure."""
        # Create minimal BenchmarkResult
        config = BenchmarkConfig(
            algorithm="GA", backend="numpy", instance_name="test_10", num_repetitions=3
        )

        results = [
            BenchmarkResult(
                config=config,
                run_id=i,
                random_seed=42 + i,
                runtime_seconds=1.5 + i * 0.1,
                final_tour_cost=100.0 + i * 10.0,
                final_tour=[0, 1, 2, 0],
                convergence_history=[(0, 120.0, 0.0), (100, 100.0 + i * 10.0, 1.0)],
                time_to_target=None,
                memory_peak_mb=50.0,
                validation_passed=True,
            )
            for i in range(3)
        ]

        # Export to CSV
        csv_path = tmp_path / "test_results.csv"
        runner = BenchmarkRunner()
        runner.export_csv(results, csv_path)

        # Verify file exists
        assert csv_path.exists(), "CSV file should be created"

        # Read and verify content
        with open(csv_path, "r") as f:
            lines = f.readlines()

        # Should have header + 3 data rows
        assert len(lines) == 4, f"Expected 4 lines (header + 3 rows), got {len(lines)}"

        # Check header
        header = lines[0].strip()
        assert "run_id" in header, "Should have run_id column"
        assert "runtime_seconds" in header, "Should have runtime_seconds column"
        assert "final_tour_cost" in header, "Should have final_tour_cost column"

        # Check first data row
        first_row = lines[1].strip().split(",")
        assert first_row[0] == "0", "First run_id should be 0"
        assert first_row[1] == "42", "First seed should be 42"

    def test_json_export_includes_convergence(self, tmp_path):
        """Verify JSON export includes full convergence history."""
        config = BenchmarkConfig(
            algorithm="SA", backend="numpy", instance_name="test_10"
        )

        result = BenchmarkResult(
            config=config,
            run_id=0,
            random_seed=42,
            runtime_seconds=2.5,
            final_tour_cost=150.0,
            final_tour=[0, 1, 2, 0],
            convergence_history=[(0, 200.0, 0.0), (100, 175.0, 0.5), (200, 150.0, 1.0)],
            time_to_target=0.8,
            memory_peak_mb=100.0,
            validation_passed=True,
        )

        # Export to JSON
        json_path = tmp_path / "test_results.json"
        runner = BenchmarkRunner()
        runner.export_json([result], json_path)

        # Verify file exists
        assert json_path.exists(), "JSON file should be created"

        # Read and verify content
        import json

        with open(json_path, "r") as f:
            data = json.load(f)

        # Should have config and results
        assert "config" in data, "Should have config field"
        assert "results" in data, "Should have results field"

        # Check convergence history is included
        first_result = data["results"][0]
        assert "convergence_history" in first_result, (
            "Should include convergence_history"
        )
        assert len(first_result["convergence_history"]) == 3, (
            "Should have 3 convergence points"
        )


# ============================================================================
# Test Class 8: End-to-End Integration
# ============================================================================


class TestEndToEndIntegration:
    """Test complete statistical analysis pipeline."""

    def test_statistical_pipeline_end_to_end(self):
        """Verify full pipeline: data generation → analysis → reporting."""
        # Step 1: Generate synthetic benchmark data
        cpu_times = generate_normal_data(mean=10.0, std=1.5, n=30, seed=42)
        gpu_times = generate_normal_data(mean=1.2, std=0.3, n=30, seed=43)

        # Step 2: Statistical analysis
        analyzer = StatisticalAnalyzer(alpha=0.05)
        summary = analyzer.paired_comparison(
            cpu_times,
            gpu_times,
            label="Test Instance: CPU vs GPU",
            metric_name="runtime_seconds",
        )

        # Step 3: Report generation
        reporter = ReportGenerator()
        table = reporter.format_markdown_table([summary], show_speedup=True)

        # Verify complete pipeline worked
        assert summary.p_value < 0.001, "Should detect significant difference"
        assert summary.effect_size > 2.0, "Should show large effect"
        assert "CPU vs GPU" in table, "Report should contain comparison info"
        assert len(table) > 100, "Report should be substantial"

    def test_time_to_target_tracking(self):
        """Verify time-to-target metric tracking in convergence data."""
        # This test validates that BenchmarkResult correctly stores time_to_target
        config = BenchmarkConfig(
            algorithm="SA",
            backend="numpy",
            instance_name="test_problem",
            target_gap=0.05,  # 5% from optimal
        )

        # Create result with time_to_target
        result = BenchmarkResult(
            config=config,
            run_id=0,
            random_seed=42,
            runtime_seconds=5.0,
            final_tour_cost=100.0,
            final_tour=[0, 1, 2, 0],
            convergence_history=[
                (0, 200.0, 0.0),
                (50, 150.0, 1.0),
                (100, 105.0, 2.5),  # Reached target at 2.5s
                (150, 100.0, 4.0),
            ],
            time_to_target=2.5,  # Reached at iteration 100
            memory_peak_mb=80.0,
            validation_passed=True,
        )

        # Verify time-to-target is captured
        assert result.time_to_target == 2.5, "Should capture time when target reached"
        assert len(result.convergence_history) == 4, (
            "Should have full convergence history"
        )

        # Verify cost progression
        costs = [point[1] for point in result.convergence_history]
        assert costs == [200.0, 150.0, 105.0, 100.0], "Costs should decrease over time"


# ============================================================================
# Test Class 9: Edge Cases and Robustness
# ============================================================================


class TestStatisticalAnalysisEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_results_export(self, tmp_path):
        """Verify graceful handling of empty results list."""
        runner = BenchmarkRunner()
        csv_path = tmp_path / "empty.csv"

        # Should not crash on empty list
        runner.export_csv([], csv_path)

        # File might not be created (implementation-dependent)
        # Just verify no exception was raised

    def test_single_sample_analysis(self):
        """Verify behavior with n=1 (degenerate case)."""
        analyzer = StatisticalAnalyzer(alpha=0.05)

        # Single data point
        data = np.array([5.0])

        p_value, is_normal = analyzer.test_normality(data)

        # Should handle gracefully (returns 0.0, False for n < 3)
        assert p_value == 0.0
        assert is_normal == False

    def test_significance_threshold_boundary(self):
        """Test is_significant() at alpha boundary."""
        summary = StatisticalSummary(
            comparison_label="test",
            metric_name="metric",
            sample_size=30,
            mean_a=10.0,
            mean_b=9.0,
            std_a=1.0,
            std_b=1.0,
            ci_95_a=(9.5, 10.5),
            ci_95_b=(8.5, 9.5),
            mean_difference=1.0,
            ci_95_difference=(0.5, 1.5),
            p_value=0.049,  # Just below 0.05
            effect_size=0.5,
            test_used="paired_t_test",
            normality_p_value_a=0.5,
            normality_p_value_b=0.5,
            is_normal=True,
        )

        # Should be significant at alpha=0.05
        assert summary.is_significant(alpha=0.05) is True, (
            "0.049 < 0.05 should be significant"
        )

        # Should not be significant at alpha=0.01
        assert summary.is_significant(alpha=0.01) is False, (
            "0.049 > 0.01 should not be significant"
        )
