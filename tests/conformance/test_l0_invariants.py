"""Conformance tests for §11 L0 invariants."""

import numpy as np

from pirtm import EmissionGate, EmissionPolicy, StepInfo, contraction_certificate, step


class TestSection11L0Invariants:
    """§11: L0 invariant enforcement and violation detection."""

    def test_l0_1_contraction_typing_detects_unsafe_telemetry(self) -> None:
        """L0.1: q < 1-ε must hold for certified telemetry."""
        info = StepInfo(
            step=0,
            q=0.99,
            epsilon=0.05,
            nXi=0.6,
            nLam=0.5,
            projected=False,
            residual=0.2,
        )

        cert = contraction_certificate(info)

        assert cert.certified is False
        assert cert.margin < 0

    def test_l0_1_runtime_projects_unsafe_step(self) -> None:
        """L0.1: runtime remediates unsafe dynamics via projection."""
        x = np.ones(4)
        xi = 0.95 * np.eye(4)
        lam = 0.95 * np.eye(4)

        def t_fn(value: np.ndarray) -> np.ndarray:
            return value

        g = np.zeros(4)

        def p_fn(value: np.ndarray) -> np.ndarray:
            return value

        _, info = step(x, xi, lam, t_fn, g, p_fn, epsilon=0.05, op_norm_T=1.0)

        assert info.projected is True
        assert info.q <= (1.0 - info.epsilon) + 1e-12

    def test_l0_4_certified_emission_blocks_unsafe_path_with_suppress_policy(self) -> None:
        """L0.4: unsafe projected transitions are non-emitting under suppress policy."""
        gate = EmissionGate(policy=EmissionPolicy.SUPPRESS)

        x = np.ones(4)
        xi = 0.95 * np.eye(4)
        lam = 0.95 * np.eye(4)

        def t_fn(value: np.ndarray) -> np.ndarray:
            return value

        g = np.zeros(4)

        def p_fn(value: np.ndarray) -> np.ndarray:
            return value

        out = gate(x, xi, lam, t_fn, g, p_fn, epsilon=0.05, op_norm_T=1.0)

        assert out.info.projected is True
        assert out.emitted is False
        assert out.policy_applied == "suppress"
