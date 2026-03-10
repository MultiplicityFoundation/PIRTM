"""
PIRTM Core Modules - Backend-Agnostic Runtime Logic (Phase 1+)

Exports the fundamental PIRTM operations:
- recurrence: X_{t+1} = P(Ξ X_t + Λ T(X_t) + G_t)
- projection: P(x) = clip(x, -1, 1)
- gain: Aggregation operator Λ and spectral analysis
- certify: Contractivity certificates and ACE verification

All modules use the backend abstraction (ADR-006) and work with any
TensorBackend implementation (NumPy, MLIR, LLVM, GPU, etc.).

See ADR-006 (Backend Abstraction), ADR-004 (Contractivity Semantics).
"""

from . import recurrence
from . import projection
from . import gain
from . import certify

# Re-export key classes and functions
from .recurrence import step as recurrence_step, iterate as recurrence_iterate
from .projection import project, project_ball, bounded_state_check
from .gain import compute_spectral_radius, gain_matrix_from_kernel, verify_gain_contraction
from .certify import ContractivityCertificate, certify_state, verify_trajectory

__all__ = [
    # Modules
    "recurrence",
    "projection",
    "gain",
    "certify",
    # Key functions
    "recurrence_step",
    "recurrence_iterate",
    "project",
    "project_ball",
    "bounded_state_check",
    "compute_spectral_radius",
    "gain_matrix_from_kernel",
    "verify_gain_contraction",
    "ContractivityCertificate",
    "certify_state",
    "verify_trajectory",
]
