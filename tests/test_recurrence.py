import numpy as np
import pytest

from pirtm.recurrence import _operator_norm, run, step


class _Projector:
    def apply(self, x):
        return x


def test_operator_norm_zero_branch():
    assert _operator_norm(np.array([])) == 0.0


@pytest.mark.parametrize("dim", [2, 4, 8])
def test_step_preserves_shape(dim):
    x = np.ones(dim)
    xi = 0.2 * np.eye(dim)
    lam = 0.3 * np.eye(dim)
    g = np.zeros(dim)
    out, info = step(x, xi, lam, lambda v: v, g, lambda v: v, op_norm_T=1.0)
    assert out.shape == x.shape
    assert info.projected is False


def test_step_object_projector(dim):
    x = np.ones(dim)
    xi = 0.2 * np.eye(dim)
    lam = 0.3 * np.eye(dim)
    g = np.zeros(dim)
    out, _ = step(x, xi, lam, lambda v: v, g, _Projector(), op_norm_T=1.0)
    assert np.allclose(out, xi @ x + lam @ x)


def test_step_invalid_projector(dim):
    x = np.ones(dim)
    xi = 0.2 * np.eye(dim)
    lam = 0.3 * np.eye(dim)
    g = np.zeros(dim)
    with pytest.raises(TypeError):
        step(x, xi, lam, lambda v: v, g, 42, op_norm_T=1.0)


def test_step_projection_trigger(dim):
    x = np.ones(dim)
    xi = 0.9 * np.eye(dim)
    lam = 0.9 * np.eye(dim)
    g = np.zeros(dim)
    _, info = step(x, xi, lam, lambda v: v, g, lambda v: v, epsilon=0.05, op_norm_T=1.0)
    assert info.projected is True
    assert info.q <= 0.95 + 1e-12


def test_run_converges_identity(dim):
    x0 = np.ones(dim)
    xi = [0.2 * np.eye(dim)] * 50
    lam = [0.2 * np.eye(dim)] * 50
    g = [np.zeros(dim)] * 50
    _, history, infos, status = run(x0, xi, lam, g, T=lambda v: v, P=lambda v: v, tol=1e-5)
    assert len(history) == len(infos) + 1
    assert status.converged is True
    assert status.safe is True


def test_run_max_steps_truncation(dim):
    x0 = np.ones(dim)
    xi = [0.5 * np.eye(dim)] * 20
    lam = [0.4 * np.eye(dim)] * 20
    g = [np.zeros(dim)] * 20
    _, _, infos, status = run(x0, xi, lam, g, T=lambda v: v, P=lambda v: v, max_steps=3)
    assert len(infos) == 3
    assert status.steps == 3


def test_run_empty_sequences(dim):
    x0 = np.ones(dim)
    _, history, infos, status = run(x0, [], [], [], T=lambda v: v, P=lambda v: v)
    assert len(history) == 1
    assert infos == []
    assert status.steps == 0
    assert np.isinf(status.residual)
