# Certificate API (`pirtm.certify`)

This page documents the certificate-focused APIs used for contraction safety checks
and stability bounds.

## Overview

PIRTM exposes two certificate surfaces:

- `contraction_certificate(...)` returns the stable `Certificate` type for
  straightforward runtime checks.
- `ace_certificate(...)` returns the richer `AceCertificate` type for advanced
  diagnostics and protocol-level analysis.

## `contraction_certificate(info, *, tail_norm=0.0) -> Certificate`

Primary API for ML0-003 contraction validation.

### Parameters

- `info`: a single `StepInfo` or a sequence of `StepInfo` records
- `tail_norm`: optional disturbance norm for tail-bound computation

### Returns

A `Certificate` with fields:

- `certified: bool`
- `margin: float`
- `tail_bound: float`
- `details: dict[str, Any]`

### Example

```python
import numpy as np
from pirtm import contraction_certificate, step

x = np.ones(4)
xi = 0.3 * np.eye(4)
lam = 0.2 * np.eye(4)


def t_fn(v: np.ndarray) -> np.ndarray:
    return 0.8 * v


def p_fn(v: np.ndarray) -> np.ndarray:
    return v

x_next, info = step(x, xi, lam, t_fn, np.zeros(4), p_fn, epsilon=0.05, op_norm_T=0.8)
cert = contraction_certificate(info)
print(cert.certified, cert.margin)
```

## `ace_certificate(info, *, tail_norm=0.0) -> AceCertificate`

Advanced ACE-native certificate path.

### Parameters

- `info`: a single `StepInfo` or a sequence of `StepInfo` records
- `tail_norm`: optional disturbance norm for tail-bound computation

### Returns

`AceCertificate` with protocol fields including:

- `level`, `certified`, `margin`, `tail_bound`
- `lipschitz_upper`, `gap_lb`, `contraction_rate`, `budget_used`
- `details` (`max_q`, `target`, step-level metadata)

## `iss_bound(info, disturbance_norm) -> float`

Computes the input-to-state stability bound from telemetry.

- Returns `disturbance_norm / (1 - max_q)` when `max_q < 1`
- Returns `inf` when `max_q >= 1`

## Deprecated aliases

### `legacy_ace_certificate(...)`

Deprecated compatibility alias that returns `Certificate`.
Use `contraction_certificate(...)` instead.

### `ace_certificate_v2(...)`

Deprecated ACE alias.
Use `ace_certificate(...)` instead.

## Related docs

- Language spec certificate section: `docs/PIRTM_LANGUAGE_SPEC.md` (§5)
- Migration notes: `docs/migration/v0.1.1.md`
- API index: `docs/api/README.md`
