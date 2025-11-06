#!/usr/bin/env python3
"""
Validation script for TspMetaheuristicStrategy protocol.

Verifies that the protocol is correctly defined and documents expected
behavior for implementations (Genetic Algorithm, Simulated Annealing, etc.).

This is a PROTOCOL VALIDATION script - it checks the protocol structure,
not algorithm implementations (those will be validated separately).

Usage:
    uv run python scripts/validate_metaheuristic_protocol.py
"""

import sys
from typing import Protocol, get_type_hints, get_origin, get_args
import inspect


def validate_protocol_structure():
    """Validate TspMetaheuristicStrategy protocol structure."""
    try:
        from src.protocols.algorithm_strategies import TspMetaheuristicStrategy
    except ImportError as e:
        print(f"❌ Failed to import TspMetaheuristicStrategy: {e}")
        return False

    print("=" * 80)
    print("TspMetaheuristicStrategy Protocol Validation")
    print("=" * 80)
    print()

    # Check that it's a Protocol
    if not issubclass(TspMetaheuristicStrategy.__class__, type(Protocol)):
        print("❌ TspMetaheuristicStrategy is not a Protocol")
        return False
    print("✅ TspMetaheuristicStrategy is a Protocol")

    # Check required methods
    required_methods = {
        "set_params": {
            "description": "Configure metaheuristic hyperparameters",
            "returns": None,
            "params": ["hyperparameters"],
        },
        "build_tour_with_stats": {
            "description": "Construct tour with optimization statistics",
            "returns": tuple,
            "params": ["context", "customers"],
        },
        "get_stats": {
            "description": "Retrieve statistics from most recent run",
            "returns": dict,
            "params": [],
        },
    }

    print()
    print("Method Validation:")
    print("-" * 80)

    all_methods_present = True
    for method_name, expected in required_methods.items():
        if not hasattr(TspMetaheuristicStrategy, method_name):
            print(f"❌ Missing method: {method_name}")
            all_methods_present = False
            continue

        method = getattr(TspMetaheuristicStrategy, method_name)

        # Check it's callable
        if not callable(method):
            print(f"❌ {method_name} is not callable")
            all_methods_present = False
            continue

        # Get signature
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        # Remove 'self' from params list for comparison
        if "self" in params:
            params.remove("self")

        # Validate parameters
        if method_name == "set_params":
            # set_params should accept **kwargs
            has_kwargs = any(
                p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
            )
            if has_kwargs:
                print(f"✅ {method_name}() - accepts **hyperparameters")
            else:
                print(f"❌ {method_name}() - should accept **hyperparameters")
                all_methods_present = False
        else:
            # Check parameter count matches
            expected_params = expected["params"]
            if params == expected_params:
                print(f"✅ {method_name}({', '.join(params)}) - signature correct")
            else:
                print(
                    f"❌ {method_name} - expected params {expected_params}, got {params}"
                )
                all_methods_present = False

    if not all_methods_present:
        return False

    print()
    print("✅ All required methods present with correct signatures")

    # Check docstring
    print()
    print("Documentation Validation:")
    print("-" * 80)

    if TspMetaheuristicStrategy.__doc__:
        doc = TspMetaheuristicStrategy.__doc__
        doc_length = len(doc)
        print(f"✅ Protocol has docstring ({doc_length} characters)")

        # Check for key documentation sections
        required_sections = [
            "Class P",  # Architecture classification
            "hyperparameter",  # Hyperparameter discussion
            "statistics",  # Statistics format
            "GPU",  # GPU acceleration notes
            "Example",  # Usage examples
        ]

        missing_sections = []
        for section in required_sections:
            if section.lower() not in doc.lower():
                missing_sections.append(section)

        if missing_sections:
            print(f"⚠️  Missing documentation sections: {', '.join(missing_sections)}")
        else:
            print("✅ All key documentation sections present")
    else:
        print("❌ Protocol missing docstring")
        return False

    return True


def demonstrate_expected_usage():
    """Demonstrate expected usage patterns for implementations."""
    print()
    print("=" * 80)
    print("Expected Usage Patterns")
    print("=" * 80)
    print()

    print("1. Genetic Algorithm Implementation:")
    print("-" * 80)
    print(
        """
class GeneticAlgorithmStrategy:
    def __init__(self):
        self._stats = {}
        self._hyperparams = {
            'population_size': 100,
            'generations': 200,
            'mutation_rate': 0.1,
            'crossover_rate': 0.8
        }
    
    def set_params(self, **hyperparameters):
        self._hyperparams.update(hyperparameters)
    
    def build_tour_with_stats(self, context, customers):
        # Initialize population
        # Run evolutionary loop
        # Track convergence history
        tour = [0] + customers + [0]  # Placeholder
        self._stats = {
            'best_fitness': 1234.56,
            'final_fitness': 1250.0,
            'iterations': self._hyperparams['generations'],
            'convergence_history': [...],
            'runtime_seconds': 5.2,
            'hyperparameters': self._hyperparams.copy()
        }
        return tour, self._stats
    
    def get_stats(self):
        return self._stats.copy()

# Usage:
strategy = GeneticAlgorithmStrategy()
strategy.set_params(population_size=200, generations=500)
tour, stats = strategy.build_tour_with_stats(context, customers)
print(f"Best fitness: {stats['best_fitness']}")
"""
    )

    print()
    print("2. Simulated Annealing Implementation:")
    print("-" * 80)
    print(
        """
class SimulatedAnnealingStrategy:
    def __init__(self):
        self._stats = {}
        self._hyperparams = {
            'initial_temp': 1000.0,
            'cooling_rate': 0.95,
            'max_iterations': 10000
        }
    
    def set_params(self, **hyperparameters):
        self._hyperparams.update(hyperparameters)
    
    def build_tour_with_stats(self, context, customers):
        # Initialize random tour
        # Run SA loop with temperature schedule
        # Track acceptance rate
        tour = [0] + customers + [0]  # Placeholder
        self._stats = {
            'best_fitness': 987.65,
            'final_fitness': 995.0,
            'iterations': 8523,  # Converged early
            'convergence_history': [...],
            'runtime_seconds': 3.1,
            'hyperparameters': self._hyperparams.copy(),
            'temperature_schedule': [...],
            'acceptance_rate': 0.35
        }
        return tour, self._stats
    
    def get_stats(self):
        return self._stats.copy()

# Usage:
strategy = SimulatedAnnealingStrategy()
strategy.set_params(initial_temp=2000.0, cooling_rate=0.98)
tour, stats = strategy.build_tour_with_stats(context, customers)
print(f"Acceptance rate: {stats['acceptance_rate']:.2%}")
"""
    )

    print()
    print("3. Statistics Dictionary Format:")
    print("-" * 80)
    print(
        """
Required keys:
- best_fitness (float): Best tour cost found during optimization
- final_fitness (float): Final tour cost (may differ from best)
- iterations (int): Number of iterations executed
- convergence_history (List[float]): Fitness values by iteration
- runtime_seconds (float): Total execution time
- hyperparameters (Dict[str, Any]): Hyperparameter values used

Optional algorithm-specific keys:
- population_diversity (List[float]): GA/PSO diversity metrics
- temperature_schedule (List[float]): SA temperature by iteration
- acceptance_rate (float): SA fraction of accepted moves
- crossover_count (int): GA successful crossovers
- mutation_count (int): GA successful mutations
"""
    )


def main():
    """Main validation entry point."""
    print()
    print("🔍 Validating TspMetaheuristicStrategy Protocol")
    print()

    # Validate protocol structure
    protocol_valid = validate_protocol_structure()

    # Show expected usage patterns
    demonstrate_expected_usage()

    # Summary
    print()
    print("=" * 80)
    print("Validation Summary")
    print("=" * 80)

    if protocol_valid:
        print("✅ TspMetaheuristicStrategy protocol is correctly defined")
        print()
        print("Next steps:")
        print("  1. Implement GeneticAlgorithmStrategy (Todo #7)")
        print("  2. Implement SimulatedAnnealingStrategy (Todo #8)")
        print("  3. Create integration tests for metaheuristic implementations")
        print("  4. Benchmark CPU vs GPU performance")
        print()
        return 0
    else:
        print("❌ TspMetaheuristicStrategy protocol validation FAILED")
        print()
        print("Please fix the issues above before implementing algorithms.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
