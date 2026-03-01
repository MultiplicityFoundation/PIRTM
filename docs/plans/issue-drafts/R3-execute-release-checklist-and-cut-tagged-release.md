# R3: Execute release checklist and cut tagged release

- **Type**: Feature request
- **Labels**: `enhancement`, `release`
- **Track**: A (Release Readiness)
- **Size**: M
- **Depends on**: R2

## Summary

Run the full release checklist and perform release cut (version bump, tag, artifacts, workflow verification).

## Motivation

The project is currently on a development version. A tagged stable release is required to complete core-completion goals.

## Acceptance Criteria

- [ ] Lint/type/test/conformance checks pass on release commit.
- [ ] Version is bumped consistently (`pyproject.toml`, `src/pirtm/__init__.py`, and release notes).
- [ ] Build artifacts validate successfully.
- [ ] Release tag is created and pushed.
- [ ] Release workflow completes successfully.
- [ ] Post-release `Unreleased` section is re-opened for next cycle.

## Implementation Checklist

- [ ] Execute `docs/release_checklist.md` top to bottom.
- [ ] Run `python scripts/bump_version.py` with chosen increment.
- [ ] Run `python -m build` and `python -m twine check dist/*`.
- [ ] Run optional integrity steps (`make sbom`, signing/verify if used).
- [ ] Create/push tag and confirm `release.yml` pass.
- [ ] Record release evidence (workflow URL + tag + artifact checksums).

## Out of Scope

- Major new feature development.
