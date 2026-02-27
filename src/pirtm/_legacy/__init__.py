"""Legacy PIRTM modules — deprecated, will be removed in v0.2.0."""

import warnings as _w

_w.warn(
    "pirtm._legacy modules are deprecated and will be removed in v0.2.0. "
    "Use the contractive core (pirtm.recurrence, pirtm.projection, etc.) instead.",
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
