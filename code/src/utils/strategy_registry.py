"""
Strategy Registry for Dynamic Strategy Discovery and Composition.

This module provides a centralized registry for all strategy implementations,
enabling dynamic strategy discovery, validation, and instantiation.

The registry supports:
- Decorator-based registration (@register_strategy)
- Academic metadata tracking (papers, complexity, authors)
- Type-safe retrieval and validation
- Multiple strategy categories (selection, crossover, mutation, improvement)
- Extensibility for new strategy types

Example:
    >>> from code.src.utils.strategy_registry import StrategyRegistry
    >>>
    >>> # Registration (done automatically via decorator)
    >>> @StrategyRegistry.register("selection", "tournament")
    >>> class TournamentSelection:
    >>>     pass
    >>>
    >>> # Retrieval
    >>> strategy_class = StrategyRegistry.get("selection", "tournament")
    >>> instance = strategy_class(tournament_size=3)
    >>>
    >>> # List available
    >>> strategies = StrategyRegistry.list_strategies("selection")
    >>> print(strategies)  # ['tournament', 'roulette', 'crowding']

References:
    Registry pattern for extensible architecture design.
"""

from typing import Dict, Type, Any, List, Optional, TypedDict, Callable
import inspect


class StrategyMetadata(TypedDict, total=False):
    """
    Metadata for registered strategies.

    Attributes:
        name: Strategy name (lowercase, snake_case)
        category: Strategy category ('selection', 'crossover', 'mutation', etc.)
        description: Human-readable description
        reference: Academic paper reference (author, year, title)
        complexity_time: Time complexity (Big-O notation)
        complexity_space: Space complexity (Big-O notation)
        parameters: Dict of parameter names and descriptions
        author_implementation: Implementation author/contributor
    """

    name: str
    category: str
    description: str
    reference: str
    complexity_time: str
    complexity_space: str
    parameters: Dict[str, str]
    author_implementation: str


class StrategyRegistry:
    """
    Centralized registry for strategy implementations.

    Provides decorator-based registration and type-safe retrieval of strategies.
    Supports multiple strategy categories and metadata tracking for academic
    compliance and documentation.

    Architecture:
        - Generic: Works with any strategy type
        - Composable: Strategies can be mixed and matched
        - Extensible: New categories can be added without code changes
        - Type-safe: Validates strategy types at retrieval time

    Class Attributes:
        _registries: Nested dict {category: {name: class}}
        _metadata: Nested dict {category: {name: metadata}}

    Example:
        >>> # Register a strategy
        >>> @StrategyRegistry.register(
        ...     category="selection",
        ...     name="tournament",
        ...     description="Tournament selection (k-tournament)",
        ...     reference="Miller & Goldberg (1995)",
        ...     complexity_time="O(n_select × k)"
        ... )
        >>> class TournamentSelection:
        ...     pass
        >>>
        >>> # Retrieve and instantiate
        >>> cls = StrategyRegistry.get("selection", "tournament")
        >>> strategy = cls(tournament_size=3)
    """

    # Class-level registries (shared across all instances)
    _registries: Dict[str, Dict[str, Type]] = {
        "selection": {},
        "crossover": {},
        "mutation": {},
        "construction": {},  # For TSP construction heuristics (Nearest Neighbor, Christofides, etc.)
        "improvement": {},  # For 2-opt, 3-opt, etc.
        "cooling": {},  # For SA cooling schedules (future)
        "neighborhood": {},  # For neighborhood structures (future)
    }

    _metadata: Dict[str, Dict[str, StrategyMetadata]] = {
        "selection": {},
        "crossover": {},
        "mutation": {},
        "construction": {},
        "improvement": {},
        "cooling": {},
        "neighborhood": {},
    }

    @classmethod
    def register(
        cls,
        category: str,
        name: str,
        description: str = "",
        reference: str = "",
        complexity_time: str = "",
        complexity_space: str = "",
        parameters: Optional[Dict[str, str]] = None,
        author_implementation: str = "",
    ) -> Callable[[Type], Type]:
        """
        Decorator to register a strategy class.

        Args:
            category: Strategy category ('selection', 'crossover', 'mutation', etc.)
            name: Strategy name (lowercase, snake_case)
            description: Human-readable description
            reference: Academic paper reference (e.g., "Davis (1985)")
            complexity_time: Time complexity in Big-O notation
            complexity_space: Space complexity in Big-O notation
            parameters: Dict of parameter names to descriptions
            author_implementation: Implementation author/contributor

        Returns:
            Decorator function that registers the class

        Raises:
            ValueError: If category is not recognized
            ValueError: If strategy name already registered in category

        Example:
            >>> @StrategyRegistry.register(
            ...     category="selection",
            ...     name="tournament",
            ...     description="k-tournament selection",
            ...     reference="Miller & Goldberg (1995)",
            ...     complexity_time="O(n_select × k)",
            ...     parameters={"tournament_size": "Number of competitors (k)"}
            ... )
            >>> class TournamentSelection:
            ...     pass
        """
        # Validate category
        if category not in cls._registries:
            raise ValueError(
                f"Unknown strategy category '{category}'. "
                f"Available: {list(cls._registries.keys())}"
            )

        def decorator(strategy_class: Type) -> Type:
            # Check for duplicate registration
            if name in cls._registries[category]:
                existing = cls._registries[category][name]
                raise ValueError(
                    f"Strategy '{name}' already registered in category '{category}' "
                    f"(existing class: {existing.__name__})"
                )

            # Register the class
            cls._registries[category][name] = strategy_class

            # Store metadata
            metadata: StrategyMetadata = {
                "name": name,
                "category": category,
                "description": description,
                "reference": reference,
                "complexity_time": complexity_time,
                "complexity_space": complexity_space,
                "parameters": parameters or {},
                "author_implementation": author_implementation,
            }
            cls._metadata[category][name] = metadata

            return strategy_class

        return decorator

    @classmethod
    def get(cls, category: str, name: str) -> Type:
        """
        Retrieve a registered strategy class.

        Args:
            category: Strategy category
            name: Strategy name

        Returns:
            Strategy class (uninstantiated)

        Raises:
            ValueError: If category or strategy name not found

        Example:
            >>> strategy_class = StrategyRegistry.get("selection", "tournament")
            >>> instance = strategy_class(tournament_size=3)
        """
        # Validate category
        if category not in cls._registries:
            raise ValueError(
                f"Unknown strategy category '{category}'. "
                f"Available: {list(cls._registries.keys())}"
            )

        # Validate strategy name
        if name not in cls._registries[category]:
            available = list(cls._registries[category].keys())
            raise ValueError(
                f"Strategy '{name}' not found in category '{category}'. "
                f"Available: {available}"
            )

        return cls._registries[category][name]

    @classmethod
    def list_strategies(cls, category: str) -> List[str]:
        """
        List all registered strategies in a category.

        Args:
            category: Strategy category

        Returns:
            List of strategy names

        Raises:
            ValueError: If category not found

        Example:
            >>> strategies = StrategyRegistry.list_strategies("selection")
            >>> print(strategies)
            ['tournament', 'roulette', 'crowding']
        """
        if category not in cls._registries:
            raise ValueError(
                f"Unknown strategy category '{category}'. "
                f"Available: {list(cls._registries.keys())}"
            )

        return list(cls._registries[category].keys())

    @classmethod
    def get_metadata(cls, category: str, name: str) -> StrategyMetadata:
        """
        Retrieve metadata for a registered strategy.

        Args:
            category: Strategy category
            name: Strategy name

        Returns:
            Strategy metadata dictionary

        Raises:
            ValueError: If category or strategy name not found

        Example:
            >>> meta = StrategyRegistry.get_metadata("selection", "tournament")
            >>> print(meta['reference'])
            'Miller & Goldberg (1995)'
        """
        # Validate existence (will raise if not found)
        cls.get(category, name)

        return cls._metadata[category][name].copy()

    @classmethod
    def list_all_categories(cls) -> List[str]:
        """
        List all available strategy categories.

        Returns:
            List of category names

        Example:
            >>> categories = StrategyRegistry.list_all_categories()
            >>> print(categories)
            ['selection', 'crossover', 'mutation', 'improvement', ...]
        """
        return list(cls._registries.keys())

    @classmethod
    def clear_category(cls, category: str) -> None:
        """
        Clear all registrations in a category (for testing).

        Args:
            category: Strategy category to clear

        Raises:
            ValueError: If category not found

        Note:
            This is intended for unit testing only. Production code
            should not clear registrations.
        """
        if category not in cls._registries:
            raise ValueError(
                f"Unknown strategy category '{category}'. "
                f"Available: {list(cls._registries.keys())}"
            )

        cls._registries[category].clear()
        cls._metadata[category].clear()

    @classmethod
    def validate_strategy_signature(
        cls, category: str, name: str, expected_method: str, expected_params: List[str]
    ) -> bool:
        """
        Validate that a strategy has the expected method signature.

        Args:
            category: Strategy category
            name: Strategy name
            expected_method: Method name to check (e.g., "select", "crossover")
            expected_params: List of expected parameter names

        Returns:
            True if signature matches, False otherwise

        Example:
            >>> valid = StrategyRegistry.validate_strategy_signature(
            ...     "selection", "tournament", "select",
            ...     ["population", "fitness", "n_select", "xp"]
            ... )
        """
        strategy_class = cls.get(category, name)

        # Check if method exists
        if not hasattr(strategy_class, expected_method):
            return False

        # Check signature
        method = getattr(strategy_class, expected_method)
        sig = inspect.signature(method)
        actual_params = list(sig.parameters.keys())

        # Remove 'self' from instance methods
        if "self" in actual_params:
            actual_params.remove("self")

        # Check if expected params are present
        return all(param in actual_params for param in expected_params)
