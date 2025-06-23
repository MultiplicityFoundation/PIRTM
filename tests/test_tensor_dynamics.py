# 📦 test_tensor_dynamics.py
# Validation of Recursive Tensor Evolution in PIRTM
Add commentMore actions
import unittest
import numpy as np
from pir_tensor import PrimeTensorSystem
from recursive_ops import recursive_update, contraction_check, is_stable

class TestTensorDynamics(unittest.TestCase):

    def setUp(self):
        """Initialize a PIRTM tensor system for testing."""
        self.dim = 3
        self.pts = PrimeTensorSystem(dim=self.dim, num_primes=10)
        self.Xi = self.pts.get_state()
        self.T = self.pts.get_tensor(0)
        self.Lambda_m = 0.9

    def test_recursive_update_dimensions(self):
        """Ensure recursive update preserves matrix dimensions."""
        Phi = np.eye(self.dim)
        Xi_next = recursive_update(self.Xi, self.T, self.Lambda_m, Phi)
        self.assertEqual(Xi_next.shape, (self.dim, self.dim))

    def test_update_with_zero_feedback(self):
        """Verify recursive evolution is deterministic with zero Φ(t)."""
        Phi_zero = np.zeros((self.dim, self.dim))
        Xi1 = recursive_update(self.Xi, self.T, self.Lambda_m, Phi_zero)
        Xi2 = recursive_update(self.Xi, self.T, self.Lambda_m)
        self.assertTrue(np.allclose(Xi1, Xi2))

    def test_contraction_coefficient_validity(self):
        """Check that contraction coefficient k is computable and non-negative."""
        k = contraction_check(
            tensor_sequence=[self.T],
            alpha_weights=[1.0],
            p_indices=[self.pts.primes[0]]
        )
        self.assertIsInstance(k, float)
        self.assertGreaterEqual(k, 0)

    def test_stability_threshold_check(self):
        """Test system stability detection logic."""
        k = 0.85
        self.assertTrue(is_stable(k))
        self.assertFalse(is_stable(1.05))

    def test_tensor_norm_monotonicity(self):
        """Confirm norm does not blow up under stable contraction."""
        Phi = np.zeros((self.dim, self.dim))
        norms = []
        Xi = self.Xi.copy()
        for _ in range(10):
            Xi = recursive_update(Xi, self.T, self.Lambda_m, Phi)
            norms.append(np.linalg.norm(Xi))
        avg_diff = np.mean(np.diff(norms))
        self.assertLessEqual(avg_diff, 1.0)  # Stable growth or decay

if __name__ == '__main__':
    unittest.main()
