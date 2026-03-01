# ADR-010 ETP — ACE/PETC Development Blueprint (Release-Aligned)

- Status: Accepted Candidate (2026-03-01)
- Decision type: Execution architecture
- Related roadmap tracks: R8, R9, R10

## Context

PIRTM now includes both core and ACE-oriented modules, but release readiness depends on explicit gate alignment and stable support boundaries. Prior ADR-010 material mixed design and implementation proposals without release-grade traceability.

Supported sources:
- `docs/architecture.md` (module graph and dependency direction)
- `docs/release_checklist.md` (required jobs and critical-suite policy)
- `docs/plans/PIRTM Core Completion.md` (remaining deltas and sequencing)

## Decision (Accepted Candidate)

Maintain ADR-010 as a release-aligned blueprint document:
- Describe target module boundaries and contracts.
- Bind each implementation phase to required CI gates.
- Treat speculative levels/features as non-binding until tested.

Release candidate focus:
- Phase 1 and Phase 2 are candidate-gating work for near-term execution.
- Phase 3 and Phase 4 are accepted as follow-through milestones once contract and protocol baselines are merged.

## Delivery Phases (Candidate)

1. Contract stabilization (types + invariants + migration notes).
2. Protocol composition (telemetry normalization + deterministic dispatch).
3. Provenance hardening (witness/ledger/ordering integrity).
4. CI elevation (critical-suites and release evidence).

## Acceptance Criteria

- Every phase has measurable gates tied to release checklist jobs.
- No blueprint claim is considered complete without corresponding test coverage.
- Public API impacts are tracked in migration and changelog docs.

## Candidate Resolutions

1. Mandatory next-cut candidate items are contract stabilization and protocol composition.
2. Provenance hardening remains release-aligned but not mandatory until tied to explicit gate criteria.

## Execution Pass 4 (Docs + Tests)

- Scope: implement protocol composition determinism for batch telemetry dispatch.
- Code: `AceProtocol.certify` selects representative telemetry by highest feasible certification level first, with `q` as deterministic tie-breaker.
- Tests: `tests/test_ace_protocol.py` includes capability-priority dispatch and same-level tie-break assertions.
- Release alignment: behavior remains non-breaking for single-item calls and improves deterministic composition semantics for multi-item certification inputs.
