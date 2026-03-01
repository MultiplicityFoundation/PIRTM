from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from pirtm.conformance import ConformanceResult
from pirtm.gate import EmissionPolicy
from pirtm.lambda_bridge import LambdaTraceBridge
from pirtm.orchestrator import SessionOrchestrator
from pirtm.petc import PETCLedger
from pirtm.qari import QARIConfig
from pirtm.types import Certificate

from ..identity import bind_identity
from ..models import TranspileResult
from ..witness import build_witness
from .computation import _build_computation_mapping, _is_prime, _validate_descriptor, _vector

if TYPE_CHECKING:
    from ..spec import TranspileSpec


def _emission_policy(value: str) -> EmissionPolicy:
    for policy in EmissionPolicy:
        if policy.value == value:
            return policy
    raise ValueError(f"unsupported emission policy: {value}")


def _first_n_primes(count: int) -> list[int]:
    primes: list[int] = []
    value = 2
    while len(primes) < count:
        if _is_prime(value):
            primes.append(value)
        value += 1
    return primes


def _next_prime(value: int) -> int:
    candidate = max(2, value + 1)
    while not _is_prime(candidate):
        candidate += 1
    return candidate


def _read_descriptor(path: str, metadata: dict[str, Any]) -> dict[str, Any]:
    source = Path(path)
    if source.exists() and source.suffix.lower() == ".json":
        parsed = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise ValueError("workflow descriptor JSON must be an object")
        merged = dict(parsed)
        merged.update(metadata)
        return merged
    if metadata:
        return dict(metadata)
    raise ValueError("workflow requires JSON descriptor at input_ref or metadata payload")


def _collect_dependencies(step: dict[str, Any], dep_map: dict[str, list[str]]) -> list[str]:
    step_id = str(step["id"])
    listed = step.get("dependencies")
    if listed is not None:
        if not isinstance(listed, list):
            raise ValueError(f"dependencies for step '{step_id}' must be a list")
        return [str(item) for item in listed]
    return [str(item) for item in dep_map.get(step_id, [])]


def _topological_order(
    steps: list[dict[str, Any]], dep_map: dict[str, list[str]]
) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for step in steps:
        step_id = str(step.get("id", "")).strip()
        if not step_id:
            raise ValueError("every workflow step requires a non-empty 'id'")
        if step_id in by_id:
            raise ValueError(f"duplicate workflow step id: {step_id}")
        by_id[step_id] = step

    incoming: dict[str, set[str]] = {step_id: set() for step_id in by_id}
    outgoing: dict[str, set[str]] = {step_id: set() for step_id in by_id}

    for step_id, step in by_id.items():
        deps = _collect_dependencies(step, dep_map)
        for dep in deps:
            if dep not in by_id:
                raise ValueError(f"step '{step_id}' depends on unknown step '{dep}'")
            incoming[step_id].add(dep)
            outgoing[dep].add(step_id)

    ready = sorted([step_id for step_id, deps in incoming.items() if not deps])
    order: list[str] = []
    while ready:
        current = ready.pop(0)
        order.append(current)
        for neighbor in sorted(outgoing[current]):
            incoming[neighbor].discard(current)
            if not incoming[neighbor] and neighbor not in order and neighbor not in ready:
                ready.append(neighbor)
        ready.sort()

    if len(order) != len(steps):
        raise ValueError("workflow dependency graph contains a cycle")

    return [by_id[step_id] for step_id in order]


def transpile_workflow(spec: TranspileSpec) -> TranspileResult:
    descriptor = _read_descriptor(spec.input_ref, spec.metadata)
    steps = descriptor.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("workflow descriptor must include a non-empty 'steps' list")

    dep_map_raw = descriptor.get("dependencies", {})
    if dep_map_raw is None:
        dep_map_raw = {}
    if not isinstance(dep_map_raw, dict):
        raise ValueError("workflow descriptor 'dependencies' must be an object")
    dep_map = {str(key): [str(item) for item in value] for key, value in dep_map_raw.items()}

    ordered_steps = _topological_order([dict(step) for step in steps], dep_map)
    orchestrator = SessionOrchestrator()
    bind_identity(orchestrator.master_audit, spec)
    descriptor_hash = hashlib.sha256(
        json.dumps(descriptor, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    orchestrator.master_audit.append_payload(
        {
            "type": "workflow_descriptor",
            "descriptor_hash": descriptor_hash,
            "step_count": len(ordered_steps),
            "timestamp": time.time(),
        }
    )

    default_primes = _first_n_primes(len(ordered_steps))
    ledger = PETCLedger(min_length=max(3, len(ordered_steps)))

    trajectory: list[np.ndarray] = []
    all_infos = []
    step_certs: list[Certificate] = []
    session_ids: list[str] = []

    for index, step in enumerate(ordered_steps):
        step_id = str(step["id"])
        mode = str(step.get("mode", "gradient_descent"))
        step_dim = int(step.get("dim", spec.dim))
        step_count = max(1, min(int(step.get("steps", 10)), spec.max_steps))
        step_payload = dict(step)
        step_payload["mode"] = mode
        step_payload["steps"] = step_count
        _validate_descriptor(step_payload)

        Xi_seq, Lam_seq, G_seq, T, _, _ = _build_computation_mapping(
            step_payload, step_dim, step_count
        )
        initial_state = _vector(step_payload.get("initial_state"), step_dim, default=1.0)

        adaptive_enabled = bool(step_payload.get("adaptive", True))
        emission_policy = str(step_payload.get("emission_policy", spec.emission_policy))
        session = orchestrator.register(
            step_id,
            QARIConfig(
                dim=step_dim,
                epsilon=float(step_payload.get("epsilon", spec.epsilon)),
                op_norm_T=float(step_payload.get("op_norm_T", spec.op_norm_T)),
                emission_policy=_emission_policy(emission_policy),
                adaptive=adaptive_enabled,
                audit=True,
                max_steps=spec.max_steps,
            ),
        )

        x_state = initial_state.copy()
        step_traj = [x_state.copy()]
        for Xi_t, Lam_t, G_t in zip(Xi_seq, Lam_seq, G_seq, strict=False):
            out = session.step(x_state, Xi_t, Lam_t, T, G_t)
            x_state = out.X_next
            step_traj.append(x_state.copy())

        cert = session.certify()
        step_certs.append(cert)
        session_ids.append(step_id)
        all_infos.extend(session.infos)
        trajectory.extend(step_traj)

        assigned_prime_raw = step_payload.get("prime_index", default_primes[index])
        assigned_prime = int(assigned_prime_raw)
        if not _is_prime(assigned_prime):
            raise ValueError(
                f"workflow step '{step_id}' has non-prime prime_index={assigned_prime}"
            )
        cert_hash = hashlib.sha256(
            json.dumps(asdict(cert), sort_keys=True, separators=(",", ":"), default=str).encode(
                "utf-8"
            )
        ).hexdigest()
        ledger.append(
            assigned_prime,
            event={
                "type": "workflow_step",
                "step_id": step_id,
                "mode": mode,
                "certificate_hash": cert_hash,
            },
        )

        orchestrator.master_audit.append_payload(
            {
                "type": "workflow_step_complete",
                "step_id": step_id,
                "mode": mode,
                "steps": step_count,
                "certified": cert.certified,
                "prime_index": assigned_prime,
                "descriptor_fragment_hash": hashlib.sha256(
                    json.dumps(step_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest(),
            }
        )
        orchestrator.complete(step_id)

    while len(ledger) < max(3, len(ordered_steps)):
        last_prime = ledger.entries()[-1].prime if len(ledger) > 0 else 1
        ledger.append(_next_prime(last_prime), event={"type": "padding"})

    petc_report = ledger.validate()
    aggregated = orchestrator.aggregate_certificates(session_ids=session_ids)

    aggregate_certificate = Certificate(
        certified=aggregated.all_certified,
        margin=float(aggregated.margin_min),
        tail_bound=max((cert.tail_bound for cert in aggregated.individual_certs), default=0.0),
        details={
            "max_q": float(aggregated.q_max_global),
            "aggregate_hash": aggregated.aggregate_hash,
            "session_ids": aggregated.session_ids,
            "individual_certified": [cert.certified for cert in aggregated.individual_certs],
            "steps": sum(int(cert.details.get("steps", 0)) for cert in aggregated.individual_certs),
        },
    )

    compliance = ConformanceResult(profile="workflow")
    compliance.record("dependency_ordering", True, f"steps={len(ordered_steps)}")
    compliance.record(
        "all_steps_executed", len(session_ids) == len(ordered_steps), f"executed={len(session_ids)}"
    )
    compliance.record(
        "all_certified", aggregated.all_certified, f"sessions={len(aggregated.session_ids)}"
    )
    compliance.record(
        "petc_satisfied", petc_report.satisfied, f"chain_length={petc_report.chain_length}"
    )

    bridge = LambdaTraceBridge(session_id=f"transpile:{spec.prime_index}:workflow")
    lambda_events = [asdict(event) for event in bridge.translate(orchestrator.master_audit)]
    receipt = bridge.batch_submit()

    xi_initial = trajectory[0] if trajectory else np.zeros(spec.dim, dtype=float)
    witness_json = build_witness(
        spec,
        xi_initial,
        trajectory[-1] if trajectory else xi_initial,
        aggregate_certificate,
        receipt.merkle_root,
        session_id=f"transpile:{spec.prime_index}:workflow",
        handler_type="workflow",
        trajectory=trajectory,
        step_infos=all_infos,
        emitted_count=len(all_infos),
        poseidon_merkle_root=receipt.poseidon_merkle_root,
        extra_fields={
            "workflowStepCount": len(ordered_steps),
            "workflowDescriptorHash": descriptor_hash,
            "workflowAggregateHash": aggregated.aggregate_hash,
            "workflowSessionIds": aggregated.session_ids,
            "lambdaEventCount": len(lambda_events),
            "petcPrimeSequence": petc_report.primes_checked,
        },
    )

    if aggregate_certificate.certified and petc_report.satisfied and compliance.passed:
        verdict = "CERTIFIED"
    else:
        verdict = "UNCERTIFIED"

    return TranspileResult(
        spec=spec,
        xi_initial=xi_initial,
        trajectory=trajectory,
        certificate=aggregate_certificate,
        petc_report=petc_report,
        audit_export=orchestrator.master_audit.export(),
        lambda_events=lambda_events,
        witness_json=witness_json,
        compliance=compliance,
        merkle_root=receipt.merkle_root,
        verdict=verdict,
    )
