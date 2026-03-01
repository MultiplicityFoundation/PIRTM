import numpy as np
import pytest

import pirtm.ace.contracts as _ace_contracts
from pirtm.types import Status, StepInfo


def pytest_configure(config):
    _ace_contracts.enable_debug()


@pytest.fixture
def rng():
    return np.random.default_rng(42)


@pytest.fixture
def dim():
    return 4


@pytest.fixture
def identity(dim):
    return np.eye(dim)


@pytest.fixture
def zero_matrix(dim):
    return np.zeros((dim, dim))


@pytest.fixture
def small_matrix(rng, dim):
    matrix = rng.standard_normal((dim, dim))
    return matrix * 0.3 / np.linalg.norm(matrix, 2)


@pytest.fixture
def identity_operator():
    return lambda x: x


@pytest.fixture
def scaling_operator():
    return lambda x: 0.5 * x


@pytest.fixture
def identity_projector():
    return lambda x: x


@pytest.fixture
def safe_step_info():
    return StepInfo(
        step=0,
        q=0.7,
        epsilon=0.05,
        nXi=0.4,
        nLam=0.3,
        projected=False,
        residual=0.001,
    )


@pytest.fixture
def unsafe_step_info():
    return StepInfo(
        step=0,
        q=0.98,
        epsilon=0.05,
        nXi=0.6,
        nLam=0.38,
        projected=True,
        residual=0.5,
    )


@pytest.fixture
def converged_status():
    return Status(converged=True, safe=True, steps=50, residual=1e-8, epsilon=0.05)


@pytest.fixture
def small_primes():
    return [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
