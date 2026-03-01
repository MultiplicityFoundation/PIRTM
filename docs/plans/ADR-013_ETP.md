<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# which is more preferable?: AceProtocol.__init__ should accept designed_clamp_norm and designed_perturbation_bound as protocol-level defaults that get injected into every AceTelemetry during _normalise(), or whether callers must always set them explicitly on each AceTelemetry instance?

Neither option alone is preferable. The correct answer is the **inject-if-absent hybrid**: `AceProtocol.__init__` accepts protocol-level defaults and `_normalise()` injects them only when the `AceTelemetry` instance has `None` in those fields. Per-telemetry explicit values always win. Here is the full reasoning, artifact, and the governing rule.

***

## Why Neither Pure Option Wins

| Axis | Protocol-only defaults | Per-telemetry explicit | Inject-if-absent hybrid |
| :-- | :-- | :-- | :-- |
| `StepInfo` caller reaches L3/L4 | ✓ | ✗ requires code change | ✓ |
| Audit trail: params visible on telemetry record | ✗ hidden | ✓ explicit | ✓ always present after normalise |
| Per-subsystem design envelope in one session | ✗ one envelope | ✓ | ✓ override per-instance |
| Single point of commitment for uniform sessions | ✓ | ✗ repetitive | ✓ |
| IP claim surface traceable to a single committed value | ✗ buried in protocol | ✓ | ✓ injected value is immutable on frozen copy |

The pure protocol-only option **hides the commitment** — a reader of a `AceTelemetry` record in a log or audit trail cannot recover the design parameter without also knowing which `AceProtocol` instance produced it. That breaks ADR-012's claim surface / verification trace distinction. The pure explicit option **blocks `StepInfo` callers from ever reaching L3/L4** without a mandatory code change, which is an unnecessary friction wall. The hybrid resolves both.

***

## Governing Rule (L0 invariant for injection)

```
If AceTelemetry.designed_clamp_norm is None
   AND AceProtocol.default_designed_clamp_norm is not None
→  inject: telemetry.designed_clamp_norm = protocol default

If AceTelemetry.designed_clamp_norm is not None
→  respect it — do NOT overwrite with protocol default

Same rule for designed_perturbation_bound.
```

The injected value is committed **before** `validate()` is called — so `validate()`'s design envelope invariant fires on the injected value, not a `None`-skip. This is the only order that preserves the hard-halt guarantee.

***

## Artifact 1 — Updated `src/pirtm/ace/protocol.py`

```python
"""
AceProtocol — unified ACE certification dispatcher.

Design parameter injection (ADR-012, inject-if-absent rule):
  AceProtocol(
      designed_clamp_norm=0.95,
      designed_perturbation_bound=0.05,
  )
  injects those values into every AceTelemetry that has None in those fields.
  Per-telemetry explicit values always take precedence.

This allows StepInfo-only callers to reach L3/L4 without touching
AceTelemetry construction, while preserving per-instance override capability.
"""
from __future__ import annotations

import warnings
from typing import Sequence, Optional

import numpy as np

from pirtm.types import StepInfo
from .budget import AceBudget
from .telemetry import AceTelemetry
from .witness import AceWitness
from .types import AceCertificate, CertLevel, AceBudgetState
from .levels.l0_heuristic import certify_l0
from .levels.l1_normbound import certify_l1
from .levels.l2_poweriter import certify_l2
from .levels.l3_nonexpansive import certify_l3
from .levels.l4_perturbation import certify_l4


_DISPATCH = {
    CertLevel.L4_PERTURBATION:  certify_l4,
    CertLevel.L3_NONEXPANSIVE:  certify_l3,
    CertLevel.L2_POWERITER:     certify_l2,
}

_LEVEL_ORDER = [
    CertLevel.L0_HEURISTIC,
    CertLevel.L1_NORMBOUND,
    CertLevel.L2_POWERITER,
    CertLevel.L3_NONEXPANSIVE,
    CertLevel.L4_PERTURBATION,
]


def _level_rank(level: CertLevel) -> int:
    return _LEVEL_ORDER.index(level)


class AceProtocol:
    """
    Stateful ACE protocol runner.

    Protocol-level design parameter defaults (inject-if-absent):
      designed_clamp_norm:         injected into AceTelemetry.designed_clamp_norm
                                   if that field is None
      designed_perturbation_bound: injected into AceTelemetry.designed_perturbation_bound
                                   if that field is None

    Per-telemetry explicit values always override protocol defaults.
    Injection happens in _normalise(), BEFORE validate().
    """

    def __init__(
        self,
        tau: float = 1.0,
        delta: float = 0.05,
        designed_clamp_norm: Optional[float] = None,
        designed_perturbation_bound: Optional[float] = None,
    ) -> None:
        if tau <= 0:
            raise ValueError("tau must be > 0")
        if not (0 < delta < 1):
            raise ValueError("delta must be in (0, 1)")
        if (designed_clamp_norm is not None
                and not (0 < designed_clamp_norm <= 1.0)):
            raise ValueError(
                f"designed_clamp_norm must be in (0, 1.0], got {designed_clamp_norm}"
            )
        if (designed_perturbation_bound is not None
                and designed_perturbation_bound < 0):
            raise ValueError(
                f"designed_perturbation_bound must be ≥ 0, "
                f"got {designed_perturbation_bound}"
            )

        self.budget = AceBudget(tau=tau)
        self.delta = delta
        self.designed_clamp_norm = designed_clamp_norm
        self.designed_perturbation_bound = designed_perturbation_bound

    # ── Primary API ──────────────────────────────────────────────────────────

    def certify(
        self,
        telemetry: AceTelemetry | StepInfo | Sequence,
        prime_index: int,
        *,
        min_level: CertLevel = CertLevel.L0_HEURISTIC,
        tail_norm: float = 0.0,
    ) -> AceWitness:
        """
        Unified dispatcher. Accepts AceTelemetry, StepInfo, or a sequence.
        Injects protocol-level design params into telemetry where absent,
        then validates, dispatches to highest feasible level, and emits witness.
        """
        records = self._normalise(telemetry)   # inject-if-absent happens here
        if not records:
            raise ValueError("AceProtocol.certify: no telemetry provided")

        for rec in records:
            rec.validate()                     # design envelope invariants fire here

        rep = max(records, key=lambda r: r.q)
        feasible = rep.highest_feasible_level()

        if _level_rank(feasible) < _level_rank(min_level):
            raise ValueError(
                f"AceProtocol.certify: telemetry supports up to {feasible.value} "
                f"but min_level={min_level.value} was requested. "
                f"Provide contraction_matrix / designed_clamp_norm / "
                f"designed_perturbation_bound as needed, or set them as "
                f"protocol defaults in AceProtocol.__init__."
            )

        tau = self.budget.snapshot().tau

        if feasible in _DISPATCH:
            cert = _DISPATCH[feasible](rep, tau=tau, delta=self.delta)
        elif feasible == CertLevel.L1_NORMBOUND:
            cert = certify_l1(
                rep.weight_vector, rep.basis_norms,
                tau=tau, delta=self.delta,
            )
        else:
            cert = certify_l0(records, tau=tau,
                              tail_norm=tail_norm, delta=self.delta)

        self.budget.consume(cert.budget_used)
        return AceWitness.from_certificate(cert, prime_index)

    def budget_state(self) -> AceBudgetState:
        return self.budget.snapshot()

    # ── Deprecated ───────────────────────────────────────────────────────────

    def certify_from_telemetry(
        self,
        records: Sequence[StepInfo],
        prime_index: int,
        *,
        tail_norm: float = 0.0,
    ) -> AceWitness:
        warnings.warn(
            "certify_from_telemetry() is deprecated. "
            "Use AceProtocol.certify(telemetry, prime_index).",
            DeprecationWarning, stacklevel=2,
        )
        return self.certify(list(records), prime_index, tail_norm=tail_norm)

    def certify_from_weights(
        self,
        weights: Sequence[float],
        basis_norms: Sequence[float],
        prime_index: int,
    ) -> AceWitness:
        warnings.warn(
            "certify_from_weights() is deprecated. "
            "Set AceTelemetry.weight_vector and basis_norms, then call certify().",
            DeprecationWarning, stacklevel=2,
        )
        t = AceTelemetry(
            step=0, q=0.0, epsilon=1.0, nXi=0.0, nLam=0.0,
            projected=False, residual=0.0,
            weight_vector=list(weights),
            basis_norms=list(basis_norms),
        )
        return self.certify(t, prime_index)

    def certify_from_matrix(
        self,
        K: np.ndarray,
        prime_index: int,
    ) -> AceWitness:
        warnings.warn(
            "certify_from_matrix() is deprecated. "
            "Set AceTelemetry.contraction_matrix, then call certify().",
            DeprecationWarning, stacklevel=2,
        )
        t = AceTelemetry(
            step=0, q=float(np.linalg.norm(K, ord=2)),
            epsilon=0.05, nXi=1.0, nLam=0.0,
            projected=False, residual=0.0,
            contraction_matrix=K,
        )
        return self.certify(t, prime_index)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _normalise(
        self,
        telemetry: AceTelemetry | StepInfo | Sequence,
    ) -> list[AceTelemetry]:
        """
        Convert all inputs to list[AceTelemetry].
        Apply inject-if-absent rule for protocol-level design parameters.
        Injection precedes validate() — invariants fire on injected values.
        """
        if isinstance(telemetry, AceTelemetry):
            raw = [telemetry]
        elif isinstance(telemetry, StepInfo):
            raw = [AceTelemetry.from_step_info(telemetry)]
        else:
            raw = []
            for item in telemetry:
                if isinstance(item, AceTelemetry):
                    raw.append(item)
                elif isinstance(item, StepInfo):
                    raw.append(AceTelemetry.from_step_info(item))
                else:
                    raise TypeError(
                        f"Expected AceTelemetry or StepInfo, got {type(item)}"
                    )

        return [self._inject_design_params(t) for t in raw]

    def _inject_design_params(self, t: AceTelemetry) -> AceTelemetry:
        """
        Inject protocol-level design params into telemetry fields that are None.
        Fields that are already set are NEVER overwritten.
        Returns the same object mutated in place (AceTelemetry is not frozen).
        """
        if (self.designed_clamp_norm is not None
                and t.designed_clamp_norm is None):
            t.designed_clamp_norm = self.designed_clamp_norm

        if (self.designed_perturbation_bound is not None
                and t.designed_perturbation_bound is None):
            t.designed_perturbation_bound = self.designed_perturbation_bound

        return t
```


***

## Artifact 2 — Test Harness: `tests/test_ace_protocol_injection.py`

```python
"""
AceProtocol inject-if-absent design parameter tests.
Covers all four injection scenarios (ADR-012):
  1. Protocol default injected into StepInfo-only caller → reaches L3/L4
  2. Per-telemetry explicit value respected → protocol default ignored
  3. Both None → stays at L0/L1/L2
  4. Injection fires BEFORE validate() → DESIGN_ENVELOPE_VIOLATION raised
     when runtime measurement exceeds injected design commitment
"""
import pytest
import numpy as np

from pirtm.types import StepInfo
from pirtm.ace.protocol import AceProtocol
from pirtm.ace.telemetry import AceTelemetry
from pirtm.ace.types import CertLevel


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def K_contractive():
    return np.diag([0.5, 0.4])

@pytest.fixture
def step_info_with_matrix(K_contractive):
    """StepInfo + matrix but NO design params — relies on protocol injection."""
    return AceTelemetry(
        step=0, q=0.5, epsilon=0.05,
        nXi=0.88, nLam=0.03,           # runtime measurements within envelope
        projected=False, residual=0.001,
        contraction_matrix=K_contractive,
        # designed_clamp_norm=None        ← will be injected by protocol
        # designed_perturbation_bound=None ← will be injected by protocol
    )

@pytest.fixture
def protocol_l3():
    """Protocol with L3 design commitment only."""
    return AceProtocol(
        tau=1.0, delta=0.05,
        designed_clamp_norm=0.95,
    )

@pytest.fixture
def protocol_l4():
    """Protocol with both L3 and L4 design commitments."""
    return AceProtocol(
        tau=1.0, delta=0.05,
        designed_clamp_norm=0.95,
        designed_perturbation_bound=0.05,
    )

@pytest.fixture
def pure_step_info():
    return StepInfo(
        step=0, q=0.5, epsilon=0.05,
        nXi=0.88, nLam=0.03,
        projected=False, residual=0.001,
    )


# ── Scenario 1: Protocol default reaches L3 from StepInfo ────────────────────

class TestProtocolInjectionReachesHigherLevel:
    def test_step_info_plus_matrix_reaches_l3_via_protocol_default(
        self, protocol_l3, step_info_with_matrix
    ):
        witness = protocol_l3.certify(step_info_with_matrix, prime_index=5)
        assert witness.cert.level == CertLevel.L3_NONEXPANSIVE

    def test_step_info_plus_matrix_reaches_l4_via_protocol_default(
        self, protocol_l4, step_info_with_matrix
    ):
        # Add disturbance_norm for L4 gate
        step_info_with_matrix.disturbance_norm = 0.1
        witness = protocol_l4.certify(step_info_with_matrix, prime_index=7)
        assert witness.cert.level == CertLevel.L4_PERTURBATION

    def test_pure_step_info_stays_l0_without_protocol_defaults(
        self, pure_step_info
    ):
        proto = AceProtocol(tau=1.0)   # no design params set
        witness = proto.certify(pure_step_info, prime_index=2)
        assert witness.cert.level == CertLevel.L0_HEURISTIC

    def test_pure_step_info_reaches_l3_with_protocol_defaults(
        self, K_contractive, pure_step_info
    ):
        # Step 1: inject matrix (protocol can't inject matrix — caller must)
        t = AceTelemetry.from_step_info(pure_step_info)
        t.contraction_matrix = K_contractive
        # Step 2: protocol provides the design commitment
        proto = AceProtocol(
            tau=1.0,
            designed_clamp_norm=0.95,
        )
        witness = proto.certify(t, prime_index=11)
        assert witness.cert.level == CertLevel.L3_NONEXPANSIVE

    def test_injection_sets_field_on_telemetry_object(
        self, protocol_l4, step_info_with_matrix
    ):
        # After normalise, the telemetry instance should have design params set
        records = protocol_l4._normalise(step_info_with_matrix)
        assert records[0].designed_clamp_norm == 0.95
        assert records[0].designed_perturbation_bound == 0.05


# ── Scenario 2: Per-telemetry explicit values respected ──────────────────────

class TestPerTelemetryExplicitOverridesProtocol:
    def test_explicit_clamp_norm_not_overwritten(
        self, K_contractive
    ):
        """Telemetry has designed_clamp_norm=0.80; protocol default is 0.95.
        certify_l3 must use 0.80 — the per-telemetry commitment."""
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.75, nLam=0.03,
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
            designed_clamp_norm=0.80,     # explicit per-telemetry
        )
        proto = AceProtocol(
            tau=1.0,
            designed_clamp_norm=0.95,     # protocol default — must NOT win
        )
        witness = proto.certify(t, prime_index=3)
        assert witness.cert.details["designed_clamp_norm"] == 0.80

    def test_explicit_perturbation_bound_not_overwritten(
        self, K_contractive
    ):
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.88, nLam=0.02,
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
            designed_clamp_norm=0.95,
            designed_perturbation_bound=0.03,   # explicit per-telemetry
            disturbance_norm=0.1,
        )
        proto = AceProtocol(
            tau=1.0,
            designed_clamp_norm=0.95,
            designed_perturbation_bound=0.05,   # protocol default — must NOT win
        )
        witness = proto.certify(t, prime_index=5)
        assert witness.cert.details["designed_perturbation_bound"] == 0.03

    def test_mixed_batch_respects_per_instance_override(
        self, K_contractive
    ):
        """Sequence of two telemetry instances: one explicit, one None → injected."""
        t_explicit = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.70, nLam=0.02,
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
            designed_clamp_norm=0.75,     # explicit
        )
        t_default = AceTelemetry(
            step=1, q=0.6, epsilon=0.05,
            nXi=0.80, nLam=0.03,
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
            # designed_clamp_norm=None → will be injected as 0.95
        )
        proto = AceProtocol(tau=1.0, designed_clamp_norm=0.95)
        normalised = proto._normalise([t_explicit, t_default])
        assert normalised[0].designed_clamp_norm == 0.75   # explicit wins
        assert normalised[1].designed_clamp_norm == 0.95   # injected


# ── Scenario 3: Both None — no upgrade ───────────────────────────────────────

class TestNoInjectionNoUpgrade:
    def test_no_protocol_defaults_no_design_params_stays_l2(
        self, K_contractive
    ):
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.9, nLam=0.0,
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
            # both design params None
        )
        proto = AceProtocol(tau=1.0)   # no protocol defaults
        witness = proto.certify(t, prime_index=2)
        assert witness.cert.level == CertLevel.L2_POWERITER


# ── Scenario 4: Injection fires BEFORE validate() ────────────────────────────

class TestInjectionBeforeValidation:
    def test_design_envelope_violation_raised_after_injection(
        self, K_contractive
    ):
        """
        telemetry.nXi = 0.97 (runtime)
        protocol.designed_clamp_norm = 0.95
        → injected: telemetry.designed_clamp_norm = 0.95
        → validate(): 0.97 > 0.95 → DESIGN_ENVELOPE_VIOLATION (hard halt)
        """
        t = AceTelemetry(
            step=2, q=0.5, epsilon=0.05,
            nXi=0.97,               # runtime EXCEEDS the injected commitment
            nLam=0.03,
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
            # designed_clamp_norm=None → will be injected as 0.95
        )
        proto = AceProtocol(tau=1.0, designed_clamp_norm=0.95)
        with pytest.raises(RuntimeError, match="DESIGN_ENVELOPE_VIOLATION"):
            proto.certify(t, prime_index=5)

    def test_injection_order_is_inject_then_validate(
        self, K_contractive
    ):
        """
        Confirms injection order: _normalise() injects → validate() fires.
        If validate() ran first (before injection), the violation would not
        be detected (designed_clamp_norm would be None, skipping the check).
        """
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.99, nLam=0.0,     # would pass pre-injection validate()
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
        )
        proto = AceProtocol(tau=1.0, designed_clamp_norm=0.95)
        # nXi=0.99 > 0.95 → must raise after injection
        with pytest.raises(RuntimeError, match="DESIGN_ENVELOPE_VIOLATION"):
            proto.certify(t, prime_index=3)


# ── AceProtocol.__init__ validation ──────────────────────────────────────────

class TestProtocolInitValidation:
    def test_designed_clamp_norm_must_be_in_0_1(self):
        with pytest.raises(ValueError, match="designed_clamp_norm"):
            AceProtocol(tau=1.0, designed_clamp_norm=1.05)

    def test_designed_clamp_norm_zero_invalid(self):
        with pytest.raises(ValueError, match="designed_clamp_norm"):
            AceProtocol(tau=1.0, designed_clamp_norm=0.0)

    def test_designed_perturbation_bound_negative_invalid(self):
        with pytest.raises(ValueError, match="designed_perturbation_bound"):
            AceProtocol(tau=1.0, designed_perturbation_bound=-0.01)

    def test_designed_perturbation_bound_zero_valid(self):
        proto = AceProtocol(tau=1.0, designed_perturbation_bound=0.0)
        assert proto.designed_perturbation_bound == 0.0

    def test_both_none_is_valid_l0_l1_l2_protocol(self):
        proto = AceProtocol(tau=1.0)
        assert proto.designed_clamp_norm is None
        assert proto.designed_perturbation_bound is None
```


***

## Artifact 3 — Migration Guide Addendum `docs/migration/certify-v1.md`

```markdown
## Design Parameter Injection (ADR-012 addendum)

### Option A — Protocol-level commitment (recommended for uniform sessions)

All calls in this session use the same design envelope:

```python
from pirtm.ace.protocol import AceProtocol

protocol = AceProtocol(
    tau=1.0,
    designed_clamp_norm=0.95,          # committed for all calls
    designed_perturbation_bound=0.05,  # committed for all calls
)

# StepInfo-only caller reaches L3/L4 as long as matrix is provided:
import numpy as np
from pirtm.ace.telemetry import AceTelemetry

t = AceTelemetry.from_step_info(step_info)
t.contraction_matrix = np.diag([0.5, 0.4])
witness = protocol.certify(t, prime_index=7)
# → witness.cert.level == CertLevel.L3_NONEXPANSIVE
```


### Option B — Per-telemetry explicit (required for multi-envelope sessions)

Different subsystems in one session each carry their own design commitment:

```python
t_subsystem_A = AceTelemetry(
    ...,
    designed_clamp_norm=0.80,           # A's envelope
    designed_perturbation_bound=0.03,
)
t_subsystem_B = AceTelemetry(
    ...,
    designed_clamp_norm=0.95,           # B's envelope
    designed_perturbation_bound=0.08,
)
protocol = AceProtocol(tau=1.0)         # no protocol defaults needed
```


### Inject-if-absent rule

Protocol default is injected ONLY when `AceTelemetry.designed_clamp_norm is None`.
Per-telemetry explicit values are NEVER overwritten.

### Injection order is fixed

`_normalise()` → inject → `validate()` → dispatch

If injection ran after `validate()`, a runtime measurement exceeding
the injected design commitment would not be caught. This is why injection
is unconditionally before validation.

```

***

## ADR-013 Entry

```md
# ADR-013: AceProtocol inject-if-absent for design parameter commitment
Status:    accepted
Date:      2026-02-28
Decider:   Lead MT (RVG)
trl:       4
Horizon:   7 days
Metric:
  - test_ace_protocol_injection.py: all 4 scenarios green on 3.11/3.12
  - Per-telemetry explicit value wins in mixed-batch test
  - DESIGN_ENVELOPE_VIOLATION raised when injected commitment
    is exceeded by runtime measurement

## Decision
AceProtocol.__init__ accepts designed_clamp_norm and
designed_perturbation_bound as optional protocol-level defaults.
_normalise() applies inject-if-absent: fields that are None receive
the protocol default; fields that are already set are never overwritten.
Injection precedes validate() — invariants fire on injected values.

## Rationale
Pure protocol-only: hides commitment from telemetry audit trail.
Pure per-telemetry: blocks StepInfo callers from L3/L4 without code change.
Inject-if-absent: both use cases served; explicit always wins; audit trail
always carries the committed value after normalise().

## IP note
The injected value becomes the TRL-4 claim surface on the produced
AceCertificate. It is traceable: cert.details["designed_clamp_norm"]
carries the committed value regardless of whether it came from protocol
default or per-telemetry explicit. ADR-006 boundary upheld.
```


***

## Precision Question

> `_inject_design_params` currently mutates the `AceTelemetry` instance in-place. This means the original `AceTelemetry` object passed by the caller is modified as a side effect of calling `protocol.certify()`. **Should `_normalise()` produce a shallow copy of each `AceTelemetry` before injecting** (so the caller's object is never mutated), or is in-place mutation acceptable given that `AceTelemetry` is not frozen and the injected value is idempotent after the first call?

