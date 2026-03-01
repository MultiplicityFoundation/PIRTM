import numpy as np
import pytest

from pirtm.ace import AceProtocol, AceTelemetry, CertLevel
from pirtm.types import StepInfo


def test_ace_protocol_l0_from_stepinfo(safe_step_info):
    protocol = AceProtocol(delta=0.05)
    witness = protocol.certify(safe_step_info, prime_index=7919)

    assert witness.prime_index == 7919
    assert witness.certificate.level == CertLevel.L0_HEURISTIC
    assert witness.certificate.certified is True


def test_ace_protocol_inject_if_absent_uses_defaults():
    matrix = 0.2 * np.eye(2)
    telemetry = AceTelemetry(
        step=0,
        q=0.2,
        epsilon=0.05,
        nXi=0.2,
        nLam=0.1,
        projected=False,
        residual=0.0,
        contraction_matrix=matrix,
    )

    protocol = AceProtocol(designed_clamp_norm=0.9)
    witness = protocol.certify(telemetry, prime_index=2)

    assert witness.certificate.level == CertLevel.L3_NONEXPANSIVE
    assert witness.certificate.details["designed_clamp_norm"] == pytest.approx(0.9)
    assert telemetry.designed_clamp_norm is None


def test_ace_protocol_explicit_design_overrides_default():
    matrix = 0.2 * np.eye(2)
    telemetry = AceTelemetry(
        step=0,
        q=0.2,
        epsilon=0.05,
        nXi=0.2,
        nLam=0.1,
        projected=False,
        residual=0.0,
        contraction_matrix=matrix,
        designed_clamp_norm=0.7,
    )

    protocol = AceProtocol(designed_clamp_norm=0.95)
    witness = protocol.certify(telemetry, prime_index=3)

    assert witness.certificate.level == CertLevel.L3_NONEXPANSIVE
    assert witness.certificate.details["designed_clamp_norm"] == pytest.approx(0.7)


def test_ace_protocol_unknown_design_envelope_violation_raises():
    matrix = 0.3 * np.eye(2)
    telemetry = AceTelemetry(
        step=0,
        q=0.3,
        epsilon=0.05,
        nXi=0.6,
        nLam=0.1,
        projected=False,
        residual=0.0,
        contraction_matrix=matrix,
        designed_clamp_norm=0.5,
    )

    protocol = AceProtocol()
    with pytest.raises(RuntimeError, match="DESIGN_ENVELOPE_VIOLATION"):
        protocol.certify(telemetry, prime_index=5)


def test_ace_protocol_l4_path_uses_perturbation_fields():
    matrix = 0.15 * np.eye(2)
    telemetry = AceTelemetry(
        step=0,
        q=0.15,
        epsilon=0.05,
        nXi=0.2,
        nLam=0.05,
        projected=False,
        residual=0.0,
        contraction_matrix=matrix,
        designed_clamp_norm=0.9,
        designed_perturbation_bound=0.1,
        disturbance_norm=0.02,
    )

    protocol = AceProtocol(delta=0.05)
    witness = protocol.certify(telemetry, prime_index=11)

    assert witness.certificate.level == CertLevel.L4_PERTURBATION
    assert witness.certificate.details["designed_perturbation_bound"] == pytest.approx(0.1)


def test_ace_protocol_rejects_min_level_above_feasible(safe_step_info: StepInfo):
    protocol = AceProtocol()
    with pytest.raises(ValueError, match="min_level"):
        protocol.certify(safe_step_info, prime_index=13, min_level=CertLevel.L2_POWERITER)
