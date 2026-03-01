from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from .types import StepInfo


@dataclass(frozen=True)
class SilenceEvent:
    step: int
    reason: str
    operator_failed: list[str]
    detail: dict


@dataclass(frozen=True)
class CSLVerdict:
    neutrality: bool
    beneficence: bool
    silence_triggered: bool
    commutes: bool
    violations: list[str]
    detail: dict


def neutrality_check(
    T: Callable[[np.ndarray], np.ndarray],
    subjects: Sequence[np.ndarray],
    epsilon_n: float = 1e-6,
) -> tuple[bool, dict]:
    if len(subjects) < 2:
        return True, {"pairs_checked": 0, "max_deviation": 0.0, "violations": []}

    outputs = [np.asarray(T(subject), dtype=float) for subject in subjects]
    max_dev = 0.0
    violations: list[tuple[int, int, float]] = []

    for index in range(len(outputs)):
        for jndex in range(index + 1, len(outputs)):
            deviation = float(np.linalg.norm(outputs[index] - outputs[jndex]))
            max_dev = max(max_dev, deviation)
            if deviation >= epsilon_n:
                violations.append((index, jndex, deviation))

    return len(violations) == 0, {
        "pairs_checked": len(outputs) * (len(outputs) - 1) // 2,
        "max_deviation": max_dev,
        "violations": violations,
    }


def beneficence_check(
    X_t: np.ndarray,
    X_next: np.ndarray,
    info: StepInfo,
    *,
    norm_growth_limit: float = 1.0,
    residual_limit: float = 10.0,
    custom_checks: Sequence[Callable[[np.ndarray, np.ndarray, StepInfo], bool]] | None = None,
) -> tuple[bool, dict]:
    violations: list[str] = []
    norm_t = float(np.linalg.norm(X_t))
    norm_next = float(np.linalg.norm(X_next))
    growth = (norm_next / norm_t) if norm_t > 0.0 else norm_next

    if growth > norm_growth_limit:
        violations.append(f"norm_growth={growth:.4f}>{norm_growth_limit}")
    if info.residual > residual_limit:
        violations.append(f"residual={info.residual:.4f}>{residual_limit}")

    if custom_checks:
        for index, check in enumerate(custom_checks):
            if not check(X_t, X_next, info):
                violations.append(f"custom_check_{index}_failed")

    return len(violations) == 0, {
        "norm_growth": growth,
        "residual": float(info.residual),
        "violations": violations,
    }


def silence_clause(
    neutrality_ok: bool,
    beneficence_ok: bool,
    step_index: int,
    detail: dict,
) -> tuple[bool, SilenceEvent | None]:
    if neutrality_ok and beneficence_ok:
        return False, None

    failed: list[str] = []
    if not neutrality_ok:
        failed.append("neutrality")
    if not beneficence_ok:
        failed.append("beneficence")

    event = SilenceEvent(
        step=step_index,
        reason=f"CSL operator(s) failed: {', '.join(failed)}",
        operator_failed=failed,
        detail=detail,
    )
    return True, event


def commutation_check(
    T: Callable[[np.ndarray], np.ndarray],
    csl_filter: Callable[[np.ndarray], np.ndarray],
    X: np.ndarray,
    epsilon_c: float = 1e-6,
) -> tuple[bool, dict]:
    path1 = np.asarray(csl_filter(T(X)), dtype=float)
    path2 = np.asarray(T(csl_filter(X)), dtype=float)
    deviation = float(np.linalg.norm(path1 - path2))
    commutes = deviation < epsilon_c
    return commutes, {
        "deviation": deviation,
        "epsilon_c": epsilon_c,
        "commutes": commutes,
    }


def evaluate_csl(
    T: Callable[[np.ndarray], np.ndarray],
    X_t: np.ndarray,
    X_next: np.ndarray,
    info: StepInfo,
    step_index: int,
    *,
    subjects: Sequence[np.ndarray] | None = None,
    csl_filter: Callable[[np.ndarray], np.ndarray] | None = None,
    epsilon_n: float = 1e-6,
    epsilon_c: float = 1e-6,
    norm_growth_limit: float = 1.0,
    residual_limit: float = 10.0,
) -> CSLVerdict:
    if subjects is not None and len(subjects) >= 2:
        neutrality_ok, neutrality_detail = neutrality_check(T, subjects, epsilon_n)
    else:
        neutrality_ok, neutrality_detail = True, {"skipped": True}

    beneficence_ok, beneficence_detail = beneficence_check(
        X_t,
        X_next,
        info,
        norm_growth_limit=norm_growth_limit,
        residual_limit=residual_limit,
    )

    silence_triggered, silence_event = silence_clause(
        neutrality_ok,
        beneficence_ok,
        step_index,
        {"neutrality": neutrality_detail, "beneficence": beneficence_detail},
    )

    if csl_filter is not None:
        commutes, commutation_detail = commutation_check(T, csl_filter, X_t, epsilon_c)
    else:
        commutes, commutation_detail = True, {"skipped": True}

    violations: list[str] = []
    if not neutrality_ok:
        violations.append("neutrality")
    if not beneficence_ok:
        violations.append("beneficence")
    if silence_triggered:
        violations.append("silence_triggered")
    if not commutes:
        violations.append("commutation")

    return CSLVerdict(
        neutrality=neutrality_ok,
        beneficence=beneficence_ok,
        silence_triggered=silence_triggered,
        commutes=commutes,
        violations=violations,
        detail={
            "neutrality": neutrality_detail,
            "beneficence": beneficence_detail,
            "commutation": commutation_detail,
            "silence_event": silence_event,
        },
    )
