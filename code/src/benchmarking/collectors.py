"""
Metrics collection and convergence tracking for benchmark experiments.

Implements real-time data collection during algorithm execution using
the existing callback protocol.
"""

import time
from typing import List, Tuple, Optional
from dataclasses import dataclass, field

from ..protocols.callback_protocol import ProgressCallback, ProgressEvent


@dataclass
class ConvergenceTracker(ProgressCallback):
    """
    Tracks convergence history during algorithm execution.

    Implements the callback protocol to capture solution quality every N
    iterations (Section 3.5.2 - Convergence Data logging).

    Attributes:
        log_interval: Iterations between logged data points (default: 100)
        history: Convergence data [(iteration, cost, elapsed_time)]
        start_time: Experiment start timestamp (set in on_start)
        target_cost: Target cost for time-to-target metric (optional)
        time_to_target: Time when target was reached (None if not yet)

    Example:
        >>> tracker = ConvergenceTracker(log_interval=100, target_cost=7800.0)
        >>> algorithm = SimulatedAnnealing(context, callback=tracker)
        >>> tour, stats = algorithm.build_tour_with_stats()
        >>> print(f"Logged {len(tracker.history)} data points")
        >>> print(f"Time to target: {tracker.time_to_target:.2f}s")
    """

    log_interval: int = 100
    target_cost: Optional[float] = None
    history: List[Tuple[int, float, float]] = field(default_factory=list)
    start_time: float = field(default=0.0, init=False)
    time_to_target: Optional[float] = field(default=None, init=False)

    def on_start(self, event: ProgressEvent) -> None:
        """Called when algorithm execution starts."""
        self.start_time = time.perf_counter()
        self.history.clear()
        self.time_to_target = None

    def on_iteration(self, event: ProgressEvent) -> None:
        """
        Called after each iteration.

        Logs convergence data every log_interval iterations and tracks
        time-to-target if target_cost is set.
        """
        # Log convergence data at regular intervals
        if event["iteration"] % self.log_interval == 0:
            elapsed = time.perf_counter() - self.start_time
            self.history.append((event["iteration"], event["best_cost"], elapsed))

            # Check if target reached (for time-to-target metric)
            if self.target_cost is not None and self.time_to_target is None:
                if event["best_cost"] <= self.target_cost:
                    self.time_to_target = elapsed

    def on_complete(self, event: ProgressEvent) -> None:
        """Called when algorithm execution completes."""
        # Always log final state
        elapsed = time.perf_counter() - self.start_time
        self.history.append((event["iteration"], event["best_cost"], elapsed))

        # Final check for time-to-target
        if self.target_cost is not None and self.time_to_target is None:
            if event["best_cost"] <= self.target_cost:
                self.time_to_target = elapsed


class MetricsCollector:
    """
    Collects comprehensive metrics during benchmark execution.

    Integrates with ConvergenceTracker and adds memory monitoring,
    validation checks, and result packaging.

    Example:
        >>> collector = MetricsCollector(config, problem_optimal_cost=7542.0)
        >>> tracker = collector.create_tracker()
        >>> # ... run algorithm with tracker ...
        >>> result = collector.create_result(
        ...     run_id=0,
        ...     runtime=1.234,
        ...     final_cost=7650.0,
        ...     final_tour=[0, 1, ..., 0],
        ...     tracker=tracker
        ... )
    """

    def __init__(
        self,
        config: "BenchmarkConfig",
        problem_optimal_cost: Optional[float] = None,
    ):
        """
        Initialize metrics collector.

        Args:
            config: Benchmark configuration
            problem_optimal_cost: Known optimal cost (for target gap calculation)
        """
        from .config import BenchmarkConfig

        self.config = config
        self.problem_optimal_cost = problem_optimal_cost

        # Calculate target cost for time-to-target metric
        self.target_cost = None
        if problem_optimal_cost is not None and config.target_gap is not None:
            self.target_cost = problem_optimal_cost * (1.0 + config.target_gap)

    def create_tracker(self) -> ConvergenceTracker:
        """Create convergence tracker with appropriate configuration."""
        return ConvergenceTracker(
            log_interval=self.config.convergence_log_interval,
            target_cost=self.target_cost,
        )

    def create_result(
        self,
        run_id: int,
        runtime_seconds: float,
        final_tour_cost: float,
        final_tour: List[int],
        tracker: ConvergenceTracker,
        memory_peak_mb: float = 0.0,
        validation_passed: bool = True,
    ) -> "BenchmarkResult":
        """
        Package collected metrics into BenchmarkResult.

        Args:
            run_id: Run index
            runtime_seconds: Total execution time
            final_tour_cost: Final solution cost
            final_tour: Final solution tour
            tracker: ConvergenceTracker used during execution
            memory_peak_mb: Peak memory usage
            validation_passed: Whether solution passed validation

        Returns:
            Complete BenchmarkResult with all metrics
        """
        from .config import BenchmarkResult

        return BenchmarkResult(
            config=self.config,
            run_id=run_id,
            random_seed=self.config.get_run_seed(run_id),
            runtime_seconds=runtime_seconds,
            final_tour_cost=final_tour_cost,
            final_tour=final_tour,
            convergence_history=tracker.history.copy(),
            time_to_target=tracker.time_to_target,
            memory_peak_mb=memory_peak_mb,
            validation_passed=validation_passed,
        )

    def get_memory_usage_mb(self, backend: str) -> float:
        """
        Get current memory usage in MB.

        Args:
            backend: "numpy" (returns 0, CPU memory not tracked)
                     "cupy" (returns GPU VRAM usage)

        Returns:
            Memory usage in MB
        """
        if backend == "cupy":
            try:
                import cupy as cp

                mempool = cp.get_default_memory_pool()
                return mempool.used_bytes() / (1024**2)
            except ImportError:
                return 0.0
        return 0.0
