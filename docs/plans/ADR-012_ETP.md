# ADR-012 ETP — Envelope Validation and TRL Claim Discipline

- Status: Accepted Candidate (2026-03-01)
- Decision type: Safety/compliance semantics
- Related roadmap tracks: R1, R8

## Context

ETP proposals introduce stronger claims around design-parameter commitment and higher-level certification confidence. Those claims must remain aligned with runtime invariants and release evidence.

Supported sources:
- `docs/architecture.md` (contractivity and certificate consistency)
- `docs/math_spec.md` (bound equations and stability regime)
- `docs/release_checklist.md` (required evidence before release)

## Decision (Accepted Candidate)

Treat TRL-level language as governed metadata:
- Claim level upgrades only when backed by deterministic checks and CI evidence.
- Separate “designed bound” claims from “runtime measured” evidence in telemetry/certificate details.

Violation handling draft:
- Design-time invalid commitments fail configuration validation.
- Runtime envelope escapes fail closed during certification path.

Governance decision:
- Canonical TRL mapping lives in code-level enums/types and is mirrored in release-facing docs.
- Minimum evidence for TRL-elevation claims includes deterministic tests, required CI passing, and release-note traceability.

## Acceptance Criteria

- TRL mapping and criteria are explicitly documented and testable.
- Certificate payload distinguishes commitment vs measurement fields.
- Release notes include any claim-surface changes.

## Candidate Resolutions

1. Canonical TRL mapping is code-first and docs-mirrored.
2. TRL elevation statements require tests + CI evidence + release-note updates in the same delivery path.

## Execution Pass 3 (Docs + Tests)

- Scope: tighten TRL metadata evidence and commitment-vs-runtime field separation in certificate payloads.
- Code: L3/L4 certificate details include explicit runtime evidence fields alongside designed commitment fields.
- Tests: `tests/test_ace_trl_metadata.py` pins code-first TRL mapping and verifies designed/runtime evidence keys for L3 and L4 payloads.
- Release alignment: pass is non-breaking for `v0.1.x` and improves audit traceability for claim-surface updates.
