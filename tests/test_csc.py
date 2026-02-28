import pytest

from pirtm.csc import compute_margin, multi_step_margin, sensitivity, solve_budget
from pirtm.types import StepInfo


def test_solve_budget_identity():
    budget = solve_budget(op_norm_T=2.0, epsilon=0.05, alpha=0.6)
    assert budget.Xi_norm_max + budget.Lam_norm_max * 2.0 == pytest.approx(0.95)


def test_compute_margin_values():
    margin = compute_margin(Xi_norm=0.3, Lam_norm=0.2, op_norm_T=2.0, epsilon=0.05)
    assert margin.margin == pytest.approx(0.25)
    assert margin.safe is True


def test_compute_margin_unsafe():
    margin = compute_margin(Xi_norm=0.9, Lam_norm=0.2, op_norm_T=2.0, epsilon=0.05)
    assert margin.safe is False


def test_multi_step_margin_finds_worst():
    infos = [
        StepInfo(0, 0.6, 0.05, 0.2, 0.2, False, 0.1),
        StepInfo(1, 0.9, 0.05, 0.3, 0.3, True, 0.2),
        StepInfo(2, 0.7, 0.05, 0.2, 0.2, False, 0.1),
    ]
    worst = multi_step_margin(infos)
    assert worst.margin == pytest.approx(0.05)


def test_sensitivity_outputs():
    out = sensitivity(Xi_norm=0.3, Lam_norm=0.2, epsilon=0.05)
    assert out["T_max"] == pytest.approx(3.25)
    out_zero = sensitivity(Xi_norm=0.0, Lam_norm=0.0, epsilon=0.05)
    assert out_zero["T_max"] == float("inf")
