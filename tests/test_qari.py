import numpy as np
import pytest

from pirtm.gate import EmissionPolicy, GatedOutput
from pirtm.qari import QARIConfig, QARISession


def test_qari_step_and_certify_pipeline():
    cfg = QARIConfig(
        dim=3, epsilon=0.05, op_norm_T=0.8, emission_policy=EmissionPolicy.PASS_THROUGH
    )
    session = QARISession(cfg)

    X = np.ones(3)
    Xi = 0.2 * np.eye(3)
    Lam = 0.2 * np.eye(3)

    def T(x):
        return 0.8 * x

    G = np.zeros(3)

    result = session.step(X, Xi, Lam, T, G)
    assert isinstance(result, GatedOutput)
    cert = session.certify()
    assert cert.certified is True
    summary = session.summary()
    assert set(summary.keys()) == {
        "steps",
        "q_max",
        "q_min",
        "q_mean",
        "residual_final",
        "projected_count",
        "projection_rate",
        "epsilon_current",
        "audit_chain_length",
    }


def test_qari_max_steps_guard():
    cfg = QARIConfig(dim=2, max_steps=1, emission_policy=EmissionPolicy.PASS_THROUGH)
    session = QARISession(cfg)

    X = np.ones(2)
    Xi = 0.2 * np.eye(2)
    Lam = 0.2 * np.eye(2)

    def T(x):
        return 0.8 * x

    G = np.zeros(2)

    session.step(X, Xi, Lam, T, G)
    with pytest.raises(RuntimeError):
        session.step(X, Xi, Lam, T, G)


def test_qari_without_audit_and_with_adaptive_update(monkeypatch):
    cfg = QARIConfig(dim=2, audit=False, adaptive=True, emission_policy=EmissionPolicy.PASS_THROUGH)
    session = QARISession(cfg)

    called = {"count": 0}

    def _fake_update(info):
        called["count"] += 1
        return 0.07

    assert session._margin is not None
    monkeypatch.setattr(session._margin, "update", _fake_update)

    X = np.ones(2)
    Xi = 0.2 * np.eye(2)
    Lam = 0.2 * np.eye(2)

    def T(x):
        return 0.8 * x

    G = np.zeros(2)

    session.step(X, Xi, Lam, T, G)
    assert called["count"] == 1
    assert session.current_epsilon == 0.07
    assert session.audit_chain is None
