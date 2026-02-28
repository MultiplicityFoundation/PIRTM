import json
import time

from pirtm.gate import GatedOutput
from pirtm.telemetry import (
    AlertRule,
    CallbackSink,
    FileSink,
    MemorySink,
    NullSink,
    TelemetryBus,
    TelemetryEvent,
)
from pirtm.types import Certificate, StepInfo


def _info(projected: bool = False, q: float = 0.4) -> StepInfo:
    return StepInfo(step=0, q=q, epsilon=0.05, nXi=0.2, nLam=0.2, projected=projected, residual=0.1)


def test_bus_defaults_to_null_sink():
    bus = TelemetryBus()
    assert len(bus.sinks) == 1
    assert isinstance(bus.sinks[0], NullSink)


def test_memory_sink_query_and_dispatch():
    sink = MemorySink()
    seen = []
    cb = CallbackSink(lambda e: seen.append(e.event_type))
    bus = TelemetryBus(sinks=[sink, cb])

    bus.emit_step(0, _info())
    bus.emit_certificate(Certificate(certified=True, margin=0.1, tail_bound=0.0))

    assert len(sink.query()) == 2
    assert len(sink.query("step")) == 1
    assert seen == ["step", "certificate"]


def test_filesink_writes_json_lines(tmp_path):
    path = tmp_path / "telemetry.jsonl"
    sink = FileSink(path)
    event = TelemetryEvent(time.time(), "step", 0, {"q": 0.4})
    sink.emit(event)
    sink.flush()
    sink.close()

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["event_type"] == "step"


def test_alert_rule_cooldown_respected():
    fired = []

    rule = AlertRule(
        name="high_q",
        condition=lambda e: e.event_type == "step" and e.payload.get("q", 0.0) > 0.9,
        action=lambda e: fired.append(e.step_index),
        cooldown_seconds=0.5,
    )
    sink = MemorySink()
    bus = TelemetryBus(sinks=[sink], alerts=[rule])

    bus.emit_step(0, _info(projected=True, q=0.96))
    bus.emit_step(1, _info(projected=True, q=0.97))
    assert fired == [0]


def test_emit_gate_is_json_serializable():
    sink = MemorySink()
    bus = TelemetryBus(sinks=[sink])
    info = _info(projected=True)
    output = GatedOutput(
        X_next=0,
        info=info,
        emitted=False,
        policy_applied="suppress",
        suppression_reason="projection_triggered",
    )
    bus.emit_gate(0, output)
    rendered = sink.events[0].to_json()
    decoded = json.loads(rendered)
    assert decoded["event_type"] == "gate"
