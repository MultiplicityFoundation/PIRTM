# ADR-011 ETP — Matrix Immutability Contract for ACE Levels

- Status: Accepted Candidate (2026-03-01)
- Decision type: Runtime correctness contract
- Related roadmap tracks: R8, R9

## Context

ACE level functions may consume shared matrix objects. Copy-on-normalize and shallow dataclass replacement patterns are efficient, but require a strict no-mutation contract to prevent caller-state corruption.

Supported sources:
- `docs/architecture.md` (invariant-driven runtime model)
- `docs/release_checklist.md` (critical suite policy for ACE)
- `docs/plans/PIRTM Core Completion.md` (quality gate consolidation)

## Decision (Accepted Candidate)

Adopt a named contract for ACE level implementations:
- Input contraction matrices are read-only.
- In-place mutation is prohibited in certification paths.

Enforcement model (draft):
- Document contract in level docstrings.
- Add debug/test guard for fingerprint-before/after verification.
- Pin with CI-required immutability tests.

Enforcement decision:
- Guard execution is debug/test by default, with CI enabling it through test configuration.
- Centralized protocol normalization is preserved; per-level guard usage remains explicit and test-enforced.

## Acceptance Criteria

- Matrix immutability contract is documented in code and docs.
- CI includes tests covering all matrix-consuming levels.
- Violation mode is deterministic and actionable.

## Candidate Resolutions

1. Matrix immutability guard is debug/test first, not always-on production runtime.
2. Safeguards are context-manager based inside level implementations, with protocol-level tests enforcing coverage.

## Execution Pass 1 (Docs + Tests)

- Scope: validate guard behavior and maintain read-only matrix contract across L2-L4.
- Tests: `tests/test_ace_matrix_immutability.py` includes positive no-mutation checks and explicit mutation-failure assertion under debug.
- Runtime model: guard remains debug/test-oriented (`tests/conftest.py` enables it globally).
