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

- [x] New simulation tests are added under `tests/` for selected modernized flows.
- [x] Tests avoid flaky/random outcomes (deterministic seeds or bounded checks).
- [x] CI includes these tests in required paths.
- [x] Legacy-only simulation paths are excluded or marked non-blocking explicitly.

## Implementation Checklist

- [x] Identify 2–3 representative simulation paths for coverage.
- [x] Add deterministic fixtures and expected-behavior assertions.
- [x] Integrate tests into `ci.yml` required matrix.
- [x] Document simulation test scope and exclusions.

## Completion Notes (2026-03-01)

- Added deterministic modernized simulation regression suite: `tests/test_simulations_modernized.py`.
- Covered representative modernized paths:
	- `QARIEngine` determinism + history/metric consistency
	- `QuantumFeedbackSimulator` determinism + analysis contract checks
- Added deterministic seed support to `QuantumFeedbackSimulator` for reproducible test behavior.
- Added simulation regression suite to required `critical-suites` CI job in `.github/workflows/ci.yml`.
- Documented release-gate scope note that research-only legacy simulation path (`riemann_verification.py`) is currently non-blocking.

## Out of Scope

- Full benchmark/performance suite.
