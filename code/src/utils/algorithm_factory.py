"""
Algorithm Factory for dynamic algorithm instantiation from JSON configurations.

This module provides a factory pattern for creating algorithm instances from
JSON or dictionary configurations, enabling:

1. Dynamic strategy composition
2. Configuration-driven experimentation
3. Reproducible algorithm setups
4. Higher-order metaheuristics support

Example Usage:
    >>> # From JSON file
    >>> algorithm = AlgorithmFactory.from_json("config/ga_tournament.json")
    >>> solution = algorithm.solve(problem)
    >>>
    >>> # From dictionary
    >>> config = {
    >>>     "algorithm": "genetic_algorithm",
    >>>     "backend": "cupy",
    >>>     "strategies": {
    >>>         "selection": {"name": "tournament", "params": {"tournament_size": 3}},
    >>>         "crossover": {"name": "order_crossover", "params": {}},
    >>>         "mutation": {"name": "swap", "params": {}}
    >>>     },
    >>>     "hyperparameters": {
    >>>         "population_size": 100,
    >>>         "max_generations": 1000,
    >>>         "crossover_rate": 0.9,
    >>>         "mutation_rate": 0.1
    >>>     }
    >>> }
    >>> algorithm = AlgorithmFactory.from_dict(config)

JSON Schema:
    {
        "algorithm": str,  # "genetic_algorithm" | "simulated_annealing"
        "backend": str,    # "numpy" | "cupy" (optional, default: "numpy")
        "strategies": {
            "<category>": {
                "name": str,         # Strategy name in registry
                "params": dict       # Strategy constructor parameters (optional)
            }
        },
        "hyperparameters": dict  # Algorithm-specific hyperparameters (optional)
    }

References:
    - Factory pattern: Gamma et al. (1994) - Design Patterns
    - Configuration-driven design: Fowler (2002) - Patterns of Enterprise Application Architecture
"""

from typing import Any, Dict, List
import json
from pathlib import Path

from .strategy_registry import StrategyRegistry


class AlgorithmFactory:
    """
    Factory for creating algorithm instances from JSON configurations.

    This class provides static methods for:
    1. Loading configurations from JSON files or dictionaries
    2. Validating configurations (algorithm types, strategies, backends)
    3. Instantiating strategies from the registry
    4. Creating algorithm instances with composed strategies

    All methods are static (no instance state needed).
    """

    @staticmethod
    def from_json(json_path: str) -> Any:
        """
        Create algorithm instance from JSON configuration file.

        Parameters
        ----------
        json_path : str
            Path to JSON configuration file.

        Returns
        -------
        algorithm : Any
            Instantiated algorithm (GeneticAlgorithm, SimulatedAnnealing, etc.)

        Raises
        ------
        FileNotFoundError
            If JSON file doesn't exist.
        ValueError
            If configuration is invalid (see validate_config for details).

        Example
        -------
        >>> algorithm = AlgorithmFactory.from_json("configs/ga_tournament.json")
        >>> solution = algorithm.solve(problem)
        """
        # Load JSON file
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {json_path}")

        with open(json_path, "r") as f:
            config = json.load(f)

        # Use from_dict for actual instantiation
        return AlgorithmFactory.from_dict(config)

    @staticmethod
    def from_dict(config: Dict[str, Any]) -> Any:
        """
        Create algorithm instance from configuration dictionary.

        Parameters
        ----------
        config : Dict[str, Any]
            Configuration dictionary with algorithm type, strategies, and hyperparameters.

        Returns
        -------
        algorithm : Any
            Instantiated algorithm with composed strategies.

        Raises
        ------
        ValueError
            If configuration is invalid. Error message lists all validation failures.

        Example
        -------
        >>> config = {
        >>>     "algorithm": "genetic_algorithm",
        >>>     "backend": "numpy",
        >>>     "strategies": {
        >>>         "selection": {"name": "tournament", "params": {"tournament_size": 3}},
        >>>         "crossover": {"name": "order_crossover"},
        >>>         "mutation": {"name": "swap"}
        >>>     },
        >>>     "hyperparameters": {"population_size": 100}
        >>> }
        >>> algorithm = AlgorithmFactory.from_dict(config)
        """
        # Step 1: Validate configuration
        errors = AlgorithmFactory.validate_config(config)
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            raise ValueError(error_msg)

        # Step 2: Extract configuration fields
        algorithm_type = config["algorithm"]
        backend = config.get("backend", "numpy")
        strategies_config = config.get("strategies", {})
        hyperparameters = config.get("hyperparameters", {})

        # Step 3: Instantiate strategies
        strategies = AlgorithmFactory._instantiate_strategies(
            algorithm_type=algorithm_type,
            strategies_config=strategies_config,
            backend=backend,
        )

        # Step 4: Instantiate algorithm
        algorithm = AlgorithmFactory._instantiate_algorithm(
            algorithm_type=algorithm_type,
            backend=backend,
            strategies=strategies,
            hyperparameters=hyperparameters,
        )

        return algorithm

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration dictionary without instantiating.

        Parameters
        ----------
        config : Dict[str, Any]
            Configuration dictionary to validate.

        Returns
        -------
        errors : List[str]
            List of validation error messages. Empty list if valid.

        Example
        -------
        >>> errors = AlgorithmFactory.validate_config(config)
        >>> if errors:
        >>>     print("Invalid configuration:")
        >>>     for error in errors:
        >>>         print(f"  - {error}")
        """
        errors = []

        # Check required field: algorithm
        if "algorithm" not in config:
            errors.append("Missing required field 'algorithm'")
            return errors  # Can't proceed without algorithm type

        algorithm_type = config["algorithm"]

        # Validate algorithm type
        supported_algorithms = ["genetic_algorithm", "simulated_annealing"]
        if algorithm_type not in supported_algorithms:
            errors.append(
                f"Unknown algorithm type '{algorithm_type}'. "
                f"Supported: {', '.join(supported_algorithms)}"
            )
            return errors  # Can't proceed without valid algorithm type

        # Validate backend
        backend = config.get("backend", "numpy")
        if backend not in ["numpy", "cupy"]:
            errors.append(f"Unknown backend '{backend}'. Supported: 'numpy', 'cupy'")
        elif backend == "cupy":
            # Check if cupy is installed
            try:
                import cupy  # noqa: F401
            except ImportError:
                errors.append(
                    "Backend 'cupy' selected but cupy is not installed. "
                    "Install with: pip install cupy-cuda12x"
                )

        # Validate strategies field
        strategies_config = config.get("strategies", {})
        if not isinstance(strategies_config, dict):
            errors.append("Field 'strategies' must be a dictionary")
            return errors

        # Check required strategies for each algorithm type
        if algorithm_type == "genetic_algorithm":
            required_strategies = ["selection", "crossover", "mutation"]
            for strategy_type in required_strategies:
                if strategy_type not in strategies_config:
                    errors.append(
                        f"Genetic Algorithm requires '{strategy_type}' strategy"
                    )

        elif algorithm_type == "simulated_annealing":
            # SA requires neighborhood strategy
            required_strategies = ["neighborhood"]
            for strategy_type in required_strategies:
                if strategy_type not in strategies_config:
                    errors.append(
                        f"Simulated Annealing requires '{strategy_type}' strategy"
                    )

        # Validate each strategy configuration
        for category, strategy_config in strategies_config.items():
            # Check strategy config structure
            if not isinstance(strategy_config, dict):
                errors.append(f"Strategy '{category}' config must be a dictionary")
                continue

            # Check required field: name
            if "name" not in strategy_config:
                errors.append(f"Strategy '{category}' missing required field 'name'")
                continue

            strategy_name = strategy_config["name"]

            # Check if strategy exists in registry
            try:
                StrategyRegistry.get(category, strategy_name)
            except ValueError as e:
                # Registry provides helpful error message with available strategies
                errors.append(str(e))

            # Validate params field (if present)
            if "params" in strategy_config:
                params = strategy_config["params"]
                if not isinstance(params, dict):
                    errors.append(f"Strategy '{category}' params must be a dictionary")

        return errors

    @staticmethod
    def _instantiate_strategies(
        algorithm_type: str,
        strategies_config: Dict[str, Dict[str, Any]],
        backend: str,
    ) -> Dict[str, Any]:
        """
        Instantiate strategy objects from configuration.

        Parameters
        ----------
        algorithm_type : str
            Algorithm type ("genetic_algorithm", "simulated_annealing").
        strategies_config : Dict[str, Dict[str, Any]]
            Dictionary of strategy configurations by category.
        backend : str
            Backend to use ("numpy" or "cupy").

        Returns
        -------
        strategies : Dict[str, Any]
            Dictionary of instantiated strategy objects by category.

        Raises
        ------
        TypeError
            If strategy instantiation fails due to invalid parameters.
        """
        strategies = {}

        for category, strategy_config in strategies_config.items():
            strategy_name = strategy_config["name"]
            strategy_params = strategy_config.get("params", {})

            # Get strategy class from registry
            strategy_class = StrategyRegistry.get(category, strategy_name)

            # Instantiate with parameters
            try:
                strategy_instance = strategy_class(**strategy_params)
            except TypeError as e:
                raise TypeError(
                    f"Failed to instantiate {category} strategy '{strategy_name}': {e}"
                )

            strategies[category] = strategy_instance

        return strategies

    @staticmethod
    def _instantiate_algorithm(
        algorithm_type: str,
        backend: str,
        strategies: Dict[str, Any],
        hyperparameters: Dict[str, Any],
    ) -> Any:
        """
        Instantiate algorithm with composed strategies.

        Parameters
        ----------
        algorithm_type : str
            Algorithm type ("genetic_algorithm", "simulated_annealing").
        backend : str
            Backend to use ("numpy" or "cupy").
        strategies : Dict[str, Any]
            Dictionary of instantiated strategy objects.
        hyperparameters : Dict[str, Any]
            Algorithm-specific hyperparameters.

        Returns
        -------
        algorithm : Any
            Instantiated algorithm instance.

        Raises
        ------
        NotImplementedError
            If algorithm type not yet supported (e.g., SA in PHASE 7).
        TypeError
            If algorithm instantiation fails due to invalid parameters.
        """
        if algorithm_type == "genetic_algorithm":
            # Import GeneticAlgorithm (lazy import to avoid circular dependencies)
            from ..algorithms.metaheuristics.genetic_algorithm import (
                GeneticAlgorithm,
            )

            # Get improvement strategy (optional, defaults to None)
            improvement_strategy = strategies.get("improvement", None)

            # Get construction strategy (optional, defaults to None → Random)
            construction_strategy = strategies.get("construction", None)

            # Map strategies to GA constructor parameters
            try:
                algorithm = GeneticAlgorithm(
                    selection_strategy=strategies["selection"],
                    crossover_strategy=strategies["crossover"],
                    mutation_strategy=strategies["mutation"],
                    improvement_strategy=improvement_strategy,  # Optional
                    construction_strategy=construction_strategy,  # Optional (NEW)
                    backend=backend,
                )

                # Set hyperparameters via set_params()
                if hyperparameters:
                    algorithm.set_params(**hyperparameters)

            except TypeError as e:
                raise TypeError(f"Failed to instantiate GeneticAlgorithm: {e}")

            return algorithm

        elif algorithm_type == "simulated_annealing":
            # Import SimulatedAnnealing
            from ..algorithms.metaheuristics.simulated_annealing import (
                SimulatedAnnealing,
            )

            # SA requires neighborhood_strategy
            if "neighborhood" not in strategies:
                raise ValueError(
                    "Simulated Annealing requires 'neighborhood' strategy in configuration"
                )

            # Get improvement strategy (optional, defaults to None)
            improvement_strategy = strategies.get("improvement", None)

            # Instantiate SA with neighborhood strategy
            try:
                algorithm = SimulatedAnnealing(
                    neighbor_strategy=strategies["neighborhood"],
                    improvement_strategy=improvement_strategy,  # Optional
                    backend=backend,
                )

                # Set hyperparameters via set_params()
                if hyperparameters:
                    algorithm.set_params(**hyperparameters)

            except TypeError as e:
                raise TypeError(f"Failed to instantiate SimulatedAnnealing: {e}")

            return algorithm

        else:
            # Should not reach here if validate_config passed
            raise ValueError(f"Unsupported algorithm type '{algorithm_type}'")
