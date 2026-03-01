# R8: Define required CI release gate matrix

- **Type**: Documentation
- **Labels**: `documentation`, `ci`, `release`
- **Track**: D (CI/Quality Gate Consolidation)
- **Size**: S
- **Depends on**: R1

## Summary

Define the release-quality gate matrix (which jobs are mandatory, pass criteria, and acceptable exceptions).

## Motivation

CI workflows exist, but release criteria are not codified as an explicit gate contract.

## Acceptance Criteria

- [x] A release gate matrix is documented in one canonical file.
- [x] Required checks and minimum outcomes are explicit (lint/type/test/conformance/build).
- [x] Non-blocking checks are explicitly identified.
- [x] Flaky/failure triage process is documented.

## Implementation Checklist

- [x] Add “Release Gate Matrix” section to `docs/release_checklist.md` or dedicated doc.
- [x] Map each gate to workflow/job names.
- [x] Add owner/escalation notes for gate failures.
- [x] Link matrix from core plan and contributing docs.

## Completion Notes (2026-03-01)

- Added canonical “Release Gate Matrix (R8 Canonical)” section to `docs/release_checklist.md`.
- Matrix now maps required gates to actual workflow/job surfaces in `.github/workflows/ci.yml`, `.github/workflows/nightly.yml`, and `.github/workflows/release.yml`.
- Added owner and escalation columns to make blocker handling explicit.
- Added critical-suite policy (ACE/transpiler coverage) and flaky/failure triage workflow.
- Added cross-link to matrix from `CONTRIBUTING.md`.
- PR-B evidence snapshot added to `docs/release_checklist.md` with workflow/job inventory, GitHub run links, and local gate results.
- Local gate rerun passed after lint fix (`ruff check`, `ruff format --check`, `mypy`, `pytest`).
- Branch-protection required-check API query returned `403` for integration token; admin-side UI confirmation remains required.

## Out of Scope

- Workflow code changes (covered by `R9`).
