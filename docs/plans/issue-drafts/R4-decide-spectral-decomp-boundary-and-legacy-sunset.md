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

- [ ] Canonical spectral boundary decision is documented.
- [ ] Public API policy for `pirtm.spectral_decomp` is explicit (supported vs deprecated).
- [ ] Sunset timeline (target version) is documented for any deprecated surface.
- [ ] README/docs are aligned with the decision.
- [ ] Follow-up tasks for implementation impacts are listed.

## Implementation Checklist

- [ ] Draft ADR-style decision note in `docs/plans/` or `docs/architecture.md`.
- [ ] Update module status table (core vs legacy).
- [ ] Add changelog entry reflecting boundary decision.
- [ ] Open follow-up issues (e.g., deprecation wrappers/import path updates).

## Out of Scope

- Full migration of simulation code (handled in `R6`).
