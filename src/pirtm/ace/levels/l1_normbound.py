from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ..types import AceCertificate, CertLevel

if TYPE_CHECKING:
    from ..telemetry import AceTelemetry


def certify_l1(
    weight_vector: list[float],
    basis_norms: list[float],
    *,
    tau: float = 1.0,
    delta: float = 0.05,
) -> AceCertificate:
    if len(weight_vector) != len(basis_norms):
        raise ValueError("L1 requires weight_vector and basis_norms to have equal length")
    if not weight_vector:
        raise ValueError("L1 requires non-empty weight_vector")

    lipschitz_upper = float(np.sum(np.abs(weight_vector) * np.asarray(basis_norms, dtype=float)))
    gap_lb = 1.0 - lipschitz_upper
    certified = lipschitz_upper < (1.0 - delta)

    return AceCertificate(
        level=CertLevel.L1_NORMBOUND,
        certified=certified,
        lipschitz_upper=lipschitz_upper,
        gap_lb=max(0.0, gap_lb),
        contraction_rate=lipschitz_upper,
        budget_used=lipschitz_upper,
        tau=tau,
        delta=delta,
        margin=gap_lb - delta,
        tail_bound=float("inf") if lipschitz_upper >= 1.0 else tau / max(1e-12, gap_lb),
        details={
            "measurement_domain": "WEIGHTED_L1",
            "term_count": len(weight_vector),
        },
    )


def certify_l1_from_telemetry(
    telemetry: AceTelemetry,
    *,
    tau: float = 1.0,
    delta: float = 0.05,
) -> AceCertificate:
    if telemetry.weight_vector is None or telemetry.basis_norms is None:
        raise TypeError("L1 requires telemetry.weight_vector and telemetry.basis_norms")
    return certify_l1(telemetry.weight_vector, telemetry.basis_norms, tau=tau, delta=delta)
