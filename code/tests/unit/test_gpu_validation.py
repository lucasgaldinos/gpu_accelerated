"""
Unit tests for GPU availability validation.

Tests ensure that when users request GPU backend but CuPy is not installed,
they receive clear, actionable error messages rather than silent failures
or confusing runtime errors.
"""

import pytest
import numpy as np

from src.protocols.problem_context import ProblemContext, CUPY_AVAILABLE
from src.data_models.problem import Problem


class TestGPUValidation:
    """Test GPU backend validation in ProblemContext."""

    @pytest.mark.skipif(
        CUPY_AVAILABLE, reason="CuPy is installed, cannot test unavailability"
    )
    def test_gpu_request_without_cupy_raises_clear_error(self):
        """Test that requesting GPU without CuPy raises ImportError with helpful message."""
        # Create minimal problem
        problem = Problem(
            name="test_problem",
            dimension=3,
            problem_type="TSP",
            edge_type="EUC_2D",
            coordinates=np.array([[0, 0], [1, 1], [2, 2]]),
            distances=None,
            capacity=None,
            demands=None,
        )

        # Create fake CuPy-like module to simulate user passing GPU backend
        class FakeCuPy:
            """Fake CuPy module to test validation."""

            pass

        fake_cupy = FakeCuPy()

        # Attempt to create GPU context should raise ImportError
        with pytest.raises(ImportError) as exc_info:
            ProblemContext(problem, xp=fake_cupy)

        # Verify error message is helpful
        error_message = str(exc_info.value)
        assert "GPU backend requested" in error_message
        assert "CuPy is not installed" in error_message
        assert "pip install cupy" in error_message.lower()

    @pytest.mark.skipif(not CUPY_AVAILABLE, reason="CuPy not available")
    def test_gpu_request_with_cupy_succeeds(self):
        """Test that requesting GPU with CuPy installed works correctly."""
        import cupy as cp

        # Create minimal problem
        problem = Problem(
            name="test_problem",
            dimension=3,
            problem_type="TSP",
            edge_type="EUC_2D",
            coordinates=np.array([[0, 0], [1, 1], [2, 2]]),
            distances=None,
            capacity=None,
            demands=None,
        )

        # Should NOT raise error when CuPy is available
        context = ProblemContext(problem, xp=cp)
        assert context.xp == cp

    def test_cpu_request_always_succeeds(self):
        """Test that requesting CPU backend always works, regardless of CuPy."""
        # Create minimal problem
        problem = Problem(
            name="test_problem",
            dimension=3,
            problem_type="TSP",
            edge_type="EUC_2D",
            coordinates=np.array([[0, 0], [1, 1], [2, 2]]),
            distances=None,
            capacity=None,
            demands=None,
        )

        # CPU request should always work
        context = ProblemContext(problem, xp=np)
        assert context.xp == np

    @pytest.mark.skipif(
        CUPY_AVAILABLE, reason="CuPy is installed, cannot test unavailability"
    )
    def test_error_message_suggests_alternatives(self):
        """Test that error message includes both install instructions and CPU fallback."""
        problem = Problem(
            name="test_problem",
            dimension=3,
            problem_type="TSP",
            edge_type="EUC_2D",
            coordinates=np.array([[0, 0], [1, 1], [2, 2]]),
            distances=None,
            capacity=None,
            demands=None,
        )

        class FakeCuPy:
            pass

        with pytest.raises(ImportError) as exc_info:
            ProblemContext(problem, xp=FakeCuPy())

        error_message = str(exc_info.value)
        # Should mention how to install CuPy
        assert "cupy-cuda" in error_message.lower()
        # Should mention CPU alternative
        assert "xp=np" in error_message
