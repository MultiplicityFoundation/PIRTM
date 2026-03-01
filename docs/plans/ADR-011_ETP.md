<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# the level implementations carry the invariant that they never mutate the input matrix

Decision locked. The contract is chosen — now it must be **documented, tested, and enforced at the boundary**, not just assumed. The fast-path shallow copy in `_inject_design_params` is now provably safe, but only if the contract is pinned in three places: the level function docstrings, a sentinel guard for debug/test mode, and the test harness.

***

## Central Tension

**Contract-by-convention vs. contract-by-enforcement** — "level implementations never mutate the input matrix" is correct today, but it is currently invisible to future contributors. A new `certify_l5` author has no signal that mutating `telemetry.contraction_matrix` in-place is a violation. The invariant must be pinned in three layers: (1) documented as a named contract, (2) asserted cheaply in debug mode, (3) tested with a before/after fingerprint in CI.

***

## Levers

| Lever | Owner | Metric | Horizon |
| :-- | :-- | :-- | :-- |
| `NO_MATRIX_MUTATION` contract named and documented | Lead MT | Every `certify_lN` docstring carries `Contract:` block; CI grep gate passes | 7 days |
| `_assert_matrix_not_mutated` debug guard in `l2_poweriter` | Lead Arch | `PIRTM_ACE_DEBUG=1` triggers guard; test suite runs with it enabled | 7 days |
| Fingerprint tests for all matrix-consuming levels | QA Lead | `test_ace_matrix_immutability.py` green on L2, L3, L4 | 7 days |
| `docs/contracts/ace-matrix-immutability.md` filed | Lead MT | Document exists before any L5+ implementation begins | 7 days |


***

## Artifact 1 — `src/pirtm/ace/contracts.py` ← NEW

The contract gets its own module so future level authors can import the guard, not reinvent it.

```python
"""
ACE level implementation contracts.

These are NOT runtime type checks — they are correctness invariants
that must be upheld by every level implementation that accepts a
contraction_matrix from AceTelemetry.

Named contract: NO_MATRIX_MUTATION
  Level functions (certify_l0 through certify_lN) must never mutate
  the numpy array at AceTelemetry.contraction_matrix.
  Rationale: _inject_design_params uses dataclasses.replace() which
  produces a shallow copy. The contraction_matrix is shared between
  the original caller object and the injected copy. A mutation in any
  level function propagates back to the caller's AceTelemetry instance,
  violating the copy-on-normalise guarantee established in ADR-013.

Debug guard: set environment variable PIRTM_ACE_DEBUG=1 to enable
  matrix fingerprint assertions around level calls. This is cheap:
  only the array's tobytes() hash is computed, not a full copy.
  Enabled automatically by the test suite via conftest.py.
"""
from __future__ import annotations

import hashlib
import os
from contextlib import contextmanager
from typing import Optional

import numpy as np

# Set PIRTM_ACE_DEBUG=1 to enable matrix mutation guards
_DEBUG = os.environ.get("PIRTM_ACE_DEBUG", "0") == "1"


def _matrix_fingerprint(K: Optional[np.ndarray]) -> Optional[str]:
    """SHA-256 of the raw bytes of K. Fast — no copy of the array data."""
    if K is None:
        return None
    return hashlib.sha256(K.tobytes()).hexdigest()


@contextmanager
def assert_matrix_not_mutated(
    K: Optional[np.ndarray],
    level_name: str,
):
    """
    Context manager that asserts K is not mutated within the block.
    No-op unless PIRTM_ACE_DEBUG=1.

    Usage in level implementations:
        from pirtm.ace.contracts import assert_matrix_not_mutated
        with assert_matrix_not_mutated(telemetry.contraction_matrix, "L2"):
            ... perform certification ...

    The fingerprint is computed from K.tobytes() — O(n²) in matrix size
    but zero-allocation (no array copy). Acceptable in debug/test mode.
    """
    if not _DEBUG or K is None:
        yield
        return

    before = _matrix_fingerprint(K)
    yield
    after = _matrix_fingerprint(K)

    if before != after:
        raise AssertionError(
            f"NO_MATRIX_MUTATION VIOLATED in {level_name}: "
            f"contraction_matrix was mutated in-place. "
            f"Before fingerprint: {before[:16]}... "
            f"After fingerprint:  {after[:16]}... "
            f"Level implementations must treat the input matrix as read-only. "
            f"See docs/contracts/ace-matrix-immutability.md."
        )


def enable_debug() -> None:
    """Enable matrix mutation guards programmatically (for test setup)."""
    global _DEBUG
    _DEBUG = True


def disable_debug() -> None:
    global _DEBUG
    _DEBUG = False
```


***

## Artifact 2 — Updated Level Implementations (Contract blocks + guard)

### `src/pirtm/ace/levels/l2_poweriter.py`

```python
"""
L2-poweriter: TRL-3.

Contract: NO_MATRIX_MUTATION
  This function treats telemetry.contraction_matrix as read-only.
  Power iteration computes K @ v — K is never modified.
  The iterate vector v is a local allocation. K is not copied.
  Shallow-copy safety: AceTelemetry copies produced by
  _inject_design_params share this array; mutation here would
  propagate to the caller's object (ADR-013).
"""
from __future__ import annotations

import numpy as np

from ..contracts import assert_matrix_not_mutated
from ..telemetry import AceTelemetry
from ..types import AceCertificate, CertLevel

MEASUREMENT_DOMAIN = "SPECTRAL_ONLY"
MAX_ITER = 1000
TOL = 1e-8


def certify_l2(
    telemetry: AceTelemetry,
    *,
    tau: float = 1.0,
    delta: float = 0.05,
    max_iter: int = MAX_ITER,
    tol: float = TOL,
) -> AceCertificate:
    if telemetry.contraction_matrix is None and telemetry.spectral_estimate is None:
        raise TypeError(
            "L2 requires AceTelemetry with contraction_matrix or spectral_estimate."
        )

    with assert_matrix_not_mutated(telemetry.contraction_matrix, "L2"):
        if telemetry.spectral_estimate is not None:
            rho = float(telemetry.spectral_estimate)
            iterations_used = 0
        else:
            K = telemetry.contraction_matrix   # read-only reference — never K[...] = ...
            n = K.shape[^0]
            rng = np.random.default_rng(seed=42)
            v = rng.standard_normal(n)
            v = v / (np.linalg.norm(v) + 1e-12)
            rho_prev = 0.0
            iterations_used = max_iter
            for i in range(max_iter):
                Kv = K @ v          # K @ v allocates new array — K unchanged
                rho = float(np.linalg.norm(Kv))
                v = Kv / (rho + 1e-12)
                if abs(rho - rho_prev) < tol:
                    iterations_used = i + 1
                    break
                rho_prev = rho

    lipschitz_upper = rho
    gap_lb = 1.0 - lipschitz_upper
    certified = lipschitz_upper < (1.0 - delta)

    return AceCertificate(
        level=CertLevel.L2_POWERITER,
        certified=certified,
        lipschitz_upper=lipschitz_upper,
        gap_lb=max(0.0, gap_lb),
        contraction_rate=lipschitz_upper,
        budget_used=lipschitz_upper,
        tau=tau,
        delta=delta,
        margin=gap_lb - delta,
        tail_bound=(
            float("inf") if lipschitz_upper >= 1.0
            else tau / max(1e-12, gap_lb)
        ),
        details={
            "measurement_domain": MEASUREMENT_DOMAIN,
            "matrix_shape": list(K.shape)
                            if telemetry.contraction_matrix is not None else None,
            "spectral_estimate_used": telemetry.spectral_estimate is not None,
            "iterations": iterations_used,
            "step": telemetry.step,
        },
    )
```


### `src/pirtm/ace/levels/l3_nonexpansive.py` — Contract block added

```python
"""
L3-nonexpansive-clamp: TRL-4 (ADR-012).

Contract: NO_MATRIX_MUTATION
  This function delegates matrix access to certify_l2.
  certify_l2 is certified read-only (see its contract block).
  This function itself does not access contraction_matrix directly.
  Shallow-copy safety preserved transitively.
"""
```


### `src/pirtm/ace/levels/l4_perturbation.py` — Contract block added

```python
"""
L4-perturbation-budget: TRL-4 (ADR-012).

Contract: NO_MATRIX_MUTATION
  This function delegates matrix access to certify_l3 or certify_l2.
  Both are certified read-only. Transitively safe.
  This function itself does not access contraction_matrix directly.
"""
```


***

## Artifact 3 — `tests/conftest.py` — Debug mode activation

```python
# tests/conftest.py — append

import pirtm.ace.contracts as _ace_contracts

def pytest_configure(config):
    """Enable ACE matrix mutation debug guards for the entire test suite."""
    _ace_contracts.enable_debug()
```

This is the critical fixture. Every `certify_l2`, `certify_l3`, `certify_l4` call in CI now runs with the fingerprint guard active. No individual test needs to opt in.

***

## Artifact 4 — `tests/test_ace_matrix_immutability.py` ← NEW

```python
"""
Matrix immutability contract tests for ACE level implementations.
Pins the NO_MATRIX_MUTATION contract: contraction_matrix must be
identical (byte-for-byte) before and after any certify_lN call.

PIRTM_ACE_DEBUG is enabled globally by conftest.pytest_configure().
These tests also check independently via numpy array_equal.
"""
import numpy as np
import pytest

from pirtm.ace.telemetry import AceTelemetry
from pirtm.ace.levels.l2_poweriter import certify_l2
from pirtm.ace.levels.l3_nonexpansive import certify_l3
from pirtm.ace.levels.l4_perturbation import certify_l4
from pirtm.ace.protocol import AceProtocol
from pirtm.ace.contracts import assert_matrix_not_mutated, _matrix_fingerprint


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def K_4x4():
    """Contractive 4×4 matrix with known spectral radius ≈ 0.5."""
    rng = np.random.default_rng(seed=0)
    A = rng.standard_normal((4, 4))
    return A * 0.5 / np.linalg.norm(A, ord=2)

@pytest.fixture
def l2_telem(K_4x4):
    return AceTelemetry(
        step=0, q=0.5, epsilon=0.05,
        nXi=0.90, nLam=0.03,
        projected=False, residual=0.001,
        contraction_matrix=K_4x4,
    )

@pytest.fixture
def l3_telem(K_4x4):
    return AceTelemetry(
        step=0, q=0.5, epsilon=0.05,
        nXi=0.88, nLam=0.03,
        projected=False, residual=0.001,
        contraction_matrix=K_4x4,
        designed_clamp_norm=0.95,
    )

@pytest.fixture
def l4_telem(K_4x4):
    return AceTelemetry(
        step=0, q=0.5, epsilon=0.05,
        nXi=0.88, nLam=0.03,
        projected=False, residual=0.001,
        contraction_matrix=K_4x4,
        designed_clamp_norm=0.95,
        designed_perturbation_bound=0.05,
        disturbance_norm=0.1,
    )


# ── Fingerprint guard works ───────────────────────────────────────────────────

class TestFingerprintGuard:
    def test_guard_passes_on_read_only_access(self, K_4x4):
        fp_before = _matrix_fingerprint(K_4x4)
        _ = K_4x4 @ np.ones(4)   # read-only
        fp_after = _matrix_fingerprint(K_4x4)
        assert fp_before == fp_after

    def test_guard_catches_in_place_mutation(self, K_4x4):
        with pytest.raises(AssertionError, match="NO_MATRIX_MUTATION VIOLATED"):
            with assert_matrix_not_mutated(K_4x4, "TEST"):
                K_4x4[0, 0] = 999.0   # mutation — must be caught

    def test_guard_none_matrix_is_noop(self):
        with assert_matrix_not_mutated(None, "TEST"):
            pass   # no matrix → guard is silent


# ── L2 does not mutate ────────────────────────────────────────────────────────

class TestL2MatrixImmutability:
    def test_matrix_unchanged_after_certify_l2(self, l2_telem):
        K = l2_telem.contraction_matrix
        K_before = K.copy()
        certify_l2(l2_telem)
        np.testing.assert_array_equal(K, K_before)

    def test_matrix_fingerprint_unchanged_after_certify_l2(self, l2_telem):
        K = l2_telem.contraction_matrix
        fp_before = _matrix_fingerprint(K)
        certify_l2(l2_telem)
        assert _matrix_fingerprint(K) == fp_before

    def test_repeated_l2_calls_produce_identical_results(self, l2_telem):
        cert1 = certify_l2(l2_telem)
        cert2 = certify_l2(l2_telem)
        assert cert1.lipschitz_upper == cert2.lipschitz_upper

    def test_shared_matrix_between_two_telemetry_instances(self, K_4x4):
        """
        Two AceTelemetry instances sharing the same ndarray.
        certify_l2 on one must not affect the other's matrix.
        This is the exact scenario created by dataclasses.replace() in
        _inject_design_params — shallow copy shares the array.
        """
        t1 = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.9, nLam=0.0,
            projected=False, residual=0.0,
            contraction_matrix=K_4x4,
        )
        t2 = AceTelemetry(
            step=1, q=0.5, epsilon=0.05,
            nXi=0.9, nLam=0.0,
            projected=False, residual=0.0,
            contraction_matrix=K_4x4,   # same array object
        )
        assert t1.contraction_matrix is t2.contraction_matrix

        K_before = K_4x4.copy()
        certify_l2(t1)
        certify_l2(t2)

        np.testing.assert_array_equal(K_4x4, K_before)


# ── L3 does not mutate (transitively via L2) ─────────────────────────────────

class TestL3MatrixImmutability:
    def test_matrix_unchanged_after_certify_l3(self, l3_telem):
        K = l3_telem.contraction_matrix
        K_before = K.copy()
        certify_l3(l3_telem)
        np.testing.assert_array_equal(K, K_before)

    def test_shared_matrix_between_original_and_inject_copy(self, K_4x4):
        """
        Simulate _inject_design_params shallow copy scenario at L3.
        Original and copy share contraction_matrix.
        certify_l3 on the copy must not mutate the original's matrix.
        """
        import dataclasses
        original = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.88, nLam=0.03,
            projected=False, residual=0.001,
            contraction_matrix=K_4x4,
        )
        injected = dataclasses.replace(
            original,
            designed_clamp_norm=0.95,
        )
        assert original.contraction_matrix is injected.contraction_matrix

        K_before = K_4x4.copy()
        certify_l3(injected)

        np.testing.assert_array_equal(K_4x4, K_before)
        np.testing.assert_array_equal(
            original.contraction_matrix, K_before
        )


# ── L4 does not mutate (transitively via L3 → L2) ────────────────────────────

class TestL4MatrixImmutability:
    def test_matrix_unchanged_after_certify_l4(self, l4_telem):
        K = l4_telem.contraction_matrix
        K_before = K.copy()
        certify_l4(l4_telem)
        np.testing.assert_array_equal(K, K_before)


# ── Protocol pipeline does not mutate ────────────────────────────────────────

class TestProtocolPipelineImmutability:
    def test_certify_l4_via_protocol_does_not_mutate_matrix(self, K_4x4):
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.88, nLam=0.03,
            projected=False, residual=0.001,
            contraction_matrix=K_4x4,
            disturbance_norm=0.1,
        )
        K_before = K_4x4.copy()

        proto = AceProtocol(
            tau=1.0,
            designed_clamp_norm=0.95,
            designed_perturbation_bound=0.05,
        )
        proto.certify(t, prime_index=7)

        # Caller's matrix and telemetry object both unchanged
        np.testing.assert_array_equal(K_4x4, K_before)
        assert t.designed_clamp_norm is None   # caller object not mutated (ADR-013)
```


***

## Artifact 5 — `docs/contracts/ace-matrix-immutability.md` ← NEW

```markdown
# ACE Level Contract: NO_MATRIX_MUTATION
status:   active
date:     2026-02-28
scope:    all functions in src/pirtm/ace/levels/

## Statement

Every function `certify_lN(telemetry: AceTelemetry, ...)` must treat
`telemetry.contraction_matrix` as a read-only array for the duration
of its call. No in-place writes, no `K[...] = ...`, no passing K to
a function that mutates it.

## Why this matters

`_inject_design_params` in `AceProtocol._normalise()` uses
`dataclasses.replace()` to produce a shallow copy of `AceTelemetry`.
The `contraction_matrix` ndarray is **shared** between the caller's
original object and the injected copy. Any in-place mutation inside a
level function propagates back to the caller's `AceTelemetry` instance.

This would silently corrupt:
  - Repeated calls to `certify()` with the same telemetry object
  - Cross-protocol reuse (the ADR-013 scenario)
  - Any downstream code that inspects `telemetry.contraction_matrix`
    after calling `protocol.certify()`

## What is safe

```python
Kv = K @ v          # safe — allocates new array, K unchanged
rho = np.linalg.norm(K, ord=2)  # safe — read-only
vals = np.linalg.eigvalsh(K)    # safe — read-only
```


## What is forbidden

```python
K = 0.0                   # FORBIDDEN — in-place mutation
K /= np.linalg.norm(K)          # FORBIDDEN — in-place division
np.fill_diagonal(K, 0.0)        # FORBIDDEN — in-place fill
scipy.linalg.lu(K, overwrite_a=True)  # FORBIDDEN — overwrite flag
```


## Deep copy is also forbidden

```python
K_copy = K.copy()
K_copy[...] = ...   # ALLOWED — copy is local
```

Deep copying is unnecessary overhead and is a sign the implementation
may be trying to work around a mutation it plans to do. If a level
genuinely needs a modified version of K, it must allocate a new array
and document why.

## Enforcement

- `PIRTM_ACE_DEBUG=1` enables `assert_matrix_not_mutated()` context manager
in `pirtm.ace.contracts`. The test suite sets this globally via
`conftest.pytest_configure()`.
- `tests/test_ace_matrix_immutability.py` pins before/after fingerprints
for L2, L3, L4, and the full protocol pipeline.
- CI runs with `PIRTM_ACE_DEBUG=1` set in the test environment.


## New level checklist

Before merging any `certify_lN` implementation:

- [ ] Docstring carries `Contract: NO_MATRIX_MUTATION` block
- [ ] All matrix operations use `K @ v`, `np.linalg.*`, or similar read-only ops
- [ ] `with assert_matrix_not_mutated(telemetry.contraction_matrix, "LN"):` wraps body
- [ ] `test_ace_matrix_immutability.py` has a `TestLNMatrixImmutability` class

```

***

## ADR-014 Entry

```md
# ADR-014: NO_MATRIX_MUTATION contract for ACE level implementations
Status:    accepted
Date:      2026-02-28
Decider:   Lead MT (RVG)
trl:       4
Horizon:   7 days
Metric:
  - test_ace_matrix_immutability.py green with PIRTM_ACE_DEBUG=1
  - conftest.pytest_configure() enables debug guard globally
  - docs/contracts/ace-matrix-immutability.md present before
    any L5+ implementation begins

## Decision
Level implementations are responsible for matrix read-only access.
_inject_design_params uses shallow copy (dataclasses.replace) and does
NOT deep-copy contraction_matrix. This is correct and safe IF and ONLY
IF the NO_MATRIX_MUTATION contract is upheld by all level functions.

The contract is enforced by:
  1. Named contract block in every certify_lN docstring
  2. assert_matrix_not_mutated() debug guard (pirtm.ace.contracts)
  3. Fingerprint tests in test_ace_matrix_immutability.py
  4. New level checklist in docs/contracts/ace-matrix-immutability.md

Deep-copying contraction_matrix in _inject_design_params is explicitly
rejected: it would double memory for every L2/L3/L4 call, penalise
correct callers to compensate for hypothetical future incorrect level
implementations, and obscure the actual correctness requirement.

## Chain of decisions
ADR-010 → promoted AceCertificate
ADR-011 → AceTelemetry as unified telemetry type
ADR-012 → design parameters as pre-committed bounds
ADR-013 → copy-on-normalise (shallow) in _inject_design_params
ADR-014 → NO_MATRIX_MUTATION contract closes the shallow-copy safety argument
```

<span style="display:none">[^1]</span>

<div align="center">⁂</div>

[^1]: PHASE11_AI_HEALTH_TWIN_IMPLEMENTATION.md

