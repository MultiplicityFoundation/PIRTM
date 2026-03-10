# ADR-008 ETP — Unified ACE Telemetry Contract

- Status: Accepted Candidate (2026-03-01)
- Decision type: API/data contract
- Related roadmap tracks: R8, R9

## Context

Current public runtime traces rely on `StepInfo`, while ACE evolution requires richer level-specific evidence. The architecture and API docs favor shared data-contract layers with explicit invariants.

Supported sources:
- `docs/architecture.md` (types as shared contract layer)
- `docs/api/README.md` (`StepInfo` current required shape)
- `docs/math_spec.md` (what telemetry must support for contraction/certification math)

## Decision (Accepted Candidate)

Define a unified ACE telemetry dataclass as a superset of `StepInfo`, with explicit optional fields for higher-certification levels.

Compatibility principle:
- `StepInfo` remains valid for baseline certification.
- Higher levels require additional explicit fields and validation.

Dispatch decision:
- Protocol dispatch uses explicit capability detection with deterministic ordering.
- Requested minimum level above feasible capability is a hard error (no silent downgrade).

## Constraints

- No implicit behavior based on undocumented `None` heuristics.
- Dispatch capability must be explicit and deterministic.
- Legacy call paths remain functional until migration timeline is approved.

## Acceptance Criteria

- Unified telemetry schema has documented minimum required fields per level.
- Validation rules cover shape/range constraints and fail deterministically.
- Existing baseline tests remain green while higher-level tests are added.

## Candidate Resolutions

1. Effective dispatch is highest-feasible by default, with explicit minimum-level enforcement to prohibit unsafe downgrade-by-request.
2. Telemetry normalization is centralized in protocol API to keep validation and dispatch guarantees coherent.

## Execution Pass 1 (Docs + Tests)

- Scope: enforce protocol-centered normalization and minimum-level gate behavior.
- Tests: existing protocol suite confirms `min_level` rejection when requested level exceeds feasible telemetry support.
- Sequencing note: telemetry-schema expansion beyond current fields remains in follow-up pass after contract-level checks remain green.
