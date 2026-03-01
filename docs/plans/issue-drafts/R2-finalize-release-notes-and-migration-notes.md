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

- [ ] `CHANGELOG.md` contains a complete release section for the target version.
- [ ] Migration notes document API/CLI behavior changes since pre-release.
- [ ] Transpiler flags `--emit-witness` / `--emit-lambda-events` are documented in release notes.
- [ ] Notes include any deprecations and planned removal timelines.
- [ ] Notes are cross-linked from `README.md` or docs index.

## Implementation Checklist

- [ ] Create release heading in `CHANGELOG.md` with date placeholder.
- [ ] Group changes into Added/Changed/Deprecated/Fixed.
- [ ] Add migration doc entry or update existing migration pages.
- [ ] Add links to key docs (`README.md`, `examples/README.md`, plan docs).
- [ ] Request maintainer review for wording and completeness.

## Out of Scope

- Running release automation or publishing.
