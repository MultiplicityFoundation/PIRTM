# PIRTM Tier 1: Packaging, Layout, and CI — Expanded Specification

## Current Layout (As-Is)

The repository lives on a single branch `Multiplicity`. The file tree:

```
PIRTM/
├── LICENSE                          # MIT
├── README.md                        # Narrative (needs rewrite, Tier 4)
├── applications/                    # 3 markdown concept docs
├── docs/                            # 5 markdown theory docs
├── examples/                        # 3 Jupyter notebooks (legacy imports)
├── figures/                         # Empty placeholder
├── notebooks/                       # 3 Jupyter notebooks (legacy imports)
├── papers/                          # 6 PDFs (Multiplicity, Prime Cascade 1-4, GUT)
├── src/
│   ├── README.md                    # 1-byte placeholder
│   ├── core/                        # <-- THE CODE LIVES HERE
│   │   ├── __init__.py              # Clean public API with __all__
│   │   ├── adaptive.py              # AdaptiveMargin
│   │   ├── certify.py               # ace_certificate, iss_bound
│   │   ├── fixed_point.py           # fixed_point_estimate
│   │   ├── infinite_prime.py        # infinite_prime_check
│   │   ├── monitor.py               # Monitor
│   │   ├── petc.py                  # petc_invariants (stub)
│   │   ├── pir_tensor.py            # LEGACY PrimeTensorSystem
│   │   ├── projection.py            # project_parameters_soft/weighted_l1
│   │   ├── recurrence.py            # step(), run()
│   │   ├── recursive_ops.py         # LEGACY recursive_update
│   │   ├── spectral_decomp.py       # LEGACY spectral analysis
│   │   └── types.py                 # StepInfo, Status, Certificate, ...
│   └── simulations/                 # 3 legacy simulation scripts
└── tests/                           # 3 legacy test files
```

### Import Problem

The package is not installable. The `__init__.py` at `src/core/__init__.py` exports a clean API, but there is no `pyproject.toml`, no `setup.py`, and no top-level package directory. This means:

- `import pirtm` fails everywhere.
- All three simulation modules import via bare names: `from pir_tensor import PrimeTensorSystem`. These only work when the CWD is `src/core/`.
- All three legacy test files import the same way: `from pir_tensor import PrimeTensorSystem`. They break under `pytest` from the repo root.

No downstream consumer — including the DRMM or Lambda-Proof repos — can depend on PIRTM as a proper Python package.

## Target Layout (To-Be)

```
PIRTM/
├── .github/
│   └── workflows/
│       └── ci.yml                   # NEW — lint, typecheck, test
├── LICENSE
├── README.md                        # Rewritten (Tier 4, not this PR)
├── CONTRIBUTING.md                  # NEW (Tier 4)
├── CHANGELOG.md                     # NEW (Tier 4)
├── pyproject.toml                   # NEW — build metadata + tool config
├── applications/
├── docs/
├── examples/
├── figures/
├── notebooks/
├── papers/
├── src/
│   └── pirtm/                       # RENAMED from src/core/
│       ├── __init__.py              # Updated version + re-exports
│       ├── adaptive.py
│       ├── certify.py
│       ├── fixed_point.py
│       ├── infinite_prime.py
│       ├── monitor.py
│       ├── petc.py
│       ├── projection.py
│       ├── recurrence.py
│       ├── types.py
│       ├── _legacy/                 # NEW — quarantine zone
│       │   ├── __init__.py
│       │   ├── pir_tensor.py        # MOVED from src/core/
│       │   ├── recursive_ops.py     # MOVED from src/core/
│       │   └── spectral_decomp.py   # MOVED from src/core/
│       └── simulations/             # MOVED from src/simulations/
│           ├── __init__.py          # NEW
│           ├── qari_module.py       # Updated imports
│           ├── quantum_feedback.py  # Updated imports
│           └── riemann_verification.py  # Updated imports
└── tests/
    ├── conftest.py                  # NEW — shared fixtures
    ├── test_primes.py               # Updated imports → pirtm._legacy
    ├── test_spectral.py             # Updated imports → pirtm._legacy
    └── test_tensor_dynamics.py      # Updated imports → pirtm._legacy
```

## Issue #1: Restructure Package Layout

### Objective

Move `src/core/` to `src/pirtm/` so that `import pirtm` works when the package is installed via `pip install -e .`.

### Exact File Operations

**Renames (preserve content, change path):**

| From | To |
|------|----|
| `src/core/__init__.py` | `src/pirtm/__init__.py` |
| `src/core/adaptive.py` | `src/pirtm/adaptive.py` |
| `src/core/certify.py` | `src/pirtm/certify.py` |
| `src/core/fixed_point.py` | `src/pirtm/fixed_point.py` |
| `src/core/infinite_prime.py` | `src/pirtm/infinite_prime.py` |
| `src/core/monitor.py` | `src/pirtm/monitor.py` |
| `src/core/petc.py` | `src/pirtm/petc.py` |
| `src/core/projection.py` | `src/pirtm/projection.py` |
| `src/core/recurrence.py` | `src/pirtm/recurrence.py` |
| `src/core/types.py` | `src/pirtm/types.py` |

**Moves to legacy quarantine:**

| From | To |
|------|----|
| `src/core/pir_tensor.py` | `src/pirtm/_legacy/pir_tensor.py` |
| `src/core/recursive_ops.py` | `src/pirtm/_legacy/recursive_ops.py` |
| `src/core/spectral_decomp.py` | `src/pirtm/_legacy/spectral_decomp.py` |

**New files to create:**

| Path | Content |
|------|---------|
| `src/pirtm/_legacy/__init__.py` | Deprecation-warning re-exports of legacy modules |
| `src/pirtm/simulations/__init__.py` | Empty `__init__` |

**Moves:**

| From | To |
|------|----|
| `src/simulations/qari_module.py` | `src/pirtm/simulations/qari_module.py` |
| `src/simulations/quantum_feedback.py` | `src/pirtm/simulations/quantum_feedback.py` |
| `src/simulations/riemann_verification.py` | `src/pirtm/simulations/riemann_verification.py` |

### Internal Import Rewrites

Every `from .xyz import ...` inside the spec-aligned modules stays the same — those are relative imports and the directory structure preserves adjacency.

The `__init__.py` relative imports also stay identical — they reference `.types`, `.recurrence`, `.projection`, etc. The only change is adding a `__version__` string.

**Updated `src/pirtm/__init__.py` additions (prepend to existing):**

```python
__version__ = "0.1.0dev0"
```

**Legacy quarantine `src/pirtm/_legacy/__init__.py`:**

```python
"""Legacy PIRTM modules — deprecated, will be removed in v0.2.0."""
import warnings as _w

_w.warn(
    "pirtm._legacy modules are deprecated and will be removed in v0.2.0. "
    "Use the contractive core (pirtm.recurrence, pirtm.projection, etc.) instead.",
    DeprecationWarning,
    stacklevel=2,
)

from .pir_tensor import PrimeTensorSystem
from .recursive_ops import recursive_update, contraction_check, is_stable, feedback_operator
from .spectral_decomp import (
    spectral_decomposition, spectral_entropy, phase_coherence,
    plot_spectrum, analyze_tensor,
)
```

**Simulation modules import rewrites:**

All three simulation files currently import bare names:
```python
from pir_tensor import PrimeTensorSystem
from recursive_ops import recursive_update
from spectral_decomp import analyze_tensor
```

These become:
```python
from pirtm._legacy import PrimeTensorSystem
from pirtm._legacy import recursive_update
from pirtm._legacy import analyze_tensor
```

**Legacy test import rewrites:**

All three test files currently import bare names:
```python
from pir_tensor import PrimeTensorSystem
from recursive_ops import recursive_update, contraction_check, is_stable
from spectral_decomp import spectral_decomposition, spectral_entropy, ...
```

These become:
```python
from pirtm._legacy import PrimeTensorSystem
from pirtm._legacy import recursive_update, contraction_check, is_stable
from pirtm._legacy import spectral_decomposition, spectral_entropy, ...
```

### Files to Delete After Move

| Path | Reason |
|------|--------|
| `src/core/` (entire directory) | Replaced by `src/pirtm/` |
| `src/simulations/` (entire directory) | Moved to `src/pirtm/simulations/` |
| `src/README.md` | 1-byte placeholder, no longer needed |

### Acceptance Criteria

- `python -c "import pirtm; print(pirtm.__version__)"` prints `0.1.0dev0`
- `python -c "from pirtm import step, run, ace_certificate, project_parameters_weighted_l1"` succeeds
- `python -c "from pirtm._legacy import PrimeTensorSystem"` succeeds with a `DeprecationWarning`
- All existing legacy tests pass when invoked via `python -m pytest tests/`

## Issue #2: Add `pyproject.toml`

### Objective

Create a PEP 621-compliant `pyproject.toml` at repo root that makes `pip install -e .` work, declares dependencies, and configures tooling.

### Full File Content

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "pirtm"
version = "0.1.0dev0"
description = "Prime-Indexed Recursive Tensor Mathematics — certified contractive core"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [
    { name = "Tyler Van Osdol" },
    { name = "Ryan Van Gelder" },
]
keywords = ["tensor", "prime", "contraction", "spectral", "multiplicity"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Scientific/Engineering :: Mathematics",
]
dependencies = [
    "numpy>=1.24",
]

[project.optional-dependencies]
legacy = [
    "sympy>=1.12",
    "matplotlib>=3.7",
]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.4",
    "mypy>=1.10",
]
all = ["pirtm[legacy,dev]"]

[project.urls]
Homepage = "https://github.com/MultiplicityFoundation/PIRTM"
Repository = "https://github.com/MultiplicityFoundation/PIRTM"
Issues = "https://github.com/MultiplicityFoundation/PIRTM/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/pirtm"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"

[tool.ruff]
target-version = "py311"
line-length = 100
src = ["src"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "SIM", "TCH"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
mypy_path = "src"
packages = ["pirtm"]
```

### Design Decisions

**Build backend: Hatchling.** Minimal config, supports `src/` layout natively via `[tool.hatch.build.targets.wheel]`. No `setup.py` or `setup.cfg` needed.

**Python ≥ 3.11.** The codebase uses `X | Y` union syntax and `slots=True` on dataclasses, both requiring 3.10+. Targeting 3.11 provides a reasonable floor.

**Core dependency: numpy only.** The spec-aligned modules import nothing beyond `numpy` and the standard library. This keeps the install lightweight.

**Optional `legacy` group.** The three legacy modules require `sympy` (for `primerange`, `nextprime`, `isprime`) and `matplotlib` (for `plot_spectrum`). Contributors working on those modules install via `pip install -e ".[legacy]"`.

**Optional `dev` group.** Pins minimum versions for `pytest`, `ruff`, `mypy`, `pytest-cov` to support CI.

### Acceptance Criteria

- From a clean virtualenv: `pip install -e .` succeeds with only `numpy` installed
- `pip install -e ".[dev]"` installs `pytest`, `ruff`, `mypy`, `pytest-cov`
- `pip install -e ".[legacy]"` installs `sympy`, `matplotlib`
- `pip install -e ".[all]"` installs everything
- `python -c "import pirtm"` succeeds post-install

## Issue #3: Add GitHub Actions CI

### Objective

Create `.github/workflows/ci.yml` that runs on every push and PR to `Multiplicity`, executing: lint → type-check → test.

### Full Workflow Content

```yaml
name: CI

on:
  push:
    branches: [Multiplicity]
  pull_request:
    branches: [Multiplicity]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint (ruff)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check src/ tests/
      - run: ruff format --check src/ tests/

  typecheck:
    name: Type-check (mypy)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: mypy src/pirtm/

  test:
    name: Test (pytest) — Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[all]"
      - run: pytest --cov=pirtm --cov-report=term-missing -v
```

### Design Decisions

**Three parallel jobs.** Lint and typecheck are fast (~15s each). Testing runs on the full Python matrix (3.11, 3.12, 3.13) in parallel. Total wall-clock time: ~90 seconds for a clean run.

**Concurrency control.** `cancel-in-progress: true` avoids stacking duplicate runs when a PR is force-pushed.

**`[all]` install for test job.** Legacy tests need `sympy`/`matplotlib`. The `all` extras group pulls in everything so both spec-aligned and legacy tests can run.

**`fail-fast: false`.** A failure on 3.11 should not mask a pass on 3.13 or vice-versa.

**No deployment step yet.** PyPI publishing will be added when `v0.1.0` is tagged (post Tier 2-4 completion).

### Acceptance Criteria

- Push to `Multiplicity` triggers all three jobs
- PR against `Multiplicity` triggers all three jobs
- `ruff check` passes with zero findings on current codebase
- `mypy` passes `--strict` on `src/pirtm/` (spec-aligned modules only — legacy excluded from strict check)
- `pytest` discovers and runs all test files in `tests/`
- Green status check required for PR merge (configure in repo settings post-merge)

## Execution Sequence

These three issues form a strict dependency chain:

```
#1 (layout) ──► #2 (pyproject.toml) ──► #3 (CI)
```

**Issue #1** must land first because `pyproject.toml` references `src/pirtm` as the package root. **Issue #2** must land before #3 because the CI workflow calls `pip install -e ".[all]"` and `mypy src/pirtm/`. Each issue is one PR against `Multiplicity`.

### Estimated Effort

| Issue | Files Touched | LOC Changed | Time Estimate |
|-------|---------------|-------------|---------------|
| #1 — Layout | ~20 files (renames + import rewrites) | ~50 lines modified | 1-2 hours |
| #2 — pyproject.toml | 1 new file | ~70 lines | 15 minutes |
| #3 — CI workflow | 1 new file | ~50 lines | 15 minutes |

### Risk: mypy --strict on First Run

The spec-aligned modules use `from __future__ import annotations` and basic type hints, but some callables are typed as `Callable` without full signatures, and `Projector` is a type alias. The first mypy run may surface 5-15 findings that need annotation fixes. These should be addressed in the same PR as #2 or as a fast-follow.

### Risk: Legacy Test Imports

The legacy tests import `sympy.isprime` and use `PrimeTensorSystem` with random state. After the import rewrite, they will emit `DeprecationWarning` on every run. This is intentional — it signals to contributors that those modules are on the removal path. The warnings will not cause test failures unless `pytest` is configured with `-W error::DeprecationWarning`, which the proposed `pytest.ini_options` does not set.

## Post-Tier 1 State

Once all three PRs merge, any contributor can:

```bash
git clone https://github.com/MultiplicityFoundation/PIRTM.git
cd PIRTM
pip install -e ".[dev]"
python -c "from pirtm import step, run, ace_certificate; print('ready')"
pytest -v
```

Every subsequent PR (Tier 2 modules, Tier 3 tests, Tier 4 docs) will get automatic lint + typecheck + test on push. The contractive core becomes a first-class installable package. The legacy code is quarantined, deprecation-warned, and import-compatible so nothing breaks during the transition.