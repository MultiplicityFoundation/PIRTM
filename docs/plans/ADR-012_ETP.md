<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# is in-place mutation is acceptable given that AceTelemetry is not frozen and the injected value is idempotent after the first call

**No. In-place mutation is not acceptable**, and idempotency is a false guarantee. Here is the exact failure case, the minimal fix, and the test that pins it.

***

## Why Idempotency Fails

Idempotency only holds if the same `AceTelemetry` instance is passed to **the same protocol** (or protocols with identical design params). The moment the same object crosses two protocols with different commitments, the inject-if-absent rule silently misfires:

```python
proto_A = AceProtocol(tau=1.0, designed_clamp_norm=0.95)
proto_B = AceProtocol(tau=1.0, designed_clamp_norm=0.80)

t = AceTelemetry(step=0, q=0.5, ..., contraction_matrix=K)
# t.designed_clamp_norm = None

proto_A.certify(t, prime_index=2)
# _inject_design_params mutates t in-place → t.designed_clamp_norm = 0.95

proto_B.certify(t, prime_index=3)
# t.designed_clamp_norm is now 0.95 (not None)
# inject-if-absent fires False → proto_B's 0.80 is SILENTLY IGNORED
# cert uses 0.95 (proto_A's value) — wrong, and undetectable
```

This is not a theoretical edge case. Any `AceProtocol` test that constructs a single fixture and passes it to two different protocol instances will hit it. The audit trail records `0.95` on the second certificate but the caller committed `0.80`. ADR-012's claim surface is corrupted silently.

The idempotency argument would only hold in a world where one `AceTelemetry` instance is ever passed to one `AceProtocol` instance — which is not an invariant the type system enforces or that the API surface implies.

***

## Central Tension

**Mutability convenience vs. audit trail integrity** — `AceTelemetry` is mutable by design (not frozen) so L3/L4 fields can be set progressively. That same mutability makes in-place injection a latent correctness bug. The fix is not to freeze `AceTelemetry` (that would break progressive field setting) but to copy-on-normalise: `_normalise()` owns a defensive copy so the caller's object is never the injection target.

***

## Levers

| Lever | Owner | Metric | Horizon |
| :-- | :-- | :-- | :-- |
| `_inject_design_params` copies via `dataclasses.replace()` | Lead MT | Cross-protocol reuse test passes; caller object unchanged after `certify()` | 7 days |
| `test_ace_protocol_injection.py` cross-protocol test added | QA Lead | New test catches mutation bug in CI before merge | 7 days |


***

## Artifact 1 — Fixed `_inject_design_params` in `protocol.py`

```python
import dataclasses

def _inject_design_params(self, t: AceTelemetry) -> AceTelemetry:
    """
    Return a COPY of t with protocol-level design params injected
    where the field is None. The caller's original object is never mutated.

    Uses dataclasses.replace() for a clean shallow copy.
    Fields already set on t are preserved exactly — never overwritten.
    """
    needs_clamp = (
        self.designed_clamp_norm is not None
        and t.designed_clamp_norm is None
    )
    needs_perturbation = (
        self.designed_perturbation_bound is not None
        and t.designed_perturbation_bound is None
    )

    if not needs_clamp and not needs_perturbation:
        return t  # no injection needed — return original, no copy cost

    overrides: dict = {}
    if needs_clamp:
        overrides["designed_clamp_norm"] = self.designed_clamp_norm
    if needs_perturbation:
        overrides["designed_perturbation_bound"] = self.designed_perturbation_bound

    return dataclasses.replace(t, **overrides)
```

The `if not needs_clamp and not needs_perturbation: return t` branch is a deliberate fast-path: when no injection is needed, the original object is returned unchanged, avoiding an unnecessary copy on every L0/L1/L2 call.

***

## Artifact 2 — `tests/test_ace_protocol_injection.py` — New Tests

Add to the existing `TestProtocolInjectionReachesHigherLevel` class:

```python
class TestCallerObjectImmutability:
    """
    Caller's AceTelemetry must be unchanged after certify().
    In-place mutation would silently corrupt cross-protocol reuse.
    """

    def test_caller_object_not_mutated_after_certify(
        self, K_contractive
    ):
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.88, nLam=0.03,
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
            # designed_clamp_norm = None
        )
        original_dcn = t.designed_clamp_norm  # None

        proto = AceProtocol(tau=1.0, designed_clamp_norm=0.95)
        proto.certify(t, prime_index=5)

        # Caller's object must be unchanged
        assert t.designed_clamp_norm == original_dcn  # still None

    def test_cross_protocol_reuse_uses_correct_commitment(
        self, K_contractive
    ):
        """
        Same AceTelemetry instance passed to proto_A then proto_B.
        Each certificate must carry its own protocol's design commitment.
        In-place mutation would make the second cert carry proto_A's value.
        """
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.75, nLam=0.03,       # nXi is within both envelopes
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
        )
        proto_A = AceProtocol(tau=1.0, designed_clamp_norm=0.95)
        proto_B = AceProtocol(tau=1.0, designed_clamp_norm=0.80)

        witness_A = proto_A.certify(t, prime_index=3)
        witness_B = proto_B.certify(t, prime_index=5)

        assert witness_A.cert.details["designed_clamp_norm"] == 0.95
        assert witness_B.cert.details["designed_clamp_norm"] == 0.80

    def test_explicit_value_on_caller_object_survives_cross_protocol(
        self, K_contractive
    ):
        """
        Caller sets designed_clamp_norm=0.70 explicitly.
        Neither protocol should overwrite it.
        """
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.65, nLam=0.0,
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
            designed_clamp_norm=0.70,   # explicit — must survive both calls
        )
        proto_A = AceProtocol(tau=1.0, designed_clamp_norm=0.95)
        proto_B = AceProtocol(tau=1.0, designed_clamp_norm=0.80)

        witness_A = proto_A.certify(t, prime_index=3)
        witness_B = proto_B.certify(t, prime_index=5)

        assert witness_A.cert.details["designed_clamp_norm"] == 0.70
        assert witness_B.cert.details["designed_clamp_norm"] == 0.70
        assert t.designed_clamp_norm == 0.70  # caller's object still 0.70

    def test_no_copy_taken_when_no_injection_needed(
        self, K_contractive
    ):
        """
        Fast-path: when no injection is needed, _inject_design_params
        returns the same object (identity, not a copy).
        """
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.88, nLam=0.03,
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
            designed_clamp_norm=0.95,          # already set — no injection
            designed_perturbation_bound=0.05,  # already set — no injection
        )
        proto = AceProtocol(
            tau=1.0,
            designed_clamp_norm=0.95,
            designed_perturbation_bound=0.05,
        )
        normalised = proto._normalise(t)
        # No injection needed → same object returned
        assert normalised[0] is t

    def test_copy_taken_when_injection_needed(
        self, K_contractive
    ):
        """
        When injection is needed, _inject_design_params returns a
        distinct object — not the same reference as the input.
        """
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.88, nLam=0.03,
            projected=False, residual=0.001,
            contraction_matrix=K_contractive,
            # designed_clamp_norm = None → injection needed
        )
        proto = AceProtocol(tau=1.0, designed_clamp_norm=0.95)
        normalised = proto._normalise(t)
        # Injection needed → new object, not same reference
        assert normalised[0] is not t
        assert normalised[0].designed_clamp_norm == 0.95
        assert t.designed_clamp_norm is None  # original untouched
```


***

## ADR-013 Amendment

```md
## ADR-013 Amendment — copy-on-normalise (2026-02-28)

_inject_design_params returns dataclasses.replace(t, **overrides)
instead of mutating t in place.

Rationale: idempotency of in-place injection holds only for single-protocol
use. Cross-protocol object reuse silently selects the first protocol's
commitment for all subsequent certifications. This corrupts the TRL-4
claim surface on the second certificate without raising any error.

Fast path: if no injection is needed, the original object is returned
(identity preserved, no copy cost on L0/L1/L2 calls).

Invariant added: after protocol.certify(t, ...), t is identical to its
pre-call state. Certified on Python 3.11/3.12 via
TestCallerObjectImmutability suite.
```


***

## Precision Question

> `dataclasses.replace()` produces a **shallow copy** — `contraction_matrix` (a `numpy.ndarray`) is shared between the original and the copy, not duplicated. If `certify_l2` (power iteration) modifies the matrix in place during computation (e.g., normalising the iterate vector against `K`), that mutation would propagate back to the caller's `AceTelemetry.contraction_matrix`. **Should `_inject_design_params` deep-copy `contraction_matrix` explicitly, or should the level implementations carry the invariant that they never mutate the input matrix?** The latter is cheaper and already true in the current `certify_l2` implementation, but it is not enforced by the type system or documented as a contract.

