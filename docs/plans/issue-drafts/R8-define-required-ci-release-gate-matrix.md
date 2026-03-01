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

- [ ] A release gate matrix is documented in one canonical file.
- [ ] Required checks and minimum outcomes are explicit (lint/type/test/conformance/build).
- [ ] Non-blocking checks are explicitly identified.
- [ ] Flaky/failure triage process is documented.

## Implementation Checklist

- [ ] Add “Release Gate Matrix” section to `docs/release_checklist.md` or dedicated doc.
- [ ] Map each gate to workflow/job names.
- [ ] Add owner/escalation notes for gate failures.
- [ ] Link matrix from core plan and contributing docs.

## Out of Scope

- Workflow code changes (covered by `R9`).
