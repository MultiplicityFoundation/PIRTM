# ADR-007 ETP — Design-Parameter Commitment Model

- Status: Accepted Candidate (2026-03-01)
- Decision type: Certification semantics
- Related roadmap tracks: R1, R8

## Context

The architectural contract requires stable runtime safety invariants, and the math spec defines certificate behavior around contraction bounds. The open design question is how pre-committed design bounds interact with runtime measurements for L3/L4-style ACE paths.

Supported sources:
- `docs/architecture.md` (contractivity and certificate consistency invariants)
- `docs/math_spec.md` (certificate equations and stability criteria)
- `docs/api/README.md` (`StepInfo`, `Certificate`, current public surfaces)

## Decision (Accepted Candidate)

Adopt a two-lane model for future L3/L4 evolution:
- Design parameters represent committed bounds.
- Runtime telemetry remains verification evidence.

Violation policy: if runtime exceeds committed design envelope, classify as hard invariant violation and fail certification path deterministically.

Scope decision:
- `v0.1.x` support remains centered on documented baseline certification semantics.
- Design-parameter envelope behavior is accepted as a candidate path and must be introduced behind versioned migration language and CI evidence.

## Constraints

- Must not break current `pirtm.certify` semantics documented in public API until a versioned migration is approved.
- Any new invariant behavior must be represented in CI-required tests before release-gate inclusion.

## Acceptance Criteria

- Decision language maps directly to `docs/math_spec.md` inequalities.
- Runtime-vs-design envelope behavior is testable and versioned.
- Migration impact is captured in changelog/migration docs before activation.

## Candidate Resolutions

1. `v0.1.x` continues to treat baseline certificate behavior as stable; extended commitment semantics remain candidate-gated until migration evidence is merged.
2. Envelope violations fail closed at protocol boundary validation, with level-level checks allowed as defense-in-depth.

## Execution Pass 2 (Docs + Tests)

- Scope: validate fail-closed behavior for runtime-vs-design envelope checks at protocol entry.
- Tests: `tests/test_ace_protocol_injection.py` includes deterministic failure assertions for both clamp and perturbation envelope violations under injected defaults.
- Governance note: behavior remains compatibility-safe for `v0.1.x` baseline while preserving hard-fail semantics when committed bounds are exceeded.
