"""Legacy PIRTM modules — deprecated transition surface.

Removal target: v0.3.0.
Use supported top-level APIs under ``pirtm`` for new integrations.
"""

import warnings as _w

_w.warn(
    "pirtm._legacy modules are deprecated and targeted for removal in v0.3.0. "
    "Use supported top-level APIs (for example: pirtm.recurrence, "
    "pirtm.projection, pirtm.spectral_decomp) instead.",
    DeprecationWarning,
    stacklevel=2,
)

from .pir_tensor import PrimeTensorSystem
from .recursive_ops import recursive_update, contraction_check, is_stable, feedback_operator
from .spectral_decomp import (
    spectral_decomposition,
    spectral_entropy,
    phase_coherence,
    plot_spectrum,
    analyze_tensor,
)
