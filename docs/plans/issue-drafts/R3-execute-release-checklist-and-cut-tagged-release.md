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

- [x] Lint/type/test/conformance checks are enforced in release workflow gate before artifact build.
- [x] Version bump tooling supports consistent prerelease → stable promotion (`pyproject.toml`, `src/pirtm/__init__.py`, and release notes/changelog date finalization).
- [x] Build artifacts and checksums are validated in release workflow (`build`, `twine check`, `SHA256SUMS`).
- [ ] Release tag is created and pushed.
- [ ] Release workflow completes successfully.
- [ ] Post-release `Unreleased` section is re-opened for next cycle.

## Implementation Checklist

- [ ] Execute `docs/release_checklist.md` top to bottom.
- [ ] Run `python scripts/bump_version.py` with chosen increment (`release` mode now supported for prerelease finalization).
- [x] Run `python -m build` and `python -m twine check dist/*` (enforced in `release.yml`).
- [x] Run optional integrity steps (`make sbom`, signing/verify if used) (tracked as optional in checklist).
- [ ] Create/push tag and confirm `release.yml` pass.
- [ ] Record release evidence (workflow URL + tag + artifact checksums).

## Completion Notes (2026-03-01)

- Hardened `.github/workflows/release.yml` with mandatory `gate` job (lint, type-check, ACE/transpiler critical suites, conformance) before artifact build/publish.
- Added `workflow_dispatch` input `publish_to_pypi` to support safe dry-run execution without accidental publish.
- Added release artifact checksum output (`dist/SHA256SUMS`) and evidence requirement in release checklist.
- Extended `scripts/bump_version.py` with `release` mode to convert prerelease versions (e.g., `0.1.0dev0`) into stable versions while finalizing changelog release date.
- Captured preflight evidence on `Multiplicity`:
	- Critical suites: `41 passed`
	- Conformance: `profile=core` and `profile=integrity` passed
	- Artifacts: build + `twine check` passed, `dist/SHA256SUMS` generated
- Lint/format release-gate debt has been cleared (`ruff check` and `ruff format --check` now pass).
- Current release-cut blocker: strict `mypy src` gate still fails with pre-existing typing debt outside this lint-focused cleanup scope.

## Out of Scope

- Major new feature development.
