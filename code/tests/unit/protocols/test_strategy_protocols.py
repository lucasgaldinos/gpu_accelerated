"""
Protocol validation tests.

Strategy: Create dummy implementations that do NOTHING
but satisfy protocol signatures. If mypy accepts them and
tests pass, protocols are correctly defined.
"""

import numpy as np
from typing import List, Tuple

from src.protocols.strategy_protocols import (
    NeighborStrategy,
    MutationOperator,
    CrossoverStrategy,
    ImprovementOperator,
)
from src.data_models.problem import Problem


# ===== DUMMY IMPLEMENTATIONS =====


class DummyNeighbor:
    """Validates NeighborStrategy protocol compliance."""

    def generate_neighbor(
        self, current_tour: List[int], problem: Problem, xp
    ) -> List[int]:
        # Identity function (valid protocol implementation)
        return current_tour


class DummyMutation:
    """Validates MutationOperator protocol compliance."""

    def mutate(self, individual: List[int], xp) -> List[int]:
        return individual


class DummyCrossover:
    """Validates CrossoverStrategy protocol compliance."""

    def crossover(
        self, parent1: List[int], parent2: List[int], xp
    ) -> Tuple[List[int], List[int]]:
        return parent1, parent2


class DummyImprovement:
    """Validates ImprovementOperator protocol compliance."""

    def improve(
        self, tour: List[int], problem: Problem, xp, max_iterations: int = 100
    ) -> List[int]:
        return tour


# ===== PROTOCOL COMPLIANCE TESTS =====


def test_neighbor_protocol_compliance():
    """Verify DummyNeighbor satisfies NeighborStrategy."""
    strategy: NeighborStrategy = DummyNeighbor()  # Type annotation validates protocol
    assert strategy is not None

    # Test call signature
    tour = [0, 1, 2, 3, 0]
    distances = np.array([[0, 1, 2, 3], [1, 0, 4, 5], [2, 4, 0, 6], [3, 5, 6, 0]])
    coordinates = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
    problem = Problem(
        name="test",
        dimension=4,
        problem_type="TSP",
        edge_type="EUC_2D",
        coordinates=coordinates,
        distances=distances,
    )

    neighbor = strategy.generate_neighbor(tour, problem, np)
    assert neighbor == tour  # Identity function


def test_mutation_protocol_compliance():
    """Verify DummyMutation satisfies MutationOperator."""
    operator: MutationOperator = DummyMutation()
    assert operator is not None

    individual = [0, 1, 2, 3, 0]
    mutated = operator.mutate(individual, np)
    assert mutated == individual


def test_crossover_protocol_compliance():
    """Verify DummyCrossover satisfies CrossoverStrategy."""
    strategy: CrossoverStrategy = DummyCrossover()
    assert strategy is not None

    parent1 = [0, 1, 2, 3, 0]
    parent2 = [0, 3, 2, 1, 0]
    child1, child2 = strategy.crossover(parent1, parent2, np)
    assert child1 == parent1
    assert child2 == parent2


def test_improvement_protocol_compliance():
    """Verify DummyImprovement satisfies ImprovementOperator."""
    operator: ImprovementOperator = DummyImprovement()
    assert operator is not None

    tour = [0, 1, 2, 3, 0]
    distances = np.array([[0, 1, 2, 3], [1, 0, 4, 5], [2, 4, 0, 6], [3, 5, 6, 0]])
    coordinates = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
    problem = Problem(
        name="test",
        dimension=4,
        problem_type="TSP",
        edge_type="EUC_2D",
        coordinates=coordinates,
        distances=distances,
    )

    improved = operator.improve(tour, problem, np, max_iterations=10)
    assert improved == tour


# ===== PROTOCOL METHOD SIGNATURE TESTS =====


def test_neighbor_strategy_has_generate_neighbor_method():
    """Verify NeighborStrategy requires generate_neighbor method."""
    strategy = DummyNeighbor()
    assert hasattr(strategy, "generate_neighbor")
    assert callable(strategy.generate_neighbor)


def test_mutation_operator_has_mutate_method():
    """Verify MutationOperator requires mutate method."""
    operator = DummyMutation()
    assert hasattr(operator, "mutate")
    assert callable(operator.mutate)


def test_crossover_strategy_has_crossover_method():
    """Verify CrossoverStrategy requires crossover method."""
    strategy = DummyCrossover()
    assert hasattr(strategy, "crossover")
    assert callable(strategy.crossover)


def test_improvement_operator_has_improve_method():
    """Verify ImprovementOperator requires improve method."""
    operator = DummyImprovement()
    assert hasattr(operator, "improve")
    assert callable(operator.improve)
