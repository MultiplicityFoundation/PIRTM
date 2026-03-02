# Release Checklist

## Release Gate Matrix (R8 Canonical)

This matrix defines which checks are required for a release-candidate commit on `Multiplicity`.

| Gate | Workflow | Job / Command | Required | Owner | Escalation |
|---|---|---|---|---|---|
| Lint | `.github/workflows/ci.yml` | `lint` (`ruff check`, `ruff format --check`) | Yes | CI/quality owner | Open `release-blocker` issue and notify Track D lead |
| Type-check | `.github/workflows/ci.yml` | `typecheck` (`mypy src/pirtm/`) | Yes | CI/quality owner | Open `release-blocker` issue and notify Track D lead |
| ACE/transpiler critical suites | `.github/workflows/ci.yml` | `critical-suites` (targeted pytest suite) | Yes | Track D + Track A leads | Open `release-blocker` issue and assign suite owner |
| Unit/integration tests | `.github/workflows/ci.yml` | `test` matrix (3.11, 3.12, 3.13) | Yes | Track A lead | Open `release-blocker` issue and assign module owner |
| Conformance profile | Manual pre-release + nightly | `pirtm-conformance --profile all --output text` | Yes | Conformance owner | Block tag until passing evidence is attached |
| Build validity | Release checklist + `release.yml` | `python -m build`, `python -m twine check dist/*` | Yes | Release manager | Block tag and assign packaging owner |
| Release artifact publish | `.github/workflows/release.yml` | `build`, `publish`, `github-release` | Yes (tagged release) | Release manager | Roll back tag/release candidate and triage |
| Nightly regression | `.github/workflows/nightly.yml` | `nightly` matrix | No (release gate), signal-only | CI/quality owner | File follow-up issue unless it reflects release blocker class |
| Optional supply chain extras | Local/manual | `make sbom`, `make sign`, `make verify` | No (recommended) | Security/release owner | Track in follow-up if omitted |

### Critical Suite Coverage Policy

- ACE and transpiler critical suites must not be skipped by path filters or conditional job logic on release-relevant changes.
- Required `critical-suites` CI job must execute at least:
	- `tests/test_cli_transpile.py`
	- `tests/test_transpiler.py`
	- `tests/test_ace_protocol.py`
	- `tests/test_ace_protocol_injection.py`
	- `tests/test_ace_matrix_immutability.py`
	- `tests/test_simulations_modernized.py`
- Legacy-classified research simulation paths (currently `src/pirtm/simulations/riemann_verification.py`) are non-blocking for release gates until promoted out of research-only scope.
- Required checks are enforced via CI job status plus manual release-checklist confirmation for conformance/build gates.

### Flaky/Failure Triage Policy

1. Classify failures as one of: deterministic regression, infrastructure transient, or flaky test.
2. Any deterministic regression is an automatic release blocker until fixed.
3. Infrastructure transients may be retried once; repeated failure becomes blocker and must be tracked.
4. Flaky tests require owner assignment and stabilization plan; release can proceed only if failure is proven non-scope and waived by Track A lead plus release manager.
5. Every waived gate must be documented in release evidence with rationale and follow-up issue.

## PR-B Evidence Snapshot (2026-03-01)

### Workflow/Job Inventory (from repository workflows)

- CI workflow (`.github/workflows/ci.yml`) defines required-gate jobs:
	- `Lint (ruff)`
	- `Type-check (mypy)`
	- `Critical suites (ACE + transpiler)`
	- `Test (pytest) — Python 3.11`
	- `Test (pytest) — Python 3.12`
	- `Test (pytest) — Python 3.13`
- Nightly workflow (`.github/workflows/nightly.yml`) remains signal-only for release gate purposes.
- Release workflow (`.github/workflows/release.yml`) enforces `gate -> build -> publish/github-release` sequencing for tags.

### GitHub Run Evidence

- Successful CI run with full job success set:
	- Run `22536756530`: https://github.com/MultiplicityFoundation/PIRTM/actions/runs/22536756530
- Latest failed CI run (before lint fix) identified root cause in required lint job:
	- Run `22545781480`: `Lint (ruff)` failed at `ruff check src/ tests/`.
	- URL: https://github.com/MultiplicityFoundation/PIRTM/actions/runs/22545781480

### Local Gate Evidence (post-fix)

- `ruff check src tests` -> pass
- `ruff format --check src tests` -> pass
- `mypy src/pirtm` -> pass
- `pytest -q` -> pass (`181 passed`)

### Required-Checks Enforcement Verification

- Attempted to fetch branch protection/required status checks via:
	- `gh api repos/MultiplicityFoundation/PIRTM/branches/Multiplicity/protection`
- Result: `403 Resource not accessible by integration` with current token scope.
- Action required: repository maintainer/admin must confirm in GitHub branch protection settings that the CI jobs listed above are marked as required checks on `Multiplicity`.

## PR-C Release-Readiness Snapshot (2026-03-02)

### Day 13–14 Gate Run (local evidence)

- Conformance directory: `python -m pytest -q tests/conformance/` -> pass (`17 passed`)
- Full test suite: `python -m pytest -q` -> pass (`207 passed, 4 warnings`)
- Type-check: `python -m mypy` -> pass (`no issues found in 64 source files`)
- Lint: `python -m ruff check .` -> pass (`All checks passed`)
- Conformance profile CLI: `pirtm-conformance --profile all --output text` -> pass (core + integrity)

### Warning snapshot

- Remaining warnings are deprecation warnings from `pirtm._legacy` import paths.
- No warnings were raised from newly added conformance/doc-sprint modules.

### Release-readiness status summary

| Gate | Status | Evidence |
|---|---|---|
| §5/§8/§9/§11 conformance tests | PASS | `tests/conformance/` (17 passing) |
| Full pytest suite | PASS | `207 passed` |
| Static typing | PASS | `mypy` clean |
| Lint | PASS | `ruff` clean |
| Conformance profile command | PASS | `pirtm-conformance --profile all` |

## Pre-release

- [ ] Ensure release branch is up to date with `Multiplicity`
- [ ] Run `ruff check src tests`
- [ ] Run `mypy src`
- [ ] Run `pytest -q`
- [ ] Run `pirtm-conformance --profile all --output text`
- [ ] Confirm `CHANGELOG.md` has release notes under `Unreleased`

## Versioning

- [ ] If releasing from prerelease (`*dev*`/`*rc*`), run `python scripts/bump_version.py release --tag`
- [ ] Otherwise bump SemVer (`major`/`minor`/`patch`) with `python scripts/bump_version.py <level> --tag`
- [ ] Verify version changed in `pyproject.toml` and `src/pirtm/__init__.py`
- [ ] Commit version + changelog updates
- [ ] Create tag (`git tag vX.Y.Z`) if `--tag` was not used

## Build and Integrity

- [ ] Build: `python -m build`
- [ ] Check artifacts: `python -m twine check dist/*.whl dist/*.tar.gz`
- [ ] Generate SBOM: `make sbom`
- [ ] (Optional) Sign artifacts: `make sign`
- [ ] (Optional) Verify signatures: `make verify`

## Publish

- [ ] Push commits and tags
- [ ] Confirm `Release` workflow succeeds (gate → build → publish/github-release)
- [ ] For `workflow_dispatch` dry-runs, keep `publish_to_pypi=false`; enable only for approved publish run
- [ ] Confirm package appears on PyPI
- [ ] Confirm GitHub release assets are attached
- [ ] Record release evidence: tag, workflow URL, and `SHA256SUMS` from workflow artifacts

## Post-release

- [ ] Create next `Unreleased` changelog section
- [ ] Announce release with highlights and migration notes
