# PIRTM v0.1.0 Completion Scan

The package is substantially complete — the core math, CLI, conformance runner, and test suite are all present.  The package metadata is now aligned to `0.1.0` (`pyproject.toml` and `src/pirtm/__init__.py`).  Remaining work is now mostly release-governance verification, not feature development.

***

## What Is Done ✅

**Core library** — all major modules present and individually tested:

- Recurrence engine, projection, certify, ACE protocol, PETC, PETC bridge
- Gate, CSL, CSL gate, spectral decomp + gov, orchestrator
- QARI, gain, weights, CSC, audit chain, telemetry, lambda bridge
- Transpiler (Phases 2.1–2.3: computation, data asset, neural network descriptors, dual-hash witness, `--emit-witness` / `--emit-lambda-events` flags)
- CLI (`pirtm` + `pirtm-conformance` entrypoints)

**Tests** — 38 test files covering every core module individually, plus integration and CLI transpile tests

**Governance (Tier 5)** — `CONTRIBUTING.md`, `SECURITY.md`, PR template, issue templates, `Makefile` supply-chain targets, release automation script

**Build system** — Hatchling, `src/` layout, `dev`/`legacy`/`all` extras, `pytest` + `ruff` + `mypy` configured

***

## Status After PR-A / PR-B / PR-C ✅

### 1. Version + Classifier Alignment — Completed

`pyproject.toml` is now `version = "0.1.0"` and classifier is now `Development Status :: 4 - Beta`.

### 2. CHANGELOG Release Section — Completed

`CHANGELOG.md` now includes `## [0.1.0] - 2026-03-01` and explicit `v0.1.0` scope notes.

### 3. `tests/README.md` Hardening — Completed

`tests/README.md` is now populated with full-suite, coverage, critical-suite, and release-gate command guidance plus marker/runtime notes.

### 4. CI Workflow Audit — Partially Completed

Workflows were audited (`ci.yml`, `nightly.yml`, `release.yml`), local gate evidence was captured, and run evidence was linked in `docs/release_checklist.md`.

**Remaining blocker**: branch-protection required-check enforcement could not be queried via token scope (`403 Resource not accessible by integration`) and still requires maintainer/admin UI confirmation on `Multiplicity`.

### 5. `docs/` Coverage Gap — Completed

The referenced docs are present and aligned with README references:

- `docs/api/README.md` — present and now includes explicit API boundary language
- `docs/architecture.md` — present
- `docs/math_spec.md` — present
- `examples/README.md` — present and referenced


### 6. `_legacy/` Quarantine — Completed

Public API boundary now explicitly states `_legacy` is deprecated/transitional and excluded from stable API guarantees.

### 7. `frontend/`, `notebooks/`, `papers/` Scope Declaration — Completed

Scope is now explicitly declared in release docs and README as out-of-package scope for `v0.1.0`.

### 8. Public API Boundary Test Coverage — Completed

A regression test now asserts top-level exports do not expose `_legacy` (`tests/test_public_api_boundary.py`).

***

## Ranked Next Steps

| Priority | Task | Artifact | Owner | Horizon |
| :-- | :-- | :-- | :-- | :-- |
| **P0** | Confirm required checks are enforced in branch protection UI | GitHub branch settings (`Multiplicity`) | Repo maintainer/admin | **Now** |
| **P0** | Push latest PR-B/PR-C fixes and verify CI green on tip commit | `.github/workflows/ci.yml` run | Track A | **Now** |
| **P1** | Attach branch-protection screenshot / settings export to release evidence | `docs/release_checklist.md` evidence block | Release manager | **Before tag** |
| **P1** | Resolve or waive unrelated flaky/numeric spectral assertion if it recurs in CI | `tests/test_spectral.py` | Track A + module owner | **Before tag** |

The only hard blocker remaining from this scan is required-check enforcement confirmation in GitHub branch protection.

***

## Response to Completion Scan: Concrete Dissonance Resolution

The dissonance is clear: **implementation appears complete**, but **release-state signals are incomplete**.  Resolution is to close signal gaps in a strict order and treat each as a gate with evidence.

### D1 — Release Identity Dissonance

**Issue**: Release identity metadata was previously inconsistent.

**Concrete steps**:

1. Update `pyproject.toml` version to `0.1.0`. ✅
2. Set classifier intent explicitly (`4 - Beta` or `5 - Production/Stable`). ✅ (`4 - Beta`)
3. Align `src/pirtm/__init__.py` version to `0.1.0`. ✅

**Done when**: `pip show pirtm` and package metadata report `0.1.0` with final classifiers.

### D2 — Narrative Dissonance (What changed vs what is shipped)

**Issue**: `CHANGELOG.md` does not yet express a real release boundary.

**Concrete steps**:

1. Promote `[Unreleased]` content into `## [0.1.0] - 2026-03-01`. ✅
2. Split entries into `Added`, `Changed`, `Fixed`, and `Docs/Governance`. ✅
3. Add explicit “Out of scope for 0.1.0” note for `frontend/`, `notebooks/`, and `papers/`. ✅

**Done when**: A reader can identify exactly what `0.1.0` contains without inspecting source.

### D3 — Verification Dissonance (Claimed readiness vs enforced quality)

**Issue**: CI and release workflow status is not yet evidenced.

**Concrete steps**:

1. Audit `.github/workflows/` for test/lint/type/release jobs. ✅
2. Run full local gate (`ruff`, `mypy`, `pytest`) and record pass status. ✅
3. Confirm required checks are enforced on default branch before tag. ⏳ (admin UI confirmation pending)

**Done when**: Branch protection requires green checks and latest commit is green end-to-end.

### D4 — API Boundary Dissonance

**Issue**: `_legacy/` presence is ambiguous for public API consumers.

**Concrete steps**:

1. Add public API statement in `README.md` and/or docs. ✅
2. Mark `_legacy/` as non-stable/internal with deprecation import warning if imported. ✅
3. Add one conformance test asserting public imports exclude `_legacy`. ✅

**Done when**: API boundary is documented, enforceable, and test-covered.

### D5 — Documentation Completeness Dissonance

**Issue**: Referenced docs and test guidance are partially unverified.

**Concrete steps**:

1. Verify presence and completeness of `docs/api/README.md`, `docs/architecture.md`, `docs/math_spec.md`, `examples/README.md`. ✅
2. Populate `tests/README.md` with commands, markers, and expected runtime profile. ✅
3. Add links from root `README.md` to these docs and verify they resolve. ✅

**Done when**: New contributors can run tests and locate API/math/architecture docs without guesswork.

### 7-Day Closure Sequence

- **Day 0 (today)**: Complete D1 + D2 (version/classifier/changelog/scope note).
- **Day 1**: Complete D3 workflow audit and enforce required checks.
- **Day 2–3**: Complete D4 API boundary declaration + test.
- **Day 3–5**: Complete D5 doc verification and `tests/README.md`.
- **Day 6–7**: Cut `v0.1.0` tag, publish release notes, open `v0.1.1` fast-follow board.

### Immediate Action Set (Next 3 PRs)

1. **PR-A (Release metadata)**: version bump, classifier decision, changelog promotion, out-of-scope statement.
2. **PR-B (Quality gate evidence)**: CI workflow verification + branch protection confirmation + gate snapshot.
3. **PR-C (API/docs boundary)**: `_legacy` policy statement, `tests/README.md`, docs link audit fixes.

If executed in this order, the repository moves from “nearly complete” to “release-consistent and auditable” with minimal scope expansion.

