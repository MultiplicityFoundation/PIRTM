# PIRTM Open-Source Core Completion Plan

## Repo Audit Summary

The [MultiplicityFoundation/PIRTM](https://github.com/MultiplicityFoundation/PIRTM) repository has a single branch (`Multiplicity`) containing a solid contractive-core implementation and several legacy modules that predate the formal PIRTM+ACE+PETC spec. The `src/core/` directory holds 12 Python files totaling ~20 KB of source. Of these, 8 modules are **spec-aligned** and production-ready; 3 are **legacy** (predate the contractive framework); and 1 (`petc.py`) is a **stub** that needs substantial expansion.

No packaging exists (`pyproject.toml`, `setup.py`), no CI workflow, no tests for the contractive core, and the README describes narrative theory rather than the actual API.

## Current State: What Exists

### Spec-Aligned Modules (Keep As-Is)

| Module | Function | Status |
|--------|----------|--------|
| `recurrence.py` | `step()` + `run()` — the certified contractive LTV core | Complete |
| `projection.py` | `project_parameters_soft` + `project_parameters_weighted_l1` (ACE budget) | Complete |
| `certify.py` | `ace_certificate()` + `iss_bound()` — margin, tail, ISS | Complete |
| `fixed_point.py` | `fixed_point_estimate()` — windowed average with tail bound | Complete |
| `adaptive.py` | `AdaptiveMargin` — epsilon controller driven by telemetry | Complete |
| `monitor.py` | `Monitor` — rolling deque of `MonitorRecord` | Complete |
| `infinite_prime.py` | `infinite_prime_check()` — coverage diagnostic | Complete |
| `types.py` | `StepInfo`, `Status`, `Certificate`, `PETCReport`, `MonitorRecord` | Complete |

The `__init__.py` already exports a clean public API with `__all__`.

### Legacy Modules (Need Deprecation or Rewrite)

| Module | Issue |
|--------|-------|
| `pir_tensor.py` | Uses `sympy.primerange`, random QR tensors, no contraction budget, no ACE integration |
| `recursive_ops.py` | Pre-contractive `recursive_update`, Frobenius-norm contraction check, no projection |
| `spectral_decomp.py` | Matplotlib-coupled, eigenvalue analysis not aligned with ACE/SCN spectral certificates |

### Existing Tests (Cover Legacy Only)

Three test files exist (`test_primes.py`, `test_spectral.py`, `test_tensor_dynamics.py`) but target the legacy modules, not the contractive core.

### Existing Examples and Docs

Three Jupyter notebooks in `examples/` and five markdown files in `docs/` cover narrative theory (Moonshine, Langlands, Riemann, Multiplicity, Primer). No examples exercise the actual `step()`/`run()` API.

## Gap Analysis: What is Missing

### Tier 1 — Packaging and CI (Blocking)

1. **`pyproject.toml`** — Package metadata, `[project]` with `numpy` dependency, `[project.optional-dependencies]` for `sympy`/`matplotlib`. Entry point: `pirtm`. Package path restructure: `src/core/` → `src/pirtm/` so `import pirtm` works.
2. **GitHub Actions CI** — `.github/workflows/ci.yml`: lint (`ruff`), type-check (`mypy --strict`), test (`pytest`), on push and PR to `Multiplicity`.
3. **Package layout** — Rename `src/core/` to `src/pirtm/` (or adopt `src/pirtm/core/` if sub-packages are planned). Add top-level `src/pirtm/__init__.py`.

### Tier 2 — Missing Core Modules (Required by Spec)

4. **PETC Ledger** — `petc.py` currently only validates primality. The spec requires a `PrimeLedger` class tracking per-prime exponent signatures `e_p`, supporting `update(prime, delta)`, `checkpoint()`, `rollback()`, conservation verification (`sum(e_input) == e_output`), and sparse-map storage.[^1]
5. **Prime Weight Synthesizer** — A module (`weights.py`) that computes raw weights \(w_p = \lambda_p \cdot p^{\alpha}\) from a prime set, alpha, and lambda vector; then delegates to `project_parameters_weighted_l1` for budget enforcement.[^1]
6. **Operator-Form Gain Builder** — A module (`gain.py`) that constructs the gain operator \(K = \sum_{p} w_p B_p\) from a list of bounded linear maps `B_p` and projected weights, returning the operator as a callable plus the certified norm upper bound \(\|K\| \leq \sum b_p |w_p|\)[^1].
7. **CSC Solver Stub** — A module (`csc.py`) that, given a target gap \(\delta\), slope \(s_{\max}\), and prime-channel bounds, solves for weights meeting all three constraints and emits a `CSCCertificate` dataclass.[^2]

### Tier 3 — Tests for Contractive Core (Required for Trust)

8. **`test_recurrence.py`** — Convergence to known fixed point, contraction rate \(\|X_t - X^*\| \leq q^t \|X_0 - X^*\|\), safety flag, projection trigger.
9. **`test_projection.py`** — Weighted-\(\ell_1\) ball membership post-projection, idempotence, edge cases (all-zero weights, zero budget).
10. **`test_certify.py`** — Certificate `certified=True` when `q < 1-epsilon`, ISS bound finite, tail bound formula.
11. **`test_petc.py`** — Ledger conservation, checkpoint/rollback, violation detection.
12. **`test_weights.py`** — Budget compliance after synthesis, alpha/lambda edge cases.
13. **`test_integration.py`** — End-to-end: build primes → synthesize weights → build gain → run recurrence → certify → check PETC ledger.

### Tier 4 — Documentation and Onboarding

14. **README rewrite** — Replace narrative README with: what PIRTM is (one paragraph), install instructions, quickstart code snippet using `step()`/`run()`, link to docs, license.
15. **`CONTRIBUTING.md`** — PR process, code style (ruff config), test requirements, branch policy.
16. **`CHANGELOG.md`** — Initial entry for v0.1.0.
17. **`docs/architecture.md`** — Map from mathematical spec (PIRTM paper Section 7) to module names.
18. **Updated examples** — At least one `.py` script (not notebook) showing: prime setup → weight synthesis → contractive run → certificate → plot convergence.

### Tier 5 — Legacy Disposition

19. **Deprecation markers** — Add `warnings.warn("deprecated", DeprecationWarning)` to `pir_tensor.py`, `recursive_ops.py`, `spectral_decomp.py`. Move to `src/pirtm/_legacy/`.
20. **Migrate simulation modules** — `src/simulations/` scripts should import from `pirtm` not from `core` directly.

## Proposed Issue Breakdown

Each item below maps to one GitHub Issue to be filed against `MultiplicityFoundation/PIRTM`.

| # | Title | Tier | Depends On | Size |
|---|-------|------|------------|------|
| 1 | Restructure package layout: `src/core/` → `src/pirtm/` | T1 | — | S |
| 2 | Add `pyproject.toml` with numpy dep and build config | T1 | #1 | S |
| 3 | Add GitHub Actions CI: ruff + mypy + pytest | T1 | #2 | S |
| 4 | Implement `PrimeLedger` in `petc.py` (signatures, conservation, checkpoint) | T2 | #1 | M |
| 5 | Add `weights.py`: prime weight synthesizer with alpha/lambda | T2 | #1 | S |
| 6 | Add `gain.py`: operator-form gain builder K = sum w_p B_p | T2 | #5 | M |
| 7 | Add `csc.py`: CSC certificate solver stub (gap, slope, small-gain) | T2 | #6 | M |
| 8 | Tests for contractive core (recurrence, projection, certify) | T3 | #1 | M |
| 9 | Tests for new modules (petc ledger, weights, gain, csc) | T3 | #4-7 | M |
| 10 | Integration test: primes → weights → gain → run → certify → PETC | T3 | #8-9 | M |
| 11 | Rewrite README with install + quickstart + API summary | T4 | #2 | S |
| 12 | Add CONTRIBUTING.md and CHANGELOG.md | T4 | — | S |
| 13 | Add `docs/architecture.md` mapping spec to modules | T4 | #1 | S |
| 14 | Add `examples/quickstart.py` end-to-end script | T4 | #6 | S |
| 15 | Deprecate legacy modules, move to `_legacy/` | T5 | #1 | S |

**Size legend:** S = single-file, <100 LOC. M = multi-file or >100 LOC.

## Execution Order

The critical path runs: #1 → #2 → #3 → #5 → #6 → #4 → #7 → #8 → #9 → #10 → #11 → #14.

Issues #12, #13, #15 are parallelizable at any point.

The first three issues (#1-3) unblock everything else. They establish `pip install -e .` and CI so all subsequent PRs get automated checks.

## Target: v0.1.0

When all 15 issues are closed, tag `v0.1.0` — the first installable, testable, certifiable release of the PIRTM open-source core. The package will expose:

- `pirtm.step()` / `pirtm.run()` — contractive recurrence
- `pirtm.project_parameters_weighted_l1()` — ACE budget projection
- `pirtm.ace_certificate()` / `pirtm.iss_bound()` — safety certificates
- `pirtm.PrimeLedger` — PETC signature tracking
- `pirtm.synthesize_weights()` — prime weight computation
- `pirtm.build_gain()` — operator-form gain constructor
- `pirtm.csc_solve()` — spectral certificate solver
- `pirtm.AdaptiveMargin` / `pirtm.Monitor` — runtime telemetry

---

## References

1. [PIRTM.pdf](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_66e2273e-f127-443b-91a5-5949929d769c/c4f32577-6055-4609-a806-f12b8bce530b/PIRTM.pdf?AWSAccessKeyId=ASIA2F3EMEYE43HLAO4F&Signature=DF9PMDrsR7YxiuDaPfu4G%2Bt%2FJ2I%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHwaCXVzLWVhc3QtMSJHMEUCIQDlHHuLuz1tTBBQQnMdhh8D2X45eu8Zy9ipNMbheYi4EAIgeqnHI7ZgHif4BXJU%2FWmyIimyDIo1vfl01wPtUDdaHXgq8wQIRBABGgw2OTk3NTMzMDk3MDUiDEIcBfQRsJ0H6wOchSrQBPiuYezzSky1qBz8sBRjL2S9Npuz2SG6Iwfcm5bgdmSHy7sJwQBVK5u0x1md1Xe8SAzlk8Cg0p%2B4L8zmOVem%2FigY1sWDDAhTTYPUCA0etsRy7ywEjpKXmLaD7VuvzDWP2rbtdUPSU4XsopHnwrORP2AGZLYnslWrINjE4G%2FQoD7E9mHmnTP1pjMG5yeButHoTirxVoj2HOnX0F5%2F2hM%2BFNMG%2B66%2Fbd4g1SKgnDK%2BOEOMLsrwtP0moJJVfUPzbjAcYW7uaOAK%2FIzjfqXNI2nSS1AbeDL5rBF2wwew6Eruw6sa8aQOUydxAYpGqO0JZFOKihc2xD0U0lepkJOrCONo120Q0C%2BUSebspfgIui0Mz6PSvRI8sPDg4IvP13ZhX%2F1jtjuenzYQzVqUfKAIzspfd6oyU2tJ0p4zCMLlpPInoN93mAPgaoniO3fueucnFe3e1WOEncERkYAAV4xpxXSnjLStEkWMoiMIKnEb4EkUgBOQqbFMzRH4qIOPvXekpy%2F4Gc%2B047Ao%2FS4Hp0wJmKnsvd3j4Aoc9dooV5e6g1dFCtiscxT7%2FD%2FhDZesFehIqL9jYSQQ89%2BwEBpmjJ92gW5TDx6YE1zL2TnPtJJOK2edNE3Z5l1Hj6pei4cO%2B2InujdJoQRIml8b%2BHPPoeXG4RgfGxO%2F%2FVIedeI5m5ytJKOIzW7ytalUCIoQnF6ZKnP9nTU5e6aA6zJ7N2LQLypcnwuQ8V1KbBtHjIqwjNo7OqY1lOH0%2FgNVt8s7PViBg94ND2uQsbWEcNDJD%2FE1nYMiYpe%2BDJ8wvduHzQY6mAH9d1HnFhz5CY1Q1PtB4et%2BsCGtnRyDB5cBAPX1nSbLz7H7zW893zLSeeY2bm1nFL0TBLFVjSJEygy4yQhhuiopkWj%2BlpHQIGYqfrBvsiUB32o4o5vENFGFU4f%2FhPRlRcZ7YXutBXjq07r4VGPI2qhfWiMvSJaSi1ha3QLYDEvVdHSW04r9aW3jKJ%2BOnEQZs20Z7GfEEHBstw%3D%3D&Expires=1772224172) - PIRTMACEPETC

2. [Drmm-Comprehensive-Overview.pdf](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_66e2273e-f127-443b-91a5-5949929d769c/0a4cf207-c523-45f4-af33-cc75d8abc636/Drmm-Comprehensive-Overview.pdf?AWSAccessKeyId=ASIA2F3EMEYE43HLAO4F&Signature=%2BK13lkpUK4JDWgLHtx46k%2BmCl4w%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHwaCXVzLWVhc3QtMSJHMEUCIQDlHHuLuz1tTBBQQnMdhh8D2X45eu8Zy9ipNMbheYi4EAIgeqnHI7ZgHif4BXJU%2FWmyIimyDIo1vfl01wPtUDdaHXgq8wQIRBABGgw2OTk3NTMzMDk3MDUiDEIcBfQRsJ0H6wOchSrQBPiuYezzSky1qBz8sBRjL2S9Npuz2SG6Iwfcm5bgdmSHy7sJwQBVK5u0x1md1Xe8SAzlk8Cg0p%2B4L8zmOVem%2FigY1sWDDAhTTYPUCA0etsRy7ywEjpKXmLaD7VuvzDWP2rbtdUPSU4XsopHnwrORP2AGZLYnslWrINjE4G%2FQoD7E9mHmnTP1pjMG5yeButHoTirxVoj2HOnX0F5%2F2hM%2BFNMG%2B66%2Fbd4g1SKgnDK%2BOEOMLsrwtP0moJJVfUPzbjAcYW7uaOAK%2FIzjfqXNI2nSS1AbeDL5rBF2wwew6Eruw6sa8aQOUydxAYpGqO0JZFOKihc2xD0U0lepkJOrCONo120Q0C%2BUSebspfgIui0Mz6PSvRI8sPDg4IvP13ZhX%2F1jtjuenzYQzVqUfKAIzspfd6oyU2tJ0p4zCMLlpPInoN93mAPgaoniO3fueucnFe3e1WOEncERkYAAV4xpxXSnjLStEkWMoiMIKnEb4EkUgBOQqbFMzRH4qIOPvXekpy%2F4Gc%2B047Ao%2FS4Hp0wJmKnsvd3j4Aoc9dooV5e6g1dFCtiscxT7%2FD%2FhDZesFehIqL9jYSQQ89%2BwEBpmjJ92gW5TDx6YE1zL2TnPtJJOK2edNE3Z5l1Hj6pei4cO%2B2InujdJoQRIml8b%2BHPPoeXG4RgfGxO%2F%2FVIedeI5m5ytJKOIzW7ytalUCIoQnF6ZKnP9nTU5e6aA6zJ7N2LQLypcnwuQ8V1KbBtHjIqwjNo7OqY1lOH0%2FgNVt8s7PViBg94ND2uQsbWEcNDJD%2FE1nYMiYpe%2BDJ8wvduHzQY6mAH9d1HnFhz5CY1Q1PtB4et%2BsCGtnRyDB5cBAPX1nSbLz7H7zW893zLSeeY2bm1nFL0TBLFVjSJEygy4yQhhuiopkWj%2BlpHQIGYqfrBvsiUB32o4o5vENFGFU4f%2FhPRlRcZ7YXutBXjq07r4VGPI2qhfWiMvSJaSi1ha3QLYDEvVdHSW04r9aW3jKJ%2BOnEQZs20Z7GfEEHBstw%3D%3D&Expires=1772224172) - Drmm Comprehensive Overview Dynamic Recursive MetaMathematics DRMM Comprehensive overview, definitio...

