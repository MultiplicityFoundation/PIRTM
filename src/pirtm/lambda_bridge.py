from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from .audit import AuditChain


@dataclass(frozen=True)
class LambdaTraceEvent:
    schema_id: str
    event_type: str
    sequence: int
    chain_hash: str
    payload: dict[str, Any]
    capability_token: str
    timestamp: float
    source: str


@dataclass(frozen=True)
class SubmissionReceipt:
    batch_id: str
    events_submitted: int
    merkle_root: str
    status: str
    timestamp: float
    poseidon_merkle_root: str | None = None


class LambdaTraceBridge:
    SCHEMA_STEP = "pirtm.step.v1"
    SCHEMA_CERTIFICATE = "pirtm.certificate.v1"
    SCHEMA_GATE = "pirtm.gate.v1"
    SCHEMA_AGGREGATE = "pirtm.aggregate.v1"

    def __init__(
        self,
        session_id: str,
        capability_token: str = "",
        submit_fn: Callable[[list[dict[str, Any]]], SubmissionReceipt] | None = None,
    ):
        self.session_id = session_id
        self.capability_token = capability_token
        self._submit_fn = submit_fn
        self._pending: list[LambdaTraceEvent] = []

    def translate(self, chain: AuditChain) -> list[LambdaTraceEvent]:
        events: list[LambdaTraceEvent] = []
        for audit_event in chain:
            payload = json.loads(audit_event.payload_json)
            event_name = str(payload.get("type", "unknown"))
            schema_id = {
                "step": self.SCHEMA_STEP,
                "certificate": self.SCHEMA_CERTIFICATE,
                "gate": self.SCHEMA_GATE,
                "aggregate_certificate": self.SCHEMA_AGGREGATE,
            }.get(event_name, f"pirtm.{event_name}.v1")
            trace_event = LambdaTraceEvent(
                schema_id=schema_id,
                event_type=f"pirtm.{event_name}",
                sequence=audit_event.sequence,
                chain_hash=audit_event.chain_hash,
                payload=payload,
                capability_token=self.capability_token,
                timestamp=time.time(),
                source=f"pirtm:{self.session_id}",
            )
            events.append(trace_event)

        self._pending.extend(events)
        return events

    def batch_submit(self) -> SubmissionReceipt:
        if not self._pending:
            return SubmissionReceipt(
                batch_id="empty",
                events_submitted=0,
                merkle_root="0" * 64,
                poseidon_merkle_root="0" * 64,
                status="empty",
                timestamp=time.time(),
            )

        hashes = [event.chain_hash for event in self._pending]
        merkle_root = self._compute_merkle_root(hashes)
        poseidon_merkle_root = self._compute_poseidon_merkle_root(hashes)
        batch_id = hashlib.sha256(
            f"{self.session_id}:{merkle_root}:{time.time()}".encode()
        ).hexdigest()[:16]

        payload = [
            {
                "schema_id": event.schema_id,
                "event_type": event.event_type,
                "sequence": event.sequence,
                "chain_hash": event.chain_hash,
                "payload": event.payload,
                "capability_token": event.capability_token,
                "timestamp": event.timestamp,
                "source": event.source,
            }
            for event in self._pending
        ]

        if self._submit_fn is not None:
            receipt = self._submit_fn(payload)
        else:
            receipt = SubmissionReceipt(
                batch_id=batch_id,
                events_submitted=len(self._pending),
                merkle_root=merkle_root,
                poseidon_merkle_root=poseidon_merkle_root,
                status="dry_run",
                timestamp=time.time(),
            )

        if receipt.status != "rejected":
            self._pending.clear()
        return receipt

    @staticmethod
    def _compute_merkle_root(hashes: list[str]) -> str:
        if not hashes:
            return "0" * 64

        layer = list(hashes)
        while len(layer) > 1:
            next_layer: list[str] = []
            for index in range(0, len(layer), 2):
                left = layer[index]
                right = layer[index + 1] if index + 1 < len(layer) else left
                next_layer.append(hashlib.sha256((left + right).encode("utf-8")).hexdigest())
            layer = next_layer

        return layer[0]

    @staticmethod
    def _poseidon_compat_hash(value: str) -> str:
        return hashlib.sha256(f"poseidon:{value}".encode()).hexdigest()

    @classmethod
    def _compute_poseidon_merkle_root(cls, hashes: list[str]) -> str:
        if not hashes:
            return "0" * 64

        layer = [cls._poseidon_compat_hash(value) for value in hashes]
        while len(layer) > 1:
            next_layer: list[str] = []
            for index in range(0, len(layer), 2):
                left = layer[index]
                right = layer[index + 1] if index + 1 < len(layer) else left
                next_layer.append(cls._poseidon_compat_hash(left + right))
            layer = next_layer
        return layer[0]

    @property
    def pending_count(self) -> int:
        return len(self._pending)
