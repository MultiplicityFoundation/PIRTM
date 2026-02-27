import numpy as np
import pytest

from pirtm.fixed_point import fixed_point_estimate


def test_empty_history_raises():
    with pytest.raises(ValueError):
        fixed_point_estimate([])


def test_constant_history_tail_bound_zero(dim):
    history = [np.ones(dim) for _ in range(5)]
    estimate, tail = fixed_point_estimate(history, window=3)
    assert np.allclose(estimate, np.ones(dim))
    assert tail == 0.0


def test_window_clamps_to_history_length(dim):
    history = [np.full(dim, float(i)) for i in range(3)]
    estimate, _ = fixed_point_estimate(history, window=10)
    assert estimate.shape == (dim,)


def test_nonzero_tail_bound(dim):
    history = [np.full(dim, 1.0), np.full(dim, 2.0), np.full(dim, 3.0)]
    _, tail = fixed_point_estimate(history, window=3)
    assert tail > 0.0
