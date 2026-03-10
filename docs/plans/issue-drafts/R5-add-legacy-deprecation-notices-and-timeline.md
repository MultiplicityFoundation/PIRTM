# R5: Add per-module legacy deprecation notices and timeline

- **Type**: Feature request
- **Labels**: `enhancement`, `legacy`, `documentation`
- **Track**: B (Legacy Boundary)
- **Size**: S
- **Depends on**: R4

## Summary

Add explicit deprecation warnings/notices at module granularity for legacy modules and publish a concrete removal schedule.

## Motivation

Package-level warnings exist, but per-module guidance and timelines are needed for safer migration planning.

## Acceptance Criteria

- [x] Each legacy module has explicit deprecation notice (runtime warning and/or module docstring).
- [x] Deprecation message includes removal target version.
- [x] `CHANGELOG.md` and one canonical docs page include the timeline.
- [ ] No regressions in existing legacy compatibility tests.

## Implementation Checklist

- [x] Add/normalize `DeprecationWarning` emission in `_legacy` modules.
- [x] Add module-level docstring deprecation headers.
- [x] Add “Legacy Sunset” section in docs.
- [x] Add changelog entry for timeline and migration pointer.

## Completion Notes (2026-03-01)

- Added explicit per-module deprecation headers and `DeprecationWarning` emissions to:
	- `src/pirtm/_legacy/pir_tensor.py`
	- `src/pirtm/_legacy/recursive_ops.py`
	- `src/pirtm/_legacy/spectral_decomp.py`
- Updated package-level warning in `src/pirtm/_legacy/__init__.py` to align with removal target `v0.3.0`.
- Added canonical “Legacy Sunset Timeline (R5)” section in `docs/architecture.md` with module-by-module migration targets and version policy (`v0.1.x`/`v0.2.x`/`v0.3.0`).
- Added changelog deprecation line pointing to per-module notices and canonical timeline docs.
- Validation note: modern spectral suites pass (`tests/test_spectral_decomp_modern.py`, `tests/test_spectral_gov.py`); legacy spectral collection currently requires `sympy` (`.[legacy]`) in the executing environment before full legacy compatibility confirmation.

## Out of Scope

- Removing legacy modules in this issue.
