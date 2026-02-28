from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np


@dataclass(slots=True)
class StepInfo:
    """Telemetry for a single contractive step."""

    step: int
    q: float
    epsilon: float
    nXi: float
    nLam: float
    projected: bool
    residual: float
    note: Optional[str] = None


@dataclass(slots=True)
class Status:
    """Safety + convergence status after running the recurrence."""

    converged: bool
    safe: bool
    steps: int
    residual: float
    epsilon: float
    note: Optional[str] = None


@dataclass(slots=True)
class Certificate:
    """Basic certificate bundle returned by :func:`ace_certificate`."""

    certified: bool
    margin: float
    tail_bound: float
    details: dict = field(default_factory=dict)


@dataclass(slots=True)
class PETCReport:
    """Full PETC chain diagnostic."""

    satisfied: bool
    chain_length: int = 0
    coverage: float = 0.0
    gap_violations: list[tuple[int, int]] = field(default_factory=list)
    monotonic: bool = True
    violations: list[int] = field(default_factory=list)
    primes_checked: list[int] = field(default_factory=list)


@dataclass(slots=True)
class PETCEntry:
    """Single entry in a PETC ledger."""

    prime: int
    event: Any = None
    info: StepInfo | None = None
    timestamp: float | None = None


@dataclass(slots=True)
class MonitorRecord:
    """Record stored by :class:`pirtm.monitor.Monitor`."""

    step: int
    info: StepInfo
    status: Optional[Status]


@dataclass(slots=True)
class WeightSchedule:
    """Pre-computed weight sequences for the contractive recurrence."""

    Xi_seq: list[np.ndarray]
    Lam_seq: list[np.ndarray]
    q_targets: np.ndarray
    primes_used: list[int]


@dataclass(slots=True)
class CSCBudget:
    """Parameter budget satisfying the contractive sufficient condition."""

    Xi_norm_max: float
    Lam_norm_max: float
    q_star: float
    epsilon: float
    op_norm_T: float
    alpha: float


@dataclass(slots=True)
class CSCMargin:
    """Margin analysis for a given parameter configuration."""

    margin: float
    q_actual: float
    q_target: float
    T_headroom: float
    epsilon_headroom: float
    safe: bool
