"""
PIRTM Projection Operator - State Space Clipping (Phase 1+)

Projection onto the unit ball: P(x) = clip(x, -1, 1)

This ensures all states remain bounded, which is essential for:
1. Contractivity preservation (L0 invariant)
2. Numerical stability (prevents overflow)
3. Physical meaningfulness (PIRTM states are normalized)

Refactored for backend abstraction (Phase 1 Liberation).
See ADR-006 for backend protocol, ADR-004 for contractivity semantics.

Reference: docs/PHASE_1_EXPANDED.md (Days 3-4 refactoring)
"""

from typing import Optional
from ..backend import TensorBackend, Array, Scalar, current_backend


def project(
    x: Array,
    min_val: Scalar = -1.0,
    max_val: Scalar = 1.0,
    backend: Optional[TensorBackend] = None,
) -> Array:
    """
    Project array onto bounded interval [min_val, max_val].
    
    Args:
        x: Input array (any shape)
        min_val: Lower bound (default -1.0)
        max_val: Upper bound (default 1.0)
        backend: TensorBackend to use (defaults to current)
    
    Returns:
        Clipped array with values in [min_val, max_val]
    
    Contractivity: The projection operator is nonexpansive:
      ||P(x) - P(y)|| ≤ ||x - y||
    
    This preserves contractivity of the overall recurrence.
    """
    if backend is None:
        backend = current_backend()
    
    return backend.clip(x, min_val, max_val)


def project_ball(
    x: Array,
    radius: Scalar = 1.0,
    backend: Optional[TensorBackend] = None,
) -> Array:
    """
    Project array onto L2 ball of given radius.
    
    Useful for constraining state norm: ||x'|| ≤ radius
    
    Args:
        x: Input array
        radius: Ball radius (default 1.0)
        backend: TensorBackend to use
    
    Returns:
        Projected array with norm ≤ radius
    """
    if backend is None:
        backend = current_backend()
    
    norm_x = backend.norm(x, order=2)
    
    if norm_x <= radius:
        return x
    
    # Scale down to fit in ball
    scale = radius / (norm_x + 1e-10)
    return backend.multiply(x, scale)


def bounded_state_check(
    x: Array,
    min_val: Scalar = -1.0,
    max_val: Scalar = 1.0,
    backend: Optional[TensorBackend] = None,
) -> bool:
    """
    Check if array is fully within bounds.
    
    Used in verification and testing to detect L0 invariant violations.
    
    Args:
        x: Input array
        min_val: Lower bound
        max_val: Upper bound
        backend: TensorBackend to use
    
    Returns:
        True if all entries in [min_val, max_val]
    """
    if backend is None:
        backend = current_backend()
    
    projected = backend.clip(x, min_val, max_val)
    diff_norm = backend.norm(backend.add(x, backend.multiply(projected, -1.0)))
    
    return diff_norm < 1e-10


__all__ = ["project", "project_ball", "bounded_state_check"]
