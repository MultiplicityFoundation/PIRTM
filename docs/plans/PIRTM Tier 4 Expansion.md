# PIRTM Tier 4: Documentation, Examples, and Developer Onboarding — Expanded Specification

## Current Documentation State

The repository has two categories of documentation, neither of which describes the spec-aligned contractive core.

**Theory docs** (`docs/`) contain five markdown files: `primer.md`, `multiplicity.md`, `moonshine.md`, `langlands_prism.md`, and `riemann.md`. These describe high-level DRMM/PEOH concepts — the \( \Xi(t) \) operator, Langlands symmetries, Moonshine connections — but contain zero references to the actual `step()`, `run()`, `ace_certificate()`, or any other function in `src/core/`. They are theory essays, not code documentation.

**README** describes PIRTM in aspirational terms (quantum cognition, Riemann Hypothesis resolution) but never mentions `pip install`, import paths, or the contractive recurrence that the code actually implements.

**Examples** (`examples/`) contain three Jupyter notebooks that import `sympy`, define their own `evolve()` functions from scratch, and never use the `pirtm` package. They are standalone simulations disconnected from the codebase.

**Result**: A new contributor cloning the repo today cannot discover what the package does, how to install it, or how any function works. Tier 4 closes this gap with 7 deliverables across 4 issues.

***

## Deliverable Inventory

| Issue | Deliverable | File | Purpose |
|-------|-------------|------|---------|
| #21 | README rewrite | `README.md` | Installation, quickstart, package identity |
| #22a | API Reference | `docs/api/README.md` | Per-function docstring-derived reference |
| #22b | Architecture Guide | `docs/architecture.md` | Module map, dependency graph, data flow |
| #22c | Mathematical Specification | `docs/math_spec.md` | Formal definitions the code implements |
| #23a | Quickstart Notebook | `examples/quickstart.ipynb` | 5-minute runnable demo |
| #23b | Full Pipeline Notebook | `examples/full_pipeline.ipynb` | Budget → weights → run → certify → monitor |
| #24 | CHANGELOG | `CHANGELOG.md` | Version history starting at 0.1.0 |

***

## Issue #21: README Rewrite

### Problem Statement

The current README describes PIRTM as a "dynamic mathematical framework unifying number theory, tensor calculus, and quantum recursion." It mentions quantum cognition, Riemann Hypothesis, and prime-coded encryption. None of these are implemented in the codebase. The README never mentions `pip install pirtm`, `from pirtm import step`, or the contractive recurrence. A reader has no way to know what the package actually does.

### Target Audience

Three readers, in order of priority:

1. **The contributor** who clones the repo and needs to run tests in < 5 minutes
2. **The downstream developer** integrating `pirtm` into DRMM or Lambda-Proof
3. **The mathematician** evaluating the contractive guarantees

### Proposed Structure

```markdown
# PIRTM — Prime-Indexed Recursive Tensor Mathematics

> Contractive recurrence engine with certified convergence.
> Pure Python. NumPy only. Drop-in for Q-ARI and Lambda-Proof.

## What It Does

PIRTM provides a single contractive recurrence loop:

    X_{t+1} = P( Xi_t @ X_t + Lam_t @ T(X_t) + G_t )

with automatic safety projection ensuring q_t < 1 - epsilon at every step,
ACE-style certificates proving convergence, ISS bounds on disturbance
sensitivity, and PETC chain validation over prime-indexed events.

## Install

    pip install pirtm          # from PyPI (after Tier 1)
    pip install -e ".[dev]"    # local dev with test deps

## Quickstart

    from pirtm import step, ace_certificate
    import numpy as np

    X = np.ones(4)
    Xi = 0.3 * np.eye(4)
    Lam = 0.2 * np.eye(4)
    T = lambda x: 0.8 * x
    G = np.zeros(4)
    P = lambda x: x

    X_next, info = step(X, Xi, Lam, T, G, P, epsilon=0.05, op_norm_T=0.8)
    cert = ace_certificate(info)
    print(f"q = {info.q:.3f}, certified = {cert.certified}")

## Full Pipeline (Post Tier 2)

    from pirtm import (
        solve_budget, synthesize_weights, validate_schedule,
        build_gain_sequence, run, ace_certificate,
        fixed_point_estimate, multi_step_margin,
    )
    # ... (abbreviated, links to examples/full_pipeline.ipynb)

## Modules

| Module | Purpose |
|--------|---------|
| `pirtm.recurrence` | `step()` and `run()` — the contractive core |
| `pirtm.projection` | Soft and weighted-L1 parameter projection |
| `pirtm.certify` | ACE certificates and ISS bounds |
| `pirtm.adaptive` | Adaptive epsilon margin controller |
| `pirtm.fixed_point` | Tail-averaged fixed-point estimator |
| `pirtm.monitor` | Rolling telemetry monitor |
| `pirtm.petc` | PETC ledger and prime-chain validation |
| `pirtm.infinite_prime` | Prime coverage diagnostic |
| `pirtm.weights` | Weight schedule synthesizer (Tier 2) |
| `pirtm.gain` | Gain builder and operator norm estimator (Tier 2) |
| `pirtm.csc` | Contractive sufficient condition solver (Tier 2) |

## Documentation

- [API Reference](docs/api/README.md)
- [Architecture](docs/architecture.md)
- [Mathematical Specification](docs/math_spec.md)
- [Quickstart Notebook](examples/quickstart.ipynb)
- [Full Pipeline Notebook](examples/full_pipeline.ipynb)

## Development

    git clone https://github.com/MultiplicityFoundation/PIRTM.git
    cd PIRTM && git checkout Multiplicity
    pip install -e ".[dev]"
    pytest -v --cov=pirtm

## License

MIT (code) · CC BY-NC-SA 4.0 (documentation)
Maintained by Citizen Gardens / Multiplicity Foundation
```

### Acceptance Criteria

- README begins with a one-line description that matches what the code does
- Contains a working `pip install` command
- Contains a runnable quickstart that imports only from `pirtm`
- Module table lists all public modules with one-line descriptions
- Links to all four documentation files (created in Issues #22a-c)
- No references to quantum cognition, Riemann Hypothesis, or unimplemented features
- Existing theory content preserved — moved to `docs/theory/` subdirectory, not deleted

### Migration Plan for Existing Content

The current README's theory content is valuable but belongs in `docs/theory/README.md`, not in the package README. The PR:

1. Creates `docs/theory/` and moves the current README body into `docs/theory/overview.md`
2. Adds a link from the new README: "For the broader Multiplicity Theory context, see [Theory Overview](docs/theory/overview.md)"
3. Existing `docs/primer.md`, `docs/moonshine.md`, etc. move into `docs/theory/` alongside it
4. No content is deleted — only reorganized

***

## Issue #22a: API Reference (`docs/api/README.md`)

### Problem Statement

No function-level documentation exists outside of the source docstrings. A developer looking up `ace_certificate()` must read `certify.py` directly. The API reference extracts every public symbol into a single navigable document.

### Structure

One H2 section per module, one H3 per public symbol. Each entry contains:

- **Signature** (full typed signature, copied from source)
- **Description** (expanded from docstring)
- **Parameters** (table: name, type, default, description)
- **Returns** (type and description)
- **Raises** (exception types and conditions)
- **Example** (minimal runnable snippet)

### Modules to Document

Every symbol in `__all__` plus the Tier 2 additions:

| Module | Symbols | Count |
|--------|---------|-------|
| `types` | `StepInfo`, `Status`, `Certificate`, `PETCReport`, `MonitorRecord`, `PETCEntry` (Tier 2), `WeightSchedule` (Tier 2), `CSCBudget` (Tier 2), `CSCMargin` (Tier 2) | 9 |
| `recurrence` | `step`, `run` | 2 |
| `projection` | `project_parameters_soft`, `project_parameters_weighted_l1` | 2 |
| `certify` | `ace_certificate`, `iss_bound` | 2 |
| `adaptive` | `AdaptiveMargin` (class + `update` method) | 1 |
| `fixed_point` | `fixed_point_estimate` | 1 |
| `monitor` | `Monitor` (class + `push`, `summary`, `last`, `__iter__`) | 1 |
| `petc` | `PETCLedger` (class + `append`, `validate`, `coverage`), `petc_invariants` | 2 |
| `infinite_prime` | `infinite_prime_check` | 1 |
| `weights` | `synthesize_weights`, `validate_schedule` | 2 |
| `gain` | `estimate_operator_norm`, `build_gain_sequence`, `check_iss_compatibility` | 3 |
| `csc` | `solve_budget`, `compute_margin`, `multi_step_margin`, `sensitivity` | 4 |
| **Total** | | **30 symbols** |

### Example Entry Format

```markdown
### `ace_certificate`

```python
def ace_certificate(
    info: StepInfo | Sequence[StepInfo],
    *,
    tail_norm: float = 0.0,
) -> Certificate
```

Build an ACE-style convergence certificate from per-step telemetry.

**Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `info` | `StepInfo \| Sequence[StepInfo]` | required | Single step or trace |
| `tail_norm` | `float` | `0.0` | Norm of the tail iterate deviation |

**Returns**: `Certificate` with `certified`, `margin`, `tail_bound`, `details`.

**Raises**: `ValueError` if `info` is empty.

**Example**

```python
from pirtm import step, ace_certificate
X_next, info = step(X, Xi, Lam, T, G, P)
cert = ace_certificate(info)
assert cert.certified
```
```

### Acceptance Criteria

- Every symbol in `__all__` has an entry
- Every parameter is documented with type, default, and description
- Every entry has a runnable example
- No symbols are documented that do not exist in the codebase
- Document is navigable via markdown anchors (H2/H3 generate automatic links on GitHub)

### Estimated Size

~800-1000 lines of markdown. 30 symbols x ~30 lines per entry.

***

## Issue #22b: Architecture Guide (`docs/architecture.md`)

### Problem Statement

Lambda-Proof has an `ARCHITECTURE.md` explaining the client-server split. PIRTM has no equivalent. A contributor does not know which module calls which, what the data flow is, or where to add new functionality.

### Proposed Content

#### Module Dependency Diagram

```
types.py  ◄── recurrence.py ◄── gain.py
    ▲              ▲
    │              │
    ├── certify.py ◄── gain.py (calls iss_bound)
    │              ◄── csc.py  (reads StepInfo)
    │
    ├── projection.py ◄── recurrence.py
    │
    ├── petc.py (self-contained)
    │
    ├── weights.py (types + numpy)
    │
    ├── adaptive.py (types only)
    │
    ├── fixed_point.py (numpy only)
    │
    ├── monitor.py (types only)
    │
    └── infinite_prime.py (stdlib only)
```

#### Data Flow: One Contractive Step

```
Input: X_t, Xi_t, Lam_t, T, G_t, P, epsilon, op_norm_T
        │
        ▼
   ┌─ Compute q_t = ||Xi_t|| + ||Lam_t|| * ||T||
   │
   │  q_t > 1 - epsilon ?
   │  ├── YES → project_parameters_soft(Xi_t, Lam_t, ...) → recompute q_t
   │  └── NO  → proceed
   │
   ▼
   candidate = Xi_t @ X_t + Lam_t @ T(X_t) + G_t
   X_{t+1} = P(candidate)
   residual = ||X_{t+1} - X_t||
        │
        ▼
   Output: X_{t+1}, StepInfo(step, q, epsilon, nXi, nLam, projected, residual)
```

#### Section Outline

1. **Package Identity**: What `pirtm` is (contractive recurrence engine, not a simulation framework)
2. **Module Map**: Diagram above + one-line per module
3. **Data Flow**: The step diagram above
4. **Type Contracts**: How `StepInfo` → `Certificate` → `CSCMargin` chain through the pipeline
5. **Invariants**: The three invariants the package maintains (contractivity, projection feasibility, certificate consistency)
6. **Extension Points**: Where to add new operators, projectors, or certificate schemes
7. **Legacy Modules**: Location of `_legacy/` and why they exist
8. **Dependency Policy**: NumPy only. No scipy, no sympy, no external dependencies beyond stdlib + numpy.

### Acceptance Criteria

- Dependency diagram matches actual imports in the codebase
- Data flow diagram matches the logic in `step()`
- Extension points section names at least 3 concrete hooks (custom `Operator`, custom `Projector`, custom certificate builder)
- No references to modules that do not exist

### Estimated Size

~300-400 lines of markdown.

***

## Issue #22c: Mathematical Specification (`docs/math_spec.md`)

### Problem Statement

The existing `primer.md` defines the recurrence as \( \Xi(t+1) = \Lambda_m \cdot \Xi(t) \cdot T_{p_i} + \Phi(t) \). The actual code implements `X_{t+1} = P(Xi_t @ X_t + Lam_t @ T(X_t) + G_t)`. These are not the same equation. The primer uses matrix multiplication on the right; the code uses matrix-vector products with a projector. No document maps the code to its mathematical specification.

### Proposed Content

#### The Contractive Recurrence

The core iteration implemented by `step()`:

\[
X_{t+1} = \mathcal{P}\!\left(\Xi_t \, X_t + \Lambda_t \, T(X_t) + G_t\right)
\]

where:
- \( X_t \in \mathbb{R}^d \) is the state vector
- \( \Xi_t, \Lambda_t \in \mathbb{R}^{d \times d} \) are parameter matrices
- \( T : \mathbb{R}^d \to \mathbb{R}^d \) is a bounded linear operator
- \( G_t \in \mathbb{R}^d \) is the gain/disturbance
- \( \mathcal{P} : \mathbb{R}^d \to \mathbb{R}^d \) is a non-expansive projector

#### Contraction Coefficient

\[
q_t = \|\Xi_t\|_2 + \|\Lambda_t\|_2 \cdot \|T\|_{op}
\]

The system contracts when \( q_t < 1 - \epsilon \) for all \( t \). This is the contractive sufficient condition (CSC).

#### Safety Projection

When \( q_t > 1 - \epsilon \), the `project_parameters_soft` function rescales:

\[
\Xi_t' = \frac{1 - \epsilon}{\|\Xi_t\|_2 + \|\Lambda_t\|_2 \cdot \|T\|_{op}} \, \Xi_t, \quad \Lambda_t' = \frac{1 - \epsilon}{\|\Xi_t\|_2 + \|\Lambda_t\|_2 \cdot \|T\|_{op}} \, \Lambda_t
\]

#### ACE Certificate

Given a trace \( \{q_0, \dots, q_{N-1}\} \) with epsilons \( \{\epsilon_0, \dots, \epsilon_{N-1}\} \):

\[
q_{\max} = \max_t q_t, \quad \text{target} = 1 - \min_t \epsilon_t, \quad \text{margin} = \text{target} - q_{\max}
\]

\[
\text{certified} \iff \text{margin} \geq 0
\]

\[
\text{tail\_bound} = \begin{cases} \frac{\text{tail\_norm}}{1 - q_{\max}} & q_{\max} < 1 \\ \infty & q_{\max} \geq 1 \end{cases}
\]

#### ISS Bound

\[
\|X_t - X^*\| \leq \frac{\|G\|_{\infty}}{1 - q_{\max}}
\]

when \( q_{\max} < 1 \).

#### Weighted-L1 Projection

The `project_parameters_weighted_l1` solves:

\[
\min_{x'} \|x' - x\|_2^2 \quad \text{s.t.} \quad \sum_i w_i |x_i'| \leq B
\]

via the KKT-based threshold search with binary refinement.

#### Adaptive Margin Update

The `AdaptiveMargin.update()` rule:

\[
\epsilon_{t+1} = \begin{cases}
\min(\epsilon_{\max},\; \epsilon_t + \delta) & \text{if } q_t > 1 - \epsilon_t \\
\max(\epsilon_{\min},\; \epsilon_{\text{base}},\; \epsilon_t - \delta) & \text{if } r_t < r^* \text{ and margin} > 0.05 \\
\epsilon_t & \text{otherwise}
\end{cases}
\]

#### Fixed-Point Estimator

\[
\hat{X}^* = \frac{1}{W} \sum_{t=N-W}^{N-1} X_t, \quad \text{tail\_bound} = \max_{t \in [N-W, N-1]} \|X_t - \hat{X}^*\|
\]

where \( W = \min(\text{window}, N) \).

#### PETC Chain Invariants

A valid PETC chain \( \mathcal{C} = \{(p_i, e_i)\} \) satisfies:
1. \( p_i \in \mathbb{P} \) for all \( i \)
2. \( p_i < p_{i+1} \) (monotonicity)
3. \( p_{i+1} - p_i \leq g_{\max} \) (gap bound)
4. \( |\mathcal{C}| \geq N_{\min} \)

Coverage: \( \rho(\mathcal{C}, [a,b]) = |\mathcal{C} \cap [a,b]| \,/\, |\mathbb{P} \cap [a,b]| \)

#### Code-to-Math Map

| Math Symbol | Code Location | Variable |
|------------|---------------|----------|
| \( X_t \) | `recurrence.step()` | `X_t` parameter |
| \( \Xi_t \) | `recurrence.step()` | `Xi_t` parameter |
| \( \Lambda_t \) | `recurrence.step()` | `Lam_t` parameter |
| \( T \) | `recurrence.step()` | `T` parameter (callable) |
| \( G_t \) | `recurrence.step()` | `G_t` parameter |
| \( \mathcal{P} \) | `recurrence.step()` | `P` parameter |
| \( q_t \) | `recurrence.step()` | `q_t` local → `StepInfo.q` |
| \( \epsilon \) | `recurrence.step()` | `epsilon` kwarg |
| \( \|T\|_{op} \) | `recurrence.step()` | `op_norm_T` kwarg |
| margin | `certify.ace_certificate()` | `Certificate.margin` |
| tail_bound | `certify.ace_certificate()` | `Certificate.tail_bound` |

### Acceptance Criteria

- Every equation has a corresponding code location in the Code-to-Math Map
- Every code function with mathematical semantics is represented by at least one equation
- Notation is consistent throughout (no switching between \( \Xi \) and Xi without the map)
- The recurrence equation matches what `step()` actually computes
- No equations reference unimplemented features

### Estimated Size

~400-500 lines of markdown.

***

## Issue #23a: Quickstart Notebook (`examples/quickstart.ipynb`)

### Problem Statement

The existing notebooks import `sympy`, define ad-hoc `evolve()` functions, and never use the `pirtm` package. A new user has no runnable example that demonstrates the actual package.

### Proposed Content

A single Jupyter notebook with 6 cells, executable in < 30 seconds:

**Cell 1 — Install**
```python
# !pip install pirtm  # uncomment if not installed
import numpy as np
from pirtm import step, run, ace_certificate
```

**Cell 2 — Setup**
```python
dim = 4
X0 = np.ones(dim)
Xi = 0.3 * np.eye(dim)
Lam = 0.2 * np.eye(dim)
T = lambda x: 0.8 * x
G = np.zeros(dim)
P = lambda x: x  # identity projector
```

**Cell 3 — Single Step**
```python
X1, info = step(X0, Xi, Lam, T, G, P, epsilon=0.05, op_norm_T=0.8)
print(f"q = {info.q:.4f}, projected = {info.projected}, residual = {info.residual:.6f}")
```

**Cell 4 — Full Run**
```python
N = 20
Xi_seq = [Xi] * N
Lam_seq = [Lam] * N
G_seq = [G] * N

X_final, history, infos, status = run(
    X0, Xi_seq, Lam_seq, G_seq,
    T=T, P=P, epsilon=0.05, op_norm_T=0.8,
)
print(f"Converged: {status.converged}, Steps: {status.steps}, Residual: {status.residual:.2e}")
```

**Cell 5 — Certificate**
```python
cert = ace_certificate(infos)
print(f"Certified: {cert.certified}, Margin: {cert.margin:.4f}, Tail bound: {cert.tail_bound:.4f}")
```

**Cell 6 — Visualize Convergence**
```python
import matplotlib.pyplot as plt
residuals = [info.residual for info in infos]
qs = [info.q for info in infos]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.semilogy(residuals)
ax1.set_xlabel("Step"); ax1.set_ylabel("Residual"); ax1.set_title("Convergence")
ax2.plot(qs)
ax2.axhline(y=1 - 0.05, color='r', linestyle='--', label='target')
ax2.set_xlabel("Step"); ax2.set_ylabel("q_t"); ax2.set_title("Contraction Coefficient")
ax2.legend()
plt.tight_layout(); plt.show()
```

### Acceptance Criteria

- Notebook runs end-to-end without error on Python 3.11+
- Imports only from `pirtm`, `numpy`, and `matplotlib`
- No `sympy` dependency
- Produces two plots: residual convergence (semilog) and contraction coefficient trace
- Cell output shows `Converged: True` and `Certified: True`

### Migration of Existing Notebooks

Existing notebooks move to `examples/legacy/`:

```
examples/
├── quickstart.ipynb              # NEW
├── full_pipeline.ipynb           # NEW (Issue #23b)
├── legacy/
│   ├── example_multiplicity_flow.ipynb   # Existing
│   ├── example_peoh_proof.ipynb          # Existing
│   └── example_qai_integration.ipynb     # Existing
└── README.md                     # Updated index
```

***

## Issue #23b: Full Pipeline Notebook (`examples/full_pipeline.ipynb`)

### Problem Statement

After Tier 2 lands, the package supports a complete workflow: CSC budget → weight synthesis → gain construction → run → certify → estimate → monitor → PETC. No example demonstrates this end-to-end pipeline.

### Proposed Content

A Jupyter notebook with 10 cells:

1. **Imports**: All Tier 0 + Tier 2 symbols
2. **Define System**: Operator `T`, dimension, prime sequence, epsilon
3. **Estimate Operator Norm**: `estimate_operator_norm(T, dim)`
4. **Solve CSC Budget**: `solve_budget(op_norm_T, epsilon)`
5. **Synthesize Weights**: `synthesize_weights(primes, dim, ...)`, `validate_schedule(...)`
6. **Build Gains**: `build_gain_sequence(N, dim, profile="decay")`
7. **Run Recurrence**: `run(X0, Xi_seq, Lam_seq, G_seq, T=T, P=P)`
8. **Certify + Margin**: `ace_certificate(infos)`, `multi_step_margin(infos)`
9. **Fixed-Point Estimate**: `fixed_point_estimate(history, window=5)`
10. **PETC + Monitor**: Build ledger, push to monitor, validate chain
11. **Visualization**: 4-panel plot (residuals, q_t trace, margin over time, PETC coverage)

### Key Differences from Quickstart

| Aspect | Quickstart | Full Pipeline |
|--------|-----------|---------------|
| Modules used | 3 (`step`, `run`, `ace_certificate`) | 12+ (all public symbols) |
| Parameter setup | Hand-crafted | Computed from `solve_budget` + `synthesize_weights` |
| Gain | Zero vector | `build_gain_sequence` with decay |
| Certificate | Single call | `ace_certificate` + `multi_step_margin` + `sensitivity` |
| PETC | Not shown | Full ledger with coverage check |
| Monitor | Not shown | Rolling telemetry with summary |
| Plots | 2 panels | 4 panels |
| Runtime | < 30 seconds | < 60 seconds |

### Acceptance Criteria

- Runs end-to-end without error after Tier 2 modules are merged
- Imports only from `pirtm`, `numpy`, `matplotlib`
- Every Tier 2 function is called at least once
- Produces a 4-panel figure
- Final cell prints a summary dict with keys: `converged`, `certified`, `margin`, `coverage`, `tail_bound`
- Notebook has markdown cells explaining each step (not just code cells)

***

## Issue #24: CHANGELOG

### Problem Statement

No version history exists. When Tier 1 ships `pirtm 0.1.0`, there must be a CHANGELOG documenting what is included.

### Proposed Format

Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) conventions:

```markdown
# Changelog

All notable changes to PIRTM are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `docs/api/README.md` — API reference for all public symbols
- `docs/architecture.md` — module map, dependency graph, data flow
- `docs/math_spec.md` — formal mathematical specification
- `examples/quickstart.ipynb` — 5-minute runnable demo
- `examples/full_pipeline.ipynb` — end-to-end pipeline notebook
- Existing theory docs reorganized into `docs/theory/`
- Existing example notebooks moved to `examples/legacy/`

## [0.2.0] — TBD

### Added
- `pirtm.petc.PETCLedger` — append-only prime-indexed event chain (Issue #4)
- `pirtm.weights` — weight schedule synthesizer (Issue #5)
- `pirtm.gain` — gain builder and operator norm estimator (Issue #6)
- `pirtm.csc` — contractive sufficient condition solver (Issue #7)
- New types: `PETCEntry`, `WeightSchedule`, `CSCBudget`, `CSCMargin`

### Changed
- `petc_invariants()` now delegates to `PETCLedger.validate()` internally

## [0.1.0] — TBD

### Added
- Package layout: `src/pirtm/` with `pyproject.toml` (Issue #1)
- CI pipeline: lint + typecheck + test on Python 3.11-3.13 (Issue #2)
- Legacy shims: `src/pirtm/_legacy/` wrapping original modules (Issue #3)
- Core modules: `types`, `recurrence`, `projection`, `certify`,
  `adaptive`, `fixed_point`, `monitor`, `petc`, `infinite_prime`
- Public API via `__all__` in `__init__.py`
```

### Acceptance Criteria

- Follows Keep a Changelog format
- Every Tier 1, 2, and 4 deliverable appears in the correct version section
- `[Unreleased]` section exists for in-progress work
- No entries reference features that do not exist in the corresponding version

***

## Execution Sequence

```
Tier 1 ──► Tier 2 ──► Tier 3 ──► Tier 4
                                    │
                      ┌─────────────┼──────────────┐
                      ▼             ▼              ▼
                  #21 README    #22a-c Docs    #23a-b Examples
                      │             │              │
                      └─────────────┼──────────────┘
                                    ▼
                              #24 CHANGELOG
```

### Dependencies

| Issue | Depends On | Rationale |
|-------|-----------|-----------|
| #21 README | Tier 1 (installable package) | README references `pip install pirtm` |
| #22a API Reference | Tier 2 (all modules exist) | Documents Tier 2 symbols |
| #22b Architecture | Tier 1 | Describes module map as-built |
| #22c Math Spec | Tier 2 | Covers CSC, weight, gain equations |
| #23a Quickstart | Tier 1 | Uses `step`, `run`, `ace_certificate` |
| #23b Full Pipeline | Tier 2 | Uses all Tier 2 functions |
| #24 CHANGELOG | Tier 1 + 2 | Documents both versions |

Issues #21, #22b, and #23a can start as soon as Tier 1 lands. Issues #22a, #22c, #23b, and #24 require Tier 2 completion.

### Estimated Effort

| Issue | Deliverable | LOC (approx) | Time |
|-------|-------------|-------------|------|
| #21 — README | `README.md` | ~120 | 1-2 hours |
| #22a — API Reference | `docs/api/README.md` | ~900 | 4-6 hours |
| #22b — Architecture | `docs/architecture.md` | ~350 | 2-3 hours |
| #22c — Math Spec | `docs/math_spec.md` | ~450 | 3-4 hours |
| #23a — Quickstart | `examples/quickstart.ipynb` | ~80 cells | 1-2 hours |
| #23b — Full Pipeline | `examples/full_pipeline.ipynb` | ~150 cells | 2-3 hours |
| #24 — CHANGELOG | `CHANGELOG.md` | ~60 | 30 min |

**Total: ~2,100 lines of documentation, 7 deliverables, 4 issues.**

***

## Post-Tier 4 State

After merge, the repository transforms from an opaque collection of source files into a documented, installable, example-backed package:

- **README**: A newcomer knows what PIRTM does, how to install it, and how to run a first step in < 2 minutes
- **API Reference**: Every public function is documented with signature, parameters, returns, raises, and example
- **Architecture**: A contributor knows the module dependency graph, data flow, and extension points
- **Math Spec**: A mathematician can verify that the code matches its formal specification, equation by equation
- **Quickstart**: A runnable notebook proves the package works
- **Full Pipeline**: A complete workflow demonstrates every module in concert
- **CHANGELOG**: Version history tracks what shipped and when

The theory docs (`primer.md`, `moonshine.md`, etc.) remain accessible under `docs/theory/` — preserved, not deleted, but no longer masquerading as code documentation.