import pytest

from pirtm.certify import ace_certificate, iss_bound
from pirtm.types import StepInfo


def test_ace_single_step_certified(safe_step_info):
    cert = ace_certificate(safe_step_info)
    assert cert.certified is True
    assert cert.margin > 0


def test_ace_single_step_not_certified(unsafe_step_info):
    cert = ace_certificate(unsafe_step_info)
    assert cert.certified is False


def test_ace_empty_raises():
    with pytest.raises(ValueError):
        ace_certificate([])


def test_ace_tail_bound_infinite():
    info = StepInfo(step=0, q=1.1, epsilon=0.05, nXi=0.4, nLam=0.7, projected=True, residual=1.0)
    cert = ace_certificate([info])
    assert cert.tail_bound == float("inf")


def test_iss_bound_basic(safe_step_info):
    bound = iss_bound([safe_step_info], disturbance_norm=0.1)
    assert bound == pytest.approx(0.1 / (1.0 - safe_step_info.q))


def test_iss_bound_unstable(unsafe_step_info):
    info = StepInfo(step=1, q=1.2, epsilon=0.05, nXi=0.4, nLam=0.9, projected=True, residual=1.0)
    assert iss_bound([info], disturbance_norm=0.2) == float("inf")


def test_iss_empty_raises():
    with pytest.raises(ValueError):
        iss_bound([], 0.1)
