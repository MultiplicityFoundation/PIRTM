from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np


def fixed_point_estimate(
    history: Sequence[np.ndarray],
    *,
    window: int = 5,
) -> Tuple[np.ndarray, float]:
    """Average the last ``window`` iterates and report a tail deviation bound."""

    if not history:
        raise ValueError("history cannot be empty")

    window = max(1, min(window, len(history)))
    tail = np.stack(history[-window:])
    estimate = np.mean(tail, axis=0)
    deviations = [float(np.linalg.norm(x - estimate)) for x in tail]
    tail_bound = max(deviations) if deviations else 0.0
    return estimate, tail_bound
