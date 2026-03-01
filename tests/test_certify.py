import pytest

from pirtm.ace.types import AceCertificate
from pirtm.certify import ace_certificate, ace_certificate_v2, iss_bound, legacy_ace_certificate
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


def test_ace_certificate_returns_ace_certificate():
    info = StepInfo(step=0, q=0.7, epsilon=0.05, nXi=0.4, nLam=0.3, projected=False, residual=0.001)
    cert = ace_certificate([info])
    assert isinstance(cert, AceCertificate)


def test_ace_certificate_v2_returns_ace_certificate():
    info = StepInfo(step=0, q=0.7, epsilon=0.05, nXi=0.4, nLam=0.3, projected=False, residual=0.001)
    with pytest.warns(DeprecationWarning):
        cert = ace_certificate_v2([info])
    assert isinstance(cert, AceCertificate)


def test_legacy_alias_emits_deprecation():
    info = StepInfo(step=0, q=0.7, epsilon=0.05, nXi=0.4, nLam=0.3, projected=False, residual=0.001)
    with pytest.warns(DeprecationWarning):
        cert = legacy_ace_certificate([info])
    from pirtm.types import Certificate

    assert isinstance(cert, Certificate)


def test_ace_certificate_details_preserve_legacy_keys(safe_step_info):
    cert = ace_certificate([safe_step_info])
    assert "max_q" in cert.details
    assert "target" in cert.details
    assert "steps" in cert.details


def test_legacy_alias_matches_primary_legacy_fields(safe_step_info):
    ace_cert = ace_certificate([safe_step_info])
    with pytest.warns(DeprecationWarning):
        legacy_cert = legacy_ace_certificate([safe_step_info])

    assert legacy_cert.certified == ace_cert.certified
    assert legacy_cert.margin == ace_cert.margin
    assert legacy_cert.tail_bound == ace_cert.tail_bound


def test_legacy_alias_includes_ace_level_detail(safe_step_info):
    with pytest.warns(DeprecationWarning):
        legacy_cert = legacy_ace_certificate([safe_step_info])
    assert "ace_level" in legacy_cert.details
