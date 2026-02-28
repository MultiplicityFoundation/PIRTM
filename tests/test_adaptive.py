from pirtm.adaptive import AdaptiveMargin
from pirtm.types import StepInfo


def test_baseline_defaults_to_epsilon():
    margin = AdaptiveMargin(epsilon=0.05)
    assert margin.baseline == 0.05


def test_update_increases_on_violation():
    margin = AdaptiveMargin(epsilon=0.05, step_size=0.02)
    info = StepInfo(0, 0.98, 0.05, 0.4, 0.6, True, 0.1)
    updated = margin.update(info)
    assert updated > 0.05


def test_update_decreases_when_safe_and_low_residual():
    margin = AdaptiveMargin(epsilon=0.06, baseline=0.02, residual_target=0.01, step_size=0.01)
    info = StepInfo(0, 0.4, 0.06, 0.2, 0.2, False, 1e-4)
    updated = margin.update(info)
    assert updated < 0.06


def test_update_respects_clamps():
    margin = AdaptiveMargin(epsilon=0.24, max_epsilon=0.25, step_size=0.1)
    info = StepInfo(0, 1.2, 0.24, 0.6, 0.6, True, 1.0)
    assert margin.update(info) == 0.25
