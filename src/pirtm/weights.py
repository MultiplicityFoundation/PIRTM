from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Literal

import numpy as np

from .types import WeightSchedule

WeightProfile = Literal["uniform", "log_decay", "harmonic"] | Callable[[int, int], float]


def _resolve_alphas(primes: Sequence[int], profile: WeightProfile) -> np.ndarray:
    count = len(primes)
    if count == 0:
        return np.array([], dtype=float)

    if profile == "uniform":
        return np.full(count, 0.5, dtype=float)

    if profile == "harmonic":
        values = np.array([1.0 / index for index in range(1, count + 1)], dtype=float)
        return np.asarray(np.clip(values, 0.0, 1.0), dtype=float)

    if profile == "log_decay":
        raw = np.array(
            [1.0 / max(math.log(max(2, int(prime))), 1e-12) for prime in primes], dtype=float
        )
        minimum = float(np.min(raw))
        maximum = float(np.max(raw))
        if maximum - minimum < 1e-12:
            return np.full(count, 0.5, dtype=float)
        normalized = (raw - minimum) / (maximum - minimum)
        return np.asarray(np.clip(normalized, 0.0, 1.0), dtype=float)

    values = np.array(
        [float(profile(index, int(prime))) for index, prime in enumerate(primes, start=1)],
        dtype=float,
    )
    return np.asarray(np.clip(values, 0.0, 1.0), dtype=float)


def synthesize_weights(
    primes: Sequence[int],
    dim: int,
    *,
    op_norm_T: float = 1.0,
    q_star: float = 0.9,
    profile: WeightProfile = "log_decay",
    epsilon: float = 0.05,
    basis: np.ndarray | None = None,
) -> WeightSchedule:
    if dim <= 0:
        raise ValueError("dim must be positive")
    if op_norm_T <= 0.0:
        raise ValueError("op_norm_T must be positive")

    q_target = min(float(q_star), 1.0 - float(epsilon))
    q_target = max(0.0, q_target)
    primes_used = [int(prime) for prime in primes]
    alphas = _resolve_alphas(primes_used, profile)
    q_targets = np.full(len(primes_used), q_target, dtype=float)

    if basis is None:
        base = np.eye(dim, dtype=float)
    else:
        base = np.asarray(basis, dtype=float)
        if base.shape != (dim, dim):
            raise ValueError("basis must have shape (dim, dim)")

    denom = 1.0 + float(op_norm_T)
    xi_seq: list[np.ndarray] = []
    lam_seq: list[np.ndarray] = []
    for alpha in alphas:
        xi_scale = (alpha * q_target) / denom
        lam_scale = ((1.0 - alpha) * q_target) / (denom * op_norm_T)
        xi_seq.append(xi_scale * base)
        lam_seq.append(lam_scale * base)

    return WeightSchedule(
        Xi_seq=xi_seq,
        Lam_seq=lam_seq,
        q_targets=q_targets,
        primes_used=primes_used,
    )


def validate_schedule(
    schedule: WeightSchedule,
    op_norm_T: float,
    *,
    tol: float = 1e-12,
) -> tuple[bool, float]:
    if op_norm_T < 0.0:
        raise ValueError("op_norm_T must be non-negative")

    max_q = 0.0
    valid = True
    for xi, lam, target in zip(schedule.Xi_seq, schedule.Lam_seq, schedule.q_targets, strict=True):
        q_value = float(np.linalg.norm(xi, 2) + np.linalg.norm(lam, 2) * op_norm_T)
        max_q = max(max_q, q_value)
        if q_value > float(target) + tol:
            valid = False
    return valid, max_q
