# R6: Migrate simulations off `_legacy` (or classify explicitly)

- **Type**: Feature request
- **Labels**: `enhancement`, `legacy`, `simulations`
- **Track**: C (Simulation Modernization)
- **Size**: M
- **Depends on**: R4

## Summary

Modernize simulation modules currently importing `pirtm._legacy`, or explicitly classify and isolate simulations that remain legacy-backed.

## Motivation

Simulation paths still coupled to legacy APIs create drift against the modern contractive core and complicate future removals.

## Acceptance Criteria

- [x] Inventory of simulation modules and import paths is documented.
- [x] Each simulation is either migrated to modern APIs or explicitly marked as legacy.
- [x] Legacy-classified simulations are isolated and documented as non-core.
- [x] Modernized simulations run successfully with current package APIs.

## Implementation Checklist

- [x] Audit `src/pirtm/simulations/*.py` legacy imports.
- [x] Replace with core APIs (`recurrence`, `qari`, `gate`, `certify`) where feasible.
- [x] Add clear headers/docs for any simulation intentionally left legacy.
- [x] Update examples/docs references to modernized simulation entry points.

## Progress Notes (2026-03-01)

- Completed module-level legacy import audit for all simulation modules.
- Added migration artifact: `docs/plans/simulation_migration_map.md`.
- Current audit result:
	- `qari_module.py`: legacy-backed, migration candidate.
	- `quantum_feedback.py`: legacy-backed, migration candidate.
	- `riemann_verification.py`: legacy-backed, currently best classified as research/non-core until generator replacement is approved.
- Phase 1 executed:
	- `qari_module.py` now uses `pirtm.spectral_decomp.analyze_tensor`.
	- `riemann_verification.py` now uses `pirtm.spectral_decomp.analyze_tensor`.
	- `quantum_feedback.py` retains legacy `analyze_tensor` temporarily due to `plot`-argument behavior mismatch.
- Added explicit legacy-classification module headers in all simulation modules that still depend on `_legacy` APIs.
- Phase 2 executed:
	- `qari_module.py` migrated off `_legacy` generator/update dependencies.
	- `quantum_feedback.py` migrated off `_legacy` generator/update/feedback/spectral dependencies.
	- `riemann_verification.py` kept explicitly research-only and legacy-classified (isolated non-core).
	- Added shared core-backed helper module: `src/pirtm/simulations/core_helpers.py`.

## Completion Notes (2026-03-01)

- `qari_module.py` and `quantum_feedback.py` now have no `_legacy` imports.
- `riemann_verification.py` remains the only `_legacy`-dependent simulation and is explicitly documented as isolated research-only/non-core.
- Migration/classification matrix updated in `docs/plans/simulation_migration_map.md`.

## Out of Scope

- Comprehensive test hardening for simulations (handled in `R7`).
