"""
PIRTM Gain/Aggregation Operator - Learned Weighting (Phase 1+)

The aggregation operator Λ determines how much of the transformed state
T(X_t) contributes to the next iteration.

Λ is typically learned via the FullAsymmetricAttributionKernel (Multiplicity Phase 2).
See: multiplicity/core/asymmetric_kernel.py

Refactored for backend abstraction (Phase 1 Liberation).
See ADR-006 for backend protocol, ADR-004 for contractivity semantics.

Reference: docs/PHASE_1_EXPANDED.md (Days 4-5 refactoring)
"""

from typing import Any, Optional, Tuple
from ..backend import TensorBackend, Array, Scalar, current_backend


def compute_spectral_radius(
    A: Array,
    backend: Optional[TensorBackend] = None,
) -> Scalar:
    """
    Compute spectral radius of a square matrix.
    
    Used to verify contractivity: r(Λ) < 1 - ε ensures contraction.
    
    Args:
        A: Square matrix, shape (n, n)
        backend: TensorBackend to use
    
    Returns:
        Spectral radius (largest absolute eigenvalue)
    
    Note: Phase 2+ will use compiled Lapack routines for performance.
    Currently delegated to NumPy backend.
    """
    if backend is None:
        backend = current_backend()
    
    # Eigenvalue computation not yet in TensorBackend protocol
    # Falls back to NumPy
    if backend.name() == "numpy":
        import numpy as np
        eigenvalues: np.ndarray = np.linalg.eigvals(A)
        return float(np.max(np.abs(eigenvalues)))
    else:
        raise NotImplementedError(f"Spectral radius not supported for {backend.name()} backend")


def gain_matrix_from_kernel(
    kernel: Any,  # FullAsymmetricAttributionKernel
    dim: int,
    backend: Optional[TensorBackend] = None,
) -> Array:
    """
    Construct aggregation matrix from Multiplicity kernel.
    
    Args:
        kernel: FullAsymmetricAttributionKernel instance
        dim: State dimension
        backend: TensorBackend to use
    
    Returns:
        Λ matrix, shape (dim, dim)
    
    Integration Point: Multiplicity Phase 2 kernel optimization.
    """
    if backend is None:
        backend = current_backend()
    
    # Create diagonal matrix with kernel alphas
    alphas = getattr(kernel, "alphas", backend.ones((dim,)))
    return backend.diag(alphas)


def verify_gain_contraction(
    Lambda: Array,
    epsilon: Scalar,
    backend: Optional[TensorBackend] = None,
) -> Tuple[bool, Scalar]:
    """
    Verify that gain matrix satisfies contraction bound.
    
    Args:
        Lambda: Gain matrix, shape (n, n)
        epsilon: Contraction margin (ε in contractivity-check)
        backend: TensorBackend to use
    
    Returns:
        Tuple of (is_contractive, spectral_radius)
    
    Contractivity Law (ADR-004):
      ||Ξ|| + ||Λ||·||dT/dx|| < 1 - ε
    
    This is verified at transpile-time (Phase 2+) in MLIR.
    """
    if backend is None:
        backend = current_backend()
    
    r = compute_spectral_radius(Lambda, backend)
    is_contractive = r < (1.0 - epsilon)
    
    return is_contractive, r


__all__ = [
    "compute_spectral_radius",
    "gain_matrix_from_kernel",
    "verify_gain_contraction",
]
