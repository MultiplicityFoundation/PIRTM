"""
Phase 1 Backend Abstraction Tests

Tests for:
1. TensorBackend protocol correctness
2. NumPy backend implementation
3. Core module (recurrence, projection, gain, certify) correctness
4. Backend-agnostic operation

Reference: ADR-006, docs/PHASE_1_EXPANDED.md, docs/PROJECT_TRACKER_SETUP.md
"""

import pytest
import numpy as np
from typing import Any, Callable
from pirtm.backend import (
    get_backend,
    current_backend,
)
from pirtm.core import (
    recurrence_step,
    project,
    project_ball,
    bounded_state_check,
    compute_spectral_radius,
    certify_state,
    verify_trajectory,
)


class TestBackendProtocol:
    """Test TensorBackend protocol implementation."""
    
    def test_numpy_backend_creation(self):
        """Backend should be instantiable."""
        backend = get_backend("numpy")
        assert backend is not None
        assert backend.name() == "numpy"
    
    def test_backend_singleton(self):
        """Same backend should be reused."""
        b1 = get_backend("numpy")
        b2 = get_backend("numpy")
        assert b1 is b2
    
    def test_default_backend(self):
        """Default backend should be NumPy."""
        backend = current_backend()
        assert backend.name() == "numpy"
    
    def test_backend_device_info(self):
        """Backend should report device location."""
        backend = get_backend("numpy")
        assert backend.device() == "cpu"
    
    def test_backend_dtype_info(self):
        """Backend should report array dtype."""
        backend = get_backend("numpy")
        x = np.array([1.0, 2.0, 3.0])
        dtype = backend.dtype(x)
        assert "float" in dtype


class TestLinearAlgebra:
    """Test linear algebra operations."""
    
    def test_matmul(self):
        """Matrix-vector multiplication should work."""
        backend = get_backend("numpy")
        A = np.array([[1.0, 2.0], [3.0, 4.0]])
        x = np.array([1.0, 2.0])
        
        result = backend.matmul(A, x)
        expected = np.array([5.0, 11.0])
        
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_dot_product(self):
        """Inner product should return scalar."""
        backend = get_backend("numpy")
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([4.0, 5.0, 6.0])
        
        result = backend.dot(x, y)
        expected = 32.0
        
        assert abs(result - expected) < 1e-10
    
    def test_norm_l2(self):
        """L2 norm should be computed correctly."""
        backend = get_backend("numpy")
        x = np.array([3.0, 4.0])
        
        result = backend.norm(x, order=2)
        expected = 5.0
        
        assert abs(result - expected) < 1e-10
    
    def test_add(self):
        """Element-wise addition should work."""
        backend = get_backend("numpy")
        x = np.array([1.0, 2.0])
        y = np.array([3.0, 4.0])
        
        result = backend.add(x, y)
        expected = np.array([4.0, 6.0])
        
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_multiply(self):
        """Element-wise multiplication should work."""
        backend = get_backend("numpy")
        x = np.array([1.0, 2.0])
        y = np.array([3.0, 4.0])
        
        result = backend.multiply(x, y)
        expected = np.array([3.0, 8.0])
        
        np.testing.assert_array_almost_equal(result, expected)


class TestNonlinearOperations:
    """Test nonlinear element-wise operations."""
    
    def test_sigmoid(self):
        """Sigmoid should compress to (0, 1)."""
        backend = get_backend("numpy")
        x = np.array([0.0, 10.0, -10.0])
        
        result = backend.sigmoid(x)
        
        # Check bounds
        assert np.all(result > 0)
        assert np.all(result < 1)
        
        # Check midpoint
        assert abs(result[0] - 0.5) < 1e-10
    
    def test_clip(self):
        """Clipping should bound values."""
        backend = get_backend("numpy")
        x = np.array([-2.0, 0.0, 2.0])
        
        result = backend.clip(x, -1.0, 1.0)
        expected = np.array([-1.0, 0.0, 1.0])
        
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_exp_log(self):
        """Exp and log should be inverses."""
        backend = get_backend("numpy")
        x = np.array([1.0, 2.0, 3.0])
        
        y = backend.exp(x)
        z = backend.log(y)
        
        np.testing.assert_array_almost_equal(x, z)


class TestMatrixCreation:
    """Test matrix creation operations."""
    
    def test_eye(self):
        """Identity matrix should have 1s on diagonal."""
        backend = get_backend("numpy")
        result = backend.eye(3)
        expected = np.eye(3)
        
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_zeros(self):
        """Zeros should create zero arrays."""
        backend = get_backend("numpy")
        result = backend.zeros((2, 3))
        expected = np.zeros((2, 3))
        
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_ones(self):
        """Ones should create arrays of 1s."""
        backend = get_backend("numpy")
        result = backend.ones((2, 3))
        expected = np.ones((2, 3))
        
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_diag(self):
        """Diagonal matrix creation."""
        backend = get_backend("numpy")
        x = np.array([1.0, 2.0, 3.0])
        
        result = backend.diag(x)
        expected = np.diag(x)
        
        np.testing.assert_array_almost_equal(result, expected)


class TestRecurrenceStep:
    """Test PIRTM recurrence step."""
    
    def test_recurrence_step_identity(self):
        """Step with identity operator should clip state."""
        backend = get_backend("numpy")
        X_t = np.array([0.5, 0.3])
        Xi_t = np.eye(2)
        Lambda_t = np.zeros((2, 2))
        
        X_next, meta = recurrence_step(X_t, Xi_t, Lambda_t, backend=backend)
        
        # With identity + no Lambda, should just clip sigmoid(X_t)
        assert meta["backend"] == "numpy"
        assert X_next.shape == X_t.shape
    
    def test_recurrence_state_bounded(self):
        """Recurrence step should produce bounded output."""
        backend = get_backend("numpy")
        X_t = np.array([10.0, 20.0])  # Large values
        Xi_t = np.eye(2)
        Lambda_t = np.zeros((2, 2))
        
        X_next, _ = recurrence_step(X_t, Xi_t, Lambda_t, backend=backend)
        
        # Output should be in [-1, 1]
        assert np.all(X_next >= -1.0 - 1e-10)
        assert np.all(X_next <= 1.0 + 1e-10)
    
    def test_recurrence_custom_transformation(self):
        """Recurrence should accept custom transformation."""
        backend = get_backend("numpy")
        X_t = np.array([0.5, 0.3])
        Xi_t = np.eye(2)
        Lambda_t = np.zeros((2, 2))
        
        # Use identity transformation instead of sigmoid
        T_func: Callable[[Any], Any] = lambda x: x
        
        X_next, _ = recurrence_step(
            X_t, Xi_t, Lambda_t, T_func=T_func, backend=backend
        )
        
        assert X_next.shape == X_t.shape


class TestProjection:
    """Test projection operations."""
    
    def test_project_clips_values(self):
        """Projection should clip to [-1, 1]."""
        backend = get_backend("numpy")
        x = np.array([-2.0, 0.0, 2.0])
        
        result = project(x, backend=backend)
        
        np.testing.assert_array_almost_equal(
            result, np.array([-1.0, 0.0, 1.0])
        )
    
    def test_project_custom_bounds(self):
        """Projection should respect custom bounds."""
        backend = get_backend("numpy")
        x = np.array([-2.0, 0.0, 2.0])
        
        result = project(x, min_val=-0.5, max_val=0.5, backend=backend)
        
        assert np.all(result >= -0.5 - 1e-10)
        assert np.all(result <= 0.5 + 1e-10)
    
    def test_project_ball(self):
        """Projection onto L2 ball should scale down if needed."""
        backend = get_backend("numpy")
        x = np.array([3.0, 4.0])  # norm = 5.0
        
        result = project_ball(x, radius=1.0, backend=backend)
        
        result_norm = backend.norm(result)
        assert result_norm <= 1.0 + 1e-10
    
    def test_bounded_state_check(self):
        """Check should detect bounded states."""
        backend = get_backend("numpy")
        
        x_bounded = np.array([0.5, -0.3])
        x_unbounded = np.array([2.0, -0.3])
        
        assert bounded_state_check(x_bounded, backend=backend)
        assert not bounded_state_check(x_unbounded, backend=backend)


class TestGainOperations:
    """Test gain/aggregation operations."""
    
    def test_spectral_radius(self):
        """Spectral radius should compute largest eigenvalue."""
        backend = get_backend("numpy")
        
        # Diagonal matrix with eigenvalues [2, 3, 1]
        A = np.diag([2.0, 3.0, 1.0])
        
        result = compute_spectral_radius(A, backend=backend)
        expected = 3.0
        
        assert abs(result - expected) < 1e-10
    
    def test_spectral_radius_complex(self):
        """Spectral radius should work with complex eigenvalues."""
        backend = get_backend("numpy")
        
        # 2x2 matrix with complex eigenvalues
        A = np.array([[0.0, 1.0], [-1.0, 0.0]])
        
        result = compute_spectral_radius(A, backend=backend)
        # Eigenvalues are ±i, so spectral radius = 1
        assert abs(result - 1.0) < 1e-10


class TestCertification:
    """Test contractivity certification."""
    
    def test_certify_bounded_state(self):
        """Certification should mark bounded states as valid."""
        backend = get_backend("numpy")
        X = np.array([0.5, 0.3])
        
        cert = certify_state(X, epsilon=0.05, backend=backend)
        
        assert cert.is_valid()
        assert cert.contraction_margin() > 0
    
    def test_certify_unbounded_state(self):
        """Certification should mark unbounded states as invalid."""
        backend = get_backend("numpy")
        X = np.array([1.5, 0.3])
        
        cert = certify_state(X, epsilon=0.05, backend=backend)
        
        assert not cert.is_valid()
    
    def test_verify_trajectory_all_valid(self):
        """Trajectory verification should pass for bounded trajectory."""
        backend = get_backend("numpy")
        trajectory = [
            np.array([0.5, 0.3]),
            np.array([0.4, 0.25]),
            np.array([0.3, 0.2]),
        ]
        
        result = verify_trajectory(trajectory, epsilon=0.05, backend=backend)
        
        assert result["all_valid"]
        assert len(result["violations"]) == 0
    
    def test_verify_trajectory_with_violation(self):
        """Trajectory verification should catch violations."""
        backend = get_backend("numpy")
        trajectory = [
            np.array([0.5, 0.3]),
            np.array([1.5, 0.3]),  # Violates invariant
            np.array([0.3, 0.2]),
        ]
        
        result = verify_trajectory(trajectory, epsilon=0.05, backend=backend)
        
        assert not result["all_valid"]
        assert len(result["violations"]) > 0
    
    def test_certificate_serialization(self):
        """Certificates should serialize to dict."""
        X = np.array([0.5, 0.3])
        cert = certify_state(X)
        
        d = cert.to_dict()
        
        assert d["is_valid"]
        assert d["epsilon"] == 0.05
        assert d["state_norm"] > 0


class TestBackendIntegration:
    """Test end-to-end backend integration."""
    
    def test_recurrence_produces_contractive_trajectory(self):
        """Recurrence should produce bounded trajectories."""
        backend = get_backend("numpy")
        
        X_t = np.array([0.5, 0.4])
        Xi_t = 0.3 * np.eye(2)  # Scaled identity for contraction
        Lambda_t = np.zeros((2, 2))
        
        trajectory = [X_t]
        
        for _ in range(20):
            X_next, _ = recurrence_step(X_t, Xi_t, Lambda_t, backend=backend)
            trajectory.append(X_next)
            X_t = X_next
        
        # All states should remain in [-1, 1]
        for X in trajectory:
            assert np.all(X >= -1.0 - 1e-10)
            assert np.all(X <= 1.0 + 1e-10)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
