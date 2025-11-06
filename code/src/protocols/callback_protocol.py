"""
Callback protocol for algorithm progress monitoring and metadata tracking.

This module defines a unified callback mechanism that serves three purposes:
1. Metadata tracking for experimental analysis (Q1)
2. Progress monitoring during execution (Q2)
3. History capture for convergence analysis (Q5)

Usage Examples
--------------

**Example 1: Progress Monitoring**

    >>> def print_progress(event: ProgressEvent) -> bool:
    ...     print(f"Iteration {event['iteration']}: cost = {event['best_cost']:.2f}")
    ...     return True  # Continue execution
    ...
    >>> result = simulated_annealing(problem, callback=print_progress)

**Example 2: History Capture**

    >>> history = []
    >>> def capture_history(event: ProgressEvent) -> bool:
    ...     history.append(event.copy())
    ...     return True
    ...
    >>> result = simulated_annealing(problem, callback=capture_history)
    >>> # Plot convergence: plt.plot([e['iteration'] for e in history],
    >>> #                           [e['best_cost'] for e in history])

**Example 3: Early Stopping**

    >>> def stop_if_optimal(event: ProgressEvent) -> bool:
    ...     if event['best_cost'] <= KNOWN_OPTIMAL:
    ...         print(f"Optimal found at iteration {event['iteration']}")
    ...         return False  # Stop execution
    ...     return True  # Continue
    ...
    >>> result = simulated_annealing(problem, callback=stop_if_optimal)

**Example 4: Combined Monitoring and History**

    >>> history = []
    >>> def monitor_and_capture(event: ProgressEvent) -> bool:
    ...     history.append(event.copy())
    ...     if event['iteration'] % 100 == 0:
    ...         print(f"[{event['iteration']}] Best: {event['best_cost']:.2f}, "
    ...               f"Temp: {event['temperature']:.2f}, "
    ...               f"Accept: {event['acceptance_rate']:.2%}")
    ...     return True
    ...
    >>> result = simulated_annealing(problem, callback=monitor_and_capture)

References
----------
.. [1] Architecture Document, Decision 1: Unified Callback Architecture
.. [2] Research Question Q1: GPU Overhead Threshold (metadata tracking)
.. [3] Research Question Q2: Scaling Behavior (progress monitoring)
.. [4] Research Question Q5: Problem Type Comparison (history capture)
"""

from typing import Callable, TypedDict


class ProgressEvent(TypedDict, total=False):
    """
    Event data emitted during algorithm execution.

    All algorithms emit at minimum: iteration, best_cost, current_cost, elapsed_time.
    Algorithm-specific fields (temperature, acceptance_rate) are optional.

    Attributes
    ----------
    iteration : int
        Current iteration number (0-indexed for SA, varies by algorithm)
    best_cost : float
        Best (lowest) solution cost found so far
    current_cost : float
        Cost of current solution (may be worse than best for SA)
    elapsed_time : float
        Wall-clock time elapsed since algorithm start (seconds)
    temperature : float, optional
        Current temperature for Simulated Annealing (None for other algorithms)
    acceptance_rate : float, optional
        Ratio of accepted moves in recent window for SA (None for deterministic algorithms)

    Notes
    -----
    Using `total=False` allows algorithm-specific fields to be optional.
    Algorithms MUST provide: iteration, best_cost, current_cost, elapsed_time.

    Examples
    --------
    >>> event: ProgressEvent = {
    ...     'iteration': 100,
    ...     'best_cost': 7542.0,
    ...     'current_cost': 7890.0,
    ...     'elapsed_time': 0.152,
    ...     'temperature': 95.3,
    ...     'acceptance_rate': 0.42
    ... }
    """

    iteration: int
    best_cost: float
    current_cost: float
    elapsed_time: float
    temperature: float  # Optional (SA only)
    acceptance_rate: float  # Optional (SA only)


CallbackFunction = Callable[[ProgressEvent], bool]
"""
Type alias for callback functions that receive progress events.

Callbacks are invoked periodically during algorithm execution (typically every 
100 iterations for SA, every 10-50 iterations for deterministic improvement).

Parameters
----------
event : ProgressEvent
    Current algorithm state and metadata

Returns
-------
bool
    True to continue execution, False to stop early

Examples
--------
>>> def simple_callback(event: ProgressEvent) -> bool:
...     print(f"Iteration {event['iteration']}: {event['best_cost']}")
...     return True
...
>>> # Usage in algorithm
>>> callback(event)  # Returns bool
"""


# Type alias for better IDE support
CallbackType = CallbackFunction


class ProgressCallback:
    """
    Protocol for class-based callbacks with lifecycle hooks.

    This is an alternative to the functional CallbackFunction pattern,
    providing explicit lifecycle methods for start, iteration, and completion.
    Used by BenchmarkRunner's ConvergenceTracker.

    Methods
    -------
    on_start(event: ProgressEvent) -> None
        Called once at algorithm initialization
    on_iteration(event: ProgressEvent) -> None
        Called after each iteration (implementation may throttle)
    on_complete(event: ProgressEvent) -> None
        Called once at algorithm completion

    Example
    -------
    >>> class MyTracker(ProgressCallback):
    ...     def on_start(self, event):
    ...         self.start_time = event['elapsed_time']
    ...     def on_iteration(self, event):
    ...         if event['iteration'] % 100 == 0:
    ...             print(f"Iteration {event['iteration']}")
    ...     def on_complete(self, event):
    ...         print(f"Done! Final cost: {event['best_cost']}")
    """

    def on_start(self, event: ProgressEvent) -> None:
        """Called when algorithm execution starts."""
        pass

    def on_iteration(self, event: ProgressEvent) -> None:
        """Called after each iteration."""
        pass

    def on_complete(self, event: ProgressEvent) -> None:
        """Called when algorithm execution completes."""
        pass
