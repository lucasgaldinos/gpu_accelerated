"""
Data structures for benchmark configuration and results.

Implements the experimental design from Section 3.5 with structured
data models for reproducible performance evaluation.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import json


@dataclass(frozen=True)
class BenchmarkConfig:
    """
    Configuration for a single benchmark experiment.

    Captures all parameters needed for reproducible execution following
    Section 3.5.4 (Reproducibility Requirements).

    Attributes:
        algorithm: Algorithm identifier ("SA", "GA", "2opt", "nearest_neighbor")
        backend: Backend module name ("numpy" for CPU, "cupy" for GPU)
        instance_name: Problem instance identifier (e.g., "berlin52")
        num_repetitions: Number of independent runs (default: 30 for CLT)
        random_seed_base: Base seed for reproducibility (default: 42)
        time_budget: Time limit in seconds for stochastic algorithms (default: 60.0)
        target_gap: Target quality gap for time-to-target metric (default: 0.05 = 5%)
        convergence_log_interval: Iterations between quality logging (default: 100)
        algorithm_params: Algorithm-specific parameters (e.g., population_size, temperature)

    Example:
        >>> config = BenchmarkConfig(
        ...     algorithm="SA",
        ...     backend="numpy",
        ...     instance_name="berlin52",
        ...     algorithm_params={"initial_temperature": 100.0}
        ... )
    """

    algorithm: str
    backend: str
    instance_name: str
    num_repetitions: int = 30
    random_seed_base: int = 42
    time_budget: Optional[float] = 60.0  # seconds
    target_gap: Optional[float] = 0.05  # 5% from optimal
    convergence_log_interval: int = 100
    algorithm_params: Dict[str, Any] = field(default_factory=dict)

    def get_run_seed(self, run_id: int) -> int:
        """
        Generate seed for specific run.

        Following Section 3.5.2 footnote [^seed_independence], uses
        sequential offset: s_i = s_0 + i for run i.

        Args:
            run_id: Run index in [0, num_repetitions)

        Returns:
            Seed for this specific run

        Example:
            >>> config = BenchmarkConfig("SA", "numpy", "berlin52")
            >>> config.get_run_seed(0)  # Returns 42
            >>> config.get_run_seed(5)  # Returns 47
        """
        return self.random_seed_base + run_id

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary for JSON serialization."""
        return {
            "algorithm": self.algorithm,
            "backend": self.backend,
            "instance_name": self.instance_name,
            "num_repetitions": self.num_repetitions,
            "random_seed_base": self.random_seed_base,
            "time_budget": self.time_budget,
            "target_gap": self.target_gap,
            "convergence_log_interval": self.convergence_log_interval,
            "algorithm_params": self.algorithm_params,
        }


@dataclass
class BenchmarkResult:
    """
    Results from a single benchmark run.

    Captures all metrics needed for statistical analysis (Section 3.5.3)
    and result reporting (Section 4).

    Attributes:
        config: Configuration used for this run
        run_id: Run index [0, num_repetitions)
        random_seed: Actual seed used (from config.get_run_seed(run_id))
        runtime_seconds: Total execution time (wall-clock)
        final_tour_cost: Final solution quality
        final_tour: Final solution tour (node sequence)
        convergence_history: Quality over time [(iteration, cost, elapsed_time)]
        time_to_target: Time to reach target_gap (None if not reached)
        memory_peak_mb: Peak memory usage (VRAM for GPU)
        validation_passed: Whether solution passed correctness checks

    Example:
        >>> result = BenchmarkResult(
        ...     config=config,
        ...     run_id=0,
        ...     random_seed=42,
        ...     runtime_seconds=1.234,
        ...     final_tour_cost=7542.0,
        ...     final_tour=[0, 1, 2, ..., 0],
        ...     convergence_history=[(0, 10000.0, 0.0), ...],
        ...     time_to_target=0.567,
        ...     memory_peak_mb=125.3,
        ...     validation_passed=True
        ... )
    """

    config: BenchmarkConfig
    run_id: int
    random_seed: int
    runtime_seconds: float
    final_tour_cost: float
    final_tour: List[int]
    convergence_history: List[Tuple[int, float, float]]  # (iter, cost, time)
    time_to_target: Optional[float]  # seconds, None if not reached
    memory_peak_mb: float
    validation_passed: bool

    def to_dict(self) -> Dict[str, Any]:
        """Export result as dictionary for JSON serialization."""
        return {
            "config": self.config.to_dict(),
            "run_id": self.run_id,
            "random_seed": self.random_seed,
            "runtime_seconds": self.runtime_seconds,
            "final_tour_cost": self.final_tour_cost,
            "final_tour": self.final_tour,
            "convergence_history": [
                {"iteration": it, "cost": cost, "time": t}
                for it, cost, t in self.convergence_history
            ],
            "time_to_target": self.time_to_target,
            "memory_peak_mb": self.memory_peak_mb,
            "validation_passed": self.validation_passed,
        }

    def save_json(self, filepath: Path) -> None:
        """Save result to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, filepath: Path) -> "BenchmarkResult":
        """Load result from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        config_dict = data["config"]
        config = BenchmarkConfig(
            algorithm=config_dict["algorithm"],
            backend=config_dict["backend"],
            instance_name=config_dict["instance_name"],
            num_repetitions=config_dict["num_repetitions"],
            random_seed_base=config_dict["random_seed_base"],
            time_budget=config_dict["time_budget"],
            target_gap=config_dict["target_gap"],
            convergence_log_interval=config_dict["convergence_log_interval"],
            algorithm_params=config_dict["algorithm_params"],
        )

        convergence_history = [
            (entry["iteration"], entry["cost"], entry["time"])
            for entry in data["convergence_history"]
        ]

        return cls(
            config=config,
            run_id=data["run_id"],
            random_seed=data["random_seed"],
            runtime_seconds=data["runtime_seconds"],
            final_tour_cost=data["final_tour_cost"],
            final_tour=data["final_tour"],
            convergence_history=convergence_history,
            time_to_target=data["time_to_target"],
            memory_peak_mb=data["memory_peak_mb"],
            validation_passed=data["validation_passed"],
        )


@dataclass
class ComparisonPair:
    """
    Pair of configurations for statistical comparison (e.g., CPU vs GPU).

    Used for paired statistical tests (Section 3.5.3) where same problem
    instance is run with different backends/algorithms.

    Attributes:
        config_a: First configuration (e.g., CPU)
        config_b: Second configuration (e.g., GPU)
        label: Human-readable comparison label (e.g., "NumPy vs CuPy")

    Example:
        >>> cpu_config = BenchmarkConfig("SA", "numpy", "berlin52")
        >>> gpu_config = BenchmarkConfig("SA", "cupy", "berlin52")
        >>> pair = ComparisonPair(cpu_config, gpu_config, "SA: NumPy vs CuPy")
    """

    config_a: BenchmarkConfig
    config_b: BenchmarkConfig
    label: str

    def __post_init__(self):
        """Validate that configurations differ in exactly one dimension."""
        # Ensure same instance for paired comparison
        if self.config_a.instance_name != self.config_b.instance_name:
            raise ValueError(
                f"ComparisonPair requires same instance: "
                f"{self.config_a.instance_name} != {self.config_b.instance_name}"
            )

        # Ensure same algorithm (for backend comparison)
        # OR same backend (for algorithm comparison)
        same_algorithm = self.config_a.algorithm == self.config_b.algorithm
        same_backend = self.config_a.backend == self.config_b.backend

        if not (same_algorithm or same_backend):
            raise ValueError(
                "ComparisonPair must vary in exactly one dimension "
                "(algorithm OR backend, not both)"
            )
