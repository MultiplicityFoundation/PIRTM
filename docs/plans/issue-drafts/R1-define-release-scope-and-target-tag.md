# R1: Define release scope and target tag

- **Type**: Feature request
- **Labels**: `enhancement`, `release`
- **Track**: A (Release Readiness)
- **Size**: S
- **Depends on**: none

## Summary

Define and approve the first stable release scope and tag target (recommended `v0.1.0`) from current mainline, including explicit in-scope/out-of-scope items.

## Motivation

Current repo state is near release-ready but lacks a frozen scope. Without scope lock, release-critical tasks cannot be finalized deterministically.

## Acceptance Criteria

- [ ] Release target is explicitly selected (`v0.1.0` or alternative) and documented.
- [ ] In-scope features/modules are listed in a release scope section.
- [ ] Out-of-scope/deferred items are listed with rationale.
- [ ] Release blocker list is defined with owners.
- [ ] Go/No-Go criteria are documented and agreed.

## Implementation Checklist

- [ ] Add scope decision to `docs/plans/PIRTM Core Completion.md`.
- [ ] Add release scope note under `CHANGELOG.md` unreleased section.
- [ ] Record decision date and responsible approver.
- [ ] Link downstream issues (`R2`, `R3`, `R8`) from this issue.

## Out of Scope

- Cutting tags or publishing artifacts.
- Code changes unrelated to scope freeze.
