# Simulation Legacy Import Audit and Migration Map (R6)

Date: 2026-03-01

## Scope

Audits `src/pirtm/simulations/*.py` for `_legacy` dependencies and defines migration targets aligned with the `R4`/`R5` boundary decisions.

## Inventory

| Module | `_legacy` imports found | Current classification | Recommended path |
|---|---|---|---|
| `src/pirtm/simulations/qari_module.py` | *(none)* | Modernized simulation | Maintain on core-backed helper path |
| `src/pirtm/simulations/quantum_feedback.py` | *(none)* | Modernized simulation | Maintain on core-backed helper path |
| `src/pirtm/simulations/riemann_verification.py` | `PrimeTensorSystem` | Legacy-backed research simulation (isolated non-core) | Keep classified research-only until generator replacement exists |

## Legacy Usage Detail

- `PrimeTensorSystem` is the dominant blocker across all simulation modules.
- `recursive_update` can be mapped to modern recurrence stepping logic with explicit norm-safe scaling.
- `analyze_tensor` can be mapped to supported `pirtm.spectral_decomp.analyze_tensor`.
- `feedback_operator` in legacy is simple and can be replaced with simulation-local helper logic where needed.

## Migration Plan (Incremental)

### Phase 1 — Replace non-blocking spectral imports

- Replace legacy `analyze_tensor` imports with supported `pirtm.spectral_decomp.analyze_tensor` where behavior is compatible.

Status:

- Completed for `qari_module.py`.
- Completed for `riemann_verification.py`.
- Deferred for `quantum_feedback.py` because it relies on legacy `analyze_tensor(..., plot=...)` signature behavior not currently present in supported API.

### Phase 2 — Recurrence-core migration for simulation loops

- Replace `recursive_update` calls with modern recurrence-oriented update paths.
- Keep simulation-local feedback generation but route state transitions through supported APIs.

Status:

- Completed for `qari_module.py` and `quantum_feedback.py` via `pirtm.simulations.core_helpers`.

### Phase 3 — Prime tensor generator decision

- Either:
  - implement a supported non-legacy prime-tensor generator utility for simulations, or
  - explicitly keep specific simulation modules legacy-classified until replacement is approved.

## Proposed Classification (Current)

- **Legacy-classified/non-core (temporary):**
  - `riemann_verification.py` (research-oriented spectral interference simulation)
- **Modernized off `_legacy`:**
  - `qari_module.py`
  - `quantum_feedback.py`

## Phase 1 Implementation Notes

- All simulation modules now include explicit legacy-classification module headers.

## Phase 2 Implementation Notes

- Added `src/pirtm/simulations/core_helpers.py` as a core-backed helper module for:
  - prime-indexed tensor bank generation
  - norm-safe recurrence updates
  - feedback helper replacement
  - optional plotting-compatible spectral analysis wrapper
- `qari_module.py` and `quantum_feedback.py` now run on core-backed simulation helpers with no `_legacy` imports.
- `riemann_verification.py` remains explicitly isolated as research-only/non-core.

## Exit Criteria for R6 completion

- Every simulation module is either:
  - migrated off `_legacy`, or
  - explicitly marked legacy-classified with rationale and non-core status.
- Documentation references point to modernized entry points for migrated modules.
