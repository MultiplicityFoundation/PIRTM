# ADR-006 ETP — ACE/PETC Modernization Baseline

- Status: Accepted Candidate (2026-03-01)
- Decision type: Architecture + delivery sequencing
- Related roadmap tracks: R8, R9, R10

## Context

PIRTM already exposes stable public contractive-core APIs and an active, stabilizing ACE surface. The active roadmap identifies documentation and release-gate alignment as current deltas, while older ETP ADR materials are exploratory and not release-authoritative.

Supported sources:
- `docs/architecture.md` (module graph, invariants, Tier 7 integration flow)
- `docs/math_spec.md` (contractive recurrence, ACE certificate math, PETC constraints)
- `docs/release_checklist.md` (release gate matrix and required critical suites)
- `docs/plans/PIRTM Core Completion.md` (remaining deltas R8–R10)
- `docs/plans/README.md` (active vs historical planning policy)

## Decision (Accepted Candidate)

Start ETP ADR-006..013 as a constrained documentation track that:
1. Converts exploratory blueprint content into concise ADR records.
2. Anchors each decision to current supported docs and current code surfaces.
3. Defers implementation claims until tied to CI gate evidence.

Decision addendum:
- Canonical placement remains under `docs/plans/` for the v0.1.x cycle.
- ADR-013, ADR-011, and ADR-008 are treated as near-term release-aligned candidates; ADR-009/007/012/010/006 remain sequencing candidates with no immediate API break required.

## Scope

In scope:
- ADR narrative normalization for `ADR-006_ETP.md` through `ADR-013_ETP.md`.
- Explicit references to supported architecture/math/release documents.
- Clear acceptance criteria for future implementation PRs.

Out of scope:
- Declaring new release policy outside existing gate matrix.
- Promoting exploratory behavior to supported API without tests + CI evidence.

## Acceptance Criteria

- Each ADR 006–013 has `Status`, `Context`, `Decision`, `Acceptance Criteria`, and `Candidate Resolutions`.
- Each ADR references only supported docs or current repo code.
- `docs/plans/README.md` labels ADR-006..013 as active accepted candidates.

## Candidate Resolutions

1. Final accepted ADRs stay in `docs/plans/` until a dedicated ADR registry is created by roadmap work outside this sequence.
2. Release-priority ordering for candidate implementation is `013 -> 011 -> 008 -> 009 -> 007 -> 012 -> 010 -> 006`.

## Execution Pass 5 (Docs + Tests)

- Scope: close the current ADR execution sequence with baseline-consolidation regression evidence.
- Tests: `tests/test_ace_etp_baseline.py` validates representative guarantees from Passes 1–4 in a compact release-oriented baseline suite.
- Coverage focus: inject/copy semantics, legacy-compat mapping, deterministic batch composition, and claim-vs-measurement certificate details.
- Release note: no new API surface; this pass codifies sequence outcomes into a single stability checkpoint.
