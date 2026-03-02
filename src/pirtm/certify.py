from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from .ace.levels import certify_l0
from .ace.protocol import to_legacy_certificate
from .types import Certificate, StepInfo

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .ace.types import AceCertificate


def _ensure_sequence(info: StepInfo | Sequence[StepInfo]) -> list[StepInfo]:
    if isinstance(info, StepInfo):
        return [info]
    return list(info)


def ace_certificate_v2(
    info: StepInfo | Sequence[StepInfo],
    *,
    tail_norm: float = 0.0,
) -> AceCertificate:
    """Deprecated ACE-native alias.

    Use :func:`ace_certificate`.
    Returns :class:`pirtm.ace.types.AceCertificate`.
    """

    warnings.warn(
        "ace_certificate_v2() is deprecated; use ace_certificate()",
        DeprecationWarning,
        stacklevel=2,
    )
    return ace_certificate(info, tail_norm=tail_norm)


def ace_certificate(
    info: StepInfo | Sequence[StepInfo],
    *,
    tail_norm: float = 0.0,
) -> AceCertificate:
    """Default ACE certificate path.

    Returns :class:`pirtm.ace.types.AceCertificate`.
    """

    records = _ensure_sequence(info)
    if not records:
        raise ValueError("no telemetry provided")
    return certify_l0(records, tail_norm=tail_norm, delta=0.0)


def contraction_certificate(
    info: StepInfo | Sequence[StepInfo],
    *,
    tail_norm: float = 0.0,
) -> Certificate:
    """Primary certificate API for contraction validation.

    Returns the stable :class:`pirtm.types.Certificate` bundle for callers that
    only need certified/margin/tail-bound diagnostics.
    """

    ace_cert = ace_certificate(info, tail_norm=tail_norm)
    return to_legacy_certificate(ace_cert)


def legacy_ace_certificate(
    info: StepInfo | Sequence[StepInfo],
    *,
    tail_norm: float = 0.0,
) -> Certificate:
    """Deprecated alias for the legacy certificate path."""

    warnings.warn(
        "legacy_ace_certificate() is deprecated; use contraction_certificate()",
        DeprecationWarning,
        stacklevel=2,
    )
    return contraction_certificate(info, tail_norm=tail_norm)


def iss_bound(
    info: StepInfo | Sequence[StepInfo],
    disturbance_norm: float,
) -> float:
    """Input-to-state stability bound given telemetry and disturbance norm."""

    records = _ensure_sequence(info)
    if not records:
        raise ValueError("no telemetry provided")
    max_q = max(r.q for r in records)
    if max_q >= 1.0:
        return float("inf")
    return disturbance_norm / (1.0 - max_q)
