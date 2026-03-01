from __future__ import annotations

import numpy as np


def project_parameters_soft(
    Xi: np.ndarray,
    Lam: np.ndarray,
    op_norm_T: float,
    target: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Scale (Ξ, Λ) so that ||Ξ|| + ||Λ|| * ||T|| <= target."""

    nXi = float(np.linalg.norm(Xi, 2))
    nLam = float(np.linalg.norm(Lam, 2))
    budget = nXi + nLam * op_norm_T

    if budget <= target or budget == 0.0:
        return Xi.copy(), Lam.copy()

    scale = target / budget
    return Xi * scale, Lam * scale


def project_parameters_weighted_l1(
    values: np.ndarray,
    weights: np.ndarray,
    budget: float,
    *,
    tol: float = 1e-9,
) -> tuple[np.ndarray, float]:
    """Project ``values`` onto the weighted-\u21111 ball ``sum w_i |x_i| <= budget``."""

    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if values.shape != weights.shape:
        raise ValueError("values and weights must match")
    if np.any(weights < 0):
        raise ValueError("weights must be non-negative")
    if budget < 0:
        raise ValueError("budget must be non-negative")

    weighted_norm = float(np.sum(weights * np.abs(values)))
    if weighted_norm <= budget + tol:
        return values.copy(), 0.0

    if not np.any(weights > 0):
        # Degenerate case: weights are all zero so the constraint is vacuous.
        return values.copy(), 0.0

    # Only weighted entries participate in the threshold search.
    mask = weights > 0
    abs_vals = np.abs(values[mask])
    w = weights[mask]
    ratios = abs_vals / w
    order = np.argsort(ratios)[::-1]
    ratios_sorted = ratios[order]
    abs_sorted = abs_vals[order]
    w_sorted = w[order]

    prefix_w_abs = np.cumsum(w_sorted * abs_sorted)
    prefix_w_sq = np.cumsum(w_sorted**2)

    tau = 0.0
    for k in range(len(abs_sorted)):
        tau = (prefix_w_abs[k] - budget) / prefix_w_sq[k]
        next_ratio = ratios_sorted[k + 1] if k + 1 < len(abs_sorted) else -np.inf
        if tau <= ratios_sorted[k] + tol and tau >= next_ratio - tol:
            break

    tau = max(tau, 0.0)

    # Refine tau with a short binary search to hit the budget tightly.
    lo, hi = 0.0, ratios_sorted[0]
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        proj = np.sign(abs_vals) * np.maximum(abs_vals - mid * w, 0.0)
        norm_val = float(np.sum(w * proj))
        if abs(norm_val - budget) < tol:
            tau = mid
            break
        if norm_val > budget:
            lo = mid
        else:
            hi = mid
            tau = mid

    projection = values.copy()
    projected_block = np.sign(values[mask]) * np.maximum(abs_vals - tau * w, 0.0)
    projection[mask] = projected_block
    return projection, tau
