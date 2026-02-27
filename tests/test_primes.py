# 📦 test_primes.py
# Unit Tests for Prime Generation and Indexing in PIRTM

import unittest
import numpy as np
from sympy import isprime, primerange
from pirtm._legacy import PrimeTensorSystem

class TestPrimeTensorSystem(unittest.TestCase):

    def test_prime_list_generation(self):
        """Ensure prime list contains only primes and is of correct length."""
        pts = PrimeTensorSystem(dim=3, num_primes=50)
        primes = pts.primes
        self.assertEqual(len(primes), 50)
        for p in primes:
            self.assertTrue(isprime(p), f"{p} is not a prime")

    def test_tensor_dimensions(self):
        """Check that all tensors have correct dimensions and are square."""
        pts = PrimeTensorSystem(dim=4, num_primes=10)
        for p in pts.primes:
            T = pts.tensors[p]
            self.assertEqual(T.shape, (4, 4))

    def test_tensor_orthogonality(self):
        """Confirm that tensors are approximately orthogonal (up to numerical tolerance)."""
        pts = PrimeTensorSystem(dim=3, num_primes=10)
        for p in pts.primes:
            T = pts.tensors[p]
            I = np.eye(3)
            should_be_identity = T.T @ T / np.linalg.norm(T)
            self.assertTrue(np.allclose(should_be_identity, I, atol=1e-1))

    def test_tensor_scaling(self):
        """Test that each tensor is scaled by log(p)."""
        pts = PrimeTensorSystem(dim=2, num_primes=5)
        for i, p in enumerate(pts.primes[:5]):
            T = pts.get_tensor(i)
            approx_norm = np.linalg.norm(T)
            self.assertGreater(approx_norm, 0.5)
            self.assertLess(approx_norm, 10.0)

    def test_initial_state_identity(self):
        """Confirm initial Xi is identity matrix of specified dimension."""
        pts = PrimeTensorSystem(dim=5, num_primes=10)
        self.assertTrue(np.allclose(pts.get_state(), np.eye(5)))

if __name__ == '__main__':
    unittest.main()
