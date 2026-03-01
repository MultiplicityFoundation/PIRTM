import numpy as np
import pytest

from pirtm.ace import AceProtocol, AceTelemetry


def test_injection_is_copy_on_normalise():
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

    proto = AceProtocol(designed_clamp_norm=0.95)
    normalised = proto._normalise(telemetry)
    assert normalised[0] is not telemetry
    assert normalised[0].designed_clamp_norm == 0.95
    assert telemetry.designed_clamp_norm is None


def test_cross_protocol_reuse_respects_each_default():
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

    proto_a = AceProtocol(designed_clamp_norm=0.95)
    proto_b = AceProtocol(designed_clamp_norm=0.8)

    cert_a = proto_a.certify(telemetry, prime_index=2).certificate
    cert_b = proto_b.certify(telemetry, prime_index=3).certificate

    assert cert_a.details["designed_clamp_norm"] == 0.95
    assert cert_b.details["designed_clamp_norm"] == 0.8
    assert telemetry.designed_clamp_norm is None


def test_explicit_value_not_overwritten_by_protocol_default():
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

    proto = AceProtocol(designed_clamp_norm=0.95)
    cert = proto.certify(telemetry, prime_index=5).certificate

    assert cert.details["designed_clamp_norm"] == 0.7
    assert telemetry.designed_clamp_norm == 0.7


def test_no_injection_needed_returns_same_object_identity_fast_path():
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
        designed_clamp_norm=0.9,
        designed_perturbation_bound=0.05,
    )

    proto = AceProtocol(designed_clamp_norm=0.95, designed_perturbation_bound=0.1)
    normalised = proto._normalise(telemetry)

    assert normalised[0] is telemetry


def test_runtime_exceeding_injected_clamp_bound_fails_closed():
    matrix = 0.2 * np.eye(2)
    telemetry = AceTelemetry(
        step=0,
        q=0.2,
        epsilon=0.05,
        nXi=0.96,
        nLam=0.1,
        projected=False,
        residual=0.0,
        contraction_matrix=matrix,
    )

    proto = AceProtocol(designed_clamp_norm=0.95)

    with pytest.raises(RuntimeError, match="DESIGN_ENVELOPE_VIOLATION"):
        proto.certify(telemetry, prime_index=7)


def test_runtime_exceeding_injected_perturbation_bound_fails_closed():
    matrix = 0.2 * np.eye(2)
    telemetry = AceTelemetry(
        step=0,
        q=0.2,
        epsilon=0.05,
        nXi=0.9,
        nLam=0.08,
        projected=False,
        residual=0.0,
        contraction_matrix=matrix,
        disturbance_norm=0.01,
        designed_clamp_norm=0.95,
    )

    proto = AceProtocol(designed_perturbation_bound=0.05)

    with pytest.raises(RuntimeError, match="DESIGN_ENVELOPE_VIOLATION"):
        proto.certify(telemetry, prime_index=11)
