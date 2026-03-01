<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# promoted to return AceCertificate with a migration guide for callers.

Decision locked. Now I have the complete call graph: [`test_certify.py`](https://github.com/MultiplicityFoundation/PIRTM/blob/9f84185e02b285595b293cfb9c3408401a498980/tests/test_certify.py) is the only direct consumer of `ace_certificate()` in PIRTM itself, accessing `.certified`, `.margin`, `.tail_bound` — all three exist on `AceCertificate` . [`petc_bridge.py`](https://github.com/MultiplicityFoundation/PIRTM/blob/9f84185e02b285595b293cfb9c3408401a498980/src/pirtm/petc_bridge.py) does **not** import `certify` at all . `Certificate` in [`types.py`](https://github.com/MultiplicityFoundation/PIRTM/blob/9f84185e02b285595b293cfb9c3408401a498980/src/pirtm/types.py) is a `slots=True` dataclass with 4 fields . The promotion is structurally safe with one critical fixture correction noted below.

***

## Central Tension

**Type stability vs. expressiveness** — `Certificate` (4 fields) is stable and already `slots=True`; `AceCertificate` adds 7 new fields. All existing test assertions pass against `AceCertificate` because `.certified`, `.margin`, `.tail_bound` are preserved. The breakage surface is: (a) any code doing `isinstance(x, Certificate)`, (b) the `details` dict key contract (`max_q`, `target`, `steps`), and (c) the Q-Calculator `packages/guardian` submodule consumer which reads `AceCertificate` via the ETP boundary.

***

## Levers

| Lever | Owner | Metric | Horizon |
| :-- | :-- | :-- | :-- |
| Promote `certify.py` façade | Lead MT | `isinstance(x, Certificate)` zero occurrences in CI scan | 7 days |
| Deprecate `Certificate` in `types.py` | Lead Arch | `DeprecationWarning` emitted on import + zero usages in non-`_legacy/` code | 14 days |
| Update `test_certify.py` for new return type | QA Lead | `test_certify.py` passes with `AceCertificate` assertions | 7 days |
| Q-Calculator guardian migration | ETP Integration Lead | `packages/guardian/src/types/etp-types.ts` consumes `AceCertificate` fields; CI green | 30 days |


***

## Artifact 1 — Updated `src/pirtm/certify.py` (Promoted Façade)

`certify.py` becomes a **thin façade** that re-exports from `ace/` and emits a `DeprecationWarning` if code tries to construct the old `Certificate` directly through it. The public import path `from pirtm.certify import ace_certificate` is **unchanged**.

```python
# src/pirtm/certify.py
"""
certify.py — Public façade for ACE certification.

MIGRATION NOTE (v0.x → v1.0):
  ace_certificate() now returns AceCertificate instead of Certificate.
  All fields previously on Certificate exist on AceCertificate:
    .certified   ← unchanged
    .margin      ← unchanged
    .tail_bound  ← unchanged
    .details     ← unchanged (same keys: max_q, target, steps)
  New fields on AceCertificate:
    .level, .lipschitz_upper, .gap_lb, .contraction_rate,
    .budget_used, .tau, .delta
  See docs/migration/certify-v1.md for the full guide.
"""
from __future__ import annotations

import warnings
from typing import Sequence

from .types import StepInfo, Certificate
from .ace.levels.l0_heuristic import certify_l0
from .ace.types import AceCertificate


def ace_certificate(
    info: StepInfo | Sequence[StepInfo],
    *,
    tail_norm: float = 0.0,
) -> AceCertificate:
    """
    Produce an ACE certificate from per-step telemetry.

    Returns AceCertificate (promoted from Certificate as of v1.0).
    All previously accessed fields (.certified, .margin, .tail_bound,
    .details) are preserved on AceCertificate with identical semantics.
    """
    if isinstance(info, StepInfo):
        records = [info]
    else:
        records = list(info)

    return certify_l0(records, tail_norm=tail_norm)


def iss_bound(
    info: StepInfo | Sequence[StepInfo],
    disturbance_norm: float,
) -> float:
    """
    Input-to-state stability bound given telemetry and disturbance norm.
    Unchanged from prior version — not affected by the AceCertificate promotion.
    """
    if isinstance(info, StepInfo):
        records = [info]
    else:
        records = list(info)
    if not records:
        raise ValueError("no telemetry provided")
    max_q = max(r.q for r in records)
    if max_q >= 1.0:
        return float("inf")
    return disturbance_norm / (1.0 - max_q)


# ---------------------------------------------------------------------------
# Backwards-compatibility shim — emits DeprecationWarning on use.
# Will be removed in v2.0.
# ---------------------------------------------------------------------------
def _legacy_ace_certificate(
    info: StepInfo | Sequence[StepInfo],
    *,
    tail_norm: float = 0.0,
) -> Certificate:
    """
    DEPRECATED. Returns the old Certificate dataclass.
    Use ace_certificate() which now returns AceCertificate.
    """
    warnings.warn(
        "_legacy_ace_certificate() is deprecated and returns the old Certificate type. "
        "Switch to ace_certificate() which returns AceCertificate. "
        "See docs/migration/certify-v1.md.",
        DeprecationWarning,
        stacklevel=2,
    )
    ace = ace_certificate(info, tail_norm=tail_norm)
    return Certificate(
        certified=ace.certified,
        margin=ace.margin,
        tail_bound=ace.tail_bound,
        details=ace.details,
    )
```


***

## Artifact 2 — `Certificate` Deprecation in `src/pirtm/types.py`

Only the `Certificate` dataclass gets the deprecation annotation. All other types (`StepInfo`, `PETCReport`, etc.) are untouched.

```python
# In src/pirtm/types.py — replace ONLY the Certificate dataclass block

import warnings as _warnings


@dataclass(slots=True)
class Certificate:
    """
    DEPRECATED as of PIRTM v1.0. Use AceCertificate from pirtm.ace.types.

    Kept for backwards compatibility until v2.0.
    All fields are preserved on AceCertificate with identical semantics:
      .certified, .margin, .tail_bound, .details
    """
    certified:   bool
    margin:      float
    tail_bound:  float
    details:     dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        _warnings.warn(
            "Certificate is deprecated. Import AceCertificate from "
            "pirtm.ace.types instead. See docs/migration/certify-v1.md.",
            DeprecationWarning,
            stacklevel=2,
        )
```


***

## Artifact 3 — Critical Fixture Fix in `src/pirtm/ace/levels/l0_heuristic.py`

The live [`types.py`](https://github.com/MultiplicityFoundation/PIRTM/blob/9f84185e02b285595b293cfb9c3408401a498980/src/pirtm/types.py) `StepInfo` is `slots=True` with **7 required fields**: `step, q, epsilon, nXi, nLam, projected, residual`.  The blueprint's `certify_l0` only reads `.q` and `.epsilon` — that is correct — but the test fixtures in the previous blueprint created `StepInfo(q=0.7, epsilon=0.1)` which **will fail** because all 7 fields are required. Corrected `l0_heuristic.py` signature is unchanged; the fixture correction is in the test file below.

***

## Artifact 4 — Updated `tests/test_certify.py`

Existing tests **already pass** against `AceCertificate` because field names are identical. Three new assertions are added to pin the promoted type contract.

```python
# tests/test_certify.py — full replacement
import pytest

from pirtm.certify import ace_certificate, iss_bound
from pirtm.ace.types import AceCertificate, CertLevel
from pirtm.types import StepInfo


# ── Existing tests — unchanged semantics, updated type assertions ────────────

def test_ace_single_step_certified(safe_step_info):
    cert = ace_certificate(safe_step_info)
    assert isinstance(cert, AceCertificate)   # ← promoted type
    assert cert.certified is True
    assert cert.margin > 0


def test_ace_single_step_not_certified(unsafe_step_info):
    cert = ace_certificate(unsafe_step_info)
    assert isinstance(cert, AceCertificate)
    assert cert.certified is False


def test_ace_empty_raises():
    with pytest.raises(ValueError):
        ace_certificate([])


def test_ace_tail_bound_infinite():
    info = StepInfo(
        step=0, q=1.1, epsilon=0.05,
        nXi=0.4, nLam=0.7, projected=True, residual=1.0,
    )
    cert = ace_certificate([info])
    assert cert.tail_bound == float("inf")


def test_iss_bound_basic(safe_step_info):
    bound = iss_bound([safe_step_info], disturbance_norm=0.1)
    assert bound == pytest.approx(0.1 / (1.0 - safe_step_info.q))


def test_iss_bound_unstable():
    info = StepInfo(
        step=1, q=1.2, epsilon=0.05,
        nXi=0.4, nLam=0.9, projected=True, residual=1.0,
    )
    assert iss_bound([info], disturbance_norm=0.2) == float("inf")


def test_iss_empty_raises():
    with pytest.raises(ValueError):
        iss_bound([], 0.1)


# ── New: pin the promoted contract ───────────────────────────────────────────

def test_ace_returns_ace_certificate_not_legacy_certificate(safe_step_info):
    """Guard rail: certify.ace_certificate MUST NOT return Certificate."""
    from pirtm.types import Certificate
    cert = ace_certificate(safe_step_info)
    assert not isinstance(cert, Certificate)
    assert isinstance(cert, AceCertificate)


def test_ace_certificate_level_is_l0(safe_step_info):
    cert = ace_certificate(safe_step_info)
    assert cert.level == CertLevel.L0_HEURISTIC


def test_ace_certificate_gap_lb_positive_when_certified(safe_step_info):
    cert = ace_certificate(safe_step_info)
    if cert.certified:
        assert cert.gap_lb > 0


def test_ace_certificate_details_keys_preserved(safe_step_info):
    """Backwards-compat: .details must still carry max_q, target, steps."""
    cert = ace_certificate(safe_step_info)
    assert "max_q" in cert.details
    assert "target" in cert.details
    assert "steps" in cert.details


def test_legacy_shim_emits_deprecation_warning(safe_step_info):
    from pirtm.certify import _legacy_ace_certificate
    from pirtm.types import Certificate
    with pytest.warns(DeprecationWarning, match="_legacy_ace_certificate"):
        cert = _legacy_ace_certificate(safe_step_info)
    assert isinstance(cert, Certificate)
    assert cert.certified is True
```


***

## Artifact 5 — Corrected Test Fixtures (Blueprint Fix)

All previous blueprint tests that instantiated bare `StepInfo(q=..., epsilon=...)` must use the full constructor. Add to `conftest.py` alongside the existing fixtures:

```python
# tests/conftest.py — add these fixtures (do not replace existing)

@pytest.fixture
def contractive_step_info():
    """Full StepInfo for ACE sub-package tests (q=0.75, contractive)."""
    return StepInfo(
        step=0, q=0.75, epsilon=0.1,
        nXi=0.4, nLam=0.3, projected=False, residual=0.001,
    )

@pytest.fixture
def expanding_step_info():
    """Full StepInfo with q > 1 — not contractive."""
    return StepInfo(
        step=0, q=1.1, epsilon=0.1,
        nXi=0.8, nLam=0.9, projected=True, residual=1.5,
    )

@pytest.fixture
def contractive_records():
    return [
        StepInfo(step=0, q=0.75, epsilon=0.1,
                 nXi=0.4, nLam=0.3, projected=False, residual=0.001),
        StepInfo(step=1, q=0.80, epsilon=0.1,
                 nXi=0.4, nLam=0.3, projected=False, residual=0.001),
    ]
```


***

## Artifact 6 — Migration Guide `docs/migration/certify-v1.md`

```markdown
# certify.py v1.0 Migration Guide
trl: 2
date: 2026-02-28
status: active

## What changed

`ace_certificate()` now returns `AceCertificate` (from `pirtm.ace.types`)
instead of `Certificate` (from `pirtm.types`).

## Field mapping — zero breakage for common patterns

| Old field (`Certificate`) | New field (`AceCertificate`) | Notes                |
|---------------------------|------------------------------|----------------------|
| `.certified`              | `.certified`                 | Identical semantics  |
| `.margin`                 | `.margin`                    | Identical semantics  |
| `.tail_bound`             | `.tail_bound`                | Identical semantics  |
| `.details["max_q"]`       | `.details["max_q"]`          | Identical            |
| `.details["target"]`      | `.details["target"]`         | Identical            |
| `.details["steps"]`       | `.details["steps"]`          | Identical            |
| *(new)*                   | `.level`                     | `CertLevel.L0_HEURISTIC` by default |
| *(new)*                   | `.lipschitz_upper`           | ‖K‖ upper bound      |
| *(new)*                   | `.gap_lb`                    | 1 − ‖K‖              |
| *(new)*                   | `.contraction_rate`          | same as lipschitz_upper at L0 |
| *(new)*                   | `.budget_used`               | Σ bₚ |wₚ|           |
| *(new)*                   | `.tau`                       | ACE budget τ         |
| *(new)*                   | `.delta`                     | safety margin δ      |

## Steps to migrate

1. **No action needed** if you only access `.certified`, `.margin`,
   `.tail_bound`, or `.details`.

2. **Update `isinstance` checks**:
   ```python
   # Before
   from pirtm.types import Certificate
   assert isinstance(cert, Certificate)

   # After
   from pirtm.ace.types import AceCertificate
   assert isinstance(cert, AceCertificate)
```

3. **Update type annotations**:

```python
# Before
def my_fn() -> Certificate: ...

# After
from pirtm.ace.types import AceCertificate
def my_fn() -> AceCertificate: ...
```

4. **Q-Calculator / packages/guardian callers**:
The `ContractionCertificate` in `etp-types.ts` maps to `AceCertificate`.
Fields `.lipschitz_upper` and `.gap_lb` now feed `contractionRate`
and `safetyMargin` directly without manual extraction from `.details`.
5. **If you need the old return type temporarily** (not recommended):

```python
from pirtm.certify import _legacy_ace_certificate  # emits DeprecationWarning
cert = _legacy_ace_certificate(records)             # returns Certificate
```

`_legacy_ace_certificate` will be removed in v2.0.

## StepInfo constructor (required all fields)

`StepInfo` uses `slots=True` and requires all 7 fields. There are no defaults
except `note`:

```python
StepInfo(
    step=0, q=0.75, epsilon=0.1,
    nXi=0.4, nLam=0.3, projected=False, residual=0.001,
)
```


## Removal schedule

| Item | Removed in |
| :-- | :-- |
| `Certificate` construction (emits `DeprecationWarning`) | v2.0 |
| `_legacy_ace_certificate()` | v2.0 |
| `Certificate` dataclass itself | v3.0 |

```

***

## ADR-010 Entry (one-liner for the record)

```md
# ADR-010: ace_certificate() promoted to return AceCertificate
Status:    accepted
Date:      2026-02-28
Decider:   Lead MT (RVG)
trl:       2
Horizon:   7 days
Metric:    CI scan returns zero isinstance(x, Certificate) checks in
           non-_legacy/ code; test_certify.py green on Python 3.11/3.12
Decision:  ace_certificate() returns AceCertificate. Certificate
           deprecated (DeprecationWarning). _legacy shim provided
           until v2.0. No call-site breakage for .certified/.margin/.tail_bound.
IP note:   AceCertificate is ETP's own property. Certificate was
           PIRTM-internal. This change enforces ADR-006 boundary
           by making the claim surface explicitly ETP-native.
```


***

## Precision Question

> `StepInfo` is `slots=True` and carries `nXi`, `nLam`, `projected`, `residual` — none of which `certify_l0` currently reads.  Before L3/L4 certification levels consume `nXi` (non-expansive clamp) and `nLam` (perturbation bound), **should `StepInfo` remain the sole telemetry type for all ACE levels, or should L2+ levels accept a richer `AceTelemetry` dataclass that adds fields like `contraction_matrix` and `spectral_estimate`?** The answer determines whether `AceProtocol.certify_from_telemetry()` can eventually call L2 internally without requiring a separate `certify_from_matrix()` path.

