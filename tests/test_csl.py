import numpy as np

from pirtm.csl import (
    beneficence_check,
    commutation_check,
    evaluate_csl,
    neutrality_check,
    silence_clause,
)
from pirtm.types import StepInfo


def _info(residual: float = 0.1) -> StepInfo:
    return StepInfo(step=0, q=0.4, epsilon=0.05, nXi=0.2, nLam=0.2, projected=False, residual=residual)


def test_neutrality_check_detects_violation():
    T = lambda x: x
    subjects = [np.array([0.0, 0.0]), np.array([1.0, 0.0])]
    ok, detail = neutrality_check(T, subjects, epsilon_n=0.1)
    assert not ok
    assert detail["pairs_checked"] == 1


def test_beneficence_check_fails_on_growth_or_residual():
    X_t = np.ones(2)
    X_next = 3.0 * np.ones(2)
    ok, detail = beneficence_check(X_t, X_next, _info(residual=11.0), norm_growth_limit=1.1, residual_limit=10.0)
    assert not ok
    assert len(detail["violations"]) >= 2


def test_silence_clause_trigger():
    triggered, event = silence_clause(False, True, 2, {"x": 1})
    assert triggered
    assert event is not None
    assert event.step == 2


def test_commutation_check_false_for_non_commuting_transform():
    T = lambda x: np.array([x[1], 2.0 * x[0]])
    csl_filter = lambda x: np.array([x[0], 0.0])
    ok, detail = commutation_check(T, csl_filter, np.array([1.0, 2.0]), epsilon_c=1e-9)
    assert not ok
    assert detail["deviation"] > 0


def test_evaluate_csl_composes_and_marks_skips():
    T = lambda x: 0.5 * x
    X_t = np.ones(2)
    X_next = 0.5 * np.ones(2)
    verdict = evaluate_csl(T, X_t, X_next, _info(), step_index=0)
    assert verdict.neutrality
    assert verdict.beneficence
    assert verdict.commutes
    assert verdict.detail["neutrality"]["skipped"] is True
    assert verdict.detail["commutation"]["skipped"] is True
