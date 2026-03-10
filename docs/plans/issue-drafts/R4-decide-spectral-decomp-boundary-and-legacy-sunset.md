# R4: Decide `spectral_decomp` support boundary and legacy sunset

- **Type**: Feature request
- **Labels**: `enhancement`, `architecture`, `legacy`
- **Track**: B (Legacy Boundary)
- **Size**: M
- **Depends on**: R1

## Summary

Define whether `pirtm.spectral_decomp` remains a supported public module or is fully treated as legacy, and set a versioned sunset policy.

## Motivation

Current state has both top-level and `_legacy` spectral surfaces. Ambiguity increases maintenance cost and user confusion.

## Acceptance Criteria

- [x] Canonical spectral boundary decision is documented.
- [x] Public API policy for `pirtm.spectral_decomp` is explicit (supported vs deprecated).
- [x] Sunset timeline (target version) is documented for any deprecated surface.
- [x] README/docs are aligned with the decision.
- [x] Follow-up tasks for implementation impacts are listed.

## Implementation Checklist

- [x] Draft ADR-style decision note in `docs/plans/` or `docs/architecture.md`.
- [x] Update module status table (core vs legacy).
- [x] Add changelog entry reflecting boundary decision.
- [x] Open follow-up issues (e.g., deprecation wrappers/import path updates).

## Completion Notes (2026-03-01)

- Canonical boundary decision documented in `docs/architecture.md` under “Spectral API Boundary Decision (R4)”.
- Policy set: `pirtm.spectral_decomp` remains supported public API for `v0.1.x`; `_legacy` spectral paths are transitional/deprecated.
- Sunset timeline documented: strict deprecation messaging in `v0.2.x`, target removal of deprecated `_legacy` spectral paths in `v0.3.0`.
- Roadmap/docs alignment completed in:
	- `docs/plans/PIRTM Core Completion.md`
	- `docs/plans/README.md`
	- `README.md`
	- `CHANGELOG.md`
- Follow-up execution remains tracked in existing backlog items `R5` (module-level deprecations/timeline) and `R6` (simulation modernization).

## Out of Scope

- Full migration of simulation code (handled in `R6`).
