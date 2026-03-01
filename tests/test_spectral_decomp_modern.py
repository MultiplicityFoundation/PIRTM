import numpy as np

from pirtm.spectral_decomp import (
    analyze_tensor,
    phase_coherence,
    spectral_decomposition,
    spectral_entropy,
)


def test_modern_spectral_decomp_basics():
    matrix = np.array([[0.8, 0.0], [0.0, 0.6]])
    eigvals, eigvecs = spectral_decomposition(matrix)
    assert eigvals.shape == (2,)
    assert eigvecs.shape == (2, 2)

    entropy = spectral_entropy(eigvals)
    coherence = phase_coherence(eigvals)
    assert entropy >= 0.0
    assert 0.0 <= coherence <= 1.0

    report = analyze_tensor(matrix)
    assert "entropy" in report
    assert "coherence" in report
