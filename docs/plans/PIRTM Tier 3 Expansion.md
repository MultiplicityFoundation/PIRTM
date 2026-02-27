# PIRTM Tier 3: Test Suite for the Contractive Core — Expanded Specification

## Current Test State

The repository contains three legacy test files under `tests/`. All three test the **legacy** modules (`pir_tensor.py`, `recursive_ops.py`, `spectral_decomp.py`) via bare imports that break outside the source directory. After Tier 1, these will be rewired to `pirtm._legacy` and will continue to run under CI.

**Zero tests exist for the 10 spec-aligned core modules.** The entire contractive core — `recurrence.py`, `projection.py`, `certify.py`, `adaptive.py`, `fixed_point.py`, `monitor.py`, `petc.py`, `infinite_prime.py` — plus the four Tier 2 modules (`petc.py` rewrite, `weights.py`, `gain.py`, `csc.py`) are untested. This tier closes that gap.

***

## Test Architecture

### Directory Layout (Post Tier 3)

```
tests/
├── conftest.py                      # Shared fixtures
├── test_primes.py                   # Legacy (rewired in Tier 1)
├── test_spectral.py                 # Legacy (rewired in Tier 1)
├── test_tensor_dynamics.py          # Legacy (rewired in Tier 1)
├── test_types.py                    # NEW — dataclass contracts
├── test_recurrence.py               # NEW — step() and run()
├── test_projection.py               # NEW — soft + weighted-l1
├── test_certify.py                  # NEW — ace_certificate + iss_bound
├── test_adaptive.py                 # NEW — AdaptiveMargin
├── test_fixed_point.py              # NEW — fixed_point_estimate
├── test_monitor.py                  # NEW — Monitor
├── test_petc.py                     # NEW — PETCLedger + petc_invariants
├── test_infinite_prime.py           # NEW — infinite_prime_check
├── test_weights.py                  # NEW — synthesize_weights (Tier 2)
├── test_gain.py                     # NEW — gain builder (Tier 2)
├── test_csc.py                      # NEW — CSC solver (Tier 2)
└── test_integration.py              # NEW — end-to-end pipeline
```

13 new test files. Target: **~150 test functions**, 95%+ line coverage on all spec-aligned modules.

### Shared Fixtures (`conftest.py`)

```python
import numpy as np
import pytest
from pirtm.types import StepInfo, Status

@pytest.fixture
def rng():
    """Deterministic RNG for reproducible tests."""
    return np.random.default_rng(42)

@pytest.fixture
def dim():
    return 4

@pytest.fixture
def identity(dim):
    return np.eye(dim)

@pytest.fixture
def zero_matrix(dim):
    return np.zeros((dim, dim))

@pytest.fixture
def small_matrix(rng, dim):
    """A small-norm random matrix (||M|| < 0.3)."""
    M = rng.standard_normal((dim, dim))
    return M * 0.3 / np.linalg.norm(M, 2)

@pytest.fixture
def identity_operator():
    """T = identity (||T|| = 1)."""
    def T(x): return x
    return T

@pytest.fixture
def scaling_operator():
    """T = 0.5 * I (||T|| = 0.5)."""
    def T(x): return 0.5 * x
    return T

@pytest.fixture
def identity_projector():
    """P = identity (no projection)."""
    def P(x): return x
    return P

@pytest.fixture
def safe_step_info():
    """A StepInfo where q < 1 - epsilon."""
    return StepInfo(step=0, q=0.7, epsilon=0.05, nXi=0.4,
                    nLam=0.3, projected=False, residual=0.001)

@pytest.fixture
def unsafe_step_info():
    """A StepInfo where q > 1 - epsilon."""
    return StepInfo(step=0, q=0.98, epsilon=0.05, nXi=0.6,
                    nLam=0.38, projected=True, residual=0.5)

@pytest.fixture
def converged_status():
    return Status(converged=True, safe=True, steps=50,
                  residual=1e-8, epsilon=0.05)

@pytest.fixture
def small_primes():
    return [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
```

***

## Issue #8: `test_types.py` — Dataclass Contracts

### What It Tests

The `types.py` module defines 5 dataclasses with `slots=True`. Tests verify construction, field access, immutability expectations, and default values.

### Test Functions (7 tests)

| Test | Covers | Key Assertion |
|------|--------|---------------|
| `test_step_info_construction` | `StepInfo` fields | All 7 required fields set correctly |
| `test_step_info_optional_note` | `note` default | `note is None` when omitted |
| `test_status_construction` | `Status` fields | `converged`, `safe`, `steps`, `residual`, `epsilon` |
| `test_certificate_defaults` | `Certificate.details` | `details` defaults to empty dict |
| `test_petc_report_construction` | `PETCReport` fields | `satisfied`, `violations`, `primes_checked` |
| `test_monitor_record_construction` | `MonitorRecord` fields | Nests `StepInfo` and optional `Status` |
| `test_slots_enforced` | `slots=True` | `hasattr(obj, '__dict__') is False` for all types |

### Branch Coverage Target

100%. These are pure dataclasses with no logic beyond `__post_init__` (none have one).

***

## Issue #9: `test_recurrence.py` — Step and Run

### What It Tests

`step()` performs one contractive iteration with automatic safety projection. `run()` loops `step()` until convergence or exhaustion. This is the mathematical heart of the package.

### Code Branches in `recurrence.py`

| Branch | Location | Trigger |
|--------|----------|---------|
| `A.size == 0` | `_operator_norm` | Empty array input |
| `callable(P)` | `_apply_projector` | P is a function |
| `hasattr(P, 'apply')` | `_apply_projector` | P is an object with `.apply()` |
| `TypeError` raise | `_apply_projector` | P is neither callable nor has `.apply` |
| `q_t > target` | `step()` | Parameters exceed contraction budget → triggers projection |
| `q_t <= target` | `step()` | Parameters within budget → no projection |
| `residual < tol` | `run()` | Early convergence exit |
| `max_steps` truncation | `run()` | `max_steps < len(sequences)` |
| Empty sequences | `run()` | Zero-length input → `infos` is empty, `residual = inf` |

### Test Functions (15 tests)

| Test | Branch | Key Assertion |
|------|--------|---------------|
| `test_step_preserves_shape` | Normal path | `X_next.shape == X_t.shape` |
| `test_step_identity_projector` | `callable(P)` | `X_next = Xi @ X + Lam @ T(X) + G` exactly |
| `test_step_object_projector` | `hasattr(P, 'apply')` | Class with `.apply()` method works |
| `test_step_invalid_projector` | `TypeError` | `pytest.raises(TypeError)` for `P=42` |
| `test_step_no_projection_when_safe` | `q <= target` | `info.projected is False`, `info.q < 0.95` |
| `test_step_triggers_projection` | `q > target` | `info.projected is True`, `info.q <= target` post-projection |
| `test_step_residual_computation` | All | `info.residual == norm(X_next - X_t)` |
| `test_step_zero_gain` | Normal | `G_t = 0` ⟹ pure linear iteration |
| `test_step_operator_norm_zero` | `A.size == 0` | Edge: empty array returns 0.0 |
| `test_run_converges_identity` | `residual < tol` | `status.converged is True` after N steps |
| `test_run_max_steps_truncation` | `max_steps` | `status.steps == max_steps` |
| `test_run_safe_flag_true` | `q <= target` all steps | `status.safe is True` |
| `test_run_safe_flag_false` | `q > target` at some step | `status.safe is False` |
| `test_run_history_length` | Normal | `len(history) == status.steps + 1` |
| `test_run_empty_sequences` | Zero-length | `status.steps == 0`, `status.residual == inf` |

### Parametric Dimensions

Use `@pytest.mark.parametrize("dim", [2, 4, 8])` on shape-sensitive tests to catch dimension-dependent bugs.

### Property: Contraction Invariant

The key mathematical property: if `info.projected is False` and `info.q < 1 - epsilon`, then `info.residual` must be strictly less than the previous step's residual (monotone decrease) **when** the system is within the contraction basin. Test this over a 50-step `run()` with known-contractive parameters.

***

## Issue #10: `test_projection.py` — Soft and Weighted-L1

### What It Tests

Two projection functions: `project_parameters_soft()` (simple scaling) and `project_parameters_weighted_l1()` (threshold search + binary refinement).

### Code Branches in `projection.py`

| Branch | Location | Trigger |
|--------|----------|---------|
| `budget <= target` | `project_parameters_soft` | Already within budget → return copies |
| `budget == 0.0` | `project_parameters_soft` | Zero matrices → return copies |
| `budget > target` | `project_parameters_soft` | Rescale |
| `values.shape != weights.shape` | `weighted_l1` | Shape mismatch → `ValueError` |
| `weights < 0` | `weighted_l1` | Negative weights → `ValueError` |
| `budget < 0` | `weighted_l1` | Negative budget → `ValueError` |
| `weighted_norm <= budget` | `weighted_l1` | Already feasible → return copy, tau=0 |
| `not any(weights > 0)` | `weighted_l1` | All-zero weights → vacuous constraint |
| `tau` threshold loop | `weighted_l1` | Multiple iterations of breakpoint search |
| Binary refinement loop | `weighted_l1` | 50-iteration bisection to tighten tau |

### Test Functions (14 tests)

| Test | Branch | Key Assertion |
|------|--------|---------------|
| `test_soft_no_projection_needed` | `budget <= target` | Output equals input (copy) |
| `test_soft_zero_matrices` | `budget == 0` | Returns zero copies |
| `test_soft_rescales_correctly` | `budget > target` | `||Xi_out|| + ||Lam_out|| * ||T|| <= target` |
| `test_soft_preserves_direction` | `budget > target` | `Xi_out / ||Xi_out|| ≈ Xi / ||Xi||` |
| `test_soft_returns_copies` | All | `Xi_out is not Xi` (new allocation) |
| `test_wl1_shape_mismatch` | Shape error | `pytest.raises(ValueError)` |
| `test_wl1_negative_weights` | Weight error | `pytest.raises(ValueError)` |
| `test_wl1_negative_budget` | Budget error | `pytest.raises(ValueError)` |
| `test_wl1_already_feasible` | `norm <= budget` | `tau == 0.0`, output equals input |
| `test_wl1_all_zero_weights` | Degenerate | Returns input unchanged |
| `test_wl1_projects_onto_ball` | Threshold + refinement | `sum(w * |proj|) <= budget + tol` |
| `test_wl1_preserves_signs` | All | `sign(proj[i]) == sign(values[i])` or `proj[i] == 0` |
| `test_wl1_uniform_weights` | Symmetric case | Equivalent to standard soft-threshold |
| `test_wl1_sparse_output` | Large tau | Some entries driven to zero |

### Property: Feasibility

For every test that calls `project_parameters_weighted_l1`, assert the post-condition:

```python
assert np.sum(weights * np.abs(projected)) <= budget + tol
```

This is the mathematical contract of the projection.

***

## Issue #11: `test_certify.py` — ACE Certificate and ISS Bound

### What It Tests

`ace_certificate()` builds a `Certificate` from step telemetry. `iss_bound()` computes the input-to-state stability bound. Both have edge cases around `max_q >= 1.0` and empty input.

### Code Branches

| Branch | Location | Trigger |
|--------|----------|---------|
| `isinstance(info, StepInfo)` | `_ensure_sequence` | Single StepInfo input |
| `list(info)` | `_ensure_sequence` | Sequence input |
| `not records` | Both functions | Empty list → `ValueError` |
| `margin >= 0` | `ace_certificate` | Certified |
| `margin < 0` | `ace_certificate` | Not certified |
| `max_q >= 1.0` | `ace_certificate` | `tail_bound = inf` |
| `max_q < 1.0` | `ace_certificate` | Finite tail bound |
| `max_q >= 1.0` | `iss_bound` | Returns `inf` |
| `max_q < 1.0` | `iss_bound` | Returns `d / (1 - max_q)` |

### Test Functions (12 tests)

| Test | Branch | Key Assertion |
|------|--------|---------------|
| `test_ace_single_step_certified` | Single, margin >= 0 | `cert.certified is True` |
| `test_ace_single_step_not_certified` | Single, margin < 0 | `cert.certified is False` |
| `test_ace_sequence_certified` | Sequence, margin >= 0 | `cert.margin > 0` |
| `test_ace_sequence_mixed_epsilon` | Varying eps | `target = 1 - min(eps)` |
| `test_ace_empty_raises` | Empty | `pytest.raises(ValueError)` |
| `test_ace_max_q_above_one` | `max_q >= 1` | `cert.tail_bound == inf` |
| `test_ace_tail_bound_finite` | `max_q < 1` | `cert.tail_bound == tail_norm / (1 - max_q)` |
| `test_ace_details_dict` | All | `cert.details` contains `max_q`, `target`, `steps` |
| `test_iss_bound_basic` | `max_q < 1` | `result == disturbance / (1 - max_q)` |
| `test_iss_bound_unstable` | `max_q >= 1` | `result == inf` |
| `test_iss_bound_empty_raises` | Empty | `pytest.raises(ValueError)` |
| `test_iss_bound_zero_disturbance` | `d = 0` | `result == 0.0` |

### Property: Margin Arithmetic

For every `ace_certificate` call, verify:
```python
assert cert.margin == approx(cert.details["target"] - cert.details["max_q"])
```

This is the core identity of the certificate.

***

## Issue #12: `test_adaptive.py` — Adaptive Margin Controller

### What It Tests

`AdaptiveMargin` adjusts epsilon based on whether the system is violating, safe-with-room, or in the neutral zone. Three update paths exist.

### Code Branches

| Branch | Location | Trigger |
|--------|----------|---------|
| `baseline is None` | `__post_init__` | Default: baseline = epsilon |
| `q > target` | `update()` | Epsilon increases |
| `residual < target AND margin > 0.05` | `update()` | Epsilon decreases |
| Neither condition | `update()` | Epsilon unchanged |
| `min_epsilon` clamp | `update()` | Decrease hits floor |
| `max_epsilon` clamp | `update()` | Increase hits ceiling |

### Test Functions (10 tests)

| Test | Branch | Key Assertion |
|------|--------|---------------|
| `test_default_baseline` | `__post_init__` | `am.baseline == am.epsilon` |
| `test_custom_baseline` | `__post_init__` | `am.baseline == custom_value` |
| `test_increase_on_violation` | `q > target` | `epsilon_new > epsilon_old` |
| `test_decrease_on_convergence` | Low residual, large margin | `epsilon_new < epsilon_old` |
| `test_no_change_neutral` | Neither branch | `epsilon_new == epsilon_old` |
| `test_clamp_max` | Repeated violations | `am.epsilon <= am.max_epsilon` |
| `test_clamp_min` | Repeated convergence | `am.epsilon >= am.min_epsilon` |
| `test_clamp_baseline` | Decrease below baseline | `am.epsilon >= am.baseline` |
| `test_step_size_effect` | Large step_size | Epsilon jumps by `step_size` per call |
| `test_multi_step_trajectory` | 20 updates | Epsilon stays in `[min, max]` throughout |

***

## Issue #13: `test_fixed_point.py` — Fixed-Point Estimator

### What It Tests

`fixed_point_estimate()` averages the last `window` iterates and reports maximum deviation.

### Code Branches

| Branch | Location | Trigger |
|--------|----------|---------|
| `not history` | Guard | Empty list → `ValueError` |
| `window > len(history)` | Clamp | Window clamped to history length |
| `window == 1` | Clamp | Single-element average |
| Normal | Core | `window <= len(history)` |

### Test Functions (8 tests)

| Test | Branch | Key Assertion |
|------|--------|---------------|
| `test_empty_raises` | Guard | `pytest.raises(ValueError)` |
| `test_single_element` | window=1 or history=1 | `estimate == history[-1]`, `tail_bound == 0` |
| `test_constant_history` | Normal | `estimate == constant`, `tail_bound == 0` |
| `test_window_clamp` | `window > len` | No error, uses full history |
| `test_window_respects_size` | `window < len` | Only last `window` entries used |
| `test_tail_bound_nonzero` | Varying history | `tail_bound > 0` |
| `test_estimate_shape` | Normal | `estimate.shape == history.shape` |
| `test_convergent_sequence` | Decreasing residuals | `tail_bound` decreases as convergence tightens |

***

## Issue #14: `test_monitor.py` — Rolling Monitor

### What It Tests

`Monitor` is a bounded deque that stores `MonitorRecord` entries and computes summaries.

### Code Branches

| Branch | Location | Trigger |
|--------|----------|---------|
| `not self.records` | `summary()` | Empty monitor → default dict |
| `not self.records` | `last()` | Empty → returns `None` |
| Normal `push` | `push()` | Creates and appends `MonitorRecord` |
| Overflow | `push()` past `maxlen` | Oldest record evicted |
| `status and status.converged` | `summary()` | Converged check on last record |

### Test Functions (9 tests)

| Test | Branch | Key Assertion |
|------|--------|---------------|
| `test_empty_summary` | Empty | `{"steps": 0, "max_q": 0.0, "converged": False}` |
| `test_empty_last` | Empty | `last() is None` |
| `test_push_returns_record` | Normal | `isinstance(result, MonitorRecord)` |
| `test_push_increments_length` | Normal | `len(list(monitor)) == N` after N pushes |
| `test_summary_max_q` | Normal | `summary()["max_q"] == max(q values)` |
| `test_summary_converged_true` | Last has converged status | `summary()["converged"] is True` |
| `test_summary_converged_false` | No status / not converged | `summary()["converged"] is False` |
| `test_maxlen_eviction` | Overflow | `len(records) <= maxlen` after many pushes |
| `test_iteration` | `__iter__` | `list(monitor)` returns all records in order |

***

## Issue #15: `test_petc.py` — PETC Ledger and Legacy Shim

### What It Tests

The rewritten `petc.py` (Tier 2, Issue #4) — both the new `PETCLedger` class and the backward-compatible `petc_invariants()` function. Also validates the existing stub behavior is preserved.

### Test Functions (12 tests)

| Test | Target | Key Assertion |
|------|--------|---------------|
| `test_ledger_append_valid` | `PETCLedger.append` | Entry created with correct prime |
| `test_ledger_append_nonprime_raises` | `PETCLedger.append` | `ValueError` on composite |
| `test_ledger_validate_satisfied` | `PETCLedger.validate` | `report.satisfied is True` for clean chain |
| `test_ledger_validate_gap_violation` | Gap detection | `report.gap_violations` is non-empty |
| `test_ledger_validate_monotonic` | Monotonicity | `report.monotonic is True` for sorted input |
| `test_ledger_validate_non_monotonic` | Monotonicity | `report.monotonic is False` for unsorted |
| `test_ledger_coverage_full` | `coverage(2, 47)` | Returns 1.0 when all primes present |
| `test_ledger_coverage_partial` | `coverage(2, 100)` | Returns < 1.0 when primes missing |
| `test_ledger_len_and_iter` | `__len__`, `__iter__` | `len(ledger) == N`, iteration yields entries |
| `test_legacy_shim_satisfied` | `petc_invariants` | Backward compat: `satisfied=True` |
| `test_legacy_shim_mass_violation` | `petc_invariants` | Backward compat: raises `ValueError` |
| `test_legacy_shim_min_length` | `petc_invariants` | `satisfied=False` when `len < min_length` |

***

## Issue #16: `test_infinite_prime.py` — Coverage Diagnostic

### What It Tests

`infinite_prime_check()` computes density, gaps, and support from a prime set.

### Test Functions (7 tests)

| Test | Branch | Key Assertion |
|------|--------|---------------|
| `test_empty_input` | No primes | `result["ok"] is False`, `reason == "no primes"` |
| `test_single_prime` | One element | `density > 0`, `largest_gap == 0` |
| `test_dense_primes_ok` | Dense set | `result["ok"] is True` |
| `test_sparse_primes_not_ok` | Sparse set, low density | `result["ok"] is False` |
| `test_custom_min_density` | `min_density=0.5` | Raises threshold |
| `test_deduplication` | Duplicate primes | `count` equals unique count |
| `test_non_primes_filtered` | Input `[1, 4, 6]` | Filtered out, treated as empty |

***

## Issue #17: `test_weights.py` — Weight Synthesizer (Tier 2)

### What It Tests

`synthesize_weights()` and `validate_schedule()` from the Tier 2 `weights.py` module.

### Test Functions (9 tests)

| Test | Target | Key Assertion |
|------|--------|---------------|
| `test_synthesize_shapes` | `synthesize_weights` | Each Xi, Lam is `(dim, dim)` |
| `test_synthesize_length` | `synthesize_weights` | `len(schedule.Xi_seq) == len(primes)` |
| `test_validate_passes` | `validate_schedule` | `(True, max_q)` with `max_q <= q_star` |
| `test_validate_fails_inflated` | `validate_schedule` | Manually inflate → `(False, _)` |
| `test_uniform_profile` | `profile="uniform"` | All alphas equal |
| `test_log_decay_profile` | `profile="log_decay"` | Alpha decreases with larger primes |
| `test_harmonic_profile` | `profile="harmonic"` | Alpha = 1/k |
| `test_custom_callable` | `profile=lambda k,p: 0.3` | Custom alpha works |
| `test_contraction_guarantee` | All profiles | `||Xi_k|| + ||Lam_k|| * ||T|| <= q_star` for all k |

### Property: CSC Satisfaction

Every schedule produced by `synthesize_weights` must satisfy the contractive sufficient condition. This is verified numerically across all entries:

\[
\|\Xi_k\|_2 + \|\Lambda_k\|_2 \cdot \|T\|_{op} \leq q^*
\]

***

## Issue #18: `test_gain.py` — Gain Builder (Tier 2)

### What It Tests

`estimate_operator_norm()`, `build_gain_sequence()`, and `check_iss_compatibility()` from Tier 2 `gain.py`.

### Test Functions (10 tests)

| Test | Target | Key Assertion |
|------|--------|---------------|
| `test_norm_identity` | `estimate_operator_norm` | Returns `~1.0` for identity |
| `test_norm_scaling` | `estimate_operator_norm` | Returns `~2.0` for `2*I` |
| `test_norm_matches_linalg` | `estimate_operator_norm` | Agrees with `np.linalg.norm(A, 2)` to 4 decimals |
| `test_norm_returns_iterations` | `estimate_operator_norm` | `iters > 0` |
| `test_gain_constant_shape` | `build_gain_sequence` | Each `G_t` has shape `(dim,)` |
| `test_gain_decay_decreasing` | `profile="decay"` | `||G_t||` decreasing over t |
| `test_gain_random_bounded` | `profile="random"` | `||G_t|| <= scale` for all t |
| `test_gain_zero_all_zero` | `profile="zero"` | Every `G_t == 0` |
| `test_gain_deterministic` | `seed=42` | Two calls yield identical sequences |
| `test_iss_compat_check` | `check_iss_compatibility` | Returns `(True, max_norm)` for small gains |

***

## Issue #19: `test_csc.py` — CSC Solver (Tier 2)

### What It Tests

`solve_budget()`, `compute_margin()`, `multi_step_margin()`, and `sensitivity()` from Tier 2 `csc.py`.

### Test Functions (10 tests)

| Test | Target | Key Assertion |
|------|--------|---------------|
| `test_solve_budget_identity` | `solve_budget` | `Xi_max + Lam_max * T == 1 - eps` |
| `test_solve_budget_alpha_split` | `solve_budget` | `Xi_max / (1-eps) == alpha` |
| `test_margin_positive` | `compute_margin` | `margin > 0` for safe params |
| `test_margin_negative` | `compute_margin` | `margin < 0`, `safe is False` |
| `test_margin_exact_boundary` | `compute_margin` | `margin == 0`, `safe is True` |
| `test_multi_step_finds_worst` | `multi_step_margin` | `margin == min over all steps` |
| `test_sensitivity_finite` | `sensitivity` | `T_max > op_norm_T`, `eps_min < eps` |
| `test_sensitivity_zero_lam` | `sensitivity` | `T_max == inf` |
| `test_sensitivity_zero_all` | `sensitivity` | Both headrooms infinite |
| `test_csc_roundtrip_with_weights` | Integration | `solve_budget` → `synthesize_weights` → `validate_schedule` passes |

***

## Issue #20: `test_integration.py` — End-to-End Pipeline

### What It Tests

The full pipeline exercised together: CSC budget → weight synthesis → gain construction → `run()` → certificate → fixed-point estimate → monitor → PETC ledger.

### Test Functions (5 tests)

| Test | Scenario | Key Assertion |
|------|----------|---------------|
| `test_full_pipeline_converges` | Standard 4D system | `status.converged`, `cert.certified`, `margin.safe` |
| `test_full_pipeline_with_adaptive` | Adaptive epsilon | `AdaptiveMargin` adjusts epsilon without crash |
| `test_full_pipeline_high_gain` | Large disturbance | `cert.certified is False`, `iss_bound > target_radius` |
| `test_full_pipeline_petc_chain` | Record primes per step | `ledger.validate().satisfied is True` |
| `test_full_pipeline_deterministic` | `seed=42` everywhere | Two runs yield bitwise identical results |

### Pipeline Template

```python
def test_full_pipeline_converges(small_primes, dim, identity_projector):
    from pirtm import (
        solve_budget, synthesize_weights, validate_schedule,
        build_gain_sequence, estimate_operator_norm,
        run, ace_certificate, fixed_point_estimate,
        multi_step_margin, Monitor, PETCLedger,
    )
    T = lambda x: 0.8 * x
    op_norm = estimate_operator_norm(T, dim, seed=42)
    budget = solve_budget(op_norm, epsilon=0.05)
    schedule = synthesize_weights(small_primes[:10], dim, op_norm_T=op_norm,
                                  q_star=budget.q_star)
    valid, max_q = validate_schedule(schedule, op_norm)
    assert valid

    gains = build_gain_sequence(10, dim, scale=0.001, profile="decay", seed=42)
    X0 = np.ones(dim)
    X_final, history, infos, status = run(
        X0, schedule.Xi_seq, schedule.Lam_seq, gains,
        T=T, P=identity_projector, epsilon=0.05, op_norm_T=op_norm,
    )
    assert status.converged or status.steps == 10
    cert = ace_certificate(infos)
    assert cert.certified
    margin = multi_step_margin(infos)
    assert margin.safe
    est, tail = fixed_point_estimate(history, window=3)
    assert tail < 1.0
```

***

## Coverage Targets

| Module | Target Coverage | Test File | Estimated Tests |
|--------|----------------|-----------|-----------------|
| `types.py` | 100% | `test_types.py` | 7 |
| `recurrence.py` | 95%+ | `test_recurrence.py` | 15 |
| `projection.py` | 95%+ | `test_projection.py` | 14 |
| `certify.py` | 100% | `test_certify.py` | 12 |
| `adaptive.py` | 100% | `test_adaptive.py` | 10 |
| `fixed_point.py` | 100% | `test_fixed_point.py` | 8 |
| `monitor.py` | 100% | `test_monitor.py` | 9 |
| `petc.py` | 95%+ | `test_petc.py` | 12 |
| `infinite_prime.py` | 100% | `test_infinite_prime.py` | 7 |
| `weights.py` | 95%+ | `test_weights.py` | 9 |
| `gain.py` | 95%+ | `test_gain.py` | 10 |
| `csc.py` | 95%+ | `test_csc.py` | 10 |
| Integration | N/A | `test_integration.py` | 5 |
| **Total** | | **13 files** | **~128 tests** |

The 95%+ targets account for defensive branches (e.g., the binary refinement loop in `weighted_l1` has a 50-iteration cap that may not fully exercise every early-exit path in a unit test).

***

## Execution Sequence

```
Tier 1 (layout, pyproject, CI) ──► Tier 2 (4 new modules) ──► Tier 3 (tests)
                                        │                          │
                                        │   ┌──────────────────────┘
                                        │   │
                                        ▼   ▼
                               Tests for existing modules can start
                               as soon as Tier 1 lands (Issues #8-#14, #16)
                               
                               Tests for Tier 2 modules (#15, #17-#19)
                               land after their respective module PRs merge
                               
                               Integration test (#20) lands last
```

### Parallelization

Issues #8 through #16 (tests for existing modules) are **fully parallel** — each is an independent test file with no cross-file dependencies. Issues #17-#19 (Tier 2 module tests) each depend only on their corresponding Tier 2 module PR. Issue #20 depends on all prior Tier 2 modules.

### Estimated Effort

| Issue | File | Tests | LOC (approx) | Time |
|-------|------|-------|-------------|------|
| #8 — types | `test_types.py` | 7 | ~60 | 30 min |
| #9 — recurrence | `test_recurrence.py` | 15 | ~200 | 2-3 hours |
| #10 — projection | `test_projection.py` | 14 | ~180 | 2-3 hours |
| #11 — certify | `test_certify.py` | 12 | ~130 | 1-2 hours |
| #12 — adaptive | `test_adaptive.py` | 10 | ~100 | 1 hour |
| #13 — fixed_point | `test_fixed_point.py` | 8 | ~80 | 45 min |
| #14 — monitor | `test_monitor.py` | 9 | ~90 | 45 min |
| #15 — petc | `test_petc.py` | 12 | ~140 | 1-2 hours |
| #16 — infinite_prime | `test_infinite_prime.py` | 7 | ~60 | 30 min |
| #17 — weights | `test_weights.py` | 9 | ~110 | 1 hour |
| #18 — gain | `test_gain.py` | 10 | ~120 | 1-2 hours |
| #19 — csc | `test_csc.py` | 10 | ~100 | 1 hour |
| #20 — integration | `test_integration.py` | 5 | ~120 | 1-2 hours |
| conftest | `conftest.py` | — | ~60 | 30 min |

**Total: ~1,550 LOC of tests, ~128 test functions, 13 PRs (parallelizable).**

***

## Post-Tier 3 State

After merge, `pytest --cov=pirtm --cov-report=term-missing -v` produces:

- **128+ passing tests** across 13 test files
- **95%+ line coverage** on every spec-aligned module
- **100% line coverage** on `types.py`, `certify.py`, `adaptive.py`, `fixed_point.py`, `monitor.py`, `infinite_prime.py`
- **CI enforced** — every PR must pass the full suite on Python 3.11, 3.12, 3.13

The contractive core becomes a **tested, certified, installable package** that downstream repos (DRMM, Lambda-Proof) can depend on with confidence.