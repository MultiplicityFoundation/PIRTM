from __future__ import annotations

from ..telemetry import AceTelemetry
from ..types import AceCertificate, CertLevel
from .l3_nonexpansive import certify_l3


def certify_l4(
    telemetry: AceTelemetry,
    *,
    tau: float = 1.0,
    delta: float = 0.05,
) -> AceCertificate:
    if telemetry.designed_perturbation_bound is None:
        raise TypeError("L4 requires designed_perturbation_bound")
    if telemetry.disturbance_norm is None:
        raise TypeError("L4 requires disturbance_norm")

    base = certify_l3(telemetry, tau=tau, delta=delta)
    perturb_bound = float(telemetry.designed_perturbation_bound)
    lipschitz_upper = float(base.lipschitz_upper)
    gap_lb = 1.0 - lipschitz_upper
    tail_bound = float("inf") if gap_lb <= 0 else float(telemetry.disturbance_norm) / max(1e-12, gap_lb)

    return AceCertificate(
        level=CertLevel.L4_PERTURBATION,
        certified=lipschitz_upper < (1.0 - delta),
        lipschitz_upper=lipschitz_upper,
        gap_lb=max(0.0, gap_lb),
        contraction_rate=lipschitz_upper,
        budget_used=base.budget_used + max(0.0, perturb_bound),
        tau=tau,
        delta=delta,
        margin=gap_lb - delta,
        tail_bound=tail_bound,
        details={
            "measurement_domain": "SPECTRAL_CLAMP_PERTURBATION",
            "designed_perturbation_bound": perturb_bound,
            "disturbance_norm": float(telemetry.disturbance_norm),
            "step": telemetry.step,
        },
    )
