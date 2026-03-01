from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from pirtm.conformance import check_core_profile
from pirtm.gate import EmissionPolicy
from pirtm.lambda_bridge import LambdaTraceBridge
from pirtm.petc import PETCLedger
from pirtm.qari import QARIConfig, QARISession
from pirtm.weights import synthesize_weights, validate_schedule

from ..identity import bind_identity
from ..models import TranspileResult
from ..witness import build_witness

if TYPE_CHECKING:
    from ..spec import TranspileSpec

Operator = Callable[[np.ndarray], np.ndarray]


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


def _emission_policy(value: str) -> EmissionPolicy:
    for policy in EmissionPolicy:
        if policy.value == value:
            return policy
    raise ValueError(f"unsupported emission policy: {value}")


def _descriptor(spec: TranspileSpec) -> dict:
    path = Path(spec.input_ref)
    if path.exists() and path.suffix.lower() == ".json":
        parsed = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise ValueError("computation descriptor JSON must be an object")
        return {**parsed, **spec.metadata}
    return dict(spec.metadata)


def _vector(values: object, dim: int, default: float = 0.0) -> np.ndarray:
    if values is None:
        return np.full(dim, default, dtype=float)
    arr = np.array(values, dtype=float).reshape(-1)
    if arr.size == 0:
        return np.full(dim, default, dtype=float)
    if arr.size >= dim:
        return arr[:dim]
    pad = np.full(dim - arr.size, float(arr[-1]), dtype=float)
    return np.concatenate([arr, pad])


def _first_n_primes(count: int) -> list[int]:
    primes: list[int] = []
    value = 2
    while len(primes) < count:
        if _is_prime(value):
            primes.append(value)
        value += 1
    return primes


def _validate_descriptor(config: dict[str, Any]) -> None:
    mode = str(config.get("mode", "gradient_descent"))
    supported = {"gradient_descent", "adam", "iterative_solver", "two_layer_nn"}
    if mode not in supported:
        raise ValueError(f"unsupported computation mode: {mode}")

    steps = int(config.get("steps", 1))
    if steps < 1:
        raise ValueError("steps must be >= 1")

    if mode in {"gradient_descent", "adam", "two_layer_nn"}:
        learning_rate = float(config.get("learning_rate", 0.2))
        if not (0.0 < learning_rate < 1.0):
            raise ValueError("learning_rate must be in (0, 1)")

    if mode == "adam":
        beta1 = float(config.get("beta1", 0.9))
        beta2 = float(config.get("beta2", 0.999))
        if not (0.0 < beta1 < 1.0):
            raise ValueError("beta1 must be in (0, 1)")
        if not (0.0 < beta2 < 1.0):
            raise ValueError("beta2 must be in (0, 1)")

    if mode == "iterative_solver":
        relaxation = float(config.get("relaxation", 0.2))
        if not (0.0 < relaxation < 1.0):
            raise ValueError("relaxation must be in (0, 1)")

    if mode == "two_layer_nn":
        input_dim = int(config.get("input_dim", 2))
        hidden_dim = int(config.get("hidden_dim", 3))
        output_dim = int(config.get("output_dim", 1))
        if min(input_dim, hidden_dim, output_dim) < 1:
            raise ValueError("two_layer_nn dimensions must be >= 1")


def _build_computation_mapping(
    config: dict[str, Any],
    dim: int,
    step_count: int,
) -> tuple[
    list[np.ndarray],
    list[np.ndarray],
    list[np.ndarray],
    Operator,
    dict[str, Any],
    dict[str, Any],
]:
    mode = str(config.get("mode", "gradient_descent"))

    learning_rate = float(config.get("learning_rate", 0.2))
    initial_state = _vector(config.get("initial_state"), dim, default=1.0)
    target_state = _vector(config.get("target_state"), dim, default=0.0)
    forcing = _vector(config.get("forcing"), dim, default=0.0)

    if mode == "gradient_descent":
        xi_scale = float(config.get("xi_scale", max(0.05, 1.0 - learning_rate)))
        lam_scale = float(config.get("lam_scale", learning_rate))
        Xi_seq = [xi_scale * np.eye(dim) for _ in range(step_count)]
        Lam_seq = [(-lam_scale) * np.eye(dim) for _ in range(step_count)]
        G_seq = [forcing.copy() for _ in range(step_count)]

        def T(x):
            return x - target_state

        extras = {
            "mode": mode,
            "learningRate": learning_rate,
            "targetStateHash": hashlib.sha256(target_state.tobytes()).hexdigest(),
            "initialStateHash": hashlib.sha256(initial_state.tobytes()).hexdigest(),
        }
        context = {"target_state": target_state, "objective": "mse_parameter_loss"}
        return Xi_seq, Lam_seq, G_seq, T, extras, context

    if mode == "adam":
        beta1 = float(config.get("beta1", 0.9))
        beta2 = float(config.get("beta2", 0.999))
        optimizer_eps = float(config.get("optimizer_epsilon", 1e-8))
        max_effective_lr = float(config.get("max_effective_lr", 0.45))

        Xi_seq: list[np.ndarray] = []
        Lam_seq: list[np.ndarray] = []
        G_seq = [forcing.copy() for _ in range(step_count)]
        effective_lrs: list[float] = []
        for t in range(1, step_count + 1):
            bias_correction = 1.0 - beta1**t
            variance_correction = 1.0 - beta2**t
            lr_t = learning_rate * (variance_correction**0.5) / max(1e-12, bias_correction)
            lr_t = min(max(lr_t, 1e-4), max_effective_lr)
            effective_lrs.append(lr_t)
            Xi_seq.append((1.0 - lr_t) * np.eye(dim))
            Lam_seq.append((-lr_t) * np.eye(dim))

        def T(x):
            return x - target_state

        extras = {
            "mode": mode,
            "learningRate": learning_rate,
            "beta1": beta1,
            "beta2": beta2,
            "optimizerEpsilon": optimizer_eps,
            "effectiveLrMin": float(min(effective_lrs)),
            "effectiveLrMax": float(max(effective_lrs)),
            "targetStateHash": hashlib.sha256(target_state.tobytes()).hexdigest(),
            "initialStateHash": hashlib.sha256(initial_state.tobytes()).hexdigest(),
        }
        context = {"target_state": target_state, "objective": "mse_parameter_loss"}
        return Xi_seq, Lam_seq, G_seq, T, extras, context

    if mode == "iterative_solver":
        relaxation = float(config.get("relaxation", 0.2))
        relaxation = min(max(relaxation, 1e-4), 0.95)
        Xi_seq = [(1.0 - relaxation) * np.eye(dim) for _ in range(step_count)]
        Lam_seq = [relaxation * np.eye(dim) for _ in range(step_count)]
        G_seq = [forcing.copy() for _ in range(step_count)]

        def T(x):
            return target_state

        extras = {
            "mode": mode,
            "relaxation": relaxation,
            "targetStateHash": hashlib.sha256(target_state.tobytes()).hexdigest(),
            "initialStateHash": hashlib.sha256(initial_state.tobytes()).hexdigest(),
        }
        context = {"target_state": target_state, "objective": "fixed_point_residual"}
        return Xi_seq, Lam_seq, G_seq, T, extras, context

    if mode == "two_layer_nn":
        input_dim = int(config.get("input_dim", 2))
        hidden_dim = int(config.get("hidden_dim", 3))
        output_dim = int(config.get("output_dim", 1))
        expected_dim = (
            (input_dim * hidden_dim) + hidden_dim + (hidden_dim * output_dim) + output_dim
        )
        if dim != expected_dim:
            raise ValueError(
                f"two_layer_nn mode expects dim={expected_dim} for shape ({input_dim},{hidden_dim},{output_dim}), got dim={dim}"
            )

        seed = int(config.get("seed", 7))
        rng = np.random.default_rng(seed)
        target_state = _vector(
            config.get("target_state", rng.normal(loc=0.0, scale=0.2, size=dim).tolist()),
            dim,
            default=0.0,
        )
        forcing = _vector(config.get("forcing"), dim, default=0.0)
        xi_scale = float(config.get("xi_scale", max(0.05, 1.0 - learning_rate)))
        lam_scale = float(config.get("lam_scale", learning_rate))

        Xi_seq = [xi_scale * np.eye(dim) for _ in range(step_count)]
        Lam_seq = [(-lam_scale) * np.eye(dim) for _ in range(step_count)]
        G_seq = [forcing.copy() for _ in range(step_count)]

        def T(x):
            return x - target_state

        extras = {
            "mode": mode,
            "learningRate": learning_rate,
            "modelShape": [input_dim, hidden_dim, output_dim],
            "parameterCount": expected_dim,
            "targetStateHash": hashlib.sha256(target_state.tobytes()).hexdigest(),
            "initialStateHash": hashlib.sha256(initial_state.tobytes()).hexdigest(),
            "objective": "mse_parameter_loss",
        }
        context = {"target_state": target_state, "objective": "mse_parameter_loss"}
        return Xi_seq, Lam_seq, G_seq, T, extras, context

    raise ValueError(f"unsupported computation mode: {mode}")


def transpile_computation(spec: TranspileSpec) -> TranspileResult:
    config = _descriptor(spec)
    _validate_descriptor(config)
    mode = str(config.get("mode", "gradient_descent"))
    steps = int(config.get("steps", min(50, spec.max_steps)))
    step_count = max(1, min(steps, spec.max_steps))
    descriptor_hash = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    initial_state = _vector(config.get("initial_state"), spec.dim, default=1.0)
    Xi_seq, Lam_seq, G_seq, T, mode_extras, mode_context = _build_computation_mapping(
        config, spec.dim, step_count
    )

    schedule_profile = str(config.get("weight_profile", "log_decay"))
    q_star = float(config.get("q_star", max(0.1, 1.0 - (spec.epsilon * 0.5))))
    schedule_primes = _first_n_primes(step_count)
    weight_schedule = synthesize_weights(
        schedule_primes,
        dim=spec.dim,
        op_norm_T=spec.op_norm_T,
        q_star=q_star,
        profile=schedule_profile,
        epsilon=spec.epsilon,
    )
    schedule_valid, schedule_max_q = validate_schedule(weight_schedule, spec.op_norm_T)

    learning_rate = float(config.get("learning_rate", 0.2))
    adaptive_enabled = bool(config.get("adaptive", True))

    def P(x):
        return x

    session = QARISession(
        QARIConfig(
            dim=spec.dim,
            epsilon=spec.epsilon,
            op_norm_T=spec.op_norm_T,
            emission_policy=_emission_policy(spec.emission_policy),
            adaptive=adaptive_enabled,
            audit=True,
            max_steps=spec.max_steps,
        )
    )
    if session.audit_chain is None:
        raise RuntimeError("audit chain unavailable")

    bind_identity(session.audit_chain, spec)
    session.audit_chain.append_payload(
        {
            "type": "computation_descriptor",
            "input_ref": spec.input_ref,
            "mode": mode,
            "steps": step_count,
            "learning_rate": learning_rate,
            "descriptor_hash": descriptor_hash,
            "weight_schedule_profile": schedule_profile,
            "weight_schedule_valid": schedule_valid,
            "adaptive_enabled": adaptive_enabled,
            "timestamp": time.time(),
        }
    )

    x_state = initial_state.copy()
    trajectory: list[np.ndarray] = [x_state.copy()]
    emitted_flags: list[bool] = []

    ledger = PETCLedger(min_length=3)

    for step_idx, (Xi_t, Lam_t, G_t) in enumerate(
        zip(Xi_seq, Lam_seq, G_seq, strict=False), start=1
    ):
        gated = session.step(x_state, Xi_t, Lam_t, T, G_t)
        x_state = gated.X_next
        trajectory.append(x_state.copy())
        emitted_flags.append(gated.emitted)

        if _is_prime(step_idx):
            digest = hashlib.sha256(x_state.tobytes()).hexdigest()
            ledger.append(
                step_idx, event={"type": "prime_step", "state_hash": digest}, info=gated.info
            )

    loss_initial: float | None = None
    loss_final: float | None = None
    loss_delta: float | None = None
    target_state = mode_context.get("target_state")
    if isinstance(target_state, np.ndarray) and trajectory:
        losses = [float(np.mean((state - target_state) ** 2)) for state in trajectory]
        loss_initial = losses[0]
        loss_final = losses[-1]
        loss_delta = loss_initial - loss_final

    while len(ledger) < 3:
        prime_fallbacks = [2, 3, 5]
        ledger.append(prime_fallbacks[len(ledger)], event={"type": "padding"})

    certificate = session.certify()
    petc_report = ledger.validate()

    compliance = check_core_profile(
        initial_state,
        Xi_seq,
        Lam_seq,
        G_seq,
        T=T,
        P=P,
        epsilon=spec.epsilon,
        op_norm_T=spec.op_norm_T,
    )

    bridge = LambdaTraceBridge(session_id=f"transpile:{spec.prime_index}:computation")
    lambda_events = [asdict(event) for event in bridge.translate(session.audit_chain)]
    receipt = bridge.batch_submit()

    witness_json = build_witness(
        spec,
        initial_state,
        trajectory[-1],
        certificate,
        receipt.merkle_root,
        session_id=f"transpile:{spec.prime_index}:computation",
        handler_type="computation",
        trajectory=trajectory,
        step_infos=session.infos,
        emitted_count=sum(1 for emitted in emitted_flags if emitted),
        poseidon_merkle_root=receipt.poseidon_merkle_root,
        extra_fields={
            **mode_extras,
            "mode": mode,
            "learningRate": learning_rate,
            "adaptiveEnabled": adaptive_enabled,
            "descriptorHash": descriptor_hash,
            "weightScheduleProfile": schedule_profile,
            "weightScheduleValid": schedule_valid,
            "weightScheduleMaxQ": float(schedule_max_q),
            "weightSchedulePrimeCount": len(weight_schedule.primes_used),
            "weightScheduleQTarget": float(weight_schedule.q_targets[0])
            if len(weight_schedule.q_targets) > 0
            else None,
            "lambdaEventCount": len(lambda_events),
            "lossInitial": loss_initial,
            "lossFinal": loss_final,
            "lossDelta": loss_delta,
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
        xi_initial=initial_state,
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
