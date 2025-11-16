"""
Crossover strategies for Genetic Algorithms.

Implements CrossoverStrategy protocol with various crossover operators:
- OrderCrossover: Standard OX operator for TSP (Davis 1985)

All implementations are:
- Backend-agnostic (work with numpy or cupy)
- Type-safe (conform to CrossoverStrategy protocol)
- Academically sound (based on published GA research)

References:
- Davis (1985): "Applying Adaptive Algorithms to Epistatic Domains"
- Goldberg & Lingle (1985): "Alleles, Loci, and the Traveling Salesman Problem"
- Fujimoto & Tsutsui (2011): "A highly parallel TSP solver for GPUs"
"""

from typing import Any, List
import numpy as np

# Note: CrossoverStrategy import is used for protocol conformance documentation
from ...protocols.strategy_protocols import CrossoverStrategy  # noqa: F401
from ...utils.strategy_registry import StrategyRegistry


@StrategyRegistry.register(
    category="crossover",
    name="order_crossover",
    description="Order Crossover (OX): preserves relative order from parent1, absolute positions from parent2",
    reference="Davis (1985) - Applying Adaptive Algorithms to Epistatic Domains",
    complexity_time="O(n)",
    complexity_space="O(n)",
    parameters={},
)
class OrderCrossover:
    """
    Order Crossover (OX) operator for TSP.

    Algorithm (Davis 1985):
        1. Select two random cut points [cut1, cut2)
        2. Copy segment parent2[cut1:cut2] to offspring
        3. Fill remaining positions with cities from parent1 in order
           (preserving relative order, skipping cities in copied segment)

    Time Complexity: O(n) where n is number of cities
    Space Complexity: O(n) for offspring array

    Properties:
        - Preserves relative order from parent1
        - Absolute positions from parent2 (in segment)
        - Standard for TSP (most common crossover)
        - Ensures valid tours (no duplicate cities)

    Reference:
        Davis, L. (1985). "Applying Adaptive Algorithms to Epistatic Domains."
        In Proceedings of IJCAI-85, pp. 162-164.

        Goldberg, D. E., & Lingle, R. (1985). "Alleles, Loci, and the Traveling
        Salesman Problem." In Proceedings of ICGA-1, pp. 154-159.

    Example:
        >>> strategy = OrderCrossover()
        >>> parent1 = [0, 1, 2, 3, 4, 5, 0]  # Tour with 5 cities
        >>> parent2 = [0, 3, 5, 1, 2, 4, 0]
        >>> offspring = strategy.crossover(parent1, parent2, problem=None, xp=np)
        >>> # offspring might be: [0, 1, 3, 5, 2, 4, 0]
        >>> # (segment from parent2, filled with parent1's order)
    """

    def crossover(
        self,
        parent1: Any,
        parent2: Any,
        problem: Any,
    ) -> Any:
        """
        Perform Order Crossover (OX) on two parent tours.

        Phase 3.5 Hybrid Bridge Architecture:
            - S-Task (Sequential): Crossover operations are CPU-only
            - Uses NumPy for random number generation
            - Permutation operations are too small to benefit from GPU parallelism

        Args:
            parent1: First parent tour [depot, c1, ..., ck, depot]
                - List or array of city indices
                - First and last elements are depot (typically 0)
            parent2: Second parent tour [depot, c1, ..., ck, depot]
                - Same structure as parent1
            problem: TSPProblem instance (not used by OX, but required by protocol)

        Returns:
            Offspring tour [depot, c1, ..., ck, depot]
                - Valid tour with same structure as parents
                - Contains each city exactly once
                - Starts and ends at depot

        Algorithm Details:
            1. Extract interior (exclude depots): parent1[1:-1]
            2. Select random cut points: [cut1, cut2) where 0 ≤ cut1 < cut2 < n
            3. Copy segment: offspring[cut1:cut2] = parent2[cut1:cut2]
            4. Fill remaining from parent1 in order:
               - Skip cities already in copied segment
               - Maintain parent1's relative order
            5. Add depots: [depot] + offspring_interior + [depot]

        Edge Cases:
            - Single customer (n=1): Returns copy of parent1
            - All cities in segment: Returns parent2 essentially
        """
        # Exclude depots for crossover
        p1_interior = parent1[1:-1]
        p2_interior = parent2[1:-1]
        n = len(p1_interior)

        # Edge case: single customer
        if n < 2:
            if hasattr(parent1, "copy"):
                return parent1.copy()
            return list(parent1)

        # Select two random cut points (CPU-only random generation)
        cut_points = np.random.choice(n, size=2, replace=False)
        cut1, cut2 = sorted(cut_points)

        # Initialize offspring interior
        offspring_interior = [None] * n

        # Step 1: Copy segment from parent2
        offspring_interior[cut1:cut2] = p2_interior[cut1:cut2]
        copied_cities = set(p2_interior[cut1:cut2])

        # Step 2: Fill remaining positions from parent1 in order
        p1_idx = 0
        for i in range(n):
            if offspring_interior[i] is None:
                # Find next city from parent1 not in copied segment
                while p1_interior[p1_idx] in copied_cities:
                    p1_idx += 1
                offspring_interior[i] = p1_interior[p1_idx]
                p1_idx += 1

        # Step 3: Add depots
        return [0] + offspring_interior + [0]


@StrategyRegistry.register(
    category="crossover",
    name="partially_mapped_crossover",
    description="Partially Mapped Crossover (PMX): preserves absolute positions with mapping to avoid duplicates",
    reference="Goldberg & Lingle (1985) - Alleles, Loci, and the Traveling Salesman Problem",
    complexity_time="O(n)",
    complexity_space="O(n)",
    parameters={},
)
class PartiallyMappedCrossover:
    """
    Partially Mapped Crossover (PMX) operator for TSP.

    Algorithm (Goldberg & Lingle 1985):
        1. Select two random cut points [cut1, cut2)
        2. Copy segment parent1[cut1:cut2] to offspring
        3. Create mapping from parent2[cut1:cut2] to parent1[cut1:cut2]
        4. Fill remaining positions using mapping to avoid duplicates

    Time Complexity: O(n) where n is number of cities
    Space Complexity: O(n) for offspring and mapping

    Properties:
        - Preserves absolute positions from parent1 (in segment)
        - Uses mapping to maintain tour validity
        - Alternative to OX (different preservation properties)

    Reference:
        Goldberg, D. E., & Lingle, R. (1985). "Alleles, Loci, and the Traveling
        Salesman Problem." In Proceedings of ICGA-1, pp. 154-159.

    Note:
        PMX is less commonly used than OX for TSP. Included for completeness
        and comparison studies. OX is generally preferred for pure TSP.

    Example:
        >>> strategy = PartiallyMappedCrossover()
        >>> parent1 = [0, 1, 2, 3, 4, 5, 0]
        >>> parent2 = [0, 3, 5, 1, 2, 4, 0]
        >>> offspring = strategy.crossover(parent1, parent2, problem=None, xp=np)
        >>> # offspring uses PMX mapping (different from OX result)
    """

    def crossover(
        self,
        parent1: Any,
        parent2: Any,
        problem: Any,
    ) -> Any:
        """
        Perform Partially Mapped Crossover (PMX).

        Phase 3.5 Hybrid Bridge Architecture:
            - S-Task (Sequential): Crossover operations are CPU-only
            - Uses NumPy for random number generation
            - Permutation operations are too small to benefit from GPU parallelism

        Args:
            parent1: First parent tour [depot, c1, ..., ck, depot]
            parent2: Second parent tour [depot, c1, ..., ck, depot]
            problem: TSPProblem instance (not used, required by protocol)

        Returns:
            Offspring tour [depot, c1, ..., ck, depot]

        Note:
            Implementation follows Goldberg & Lingle (1985) exactly as specified.
            Uses position-based mapping (NOT value→value dict) to avoid cycles.
            Reference: https://ultraevolution.org/blog/pmx_crossover/
        """
        # Exclude depots
        p1_interior = parent1[1:-1]
        p2_interior = parent2[1:-1]
        n = len(p1_interior)

        # Edge case: single customer
        if n < 2:
            if hasattr(parent1, "copy"):
                return parent1.copy()
            return list(parent1)

        # Select two random cut points (CPU-only random generation)
        cut_points = np.random.choice(n, size=2, replace=False)
        cut1, cut2 = sorted(cut_points)

        # Initialize offspring - start by copying entire parent1
        offspring_interior = list(p1_interior)

        # Step 1: Segment already copied (from parent1)

        # Step 2: Fill positions outside segment from parent2, resolving conflicts
        # Process left segment [0, cut1) and right segment [cut2, n)
        for i in list(range(0, cut1)) + list(range(cut2, n)):
            candidate = p2_interior[i]
            
            # If candidate already in middle segment, follow mapping chain
            # Mapping: find position of candidate in p1 segment, use p2's value at that position
            while candidate in p1_interior[cut1:cut2]:
                # Find WHERE candidate appears in parent1's segment
                segment_idx = p1_interior[cut1:cut2].index(candidate)
                actual_idx = cut1 + segment_idx
                # Replace with parent2's value at that POSITION
                candidate = p2_interior[actual_idx]
            
            offspring_interior[i] = candidate

        # Add depots
        return [0] + offspring_interior + [0]
