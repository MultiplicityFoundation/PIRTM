"""Conformance-oriented tests for §8 Emission Gate policy behavior."""

import numpy as np

from pirtm.csl_gate import CSLEmissionGate
from pirtm.gate import EmissionGate, EmissionPolicy


def _safe_state(dim: int = 4):
    x = np.ones(dim)
    xi = 0.2 * np.eye(dim)
    lam = 0.2 * np.eye(dim)
    g = np.zeros(dim)

    def t_fn(v: np.ndarray) -> np.ndarray:
        return 0.8 * v

    def p_fn(v: np.ndarray) -> np.ndarray:
        return v

    return x, xi, lam, t_fn, g, p_fn


def _projected_state(dim: int = 4):
    x = np.ones(dim)
    xi = 0.95 * np.eye(dim)
    lam = 0.95 * np.eye(dim)
    g = np.zeros(dim)

    def t_fn(v: np.ndarray) -> np.ndarray:
        return v

    def p_fn(v: np.ndarray) -> np.ndarray:
        return v

    return x, xi, lam, t_fn, g, p_fn


class TestSection8EmissionGate:
    """§8 Emission gate policy enforcement against current runtime policies."""

    def test_pass_through_emits_when_projection_triggered(self) -> None:
        state = _projected_state()
        gate = EmissionGate(policy=EmissionPolicy.PASS_THROUGH)

        out = gate(*state, epsilon=0.05, op_norm_T=1.0)

        assert out.info.projected is True
        assert out.emitted is True
        assert out.policy_applied == "pass_through"

    def test_suppress_blocks_output_on_projection(self) -> None:
        state = _projected_state()
        gate = EmissionGate(policy=EmissionPolicy.SUPPRESS)

        out = gate(*state, epsilon=0.05, op_norm_T=1.0)

        assert out.info.projected is True
        assert out.emitted is False
        assert out.policy_applied == "suppress"
        assert np.allclose(out.X_next, np.zeros_like(state[0]))

    def test_hold_returns_prior_state_on_projection(self) -> None:
        state = _projected_state()
        gate = EmissionGate(policy=EmissionPolicy.HOLD)

        out = gate(*state, epsilon=0.05, op_norm_T=1.0)

        assert out.info.projected is True
        assert out.emitted is False
        assert out.policy_applied == "hold"
        assert np.allclose(out.X_next, state[0])

    def test_attenuate_scales_output_on_projection(self) -> None:
        state = _projected_state()
        gate = EmissionGate(policy=EmissionPolicy.ATTENUATE, attenuation_floor=0.02)

        out = gate(*state, epsilon=0.05, op_norm_T=1.0)

        assert out.info.projected is True
        assert out.emitted is True
        assert out.policy_applied.startswith("attenuate(scale=")
        assert np.linalg.norm(out.X_next) <= np.linalg.norm(state[0]) + 1e-12

    def test_custom_predicate_can_gate_safe_state(self) -> None:
        state = _safe_state()
        gate = EmissionGate(
            policy=EmissionPolicy.SUPPRESS,
            custom_predicate=lambda _x, _info: False,
        )

        out = gate(*state, epsilon=0.05, op_norm_T=0.8)

        assert out.info.projected is False
        assert out.emitted is False
        assert "custom_predicate_failed" in out.suppression_reason


class TestSection8CSLGatedComposition:
    """§8 CSL-gated composition via CSLEmissionGate."""

    def test_csl_gated_emits_when_contraction_and_csl_pass(self) -> None:
        contraction_gate = EmissionGate(policy=EmissionPolicy.PASS_THROUGH)
        gate = CSLEmissionGate(contraction_gate)

        state = _safe_state()
        out = gate(*state, step_index=0, epsilon=0.05, op_norm_T=0.8)

        assert out.emitted is True
        assert out.final_policy == "emitted"

    def test_csl_gated_short_circuits_when_contraction_blocks(self) -> None:
        contraction_gate = EmissionGate(policy=EmissionPolicy.SUPPRESS)
        gate = CSLEmissionGate(contraction_gate)

        state = _projected_state()
        out = gate(*state, step_index=0, epsilon=0.05, op_norm_T=1.0)

        assert out.emitted is False
        assert out.final_policy == "contraction_gated"
        assert out.csl_verdict.detail["skipped"] == "contraction_gated"
