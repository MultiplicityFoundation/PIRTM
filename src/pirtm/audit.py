from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from .ace.types import AceCertificate
from .types import Certificate, StepInfo


@dataclass(frozen=True)
class AuditEvent:
    sequence: int
    event_hash: str
    chain_hash: str
    payload_json: str


class AuditChain:
    GENESIS_HASH = "0" * 64

    def __init__(self):
        self._events: list[AuditEvent] = []
        self._head: str = self.GENESIS_HASH

    def append_step(self, info: StepInfo) -> AuditEvent:
        payload = {
            "type": "step",
            "step": info.step,
            "q": float(info.q),
            "epsilon": float(info.epsilon),
            "nXi": float(info.nXi),
            "nLam": float(info.nLam),
            "projected": bool(info.projected),
            "residual": float(info.residual),
        }
        return self._append(payload)

    def append_certificate(self, cert: Certificate | AceCertificate) -> AuditEvent:
        payload = {
            "type": "certificate",
            "certified": bool(cert.certified),
            "margin": float(cert.margin),
            "q_max": cert.details.get("max_q"),
            "tail_bound": float(cert.tail_bound),
        }
        return self._append(payload)

    def append_gate(self, step_index: int, emitted: bool, policy: str, reason: str) -> AuditEvent:
        payload = {
            "type": "gate",
            "step": int(step_index),
            "emitted": bool(emitted),
            "policy": str(policy),
            "reason": str(reason),
        }
        return self._append(payload)

    def append_payload(self, payload: dict) -> AuditEvent:
        return self._append(payload)

    def _append(self, payload: dict) -> AuditEvent:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        event_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        chain_hash = hashlib.sha256((self._head + event_hash).encode("utf-8")).hexdigest()

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
        head = self.GENESIS_HASH
        for event in self._events:
            recomputed_event_hash = hashlib.sha256(event.payload_json.encode("utf-8")).hexdigest()
            if recomputed_event_hash != event.event_hash:
                return False
            expected_chain_hash = hashlib.sha256((head + event.event_hash).encode("utf-8")).hexdigest()
            if expected_chain_hash != event.chain_hash:
                return False
            head = event.chain_hash
        return True

    def export(self) -> list[dict]:
        return [asdict(event) for event in self._events]

    @property
    def head(self) -> str:
        return self._head

    @property
    def length(self) -> int:
        return len(self._events)

    def __iter__(self):
        return iter(self._events)

    def __len__(self) -> int:
        return len(self._events)
