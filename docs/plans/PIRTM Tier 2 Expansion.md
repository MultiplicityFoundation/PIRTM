# PIRTM Tier 2: Missing Core Modules — Expanded Specification

## Context: What Exists vs. What Is Missing

The PIRTM contractive core currently ships 10 spec-aligned modules inside `src/core/`. These implement the recurrence loop, projections, certificates, monitoring, and adaptive margins. The public `__init__.py` exports everything via `__all__`.

After Tier 1 lands, the package will be installable as `pirtm` and CI will enforce lint + typecheck + test on every push.

Tier 2 adds the four missing modules that complete the mathematical specification. Each module below is self-contained, imports only `numpy` and existing `pirtm.*` modules, and exports through `__init__.py`.

***

## Module Inventory (Before / After)

| Module | Status | File |
|--------|--------|------|
| `types.py` | Done | Dataclasses: `StepInfo`, `Status`, `Certificate`, `PETCReport`, `MonitorRecord` |
| `recurrence.py` | Done | `step()`, `run()` — the contractive core loop |
| `projection.py` | Done | `project_parameters_soft()`, `project_parameters_weighted_l1()` |
| `certify.py` | Done | `ace_certificate()`, `iss_bound()` |
| `fixed_point.py` | Done | `fixed_point_estimate()` — tail-averaged estimator |
| `adaptive.py` | Done | `AdaptiveMargin` — epsilon controller |
| `monitor.py` | Done | `Monitor` — rolling telemetry |
| `infinite_prime.py` | Done | `infinite_prime_check()` — coverage diagnostic |
| `petc.py` | **Stub** | `petc_invariants()` — validates primes only, missing ledger/chain semantics |
| `weights.py` | **Missing** | Prime weight synthesizer — no file exists |
| `gain.py` | **Missing** | Gain builder / operator norm estimator — no file exists |
| `csc.py` | **Missing** | Contractive sufficient condition solver — no file exists |

***

## Issue #4: Rewrite `petc.py` — Full PETC Ledger

### Problem Statement

The current `petc.py` checks whether a list of integers are prime and returns a `PETCReport`. This is a primality validator, not a Prime-typed Event-Triggered Chain ledger. The spec requires:

- **Chain construction**: Given a sequence of events indexed by primes, build an ordered ledger with event metadata.
- **Gap analysis**: Detect prime-gap violations where consecutive chain links exceed a maximum allowable gap.
- **Coverage scoring**: Compute the fraction of prime indices that are present vs. expected in a given range.
- **Chain integrity**: Verify that the chain is monotonically ordered and free of duplicates.
- **Binding to `StepInfo`**: Each ledger entry should optionally carry a `StepInfo` from the contractive core, linking the PETC chain to the recurrence's telemetry.

### Mathematical Specification

A PETC chain \( \mathcal{C} \) is an ordered sequence of prime-indexed events:

\[
\mathcal{C} = \{(p_i, e_i)\}_{i=1}^{N}, \quad p_1 < p_2 < \cdots < p_N, \quad p_i \in \mathbb{P}
\]

**Chain validity** requires:

1. **Primality**: Every index \( p_i \) is prime (keep from existing code)
2. **Monotonicity**: \( p_i < p_{i+1} \) for all \( i \)
3. **Gap bound**: \( p_{i+1} - p_i \leq g_{\max} \) for a user-defined \( g_{\max} \)
4. **Minimum length**: \( N \geq N_{\min} \)

**Coverage score**:

\[
\rho(\mathcal{C}, [a, b]) = \frac{|\{p_i \in \mathcal{C} : a \leq p_i \leq b\}|}{|\{p \in \mathbb{P} : a \leq p \leq b\}|}
\]

### New Types (add to `types.py`)

```python
@dataclass(slots=True)
class PETCEntry:
    """Single entry in a PETC ledger."""
    prime: int
    event: Any  # user-defined payload
    info: StepInfo | None = None
    timestamp: float | None = None


@dataclass(slots=True)
class PETCReport:  # REPLACE existing
    """Full PETC chain diagnostic."""
    satisfied: bool
    chain_length: int
    coverage: float
    gap_violations: list[tuple[int, int]]  # (p_i, p_{i+1}) pairs
    monotonic: bool
    violations: list[int]  # non-prime indices
    primes_checked: list[int]
```

### Proposed API

```python
class PETCLedger:
    """Append-only prime-indexed event-triggered chain."""

    def __init__(self, *, max_gap: int = 100, min_length: int = 3) -> None: ...
    def append(self, prime: int, event: Any = None, info: StepInfo | None = None) -> PETCEntry: ...
    def validate(self) -> PETCReport: ...
    def coverage(self, lo: int, hi: int) -> float: ...
    def entries(self) -> list[PETCEntry]: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[PETCEntry]: ...
```

**Backward-compat shim**: The free function `petc_invariants()` stays in the public API and delegates to `PETCLedger().validate()` internally. Existing callers see no break.

### Internal Implementation Notes

- Primality check: Keep the existing `_is_prime()` helper — it is stdlib-only, no `sympy` dependency.
- Gap detection: Single pass over sorted entries, \( O(N) \).
- Coverage: Use `_is_prime()` sieve over `[lo, hi]` to build the denominator. For ranges up to 10^6 this is sub-second.
- No new dependencies. Pure `numpy`-free — this module uses only builtins and `math`.

### Acceptance Criteria

- `PETCLedger` is constructable with default and custom `max_gap`, `min_length`
- `append()` raises `ValueError` on non-prime index
- `validate()` returns `PETCReport` with correct `coverage`, `gap_violations`, `monotonic` fields
- `coverage(2, 100)` returns 1.0 if all primes in  are present[^1]
- `petc_invariants([2, 3, 5, 7, 11])` returns backward-compatible `PETCReport` with `satisfied=True`
- `petc_invariants([2, 4, 6])` still raises for mass violation (existing behavior preserved)

### File: `src/pirtm/petc.py` — ~120 LOC

***

## Issue #5: Add `weights.py` — Prime Weight Synthesizer

### Problem Statement

The contractive recurrence in `recurrence.py` operates on sequences of parameter matrices `Xi_seq` and `Lam_seq`. The theory defines these weights as functions of the prime index — specifically, the contraction coefficient \( q_t \) at step \( t \) is:

\[
q_t = \|\Xi_t\| + \|\Lambda_t\| \cdot \|T\|_{op}
\]

This is computed inside `step()`, but there is no module that **synthesizes** the weight sequences \( \{\Xi_t\} \) and \( \{\Lambda_t\} \) from a set of primes and a target contraction budget. The caller must hand-craft these arrays. This is the gap: the package provides the loop but not the initialization.

### Mathematical Specification

Given:
- A prime sequence \( \{p_k\}_{k=1}^{N} \)
- An operator norm \( \|T\|_{op} \)
- A contraction budget \( q^* < 1 \)
- A decay profile \( \alpha(k) \) (e.g. \( 1/\log p_k \))

**Synthesize**:

\[
\Xi_k = \frac{\alpha(k) \cdot q^*}{1 + \|T\|_{op}} \cdot I_d
\]

\[
\Lambda_k = \frac{(1 - \alpha(k)) \cdot q^*}{(1 + \|T\|_{op}) \cdot \|T\|_{op}} \cdot I_d
\]

This guarantees \( q_k = \|\Xi_k\| + \|\Lambda_k\| \cdot \|T\|_{op} \leq q^* \) by construction.

**Alternative profiles** the module should support:
- `"uniform"`: \( \alpha(k) = 0.5 \) for all \( k \)
- `"log_decay"`: \( \alpha(k) = 1 / \log(p_k) \), normalized to[^2]
- `"harmonic"`: \( \alpha(k) = 1/k \)
- Custom callable: `Callable[[int, int], float]` taking `(k, p_k)`

### Proposed API

```python
WeightProfile = Literal["uniform", "log_decay", "harmonic"] | Callable[[int, int], float]


@dataclass(slots=True)
class WeightSchedule:
    """Pre-computed weight sequences for the contractive recurrence."""
    Xi_seq: list[np.ndarray]      # len = N, each (d, d)
    Lam_seq: list[np.ndarray]     # len = N, each (d, d)
    q_targets: np.ndarray         # (N,), per-step target q
    primes_used: list[int]        # the prime sequence


def synthesize_weights(
    primes: Sequence[int],
    dim: int,
    *,
    op_norm_T: float = 1.0,
    q_star: float = 0.9,
    profile: WeightProfile = "log_decay",
    epsilon: float = 0.05,
) -> WeightSchedule: ...


def validate_schedule(
    schedule: WeightSchedule,
    op_norm_T: float,
) -> tuple[bool, float]:
    """Check that every q_k <= q* and return (valid, max_q)."""
    ...
```

### Implementation Notes

- `synthesize_weights` returns diagonal `(d, d)` matrices. For non-diagonal initialization (needed by advanced users), accept an optional `basis: np.ndarray` parameter and multiply `Xi_k = alpha_k * q* / denom * basis`.
- `validate_schedule` is a pure verification pass — no mutation. It recomputes \( q_k \) from the matrices and checks against the schedule's `q_targets`.
- Add `WeightSchedule` to `types.py` if the dataclass needs to be importable standalone.
- The module imports only `numpy` and `math`. No `sympy` needed — primes are passed in, not generated.

### Acceptance Criteria

- `synthesize_weights([2,3,5,7,11], dim=4)` returns a `WeightSchedule` with 5 entries
- Every `Xi_seq[k]` is `(4,4)`, every `Lam_seq[k]` is `(4,4)`
- `validate_schedule(schedule, op_norm_T=1.0)` returns `(True, max_q)` with `max_q <= 0.9`
- `profile="uniform"` produces equal `alpha` across all steps
- Custom callable profile works: `synthesize_weights(primes, 4, profile=lambda k, p: 0.3)`
- `WeightSchedule` round-trips through `pickle`

### File: `src/pirtm/weights.py` — ~100 LOC

***

## Issue #6: Add `gain.py` — Gain Builder and Norm Estimator

### Problem Statement

The `step()` function in `recurrence.py` requires a `G_t` (gain/disturbance) array at each step and an `op_norm_T` scalar. Currently these are user-supplied magic numbers. The package needs a module that:

1. **Estimates** \( \|T\|_{op} \) from a callable operator `T` via power iteration.
2. **Constructs** gain sequences \( \{G_t\} \) from common patterns: constant, decaying, random bounded.
3. **Validates** gain norms against the ISS bound from `certify.py`.

### Mathematical Specification

**Operator norm estimation** via power iteration:

\[
\|T\|_{op} = \lim_{k \to \infty} \frac{\|T(v_k)\|}{\|v_k\|}, \quad v_{k+1} = \frac{T(v_k)}{\|T(v_k)\|}
\]

Converges geometrically for operators with a spectral gap. The implementation runs for `max_iter` steps or until \( \Delta < \text{tol} \).

**Gain sequence patterns**:

- `"constant"`: \( G_t = g \cdot u \) for a fixed direction \( u \) and scalar \( g \)
- `"decay"`: \( G_t = g \cdot (1 + t)^{-\beta} \cdot u \)
- `"random"`: \( G_t \sim \mathcal{U}[-g, g]^{d} \) with \( \|G_t\| \leq g \) enforced by clipping
- `"zero"`: \( G_t = 0 \) (autonomous system)

**ISS compatibility check**: Given a gain sequence and a `StepInfo` trace, verify:

\[
\|G_t\| \leq (1 - q_{\max}) \cdot r_{\text{target}}
\]

where \( r_{\text{target}} \) is the user's desired fixed-point radius.

### Proposed API

```python
GainProfile = Literal["constant", "decay", "random", "zero"] | Callable[[int], np.ndarray]


def estimate_operator_norm(
    T: Callable[[np.ndarray], np.ndarray],
    dim: int,
    *,
    max_iter: int = 200,
    tol: float = 1e-10,
    seed: int | None = None,
) -> tuple[float, int]:
    """Return (estimated_norm, iterations_used)."""
    ...


def build_gain_sequence(
    length: int,
    dim: int,
    *,
    scale: float = 0.01,
    profile: GainProfile = "decay",
    decay_rate: float = 1.0,
    seed: int | None = None,
) -> list[np.ndarray]:
    """Return a list of G_t arrays."""
    ...


def check_iss_compatibility(
    gains: Sequence[np.ndarray],
    infos: Sequence[StepInfo],
    target_radius: float,
) -> tuple[bool, float]:
    """Return (compatible, max_gain_norm). compatible=True iff ISS constraint met."""
    ...
```

### Implementation Notes

- `estimate_operator_norm` uses a deterministic seed by default (`seed=42`) for reproducibility. The initial vector is drawn from `np.random.default_rng(seed).standard_normal(dim)`.
- Power iteration returns both the estimated norm and the iteration count for diagnostic purposes.
- `build_gain_sequence` with `profile="random"` clips each vector: if \( \|G_t\| > \text{scale} \), rescale to `scale`.
- `check_iss_compatibility` reads `info.q` from each `StepInfo` to extract \( q_{\max} \), then compares against `iss_bound()` from `certify.py`.
- The module imports `numpy` and `pirtm.types`. The `check_iss_compatibility` function calls `iss_bound` from `pirtm.certify` — this is an intra-package dependency, not external.

### Acceptance Criteria

- `estimate_operator_norm(lambda x: 2*x, dim=4)` returns `(~2.0, k)` within `tol`
- `estimate_operator_norm(lambda x: A @ x, dim=4)` matches `np.linalg.norm(A, 2)` to 4 decimal places
- `build_gain_sequence(50, 4, profile="decay")` returns 50 arrays each of shape `(4,)`
- `build_gain_sequence(50, 4, profile="zero")` returns all-zero arrays
- `build_gain_sequence(50, 4, profile="random", seed=42)` is deterministic across runs
- `check_iss_compatibility(gains, infos, target_radius=1.0)` returns `(True, max_norm)` when gains are small enough

### File: `src/pirtm/gain.py` — ~130 LOC

***

## Issue #7: Add `csc.py` — Contractive Sufficient Condition Solver

### Problem Statement

The contractive core guarantees convergence when \( q_t < 1 - \epsilon \) at every step. But there is no module that, given a problem setup (operator norm, dimension, desired accuracy), solves for the **maximum allowable parameter norms** that satisfy the contractive sufficient condition (CSC). This is the synthesis/verification complement to the runtime check in `step()`.

### Mathematical Specification

**CSC** (Contractive Sufficient Condition):

\[
\|\Xi\| + \|\Lambda\| \cdot \|T\|_{op} \leq 1 - \epsilon
\]

Given \( \|T\|_{op} \), \( \epsilon \), and a split ratio \( \alpha \in [0, 1] \):

\[
\|\Xi\|_{\max} = \alpha \cdot (1 - \epsilon)
\]

\[
\|\Lambda\|_{\max} = \frac{(1 - \alpha) \cdot (1 - \epsilon)}{\|T\|_{op}}
\]

**Margin analysis**: Given actual norms \( (\|\Xi\|, \|\Lambda\|) \):

\[
\text{margin} = (1 - \epsilon) - (\|\Xi\| + \|\Lambda\| \cdot \|T\|_{op})
\]

**Sensitivity**: How much can \( \|T\|_{op} \) grow before CSC is violated:

\[
\|T\|_{op,\max} = \frac{(1 - \epsilon) - \|\Xi\|}{\|\Lambda\|}
\]

**Multi-step CSC**: Over a sequence \( \{(\Xi_t, \Lambda_t)\}_{t=0}^{N-1} \), the worst-case margin:

\[
\text{margin}_{\min} = \min_{t} \left[ (1 - \epsilon_t) - q_t \right]
\]

### Proposed Types (add to `types.py`)

```python
@dataclass(slots=True)
class CSCBudget:
    """Parameter budget satisfying the contractive sufficient condition."""
    Xi_norm_max: float
    Lam_norm_max: float
    q_star: float
    epsilon: float
    op_norm_T: float
    alpha: float


@dataclass(slots=True)
class CSCMargin:
    """Margin analysis for a given parameter configuration."""
    margin: float
    q_actual: float
    q_target: float
    T_headroom: float       # how much ||T|| can grow
    epsilon_headroom: float  # how much epsilon can shrink
    safe: bool
```

### Proposed API

```python
def solve_budget(
    op_norm_T: float,
    *,
    epsilon: float = 0.05,
    alpha: float = 0.5,
) -> CSCBudget:
    """Compute maximum allowable norms for Xi and Lam."""
    ...


def compute_margin(
    Xi_norm: float,
    Lam_norm: float,
    op_norm_T: float,
    *,
    epsilon: float = 0.05,
) -> CSCMargin:
    """Analyze safety margin for a specific parameter configuration."""
    ...


def multi_step_margin(
    infos: Sequence[StepInfo],
) -> CSCMargin:
    """Worst-case margin over a trajectory."""
    ...


def sensitivity(
    Xi_norm: float,
    Lam_norm: float,
    *,
    epsilon: float = 0.05,
) -> dict[str, float]:
    """Return max allowable op_norm_T and min allowable epsilon."""
    ...
```

### Implementation Notes

- Pure arithmetic — no `numpy` needed for `solve_budget`, `compute_margin`, `sensitivity`. Only `multi_step_margin` reads `StepInfo` sequences.
- `compute_margin` is the runtime analog of what `step()` checks internally but returns a structured report instead of a boolean.
- `sensitivity` answers "how robust is this setup?" — critical for users designing systems where operator norms are uncertain.
- `multi_step_margin` wraps over the `StepInfo` trace and finds the step with minimum margin. It reads `info.q` and `info.epsilon`.

### Relationship to Existing Modules

| CSC function | Relates to |
|-------------|------------|
| `solve_budget()` | Feeds into `synthesize_weights()` from `weights.py` (Issue #5) — the budget defines `q_star` |
| `compute_margin()` | Structural analog of the check inside `step()` |
| `multi_step_margin()` | Same data as `ace_certificate()` in `certify.py` but returns `CSCMargin` instead of `Certificate` |
| `sensitivity()` | Complements `iss_bound()` from `certify.py` — different question, same parameters |

### Acceptance Criteria

- `solve_budget(op_norm_T=2.0, epsilon=0.05, alpha=0.6)` returns budget where `Xi_norm_max + Lam_norm_max * 2.0 == 0.95`
- `compute_margin(Xi_norm=0.3, Lam_norm=0.2, op_norm_T=2.0)` returns `margin = 0.95 - (0.3 + 0.4) = 0.25`
- `compute_margin` with `q_actual > q_target` returns `safe=False`
- `multi_step_margin(infos)` returns the step with minimum margin
- `sensitivity(Xi_norm=0.3, Lam_norm=0.2)` returns finite `T_max` and `epsilon_min`
- `sensitivity(Xi_norm=0.0, Lam_norm=0.0)` returns `T_max = inf`

### File: `src/pirtm/csc.py` — ~100 LOC

***

## Updated `__init__.py` Exports (Post Tier 2)

After all four modules land, `src/pirtm/__init__.py` adds these exports to the existing `__all__`:

```python
from .petc import PETCLedger, petc_invariants
from .weights import synthesize_weights, validate_schedule, WeightSchedule
from .gain import estimate_operator_norm, build_gain_sequence, check_iss_compatibility
from .csc import solve_budget, compute_margin, multi_step_margin, sensitivity, CSCBudget, CSCMargin

# Added to __all__:
#   "PETCLedger",
#   "WeightSchedule", "synthesize_weights", "validate_schedule",
#   "estimate_operator_norm", "build_gain_sequence", "check_iss_compatibility",
#   "CSCBudget", "CSCMargin", "solve_budget", "compute_margin",
#   "multi_step_margin", "sensitivity",
```

Updated `PETCEntry` and `PETCReport` (revised) plus `CSCBudget` and `CSCMargin` are added to `types.py`.

***

## Dependency Graph

```
types.py  ◄── recurrence.py ◄── gain.py (check_iss_compatibility uses StepInfo)
    ▲              ▲
    │              │
    ├── certify.py ◄── gain.py (calls iss_bound)
    │
    ├── projection.py ◄── recurrence.py
    │
    ├── petc.py (self-contained, only types.py)
    │
    ├── weights.py (only types.py + numpy)
    │
    └── csc.py (only types.py + StepInfo read)
```

**No circular imports.** Every new module depends only on `types.py` and optionally `certify.py`. The dependency direction is always toward the leaf types.

***

## Execution Sequence

Issues #4-#7 have **no inter-dependencies** — they can be worked in parallel on separate branches:

```
Tier 1 (#1 → #2 → #3) must land first
          │
          ▼
    ┌─────┼─────┬─────┐
    ▼     ▼     ▼     ▼
  #4    #5    #6    #7
 petc  weights gain  csc
    └─────┼─────┴─────┘
          ▼
   Update __init__.py + types.py (single follow-up PR)
```

### Estimated Effort

| Issue | File | LOC (approx) | Complexity | Time |
|-------|------|-------------|------------|------|
| #4 — PETC Ledger | `petc.py` | ~120 | Medium (chain logic, backward compat) | 2-3 hours |
| #5 — Weight Synthesizer | `weights.py` | ~100 | Low (arithmetic, diagonal matrices) | 1-2 hours |
| #6 — Gain Builder | `gain.py` | ~130 | Medium (power iteration, ISS link) | 2-3 hours |
| #7 — CSC Solver | `csc.py` | ~100 | Low (pure arithmetic) | 1-2 hours |
| Follow-up | `__init__.py`, `types.py` | ~30 | Low | 30 min |

Total: ~480 LOC of new code, 4 parallel PRs + 1 follow-up.

***

## Post-Tier 2 State

After merge, the package provides a complete pipeline:

```python
from pirtm import (
    # Tier 0 (existing)
    step, run, ace_certificate, iss_bound,
    project_parameters_soft, project_parameters_weighted_l1,
    fixed_point_estimate, AdaptiveMargin, Monitor,
    infinite_prime_check,
    # Tier 2 (new)
    PETCLedger, petc_invariants,
    synthesize_weights, validate_schedule,
    estimate_operator_norm, build_gain_sequence, check_iss_compatibility,
    solve_budget, compute_margin, multi_step_margin, sensitivity,
)

# Full workflow:
budget = solve_budget(op_norm_T=2.0, epsilon=0.05)
schedule = synthesize_weights(primes, dim=8, op_norm_T=2.0, q_star=budget.q_star)
assert validate_schedule(schedule, op_norm_T=2.0)
gains = build_gain_sequence(len(primes), dim=8, scale=0.01)
X_final, history, infos, status = run(X0, schedule.Xi_seq, schedule.Lam_seq, gains, T=T, P=P)
cert = ace_certificate(infos)
margin = multi_step_margin(infos)
```

No hand-crafted magic numbers. Every parameter is either computed from the spec or validated against the CSC. The DRMM repo and Lambda-Proof can now depend on `pirtm>=0.1.0` as a proper upstream.

---

## References

1. [Universal_Logic.pdf](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_66e2273e-f127-443b-91a5-5949929d769c/c49e3b4d-e834-455e-90db-6768f69fb312/Universal_Logic.pdf?AWSAccessKeyId=ASIA2F3EMEYE7CXCGMQL&Signature=OT17VyGXMh6ycr6XfXMGmFGhszc%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEG4aCXVzLWVhc3QtMSJHMEUCIBT44%2FPBh7q1Lvy7fzfeoFfj5%2F9T6f%2BQunYVi1rCzbUeAiEA5BGgmKQlGZ5zPnScnUDzJvjAVkX%2B72iyg2aTVWVbjjMq8wQINxABGgw2OTk3NTMzMDk3MDUiDHqxOFKmzTsp7LRyjSrQBB69UdUFxwBtq80qZXLxzaa9aV7rRJ%2Fo%2FJ2K0M3QJkgveMPbvRWoxijnRjrgV2hCGxONaf9ea3jtWZj6HiCbYBYmCgr6hQ3hXLMXJVPCxRqL2WJu1UOh8CE8fHqcAWPXTw5Shn9pthI3uVd9fH07enSvaQAG1eZm6NUl%2BHA30pRPHIfqqpHhaPrxFfEVuJ4vYiWiafC1FPM4yQg4BMrGTej2OyCMPGF49nVj4myRK3eTUvOIUZdxe1HKn%2BJiafEPSZNtvpbe817yeGmSio1NV59t9GFr2sxMAMZ2bcM8wUUDod2oRcg6gRT8QunGC9XQSxC8v8%2ByqzdaSGEU7%2F4LMHjPPJuRrxmTmgC%2FYmRUapa43fwXq18m5cuZ6iJ0aR9oTZgZ8lgZvCh9K3Dbq9VZJ8I9gtBDoZIHRJaGDiyxX6%2Bdla3sRXosPqDTUJsSNKdaNfdP9lYBvlitWB9amsqewG1MC6UM7NiQMPTNKOujVxsqGH%2FTAAQe9Bk2f5Z%2BmdwSpKw%2FK4l%2FkJMk%2FsAptn%2F6f5ABR1WUJ8oaSSxqDr1CPkCPKrAKB4sqxoEEag857i1OlKFkS7jz1mAENu4SaUidYrDU0eiEzbYtNkLnGd0QoUd%2FEXlO6ccwe%2FZ7LdTCgpWQByxqsIj4TZn9AjTnPFBPG1QmakhjEH8KD%2BBM6%2Fr2ItfunHmcyeaTF%2FkkmlOJ0OkyIlQpzxYOwpGb1pQNSryJKlqLQDc%2F4NOgHnksk%2FUppoQXJY8nBZWIxqIZjmWORj5RBqYH2IFekFHddSNP%2Fc%2BqeAEw%2Fd2EzQY6mAHTJ6QAQI9VFKIKES4oOaleYkoXBwNVeKSo%2BV0yD7tnOjmM3udyv2IW6qAt%2FLJgDsRjH409THtYMHqpZLYqFjTohZzL50%2Bg5bEdaeYUnJvSkleF1EvoZjRsZI1an%2FHdh3zZYRkJEXD8C%2B%2F7VlqU5%2FIqTXKJvZW2KCvTnev76KmCpTGQ0yHq%2F56RacjvDUpwW0uBhsgxVKWa9g%3D%3D&Expires=1772175509)

2. [Arithmetic_Control_Engine.pdf](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_66e2273e-f127-443b-91a5-5949929d769c/6087b4f7-2fd4-45d1-9361-dcd64931b78d/Arithmetic_Control_Engine.pdf?AWSAccessKeyId=ASIA2F3EMEYE7CXCGMQL&Signature=24hBW8y4P8MhBcR7Ku0W48ASXjk%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEG4aCXVzLWVhc3QtMSJHMEUCIBT44%2FPBh7q1Lvy7fzfeoFfj5%2F9T6f%2BQunYVi1rCzbUeAiEA5BGgmKQlGZ5zPnScnUDzJvjAVkX%2B72iyg2aTVWVbjjMq8wQINxABGgw2OTk3NTMzMDk3MDUiDHqxOFKmzTsp7LRyjSrQBB69UdUFxwBtq80qZXLxzaa9aV7rRJ%2Fo%2FJ2K0M3QJkgveMPbvRWoxijnRjrgV2hCGxONaf9ea3jtWZj6HiCbYBYmCgr6hQ3hXLMXJVPCxRqL2WJu1UOh8CE8fHqcAWPXTw5Shn9pthI3uVd9fH07enSvaQAG1eZm6NUl%2BHA30pRPHIfqqpHhaPrxFfEVuJ4vYiWiafC1FPM4yQg4BMrGTej2OyCMPGF49nVj4myRK3eTUvOIUZdxe1HKn%2BJiafEPSZNtvpbe817yeGmSio1NV59t9GFr2sxMAMZ2bcM8wUUDod2oRcg6gRT8QunGC9XQSxC8v8%2ByqzdaSGEU7%2F4LMHjPPJuRrxmTmgC%2FYmRUapa43fwXq18m5cuZ6iJ0aR9oTZgZ8lgZvCh9K3Dbq9VZJ8I9gtBDoZIHRJaGDiyxX6%2Bdla3sRXosPqDTUJsSNKdaNfdP9lYBvlitWB9amsqewG1MC6UM7NiQMPTNKOujVxsqGH%2FTAAQe9Bk2f5Z%2BmdwSpKw%2FK4l%2FkJMk%2FsAptn%2F6f5ABR1WUJ8oaSSxqDr1CPkCPKrAKB4sqxoEEag857i1OlKFkS7jz1mAENu4SaUidYrDU0eiEzbYtNkLnGd0QoUd%2FEXlO6ccwe%2FZ7LdTCgpWQByxqsIj4TZn9AjTnPFBPG1QmakhjEH8KD%2BBM6%2Fr2ItfunHmcyeaTF%2FkkmlOJ0OkyIlQpzxYOwpGb1pQNSryJKlqLQDc%2F4NOgHnksk%2FUppoQXJY8nBZWIxqIZjmWORj5RBqYH2IFekFHddSNP%2Fc%2BqeAEw%2Fd2EzQY6mAHTJ6QAQI9VFKIKES4oOaleYkoXBwNVeKSo%2BV0yD7tnOjmM3udyv2IW6qAt%2FLJgDsRjH409THtYMHqpZLYqFjTohZzL50%2Bg5bEdaeYUnJvSkleF1EvoZjRsZI1an%2FHdh3zZYRkJEXD8C%2B%2F7VlqU5%2FIqTXKJvZW2KCvTnev76KmCpTGQ0yHq%2F56RacjvDUpwW0uBhsgxVKWa9g%3D%3D&Expires=1772175509)

