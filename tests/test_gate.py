import numpy as np

from pirtm.gate import EmissionGate, EmissionPolicy, gated_run
from pirtm.recurrence import step


def _projected_case(dim: int = 3):
    X = np.ones(dim)
    Xi = 0.9 * np.eye(dim)
    Lam = 0.9 * np.eye(dim)

    def T(x):
        return x

    G = np.zeros(dim)

    def P(x):
        return x

    return X, Xi, Lam, T, G, P


def test_pass_through_matches_step_output():
    X, Xi, Lam, T, G, P = _projected_case()
    expected_X, expected_info = step(X, Xi, Lam, T, G, P, epsilon=0.05, op_norm_T=1.0)

    gate = EmissionGate(policy=EmissionPolicy.PASS_THROUGH)
    out = gate(X, Xi, Lam, T, G, P, epsilon=0.05, op_norm_T=1.0)

    assert np.allclose(out.X_next, expected_X)
    assert out.info.projected == expected_info.projected
    assert out.emitted is True


def test_suppress_and_hold_do_not_leak_raw_output():
    X, Xi, Lam, T, G, P = _projected_case()
    raw_X, _ = step(X, Xi, Lam, T, G, P, epsilon=0.05, op_norm_T=1.0)

    sup = EmissionGate(policy=EmissionPolicy.SUPPRESS)
    out_sup = sup(X, Xi, Lam, T, G, P, epsilon=0.05, op_norm_T=1.0)
    assert out_sup.emitted is False
    assert np.allclose(out_sup.X_next, np.zeros_like(X))
    assert not np.allclose(out_sup.X_next, raw_X)

    hold = EmissionGate(policy=EmissionPolicy.HOLD)
    out_hold = hold(X, Xi, Lam, T, G, P, epsilon=0.05, op_norm_T=1.0)
    assert out_hold.emitted is False
    assert np.allclose(out_hold.X_next, X)
    assert not np.allclose(out_hold.X_next, raw_X)


def test_custom_predicate_composes_with_contraction():
    dim = 3
    X = np.ones(dim)
    Xi = 0.2 * np.eye(dim)
    Lam = 0.2 * np.eye(dim)

    def T(x):
        return 0.8 * x

    G = np.zeros(dim)

    def P(x):
        return x

    gate = EmissionGate(policy=EmissionPolicy.SUPPRESS, custom_predicate=lambda _x, _i: False)
    out = gate(X, Xi, Lam, T, G, P, epsilon=0.05, op_norm_T=0.8)
    assert out.emitted is False
    assert out.policy_applied == "suppress"
    assert "custom_predicate_failed" in out.suppression_reason


def test_gated_run_collects_trace():
    dim = 2
    X0 = np.ones(dim)
    Xi_seq = [0.2 * np.eye(dim)] * 4
    Lam_seq = [0.2 * np.eye(dim)] * 4
    G_seq = [np.zeros(dim)] * 4

    def T(x):
        return 0.8 * x

    def P(x):
        return x

    gate = EmissionGate(policy=EmissionPolicy.PASS_THROUGH)

    Xf, history, outputs = gated_run(
        X0,
        Xi_seq,
        Lam_seq,
        G_seq,
        T=T,
        P=P,
        gate=gate,
        epsilon=0.05,
        op_norm_T=0.8,
    )

    assert len(history) == 5
    assert len(outputs) == 4
    assert Xf.shape == X0.shape
