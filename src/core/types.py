from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


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
    """Simple PETC (prime-typed event chain) diagnostic."""

    satisfied: bool
    violations: list[int]
    primes_checked: list[int]


@dataclass(slots=True)
class MonitorRecord:
    """Record stored by :class:`pirtm.monitor.Monitor`."""

    step: int
    info: StepInfo
    status: Optional[Status]
