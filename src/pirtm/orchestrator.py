from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass

from .audit import AuditChain
from .qari import QARIConfig, QARISession
from .types import Certificate


@dataclass(frozen=True)
class SessionDescriptor:
    session_id: str
    config: QARIConfig
    created_at: float
    status: str


@dataclass(frozen=True)
class AggregatedCertificate:
    session_ids: list[str]
    individual_certs: list[Certificate]
    all_certified: bool
    q_max_global: float
    margin_min: float
    aggregate_hash: str


@dataclass
class SessionSnapshot:
    session_id: str
    config_dict: dict
    step_count: int
    infos: list[dict]
    epsilon: float
    audit_events: list[dict]
    snapshot_time: float


class SessionOrchestrator:
    def __init__(self):
        self._sessions: dict[str, QARISession] = {}
        self._descriptors: dict[str, SessionDescriptor] = {}
        self._master_audit = AuditChain()

    def register(self, session_id: str, config: QARIConfig, **session_kwargs) -> QARISession:
        if session_id in self._sessions:
            raise ValueError(f"Session '{session_id}' already registered")

        session = QARISession(config, **session_kwargs)
        self._sessions[session_id] = session
        self._descriptors[session_id] = SessionDescriptor(
            session_id=session_id,
            config=config,
            created_at=time.time(),
            status="active",
        )
        return session

    def get(self, session_id: str) -> QARISession:
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' not found")
        return self._sessions[session_id]

    def list_sessions(self, status: str | None = None) -> list[SessionDescriptor]:
        values = list(self._descriptors.values())
        if status is None:
            return values
        return [desc for desc in values if desc.status == status]

    def aggregate_certificates(
        self,
        session_ids: list[str] | None = None,
        tail_norm: float = 0.0,
    ) -> AggregatedCertificate:
        if session_ids is None:
            session_ids = [
                sid for sid, desc in self._descriptors.items() if desc.status in ("active", "completed")
            ]

        certs: list[Certificate] = []
        for session_id in session_ids:
            if session_id not in self._sessions:
                raise KeyError(f"Session '{session_id}' not found")
            certs.append(self._sessions[session_id].certify(tail_norm=tail_norm))

        cert_hashes: list[str] = []
        for cert in certs:
            canonical = json.dumps(asdict(cert), sort_keys=True, separators=(",", ":"), default=str)
            cert_hashes.append(hashlib.sha256(canonical.encode("utf-8")).hexdigest())

        aggregate_hash = hashlib.sha256("".join(cert_hashes).encode("utf-8")).hexdigest()

        self._master_audit.append_payload(
            {
                "type": "aggregate_certificate",
                "session_ids": session_ids,
                "all_certified": all(cert.certified for cert in certs),
                "aggregate_hash": aggregate_hash,
            }
        )

        q_maxes = [float(cert.details.get("max_q", 0.0)) for cert in certs]
        margins = [float(cert.margin) for cert in certs]
        return AggregatedCertificate(
            session_ids=list(session_ids),
            individual_certs=certs,
            all_certified=all(cert.certified for cert in certs),
            q_max_global=max(q_maxes) if q_maxes else 0.0,
            margin_min=min(margins) if margins else 0.0,
            aggregate_hash=aggregate_hash,
        )

    def pause(self, session_id: str) -> SessionSnapshot:
        session = self.get(session_id)
        descriptor = self._descriptors[session_id]

        config_dict = asdict(session.config)
        if "emission_policy" in config_dict and hasattr(config_dict["emission_policy"], "value"):
            config_dict["emission_policy"] = config_dict["emission_policy"].value

        snapshot = SessionSnapshot(
            session_id=session_id,
            config_dict=config_dict,
            step_count=session.step_count,
            infos=[asdict(info) for info in session.infos],
            epsilon=session.current_epsilon,
            audit_events=session.audit_chain.export() if session.audit_chain is not None else [],
            snapshot_time=time.time(),
        )

        self._descriptors[session_id] = SessionDescriptor(
            session_id=session_id,
            config=descriptor.config,
            created_at=descriptor.created_at,
            status="paused",
        )
        return snapshot

    def complete(self, session_id: str) -> None:
        if session_id not in self._descriptors:
            raise KeyError(f"Session '{session_id}' not found")
        descriptor = self._descriptors[session_id]
        self._descriptors[session_id] = SessionDescriptor(
            session_id=session_id,
            config=descriptor.config,
            created_at=descriptor.created_at,
            status="completed",
        )

    def global_summary(self) -> dict:
        per_session = {sid: session.summary() for sid, session in self._sessions.items()}
        total_steps = sum(summary.get("steps", 0) for summary in per_session.values())
        total_projections = sum(summary.get("projected_count", 0) for summary in per_session.values())
        return {
            "total_sessions": len(self._sessions),
            "active": len([d for d in self._descriptors.values() if d.status == "active"]),
            "completed": len([d for d in self._descriptors.values() if d.status == "completed"]),
            "paused": len([d for d in self._descriptors.values() if d.status == "paused"]),
            "total_steps": total_steps,
            "total_projections": total_projections,
            "master_audit_length": len(self._master_audit),
            "per_session": per_session,
        }

    @property
    def master_audit(self) -> AuditChain:
        return self._master_audit
