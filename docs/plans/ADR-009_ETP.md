# ADR-009 ETP — Certificate Type Promotion and Migration

- Status: Accepted Candidate (2026-03-01)
- Decision type: Public API evolution
- Related roadmap tracks: R1, R2

## Context

The API reference currently documents `Certificate` as the public return contract. Exploratory ETP drafts propose richer ACE certificate payloads. Promotion must preserve compatibility and release discipline.

Supported sources:
- `docs/api/README.md` (`Certificate` public type)
- `docs/math_spec.md` (existing certificate equations and semantics)
- `docs/plans/PIRTM Core Completion.md` (release-scope and migration discipline)

## Decision (Accepted Candidate)

Treat richer `AceCertificate` adoption as a versioned migration, not a silent substitution.

Migration policy draft:
1. Preserve current fields/semantics for baseline callers.
2. Add richer fields without breaking existing assertions.
3. Document deprecation horizon for legacy type checks if replacement proceeds.

Versioning decision:
- Promotion is targeted for post-`v0.1.x` unless explicitly included in a scope lock update.
- Legacy compatibility mapping is retained during transition, with deprecation language defined in migration docs before cutover.

## Constraints

- No API promotion without migration notes and release checklist evidence.
- Avoid introducing runtime warnings that break existing test harness behavior unexpectedly.

## Acceptance Criteria

- A concrete migration note exists before behavior switch.
- Critical tests include both legacy-field compatibility and richer-field assertions.
- Changelog includes upgrade guidance and compatibility window.

## Candidate Resolutions

1. Type promotion is deferred beyond the current `v0.1.x` stability surface unless release scope is explicitly amended.
2. Legacy type remains available as deprecated compatibility mapping during transition.

## Execution Pass 2 (Docs + Tests)

- Scope: pin migration behavior around `ace_certificate` and legacy compatibility mapping.
- Tests: `tests/test_certify.py` now includes explicit assertions for legacy field/key compatibility and deprecated legacy-path parity.
- Migration docs: `docs/migration/certify-v1.md` clarifies `v0.1.x` compatibility window and deprecation-first transition behavior.
