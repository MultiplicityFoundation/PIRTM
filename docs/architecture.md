# PIRTM Architecture

## Package Identity

PIRTM is a numerical control core centered on contractive recurrence with runtime safety projection and certification.

## Module Graph

- `types` is the shared data contract layer.
- `recurrence` is the execution core.
- `projection` constrains parameter norms.
- `certify` consumes `StepInfo` traces for guarantees.
- `petc`, `weights`, `gain`, and `csc` provide Tier 2 planning/validation.
- `gate`, `telemetry`, `audit`, and `qari` provide Tier 6 runtime governance and traceability.
- `csl`, `csl_gate`, `spectral_gov`, `orchestrator`, `lambda_bridge`, and `petc_bridge` provide Tier 7 protocol-layer integration.

Dependency direction is mostly leafward toward `types`.

## Data Flow (`step`)

1. Compute `q_t = ||Xi_t|| + ||Lam_t|| * op_norm_T`.
2. If `q_t > 1 - epsilon`, project `(Xi_t, Lam_t)`.
3. Compute candidate state: `Xi_t @ X_t + Lam_t @ T(X_t) + G_t`.
4. Apply projector `P`.
5. Emit `StepInfo` telemetry.

## Invariants

- Contractivity target: `q_t <= 1 - epsilon` after projection.
- Projection feasibility for weighted `\ell_1` constraints.
- Certificate consistency: `margin = target - max_q`.

## Extension Points

- Custom `T` operator callable.
- Custom projector callable/object with `.apply`.
- Custom weight/gain schedules via Tier 2 APIs.
- Custom telemetry sinks/alerts and λ-trace submit function.
- Custom CSL predicates via subject sets and filter function.

## Tier 7 Flow

1. `SpectralGovernor.govern(T)` recommends `epsilon` and `op_norm_T`.
2. `CSLEmissionGate` composes contraction and CSL checks per step.
3. `QARISession` records telemetry and optional audit chain.
4. `SessionOrchestrator` coordinates multiple sessions and aggregates certificates.
5. `LambdaTraceBridge` translates audit chains for external submission.
6. `PETCAllocator` assigns prime-indexed ordering across session event chains.

## Legacy Boundary

Legacy modules are under `pirtm._legacy` with deprecation warning at import and compatibility-only scope.

### Legacy Sunset Timeline (R5)

| Legacy module | Status | Migration target | Removal target |
|---|---|---|---|
| `pirtm._legacy.pir_tensor` | Deprecated | `pirtm.recurrence`, `pirtm.projection`, `pirtm.qari` | `v0.3.0` |
| `pirtm._legacy.recursive_ops` | Deprecated | `pirtm.recurrence`, `pirtm.certify`, `pirtm.gain`, `pirtm.csc` | `v0.3.0` |
| `pirtm._legacy.spectral_decomp` | Deprecated | `pirtm.spectral_decomp`, `pirtm.spectral_gov` | `v0.3.0` |

Policy:

- `v0.1.x`: deprecated modules remain available with explicit per-module warnings.
- `v0.2.x`: deprecation messaging tightened and migration guidance emphasized.
- `v0.3.0`: remove deprecated `_legacy` modules that have supported replacements.

## Spectral API Boundary Decision (R4)

Decision date: 2026-03-01

- `pirtm.spectral_decomp` remains a **supported public API surface** for the `v0.1.x` line.
- `pirtm.spectral_gov` remains a supported governance companion API.
- Spectral utilities under `pirtm._legacy` are **deprecated transition surfaces** only.

### Sunset Timeline

- `v0.1.x`: top-level spectral APIs supported; `_legacy` remains available with deprecation warnings.
- `v0.2.x`: deprecation messages become strict and include migration guidance.
- `v0.3.0` target: remove deprecated `_legacy` spectral entry points that are superseded by supported top-level APIs.

This boundary keeps public spectral usage stable while allowing controlled legacy retirement through `R5` and simulation migration work in `R6`.
