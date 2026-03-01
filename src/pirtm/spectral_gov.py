from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from .spectral_decomp import phase_coherence, spectral_decomposition, spectral_entropy

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class SpectralReport:
    spectral_radius: float
    spectral_entropy: float
    phase_coherence: float
    op_norm_estimate: float
    contraction_feasible: bool
    recommended_epsilon: float
    eigenvalues: np.ndarray
    detail: dict


class SpectralGovernor:
    def __init__(
        self,
        dim: int,
        min_epsilon: float = 0.01,
        max_epsilon: float = 0.3,
        safety_margin: float = 0.1,
        entropy_ceiling: float = 2.0,
    ):
        self.dim = dim
        self.min_epsilon = min_epsilon
        self.max_epsilon = max_epsilon
        self.safety_margin = safety_margin
        self.entropy_ceiling = entropy_ceiling
        self._history: list[SpectralReport] = []

    def analyze(self, T: Callable[[np.ndarray], np.ndarray], n_samples: int = 10) -> SpectralReport:
        del n_samples
        jacobian = np.zeros((self.dim, self.dim), dtype=float)
        delta = 1e-5
        x0 = np.zeros(self.dim, dtype=float)
        f0 = np.asarray(T(x0), dtype=float)

        for index in range(self.dim):
            e_i = np.zeros(self.dim, dtype=float)
            e_i[index] = delta
            f_i = np.asarray(T(x0 + e_i), dtype=float)
            jacobian[:, index] = (f_i - f0) / delta

        eigvals, _ = spectral_decomposition(jacobian)
        spectral_radius = float(np.max(np.abs(eigvals))) if eigvals.size > 0 else 0.0
        entropy = float(spectral_entropy(eigvals))
        coherence = float(phase_coherence(eigvals))

        singular_values = np.linalg.svd(jacobian, compute_uv=False)
        op_norm_estimate = (
            float(singular_values[0]) if singular_values.size > 0 else spectral_radius
        )

        contraction_feasible = spectral_radius < 1.0
        if contraction_feasible:
            candidate = 1.0 - spectral_radius - self.safety_margin
            recommended = min(max(candidate, self.min_epsilon), self.max_epsilon)
        else:
            recommended = self.max_epsilon

        report = SpectralReport(
            spectral_radius=spectral_radius,
            spectral_entropy=entropy,
            phase_coherence=coherence,
            op_norm_estimate=op_norm_estimate,
            contraction_feasible=contraction_feasible,
            recommended_epsilon=recommended,
            eigenvalues=eigvals,
            detail={
                "dim": self.dim,
                "jacobian_norm": float(np.linalg.norm(jacobian)),
                "singular_values": singular_values.tolist(),
                "entropy_within_ceiling": entropy <= self.entropy_ceiling,
            },
        )
        self._history.append(report)
        return report

    def govern(self, T: Callable[[np.ndarray], np.ndarray]) -> tuple[float, float, SpectralReport]:
        report = self.analyze(T)
        return report.recommended_epsilon, report.op_norm_estimate, report

    def trend(self) -> dict:
        if not self._history:
            return {"reports": 0}

        radii = [report.spectral_radius for report in self._history]
        entropies = [report.spectral_entropy for report in self._history]
        return {
            "reports": len(self._history),
            "radius_min": min(radii),
            "radius_max": max(radii),
            "radius_trend": "stable" if max(radii) - min(radii) < 0.05 else "volatile",
            "entropy_mean": sum(entropies) / len(entropies),
            "contraction_rate": sum(1 for report in self._history if report.contraction_feasible)
            / len(self._history),
        }

    @property
    def history(self) -> list[SpectralReport]:
        return list(self._history)
