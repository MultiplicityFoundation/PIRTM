from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from pirtm.certify import ace_certificate
from pirtm.gain import estimate_operator_norm
from pirtm.recurrence import run, step

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from pirtm.types import StepInfo


def drmm_step(
    X: np.ndarray,
    Xi_matrix: np.ndarray,
    Lam_matrix: np.ndarray,
    T: Callable[[np.ndarray], np.ndarray],
    G: np.ndarray | None = None,
    *,
    epsilon: float = 0.05,
    op_norm_T: float | None = None,
) -> tuple[np.ndarray, StepInfo]:
    if G is None:
        G = np.zeros_like(X)

    def P(x: np.ndarray) -> np.ndarray:
        return x

    if op_norm_T is None:
        op_norm_T, _ = estimate_operator_norm(T, dim=int(X.shape[0]))

    return step(X, Xi_matrix, Lam_matrix, T, G, P, epsilon=epsilon, op_norm_T=op_norm_T)


def drmm_evolve(
    X0: np.ndarray,
    Xi_sequence: Sequence[np.ndarray],
    Lam_sequence: Sequence[np.ndarray],
    T: Callable[[np.ndarray], np.ndarray],
    G_sequence: Sequence[np.ndarray] | None = None,
    *,
    epsilon: float = 0.05,
    op_norm_T: float | None = None,
    certify: bool = True,
) -> dict[str, Any]:
    n_steps = len(Xi_sequence)
    if G_sequence is None:
        G_sequence = [np.zeros_like(X0)] * n_steps

    def P(x: np.ndarray) -> np.ndarray:
        return x

    if op_norm_T is None:
        op_norm_T, _ = estimate_operator_norm(T, dim=int(X0.shape[0]))

    X_final, history, infos, status = run(
        X0,
        Xi_sequence,
        Lam_sequence,
        G_sequence,
        T=T,
        P=P,
        epsilon=epsilon,
        op_norm_T=op_norm_T,
    )

    result: dict[str, Any] = {
        "X_final": X_final,
        "history": history,
        "infos": infos,
        "status": status,
        "certificate": None,
    }
    if certify:
        result["certificate"] = ace_certificate(infos)
    return result
