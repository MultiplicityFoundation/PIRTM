import numpy as np
import pytest

from pirtm.ace.contracts import assert_matrix_not_mutated
from pirtm.ace.contracts import _matrix_fingerprint
from pirtm.ace.levels import certify_l2, certify_l3, certify_l4
from pirtm.ace.telemetry import AceTelemetry


def _base_matrix() -> np.ndarray:
    return np.array([[0.2, 0.0], [0.0, 0.1]], dtype=float)


def test_l2_does_not_mutate_contraction_matrix():
    matrix = _base_matrix()
    fp_before = _matrix_fingerprint(matrix)

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

    certify_l2(telemetry)
    assert _matrix_fingerprint(matrix) == fp_before


def test_l3_does_not_mutate_contraction_matrix():
    matrix = _base_matrix()
    fp_before = _matrix_fingerprint(matrix)

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

    certify_l3(telemetry)
    assert _matrix_fingerprint(matrix) == fp_before


def test_l4_does_not_mutate_contraction_matrix():
    matrix = _base_matrix()
    fp_before = _matrix_fingerprint(matrix)

    telemetry = AceTelemetry(
        step=0,
        q=0.2,
        epsilon=0.05,
        nXi=0.2,
        nLam=0.05,
        projected=False,
        residual=0.0,
        contraction_matrix=matrix,
        designed_clamp_norm=0.9,
        designed_perturbation_bound=0.1,
        disturbance_norm=0.01,
    )

    certify_l4(telemetry)
    assert _matrix_fingerprint(matrix) == fp_before


def test_matrix_guard_raises_on_in_place_mutation_when_debug_enabled():
    matrix = _base_matrix()
    with pytest.raises(AssertionError, match="NO_MATRIX_MUTATION VIOLATED"):
        with assert_matrix_not_mutated(matrix, "TEST"):
            matrix[0, 0] = 999.0
