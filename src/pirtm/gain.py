from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Literal

import numpy as np

from .certify import iss_bound

if TYPE_CHECKING:
    from .types import StepInfo

GainProfile = Literal["constant", "decay", "random", "zero"] | Callable[[int], np.ndarray]


def estimate_operator_norm(
    T: Callable[[np.ndarray], np.ndarray],
    dim: int,
    *,
    max_iter: int = 200,
    tol: float = 1e-10,
    seed: int | None = None,
) -> tuple[float, int]:
    if dim <= 0:
        raise ValueError("dim must be positive")

    rng = np.random.default_rng(42 if seed is None else seed)
    vector = rng.standard_normal(dim)
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        vector = np.ones(dim, dtype=float)
        norm = float(np.linalg.norm(vector))
    vector = vector / norm

    previous = 0.0
    for index in range(1, max_iter + 1):
        image = np.asarray(T(vector), dtype=float)
        estimate = float(np.linalg.norm(image))
        if estimate == 0.0:
            return 0.0, index
        vector = image / estimate
        if abs(estimate - previous) < tol:
            return estimate, index
        previous = estimate
    return previous, max_iter


def build_gain_sequence(
    length: int,
    dim: int,
    *,
    scale: float = 0.01,
    profile: GainProfile = "decay",
    decay_rate: float = 1.0,
    seed: int | None = None,
) -> list[np.ndarray]:
    if length < 0:
        raise ValueError("length must be non-negative")
    if dim <= 0:
        raise ValueError("dim must be positive")

    rng = np.random.default_rng(seed)
    unit = np.ones(dim, dtype=float)
    unit /= float(np.linalg.norm(unit))

    gains: list[np.ndarray] = []
    for index in range(length):
        if callable(profile):
            value = np.asarray(profile(index), dtype=float)
        elif profile == "zero":
            value = np.zeros(dim, dtype=float)
        elif profile == "constant":
            value = scale * unit
        elif profile == "decay":
            value = (scale / ((1.0 + index) ** decay_rate)) * unit
        elif profile == "random":
            value = rng.uniform(-scale, scale, size=dim)
            value_norm = float(np.linalg.norm(value))
            if value_norm > scale and value_norm > 0.0:
                value = value * (scale / value_norm)
        else:
            raise ValueError(f"unknown profile: {profile}")

        if value.shape != (dim,):
            raise ValueError("gain vectors must have shape (dim,)")
        gains.append(value)

    return gains


def check_iss_compatibility(
    gains: Sequence[np.ndarray],
    infos: Sequence[StepInfo],
    target_radius: float,
) -> tuple[bool, float]:
    if target_radius < 0.0:
        raise ValueError("target_radius must be non-negative")
    if not infos:
        raise ValueError("infos must not be empty")

    gain_norms = [float(np.linalg.norm(np.asarray(gain, dtype=float))) for gain in gains]
    max_gain_norm = max(gain_norms, default=0.0)
    bound = iss_bound(infos, disturbance_norm=max_gain_norm)
    compatible = np.isfinite(bound) and bound <= target_radius
    return bool(compatible), max_gain_norm
