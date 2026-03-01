from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np

from .projection import project_parameters_soft
from .types import Status, StepInfo

Operator = Callable[[np.ndarray], np.ndarray]
Projector = Callable[[np.ndarray], np.ndarray]


def _operator_norm(A: np.ndarray) -> float:
    if A.size == 0:
        return 0.0
    return float(np.linalg.norm(A, 2))


def _apply_projector(P: Projector | object, X: np.ndarray) -> np.ndarray:
    if callable(P):
        return np.asarray(P(X), dtype=float)
    if hasattr(P, "apply"):
        return np.asarray(P.apply(X), dtype=float)
    raise TypeError("P must be callable or expose an 'apply' method")


def step(
    X_t: np.ndarray,
    Xi_t: np.ndarray,
    Lam_t: np.ndarray,
    T: Operator,
    G_t: np.ndarray,
    P: Projector | object,
    *,
    epsilon: float = 0.05,
    op_norm_T: float = 1.0,
    t: int = 0,
) -> tuple[np.ndarray, StepInfo]:
    """One contractive step with automatic safety projection."""

    nXi = _operator_norm(Xi_t)
    nLam = _operator_norm(Lam_t)
    q_t = nXi + nLam * op_norm_T
    target = 1.0 - float(epsilon)
    projected = False

    if q_t > target:
        Xi_t, Lam_t = project_parameters_soft(Xi_t, Lam_t, op_norm_T, target)
        projected = True
        nXi = _operator_norm(Xi_t)
        nLam = _operator_norm(Lam_t)
        q_t = nXi + nLam * op_norm_T

    candidate = Xi_t @ X_t + Lam_t @ T(X_t) + G_t
    X_next = _apply_projector(P, candidate)
    residual = float(np.linalg.norm(X_next - X_t))

    info = StepInfo(
        step=t,
        q=q_t,
        epsilon=float(epsilon),
        nXi=nXi,
        nLam=nLam,
        projected=projected,
        residual=residual,
    )
    return X_next, info


def run(
    X0: np.ndarray,
    Xi_seq: Sequence[np.ndarray],
    Lam_seq: Sequence[np.ndarray],
    G_seq: Sequence[np.ndarray],
    *,
    T: Operator,
    P: Projector | object,
    epsilon: float = 0.05,
    op_norm_T: float = 1.0,
    tol: float = 1e-6,
    max_steps: int | None = None,
) -> tuple[np.ndarray, list[np.ndarray], list[StepInfo], Status]:
    """Run the PIRTM recurrence until convergence or ``max_steps``."""

    X = np.array(X0, dtype=float)
    history = [X.copy()]
    infos: list[StepInfo] = []
    converged = False
    safe = True
    target = 1.0 - float(epsilon)

    T_max = min(len(Xi_seq), len(Lam_seq), len(G_seq))
    if max_steps is not None:
        T_max = min(T_max, max_steps)

    for t in range(T_max):
        X_next, info = step(
            X,
            Xi_seq[t],
            Lam_seq[t],
            T,
            G_seq[t],
            P,
            epsilon=epsilon,
            op_norm_T=op_norm_T,
            t=t,
        )
        infos.append(info)
        history.append(X_next.copy())
        X = X_next
        safe = safe and info.q <= target + 1e-12
        if info.residual < tol:
            converged = True
            break

    residual = infos[-1].residual if infos else float("inf")
    status = Status(
        converged=converged,
        safe=safe,
        steps=len(infos),
        residual=residual,
        epsilon=float(epsilon),
        note=None,
    )
    return X, history, infos, status
