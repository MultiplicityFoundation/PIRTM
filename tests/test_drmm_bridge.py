import numpy as np

from pirtm.integrations.drmm_bridge import drmm_evolve, drmm_step


def test_drmm_step_smoke():
    dim = 4
    X = np.ones(dim)
    Xi = 0.2 * np.eye(dim)
    Lam = 0.3 * np.eye(dim)
    T = lambda x: 0.7 * x

    X_next, info = drmm_step(X, Xi, Lam, T, epsilon=0.05)

    assert X_next.shape == X.shape
    assert info.q <= 1.0


def test_drmm_evolve_returns_certificate():
    dim = 4
    X0 = np.ones(dim)
    Xi_sequence = [0.2 * np.eye(dim)] * 8
    Lam_sequence = [0.3 * np.eye(dim)] * 8
    T = lambda x: 0.7 * x

    result = drmm_evolve(
        X0,
        Xi_sequence,
        Lam_sequence,
        T,
        epsilon=0.05,
        certify=True,
    )

    assert "X_final" in result
    assert "history" in result
    assert "infos" in result
    assert "status" in result
    assert result["certificate"] is not None
