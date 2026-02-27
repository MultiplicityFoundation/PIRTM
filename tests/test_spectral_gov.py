import numpy as np

from pirtm.spectral_gov import SpectralGovernor


def test_spectral_governor_analyze_and_clamp():
    gov = SpectralGovernor(dim=3, min_epsilon=0.01, max_epsilon=0.2, safety_margin=0.1)
    T = lambda x: 0.7 * x

    report = gov.analyze(T)
    assert report.spectral_radius < 1.0
    assert report.contraction_feasible is True
    assert 0.01 <= report.recommended_epsilon <= 0.2
    assert report.op_norm_estimate > 0.0


def test_spectral_governor_non_contractive_sets_max_epsilon():
    gov = SpectralGovernor(dim=2, max_epsilon=0.25)
    T = lambda x: 1.2 * x
    epsilon, op_norm, report = gov.govern(T)
    assert report.contraction_feasible is False
    assert epsilon == 0.25
    assert op_norm >= report.spectral_radius


def test_spectral_governor_trend_summary():
    gov = SpectralGovernor(dim=2)
    gov.analyze(lambda x: 0.8 * x)
    gov.analyze(lambda x: 0.82 * x)
    trend = gov.trend()
    assert trend["reports"] == 2
    assert "radius_trend" in trend
    assert 0.0 <= trend["contraction_rate"] <= 1.0
