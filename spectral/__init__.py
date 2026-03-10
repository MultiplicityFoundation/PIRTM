"""
Spectral analysis and complex resonance detection for PIRTM.

Modules:
  laplacian.py — Prime-Cayley Laplacian construction (Phase 1)
  heat_kernel.py — Bessel heat kernel (Phase 1)
  green.py — Green's function (Phase 1)
  resonance.py — Real-axis resonance (Phase 1)
  aaa.py — AAA rational approximation (Phase 3)
  continuation.py — Complex continuation & resonance detection (Phase 3)
  fingerprint.py — Spectral operator identification via 5-point test (Phase 2/4)

Diagnostics:
  Three independent methods for operator classification from CSV:
    1. Two-line estimate (direct eigenvalue formula)
    2. Cheeger impossibility bound (rigorous lower bound)
    3. 5-point spectral shape test (noise-robust classification)

@spec: ADR-015, ADR-017, ADR-019, ADR-020 (operator identity gate)
"""
from __future__ import annotations

from .fingerprint import (
    OperatorType,
    FingerprintVerdict,
    SpectralFingerprint,
    two_line_estimate,
    cheeger_lower_bound,
    cheeger_impossibility_test,
    infer_beta_from_gamma,
    classify_gap_scaling,
    shape_test_5point,
    shape_test_5point_with_M,
)

__all__ = [
    "OperatorType",
    "FingerprintVerdict",
    "SpectralFingerprint",
    "two_line_estimate",
    "cheeger_lower_bound",
    "cheeger_impossibility_test",
    "infer_beta_from_gamma",
    "classify_gap_scaling",
    "shape_test_5point",
    "shape_test_5point_with_M",
]
