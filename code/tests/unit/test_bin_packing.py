"""
Unit tests for bin packing algorithms (FFD and BFD).

Tests verify correctness, capacity constraints, and compare strategies.
"""

import pytest
import numpy as np
from src.algorithms.bin_packing.construction.first_fit_decreasing import (
    FirstFitDecreasing,
)
from src.algorithms.bin_packing.construction.best_fit_decreasing import (
    BestFitDecreasing,
)


class TestFirstFitDecreasing:
    """Test suite for First Fit Decreasing algorithm."""

    def test_basic_packing(self):
        """Test basic FFD packing with simple instance."""
        ffd = FirstFitDecreasing()
        demands = np.array([20, 30, 25, 40, 35])
        capacity = 100

        bins = ffd.pack(demands, capacity)

        # Verify all items are assigned
        all_indices = [idx for bin_items in bins for idx in bin_items]
        assert len(all_indices) == len(demands)
        assert set(all_indices) == set(range(len(demands)))

    def test_capacity_constraints(self):
        """Verify all bins respect capacity constraint."""
        ffd = FirstFitDecreasing()
        demands = np.array([45, 30, 25, 20, 15, 10])
        capacity = 100

        bins = ffd.pack(demands, capacity)

        # Check each bin's load
        for bin_indices in bins:
            load = sum(demands[idx] for idx in bin_indices)
            assert load <= capacity, f"Bin exceeds capacity: {load} > {capacity}"

    def test_perfect_packing(self):
        """Test case where items fit perfectly into bins."""
        ffd = FirstFitDecreasing()
        demands = np.array([50, 50, 40, 40, 30, 30])
        capacity = 100

        bins = ffd.pack(demands, capacity)

        # Should use 3 bins: [50,50], [40,40], [30,30] (if perfect)
        # Or similar perfect combinations
        assert len(bins) <= 3

        # Verify capacity constraints
        for bin_indices in bins:
            load = sum(demands[idx] for idx in bin_indices)
            assert load <= capacity

    def test_empty_items(self):
        """Test that empty items array raises error."""
        ffd = FirstFitDecreasing()

        with pytest.raises(ValueError, match="empty"):
            ffd.pack(np.array([]), capacity=100)

    def test_item_exceeds_capacity(self):
        """Test that oversized item raises error."""
        ffd = FirstFitDecreasing()
        demands = np.array([20, 30, 150])  # 150 > capacity

        with pytest.raises(ValueError, match="exceeds capacity"):
            ffd.pack(demands, capacity=100)

    def test_zero_capacity(self):
        """Test that zero capacity raises error."""
        ffd = FirstFitDecreasing()

        with pytest.raises(ValueError, match="positive"):
            ffd.pack(np.array([10, 20]), capacity=0)

    def test_single_item(self):
        """Test packing single item."""
        ffd = FirstFitDecreasing()
        demands = np.array([50])

        bins = ffd.pack(demands, capacity=100)

        assert len(bins) == 1
        assert bins[0] == [0]

    def test_all_items_fit_one_bin(self):
        """Test when all items fit in single bin."""
        ffd = FirstFitDecreasing()
        demands = np.array([10, 20, 15, 25])  # Sum = 70

        bins = ffd.pack(demands, capacity=100)

        assert len(bins) == 1
        assert len(bins[0]) == 4

    def test_sorting_behavior(self):
        """Verify FFD sorts items in descending order."""
        ffd = FirstFitDecreasing()
        assert ffd.uses_sorting() is True
        assert ffd.get_name() == "First Fit Decreasing"

    def test_typical_cvrp_instance(self):
        """Test with typical CVRP customer demands."""
        ffd = FirstFitDecreasing()
        # Customer demands (excluding depot)
        demands = np.array([18, 26, 11, 30, 21, 19, 15, 16, 29, 26])
        capacity = 60

        bins = ffd.pack(demands, capacity)

        # Verify feasibility
        for bin_indices in bins:
            load = sum(demands[idx] for idx in bin_indices)
            assert load <= capacity

        # All customers assigned
        all_indices = [idx for bin_items in bins for idx in bin_items]
        assert len(all_indices) == len(demands)


class TestBestFitDecreasing:
    """Test suite for Best Fit Decreasing algorithm."""

    def test_basic_packing(self):
        """Test basic BFD packing with simple instance."""
        bfd = BestFitDecreasing()
        demands = np.array([20, 30, 25, 40, 35])
        capacity = 100

        bins = bfd.pack(demands, capacity)

        # Verify all items are assigned
        all_indices = [idx for bin_items in bins for idx in bin_items]
        assert len(all_indices) == len(demands)
        assert set(all_indices) == set(range(len(demands)))

    def test_capacity_constraints(self):
        """Verify all bins respect capacity constraint."""
        bfd = BestFitDecreasing()
        demands = np.array([45, 30, 25, 20, 15, 10])
        capacity = 100

        bins = bfd.pack(demands, capacity)

        # Check each bin's load
        for bin_indices in bins:
            load = sum(demands[idx] for idx in bin_indices)
            assert load <= capacity, f"Bin exceeds capacity: {load} > {capacity}"

    def test_best_fit_optimization(self):
        """Test that BFD minimizes wasted space."""
        bfd = BestFitDecreasing()
        # Instance where best fit matters
        demands = np.array([40, 35, 25, 20, 15])
        capacity = 100

        bins = bfd.pack(demands, capacity)

        # Should pack efficiently: [40,35,25], [20,15]
        # Total waste should be minimized
        total_waste = 0
        for bin_indices in bins:
            load = sum(demands[idx] for idx in bin_indices)
            waste = capacity - load
            total_waste += waste

        # BFD should minimize total waste
        assert total_waste <= 65  # Reasonable upper bound

    def test_empty_items(self):
        """Test that empty items array raises error."""
        bfd = BestFitDecreasing()

        with pytest.raises(ValueError, match="empty"):
            bfd.pack(np.array([]), capacity=100)

    def test_item_exceeds_capacity(self):
        """Test that oversized item raises error."""
        bfd = BestFitDecreasing()
        demands = np.array([20, 30, 150])  # 150 > capacity

        with pytest.raises(ValueError, match="exceeds capacity"):
            bfd.pack(demands, capacity=100)

    def test_zero_capacity(self):
        """Test that zero capacity raises error."""
        bfd = BestFitDecreasing()

        with pytest.raises(ValueError, match="positive"):
            bfd.pack(np.array([10, 20]), capacity=0)

    def test_single_item(self):
        """Test packing single item."""
        bfd = BestFitDecreasing()
        demands = np.array([50])

        bins = bfd.pack(demands, capacity=100)

        assert len(bins) == 1
        assert bins[0] == [0]

    def test_all_items_fit_one_bin(self):
        """Test when all items fit in single bin."""
        bfd = BestFitDecreasing()
        demands = np.array([10, 20, 15, 25])  # Sum = 70

        bins = bfd.pack(demands, capacity=100)

        assert len(bins) == 1
        assert len(bins[0]) == 4

    def test_sorting_behavior(self):
        """Verify BFD sorts items in descending order."""
        bfd = BestFitDecreasing()
        assert bfd.uses_sorting() is True
        assert bfd.get_name() == "Best Fit Decreasing"

    def test_typical_cvrp_instance(self):
        """Test with typical CVRP customer demands."""
        bfd = BestFitDecreasing()
        # Customer demands (excluding depot)
        demands = np.array([18, 26, 11, 30, 21, 19, 15, 16, 29, 26])
        capacity = 60

        bins = bfd.pack(demands, capacity)

        # Verify feasibility
        for bin_indices in bins:
            load = sum(demands[idx] for idx in bin_indices)
            assert load <= capacity

        # All customers assigned
        all_indices = [idx for bin_items in bins for idx in bin_items]
        assert len(all_indices) == len(demands)


class TestFFDvsBFDComparison:
    """Compare FFD and BFD strategies."""

    def test_same_bin_count_simple(self):
        """For many instances, FFD and BFD use same number of bins."""
        demands = np.array([45, 30, 25, 20, 15])
        capacity = 100

        ffd = FirstFitDecreasing()
        bfd = BestFitDecreasing()

        ffd_bins = ffd.pack(demands, capacity)
        bfd_bins = bfd.pack(demands, capacity)

        # Both should use 2 bins for this instance
        assert len(ffd_bins) == len(bfd_bins) == 2

    def test_both_satisfy_capacity(self):
        """Both strategies must respect capacity constraints."""
        demands = np.array([50, 40, 35, 30, 25, 20, 15, 10])
        capacity = 100

        ffd = FirstFitDecreasing()
        bfd = BestFitDecreasing()

        ffd_bins = ffd.pack(demands, capacity)
        bfd_bins = bfd.pack(demands, capacity)

        # Check FFD bins
        for bin_indices in ffd_bins:
            load = sum(demands[idx] for idx in bin_indices)
            assert load <= capacity

        # Check BFD bins
        for bin_indices in bfd_bins:
            load = sum(demands[idx] for idx in bin_indices)
            assert load <= capacity

    def test_bfd_tighter_packing(self):
        """BFD generally produces tighter packing (less waste)."""
        # Instance where best fit makes difference
        demands = np.array([70, 30, 30, 30, 25, 25])
        capacity = 100

        ffd = FirstFitDecreasing()
        bfd = BestFitDecreasing()

        ffd_bins = ffd.pack(demands, capacity)
        bfd_bins = bfd.pack(demands, capacity)

        # Calculate total waste for each
        ffd_waste = sum(
            capacity - sum(demands[idx] for idx in bin_items) for bin_items in ffd_bins
        )
        bfd_waste = sum(
            capacity - sum(demands[idx] for idx in bin_items) for bin_items in bfd_bins
        )

        # BFD should have equal or less waste
        assert bfd_waste <= ffd_waste

    def test_large_instance_performance(self):
        """Test both strategies on larger instance."""
        np.random.seed(42)
        demands = np.random.randint(10, 50, size=50)
        capacity = 100

        ffd = FirstFitDecreasing()
        bfd = BestFitDecreasing()

        ffd_bins = ffd.pack(demands, capacity)
        bfd_bins = bfd.pack(demands, capacity)

        # Both should find valid solutions
        assert len(ffd_bins) > 0
        assert len(bfd_bins) > 0

        # BFD typically uses same or fewer bins
        assert len(bfd_bins) <= len(ffd_bins)
