"""
Unit tests for callback protocol.

Tests callback invocation patterns, history capture, early stopping,
and type validation for ProgressEvent.
"""

from src.protocols.callback_protocol import ProgressEvent


class TestProgressEvent:
    """Test ProgressEvent TypedDict structure."""

    def test_progress_event_all_fields(self):
        """Test ProgressEvent with all fields (SA)."""
        event: ProgressEvent = {
            "iteration": 100,
            "best_cost": 7542.0,
            "current_cost": 7890.0,
            "elapsed_time": 0.152,
            "temperature": 95.3,
            "acceptance_rate": 0.42,
        }

        assert event["iteration"] == 100
        assert event["best_cost"] == 7542.0
        assert event["current_cost"] == 7890.0
        assert event["elapsed_time"] == 0.152
        assert event["temperature"] == 95.3
        assert event["acceptance_rate"] == 0.42

    def test_progress_event_minimal_fields(self):
        """Test ProgressEvent without SA-specific fields (deterministic algorithms)."""
        event: ProgressEvent = {
            "iteration": 50,
            "best_cost": 6820.0,
            "current_cost": 6820.0,  # Same as best for deterministic
            "elapsed_time": 0.087,
        }

        assert event["iteration"] == 50
        assert event["best_cost"] == 6820.0
        assert "temperature" not in event  # Optional field
        assert "acceptance_rate" not in event  # Optional field

    def test_progress_event_copy_independence(self):
        """Test that copied events are independent."""
        event1: ProgressEvent = {
            "iteration": 10,
            "best_cost": 1000.0,
            "current_cost": 1200.0,
            "elapsed_time": 0.5,
        }

        event2 = event1.copy()
        event2["iteration"] = 20

        assert event1["iteration"] == 10  # Original unchanged
        assert event2["iteration"] == 20  # Copy modified


class TestCallbackInvocation:
    """Test callback function invocation patterns."""

    def test_simple_callback_returns_true(self):
        """Test callback that always continues."""

        def simple_callback(event: ProgressEvent) -> bool:
            return True

        event: ProgressEvent = {
            "iteration": 1,
            "best_cost": 100.0,
            "current_cost": 100.0,
            "elapsed_time": 0.01,
        }

        result = simple_callback(event)
        assert result is True

    def test_early_stopping_callback(self):
        """Test callback that stops execution."""
        OPTIMAL_COST = 7542.0

        def stop_if_optimal(event: ProgressEvent) -> bool:
            if event["best_cost"] <= OPTIMAL_COST:
                return False  # Stop
            return True  # Continue

        # Event above optimal - continue
        event_bad: ProgressEvent = {
            "iteration": 10,
            "best_cost": 8000.0,
            "current_cost": 8500.0,
            "elapsed_time": 0.1,
        }
        assert stop_if_optimal(event_bad) is True

        # Event at optimal - stop
        event_optimal: ProgressEvent = {
            "iteration": 50,
            "best_cost": 7542.0,
            "current_cost": 7542.0,
            "elapsed_time": 0.5,
        }
        assert stop_if_optimal(event_optimal) is False

    def test_conditional_callback(self):
        """Test callback with conditional logic."""
        calls = []

        def log_every_100(event: ProgressEvent) -> bool:
            if event["iteration"] % 100 == 0:
                calls.append(event["iteration"])
            return True

        # Invoke at various iterations
        for i in [50, 100, 150, 200, 250, 300]:
            event: ProgressEvent = {
                "iteration": i,
                "best_cost": 1000.0,
                "current_cost": 1000.0,
                "elapsed_time": i * 0.01,
            }
            log_every_100(event)

        assert calls == [100, 200, 300]  # Only multiples of 100


class TestHistoryCapture:
    """Test history capture pattern (common usage)."""

    def test_history_capture(self):
        """Test capturing full history."""
        history = []

        def capture_history(event: ProgressEvent) -> bool:
            history.append(event.copy())  # Important: copy!
            return True

        # Simulate algorithm iterations
        for i in range(5):
            event: ProgressEvent = {
                "iteration": i,
                "best_cost": 1000.0 - i * 10,  # Improving
                "current_cost": 1000.0 - i * 10,
                "elapsed_time": i * 0.1,
            }
            capture_history(event)

        assert len(history) == 5
        assert history[0]["iteration"] == 0
        assert history[4]["iteration"] == 4
        assert history[0]["best_cost"] == 1000.0
        assert history[4]["best_cost"] == 960.0

    def test_history_independence(self):
        """Test that history events are independent copies."""
        history = []

        def capture_history(event: ProgressEvent) -> bool:
            history.append(event.copy())
            return True

        # First event
        event: ProgressEvent = {
            "iteration": 0,
            "best_cost": 1000.0,
            "current_cost": 1000.0,
            "elapsed_time": 0.0,
        }
        capture_history(event)

        # Modify event
        event["iteration"] = 1
        event["best_cost"] = 900.0
        capture_history(event)

        # Check history preserved original values
        assert history[0]["iteration"] == 0
        assert history[0]["best_cost"] == 1000.0
        assert history[1]["iteration"] == 1
        assert history[1]["best_cost"] == 900.0


class TestCombinedPatterns:
    """Test combined callback patterns (monitoring + history)."""

    def test_monitoring_and_history(self):
        """Test callback that does both monitoring and history capture."""
        history = []
        printed_iterations = []

        def monitor_and_capture(event: ProgressEvent) -> bool:
            history.append(event.copy())

            if event["iteration"] % 50 == 0:
                printed_iterations.append(event["iteration"])

            return event["best_cost"] > 500.0  # Stop if below 500

        # Simulate iterations
        for i in range(0, 201, 50):  # 0, 50, 100, 150, 200
            event: ProgressEvent = {
                "iteration": i,
                "best_cost": 1000.0 - i * 2.0,
                "current_cost": 1000.0 - i * 2.0,
                "elapsed_time": i * 0.01,
            }
            result = monitor_and_capture(event)

            if not result:
                break  # Early stop

        # Check monitoring happened
        assert printed_iterations == [0, 50, 100, 150, 200]

        # Check history captured
        assert len(history) == 5

        # Check early stopping would occur at iteration 250 (cost = 500)
        event_stop: ProgressEvent = {
            "iteration": 250,
            "best_cost": 500.0,
            "current_cost": 500.0,
            "elapsed_time": 2.5,
        }
        assert monitor_and_capture(event_stop) is False


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_none_callback_handling(self):
        """Test that None callback is valid (no-op pattern)."""
        callback = None

        # Algorithm should check: if callback is not None
        event: ProgressEvent = {
            "iteration": 1,
            "best_cost": 100.0,
            "current_cost": 100.0,
            "elapsed_time": 0.01,
        }

        # This pattern is safe
        if callback is not None:
            callback(event)

        # No error raised
        assert True

    def test_callback_with_sa_fields(self):
        """Test callback handling SA-specific fields."""
        sa_calls = []

        def track_temperature(event: ProgressEvent) -> bool:
            if "temperature" in event:
                sa_calls.append(event["temperature"])
            return True

        # SA event
        sa_event: ProgressEvent = {
            "iteration": 100,
            "best_cost": 7000.0,
            "current_cost": 7200.0,
            "elapsed_time": 1.0,
            "temperature": 95.5,
            "acceptance_rate": 0.38,
        }
        track_temperature(sa_event)

        # Deterministic event (no temperature)
        det_event: ProgressEvent = {
            "iteration": 10,
            "best_cost": 6500.0,
            "current_cost": 6500.0,
            "elapsed_time": 0.1,
        }
        track_temperature(det_event)

        assert len(sa_calls) == 1
        assert sa_calls[0] == 95.5

    def test_callback_returning_non_bool(self):
        """Test callback that returns non-boolean (should be caught by type checker)."""

        def bad_callback(event: ProgressEvent) -> bool:
            return 1  # type: ignore  # Technically truthy but wrong type

        event: ProgressEvent = {
            "iteration": 1,
            "best_cost": 100.0,
            "current_cost": 100.0,
            "elapsed_time": 0.01,
        }

        result = bad_callback(event)

        # Python allows this (1 is truthy), but mypy would catch it
        assert result == 1  # Not bool, but works in if statements
        assert bool(result) is True  # Converts to True
