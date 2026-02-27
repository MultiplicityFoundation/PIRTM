# PIRTM API Reference

## Core Types (`pirtm.types`)

### `StepInfo`
- Fields: `step`, `q`, `epsilon`, `nXi`, `nLam`, `projected`, `residual`, `note`

### `Status`
- Fields: `converged`, `safe`, `steps`, `residual`, `epsilon`, `note`

### `Certificate`
- Fields: `certified`, `margin`, `tail_bound`, `details`

### `PETCEntry` / `PETCReport`
- `PETCEntry`: prime-indexed ledger entry payload
- `PETCReport`: chain validation (`satisfied`, `coverage`, gaps, monotonicity, violations)

### `WeightSchedule`, `CSCBudget`, `CSCMargin`
- Tier 2 planning/certification dataclasses.

## Recurrence (`pirtm.recurrence`)

### `step(X_t, Xi_t, Lam_t, T, G_t, P, *, epsilon=0.05, op_norm_T=1.0, t=0)`
Runs one contractive step and returns `(X_next, StepInfo)`.

### `run(X0, Xi_seq, Lam_seq, G_seq, *, T, P, epsilon=0.05, op_norm_T=1.0, tol=1e-6, max_steps=None)`
Runs recurrence over sequences and returns `(X_final, history, infos, status)`.

## Projection (`pirtm.projection`)

### `project_parameters_soft(Xi, Lam, op_norm_T, target)`
Scales matrices to enforce `||Xi|| + ||Lam||*||T|| <= target`.

### `project_parameters_weighted_l1(values, weights, budget, *, tol=1e-9)`
Projects vector onto weighted `\ell_1` ball and returns `(projection, tau)`.

## Certificates (`pirtm.certify`)

### `ace_certificate(info, *, tail_norm=0.0)`
Builds certificate with `margin = target - max_q`.

### `iss_bound(info, disturbance_norm)`
Returns disturbance bound `d/(1-max_q)` when stable, else `inf`.

## PETC (`pirtm.petc`)

### `PETCLedger(max_gap=100, min_length=3)`
- `append(prime, event=None, info=None)`
- `validate() -> PETCReport`
- `coverage(lo, hi) -> float`

### `petc_invariants(primes, min_length=3)`
Backward-compatible shim around ledger validation with mass-violation guard.

## Weights (`pirtm.weights`)

### `synthesize_weights(primes, dim, *, op_norm_T=1.0, q_star=0.9, profile='log_decay', epsilon=0.05, basis=None)`
Returns `WeightSchedule` for recurrence initialization.

### `validate_schedule(schedule, op_norm_T, *, tol=1e-12)`
Verifies per-step `q_k <= q_target`.

## Gain (`pirtm.gain`)

### `estimate_operator_norm(T, dim, *, max_iter=200, tol=1e-10, seed=None)`
Power-iteration estimator returning `(norm, iterations)`.

### `build_gain_sequence(length, dim, *, scale=0.01, profile='decay', decay_rate=1.0, seed=None)`
Builds gain vectors for recurrence driving.

### `check_iss_compatibility(gains, infos, target_radius)`
Returns `(compatible, max_gain_norm)`.

## CSC (`pirtm.csc`)

### `solve_budget(op_norm_T, *, epsilon=0.05, alpha=0.5)`
Computes CSC-safe max norms.

### `compute_margin(Xi_norm, Lam_norm, op_norm_T, *, epsilon=0.05)`
Computes safety margin for a configuration.

### `multi_step_margin(infos)`
Computes worst-case margin over a run trace.

### `sensitivity(Xi_norm, Lam_norm, *, epsilon=0.05)`
Reports `T_max`, `epsilon_min`, and headroom.

## Gate (`pirtm.gate`)

### `EmissionPolicy`
- Enum: `PASS_THROUGH`, `SUPPRESS`, `HOLD`, `ATTENUATE`.

### `EmissionGate(policy=EmissionPolicy.SUPPRESS, custom_predicate=None, attenuation_floor=0.01)`
- Callable wrapper around `step()` with emission policy on predicate failure.

### `gated_run(X0, Xi_seq, Lam_seq, G_seq, *, T, P, gate, epsilon=0.05, op_norm_T=1.0)`
- Runs recurrence through an `EmissionGate`, returns `(X_final, history, gated_outputs)`.

## Telemetry (`pirtm.telemetry`)

### `TelemetryEvent`
- Fields: `timestamp`, `event_type`, `step_index`, `payload`, `source`, `version`.

### Sinks
- `NullSink` (default no-op), `MemorySink`, `FileSink`, `CallbackSink`.

### `TelemetryBus(sinks=None, alerts=None)`
- Emits `step`, `gate`, `certificate`, and `alert` events to all sinks.

## Audit (`pirtm.audit`)

### `AuditChain`
- Hash-chained append-only event log with deterministic canonical JSON.
- APIs: `append_step`, `append_gate`, `append_certificate`, `verify`, `export`, `head`, `len`.

## Q-ARI (`pirtm.qari`)

### `QARIConfig`
- Session config for dimension, epsilon, operator norm, emission policy, adaptive/audit flags.

### `QARISession`
- High-level runtime: `step`, `certify`, `summary`, telemetry emission, optional audit chain.

## CSL (`pirtm.csl`, `pirtm.csl_gate`)

### `evaluate_csl(...) -> CSLVerdict`
- Composes Neutrality, Beneficence, Silence, and Commutation checks.

### `CSLEmissionGate`
- Two-stage gate: contraction gate first, then CSL evaluation.
- Emits only when both stages pass; silence returns NO-OP (`X_t`).

## Spectral Governance (`pirtm.spectral_decomp`, `pirtm.spectral_gov`)

### `spectral_decomposition`, `spectral_entropy`, `phase_coherence`, `analyze_tensor`
- Matrix spectral utilities used by governance and diagnostics.

### `SpectralGovernor`
- Finite-difference Jacobian probing + eig/SVD analysis.
- Returns governance tuple `(recommended_epsilon, op_norm_estimate, SpectralReport)`.

## Multi-Session (`pirtm.orchestrator`)

### `SessionOrchestrator`
- Session registry by ID, pause snapshots, aggregate certificates, global summaries.

### `AggregatedCertificate`, `SessionSnapshot`
- Federation-level certificate bundle and serializable migration payload.

## ΛProof Bridge (`pirtm.lambda_bridge`)

### `LambdaTraceBridge(session_id, capability_token="", submit_fn=None)`
- Translates `AuditChain` events into Λ-trace payloads.
- `batch_submit()` supports dry-run and submit-function integration.

## PETC Bridge (`pirtm.petc_bridge`)

### `PETCAllocator`
- Allocates non-colliding prime index sequences per session.
- Tags audit chains with `(prime_index, chain_hash)` and verifies global ordering.
