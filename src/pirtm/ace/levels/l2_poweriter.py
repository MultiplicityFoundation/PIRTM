from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ..contracts import assert_matrix_not_mutated
from ..types import AceCertificate, CertLevel

if TYPE_CHECKING:
    from ..telemetry import AceTelemetry


def certify_l2(
    telemetry: AceTelemetry,
    *,
    tau: float = 1.0,
    delta: float = 0.05,
    max_iter: int = 500,
    tol: float = 1e-8,
) -> AceCertificate:
    if telemetry.contraction_matrix is None and telemetry.spectral_estimate is None:
        raise TypeError("L2 requires contraction_matrix or spectral_estimate")

    if telemetry.spectral_estimate is not None:
        rho = float(telemetry.spectral_estimate)
        iterations_used = 0
        matrix_shape: list[int] | None = None
    else:
        matrix = telemetry.contraction_matrix
        if matrix is None:
            raise TypeError("L2 requires contraction_matrix when spectral_estimate is absent")
        with assert_matrix_not_mutated(matrix, "L2"):
            n = matrix.shape[0]
            rng = np.random.default_rng(seed=42)
            vector = np.asarray(rng.standard_normal(size=(n,)), dtype=float)
            vector = np.asarray(vector / (np.linalg.norm(vector) + 1e-12), dtype=float)
            rho_prev = 0.0
            iterations_used = max_iter
            for index in range(max_iter):
                product = matrix @ vector
                rho = float(np.linalg.norm(product))
                vector = np.asarray(product / (rho + 1e-12), dtype=float)
                if abs(rho - rho_prev) < tol:
                    iterations_used = index + 1
                    break
                rho_prev = rho
            matrix_shape = [int(x) for x in matrix.shape]

    lipschitz_upper = rho
    gap_lb = 1.0 - lipschitz_upper
    certified = lipschitz_upper < (1.0 - delta)

    return AceCertificate(
        level=CertLevel.L2_POWERITER,
        certified=certified,
        lipschitz_upper=lipschitz_upper,
        gap_lb=max(0.0, gap_lb),
        contraction_rate=lipschitz_upper,
        budget_used=lipschitz_upper,
        tau=tau,
        delta=delta,
        margin=gap_lb - delta,
        tail_bound=float("inf") if lipschitz_upper >= 1.0 else tau / max(1e-12, gap_lb),
        details={
            "measurement_domain": "SPECTRAL_ONLY",
            "matrix_shape": matrix_shape,
            "spectral_estimate_used": telemetry.spectral_estimate is not None,
            "iterations": iterations_used,
            "step": telemetry.step,
        },
    )
