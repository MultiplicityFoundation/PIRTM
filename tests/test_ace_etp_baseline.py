import numpy as np
import pytest

from pirtm.ace import AceProtocol, AceTelemetry, CertLevel
from pirtm.certify import ace_certificate, legacy_ace_certificate


def test_baseline_pass13_identity_fast_path_and_copy_on_injection():
    matrix = 0.2 * np.eye(2)

    no_injection = AceTelemetry(
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
    assert proto._normalise(no_injection)[0] is no_injection

    needs_injection = AceTelemetry(
        step=0,
        q=0.2,
        epsilon=0.05,
        nXi=0.2,
        nLam=0.1,
        projected=False,
        residual=0.0,
        contraction_matrix=matrix,
    )
    normalised = proto._normalise(needs_injection)
    assert normalised[0] is not needs_injection
    assert normalised[0].designed_clamp_norm == pytest.approx(0.95)
    assert needs_injection.designed_clamp_norm is None


def test_baseline_pass24_legacy_compat_and_batch_composition():
    from pirtm.types import StepInfo

    info = StepInfo(step=0, q=0.7, epsilon=0.05, nXi=0.4, nLam=0.3, projected=False, residual=0.001)
    ace = ace_certificate([info])
    with pytest.warns(DeprecationWarning):
        legacy = legacy_ace_certificate([info])
    assert legacy.certified == ace.certified
    assert "ace_level" in legacy.details

    matrix = 0.2 * np.eye(2)
    level2_only = AceTelemetry(
        step=0,
        q=0.9,
        epsilon=0.05,
        nXi=0.2,
        nLam=0.1,
        projected=False,
        residual=0.0,
        contraction_matrix=matrix,
    )
    level4_capable = AceTelemetry(
        step=1,
        q=0.2,
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
    witness = AceProtocol().certify([level2_only, level4_capable], prime_index=31)
    assert witness.certificate.level == CertLevel.L4_PERTURBATION


def test_baseline_pass3_claim_vs_measurement_fields_present():
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

    witness = AceProtocol().certify(telemetry, prime_index=37)
    details = witness.certificate.details
    assert "designed_perturbation_bound" in details
    assert "runtime_nLam" in details
    assert details["runtime_nLam"] == pytest.approx(0.05)
