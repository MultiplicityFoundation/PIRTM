from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .adaptive import AdaptiveMargin
from .audit import AuditChain
from .certify import ace_certificate
from .gate import EmissionGate, EmissionPolicy, GatedOutput
from .telemetry import TelemetryBus
from .types import Certificate, StepInfo


@dataclass
class QARIConfig:
    dim: int
    epsilon: float = 0.05
    op_norm_T: float = 1.0
    emission_policy: EmissionPolicy = EmissionPolicy.SUPPRESS
    adaptive: bool = True
    audit: bool = True
    max_steps: int = 1000
    convergence_tol: float = 1e-6


class QARISession:
    def __init__(
        self,
        config: QARIConfig,
        projector: Callable[[np.ndarray], np.ndarray] | None = None,
        custom_predicate: Callable[[np.ndarray, StepInfo], bool] | None = None,
        telemetry: TelemetryBus | None = None,
    ):
        self.config = config
        self.P = projector or (lambda x: x)
        self._gate = EmissionGate(
            policy=config.emission_policy,
            custom_predicate=custom_predicate,
        )
        self._margin = AdaptiveMargin(epsilon=config.epsilon) if config.adaptive else None
        self._telemetry = telemetry or TelemetryBus()
        self._audit = AuditChain() if config.audit else None

        self._step_count = 0
        self._infos: list[StepInfo] = []
        self._epsilon = float(config.epsilon)

    def step(
        self,
        X_t: np.ndarray,
        Xi_t: np.ndarray,
        Lam_t: np.ndarray,
        T: Callable[[np.ndarray], np.ndarray],
        G_t: np.ndarray,
    ) -> GatedOutput:
        if self._step_count >= self.config.max_steps:
            raise RuntimeError(f"QARISession exceeded max_steps ({self.config.max_steps})")

        result = self._gate(
            X_t,
            Xi_t,
            Lam_t,
            T,
            G_t,
            self.P,
            epsilon=self._epsilon,
            op_norm_T=self.config.op_norm_T,
        )

        self._infos.append(result.info)
        self._telemetry.emit_step(self._step_count, result.info)
        self._telemetry.emit_gate(self._step_count, result)

        if self._audit is not None:
            self._audit.append_step(result.info)
            self._audit.append_gate(
                self._step_count,
                result.emitted,
                result.policy_applied,
                result.suppression_reason,
            )

        if self._margin is not None:
            self._epsilon = self._margin.update(result.info)

        self._step_count += 1
        return result

    def certify(self, tail_norm: float = 0.0) -> Certificate:
        if not self._infos:
            raise ValueError("No steps recorded. Call step() first.")
        cert = ace_certificate(self._infos, tail_norm=tail_norm)
        self._telemetry.emit_certificate(cert)
        if self._audit is not None:
            self._audit.append_certificate(cert)
        return cert

    @property
    def step_count(self) -> int:
        return self._step_count

    @property
    def current_epsilon(self) -> float:
        return self._epsilon

    @property
    def audit_chain(self) -> AuditChain | None:
        return self._audit

    @property
    def infos(self) -> list[StepInfo]:
        return list(self._infos)

    def summary(self) -> dict:
        if not self._infos:
            return {"steps": 0}
        qs = [entry.q for entry in self._infos]
        residuals = [entry.residual for entry in self._infos]
        projected = sum(1 for entry in self._infos if entry.projected)
        return {
            "steps": self._step_count,
            "q_max": max(qs),
            "q_min": min(qs),
            "q_mean": sum(qs) / len(qs),
            "residual_final": residuals[-1],
            "projected_count": projected,
            "projection_rate": projected / len(self._infos),
            "epsilon_current": self._epsilon,
            "audit_chain_length": len(self._audit) if self._audit is not None else 0,
        }
