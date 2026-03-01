import numpy as np

from pirtm.conformance import check_core_profile, check_integrity_profile
from pirtm.recurrence import run


def _basic_sequences(dim: int, n_steps: int):
    X0 = np.ones(dim)
    Xi_seq = [0.3 * np.eye(dim)] * n_steps
    Lam_seq = [0.2 * np.eye(dim)] * n_steps
    G_seq = [np.zeros(dim)] * n_steps

    def T(x):
        return 0.8 * x

    def P(x):
        return x

    return X0, Xi_seq, Lam_seq, G_seq, T, P


def test_check_core_profile_passes_smoke():
    X0, Xi_seq, Lam_seq, G_seq, T, P = _basic_sequences(dim=4, n_steps=10)
    result = check_core_profile(
        X0,
        Xi_seq,
        Lam_seq,
        G_seq,
        T,
        P,
        epsilon=0.05,
        op_norm_T=0.8,
    )
    assert result.passed
    assert result.profile == "core"
    assert len(result.checks) >= 5


def test_check_integrity_profile_detects_replay():
    X0, Xi_seq, Lam_seq, G_seq, T, P = _basic_sequences(dim=3, n_steps=6)
    _, _, infos, _ = run(
        X0,
        Xi_seq,
        Lam_seq,
        G_seq,
        T=T,
        P=P,
        epsilon=0.05,
        op_norm_T=0.8,
    )
    infos[2].step = infos[1].step
    result = check_integrity_profile(infos)
    assert not result.passed
    checks = {entry["name"]: entry["passed"] for entry in result.checks}
    assert checks["anti_replay"] is False
