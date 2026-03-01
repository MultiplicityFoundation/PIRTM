from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from .ace.types import AceCertificate
    from .gate import GatedOutput
    from .types import Certificate, StepInfo


@dataclass(frozen=True)
class TelemetryEvent:
    timestamp: float
    event_type: str
    step_index: int
    payload: dict
    source: str = "pirtm"
    version: str = "0.2.0"

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)


class TelemetrySink(ABC):
    @abstractmethod
    def emit(self, event: TelemetryEvent) -> None:
        raise NotImplementedError

    def flush(self) -> None:
        return None

    def close(self) -> None:
        return None


class NullSink(TelemetrySink):
    def emit(self, event: TelemetryEvent) -> None:
        return None


class MemorySink(TelemetrySink):
    def __init__(self, max_events: int = 10_000):
        self.events: list[TelemetryEvent] = []
        self.max_events = max_events

    def emit(self, event: TelemetryEvent) -> None:
        if len(self.events) >= self.max_events:
            self.events.pop(0)
        self.events.append(event)

    def query(self, event_type: str | None = None) -> list[TelemetryEvent]:
        if event_type is None:
            return list(self.events)
        return [event for event in self.events if event.event_type == event_type]


class FileSink(TelemetrySink):
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._file = self.path.open("a", encoding="utf-8")

    def emit(self, event: TelemetryEvent) -> None:
        self._file.write(event.to_json() + "\n")

    def flush(self) -> None:
        self._file.flush()

    def close(self) -> None:
        self._file.close()


class CallbackSink(TelemetrySink):
    def __init__(self, callback: Callable[[TelemetryEvent], None]):
        self.callback = callback

    def emit(self, event: TelemetryEvent) -> None:
        self.callback(event)


@dataclass
class AlertRule:
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
    def __init__(
        self,
        sinks: Sequence[TelemetrySink] | None = None,
        alerts: Sequence[AlertRule] | None = None,
    ):
        self.sinks = list(sinks) if sinks is not None else [NullSink()]
        self.alerts = list(alerts) if alerts is not None else []

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

    def emit_certificate(self, cert: Certificate | AceCertificate) -> None:
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


def projection_rate_alert(
    window: int = 10,
    threshold: float = 0.5,
    action: Callable[[TelemetryEvent], None] | None = None,
) -> AlertRule:
    recent: list[bool] = []

    def condition(event: TelemetryEvent) -> bool:
        if event.event_type != "step":
            return False
        recent.append(bool(event.payload.get("projected", False)))
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
    def condition(event: TelemetryEvent) -> bool:
        if event.event_type != "step":
            return False
        return float(event.payload.get("q", 0.0)) > threshold

    return AlertRule(
        name=f"q_divergence>{threshold}",
        condition=condition,
        action=action or (lambda e: None),
    )
