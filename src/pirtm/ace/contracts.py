from __future__ import annotations

import hashlib
import os
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

_DEBUG = os.environ.get("PIRTM_ACE_DEBUG", "0") == "1"


def _matrix_fingerprint(matrix: np.ndarray | None) -> str | None:
    if matrix is None:
        return None
    return hashlib.sha256(matrix.tobytes()).hexdigest()


@contextmanager
def assert_matrix_not_mutated(matrix: np.ndarray | None, level_name: str):
    if not _DEBUG or matrix is None:
        yield
        return

    before = _matrix_fingerprint(matrix)
    yield
    after = _matrix_fingerprint(matrix)

    if before != after:
        raise AssertionError(
            f"NO_MATRIX_MUTATION VIOLATED in {level_name}: contraction_matrix mutated in-place"
        )


def enable_debug() -> None:
    global _DEBUG
    _DEBUG = True


def disable_debug() -> None:
    global _DEBUG
    _DEBUG = False
