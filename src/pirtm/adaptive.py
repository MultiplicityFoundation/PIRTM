from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import StepInfo


@dataclass
class AdaptiveMargin:
    """Holds an adaptive epsilon controller driven by telemetry."""

    epsilon: float = 0.05
    min_epsilon: float = 0.01
    max_epsilon: float = 0.25
    step_size: float = 0.01
    residual_target: float = 1e-5
    baseline: float | None = None

    def __post_init__(self) -> None:
        if self.baseline is None:
            self.baseline = self.epsilon

    def update(self, info: StepInfo) -> float:
        """Update epsilon using residual + contraction telemetry."""

        target = 1.0 - self.epsilon
        margin = target - info.q
        baseline = self.baseline if self.baseline is not None else self.min_epsilon
        if info.q > target:
            self.epsilon = min(self.max_epsilon, self.epsilon + self.step_size)
        elif info.residual < self.residual_target and margin > 0.05:
            proposed = self.epsilon - self.step_size
            self.epsilon = max(self.min_epsilon, baseline, proposed)
        return self.epsilon
