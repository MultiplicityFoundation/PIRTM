# R7: Add simulation regression tests for modernized flows

- **Type**: Feature request
- **Labels**: `enhancement`, `tests`, `simulations`
- **Track**: C (Simulation Modernization)
- **Size**: M
- **Depends on**: R6

## Summary

Add minimal but stable regression tests for modernized simulation paths to prevent backsliding into legacy-only behavior.

## Motivation

Simulation modernization is fragile without tests; this issue adds confidence gates for future changes.

## Acceptance Criteria

- [ ] New simulation tests are added under `tests/` for selected modernized flows.
- [ ] Tests avoid flaky/random outcomes (deterministic seeds or bounded checks).
- [ ] CI includes these tests in required paths.
- [ ] Legacy-only simulation paths are excluded or marked non-blocking explicitly.

## Implementation Checklist

- [ ] Identify 2–3 representative simulation paths for coverage.
- [ ] Add deterministic fixtures and expected-behavior assertions.
- [ ] Integrate tests into `ci.yml` required matrix.
- [ ] Document simulation test scope and exclusions.

## Out of Scope

- Full benchmark/performance suite.
