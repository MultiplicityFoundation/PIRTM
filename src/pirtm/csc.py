from __future__ import annotations

from collections.abc import Sequence

from .types import CSCBudget, CSCMargin, StepInfo


def solve_budget(
    op_norm_T: float,
    *,
    epsilon: float = 0.05,
    alpha: float = 0.5,
) -> CSCBudget:
    if op_norm_T <= 0.0:
        raise ValueError("op_norm_T must be positive")
    if not (0.0 <= epsilon < 1.0):
        raise ValueError("epsilon must be in [0, 1)")
    if not (0.0 <= alpha <= 1.0):
        raise ValueError("alpha must be in [0, 1]")

    q_star = 1.0 - epsilon
    xi_norm_max = alpha * q_star
    lam_norm_max = ((1.0 - alpha) * q_star) / op_norm_T
    return CSCBudget(
        Xi_norm_max=xi_norm_max,
        Lam_norm_max=lam_norm_max,
        q_star=q_star,
        epsilon=epsilon,
        op_norm_T=op_norm_T,
        alpha=alpha,
    )


def compute_margin(
    Xi_norm: float,
    Lam_norm: float,
    op_norm_T: float,
    *,
    epsilon: float = 0.05,
) -> CSCMargin:
    q_target = 1.0 - epsilon
    q_actual = float(Xi_norm + Lam_norm * op_norm_T)
    margin = q_target - q_actual

    if Lam_norm > 0.0:
        t_headroom = ((1.0 - epsilon) - Xi_norm) / Lam_norm
    else:
        t_headroom = float("inf")

    epsilon_headroom = max(0.0, margin)
    return CSCMargin(
        margin=margin,
        q_actual=q_actual,
        q_target=q_target,
        T_headroom=t_headroom,
        epsilon_headroom=epsilon_headroom,
        safe=margin >= 0.0,
    )


def multi_step_margin(infos: Sequence[StepInfo]) -> CSCMargin:
    if not infos:
        raise ValueError("infos must not be empty")

    worst = min(infos, key=lambda info: (1.0 - info.epsilon) - info.q)
    q_target = 1.0 - worst.epsilon
    q_actual = worst.q
    margin = q_target - q_actual

    if worst.nLam > 0.0:
        t_headroom = (q_target - worst.nXi) / worst.nLam
    else:
        t_headroom = float("inf")

    return CSCMargin(
        margin=margin,
        q_actual=q_actual,
        q_target=q_target,
        T_headroom=t_headroom,
        epsilon_headroom=max(0.0, margin),
        safe=margin >= 0.0,
    )


def sensitivity(
    Xi_norm: float,
    Lam_norm: float,
    *,
    epsilon: float = 0.05,
) -> dict[str, float]:
    q_target = 1.0 - epsilon
    if Lam_norm > 0.0:
        t_max = (q_target - Xi_norm) / Lam_norm
    else:
        t_max = float("inf")

    epsilon_min = max(0.0, Xi_norm + Lam_norm - 1.0)
    epsilon_headroom = float("inf") if Xi_norm == 0.0 and Lam_norm == 0.0 else max(0.0, epsilon - epsilon_min)
    return {
        "T_max": t_max,
        "epsilon_min": epsilon_min,
        "epsilon_headroom": epsilon_headroom,
    }
