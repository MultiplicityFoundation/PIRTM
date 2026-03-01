from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from .recurrence import step

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from .types import StepInfo


class EmissionPolicy(enum.Enum):
    PASS_THROUGH = "pass_through"
    SUPPRESS = "suppress"
    HOLD = "hold"
    ATTENUATE = "attenuate"


@dataclass(frozen=True)
class GatedOutput:
    X_next: np.ndarray
    info: StepInfo
    emitted: bool
    policy_applied: str
    suppression_reason: str


class EmissionGate:
    def __init__(
        self,
        policy: EmissionPolicy = EmissionPolicy.SUPPRESS,
        custom_predicate: Callable[[np.ndarray, StepInfo], bool] | None = None,
        attenuation_floor: float = 0.01,
    ):
        self.policy = policy
        self.custom_predicate = custom_predicate
        self.attenuation_floor = float(attenuation_floor)

    def __call__(
        self,
        X_t: np.ndarray,
        Xi_t: np.ndarray,
        Lam_t: np.ndarray,
        T: Callable[[np.ndarray], np.ndarray],
        G_t: np.ndarray,
        P: Callable[[np.ndarray], np.ndarray] | object,
        *,
        epsilon: float = 0.05,
        op_norm_T: float = 1.0,
    ) -> GatedOutput:
        X_next, info = step(
            X_t,
            Xi_t,
            Lam_t,
            T,
            G_t,
            P,
            epsilon=epsilon,
            op_norm_T=op_norm_T,
        )

        contraction_ok = not info.projected
        custom_ok = True
        if self.custom_predicate is not None:
            custom_ok = bool(self.custom_predicate(X_next, info))

        if contraction_ok and custom_ok:
            return GatedOutput(
                X_next=X_next,
                info=info,
                emitted=True,
                policy_applied="none",
                suppression_reason="",
            )

        reason: list[str] = []
        if not contraction_ok:
            reason.append(f"projection_triggered(q={info.q:.4f})")
        if not custom_ok:
            reason.append("custom_predicate_failed")

        if self.policy == EmissionPolicy.PASS_THROUGH:
            return GatedOutput(
                X_next=X_next,
                info=info,
                emitted=True,
                policy_applied="pass_through",
                suppression_reason="; ".join(reason),
            )

        if self.policy == EmissionPolicy.SUPPRESS:
            return GatedOutput(
                X_next=np.zeros_like(X_t),
                info=info,
                emitted=False,
                policy_applied="suppress",
                suppression_reason="; ".join(reason),
            )

        if self.policy == EmissionPolicy.HOLD:
            return GatedOutput(
                X_next=np.array(X_t, copy=True),
                info=info,
                emitted=False,
                policy_applied="hold",
                suppression_reason="; ".join(reason),
            )

        if self.policy == EmissionPolicy.ATTENUATE:
            margin = max(1.0 - float(epsilon) - float(info.q), 0.0)
            scale = max(margin, self.attenuation_floor)
            return GatedOutput(
                X_next=scale * X_next,
                info=info,
                emitted=True,
                policy_applied=f"attenuate(scale={scale:.4f})",
                suppression_reason="; ".join(reason),
            )

        raise ValueError(f"unknown policy: {self.policy}")


def gated_run(
    X0: np.ndarray,
    Xi_seq: Sequence[np.ndarray],
    Lam_seq: Sequence[np.ndarray],
    G_seq: Sequence[np.ndarray],
    *,
    T: Callable[[np.ndarray], np.ndarray],
    P: Callable[[np.ndarray], np.ndarray] | object,
    gate: EmissionGate,
    epsilon: float = 0.05,
    op_norm_T: float = 1.0,
) -> tuple[np.ndarray, list[np.ndarray], list[GatedOutput]]:
    X = np.array(X0, copy=True)
    history = [np.array(X, copy=True)]
    outputs: list[GatedOutput] = []

    for Xi_t, Lam_t, G_t in zip(Xi_seq, Lam_seq, G_seq, strict=False):
        out = gate(X, Xi_t, Lam_t, T, G_t, P, epsilon=epsilon, op_norm_T=op_norm_T)
        outputs.append(out)
        X = out.X_next
        history.append(np.array(X, copy=True))

    return X, history, outputs
