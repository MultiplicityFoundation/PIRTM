import numpy as np
import pytest

from pirtm.projection import project_parameters_soft, project_parameters_weighted_l1


def test_soft_no_projection_needed(identity):
    xi, lam = project_parameters_soft(0.1 * identity, 0.1 * identity, 1.0, 1.0)
    assert np.allclose(xi, 0.1 * identity)
    assert np.allclose(lam, 0.1 * identity)


def test_soft_rescales_correctly(identity):
    xi_in = 2.0 * identity
    lam_in = 2.0 * identity
    xi, lam = project_parameters_soft(xi_in, lam_in, 1.0, 0.95)
    budget = np.linalg.norm(xi, 2) + np.linalg.norm(lam, 2)
    assert budget <= 0.95 + 1e-12


def test_wl1_validation_errors():
    with pytest.raises(ValueError):
        project_parameters_weighted_l1(np.array([1.0]), np.array([1.0, 2.0]), 1.0)
    with pytest.raises(ValueError):
        project_parameters_weighted_l1(np.array([1.0]), np.array([-1.0]), 1.0)
    with pytest.raises(ValueError):
        project_parameters_weighted_l1(np.array([1.0]), np.array([1.0]), -1.0)


def test_wl1_already_feasible_returns_copy():
    values = np.array([0.2, -0.1])
    weights = np.array([1.0, 1.0])
    out, tau = project_parameters_weighted_l1(values, weights, 10.0)
    assert np.allclose(out, values)
    assert out is not values
    assert tau == 0.0


def test_wl1_projects_to_budget():
    values = np.array([3.0, -2.0, 1.5])
    weights = np.array([1.0, 2.0, 0.5])
    out, _ = project_parameters_weighted_l1(values, weights, 2.0)
    assert np.sum(weights * np.abs(out)) <= 2.0 + 1e-9


def test_wl1_all_zero_weights(values=np.array([1.0, -2.0])):
    out, tau = project_parameters_weighted_l1(values, np.zeros_like(values), 0.0)
    assert np.allclose(out, values)
    assert tau == 0.0
