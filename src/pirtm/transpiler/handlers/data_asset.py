from __future__ import annotations

import hashlib
import time
from dataclasses import asdict

import numpy as np

from pirtm.conformance import check_core_profile
from pirtm.gate import EmissionPolicy
from pirtm.lambda_bridge import LambdaTraceBridge
from pirtm.petc import PETCLedger
from pirtm.qari import QARIConfig, QARISession

from ..identity import bind_identity
from ..models import TranspileResult
from ..prime_mapper import map_content_to_prime_channels
from ..spec import TranspileSpec
from ..witness import build_witness


def _emission_policy(value: str) -> EmissionPolicy:
    for policy in EmissionPolicy:
        if policy.value == value:
            return policy
    raise ValueError(f"unsupported emission policy: {value}")


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    cursor = 3
    while cursor * cursor <= n:
        if n % cursor == 0:
            return False
        cursor += 2
    return True


def _next_prime(n: int) -> int:
    candidate = max(2, n + 1)
    while not _is_prime(candidate):
        candidate += 1
    return candidate


def transpile_data_asset(spec: TranspileSpec) -> TranspileResult:
    with open(spec.input_ref, "rb") as handle:
        raw = handle.read()
    content_hash = hashlib.sha256(raw).hexdigest()
    prime_map = spec.metadata.get("prime_map") if isinstance(spec.metadata, dict) else None
    channels = map_content_to_prime_channels(raw, spec.input_ref, spec.dim, prime_map=prime_map)

    xi_initial = np.stack([channel.vector for channel in channels], axis=0)
    x_state = np.mean(xi_initial, axis=0)
    trajectory: list[np.ndarray] = [x_state.copy()]

    session = QARISession(
        QARIConfig(
            dim=spec.dim,
            epsilon=spec.epsilon,
            op_norm_T=spec.op_norm_T,
            emission_policy=_emission_policy(spec.emission_policy),
            adaptive=True,
            audit=True,
            max_steps=spec.max_steps,
        )
    )
    if session.audit_chain is None:
        raise RuntimeError("audit chain unavailable")

    bind_identity(session.audit_chain, spec)
    session.audit_chain.append_payload(
        {
            "type": "content_anchor",
            "input_ref": spec.input_ref,
            "content_hash": content_hash,
            "timestamp": time.time(),
        }
    )

    ledger = PETCLedger(min_length=3)
    for channel in channels:
        ledger.append(channel.prime, event={"digest": channel.digest})
    while len(ledger) < 3:
        last = ledger.entries()[-1].prime if len(ledger) > 0 else 1
        ledger.append(_next_prime(last), event={"type": "padding"})

    step_count = min(max(3, len(channels)), spec.max_steps)
    Xi = 0.25 * np.eye(spec.dim)
    Lam = 0.25 * np.eye(spec.dim)
    G = np.zeros(spec.dim)
    T = lambda x: 0.5 * x
    P = lambda x: x

    emitted_flags: list[bool] = []
    Xi_seq = [Xi.copy() for _ in range(step_count)]
    Lam_seq = [Lam.copy() for _ in range(step_count)]
    G_seq = [G.copy() for _ in range(step_count)]

    for Xi_t, Lam_t, G_t in zip(Xi_seq, Lam_seq, G_seq):
        gated = session.step(x_state, Xi_t, Lam_t, T, G_t)
        x_state = gated.X_next
        trajectory.append(x_state.copy())
        emitted_flags.append(gated.emitted)

    certificate = session.certify()
    petc_report = ledger.validate()

    compliance = check_core_profile(
        np.mean(xi_initial, axis=0),
        Xi_seq,
        Lam_seq,
        G_seq,
        T=T,
        P=P,
        epsilon=spec.epsilon,
        op_norm_T=spec.op_norm_T,
    )

    bridge = LambdaTraceBridge(session_id=f"transpile:{spec.prime_index}")
    lambda_events = [asdict(event) for event in bridge.translate(session.audit_chain)]
    receipt = bridge.batch_submit()
    witness_json = build_witness(
        spec,
        xi_initial,
        trajectory[-1],
        certificate,
        receipt.merkle_root,
        session_id=f"transpile:{spec.prime_index}",
        handler_type="data_asset",
        trajectory=trajectory,
        step_infos=session.infos,
        emitted_count=sum(1 for emitted in emitted_flags if emitted),
        poseidon_merkle_root=receipt.poseidon_merkle_root,
        extra_fields={
            "contentHash": content_hash,
            "channelCount": len(channels),
            "channelPrimes": [channel.prime for channel in channels],
            "lambdaEventCount": len(lambda_events),
        },
    )

    if certificate.certified and petc_report.satisfied and compliance.passed:
        verdict = "CERTIFIED"
    elif emitted_flags and not any(emitted_flags):
        verdict = "SILENT"
    else:
        verdict = "UNCERTIFIED"

    return TranspileResult(
        spec=spec,
        xi_initial=xi_initial,
        trajectory=trajectory,
        certificate=certificate,
        petc_report=petc_report,
        audit_export=session.audit_chain.export(),
        lambda_events=lambda_events,
        witness_json=witness_json,
        compliance=compliance,
        merkle_root=receipt.merkle_root,
        verdict=verdict,
    )
