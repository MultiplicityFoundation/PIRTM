import numpy as np

from pirtm.csl_gate import CSLEmissionGate
from pirtm.gate import EmissionGate, EmissionPolicy


def _safe_case():
    X = np.ones(3)
    Xi = 0.2 * np.eye(3)
    Lam = 0.2 * np.eye(3)

    def T(x):
        return 0.8 * x

    G = np.zeros(3)

    def P(x):
        return x

    return X, Xi, Lam, T, G, P


def test_csl_gate_emits_only_when_both_stages_pass():
    gate = CSLEmissionGate(
        EmissionGate(policy=EmissionPolicy.PASS_THROUGH),
        subjects=[np.ones(3), np.ones(3)],
        csl_filter=lambda x: x,
    )
    X, Xi, Lam, T, G, P = _safe_case()
    out = gate(X, Xi, Lam, T, G, P, step_index=0, epsilon=0.05, op_norm_T=0.8)
    assert out.emitted is True
    assert out.silenced is False
    assert out.final_policy == "emitted"


def test_csl_gate_skips_csl_when_contraction_gate_blocks():
    contraction = EmissionGate(policy=EmissionPolicy.SUPPRESS)
    gate = CSLEmissionGate(contraction)

    X = np.ones(3)
    Xi = 0.95 * np.eye(3)
    Lam = 0.95 * np.eye(3)

    def T(x):
        return x

    G = np.zeros(3)

    def P(x):
        return x

    out = gate(X, Xi, Lam, T, G, P, step_index=0, epsilon=0.05, op_norm_T=1.0)
    assert out.emitted is False
    assert out.final_policy == "contraction_gated"
    assert out.csl_verdict.detail["skipped"] == "contraction_gated"


def test_csl_silence_returns_noop_input_state():
    gate = CSLEmissionGate(
        EmissionGate(policy=EmissionPolicy.PASS_THROUGH),
        subjects=[np.zeros(2), np.ones(2)],
        epsilon_n=1e-12,
    )
    X = np.ones(2)
    Xi = 0.2 * np.eye(2)
    Lam = 0.2 * np.eye(2)

    def T(x):
        return 0.8 * x

    G = np.zeros(2)

    def P(x):
        return x

    out = gate(X, Xi, Lam, T, G, P, step_index=1, epsilon=0.05, op_norm_T=0.8)
    assert out.silenced is True
    assert out.emitted is False
    assert np.allclose(out.X_next, X)
