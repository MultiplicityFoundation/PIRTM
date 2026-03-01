import numpy as np
import pytest

from pirtm.gate import GatedOutput
from pirtm.integrations.feedback_bridge import (
    ConvergenceController,
    DRMMInferenceLoop,
    EntropicFeedbackLoop,
    EthicalModulator,
)


def test_drmm_inference_loop_evolve_and_run():
    loop = DRMMInferenceLoop(dim=3)

    X0 = np.ones(3)
    Xi = 0.2 * np.eye(3)
    Lam = 0.2 * np.eye(3)

    def T(x):
        return 0.8 * x

    X_next, out = loop.evolve(X0, Xi, Lam, T)
    assert X_next.shape == X0.shape
    assert isinstance(out, GatedOutput)

    Xi_seq = [Xi] * 4
    Lam_seq = [Lam] * 4
    result = loop.run(X0, Xi_seq, Lam_seq, T)
    assert "certificate" in result
    assert "audit_export" in result
    if result["audit_export"] is not None:
        assert isinstance(result["audit_export"], list)
    assert len(loop.telemetry_events) > 0


def test_legacy_shims_warn_and_keep_behavior():
    with pytest.warns(DeprecationWarning):
        legacy_loop = EntropicFeedbackLoop(alpha=0.1)
    X = np.array([1.0, 2.0])
    updated = legacy_loop.update(X, 2)
    expected = X + 0.1 * 2 * (-np.log(np.abs(X) + 1e-8))
    assert np.allclose(updated, expected)

    with pytest.warns(DeprecationWarning):
        ctrl = ConvergenceController(threshold=1e-3)
    assert bool(ctrl.is_converged(np.array([0.0, 0.0]), np.array([1e-4, 0.0])))

    with pytest.warns(DeprecationWarning):
        mod = EthicalModulator(filter_strength=0.05)
    mod_out = mod.apply(np.array([1.0, -1.0]))
    expected_mod = np.array([1.0, -1.0]) - 0.05 * np.tanh(np.array([1.0, -1.0]))
    assert np.allclose(mod_out, expected_mod)
