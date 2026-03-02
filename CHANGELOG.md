# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added
- New primary certificate API: `contraction_certificate(info, *, tail_norm=0.0)` returning `Certificate` for standard contraction validation.
- PETC helper APIs: `compute_coverage(chain, a, b)` and `validate_petc_chain(...)` with explicit invariant diagnostics.
- New `pirtm petc` CLI commands: `coverage` and `validate` for JSON chain analysis.
- Migration guide for certificate API clarification: `docs/migration/v0.1.1.md`.

### Changed
- Top-level exports/docs now position `contraction_certificate()` as the recommended default path; `ace_certificate()` remains for ACE-native diagnostics.
- Language spec §5 now distinguishes standard certificate usage from ACE diagnostics and includes explicit API mapping.
- Ruff configuration now excludes notebook paths (`examples/*.ipynb`, `notebooks/*.ipynb`) from repository lint gating.

### Deprecated
- `legacy_ace_certificate()` deprecation guidance now points to `contraction_certificate()`.

### Fixed
- CLI typing/lint regressions introduced during PETC CLI integration were resolved (`mypy` clean).
- Example scripts and tooling import/style issues were cleaned up to restore full lint pass.

## [0.1.0] - 2026-03-01

### Release Scope Note (`v0.1.0`)
- Scope lock is tracked in `docs/plans/PIRTM Core Completion.md` under “Release Scope: v0.1.0 (Scope Lock Draft)”.
- `v0.1.0` is treated as a public-facing semantic-version promise for explicitly in-scope surfaces.
- In-scope release gating requires: CI green on scoped modules, enforced/tested L0 invariants, and no unowned release blockers.
- Out-of-scope items for this cut include MCP/agent integrations, UI surfaces, Terraform/cloud provisioning, and non-blocking cross-repo integrations.
- Repository directories `frontend/`, `notebooks/`, and `papers/` are explicitly out of package release scope for `v0.1.0` and are not part of the `pirtm` public API/stability contract.
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
- Per-module legacy deprecation notices now include explicit `v0.3.0` removal target and migration pointers; canonical timeline is documented in `docs/architecture.md`.

### Fixed
- CLI tests now assert and protect explicit output-gating behavior for witness and Lambda event payloads.
- Transpiler CLI contracts hardened for malformed metadata inputs and non-object metadata payloads.
