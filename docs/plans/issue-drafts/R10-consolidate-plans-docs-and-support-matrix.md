# R10: Consolidate plans/docs into active roadmap and support matrix

- **Type**: Documentation
- **Labels**: `documentation`, `roadmap`
- **Track**: E (Roadmap and Documentation Sync)
- **Size**: M
- **Depends on**: R3, R4, R8

## Summary

Consolidate planning/docs into one active roadmap source and publish a concise support matrix (core, ACE, transpiler, legacy).

## Motivation

Plan docs currently mix historical and active material. A single source of truth is required for maintainability and onboarding.

## Acceptance Criteria

- [x] One active roadmap document is designated and linked from primary docs.
- [x] Superseded plan sections are marked clearly as historical.
- [x] Support matrix is published with status/stability per subsystem.
- [x] README/examples/docs links are synchronized (including CLI gating behavior).

## Implementation Checklist

- [x] Add “Active Roadmap” pointer in `docs/plans/README.md` or equivalent.
- [x] Mark superseded ADR/plan sections with status tags where needed.
- [x] Create/update support matrix section in docs.
- [x] Cross-link release notes and migration docs from README.

## Completion Notes (2026-03-01)

- Added canonical plans index at `docs/plans/README.md` with active roadmap pointer and explicit status map (`Active`, `Reference`, `Historical`, `Historical/Exploratory`).
- Marked superseded tier expansion docs and exploratory ADR artifacts as historical in the plans status map.
- Published support matrix in both `docs/plans/README.md` and `docs/plans/PIRTM Core Completion.md`.
- Synchronized docs links from `README.md` and `docs/README.md` to include active roadmap, plans index, release notes, and migration notes.

## Out of Scope

- Feature implementation changes unrelated to docs/roadmap alignment.
