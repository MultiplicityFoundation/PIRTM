# PIRTM Open-Source Core Completion Plan

## Status Snapshot (2026-03-01)

This plan started as a baseline gap analysis and is now partially historical. Current repository status indicates substantial completion of the original Tier 1–4 blocking items:

- Packaging exists (`pyproject.toml`) with project scripts, optional dependencies, and `src/pirtm/` layout.
- CI exists under `.github/workflows/` (`ci.yml`, `nightly.yml`, `release.yml`).
- Core modules listed as missing in the original audit (including `petc.py`, `weights.py`, `gain.py`, `csc.py`) are present in `src/pirtm/`.
- Contractive-core and integration-oriented tests are present across `tests/` (including recurrence/projection/certify/petc/weights/integration coverage).
- User-facing docs and examples now include transpiler CLI output-gating behavior (`--emit-witness`, `--emit-lambda-events`) in `README.md` and `examples/README.md`.

Use the remainder of this document as historical context; execution should prioritize remaining deltas and modernization tasks rather than already-completed bootstrap work.

## Remaining Deltas Roadmap (2026-03-01)

This section replaces the historical gap list with only unfinished work items for the current repository.

### Delta A — Release Readiness and Version Cut (Highest Priority)

Current state: package version remains development (`0.1.0dev0`) and `CHANGELOG.md` has `Unreleased` entries only.

**Deliverables**
- Define release scope and target tag (recommended: `v0.1.0` stabilization cut from current mainline).
- Finalize changelog sections into release notes (breaking changes, migration notes, CLI behavior changes).
- Execute release checklist end-to-end (`ruff`, `mypy`, `pytest`, conformance, build, integrity checks).
- Tag and publish release artifacts.

**Dependencies**: none.

## Release Scope: v0.1.0 (Scope Lock Draft)

**Decision date**: 2026-02-28  
**Approver**: Lead Multiplicity Theorist (final sign-off pending name record)

### Central Tension

Scope fidelity vs. release velocity: a conservative freeze delays `R2`, `R3`, and `R8`; an aggressive freeze risks shipping an unvetted contract that weakens L0 invariant guarantees or expands legal surface area.

### Precision Decision

`v0.1.0` is treated as a **public-facing semantic-version contract** for the explicitly in-scope surfaces below (not just an internal coordination tag). This means in-scope API/behavior is freeze-controlled and requires explicit approver sign-off.

### Levers

| Lever | Owner | Metric | Horizon |
|---|---|---|---|
| Scope lock decision published | Lead Multiplicity Theorist | PR merged to this file | 7 days |
| Blocker list with owners | Track A lead | All blockers have owner + resolution criteria | 7 days |
| Go/No-Go criteria ratified | All track leads | Criteria approved asynchronously or in sync | 14 days |
| `CHANGELOG.md` unreleased scope note populated | Track A implementation owner | Section present and reviewed before tag | 30 days |

### In Scope (Proposed for `v0.1.0`)

| Area | In-Scope Surface |
|---|---|
| Core Library (mirror-dissonance) | Stable public API surface for phase dissonance detection (types and entrypoints) |
| Core Library (mirror-dissonance) | L0 invariant enforcement path fails loudly on violation |
| Core Library (mirror-dissonance) | Basic test coverage with pass/fail CI gate |
| PIRTM Core | Core modules sufficient for reference use case demonstration |
| PIRTM Core | This plan document updated to runtime-truth state |
| Governance / Compliance | `LICENSE` present and correct |
| Governance / Compliance | `CHANGELOG.md` promoted with release scope note, date, and approver |

### Out of Scope (Deferred)

| Item | Rationale |
|---|---|
| MCP / agent integrations | Avoid freezing agent API before core stabilizes |
| UI surfaces | No direct dependency in `R1`-`R8` |
| Terraform / cloud resources | Post-release concern unless CI requires it |
| Q-Calculator and Lambda-Proof integrations | Cross-repo coupling should not block PIRTM core release |
| Published package registry artifacts | Explicitly excluded by `R1` issue scope |

### Release Blockers (Track A)

| Blocker | Owner | Resolution Criteria |
|---|---|---|
| Scope and tag finalization (`v0.1.0` or alternative) | Lead Multiplicity Theorist | Scope section finalized and approved |
| Release notes + migration notes (`R2`) | Track A lead | Draft merged and linked from README/docs |
| Release gate matrix (`R8`) | CI/quality owner | Required checks documented and accepted |

### Go / No-Go Criteria (Draft)

- All in-scope modules pass required CI on mainline.
- No open `release-blocker` issue without owner and target resolution date.
- L0 invariants are enforced and covered by tests.
- `CHANGELOG.md` and this plan reflect the same frozen scope.
- Precision decision above is explicitly recorded in writing.
- Lead Multiplicity Theorist signs off.

### Downstream Links

`R1` unblocks: `R2`, `R3`, `R8`.

---

### Delta B — Legacy Boundary Completion

Current state: legacy code is present under `src/pirtm/_legacy/` with package-level deprecation warning, while `src/pirtm/spectral_decomp.py` also exists as a top-level module.

**Deliverables**
- Decide and document canonical spectral API boundary:
	- keep `pirtm.spectral_decomp` as supported, or
	- move fully behind `_legacy` and provide explicit migration path.
- Add explicit per-module deprecation notices (not only package-level) for `_legacy` modules where appropriate.
- Add removal timeline in docs/changelog (versioned target for `_legacy` sunset).

**Dependencies**: Delta A scope decision should confirm whether this is a release blocker.

---

### Delta C — Simulation Modernization

Current state: simulation scripts under `src/pirtm/simulations/` still import `pirtm._legacy` primitives.

**Deliverables**
- Migrate simulation modules to contractive-core APIs (`recurrence`, `qari`, `gate`, `certify`) where feasible.
- For simulations that must remain legacy-backed, mark them as legacy examples and isolate entry points.
- Add minimal simulation regression tests for selected modernized paths.

**Dependencies**: Delta B boundary decision.

---

### Delta D — CI/Quality Gate Consolidation

Current state: CI workflows exist (`ci.yml`, `nightly.yml`, `release.yml`) but roadmap-level acceptance criteria are not yet codified for release quality.

**Deliverables**
- Define release gate matrix in docs: required jobs, test subsets, and conformance profile outcomes.
- Ensure ACE/transpiler critical tests are explicitly included in required CI paths.
- Add failure-triage policy for flaky or long-running integration slices.

**Dependencies**: Delta A.

---

### Delta E — Roadmap and Documentation Sync

Current state: plan docs include historical assumptions and exploratory ADR material that can drift from runtime truth.

**Deliverables**
- Align `docs/plans/` with implemented state (mark superseded plan sections and keep one active roadmap source of truth).
- Add a concise “Current Support Matrix” (core, ACE, transpiler, legacy) with status and stability level.
- Keep README/examples/docs cross-linked for CLI behavior (including output gating flags) and release notes.

**Dependencies**: Delta A and Delta B decisions.

## Sequenced Execution Plan (Current-Reality Order)

1. **A1**: Freeze release scope and milestone definition (`v0.1.0` or explicit alternative).
2. **A2**: Run full release-quality pass and resolve blockers.
3. **B1**: Decide legacy spectral boundary and deprecation policy.
4. **C1**: Modernize simulation imports or explicitly classify legacy-only simulations.
5. **D1**: Lock CI gate matrix to release criteria.
6. **E1**: Publish synchronized roadmap/docs set and close historical plan sections.

## Issue Breakdown (Remaining Work Only)

| # | Title | Track | Depends On | Size |
|---|-------|-------|------------|------|
| R1 | Define release scope and target tag | A | — | S |
| R2 | Finalize release notes and migration notes | A | R1 | S |
| R3 | Execute release checklist and cut tagged release | A | R2 | M |
| R4 | Decide `spectral_decomp` support boundary and legacy sunset | B | R1 | M |
| R5 | Add per-module legacy deprecation notices + timeline | B | R4 | S |
| R6 | Migrate simulations off `_legacy` (or classify explicitly) | C | R4 | M |
| R7 | Add simulation regression tests for modernized flows | C | R6 | M |
| R8 | Define required CI release gate matrix | D | R1 | S |
| R9 | Align required CI paths with ACE/transpiler critical suites | D | R8 | S |
| R10 | Consolidate plans/docs into active roadmap + support matrix | E | R3,R4,R8 | M |

**Size legend:** S = single-file or small docs/config update. M = multi-file or cross-module update.

## Target Outcome

Completion of `R1`–`R10` yields a release-ready PIRTM core with:
- an actual tagged release (not dev-only),
- an explicit and enforceable legacy boundary,
- modernized or clearly scoped simulation surface,
- stable CI release gates, and
- one current roadmap reflecting implemented reality.

## Historical Baseline

The original Tier 1–5 checklist is retained in git history and was superseded by this remaining-deltas roadmap after substantial completion of packaging, CI, core modules, tests, and onboarding docs.

