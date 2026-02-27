# 📦 test_spectral.py
# Spectral Convergence Tests for PIRTM Operators

import unittest
import numpy as np
from pirtm._legacy import PrimeTensorSystem
from pirtm._legacy import (
    spectral_decomposition,
    spectral_entropy,
    phase_coherence,
    analyze_tensor
)

class TestSpectralAnalysis(unittest.TestCase):

    def setUp(self):
        """Initialize prime tensor system and get sample tensor."""
        self.dim = 4
        self.pts = PrimeTensorSystem(dim=self.dim, num_primes=20)
        self.tensor = self.pts.get_tensor(0)

    def test_spectral_decomposition_returns_eigs_and_vecs(self):
        """Check that eigendecomposition returns matching shapes."""
        eigvals, eigvecs = spectral_decomposition(self.tensor)
        self.assertEqual(len(eigvals), self.dim)
        self.assertEqual(eigvecs.shape, (self.dim, self.dim))

    def test_spectral_entropy_bounds(self):
        """Ensure entropy is finite and non-negative."""
        eigvals, _ = spectral_decomposition(self.tensor)
        entropy = spectral_entropy(eigvals)
        self.assertGreaterEqual(entropy, 0)
        self.assertLess(entropy, 10)

    def test_phase_coherence_range(self):
        """Check that phase coherence lies in [0, 1]."""
        eigvals, _ = spectral_decomposition(self.tensor)
        coherence = phase_coherence(eigvals)
        self.assertGreaterEqual(coherence, 0)
        self.assertLessEqual(coherence, 1)

    def test_analyze_tensor_output(self):
        """Ensure composite analysis includes entropy and coherence."""
        result = analyze_tensor(self.tensor, plot=False)
        self.assertIn('entropy', result)
        self.assertIn('coherence', result)
        self.assertIsInstance(result['entropy'], float)
        self.assertIsInstance(result['coherence'], float)

    def test_entropy_changes_over_perturbation(self):
        """Verify entropy responds to small perturbations."""
        rng = np.random.default_rng(42)
        perturbed = self.tensor + 0.02 * rng.standard_normal(self.tensor.shape)
        ent1 = spectral_entropy(spectral_decomposition(self.tensor)[0])
        ent2 = spectral_entropy(spectral_decomposition(perturbed)[0])
        self.assertNotAlmostEqual(ent1, ent2, delta=1e-4)

if __name__ == '__main__':
    unittest.main()
