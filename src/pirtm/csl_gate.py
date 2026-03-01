from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from .csl import CSLVerdict, evaluate_csl

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from .gate import EmissionGate, GatedOutput
    from .types import StepInfo


@dataclass(frozen=True)
class CSLGatedOutput:
    X_next: np.ndarray
    info: StepInfo
    gate_output: GatedOutput
    csl_verdict: CSLVerdict
    emitted: bool
    silenced: bool
    final_policy: str


class CSLEmissionGate:
    def __init__(
        self,
        contraction_gate: EmissionGate,
        *,
        subjects: Sequence[np.ndarray] | None = None,
        csl_filter: Callable[[np.ndarray], np.ndarray] | None = None,
        epsilon_n: float = 1e-6,
        epsilon_c: float = 1e-6,
        norm_growth_limit: float = 1.0,
        residual_limit: float = 10.0,
    ):
        self.contraction_gate = contraction_gate
        self.subjects = subjects
        self.csl_filter = csl_filter
        self.epsilon_n = epsilon_n
        self.epsilon_c = epsilon_c
        self.norm_growth_limit = norm_growth_limit
        self.residual_limit = residual_limit

    def __call__(
        self,
        X_t: np.ndarray,
        Xi_t: np.ndarray,
        Lam_t: np.ndarray,
        T: Callable[[np.ndarray], np.ndarray],
        G_t: np.ndarray,
        P: Callable[[np.ndarray], np.ndarray] | object,
        step_index: int,
        *,
        epsilon: float = 0.05,
        op_norm_T: float = 1.0,
    ) -> CSLGatedOutput:
        gate_output = self.contraction_gate(
            X_t,
            Xi_t,
            Lam_t,
            T,
            G_t,
            P,
            epsilon=epsilon,
            op_norm_T=op_norm_T,
        )

        if not gate_output.emitted:
            skip_verdict = CSLVerdict(
                neutrality=True,
                beneficence=True,
                silence_triggered=False,
                commutes=True,
                violations=[],
                detail={"skipped": "contraction_gated"},
            )
            return CSLGatedOutput(
                X_next=gate_output.X_next,
                info=gate_output.info,
                gate_output=gate_output,
                csl_verdict=skip_verdict,
                emitted=False,
                silenced=False,
                final_policy="contraction_gated",
            )

        verdict = evaluate_csl(
            T=T,
            X_t=X_t,
            X_next=gate_output.X_next,
            info=gate_output.info,
            step_index=step_index,
            subjects=self.subjects,
            csl_filter=self.csl_filter,
            epsilon_n=self.epsilon_n,
            epsilon_c=self.epsilon_c,
            norm_growth_limit=self.norm_growth_limit,
            residual_limit=self.residual_limit,
        )

        if verdict.silence_triggered:
            return CSLGatedOutput(
                X_next=np.array(X_t, copy=True),
                info=gate_output.info,
                gate_output=gate_output,
                csl_verdict=verdict,
                emitted=False,
                silenced=True,
                final_policy="csl_silenced",
            )

        if not verdict.commutes:
            return CSLGatedOutput(
                X_next=np.array(X_t, copy=True),
                info=gate_output.info,
                gate_output=gate_output,
                csl_verdict=verdict,
                emitted=False,
                silenced=True,
                final_policy="csl_silenced(non_commuting)",
            )

        return CSLGatedOutput(
            X_next=gate_output.X_next,
            info=gate_output.info,
            gate_output=gate_output,
            csl_verdict=verdict,
            emitted=True,
            silenced=False,
            final_policy="emitted",
        )
