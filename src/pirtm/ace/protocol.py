from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from pirtm.types import StepInfo

from .budget import AceBudget
from .levels import certify_l0, certify_l1_from_telemetry, certify_l2, certify_l3, certify_l4
from .telemetry import AceTelemetry
from .types import AceBudgetState, AceCertificate, CertLevel
from .witness import AceWitness

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pirtm.types import Certificate

_LEVEL_ORDER = [
    CertLevel.L0_HEURISTIC,
    CertLevel.L1_NORMBOUND,
    CertLevel.L2_POWERITER,
    CertLevel.L3_NONEXPANSIVE,
    CertLevel.L4_PERTURBATION,
]


def _rank(level: CertLevel) -> int:
    return _LEVEL_ORDER.index(level)


class AceProtocol:
    """Unified ACE dispatcher with inject-if-absent design parameter defaults."""

    def __init__(
        self,
        tau: float = 1.0,
        delta: float = 0.05,
        designed_clamp_norm: float | None = None,
        designed_perturbation_bound: float | None = None,
    ) -> None:
        if tau <= 0:
            raise ValueError("tau must be > 0")
        if not (0 < delta < 1):
            raise ValueError("delta must be in (0, 1)")
        if designed_clamp_norm is not None and not (0 < designed_clamp_norm <= 1.0):
            raise ValueError("designed_clamp_norm must be in (0, 1]")
        if designed_perturbation_bound is not None and designed_perturbation_bound < 0:
            raise ValueError("designed_perturbation_bound must be >= 0")

        self.budget = AceBudget(tau=tau)
        self.delta = delta
        self.designed_clamp_norm = designed_clamp_norm
        self.designed_perturbation_bound = designed_perturbation_bound

    def certify(
        self,
        telemetry: AceTelemetry | StepInfo | Sequence[AceTelemetry | StepInfo],
        prime_index: int,
        *,
        min_level: CertLevel = CertLevel.L0_HEURISTIC,
        tail_norm: float = 0.0,
    ) -> AceWitness:
        records = self._normalise(telemetry)
        if not records:
            raise ValueError("AceProtocol.certify: no telemetry provided")

        for rec in records:
            rec.validate()

        ranked_records = [(rec.highest_feasible_level(), rec) for rec in records]
        feasible, representative = max(ranked_records, key=lambda item: (_rank(item[0]), item[1].q))
        if _rank(feasible) < _rank(min_level):
            raise ValueError(
                f"AceProtocol.certify: telemetry supports up to {feasible.value} "
                f"but min_level={min_level.value} was requested"
            )

        tau = self.budget.snapshot().tau
        if feasible == CertLevel.L4_PERTURBATION:
            cert = certify_l4(representative, tau=tau, delta=self.delta)
        elif feasible == CertLevel.L3_NONEXPANSIVE:
            cert = certify_l3(representative, tau=tau, delta=self.delta)
        elif feasible == CertLevel.L2_POWERITER:
            cert = certify_l2(representative, tau=tau, delta=self.delta)
        elif feasible == CertLevel.L1_NORMBOUND:
            cert = certify_l1_from_telemetry(representative, tau=tau, delta=self.delta)
        else:
            cert = certify_l0(
                [rec.to_step_info() for rec in records], tau=tau, tail_norm=tail_norm, delta=0.0
            )

        self.budget.consume(cert.budget_used)
        return AceWitness.from_certificate(cert, prime_index)

    def budget_state(self) -> AceBudgetState:
        return self.budget.snapshot()

    def certify_from_telemetry(
        self,
        records: Sequence[StepInfo],
        prime_index: int,
        *,
        tail_norm: float = 0.0,
    ) -> AceWitness:
        warnings.warn(
            "certify_from_telemetry() is deprecated. Use certify().",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.certify(list(records), prime_index, tail_norm=tail_norm)

    def _normalise(
        self,
        telemetry: AceTelemetry | StepInfo | Sequence[AceTelemetry | StepInfo],
    ) -> list[AceTelemetry]:
        if isinstance(telemetry, AceTelemetry):
            return [self._inject_design_params(telemetry)]
        if isinstance(telemetry, StepInfo):
            return [self._inject_design_params(AceTelemetry.from_step_info(telemetry))]

        result: list[AceTelemetry] = []
        for item in telemetry:
            if isinstance(item, AceTelemetry):
                result.append(self._inject_design_params(item))
            elif isinstance(item, StepInfo):
                result.append(self._inject_design_params(AceTelemetry.from_step_info(item)))
            else:
                raise TypeError(f"unsupported telemetry item: {type(item)!r}")
        return result

    def _inject_design_params(self, telemetry: AceTelemetry) -> AceTelemetry:
        needs_clamp_injection = (
            telemetry.designed_clamp_norm is None and self.designed_clamp_norm is not None
        )
        needs_perturbation_injection = (
            telemetry.designed_perturbation_bound is None
            and self.designed_perturbation_bound is not None
        )

        if not needs_clamp_injection and not needs_perturbation_injection:
            return telemetry

        injected = AceTelemetry(**telemetry.__dict__)
        if needs_clamp_injection:
            injected.designed_clamp_norm = self.designed_clamp_norm
        if needs_perturbation_injection:
            injected.designed_perturbation_bound = self.designed_perturbation_bound
        return injected


def to_legacy_certificate(certificate: AceCertificate) -> Certificate:
    from pirtm.types import Certificate

    return Certificate(
        certified=certificate.certified,
        margin=certificate.margin,
        tail_bound=certificate.tail_bound,
        details={
            "max_q": certificate.lipschitz_upper,
            "target": 1.0 - certificate.delta,
            "steps": int(certificate.details.get("steps", 1)),
            "ace_level": certificate.level.value,
            **certificate.details,
        },
    )
