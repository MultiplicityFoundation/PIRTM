import json
from dataclasses import asdict

import numpy as np
import pytest

from pirtm.gate import EmissionPolicy
from pirtm.orchestrator import SessionOrchestrator
from pirtm.qari import QARIConfig


def _one_step(session):
    X = np.ones(2)
    Xi = 0.2 * np.eye(2)
    Lam = 0.2 * np.eye(2)
    T = lambda x: 0.8 * x
    G = np.zeros(2)
    session.step(X, Xi, Lam, T, G)


def test_register_get_duplicate_and_missing():
    orch = SessionOrchestrator()
    cfg = QARIConfig(dim=2, emission_policy=EmissionPolicy.PASS_THROUGH)
    session = orch.register("s1", cfg)
    assert orch.get("s1") is session
    with pytest.raises(ValueError):
        orch.register("s1", cfg)
    with pytest.raises(KeyError):
        orch.get("missing")


def test_aggregate_certificates_and_master_audit():
    orch = SessionOrchestrator()
    cfg = QARIConfig(dim=2, emission_policy=EmissionPolicy.PASS_THROUGH)
    s1 = orch.register("s1", cfg)
    s2 = orch.register("s2", cfg)
    _one_step(s1)
    _one_step(s2)

    agg1 = orch.aggregate_certificates(["s1", "s2"])
    agg2 = orch.aggregate_certificates(["s1", "s2"])
    assert agg1.all_certified is True
    assert agg1.aggregate_hash == agg2.aggregate_hash
    assert len(orch.master_audit) >= 2


def test_pause_list_and_global_summary_serializable_snapshot():
    orch = SessionOrchestrator()
    cfg = QARIConfig(dim=2, emission_policy=EmissionPolicy.PASS_THROUGH)
    session = orch.register("s1", cfg)
    _one_step(session)

    snapshot = orch.pause("s1")
    json.dumps(asdict(snapshot), default=str)

    paused = orch.list_sessions(status="paused")
    assert len(paused) == 1

    summary = orch.global_summary()
    assert summary["total_sessions"] == 1
    assert "master_audit_length" in summary
