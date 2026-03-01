# R9: Align required CI paths with ACE/transpiler critical suites

- **Type**: Feature request
- **Labels**: `enhancement`, `ci`, `tests`
- **Track**: D (CI/Quality Gate Consolidation)
- **Size**: S
- **Depends on**: R8

## Summary

Update CI workflow job definitions so required paths explicitly cover ACE and transpiler critical suites.

## Motivation

Recent work concentrated in ACE and transpiler surfaces; required CI should enforce these areas on release-critical changes.

## Acceptance Criteria

- [x] Required CI jobs execute ACE critical tests.
- [x] Required CI jobs execute transpiler CLI/workflow critical tests.
- [x] Path filters or job conditions do not skip critical suites for relevant changes.
- [x] Workflow documentation reflects enforced suites.

## Implementation Checklist

- [x] Identify critical test commands and expected duration.
- [x] Update `.github/workflows/ci.yml` required jobs/steps.
- [ ] Validate with a PR touching ACE + transpiler files.
- [x] Document the critical-suite policy near release gates.

## Completion Notes (2026-03-01)

- Added dedicated `critical-suites` job to `.github/workflows/ci.yml`.
- Critical suite now explicitly runs ACE + transpiler tests:
	- `tests/test_cli_transpile.py`
	- `tests/test_transpiler.py`
	- `tests/test_ace_protocol.py`
	- `tests/test_ace_protocol_injection.py`
	- `tests/test_ace_matrix_immutability.py`
- CI trigger remains branch-wide for `Multiplicity` push/PR; no path filter currently skips critical suites.
- Updated `docs/release_checklist.md` gate matrix and critical-suite policy to reference the required `critical-suites` job.

## Out of Scope

- Expanding full test coverage beyond critical suites.
