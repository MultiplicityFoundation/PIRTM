import numpy as np
import pytest

from pirtm.gain import build_gain_sequence, check_iss_compatibility, estimate_operator_norm
from pirtm.types import StepInfo


def test_estimate_operator_norm_scaling():
    estimate, _ = estimate_operator_norm(lambda x: 2.0 * x, dim=4)
    assert estimate == pytest.approx(2.0, rel=1e-6)


def test_estimate_operator_norm_matrix():
    matrix = np.diag([3.0, 2.0, 1.0, 0.5])
    estimate, _ = estimate_operator_norm(lambda x: matrix @ x, dim=4)
    assert estimate == pytest.approx(np.linalg.norm(matrix, 2), rel=1e-4)


def test_build_gain_sequence_profiles():
    decay = build_gain_sequence(10, 4, profile="decay")
    zeros = build_gain_sequence(5, 4, profile="zero")
    rnd1 = build_gain_sequence(5, 4, profile="random", seed=42)
    rnd2 = build_gain_sequence(5, 4, profile="random", seed=42)
    assert len(decay) == 10 and all(v.shape == (4,) for v in decay)
    assert all(np.allclose(v, 0.0) for v in zeros)
    assert all(np.allclose(a, b) for a, b in zip(rnd1, rnd2, strict=False))


def test_check_iss_compatibility():
    gains = build_gain_sequence(4, 4, profile="constant", scale=0.01)
    infos = [
        StepInfo(step=i, q=0.6, epsilon=0.05, nXi=0.3, nLam=0.3, projected=False, residual=0.01)
        for i in range(4)
    ]
    compatible, max_gain = check_iss_compatibility(gains, infos, target_radius=1.0)
    assert compatible is True
    assert max_gain <= 0.01 + 1e-12
