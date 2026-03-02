"""Conformance tests for PIRTM Language Spec §5 certificate types."""

from pirtm import StepInfo, ace_certificate, contraction_certificate


def _mk_stepinfo(q: float = 0.4, epsilon: float = 0.05) -> StepInfo:
    return StepInfo(
        step=0,
        q=q,
        epsilon=epsilon,
        nXi=0.2,
        nLam=0.2,
        projected=False,
        residual=0.01,
    )


class TestSection5Certificates:
    """§5 Certificate Types."""

    def test_minimal_certificate_has_certified_field(self) -> None:
        """§5.1: Minimal certificate includes certified boolean."""
        cert = contraction_certificate(_mk_stepinfo())
        assert hasattr(cert, "certified")
        assert isinstance(cert.certified, bool)

    def test_standard_certificate_structure(self) -> None:
        """§5.2: Standard certificate shape from contraction_certificate()."""
        cert = contraction_certificate(_mk_stepinfo())

        assert hasattr(cert, "certified")
        assert hasattr(cert, "margin")
        assert hasattr(cert, "tail_bound")
        assert hasattr(cert, "details")
        assert isinstance(cert.details, dict)

    def test_ace_certificate_structure(self) -> None:
        """§5.3: ACE certificate carries aggregate diagnostics."""
        ace = ace_certificate(_mk_stepinfo())

        assert hasattr(ace, "certified")
        assert hasattr(ace, "margin")
        assert hasattr(ace, "tail_bound")
        assert hasattr(ace, "details")
        assert "max_q" in ace.details
        assert "target" in ace.details

    def test_certified_iff_margin_nonnegative(self) -> None:
        """§5.3: certified is equivalent to nonnegative margin."""
        ace_safe = ace_certificate(_mk_stepinfo(q=0.4, epsilon=0.05))
        assert ace_safe.certified == (ace_safe.margin >= 0)

        ace_unsafe = ace_certificate(_mk_stepinfo(q=0.99, epsilon=0.05))
        assert ace_unsafe.certified == (ace_unsafe.margin >= 0)
