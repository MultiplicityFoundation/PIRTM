# PIRTM Tier 6: Emission Gating, Streaming Telemetry, and Q-ARI Adapter — Expanded Specification

## Problem Statement

After Tiers 1-5, PIRTM is an installable, tested, documented, governed, conformance-certified, and release-hardened package. Three capabilities remain unimplemented:

1. **No emission gating.** The COVENANT's conformance plan (Section 5.3) requires that "outputs/actions are suppressed/nullified when predicates fail" and that "no information leakage via side channels" occurs in default configuration. Currently, `step()` returns `X_next` unconditionally — even when projection fires, the caller receives the projected output. There is no silent-path mode where predicate failure produces a null output. DRMM's `EthicalModulator` applies a `tanh` saturation but has no concept of suppression.

2. **No streaming telemetry.** The `Monitor` class stores `MonitorRecord` entries in memory and exposes `summary()` and `last()`. But there is no mechanism for real-time telemetry — push to external sinks, streaming iteration, threshold-triggered alerts, or structured logging compatible with Lambda-Proof's audit event chain. Lambda-Proof has an extensive audit infrastructure (Audit Event Chain with Merkle Checkpoints, Λ-trace) that PIRTM cannot currently feed.

3. **No Q-ARI adapter.** PIRTM is the mathematical engine. Q-ARI (Quantum Adaptive Recursive Intelligence) is the application layer that consumes it. No adapter exists to translate Q-ARI's inference loop into PIRTM's contractive recurrence. DRMM's `feedback_loops.py` has an `EntropicFeedbackLoop` and `ConvergenceController` that should delegate to PIRTM but do not.

Tier 6 closes all three gaps across 5 issues (#31-#35).

***

## Deliverable Inventory

| Issue | Deliverable | File(s) | Purpose |
|-------|-------------|---------|---------|
| #31 | Emission gate | `src/pirtm/gate.py` | Silent-path suppression when predicates fail |
| #32 | Streaming telemetry | `src/pirtm/telemetry.py` | Push-based sink protocol, structured events, alert hooks |
| #33 | Audit bridge | `src/pirtm/audit.py` | Merkle-chained trace events for Lambda-Proof Λ-trace |
| #34 | Q-ARI adapter | `src/pirtm/qari.py` | Map Q-ARI inference loop to contractive recurrence |
| #35 | DRMM feedback upgrade | `drmm/adapters/feedback_bridge.py` | Replace ad-hoc feedback loops with gated PIRTM pipeline |

***

## Issue #31: Emission Gate (`src/pirtm/gate.py`)

### Problem Statement

The COVENANT's Emission Gating requirement (Section 5.3) states: "Action tensors/outputs are suppressed or nullified when predicates fail". The current `step()` function always returns a valid `X_next` even when projection was triggered — meaning the caller cannot distinguish between a clean step and a remediated step that should have been suppressed.

The DRMM `EthicalModulator` applies `X - lambda * tanh(X)` as a "soft ethical barrier". This is saturation, not suppression. It attenuates without nullifying. It does not know about \( q_t \) or the contraction predicate.

### Proposed Architecture

A `GatedStep` wrapper that interposes between `step()` and the caller, implementing three emission policies:

```python
# src/pirtm/gate.py

"""Emission gating: suppress output when contraction predicate fails."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Callable

import numpy as np

from .recurrence import step
from .types import StepInfo


class EmissionPolicy(enum.Enum):
    """Controls what happens when the contraction predicate fails."""
    PASS_THROUGH = "pass_through"   # Tier 0-5 behavior: return projected X
    SUPPRESS = "suppress"           # Return zero vector (silent path)
    HOLD = "hold"                   # Return previous X (freeze in place)
    ATTENUATE = "attenuate"         # Scale output by margin distance


@dataclass(frozen=True)
class GatedOutput:
    """Result of a gated step."""
    X_next: np.ndarray
    info: StepInfo
    emitted: bool           # True if output was passed through
    policy_applied: str     # Which policy was applied
    suppression_reason: str # Empty if emitted


class EmissionGate:
    """Wraps step() with predicate-aware emission control.

    The gate evaluates two predicates after each step:
    1. Contraction predicate: q_t < 1 - epsilon (from step())
    2. Custom predicate: caller-supplied function on (X_next, info)

    If either predicate fails, the emission policy determines the output.
    """

    def __init__(
        self,
        policy: EmissionPolicy = EmissionPolicy.SUPPRESS,
        custom_predicate: Callable[[np.ndarray, StepInfo], bool] | None = None,
        attenuation_floor: float = 0.01,
    ):
        self.policy = policy
        self.custom_predicate = custom_predicate
        self.attenuation_floor = attenuation_floor

    def __call__(
        self,
        X_t: np.ndarray,
        Xi_t: np.ndarray,
        Lam_t: np.ndarray,
        T: Callable,
        G_t: np.ndarray,
        P: Callable,
        *,
        epsilon: float = 0.05,
        op_norm_T: float = 1.0,
    ) -> GatedOutput:
        # Execute the underlying step
        X_next, info = step(X_t, Xi_t, Lam_t, T, G_t, P,
                           epsilon=epsilon, op_norm_T=op_norm_T)

        # Evaluate predicates
        contraction_ok = not info.projected  # Clean step, no projection needed
        custom_ok = True
        if self.custom_predicate is not None:
            custom_ok = self.custom_predicate(X_next, info)

        if contraction_ok and custom_ok:
            return GatedOutput(
                X_next=X_next,
                info=info,
                emitted=True,
                policy_applied="none",
                suppression_reason="",
            )

        # Predicate failed — apply emission policy
        reason = []
        if not contraction_ok:
            reason.append(f"projection_triggered(q={info.q:.4f})")
        if not custom_ok:
            reason.append("custom_predicate_failed")

        if self.policy == EmissionPolicy.PASS_THROUGH:
            return GatedOutput(
                X_next=X_next,
                info=info,
                emitted=True,
                policy_applied="pass_through",
                suppression_reason="; ".join(reason),
            )

        elif self.policy == EmissionPolicy.SUPPRESS:
            return GatedOutput(
                X_next=np.zeros_like(X_t),
                info=info,
                emitted=False,
                policy_applied="suppress",
                suppression_reason="; ".join(reason),
            )

        elif self.policy == EmissionPolicy.HOLD:
            return GatedOutput(
                X_next=X_t.copy(),
                info=info,
                emitted=False,
                policy_applied="hold",
                suppression_reason="; ".join(reason),
            )

        elif self.policy == EmissionPolicy.ATTENUATE:
            # Scale by how close q is to the safe boundary
            margin = max(1.0 - epsilon - info.q, 0.0)
            scale = max(margin, self.attenuation_floor)
            return GatedOutput(
                X_next=scale * X_next,
                info=info,
                emitted=True,
                policy_applied=f"attenuate(scale={scale:.4f})",
                suppression_reason="; ".join(reason),
            )

        raise ValueError(f"Unknown policy: {self.policy}")


def gated_run(
    X0: np.ndarray,
    Xi_seq: list[np.ndarray],
    Lam_seq: list[np.ndarray],
    G_seq: list[np.ndarray],
    T: Callable,
    P: Callable,
    gate: EmissionGate,
    *,
    epsilon: float = 0.05,
    op_norm_T: float = 1.0,
) -> tuple[np.ndarray, list[np.ndarray], list[GatedOutput]]:
    """Run the full recurrence through an emission gate.

    Returns: (X_final, history, gated_outputs)
    """
    X = X0.copy()
    history = [X.copy()]
    outputs = []

    for Xi, Lam, G in zip(Xi_seq, Lam_seq, G_seq):
        result = gate(X, Xi, Lam, T, G, P,
                     epsilon=epsilon, op_norm_T=op_norm_T)
        X = result.X_next
        history.append(X.copy())
        outputs.append(result)

    return X, history, outputs
```

### Emission Policy Semantics

| Policy | Predicate Fails | Output | Use Case |
|--------|----------------|--------|----------|
| `PASS_THROUGH` | Return projected X | Normal `X_next` | Backward-compatible (Tier 0-5 behavior) |
| `SUPPRESS` | Return zero vector | `np.zeros_like(X)` | COVENANT silent-path compliance |
| `HOLD` | Return previous X | `X_t` (frozen) | Safety-critical: freeze on violation |
| `ATTENUATE` | Scale by margin | `margin * X_next` | Graceful degradation |

### Custom Predicates

The gate supports caller-supplied predicates beyond contraction:

```python
# Example: Suppress if residual is too large (divergence detector)
def residual_check(X_next: np.ndarray, info: StepInfo) -> bool:
    return info.residual < 1.0

# Example: Suppress if norm exceeds safety envelope
def norm_check(X_next: np.ndarray, info: StepInfo) -> bool:
    return np.linalg.norm(X_next) < 100.0

gate = EmissionGate(
    policy=EmissionPolicy.SUPPRESS,
    custom_predicate=lambda X, info: residual_check(X, info) and norm_check(X, info),
)
```

### Acceptance Criteria

- `EmissionGate` with `SUPPRESS` policy returns zero vector when `info.projected == True`
- `EmissionGate` with `HOLD` policy returns `X_t` (input, not output) when predicate fails
- `EmissionGate` with `PASS_THROUGH` returns identical output to bare `step()`
- `gated_run()` produces a trace of `GatedOutput` objects with per-step suppression metadata
- Custom predicates compose with the contraction predicate (both must pass)
- No output leakage: when `emitted=False`, the `X_next` field contains only the policy-determined value (zero or held), not the true computed value
- Module has zero external dependencies beyond numpy

### Estimated Size

~200 LOC.

***

## Issue #32: Streaming Telemetry (`src/pirtm/telemetry.py`)

### Problem Statement

The existing `Monitor` class is a pull-based in-memory buffer. It stores `MonitorRecord` entries and provides `summary()` and `last()`. This works for notebooks but fails for:

- **Real-time dashboards**: No push mechanism
- **Alerting**: No threshold-triggered callbacks
- **External sinks**: No protocol for writing to files, databases, or message queues
- **Audit chains**: No structured events compatible with Lambda-Proof's Λ-trace format

### Proposed Architecture

A sink-based telemetry system that the existing `Monitor` can plug into:

```python
# src/pirtm/telemetry.py

"""Push-based telemetry with pluggable sinks and alert hooks."""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Callable, Sequence

from .types import StepInfo, Certificate
from .gate import GatedOutput


@dataclass(frozen=True)
class TelemetryEvent:
    """Structured telemetry event."""
    timestamp: float
    event_type: str           # "step", "certificate", "gate", "alert"
    step_index: int
    payload: dict
    source: str = "pirtm"
    version: str = "0.2.0"

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)


class TelemetrySink(ABC):
    """Abstract base class for telemetry sinks."""

    @abstractmethod
    def emit(self, event: TelemetryEvent) -> None:
        """Write a single event to the sink."""

    def flush(self) -> None:
        """Flush buffered events. Default: no-op."""

    def close(self) -> None:
        """Release resources. Default: no-op."""


class NullSink(TelemetrySink):
    """Discards all events. Used as default when no sink is configured."""
    def emit(self, event: TelemetryEvent) -> None:
        pass


class MemorySink(TelemetrySink):
    """Stores events in memory. Drop-in replacement for Monitor internals."""

    def __init__(self, max_events: int = 10_000):
        self.events: list[TelemetryEvent] = []
        self.max_events = max_events

    def emit(self, event: TelemetryEvent) -> None:
        if len(self.events) >= self.max_events:
            self.events.pop(0)  # Ring buffer behavior
        self.events.append(event)

    def query(self, event_type: str | None = None) -> list[TelemetryEvent]:
        if event_type is None:
            return list(self.events)
        return [e for e in self.events if e.event_type == event_type]


class FileSink(TelemetrySink):
    """Appends JSON-lines to a file. One event per line."""

    def __init__(self, path: str):
        self.path = path
        self._file = open(path, "a")

    def emit(self, event: TelemetryEvent) -> None:
        self._file.write(event.to_json() + "\n")

    def flush(self) -> None:
        self._file.flush()

    def close(self) -> None:
        self._file.close()


class CallbackSink(TelemetrySink):
    """Invokes a callback for each event. For custom integrations."""

    def __init__(self, callback: Callable[[TelemetryEvent], None]):
        self.callback = callback

    def emit(self, event: TelemetryEvent) -> None:
        self.callback(event)


@dataclass
class AlertRule:
    """Threshold-triggered alert."""
    name: str
    condition: Callable[[TelemetryEvent], bool]
    action: Callable[[TelemetryEvent], None]
    cooldown_seconds: float = 5.0
    _last_fired: float = field(default=0.0, init=False, repr=False)

    def evaluate(self, event: TelemetryEvent) -> None:
        now = time.monotonic()
        if now - self._last_fired < self.cooldown_seconds:
            return
        if self.condition(event):
            self.action(event)
            self._last_fired = now


class TelemetryBus:
    """Central telemetry dispatcher.

    Receives events from PIRTM operations and routes them
    to registered sinks and alert rules.
    """

    def __init__(
        self,
        sinks: Sequence[TelemetrySink] | None = None,
        alerts: Sequence[AlertRule] | None = None,
    ):
        self.sinks = list(sinks) if sinks else [NullSink()]
        self.alerts = list(alerts) if alerts else []

    def emit_step(self, step_index: int, info: StepInfo) -> None:
        event = TelemetryEvent(
            timestamp=time.time(),
            event_type="step",
            step_index=step_index,
            payload=asdict(info),
        )
        self._dispatch(event)

    def emit_gate(self, step_index: int, output: GatedOutput) -> None:
        event = TelemetryEvent(
            timestamp=time.time(),
            event_type="gate",
            step_index=step_index,
            payload={
                "emitted": output.emitted,
                "policy_applied": output.policy_applied,
                "suppression_reason": output.suppression_reason,
                "q": output.info.q,
            },
        )
        self._dispatch(event)

    def emit_certificate(self, cert: Certificate) -> None:
        event = TelemetryEvent(
            timestamp=time.time(),
            event_type="certificate",
            step_index=-1,
            payload=asdict(cert),
        )
        self._dispatch(event)

    def emit_alert(self, name: str, detail: dict) -> None:
        event = TelemetryEvent(
            timestamp=time.time(),
            event_type="alert",
            step_index=-1,
            payload={"alert_name": name, **detail},
        )
        self._dispatch(event)

    def _dispatch(self, event: TelemetryEvent) -> None:
        for sink in self.sinks:
            sink.emit(event)
        for rule in self.alerts:
            rule.evaluate(event)

    def flush(self) -> None:
        for sink in self.sinks:
            sink.flush()

    def close(self) -> None:
        for sink in self.sinks:
            sink.close()
```

### Built-in Alert Rules

```python
# Pre-built alert factories

def projection_rate_alert(
    window: int = 10,
    threshold: float = 0.5,
    action: Callable[[TelemetryEvent], None] | None = None,
) -> AlertRule:
    """Alert when projection rate exceeds threshold over a sliding window."""
    recent: list[bool] = []

    def condition(event: TelemetryEvent) -> bool:
        if event.event_type != "step":
            return False
        recent.append(event.payload.get("projected", False))
        if len(recent) > window:
            recent.pop(0)
        rate = sum(recent) / len(recent)
        return rate > threshold

    return AlertRule(
        name=f"projection_rate>{threshold:.0%}",
        condition=condition,
        action=action or (lambda e: None),
    )


def q_divergence_alert(
    threshold: float = 0.95,
    action: Callable[[TelemetryEvent], None] | None = None,
) -> AlertRule:
    """Alert when q_t approaches 1.0 (near-loss of contraction)."""
    def condition(event: TelemetryEvent) -> bool:
        if event.event_type != "step":
            return False
        return event.payload.get("q", 0.0) > threshold

    return AlertRule(
        name=f"q_divergence>{threshold}",
        condition=condition,
        action=action or (lambda e: None),
    )
```

### Privacy Invariant

The telemetry system satisfies COVENANT Privacy Profile by design:

- **Default sink is `NullSink`** — zero telemetry unless explicitly configured
- **No network calls** — `FileSink` writes local; `CallbackSink` delegates to caller
- **No user identifiers** — `TelemetryEvent` contains only numerical state metadata
- **No automatic reporting** — bus never phones home; caller must attach sinks

### Acceptance Criteria

- `NullSink` is the default (zero telemetry by default)
- `MemorySink` provides `query()` for filtering events by type
- `FileSink` writes valid JSON-lines (one JSON object per line)
- `AlertRule` respects cooldown (does not fire more than once per cooldown period)
- `TelemetryBus` dispatches to all registered sinks
- Events are serializable to JSON without loss
- Zero network dependencies; zero external imports beyond stdlib + numpy

### Estimated Size

~300 LOC.

***

## Issue #33: Audit Bridge (`src/pirtm/audit.py`)

### Problem Statement

Lambda-Proof maintains an Audit Event Chain with Merkle Checkpoints — a tamper-evident log where each event is hashed with its predecessor to form a chain. PIRTM's `StepInfo` and `Certificate` types contain the right data but produce no Merkle commitments. The COVENANT Integrity Profile requires "canonical ordering and hashing of trace fields" and "non-collision fingerprinting for snapshots/events".

### Proposed Architecture

```python
# src/pirtm/audit.py

"""Merkle-chained audit events for Lambda-Proof Λ-trace integration."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Sequence

from .types import StepInfo, Certificate


@dataclass(frozen=True)
class AuditEvent:
    """Single event in the audit chain."""
    sequence: int
    event_hash: str        # SHA-256 of canonical payload
    chain_hash: str        # SHA-256(prev_chain_hash + event_hash)
    payload_json: str      # Canonical JSON (sorted keys, deterministic)


class AuditChain:
    """Append-only Merkle-chained audit log for PIRTM traces.

    Each event is hashed with sorted-key JSON canonicalization.
    The chain hash links each event to its predecessor, forming
    a tamper-evident log compatible with Lambda-Proof's Λ-trace.
    """

    GENESIS_HASH = "0" * 64  # 256-bit zero

    def __init__(self):
        self._events: list[AuditEvent] = []
        self._head: str = self.GENESIS_HASH

    def append_step(self, info: StepInfo) -> AuditEvent:
        """Append a step event to the chain."""
        payload = {
            "type": "step",
            "step": info.step,
            "q": float(info.q),
            "epsilon": float(info.epsilon),
            "nXi": float(info.nXi),
            "nLam": float(info.nLam),
            "projected": info.projected,
            "residual": float(info.residual),
        }
        return self._append(payload)

    def append_certificate(self, cert: Certificate) -> AuditEvent:
        """Append a certificate event to the chain."""
        payload = {
            "type": "certificate",
            "certified": cert.certified,
            "margin": float(cert.margin),
            "q_max": float(cert.q_max) if hasattr(cert, 'q_max') else None,
            "tail_bound": float(cert.tail_bound),
        }
        return self._append(payload)

    def append_gate(self, step_index: int, emitted: bool,
                    policy: str, reason: str) -> AuditEvent:
        """Append a gate decision event to the chain."""
        payload = {
            "type": "gate",
            "step": step_index,
            "emitted": emitted,
            "policy": policy,
            "reason": reason,
        }
        return self._append(payload)

    def _append(self, payload: dict) -> AuditEvent:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        event_hash = hashlib.sha256(canonical.encode()).hexdigest()
        chain_hash = hashlib.sha256(
            (self._head + event_hash).encode()
        ).hexdigest()

        event = AuditEvent(
            sequence=len(self._events),
            event_hash=event_hash,
            chain_hash=chain_hash,
            payload_json=canonical,
        )
        self._events.append(event)
        self._head = chain_hash
        return event

    def verify(self) -> bool:
        """Verify the entire chain's Merkle integrity."""
        head = self.GENESIS_HASH
        for event in self._events:
            expected_chain = hashlib.sha256(
                (head + event.event_hash).encode()
            ).hexdigest()
            if expected_chain != event.chain_hash:
                return False
            # Verify event_hash matches payload
            recomputed = hashlib.sha256(
                event.payload_json.encode()
            ).hexdigest()
            if recomputed != event.event_hash:
                return False
            head = event.chain_hash
        return True

    def export(self) -> list[dict]:
        """Export chain as list of dicts for Λ-trace submission."""
        return [asdict(e) for e in self._events]

    @property
    def head(self) -> str:
        """Current chain head hash."""
        return self._head

    @property
    def length(self) -> int:
        return len(self._events)

    def __iter__(self):
        return iter(self._events)

    def __len__(self):
        return len(self._events)
```

### Λ-Trace Submission Format

The `export()` method produces a JSON array compatible with Lambda-Proof's audit event schema:

```json
[
  {
    "sequence": 0,
    "event_hash": "a1b2c3...",
    "chain_hash": "d4e5f6...",
    "payload_json": "{\"epsilon\":0.05,\"nLam\":0.2,\"nXi\":0.3,\"projected\":false,\"q\":0.46,\"residual\":0.001234,\"step\":0,\"type\":\"step\"}"
  },
  {
    "sequence": 1,
    "event_hash": "g7h8i9...",
    "chain_hash": "j0k1l2...",
    "payload_json": "{\"certified\":true,\"margin\":0.49,\"q_max\":0.46,\"tail_bound\":0.002,\"type\":\"certificate\"}"
  }
]
```

### Properties

- **Deterministic**: Same inputs always produce same hashes (sorted keys, compact separators)
- **Tamper-evident**: Altering any event breaks `verify()` for all subsequent events
- **Append-only**: No mutation or deletion API
- **Self-contained**: Uses only `hashlib` from stdlib — no cryptographic dependencies

### Acceptance Criteria

- `AuditChain.verify()` returns `True` for an unmodified chain
- `AuditChain.verify()` returns `False` if any event's `payload_json` is altered
- `AuditChain.verify()` returns `False` if any event's `chain_hash` is altered
- `export()` produces valid JSON parseable by `json.loads()`
- Canonical JSON uses `sort_keys=True` and `separators=(",", ":")` for determinism
- Genesis hash is `"0" * 64`
- Chain is iterable and has `len()`
- Zero external dependencies

### Estimated Size

~180 LOC.

***

## Issue #34: Q-ARI Adapter (`src/pirtm/qari.py`)

### Problem Statement

Q-ARI (Quantum Adaptive Recursive Intelligence) represents the application layer where PIRTM's contractive recurrence governs an inference loop. The conceptual mapping:

| Q-ARI Concept | PIRTM Mapping |
|--------------|---------------|
| Inference state | \( X_t \) — state vector |
| Recursive operator | \( \Xi_t \) — parameter matrix |
| Adaptation weights | \( \Lambda_t \) — modulation matrix |
| Transform | \( T \) — bounded operator (e.g., neural layer) |
| External input / disturbance | \( G_t \) — gain vector |
| Safety constraint | \( \mathcal{P} \) — projector |
| Stability certificate | ACE certificate |
| Drift detection | \( q_t \) monitoring + adaptive epsilon |
| Emission control | Gate (suppress on predicate failure) |

No code currently implements this mapping. A developer building a Q-ARI system must manually assemble `step()`, `EmissionGate`, `AdaptiveMargin`, `Monitor`, and `AuditChain` calls. The adapter provides a single high-level class.

### Proposed Architecture

```python
# src/pirtm/qari.py

"""Q-ARI adapter: map inference loops to PIRTM's contractive recurrence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterator

import numpy as np

from .recurrence import step
from .certify import ace_certificate
from .adaptive import AdaptiveMargin
from .gate import EmissionGate, EmissionPolicy, GatedOutput
from .telemetry import TelemetryBus, NullSink
from .audit import AuditChain
from .types import StepInfo, Certificate


@dataclass
class QARIConfig:
    """Configuration for a Q-ARI inference session."""
    dim: int
    epsilon: float = 0.05
    op_norm_T: float = 1.0
    emission_policy: EmissionPolicy = EmissionPolicy.SUPPRESS
    adaptive: bool = True
    audit: bool = True
    max_steps: int = 1000
    convergence_tol: float = 1e-6


class QARISession:
    """A single Q-ARI inference session backed by PIRTM.

    Encapsulates the full pipeline:
    step → gate → adaptive margin → telemetry → audit

    Usage:
        config = QARIConfig(dim=8, epsilon=0.05)
        session = QARISession(config)

        # Define the inference operator
        T = lambda x: model.forward(x)  # Your inference function

        # Run inference loop
        X = initial_state
        for t, (Xi_t, Lam_t, G_t) in enumerate(parameter_stream):
            result = session.step(X, Xi_t, Lam_t, T, G_t)
            if result.emitted:
                X = result.X_next
                process_output(X)
            else:
                handle_suppression(result)

        # Get convergence certificate
        cert = session.certify()
        report = session.audit_chain.export()
    """

    def __init__(
        self,
        config: QARIConfig,
        projector: Callable[[np.ndarray], np.ndarray] | None = None,
        custom_predicate: Callable[[np.ndarray, StepInfo], bool] | None = None,
        telemetry: TelemetryBus | None = None,
    ):
        self.config = config
        self.P = projector or (lambda x: x)
        self._gate = EmissionGate(
            policy=config.emission_policy,
            custom_predicate=custom_predicate,
        )
        self._margin = AdaptiveMargin() if config.adaptive else None
        self._telemetry = telemetry or TelemetryBus()
        self._audit = AuditChain() if config.audit else None

        self._step_count = 0
        self._infos: list[StepInfo] = []
        self._epsilon = config.epsilon

    def step(
        self,
        X_t: np.ndarray,
        Xi_t: np.ndarray,
        Lam_t: np.ndarray,
        T: Callable,
        G_t: np.ndarray,
    ) -> GatedOutput:
        """Execute one gated inference step.

        Returns GatedOutput with emission decision.
        """
        if self._step_count >= self.config.max_steps:
            raise RuntimeError(
                f"QARISession exceeded max_steps ({self.config.max_steps})"
            )

        result = self._gate(
            X_t, Xi_t, Lam_t, T, G_t, self.P,
            epsilon=self._epsilon,
            op_norm_T=self.config.op_norm_T,
        )

        # Record telemetry
        self._infos.append(result.info)
        self._telemetry.emit_step(self._step_count, result.info)
        self._telemetry.emit_gate(self._step_count, result)

        # Audit chain
        if self._audit is not None:
            self._audit.append_step(result.info)
            self._audit.append_gate(
                self._step_count,
                result.emitted,
                result.policy_applied,
                result.suppression_reason,
            )

        # Adaptive margin
        if self._margin is not None:
            self._epsilon = self._margin.update(
                result.info.q,
                result.info.residual,
                self._epsilon,
            )

        self._step_count += 1
        return result

    def certify(self, tail_norm: float = 0.0) -> Certificate:
        """Build ACE certificate over all recorded steps."""
        if not self._infos:
            raise ValueError("No steps recorded. Call step() first.")
        cert = ace_certificate(self._infos, tail_norm=tail_norm)
        self._telemetry.emit_certificate(cert)
        if self._audit is not None:
            self._audit.append_certificate(cert)
        return cert

    @property
    def step_count(self) -> int:
        return self._step_count

    @property
    def current_epsilon(self) -> float:
        return self._epsilon

    @property
    def audit_chain(self) -> AuditChain | None:
        return self._audit

    @property
    def infos(self) -> list[StepInfo]:
        return list(self._infos)

    def summary(self) -> dict:
        """Summary statistics for the session."""
        if not self._infos:
            return {"steps": 0}
        qs = [i.q for i in self._infos]
        residuals = [i.residual for i in self._infos]
        projected = sum(1 for i in self._infos if i.projected)
        return {
            "steps": self._step_count,
            "q_max": max(qs),
            "q_min": min(qs),
            "q_mean": sum(qs) / len(qs),
            "residual_final": residuals[-1],
            "projected_count": projected,
            "projection_rate": projected / len(self._infos),
            "epsilon_current": self._epsilon,
            "audit_chain_length": len(self._audit) if self._audit else 0,
        }
```

### Acceptance Criteria

- `QARISession.step()` returns `GatedOutput` with emission decision
- `QARISession.certify()` returns `Certificate` from accumulated trace
- Adaptive margin updates epsilon after each step when enabled
- Audit chain records every step and gate decision when enabled
- `max_steps` guard prevents infinite loops
- `summary()` returns a dict with keys matching the specified schema
- `QARISession` is usable without telemetry (default `NullSink`)
- `QARISession` is usable without audit (config `audit=False`)
- Zero external dependencies beyond numpy

### Estimated Size

~250 LOC.

***

## Issue #35: DRMM Feedback Upgrade (`drmm/adapters/feedback_bridge.py`)

### Problem Statement

DRMM's `feedback_loops.py` contains three classes:

| Class | What It Does | Problem |
|-------|-------------|---------|
| `EntropicFeedbackLoop` | `X + alpha * t * (-log(\|X\| + eps))` | No contraction check, no projection, no certificate |
| `ConvergenceController` | `norm(X_new - X_old) < threshold` | No connection to \( q_t \); threshold is static |
| `EthicalModulator` | `X - lambda * tanh(X)` | Saturation, not suppression; no predicate awareness |

The Tier 5 adapter (`pirtm_bridge.py`) replaced `Xi.evolve()` and `recursive_tensor_update()`. This issue replaces the feedback loop classes with PIRTM-backed equivalents.

### Proposed Architecture

```python
# drmm/adapters/feedback_bridge.py

"""Replace DRMM feedback loops with PIRTM-backed gated pipeline."""

from __future__ import annotations

import warnings
from typing import Callable

import numpy as np
from pirtm.qari import QARISession, QARIConfig
from pirtm.gate import EmissionPolicy, GatedOutput
from pirtm.telemetry import TelemetryBus, MemorySink
from pirtm.audit import AuditChain


class DRMMInferenceLoop:
    """Drop-in replacement for EntropicFeedbackLoop + ConvergenceController
    + EthicalModulator, backed by PIRTM's Q-ARI session.

    Maps DRMM's entropy-driven feedback to PIRTM's contractive recurrence
    with emission gating and audit chain.
    """

    def __init__(
        self,
        dim: int,
        epsilon: float = 0.05,
        op_norm_T: float = 1.0,
        emission_policy: EmissionPolicy = EmissionPolicy.SUPPRESS,
        convergence_tol: float = 1e-3,
        audit: bool = True,
    ):
        config = QARIConfig(
            dim=dim,
            epsilon=epsilon,
            op_norm_T=op_norm_T,
            emission_policy=emission_policy,
            adaptive=True,
            audit=audit,
            convergence_tol=convergence_tol,
        )
        self._sink = MemorySink()
        self._bus = TelemetryBus(sinks=[self._sink])
        self._session = QARISession(config, telemetry=self._bus)

    def evolve(
        self,
        X: np.ndarray,
        Xi: np.ndarray,
        Lam: np.ndarray,
        T: Callable,
        G: np.ndarray | None = None,
    ) -> tuple[np.ndarray, GatedOutput]:
        """One gated evolution step. Replaces the entire
        EntropicFeedbackLoop.update() → EthicalModulator.apply() chain.
        """
        if G is None:
            G = np.zeros_like(X)
        result = self._session.step(X, Xi, Lam, T, G)
        return result.X_next, result

    def run(
        self,
        X0: np.ndarray,
        Xi_seq: list[np.ndarray],
        Lam_seq: list[np.ndarray],
        T: Callable,
        G_seq: list[np.ndarray] | None = None,
    ) -> dict:
        """Full evolution with certificate. Replaces the for-loop in
        DRMM's __main__ block.
        """
        N = len(Xi_seq)
        if G_seq is None:
            G_seq = [np.zeros_like(X0)] * N

        X = X0.copy()
        history = [X.copy()]
        outputs = []

        for Xi, Lam, G in zip(Xi_seq, Lam_seq, G_seq):
            X, result = self.evolve(X, Xi, Lam, T, G)
            history.append(X.copy())
            outputs.append(result)

        cert = self._session.certify()

        return {
            "X_final": X,
            "history": history,
            "outputs": outputs,
            "certificate": cert,
            "summary": self._session.summary(),
            "audit_export": self._session.audit_chain.export()
                if self._session.audit_chain else None,
        }

    @property
    def session(self) -> QARISession:
        return self._session

    @property
    def telemetry_events(self):
        return self._sink.events


# Legacy shims with deprecation warnings

class EntropicFeedbackLoop:
    """DEPRECATED: Use DRMMInferenceLoop instead."""

    def __init__(self, alpha: float = 0.1):
        warnings.warn(
            "EntropicFeedbackLoop is deprecated. Use DRMMInferenceLoop.",
            DeprecationWarning, stacklevel=2,
        )
        self.alpha = alpha

    def entropy_gradient(self, X):
        return -np.log(np.abs(X) + 1e-8)

    def update(self, X, t):
        return X + self.alpha * t * self.entropy_gradient(X)


class ConvergenceController:
    """DEPRECATED: Use PIRTM's residual tracking instead."""

    def __init__(self, threshold: float = 1e-3):
        warnings.warn(
            "ConvergenceController is deprecated. Use pirtm.recurrence.run().",
            DeprecationWarning, stacklevel=2,
        )
        self.threshold = threshold

    def is_converged(self, X_old, X_new):
        return np.linalg.norm(X_new - X_old) < self.threshold


class EthicalModulator:
    """DEPRECATED: Use EmissionGate with SUPPRESS policy instead."""

    def __init__(self, filter_strength: float = 0.05):
        warnings.warn(
            "EthicalModulator is deprecated. Use pirtm.gate.EmissionGate.",
            DeprecationWarning, stacklevel=2,
        )
        self.f = lambda x: np.tanh(x)
        self.lam = filter_strength

    def apply(self, X):
        return X - self.lam * self.f(X)
```

### Migration Map

| Old DRMM Pattern | New Pattern |
|-------------------|------------|
| `loop = EntropicFeedbackLoop(alpha=0.05)` → `loop.update(X, t)` | `session = DRMMInferenceLoop(dim=3)` → `session.evolve(X, Xi, Lam, T)` |
| `mod = EthicalModulator()` → `mod.apply(X)` | Absorbed into `EmissionGate.SUPPRESS` policy |
| `ctrl = ConvergenceController()` → `ctrl.is_converged(X_old, X_new)` | `session.run(...)["certificate"].certified` |
| Manual `for t in range(1, 11)` loop | `session.run(X0, Xi_seq, Lam_seq, T)` |

### Acceptance Criteria

- `DRMMInferenceLoop.evolve()` returns `(X_next, GatedOutput)`
- `DRMMInferenceLoop.run()` returns a dict with `certificate` and `audit_export`
- Legacy shims emit `DeprecationWarning` on instantiation
- Legacy shim behavior is identical to the original
- Telemetry events are accessible via `telemetry_events` property
- Audit chain is exportable and verifiable

### Estimated Size

~200 LOC.

***

## Execution Sequence

```
Tier 5 ──► Tier 6
              │
    ┌─────────┼──────────┐
    ▼         ▼          ▼
  #31 Gate  #32 Telem  #33 Audit
    │         │          │
    └─────────┼──────────┘
              ▼
          #34 Q-ARI Adapter
              │
              ▼
          #35 DRMM Feedback
```

### Dependencies

| Issue | Depends On | Rationale |
|-------|-----------|-----------|
| #31 Gate | Tier 1 (`step()` exists) | Wraps `step()` with emission control |
| #32 Telemetry | #31 (references `GatedOutput` type) | Emits gate events |
| #33 Audit | Tier 1 (`StepInfo`, `Certificate` types exist) | Chains step events |
| #34 Q-ARI | #31 + #32 + #33 (composes all three) | Unified session class |
| #35 DRMM Feedback | #34 (wraps Q-ARI session) | Top-level DRMM interface |

Issues #31, #32, and #33 are parallel (they share types but not implementations). Issue #34 follows all three. Issue #35 follows #34.

### Estimated Effort

| Issue | Deliverable | LOC (approx) | Time |
|-------|-------------|-------------|------|
| #31 — Gate | `gate.py` + tests | ~200 | 2-3 hours |
| #32 — Telemetry | `telemetry.py` + tests | ~300 | 3-4 hours |
| #33 — Audit | `audit.py` + tests | ~180 | 2-3 hours |
| #34 — Q-ARI | `qari.py` + tests | ~250 | 3-4 hours |
| #35 — DRMM Feedback | `feedback_bridge.py` + tests | ~200 | 2-3 hours |

**Total: ~1,130 LOC, 5 issues, 12-17 hours of implementation.**

***

## Post-Tier 6 State

After Tier 6, the PIRTM ecosystem reaches its full architectural scope:

- **Emission Gating**: Predicate failure produces a null output (silent path), not a potentially unsafe projected value — satisfying COVENANT Section 5.3
- **Streaming Telemetry**: Push-based events flow to pluggable sinks with threshold-triggered alerts, privacy-preserving by default (NullSink)
- **Audit Chain**: Merkle-chained, tamper-evident trace log compatible with Lambda-Proof's Λ-trace format
- **Q-ARI Session**: A single class composes gate + margin + telemetry + audit into an inference loop with a convergence certificate
- **DRMM Feedback**: The ad-hoc entropy loops and tanh modulators are replaced with certified, gated evolution — `DRMMInferenceLoop.run()` returns a certificate and an exportable audit chain

The full tier dependency chain: Tier 1 (installable) → Tier 2 (complete API) → Tier 3 (property tests) → Tier 4 (documentation) → Tier 5 (governance + CI) → **Tier 6 (emission gating + telemetry + Q-ARI)**.

The package is now both a standalone numerical engine and a first-class participant in the Multiplicity Foundation's COVENANT conformance ecosystem.