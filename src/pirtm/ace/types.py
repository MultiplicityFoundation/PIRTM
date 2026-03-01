from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CertLevel(str, Enum):
    """ACE certificate fidelity tiers with TRL mapping."""

    L0_HEURISTIC = "L0-heuristic"
    L1_NORMBOUND = "L1-normbound"
    L2_POWERITER = "L2-poweriter"
    L3_NONEXPANSIVE = "L3-nonexpansive-clamp"
    L4_PERTURBATION = "L4-perturbation-budget"

    @property
    def trl(self) -> int:
        return {
            CertLevel.L0_HEURISTIC: 2,
            CertLevel.L1_NORMBOUND: 2,
            CertLevel.L2_POWERITER: 3,
            CertLevel.L3_NONEXPANSIVE: 4,
            CertLevel.L4_PERTURBATION: 4,
        }[self]


@dataclass(frozen=True)
class AceCertificate:
    """Machine-checkable ACE certificate produced by protocol levels."""

    level: CertLevel
    certified: bool
    lipschitz_upper: float
    gap_lb: float
    contraction_rate: float
    budget_used: float
    tau: float
    delta: float
    margin: float
    tail_bound: float
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.lipschitz_upper < 0:
            raise ValueError("lipschitz_upper must be >= 0")
        if self.certified and self.gap_lb <= 0:
            raise ValueError("certified certificates require gap_lb > 0")


@dataclass(frozen=True)
class AceBudgetState:
    """Snapshot of protocol budget state."""

    tau: float
    consumed: float
    depletion_rate: float

    @property
    def remaining(self) -> float:
        return max(0.0, self.tau - self.consumed)

    @property
    def is_depleted(self) -> bool:
        return self.consumed >= self.tau
