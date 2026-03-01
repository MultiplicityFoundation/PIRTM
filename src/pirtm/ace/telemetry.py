from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pirtm.types import StepInfo

from .types import CertLevel

if TYPE_CHECKING:
    import numpy as np

_DESIGN_ENVELOPE_TOL = 1e-9


@dataclass
class AceTelemetry:
    """Unified telemetry structure for ACE protocol levels."""

    step: int
    q: float
    epsilon: float
    nXi: float
    nLam: float
    projected: bool
    residual: float
    note: str | None = None

    weight_vector: list[float] | None = None
    basis_norms: list[float] | None = None

    contraction_matrix: np.ndarray | None = None
    spectral_estimate: float | None = None

    designed_clamp_norm: float | None = None
    clamp_radius: float | None = None

    designed_perturbation_bound: float | None = None
    disturbance_norm: float | None = None

    @classmethod
    def from_step_info(cls, info: StepInfo) -> AceTelemetry:
        return cls(
            step=info.step,
            q=info.q,
            epsilon=info.epsilon,
            nXi=info.nXi,
            nLam=info.nLam,
            projected=info.projected,
            residual=info.residual,
            note=info.note,
        )

    def highest_feasible_level(self) -> CertLevel:
        if (
            self.designed_perturbation_bound is not None
            and self.disturbance_norm is not None
            and (self.contraction_matrix is not None or self.spectral_estimate is not None)
        ):
            return CertLevel.L4_PERTURBATION
        if self.designed_clamp_norm is not None and (
            self.contraction_matrix is not None or self.spectral_estimate is not None
        ):
            return CertLevel.L3_NONEXPANSIVE
        if self.contraction_matrix is not None or self.spectral_estimate is not None:
            return CertLevel.L2_POWERITER
        if self.weight_vector is not None and self.basis_norms is not None:
            return CertLevel.L1_NORMBOUND
        return CertLevel.L0_HEURISTIC

    def validate(self) -> None:
        if self.q < 0:
            raise ValueError("AceTelemetry.q must be >= 0")
        if not (0.0 < self.epsilon <= 1.0):
            raise ValueError("AceTelemetry.epsilon must be in (0, 1]")

        if (
            self.weight_vector is not None
            and self.basis_norms is not None
            and len(self.weight_vector) != len(self.basis_norms)
        ):
            raise ValueError("weight_vector and basis_norms must have equal length")

        if self.contraction_matrix is not None:
            matrix = self.contraction_matrix
            if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
                raise ValueError("contraction_matrix must be square 2-D")

        if self.designed_clamp_norm is not None:
            if self.designed_clamp_norm > 1.0 + _DESIGN_ENVELOPE_TOL:
                raise ValueError("DESIGN_PARAMETER_INVALID: designed_clamp_norm > 1.0")
            if self.nXi > self.designed_clamp_norm + _DESIGN_ENVELOPE_TOL:
                raise RuntimeError(
                    "DESIGN_ENVELOPE_VIOLATION: nXi(runtime) exceeds designed_clamp_norm"
                )

        if self.designed_perturbation_bound is not None:
            if self.designed_perturbation_bound < 0:
                raise ValueError("DESIGN_PARAMETER_INVALID: designed_perturbation_bound < 0")
            if self.nLam > self.designed_perturbation_bound + _DESIGN_ENVELOPE_TOL:
                raise RuntimeError(
                    "DESIGN_ENVELOPE_VIOLATION: nLam(runtime) exceeds designed_perturbation_bound"
                )

    def to_step_info(self) -> StepInfo:
        return StepInfo(
            step=self.step,
            q=self.q,
            epsilon=self.epsilon,
            nXi=self.nXi,
            nLam=self.nLam,
            projected=self.projected,
            residual=self.residual,
            note=self.note,
        )
