"""
PIRTM — Prime-Indexed Recurrence Tensor Mathematics.

Phase 1 (Spec Canon): Mathematical specification and governance.
Phase 2: Spectral governance and integration with recurrence runtime.
Phase 3: Complex resonance detection via analytic continuation (AAA + Track A/B).
Phase 4: MLIR emission and compile-time verification.

Phase 1 Liberation (2026-03, ongoing):
  - Backend abstraction protocol (ADR-006) ✅ COMPLETE
  - NumPy backend reference implementation ✅ COMPLETE
  - Core runtime modules (recurrence, projection, gain, certify) ✅ COMPLETE
  - Multi-backend support (MLIR, LLVM, GPU to come)

Phase 2 Liberation (2026-03, in progress):
  - MLIR transpiler (ADR-007) — Emit verified recurrence to linalg dialect
  - Contractivity bounds as first-class IR attributes
  - Witness hash encoding (ACE integration)
  - CLI: pirtm transpile --output mlir
  - Round-trip validation: descriptor → MLIR → mlir-opt

@spec: docs/math_spec.md, ADR-004, ADR-006, ADR-007, PIRTM_LIBERATION_ROADMAP.md
@team: PIRTM Core Team
"""
from __future__ import annotations

__version__ = "0.4.1-phase2-mlir"

# Phase 1: Backend abstraction
from . import backend
from . import core

# Phase 2: MLIR transpiler integration
from . import transpiler

# Top-level convenience exports so `from pirtm import step` works
from .core.recurrence import step, iterate
from .core.certify import certify_state, verify_trajectory, ContractivityCertificate
from .core.projection import project, project_ball
from .core.gain import compute_spectral_radius, verify_gain_contraction

__all__ = [
    "backend",
    "core",
    "transpiler",
    # Recurrence
    "step",
    "iterate",
    # Certification
    "certify_state",
    "verify_trajectory",
    "ContractivityCertificate",
    # Projection
    "project",
    "project_ball",
    # Gain / spectral
    "compute_spectral_radius",
    "verify_gain_contraction",
]


