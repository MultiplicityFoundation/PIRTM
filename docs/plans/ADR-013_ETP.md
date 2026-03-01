# ADR-013 ETP — Protocol Defaults and Inject-if-Absent Semantics

- Status: Accepted Candidate (2026-03-01)
- Decision type: Protocol API behavior
- Related roadmap tracks: R8, R9

## Context

Higher ACE levels require design parameters that may be repetitive across sessions. For usability and auditability, protocol-level defaults and per-telemetry explicit values must coexist without ambiguity.

Supported sources:
- `docs/architecture.md` (protocol-layer integration and invariants)
- `docs/api/README.md` (public type surfaces and caller expectations)
- `docs/release_checklist.md` (critical suites and deterministic behavior policy)

## Decision (Accepted Candidate)

Adopt inject-if-absent semantics:
- Protocol defaults are applied only when telemetry fields are `None`.
- Explicit telemetry values always take precedence.
- Injection occurs before validation so invariants evaluate committed values.

Mutability rule: caller-provided telemetry objects remain unchanged after certification unless API explicitly documents mutation.

Normalization decision:
- Normalization returns original object only when no injection is needed.
- When injection is required, normalization uses a copy-on-normalize path to preserve caller immutability.

## Acceptance Criteria

- Cross-protocol reuse tests validate correct commitment selection.
- Caller-object immutability is covered by tests.
- Behavior is documented in protocol API docstrings and migration notes.

## Candidate Resolutions

1. Identity fast-path is accepted when no injection is needed.
2. Injection diagnostics are optional and non-blocking for current candidate acceptance.

## Execution Pass 1 (Docs + Tests)

- Scope: implement and verify copy-on-normalize semantics with explicit identity fast-path.
- Code: `AceProtocol._inject_design_params` returns original telemetry when no injection is needed, and copy-on-normalize only when injection is required.
- Tests: `tests/test_ace_protocol_injection.py` includes identity-fast-path assertion and copy-on-injection assertions.
- Result target: cross-protocol reuse remains safe; caller object immutability remains preserved when injection occurs.
