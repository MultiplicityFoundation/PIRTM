from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from pirtm.ace.types import AceCertificate
    from pirtm.types import Certificate, StepInfo

    from .spec import TranspileSpec


def _state_hash(state: np.ndarray) -> str:
    payload = json.dumps(state.tolist(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _poseidon_compat_hash(text: str) -> str:
    return hashlib.sha256(f"poseidon:{text}".encode()).hexdigest()


def _poseidon_state_hash(state: np.ndarray) -> str:
    payload = json.dumps(state.tolist(), sort_keys=True, separators=(",", ":"))
    return _poseidon_compat_hash(payload)


def _trajectory_hash(trajectory: list[np.ndarray]) -> str:
    payload = json.dumps(
        [state.tolist() for state in trajectory], sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_witness(
    spec: TranspileSpec,
    xi_initial: np.ndarray,
    final_state: np.ndarray,
    certificate: AceCertificate | Certificate,
    merkle_root: str,
    session_id: str,
    *,
    handler_type: str = "unknown",
    trajectory: list[np.ndarray] | None = None,
    step_infos: list[StepInfo] | None = None,
    emitted_count: int | None = None,
    poseidon_merkle_root: str | None = None,
    extra_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    prev_hash = _state_hash(xi_initial)
    new_hash = _state_hash(final_state)
    prev_poseidon_hash = _poseidon_state_hash(xi_initial)
    new_poseidon_hash = _poseidon_state_hash(final_state)

    metadata = spec.metadata if isinstance(spec.metadata, dict) else {}
    configured_scheme = str(metadata.get("hash_scheme", "dual"))
    if configured_scheme not in {"sha256", "poseidon_compat", "dual"}:
        configured_scheme = "dual"
    emit_dual = bool(metadata.get("dual_hash", False)) or configured_scheme == "dual"

    primary_scheme = "sha256"
    if configured_scheme == "poseidon_compat" and not emit_dual:
        primary_scheme = "poseidon_compat"

    primary_state_hash = prev_hash if primary_scheme == "sha256" else prev_poseidon_hash
    primary_new_state_hash = new_hash if primary_scheme == "sha256" else new_poseidon_hash
    primary_merkle_root = (
        merkle_root if primary_scheme == "sha256" else (poseidon_merkle_root or merkle_root)
    )

    cert_dict = asdict(certificate)
    nonce = hashlib.sha256(f"{session_id}:{spec.identity_commitment}".encode()).hexdigest()[:32]
    witness = {
        "stateHash": primary_state_hash,
        "newStateHash": primary_new_state_hash,
        "prevStateHash": primary_state_hash,
        "primeIndex": int(spec.prime_index),
        "identityCommitment": str(spec.identity_commitment),
        "timestamp": int(__import__("time").time()),
        "nonce": nonce,
        "certificate": cert_dict,
        "merkleRoot": primary_merkle_root,
        "hashScheme": primary_scheme,
        "hashSchemes": [primary_scheme],
        "pathType": handler_type,
    }

    if emit_dual:
        witness["stateHashSha256"] = prev_hash
        witness["newStateHashSha256"] = new_hash
        witness["prevStateHashSha256"] = prev_hash
        witness["stateHashPoseidon"] = prev_poseidon_hash
        witness["newStateHashPoseidon"] = new_poseidon_hash
        witness["prevStateHashPoseidon"] = prev_poseidon_hash
        witness["merkleRootSha256"] = merkle_root
        witness["merkleRootPoseidon"] = poseidon_merkle_root
        witness["hashSchemes"] = ["sha256", "poseidon_compat"]

    if trajectory is not None and trajectory:
        witness["trajectoryLength"] = len(trajectory)
        witness["trajectoryHash"] = _trajectory_hash(trajectory)
        witness["finalStateNorm"] = float(np.linalg.norm(trajectory[-1]))

    if step_infos:
        qs = [info.q for info in step_infos]
        witness["stepCount"] = len(step_infos)
        witness["qMax"] = float(max(qs))
        witness["qMin"] = float(min(qs))
        witness["projectedCount"] = int(sum(1 for info in step_infos if info.projected))
        witness["residualFinal"] = float(step_infos[-1].residual)

    if emitted_count is not None:
        witness["emittedCount"] = int(emitted_count)

    if extra_fields:
        witness.update(extra_fields)

    return witness
