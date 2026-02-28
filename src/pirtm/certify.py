from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

from .types import Certificate, StepInfo


def _ensure_sequence(info: StepInfo | Sequence[StepInfo]) -> list[StepInfo]:
    if isinstance(info, StepInfo):
        return [info]
    return list(info)


def ace_certificate(
    info: StepInfo | Sequence[StepInfo],
    *,
    tail_norm: float = 0.0,
) -> Certificate:
    """Elementary ACE-style certificate from per-step telemetry."""

    records = _ensure_sequence(info)
    if not records:
        raise ValueError("no telemetry provided")

    target = 1.0 - min(r.epsilon for r in records)
    max_q = max(r.q for r in records)
    margin = target - max_q
    certified = margin >= 0
    if max_q >= 1.0:
        tail_bound = float("inf")
    else:
        tail_bound = tail_norm / max(1e-12, 1.0 - max_q)

    return Certificate(
        certified=certified,
        margin=margin,
        tail_bound=tail_bound,
        details={
            "max_q": max_q,
            "target": target,
            "steps": len(records),
        },
    )


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
