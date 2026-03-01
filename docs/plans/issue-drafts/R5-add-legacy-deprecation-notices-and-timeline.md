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

- [ ] Each legacy module has explicit deprecation notice (runtime warning and/or module docstring).
- [ ] Deprecation message includes removal target version.
- [ ] `CHANGELOG.md` and one canonical docs page include the timeline.
- [ ] No regressions in existing legacy compatibility tests.

## Implementation Checklist

- [ ] Add/normalize `DeprecationWarning` emission in `_legacy` modules.
- [ ] Add module-level docstring deprecation headers.
- [ ] Add “Legacy Sunset” section in docs.
- [ ] Add changelog entry for timeline and migration pointer.

## Out of Scope

- Removing legacy modules in this issue.
