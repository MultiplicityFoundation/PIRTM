# R2: Finalize release notes and migration notes

- **Type**: Documentation
- **Labels**: `documentation`, `release`
- **Track**: A (Release Readiness)
- **Size**: S
- **Depends on**: R1

## Summary

Convert `CHANGELOG.md` unreleased items into finalized release notes and add migration notes for public-facing behavior changes (including transpiler CLI output gating).

## Motivation

Release-quality notes are required for users to adopt the stable release safely and understand behavior changes.

## Acceptance Criteria

- [x] `CHANGELOG.md` contains a complete release section for the target version.
- [x] Migration notes document API/CLI behavior changes since pre-release.
- [x] Transpiler flags `--emit-witness` / `--emit-lambda-events` are documented in release notes.
- [x] Notes include any deprecations and planned removal timelines.
- [x] Notes are cross-linked from `README.md` or docs index.

## Implementation Checklist

- [x] Create release heading in `CHANGELOG.md` with date placeholder.
- [x] Group changes into Added/Changed/Deprecated/Fixed.
- [x] Add migration doc entry or update existing migration pages.
- [x] Add links to key docs (`README.md`, `examples/README.md`, plan docs).
- [ ] Request maintainer review for wording and completeness.

## Completion Notes (2026-03-01)

- Added `## [0.1.0] - YYYY-MM-DD` draft release section in `CHANGELOG.md` with `Added` / `Changed` / `Deprecated` / `Fixed` groupings.
- Added migration guide `docs/migration/v0.1.0.md` documenting CLI/API behavior changes since pre-release.
- Documented transpiler output-gating flags (`--emit-witness`, `--emit-lambda-events`) in release notes and migration notes.
- Added deprecation/timeline signals in release notes and linked the legacy-boundary follow-up (`R4`, `R5`).
- Cross-linked release and migration docs from `README.md` documentation index.

## Out of Scope

- Running release automation or publishing.
