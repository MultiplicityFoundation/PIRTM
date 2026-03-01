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

- [ ] One active roadmap document is designated and linked from primary docs.
- [ ] Superseded plan sections are marked clearly as historical.
- [ ] Support matrix is published with status/stability per subsystem.
- [ ] README/examples/docs links are synchronized (including CLI gating behavior).

## Implementation Checklist

- [ ] Add “Active Roadmap” pointer in `docs/plans/README.md` or equivalent.
- [ ] Mark superseded ADR/plan sections with status tags where needed.
- [ ] Create/update support matrix section in docs.
- [ ] Cross-link release notes and migration docs from README.

## Out of Scope

- Feature implementation changes unrelated to docs/roadmap alignment.
