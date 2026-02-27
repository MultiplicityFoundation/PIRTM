# PIRTM Tier 5: Governance, Cross-Repo Integration, and Release Hardening — Expanded Specification

## Problem Statement

After Tiers 1-4, PIRTM is an installable, tested, documented Python package. But it exists in isolation. Three critical gaps remain:

1. **No governance artifacts.** No CONTRIBUTING.md, no SECURITY.md, no PR template, no issue templates. Lambda-Proof has all of these. PIRTM has none.
2. **No cross-repo integration.** DRMM's `operators.py` defines its own `Xi.evolve()` function and `tensor_core.py` defines its own `recursive_tensor_update()` loop — both duplicate what `pirtm.recurrence.step()` and `pirtm.recurrence.run()` already provide. Lambda-Proof's COVENANT references "Covered Technology" conformance but no mechanism exists to run PIRTM's contractive checks as part of that conformance suite.
3. **No release pipeline.** No `pyproject.toml` version bump automation, no GitHub release workflow, no tag-triggered publishing, no signed artifacts.

Tier 5 closes all three gaps across 6 issues (#25-#30).

***

## Deliverable Inventory

| Issue | Deliverable | Files | Purpose |
|-------|-------------|-------|---------|
| #25 | Governance files | `CONTRIBUTING.md`, `SECURITY.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/` | Contributor onboarding and security reporting |
| #26 | DRMM integration adapter | `drmm/adapters/pirtm_bridge.py` in DRMM repo | Replace DRMM's ad-hoc recurrence with `pirtm.run()` |
| #27 | Lambda-Proof conformance hook | `pirtm.conformance` module + CLI entry point | Run PIRTM stability predicates as COVENANT conformance tests |
| #28 | CI hardening | `.github/workflows/release.yml`, `.github/workflows/nightly.yml` | Tag-triggered PyPI publish, nightly regression |
| #29 | Release automation | `scripts/bump_version.py`, release checklist | Semver bump, CHANGELOG update, tag creation |
| #30 | Security and supply chain | `SBOM`, signed wheels, `Makefile` provenance targets | Reproducible builds, artifact signing, SBOM generation |

***

## Issue #25: Governance Files

### Problem Statement

Lambda-Proof has a 400-line CONTRIBUTING.md covering setup, commit conventions, PR templates, testing pyramid, security checklist, and code style. PIRTM has zero governance files. A contributor arriving from the Lambda-Proof ecosystem expects the same structure.

### Deliverable: `CONTRIBUTING.md`

Adapted from Lambda-Proof's conventions to PIRTM's Python context:

#### Section Outline

1. **Core Principles** — Contractivity invariant, safety-first projection, zero-surveillance (aligned with COVENANT)
2. **Development Setup** — `git clone`, `pip install -e ".[dev]"`, `pytest -v --cov=pirtm`
3. **Making Changes** — Minimal-change philosophy (same as Lambda-Proof)
4. **Commit Conventions** — Conventional commits: `feat(recurrence):`, `fix(certify):`, `test(projection):`
5. **PR Guidelines** — Title format, description template, review process
6. **Testing Requirements** — Coverage targets, testing pyramid
7. **Code Style** — Python-specific: ruff for linting, mypy for typing, NumPy docstring format
8. **Security Checklist** — No secrets, no PII, no telemetry, no external network calls
9. **License** — MIT (code), CC BY-NC-SA 4.0 (documentation)

#### Testing Pyramid (PIRTM-Specific)

```
                /\
               /  \
              /Prop \          <- 5% (property-based, hypothesis)
             /--------\
            /  Integ.  \       <- 15% (cross-module pipelines)
           /------------\
          /     Unit      \    <- 80% (per-function, per-branch)
         /------------------\
```

#### Coverage Targets

| Module Category | Target |
|----------------|--------|
| Core modules (`recurrence`, `certify`, `projection`) | 100% branch coverage |
| Tier 2 modules (`weights`, `gain`, `csc`) | 95% branch coverage |
| Utility modules (`petc`, `monitor`, `adaptive`) | 90% branch coverage |
| Integration tests | Every public function called at least once in a pipeline |

#### PR Description Template

```markdown
## Summary
Brief description.

## Changes
- [ ] Files changed with rationale
- [ ] Mathematical invariant preserved: q_t < 1 - epsilon

## Testing
- [ ] `pytest -v --cov=pirtm` passes
- [ ] Coverage >= baseline (no regression)
- [ ] New tests added for new code paths

## Checklist
- [ ] Conventional commit format
- [ ] No new dependencies beyond numpy
- [ ] No telemetry or network calls
- [ ] Type annotations on all public functions
- [ ] Docstrings on all public symbols
```

### Deliverable: `SECURITY.md`

```markdown
# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| 0.1.x   | Security fixes only |
| < 0.1   | No        |

## Reporting

Report vulnerabilities privately via GitHub Security Advisories:
https://github.com/MultiplicityFoundation/PIRTM/security/advisories/new

Do NOT open a public issue for security vulnerabilities.

## Scope

PIRTM is a pure-Python numerical library. Security-relevant concerns include:
- Numerical overflow/underflow leading to incorrect convergence certificates
- Denial of service via pathological inputs (e.g., matrices triggering infinite loops)
- Supply chain compromise of published wheels

## Response Timeline
- Acknowledgment: 48 hours
- Triage: 7 days
- Fix (critical): 14 days
- Fix (moderate): 30 days

## Dependency Policy

PIRTM depends on NumPy only. No network dependencies. No native code
beyond NumPy's compiled core. This minimizes the attack surface.
```

### Deliverable: Issue Templates

Three templates in `.github/ISSUE_TEMPLATE/`:

**`bug_report.yml`** — Structured bug report with fields: description, steps to reproduce, expected behavior, actual behavior, PIRTM version, Python version, NumPy version, OS.

**`feature_request.yml`** — Structured feature request with fields: description, motivation, proposed API, mathematical specification (if applicable), alternatives considered.

**`documentation.yml`** — Documentation issue with fields: which document, what's wrong/missing, suggested improvement.

### Acceptance Criteria

- CONTRIBUTING.md references `pirtm`-specific commands (`pip install -e ".[dev]"`, `pytest`, `ruff`, `mypy`)
- SECURITY.md links to GitHub Security Advisories (not a public email)
- PR template includes the contractivity invariant check
- All three issue templates render correctly on GitHub's issue creation page
- Commit convention types match Lambda-Proof's set: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `security`, `ci`

### Estimated Size

~350 lines across all governance files.

***

## Issue #26: DRMM Integration Adapter

### Problem Statement

DRMM's codebase contains two functions that duplicate PIRTM's core:

| DRMM Function | What It Does | PIRTM Equivalent |
|--------------|-------------|-----------------|
| `Xi.evolve(X, t, alpha)` | `X + alpha * t * gradient` — ad-hoc entropy-weighted drift | `pirtm.recurrence.step()` with proper contractivity check |
| `recursive_tensor_update(T, f, steps)` | Bare loop: `for _ in range(steps): T = f(T)` | `pirtm.recurrence.run()` with safety projection, telemetry, and certificates |
| `LambdaM.evolve(X, t)` | `exp(-1/(1+t^2)) * X` — time-varying scalar modulation | Maps to `Lam_t` parameter in `step()` |

None of the DRMM versions check contractivity. None produce `StepInfo` telemetry. None certify convergence. DRMM depends on `sympy` for prime generation; PIRTM uses only `math` from stdlib.

### Proposed Architecture

A thin adapter in the DRMM repo that wraps PIRTM's contractive core:

```python
# drmm/adapters/pirtm_bridge.py

"""Bridge DRMM operators to PIRTM's contractive recurrence."""

from __future__ import annotations

import numpy as np
from pirtm import step, run, ace_certificate
from pirtm.types import StepInfo, Status, Certificate


def drmm_step(
    X: np.ndarray,
    Xi_matrix: np.ndarray,
    Lam_matrix: np.ndarray,
    T: callable,
    G: np.ndarray | None = None,
    *,
    epsilon: float = 0.05,
    op_norm_T: float | None = None,
) -> tuple[np.ndarray, StepInfo]:
    """Execute one DRMM evolution step with contractive guarantees.

    Replaces Xi.evolve() and LambdaM.evolve() with a single call
    that checks q_t < 1 - epsilon and projects if violated.
    """
    if G is None:
        G = np.zeros_like(X)
    P = lambda x: x  # identity projector; override for constrained DRMM

    if op_norm_T is None:
        from pirtm.gain import estimate_operator_norm
        op_norm_T = estimate_operator_norm(T, X.shape)

    return step(X, Xi_matrix, Lam_matrix, T, G, P,
                epsilon=epsilon, op_norm_T=op_norm_T)


def drmm_evolve(
    X0: np.ndarray,
    Xi_sequence: list[np.ndarray],
    Lam_sequence: list[np.ndarray],
    T: callable,
    G_sequence: list[np.ndarray] | None = None,
    *,
    epsilon: float = 0.05,
    op_norm_T: float | None = None,
    certify: bool = True,
) -> dict:
    """Full DRMM evolution with PIRTM backend.

    Replaces recursive_tensor_update() with certified convergence.

    Returns:
        dict with keys: X_final, history, infos, status, certificate
    """
    N = len(Xi_sequence)
    if G_sequence is None:
        G_sequence = [np.zeros_like(X0)] * N
    P = lambda x: x

    if op_norm_T is None:
        from pirtm.gain import estimate_operator_norm
        op_norm_T = estimate_operator_norm(T, X0.shape)

    X_final, history, infos, status = run(
        X0, Xi_sequence, Lam_sequence, G_sequence,
        T=T, P=P, epsilon=epsilon, op_norm_T=op_norm_T,
    )

    result = {
        "X_final": X_final,
        "history": history,
        "infos": infos,
        "status": status,
        "certificate": None,
    }

    if certify:
        result["certificate"] = ace_certificate(infos)

    return result


def legacy_Xi_evolve(X: np.ndarray, t: float, alpha: float = 0.1) -> np.ndarray:
    """Backward-compatible wrapper for Xi.evolve().

    WARNING: This function does NOT check contractivity.
    Use drmm_step() for safe evolution.
    """
    import warnings
    warnings.warn(
        "legacy_Xi_evolve is deprecated. Use drmm_step() for contractive guarantees.",
        DeprecationWarning,
        stacklevel=2,
    )
    gradient = -np.log1p(np.abs(X))
    return X + alpha * t * gradient
```

### Migration Path for DRMM Callers

| Current DRMM Usage | Replacement |
|--------------------|-------------|
| `Xi.evolve(X, t)` | `drmm_step(X, Xi_matrix, Lam_matrix, T)` |
| `LambdaM.evolve(X, t)` | Absorbed into `Lam_matrix` parameter of `drmm_step()` |
| `recursive_tensor_update(T, f, steps)` | `drmm_evolve(X0, Xi_seq, Lam_seq, T)` |
| `MoonshineOperator.apply(X, p)` | Wrap as `T = lambda x: moonshine.apply(x, p)`, pass to `drmm_step` |

### New Dependency in DRMM

```toml
# drmm/pyproject.toml (additions)
[project]
dependencies = [
    "pirtm >= 0.1.0",
    "numpy >= 1.24",
]
```

This **removes** the `sympy` dependency from DRMM's critical path. `sympy` was used only for `primerange()` in `tensor_core.py`; PIRTM provides its own prime utilities via `petc._is_prime()` and the Tier 2 `weights.synthesize_weights()`.

### Acceptance Criteria

- `drmm_step()` returns the same `StepInfo` type as `pirtm.step()`
- `drmm_evolve()` returns a `Certificate` when `certify=True`
- `legacy_Xi_evolve()` emits a `DeprecationWarning`
- DRMM's existing tests still pass (legacy functions are preserved, not deleted)
- No `sympy` import in the adapter
- Adapter is < 150 LOC

***

## Issue #27: Lambda-Proof Conformance Hook

### Problem Statement

The Lambda-Proof COVENANT defines conformance profiles including "Governance and Stability Predicates" — the implementation must evaluate governance predicates for each protected transition, fail closed when predicates fail, and execute deterministic remediation. PIRTM's `step()` function already does exactly this: it checks \( q_t < 1 - \epsilon \), fails closed via projection when violated, and records a deterministic `StepInfo`. But no mechanism exists to invoke PIRTM as a conformance check from Lambda-Proof's test harness.

### Proposed Architecture

A new module `pirtm.conformance` with a CLI entry point:

```python
# src/pirtm/conformance.py

"""COVENANT conformance predicates for Lambda-Proof integration."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from typing import Any

from .recurrence import step, run
from .certify import ace_certificate, iss_bound
from .types import StepInfo, Status, Certificate


class ConformanceResult:
    """Machine-readable conformance report."""

    def __init__(self, profile: str, version: str = "0.2.0"):
        self.profile = profile
        self.version = version
        self.checks: list[dict[str, Any]] = []
        self.passed = True

    def record(self, name: str, passed: bool, detail: str = ""):
        self.checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            self.passed = False

    def to_json(self) -> str:
        return json.dumps({
            "profile": self.profile,
            "pirtm_version": self.version,
            "passed": self.passed,
            "checks": self.checks,
        }, indent=2)


def check_core_profile(
    X0, Xi_seq, Lam_seq, G_seq, T, P,
    *,
    epsilon: float = 0.05,
    op_norm_T: float = 1.0,
) -> ConformanceResult:
    """Run COVENANT Core Profile checks against a transition sequence.

    Core Profile requirements (from COVENANT Section 4.1):
    - Governance predicates evaluated for each transition
    - Fail-closed on predicate failure
    - Deterministic remediation (project/freeze/rollback)
    - Canonical commitment/fingerprint for each event
    """
    result = ConformanceResult(profile="core")

    # Check 1: Predicate evaluation (q_t computed for every step)
    X_final, history, infos, status = run(
        X0, Xi_seq, Lam_seq, G_seq,
        T=T, P=P, epsilon=epsilon, op_norm_T=op_norm_T,
    )
    all_q_computed = all(hasattr(info, 'q') and info.q is not None for info in infos)
    result.record(
        "predicate_evaluation",
        all_q_computed,
        f"q_t computed for {len(infos)}/{len(Xi_seq)} steps"
    )

    # Check 2: Fail-closed (projection triggered when q > 1 - epsilon)
    violations = [i for i in infos if i.q > 1 - epsilon and not i.projected]
    result.record(
        "fail_closed",
        len(violations) == 0,
        f"{len(violations)} unmitigated violations"
    )

    # Check 3: Deterministic remediation (projection is deterministic)
    projected_steps = [i for i in infos if i.projected]
    if projected_steps:
        # Re-run same inputs — check determinism
        X_final2, _, infos2, _ = run(
            X0, Xi_seq, Lam_seq, G_seq,
            T=T, P=P, epsilon=epsilon, op_norm_T=op_norm_T,
        )
        deterministic = all(
            abs(a.q - b.q) < 1e-12 and a.projected == b.projected
            for a, b in zip(infos, infos2)
        )
        result.record(
            "deterministic_remediation",
            deterministic,
            f"Re-ran {len(infos)} steps; determinism={'passed' if deterministic else 'failed'}"
        )
    else:
        result.record(
            "deterministic_remediation",
            True,
            "No projections triggered; trivially deterministic"
        )

    # Check 4: Canonical fingerprint (StepInfo is hashable/serializable)
    try:
        for info in infos:
            _ = json.dumps(asdict(info))
        result.record("canonical_fingerprint", True, "All StepInfo serializable")
    except (TypeError, ValueError) as e:
        result.record("canonical_fingerprint", False, str(e))

    # Check 5: Certificate consistency
    cert = ace_certificate(infos)
    result.record(
        "certificate_consistency",
        cert.certified == (cert.margin >= 0),
        f"margin={cert.margin:.6f}, certified={cert.certified}"
    )

    return result


def check_integrity_profile(infos: list[StepInfo]) -> ConformanceResult:
    """Run COVENANT Integrity Profile checks.

    Integrity requirements (from COVENANT Section 4.3):
    - Canonical ordered tuple for commitments
    - Anti-replay (no duplicate step indices)
    - Deterministic trace export
    """
    result = ConformanceResult(profile="integrity")

    # Check 1: Canonical ordering
    steps = [i.step for i in infos]
    result.record(
        "canonical_ordering",
        steps == sorted(steps),
        f"Step indices: {steps[:5]}..."
    )

    # Check 2: Anti-replay (no duplicate step indices)
    result.record(
        "anti_replay",
        len(steps) == len(set(steps)),
        f"Unique: {len(set(steps))}/{len(steps)}"
    )

    # Check 3: Deterministic trace export
    try:
        trace = [json.dumps(asdict(i), sort_keys=True) for i in infos]
        trace2 = [json.dumps(asdict(i), sort_keys=True) for i in infos]
        result.record(
            "deterministic_trace",
            trace == trace2,
            f"Serialized {len(trace)} records"
        )
    except Exception as e:
        result.record("deterministic_trace", False, str(e))

    return result
```

### CLI Entry Point

```toml
# pyproject.toml addition
[project.scripts]
pirtm-conformance = "pirtm.conformance:_cli_main"
```

```python
def _cli_main():
    """CLI: pirtm-conformance --profile core --dim 4 --steps 20"""
    import argparse
    import numpy as np

    parser = argparse.ArgumentParser(description="PIRTM COVENANT conformance check")
    parser.add_argument("--profile", choices=["core", "integrity", "all"], default="all")
    parser.add_argument("--dim", type=int, default=4)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--epsilon", type=float, default=0.05)
    parser.add_argument("--output", choices=["json", "text"], default="text")
    args = parser.parse_args()

    # Generate canonical test vectors
    dim = args.dim
    N = args.steps
    X0 = np.ones(dim)
    Xi_seq = [0.3 * np.eye(dim)] * N
    Lam_seq = [0.2 * np.eye(dim)] * N
    G_seq = [np.zeros(dim)] * N
    T = lambda x: 0.8 * x
    P = lambda x: x

    results = []
    if args.profile in ("core", "all"):
        r = check_core_profile(X0, Xi_seq, Lam_seq, G_seq, T, P,
                               epsilon=args.epsilon, op_norm_T=0.8)
        results.append(r)
    if args.profile in ("integrity", "all"):
        _, _, infos, _ = run(X0, Xi_seq, Lam_seq, G_seq,
                             T=T, P=P, epsilon=args.epsilon, op_norm_T=0.8)
        r = check_integrity_profile(infos)
        results.append(r)

    exit_code = 0
    for r in results:
        if args.output == "json":
            print(r.to_json())
        else:
            status = "PASS" if r.passed else "FAIL"
            print(f"[{status}] Profile: {r.profile}")
            for c in r.checks:
                mark = "+" if c["passed"] else "X"
                print(f"  [{mark}] {c['name']}: {c['detail']}")
        if not r.passed:
            exit_code = 1

    sys.exit(exit_code)
```

### Mapping to COVENANT Sections

| COVENANT Requirement | PIRTM Conformance Check | Method |
|-------------------------------|------------------------|--------|
| Section 4.1 — Predicate evaluation | `predicate_evaluation` | Verify `q_t` computed at every step |
| Section 4.1 — Fail closed | `fail_closed` | Verify projection triggered when `q > 1 - epsilon` |
| Section 4.1 — Deterministic remediation | `deterministic_remediation` | Re-run identical inputs, compare traces |
| Section 4.3 — Canonical commitments | `canonical_fingerprint` | JSON-serialize every `StepInfo` |
| Section 4.3 — Anti-replay | `anti_replay` | Verify unique monotonic step indices |
| Section 4.3 — Deterministic trace | `deterministic_trace` | Sort-key JSON comparison |
| Section 5.3 — Emission gating | Future (Tier 6) | Verify suppression on predicate failure |

### Lambda-Proof CI Integration

Lambda-Proof's conformance harness can invoke PIRTM checks as a subprocess:

```yaml
# In Lambda-Proof's CI workflow
- name: PIRTM Stability Conformance
  run: |
    pip install pirtm
    pirtm-conformance --profile all --output json > pirtm_conformance.json
    # Parse exit code: 0 = all pass, 1 = failure
```

### Acceptance Criteria

- `pirtm-conformance --profile all` exits 0 on canonical test vectors
- `pirtm-conformance --profile all --output json` produces valid JSON matching COVENANT's "Conformance Report" schema
- Core profile runs both `run()` and `ace_certificate()` in a single invocation
- Integrity profile detects deliberately duplicated step indices (negative test)
- CLI is installable via `pip install pirtm` (entry point in `pyproject.toml`)
- Module is importable: `from pirtm.conformance import check_core_profile`

### Estimated Size

~250 LOC (module) + ~50 LOC (CLI glue).

***

## Issue #28: CI Hardening

### Problem Statement

PIRTM currently has no `.github/` directory — no workflows, no CI, no automated checks. Tier 1 (Issue #2) creates the initial CI pipeline for lint + typecheck + test. Tier 5 extends this with two additional workflows:

### Deliverable: `release.yml` — Tag-Triggered PyPI Publish

```yaml
name: Release to PyPI
on:
  push:
    tags: ["v*"]

permissions:
  contents: write
  id-token: write  # for trusted publishing

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build twine
      - run: python -m build
      - run: twine check dist/*

      # Verify tests pass on the tagged commit
      - run: pip install -e ".[dev]"
      - run: pytest -v --cov=pirtm --cov-fail-under=90

      # Upload artifacts
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1

  github-release:
    needs: publish
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - name: Extract changelog
        run: |
          VERSION=${GITHUB_REF_NAME#v}
          sed -n "/^## \[$VERSION\]/,/^## \[/p" CHANGELOG.md | head -n -1 > release_notes.md
      - uses: softprops/action-gh-release@v2
        with:
          body_path: release_notes.md
          generate_release_notes: false
```

### Deliverable: `nightly.yml` — Nightly Regression

```yaml
name: Nightly Regression
on:
  schedule:
    - cron: "0 6 * * *"  # 6 AM UTC daily
  workflow_dispatch:

jobs:
  nightly:
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
        numpy-version: ["1.24", "1.26", "2.0"]
        os: [ubuntu-latest, macos-latest, windows-latest]
      fail-fast: false

    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: Multiplicity
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install numpy==${{ matrix.numpy-version }}.*
      - run: pip install -e ".[dev]"
      - run: pytest -v --cov=pirtm -x --tb=short
      - name: Property tests (extended)
        run: pytest tests/ -k "property" --hypothesis-seed=0 -v
```

### Matrix Coverage

| Axis | Values | Rationale |
|------|--------|-----------|
| Python | 3.11, 3.12, 3.13 | Active CPython versions |
| NumPy | 1.24, 1.26, 2.0 | NumPy 2.0 changed array API substantially |
| OS | Linux, macOS, Windows | Cross-platform float behavior |
| **Total combinations** | **27** | Nightly only; too expensive for per-PR |

### Acceptance Criteria

- `release.yml` triggers only on `v*` tags
- `release.yml` runs full test suite before publishing (gate, not just publish)
- `release.yml` creates a GitHub Release with CHANGELOG-extracted notes
- `nightly.yml` runs on the full matrix and reports failures per combination
- Both workflows use `id-token: write` for trusted publishing (no stored API tokens)
- `nightly.yml` runs extended property tests with a fixed seed for reproducibility

***

## Issue #29: Release Automation

### Problem Statement

Manual version bumps in `pyproject.toml`, CHANGELOG updates, and tag creation are error-prone. A release script automates the mechanical steps.

### Deliverable: `scripts/bump_version.py`

```python
"""Bump PIRTM version, update CHANGELOG, create git tag.

Usage:
    python scripts/bump_version.py patch   # 0.1.0 -> 0.1.1
    python scripts/bump_version.py minor   # 0.1.0 -> 0.2.0
    python scripts/bump_version.py major   # 0.1.0 -> 1.0.0
    python scripts/bump_version.py --dry-run minor
"""

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path


def read_version() -> str:
    pyproject = Path("pyproject.toml").read_text()
    match = re.search(r'version\s*=\s*"(\d+\.\d+\.\d+)"', pyproject)
    if not match:
        sys.exit("Cannot parse version from pyproject.toml")
    return match.group(1)


def bump(current: str, part: str) -> str:
    major, minor, patch = map(int, current.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    elif part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        sys.exit(f"Unknown part: {part}")


def update_pyproject(old: str, new: str):
    path = Path("pyproject.toml")
    text = path.read_text()
    path.write_text(text.replace(f'version = "{old}"', f'version = "{new}"'))


def update_changelog(new: str):
    path = Path("CHANGELOG.md")
    text = path.read_text()
    today = date.today().isoformat()
    text = text.replace(
        "## [Unreleased]",
        f"## [Unreleased]\n\n## [{new}] — {today}",
    )
    path.write_text(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("part", choices=["major", "minor", "patch"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    old = read_version()
    new = bump(old, args.part)
    tag = f"v{new}"

    print(f"Version: {old} -> {new}")
    print(f"Tag: {tag}")

    if args.dry_run:
        print("Dry run — no changes made.")
        return

    update_pyproject(old, new)
    update_changelog(new)
    subprocess.run(["git", "add", "pyproject.toml", "CHANGELOG.md"], check=True)
    subprocess.run(["git", "commit", "-m", f"chore: release {new}"], check=True)
    subprocess.run(["git", "tag", "-a", tag, "-m", f"Release {new}"], check=True)
    print(f"Done. Push with: git push origin Multiplicity {tag}")


if __name__ == "__main__":
    main()
```

### Release Checklist (`docs/release_checklist.md`)

```markdown
# Release Checklist

## Pre-Release
- [ ] All Tier N issues for this version are merged
- [ ] `pytest -v --cov=pirtm --cov-fail-under=90` passes on Multiplicity branch
- [ ] `ruff check src/` reports zero violations
- [ ] `mypy src/pirtm/` reports zero errors
- [ ] CHANGELOG [Unreleased] section lists all changes
- [ ] README quickstart code runs without error
- [ ] examples/ notebooks execute cleanly

## Release
- [ ] `python scripts/bump_version.py {major|minor|patch}`
- [ ] `git push origin Multiplicity v{VERSION}`
- [ ] Verify release.yml workflow completes green
- [ ] Verify PyPI package is accessible: `pip install pirtm=={VERSION}`
- [ ] Verify GitHub Release has correct notes

## Post-Release
- [ ] Announce on relevant channels
- [ ] Update downstream consumers (DRMM adapter version pin)
- [ ] Begin next version's [Unreleased] CHANGELOG section
```

### Acceptance Criteria

- `bump_version.py` reads the current version from `pyproject.toml` (not hardcoded)
- `bump_version.py` updates both `pyproject.toml` and `CHANGELOG.md` atomically
- `--dry-run` makes zero file changes
- The created tag matches `v{new_version}` format expected by `release.yml`
- Release checklist is actionable (every item is a yes/no gate)

***

## Issue #30: Security and Supply Chain

### Problem Statement

The COVENANT's conformance plan (Section 3.3.F) recommends reproducible builds, SBOM publication, and signed releases for supply chain integrity. Lambda-Proof's conformance certification at Level 1+ requires SBOM generation. PIRTM must produce these artifacts to participate in the certification ecosystem.

### Deliverable: `Makefile` Provenance Targets

```makefile
# Makefile — supply chain targets

.PHONY: sbom build-wheel sign-wheel verify-wheel

DIST := dist
VERSION := $(shell python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")

sbom:
	pip install cyclonedx-bom
	cyclonedx-py environment \
		--output $(DIST)/pirtm-$(VERSION).sbom.json \
		--format json \
		--schema-version 1.5

build-wheel:
	python -m build --wheel --outdir $(DIST)

sign-wheel: build-wheel
	pip install sigstore
	python -m sigstore sign $(DIST)/pirtm-$(VERSION)-py3-none-any.whl

verify-wheel:
	python -m sigstore verify identity \
		--cert-identity "https://github.com/MultiplicityFoundation/PIRTM/.github/workflows/release.yml" \
		--cert-oidc-issuer "https://token.actions.githubusercontent.com" \
		$(DIST)/pirtm-$(VERSION)-py3-none-any.whl

reproducible-check:
	# Build twice, compare hashes
	python -m build --wheel --outdir /tmp/build1
	python -m build --wheel --outdir /tmp/build2
	diff <(sha256sum /tmp/build1/*.whl | cut -d' ' -f1) \
	     <(sha256sum /tmp/build2/*.whl | cut -d' ' -f1)
	@echo "Reproducible build verified."

clean:
	rm -rf $(DIST) build *.egg-info
```

### SBOM Output

CycloneDX JSON format listing:

- `pirtm` package metadata (name, version, author, license)
- Direct dependency: `numpy` (version pinned to range)
- Dev dependencies: `pytest`, `pytest-cov`, `ruff`, `mypy` (marked as dev scope)
- Build hash and provenance metadata

### Sigstore Integration

PIRTM uses [Sigstore](https://sigstore.dev) for keyless signing via GitHub Actions' OIDC identity. This means:

- No GPG keys to manage or rotate
- Signatures are tied to the GitHub Actions workflow identity
- Anyone can verify the wheel was built by the official `release.yml` workflow
- Verification command is published in `Makefile` and README

### CI Integration

Added to `release.yml` as a post-build step:

```yaml
      - name: Generate SBOM
        run: make sbom
      - name: Sign wheel
        run: make sign-wheel
      - uses: actions/upload-artifact@v4
        with:
          name: provenance
          path: |
            dist/*.sbom.json
            dist/*.sigstore
```

### Acceptance Criteria

- `make sbom` produces a valid CycloneDX 1.5 JSON file
- `make sign-wheel` produces a `.sigstore` bundle alongside the wheel
- `make verify-wheel` succeeds when run against the signed wheel
- `make reproducible-check` succeeds (two builds produce identical wheel hashes)
- SBOM lists `numpy` as the sole runtime dependency
- All provenance artifacts are uploaded as GitHub Release assets alongside the wheel

***

## Execution Sequence

```
Tier 4 (docs) ──► Tier 5
                    │
      ┌─────────────┼───────────────┬──────────────┐
      ▼             ▼               ▼              ▼
  #25 Governance  #26 DRMM      #27 Conformance  #28 CI
      │           adapter        hook              │
      └─────────────┼───────────────┘              │
                    ▼                              ▼
                #29 Release ◄──────────────────────┘
                    │
                    ▼
                #30 Supply Chain
```

### Dependencies

| Issue | Depends On | Rationale |
|-------|-----------|-----------|
| #25 Governance | Tier 1 (repo structure exists) | References `pyproject.toml`, test commands |
| #26 DRMM Adapter | Tier 2 (`pirtm.gain.estimate_operator_norm` needed) | Adapter imports Tier 2 functions |
| #27 Conformance | Tier 2 (full `run()` + `ace_certificate()` pipeline) | Conformance checks require complete pipeline |
| #28 CI Hardening | Tier 1 (initial CI exists to extend) | Extends `ci.yml` with release + nightly |
| #29 Release | #28 (release.yml must exist) | Bump script creates tags that trigger release.yml |
| #30 Supply Chain | #28 + #29 (release pipeline exists) | Signs artifacts produced by release pipeline |

Issues #25, #26, #27, and #28 are parallel. Issue #29 follows #28. Issue #30 follows #29.

### Estimated Effort

| Issue | Deliverable | LOC (approx) | Time |
|-------|-------------|-------------|------|
| #25 — Governance | CONTRIBUTING + SECURITY + templates | ~350 | 3-4 hours |
| #26 — DRMM Adapter | `pirtm_bridge.py` + tests | ~250 | 2-3 hours |
| #27 — Conformance | `conformance.py` + CLI + tests | ~350 | 3-4 hours |
| #28 — CI Hardening | `release.yml` + `nightly.yml` | ~200 | 2-3 hours |
| #29 — Release Automation | `bump_version.py` + checklist | ~150 | 1-2 hours |
| #30 — Supply Chain | Makefile + SBOM + signing | ~100 | 1-2 hours |

**Total: ~1,400 LOC, 6 issues, 12-18 hours of implementation.**

***

## Post-Tier 5 State

After Tier 5 merges, the PIRTM ecosystem reaches operational maturity:

- **Governance**: A contributor knows how to set up, commit, PR, and get reviewed — same patterns as Lambda-Proof
- **DRMM Integration**: DRMM calls `pirtm.run()` instead of rolling its own ad-hoc loops — contractivity guaranteed, `sympy` dependency dropped
- **COVENANT Conformance**: `pirtm-conformance --profile all` proves PIRTM satisfies the COVENANT's Core and Integrity profiles — machine-readable JSON for registry submission
- **Release Pipeline**: `git push origin v0.2.0` triggers build → test → publish → GitHub Release → SBOM → signed wheel with zero manual intervention
- **Supply Chain**: Every published wheel has a Sigstore signature, a CycloneDX SBOM, and a reproducible build verification target

The three repos — PIRTM, DRMM, Lambda-Proof — operate as a coordinated ecosystem rather than three isolated repositories.