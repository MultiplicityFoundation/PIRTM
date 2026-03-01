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

- [ ] Required CI jobs execute ACE critical tests.
- [ ] Required CI jobs execute transpiler CLI/workflow critical tests.
- [ ] Path filters or job conditions do not skip critical suites for relevant changes.
- [ ] Workflow documentation reflects enforced suites.

## Implementation Checklist

- [ ] Identify critical test commands and expected duration.
- [ ] Update `.github/workflows/ci.yml` required jobs/steps.
- [ ] Validate with a PR touching ACE + transpiler files.
- [ ] Document the critical-suite policy near release gates.

## Out of Scope

- Expanding full test coverage beyond critical suites.
