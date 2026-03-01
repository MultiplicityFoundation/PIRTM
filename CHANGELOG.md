# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added
- Placeholder for post-`v0.1.0` development entries.

### Changed
- Placeholder for post-`v0.1.0` development entries.

### Deprecated
- Placeholder for post-`v0.1.0` development entries.

### Fixed
- Placeholder for post-`v0.1.0` development entries.

## [0.1.0] - YYYY-MM-DD

### Release Scope Note (`v0.1.0` draft)
- Scope lock is tracked in `docs/plans/PIRTM Core Completion.md` under “Release Scope: v0.1.0 (Scope Lock Draft)”.
- `v0.1.0` is treated as a public-facing semantic-version promise for explicitly in-scope surfaces.
- In-scope release gating requires: CI green on scoped modules, enforced/tested L0 invariants, and no unowned release blockers.
- Out-of-scope items for this cut include MCP/agent integrations, UI surfaces, Terraform/cloud provisioning, and non-blocking cross-repo integrations.
- `R1` scope lock unblocks `R2` (release notes), `R3` (release execution), and `R8` (release gate matrix).

### Added
- Tier 5 governance: `CONTRIBUTING.md`, `SECURITY.md`, PR template, and issue templates.
- Conformance profile runner via `pirtm-conformance` CLI.
- Integration bridge for DRMM-style workflows in `pirtm.integrations.drmm_bridge`.
- Release and nightly workflows for CI hardening.
- Release automation script and checklist.
- Supply-chain `Makefile` targets for SBOM/signature workflows.
- Phase-scoped transpiler CLI with descriptor-driven workflows and dedicated command parser wiring.
- ACE protocol package scaffolding (`pirtm.ace.*`) and immutability/injection-focused regression tests.
- Issue-draft backlog set for core completion tracks (`R1`–`R10`) under `docs/plans/issue-drafts/`.

### Changed
- Transpiler JSON output now omits `witness_json` and `lambda_events` by default; use `--emit-witness` and `--emit-lambda-events` for explicit inclusion.
- Metadata parsing for transpiler CLI now fails with explicit object/JSON validation errors.
- Core completion plan updated from historical bootstrap gaps to remaining-deltas roadmap execution.
- Documentation expanded for transpiler hash/export behavior and CLI usage parity.
- Spectral API boundary decision recorded: `pirtm.spectral_decomp` remains supported public API for `v0.1.x`; `_legacy` spectral paths remain transitional.

### Deprecated
- `_legacy` surfaces remain deprecated; module-by-module sunset policy and target removal version are tracked in roadmap items `R4` and `R5`.
- Legacy `Certificate` compatibility path is deprecated in favor of ACE-native certificate typing; see migration notes (`docs/migration/certify-v1.md`).
- `_legacy` spectral entry points are targeted for sunset in `v0.3.0` (with stricter migration messaging in `v0.2.x`).

### Fixed
- CLI tests now assert and protect explicit output-gating behavior for witness and Lambda event payloads.
- Transpiler CLI contracts hardened for malformed metadata inputs and non-object metadata payloads.
