import numpy as np

from pirtm.ace import AceProtocol, AceTelemetry, CertLevel


def test_cert_level_trl_mapping_is_code_first_metadata():
    assert CertLevel.L0_HEURISTIC.trl == 2
    assert CertLevel.L1_NORMBOUND.trl == 2
    assert CertLevel.L2_POWERITER.trl == 3
    assert CertLevel.L3_NONEXPANSIVE.trl == 4
    assert CertLevel.L4_PERTURBATION.trl == 4


def test_l3_details_include_designed_and_runtime_evidence():
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
    )

    witness = AceProtocol().certify(telemetry, prime_index=17)
    details = witness.certificate.details

    assert witness.certificate.level == CertLevel.L3_NONEXPANSIVE
    assert "designed_clamp_norm" in details
    assert "runtime_nXi" in details
    assert details["runtime_nXi"] == 0.2


def test_l4_details_include_designed_and_runtime_evidence():
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

    witness = AceProtocol().certify(telemetry, prime_index=19)
    details = witness.certificate.details

    assert witness.certificate.level == CertLevel.L4_PERTURBATION
    assert "designed_perturbation_bound" in details
    assert "runtime_nLam" in details
    assert details["runtime_nLam"] == 0.05
