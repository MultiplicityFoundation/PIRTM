"""Legacy PIRTM modules — deprecated transition surface.

Removal target: v0.3.0.
Use supported top-level APIs under ``pirtm`` for new integrations.
"""

import warnings as _w

from .pir_tensor import PrimeTensorSystem
from .recursive_ops import contraction_check, feedback_operator, is_stable, recursive_update
from .spectral_decomp import (
    analyze_tensor,
    phase_coherence,
    plot_spectrum,
    spectral_decomposition,
    spectral_entropy,
)

__all__ = [
    "PrimeTensorSystem",
    "contraction_check",
    "feedback_operator",
    "is_stable",
    "recursive_update",
    "analyze_tensor",
    "phase_coherence",
    "plot_spectrum",
    "spectral_decomposition",
    "spectral_entropy",
]

_w.warn(
    "pirtm._legacy modules are deprecated and targeted for removal in v0.3.0. "
    "Use supported top-level APIs (for example: pirtm.recurrence, "
    "pirtm.projection, pirtm.spectral_decomp) instead.",
    DeprecationWarning,
    stacklevel=2,
)
