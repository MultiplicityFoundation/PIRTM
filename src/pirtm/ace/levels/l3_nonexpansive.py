from __future__ import annotations

from ..telemetry import AceTelemetry
from ..types import AceCertificate, CertLevel
from .l2_poweriter import certify_l2


def certify_l3(
    telemetry: AceTelemetry,
    *,
    tau: float = 1.0,
    delta: float = 0.05,
) -> AceCertificate:
    if telemetry.designed_clamp_norm is None:
        raise TypeError("L3 requires designed_clamp_norm")
    base = certify_l2(telemetry, tau=tau, delta=delta)
    design_bound = float(telemetry.designed_clamp_norm)
    measured_bound = float(base.lipschitz_upper)
    lipschitz_upper = min(design_bound, measured_bound)
    gap_lb = 1.0 - lipschitz_upper

    return AceCertificate(
        level=CertLevel.L3_NONEXPANSIVE,
        certified=lipschitz_upper < (1.0 - delta),
        lipschitz_upper=lipschitz_upper,
        gap_lb=max(0.0, gap_lb),
        contraction_rate=lipschitz_upper,
        budget_used=base.budget_used,
        tau=tau,
        delta=delta,
        margin=gap_lb - delta,
        tail_bound=float("inf") if lipschitz_upper >= 1.0 else tau / max(1e-12, gap_lb),
        details={
            "measurement_domain": "SPECTRAL_PLUS_DESIGN_CLAMP",
            "designed_clamp_norm": design_bound,
            "measured_lipschitz_upper": measured_bound,
            "step": telemetry.step,
        },
    )
