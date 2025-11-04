"""
Unit tests for strategy wrapper equivalence.

Tests that wrapper classes produce equivalent results to underlying algorithms.

Test Coverage:
    - FFDStrategy ≈ FirstFitDecreasing (same bin assignments)
    - BFDStrategy ≈ BestFitDecreasing (same bin assignments)
    - NearestNeighborStrategy produces valid tours
    - ChristofidesStrategy produces valid tours
    - Backend parameter acceptance (xp=np works, xp=cp planned)

Dependencies:
    pytest, numpy
"""

import pytest
import numpy as np

# Import strategies
import sys

sys.path.insert(0, "../..")  # code/tests/unit → code/src

from algorithms.strategies.bin_packing_strategies import FFDStrategy, BFDStrategy
from algorithms.strategies.tsp_strategies import (
    NearestNeighborStrategy,
    ChristofidesStrategy,
)

# Import underlying algorithms for equivalence testing
from algorithms.bin_packing.construction.first_fit_decreasing import FirstFitDecreasing
from algorithms.bin_packing.construction.best_fit_decreasing import BestFitDecreasing
from algorithms.construction.nearest_neighbor import nearest_neighbor
from algorithms.construction.christofides import christofides
from data_models.problem import Problem


# ==============================================================================
# BIN PACKING EQUIVALENCE TESTS
# ==============================================================================


def test_ffd_strategy_equivalence():
    """Test FFDStrategy produces same results as FirstFitDecreasing."""
    demands = np.array([40, 30, 25, 20, 15])
    capacity = 100

    # Strategy wrapper result
    strategy = FFDStrategy()
    strategy_bins = strategy.pack(items=demands, capacity=capacity, xp=np)

    # Direct algorithm result
    algorithm = FirstFitDecreasing()
    direct_bins = algorithm.pack(items=demands, capacity=capacity)

    # Compare bin assignments
    assert len(strategy_bins) == len(direct_bins), (
        f"Different number of bins: {len(strategy_bins)} vs {len(direct_bins)}"
    )

    # Both should produce [[0, 1, 2], [3, 4]] for this input
    for i, (s_bin, d_bin) in enumerate(zip(strategy_bins, direct_bins)):
        assert set(s_bin) == set(d_bin), f"Bin {i} contents differ: {s_bin} vs {d_bin}"


def test_bfd_strategy_equivalence():
    """Test BFDStrategy produces same results as BestFitDecreasing."""
    demands = np.array([50, 30, 20, 15, 10])
    capacity = 100

    # Strategy wrapper result
    strategy = BFDStrategy()
    strategy_bins = strategy.pack(items=demands, capacity=capacity, xp=np)

    # Direct algorithm result
    algorithm = BestFitDecreasing()
    direct_bins = algorithm.pack(items=demands, capacity=capacity)

    # Compare bin assignments
    assert len(strategy_bins) == len(direct_bins), (
        f"Different number of bins: {len(strategy_bins)} vs {len(direct_bins)}"
    )

    for i, (s_bin, d_bin) in enumerate(zip(strategy_bins, direct_bins)):
        assert set(s_bin) == set(d_bin), f"Bin {i} contents differ: {s_bin} vs {d_bin}"


def test_ffd_strategy_accepts_backend_parameter():
    """Test FFDStrategy accepts xp parameter (protocol compliance)."""
    demands = np.array([40, 30, 25])
    capacity = 100

    strategy = FFDStrategy()

    # Should not raise error with xp=np
    bins = strategy.pack(items=demands, capacity=capacity, xp=np)
    assert len(bins) > 0, "Should produce bins"


def test_bfd_strategy_accepts_backend_parameter():
    """Test BFDStrategy accepts xp parameter (protocol compliance)."""
    demands = np.array([40, 30, 25])
    capacity = 100

    strategy = BFDStrategy()

    # Should not raise error with xp=np
    bins = strategy.pack(items=demands, capacity=capacity, xp=np)
    assert len(bins) > 0, "Should produce bins"


# ==============================================================================
# TSP CONSTRUCTION VALIDITY TESTS
# ==============================================================================


def test_nearest_neighbor_strategy_produces_valid_tour():
    """Test NearestNeighborStrategy produces valid tours."""
    locations = np.array(
        [
            [0.0, 0.0],  # Depot
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
        ]
    )
    customers = [1, 2, 3]

    strategy = NearestNeighborStrategy()
    tour = strategy.build_tour(customers=customers, locations=locations, xp=np)

    # Validation
    assert tour[0] == 0, f"Tour should start at depot, got {tour[0]}"
    assert tour[-1] == 0, f"Tour should end at depot, got {tour[-1]}"
    assert set(tour[1:-1]) == {1, 2, 3}, f"Tour should visit all customers: {tour}"
    assert len(tour) == len(customers) + 2, (
        f"Tour length should be {len(customers) + 2}"
    )


def test_christofides_strategy_produces_valid_tour():
    """Test ChristofidesStrategy produces valid tours."""
    locations = np.array(
        [
            [0.0, 0.0],  # Depot
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
        ]
    )
    customers = [1, 2, 3]

    strategy = ChristofidesStrategy()
    tour = strategy.build_tour(customers=customers, locations=locations, xp=np)

    # Validation
    assert tour[0] == 0, f"Tour should start at depot, got {tour[0]}"
    assert tour[-1] == 0, f"Tour should end at depot, got {tour[-1]}"
    assert set(tour[1:-1]) == {1, 2, 3}, f"Tour should visit all customers: {tour}"
    assert len(tour) == len(customers) + 2, (
        f"Tour length should be {len(customers) + 2}"
    )


def test_nearest_neighbor_strategy_accepts_backend():
    """Test NearestNeighborStrategy accepts xp parameter."""
    locations = np.array([[0, 0], [1, 0], [0, 1]])
    customers = [1, 2]

    strategy = NearestNeighborStrategy()

    # Should not raise error
    tour = strategy.build_tour(customers=customers, locations=locations, xp=np)
    assert len(tour) >= 3, (
        "Tour should have at least 3 nodes (depot + 2 customers + depot)"
    )


def test_christofides_strategy_accepts_backend():
    """Test ChristofidesStrategy accepts xp parameter."""
    locations = np.array([[0, 0], [1, 0], [0, 1]])
    customers = [1, 2]

    strategy = ChristofidesStrategy()

    # Should not raise error
    tour = strategy.build_tour(customers=customers, locations=locations, xp=np)
    assert len(tour) >= 3, "Tour should have at least 3 nodes"


# ==============================================================================
# ERROR HANDLING TESTS
# ==============================================================================


def test_nearest_neighbor_rejects_empty_customers():
    """Test NearestNeighborStrategy validates empty customer list."""
    locations = np.array([[0, 0], [1, 0]])
    customers = []

    strategy = NearestNeighborStrategy()

    with pytest.raises(ValueError, match="Customers list cannot be empty"):
        strategy.build_tour(customers=customers, locations=locations, xp=np)


def test_christofides_rejects_empty_customers():
    """Test ChristofidesStrategy validates empty customer list."""
    locations = np.array([[0, 0], [1, 0]])
    customers = []

    strategy = ChristofidesStrategy()

    with pytest.raises(ValueError, match="Customers list cannot be empty"):
        strategy.build_tour(customers=customers, locations=locations, xp=np)


def test_nearest_neighbor_rejects_depot_in_customers():
    """Test NearestNeighborStrategy rejects depot (0) in customer list."""
    locations = np.array([[0, 0], [1, 0], [0, 1]])
    customers = [0, 1]  # Invalid: includes depot

    strategy = NearestNeighborStrategy()

    with pytest.raises(ValueError, match="Depot.*should not be in customers"):
        strategy.build_tour(customers=customers, locations=locations, xp=np)


def test_christofides_rejects_depot_in_customers():
    """Test ChristofidesStrategy rejects depot (0) in customer list."""
    locations = np.array([[0, 0], [1, 0], [0, 1]])
    customers = [0, 1]  # Invalid: includes depot

    strategy = ChristofidesStrategy()

    with pytest.raises(ValueError, match="Depot.*should not be in customers"):
        strategy.build_tour(customers=customers, locations=locations, xp=np)


# ==============================================================================
# CONSISTENCY TESTS (Same Input → Deterministic Output)
# ==============================================================================


def test_ffd_strategy_deterministic():
    """Test FFDStrategy produces consistent results."""
    demands = np.array([40, 30, 25, 20, 15])
    capacity = 100

    strategy = FFDStrategy()
    bins1 = strategy.pack(items=demands, capacity=capacity, xp=np)
    bins2 = strategy.pack(items=demands, capacity=capacity, xp=np)

    # Should be identical
    assert bins1 == bins2, "FFDStrategy should be deterministic"


def test_bfd_strategy_deterministic():
    """Test BFDStrategy produces consistent results."""
    demands = np.array([40, 30, 25, 20, 15])
    capacity = 100

    strategy = BFDStrategy()
    bins1 = strategy.pack(items=demands, capacity=capacity, xp=np)
    bins2 = strategy.pack(items=demands, capacity=capacity, xp=np)

    # Should be identical
    assert bins1 == bins2, "BFDStrategy should be deterministic"


# ==============================================================================
# PARAMETRIZED TESTS
# ==============================================================================


@pytest.mark.parametrize(
    "demands,capacity",
    [
        (np.array([10, 20, 30]), 50),
        (np.array([15, 15, 15, 15]), 30),
        (np.array([5, 10, 15, 20, 25]), 40),
    ],
)
def test_ffd_bfd_always_valid(demands, capacity):
    """Test that FFD and BFD always produce valid packings."""
    ffd = FFDStrategy()
    bfd = BFDStrategy()

    ffd_bins = ffd.pack(items=demands, capacity=capacity, xp=np)
    bfd_bins = bfd.pack(items=demands, capacity=capacity, xp=np)

    # Check FFD bins
    for bin_items in ffd_bins:
        bin_demand = sum(demands[i] for i in bin_items)
        assert bin_demand <= capacity, f"FFD bin exceeds capacity: {bin_demand}"

    # Check BFD bins
    for bin_items in bfd_bins:
        bin_demand = sum(demands[i] for i in bin_items)
        assert bin_demand <= capacity, f"BFD bin exceeds capacity: {bin_demand}"


@pytest.mark.parametrize(
    "n_customers",
    [1, 2, 3, 5, 10],
)
def test_tsp_strategies_scale(n_customers):
    """Test TSP strategies work for various problem sizes."""
    # Generate random locations
    np.random.seed(42)
    locations = np.random.rand(n_customers + 1, 2) * 10.0
    locations[0] = [0.0, 0.0]  # Depot

    customers = list(range(1, n_customers + 1))

    # Test Nearest Neighbor
    nn = NearestNeighborStrategy()
    nn_tour = nn.build_tour(customers=customers, locations=locations, xp=np)
    assert len(nn_tour) == n_customers + 2, f"NN tour wrong length: {len(nn_tour)}"

    # Test Christofides
    ch = ChristofidesStrategy()
    ch_tour = ch.build_tour(customers=customers, locations=locations, xp=np)
    assert len(ch_tour) == n_customers + 2, (
        f"Christofides tour wrong length: {len(ch_tour)}"
    )


# ==============================================================================
# NOTES
# ==============================================================================

# Testing Strategy:
# 1. Equivalence: Wrappers produce same results as underlying algorithms
# 2. Validity: TSP tours are valid (depot start/end, customer coverage)
# 3. Backend acceptance: All strategies accept xp parameter
# 4. Error handling: Invalid inputs raise appropriate errors
# 5. Determinism: Same input produces same output
# 6. Scalability: Strategies work for various problem sizes

# Future Tests:
# - test_cupy_backend(): Test with xp=cupy (GPU backend)
# - test_performance_parity(): Benchmark wrapper overhead
# - test_memory_efficiency(): Compare memory usage
