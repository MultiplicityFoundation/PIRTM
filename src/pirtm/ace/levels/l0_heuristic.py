from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import AceCertificate, CertLevel

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pirtm.types import StepInfo


def certify_l0(
    records: Sequence[StepInfo],
    *,
    tau: float = 1.0,
    tail_norm: float = 0.0,
    delta: float = 0.0,
) -> AceCertificate:
    if not records:
        raise ValueError("L0: no telemetry provided")

    target = 1.0 - min(r.epsilon for r in records)
    max_q = max(r.q for r in records)
    margin = target - max_q
    certified = margin >= delta
    tail_bound = float("inf") if max_q >= 1.0 else tail_norm / max(1e-12, 1.0 - max_q)

    return AceCertificate(
        level=CertLevel.L0_HEURISTIC,
        certified=certified,
        lipschitz_upper=max_q,
        gap_lb=max(0.0, 1.0 - max_q),
        contraction_rate=max_q,
        budget_used=max_q,
        tau=tau,
        delta=delta,
        margin=margin,
        tail_bound=tail_bound,
        details={
            "max_q": max_q,
            "target": target,
            "steps": len(records),
        },
    )
