# Q2 Research Track: External Data Contract

**Reference**: Tooling repo, `/multiplicity/Core/docs/plans/q2/`  
**Date**: 2026-03-07  
**Status**: EXTERNAL LINK (non-blocking for PIRTM Phase 2)

---

## What is Q2?

Q2 is a separate **research execution lane** in the Tooling repository that measures and constrains "growing PETC" feasibility for future Phase 4 work. It produces:
- **Task 1c**: Spectral gap scaling Δ(N) vs prime count N
- **Task 1a**: Adiabatic theorem constraints on schedule growth rates

**Key property**: Q2 is **non-blocking for Phase 2**. PIRTM Phase 2 remains static-Ξ^(N) regardless of Q2 status.

---

## Canonical Location & SHA

```
Repository:  MultiplicityFoundation/Tooling (monorepo)
Branch:      main
Commit SHA:  ec9eec5f11869c5faef1e44e59425ca3def34dae (pinned at Q2 capsule creation)

Tooling path: multiplicity/Core/docs/plans/q2/
```

**Primary artifacts**:
- `Task1c-gap.csv` — measured gap data (4 rows, 9 columns, reproducible)
- `Task1c-gap-fit.md` — analysis report (constrain: slope ∈ [-3.46, -3.16], R² > 0.92)
- `Task1a-adiabatic-theorem.md` — reading guide + theorem extraction (due Tue Mar 11)
- `Task1a-constraint.md` — derived schedule constraint (due Tue Mar 11)

---

## Data Contract: Slope & R² Policy

### Primary Contract

$$\boxed{\Delta(N) = A \cdot N^{-\alpha}, \quad \alpha \in [-3.46, -3.16] \text{ (95% CI)}}$$

**What this means**:
- Measured gap Δ(N) between first two eigenvalues of restricted Cayley Laplacian
- Scaling law: N ↦ N + Δ exponent is −3.31 ± 0.15
- **Implication for Phase 4**: If error ~ 1/Δ², constraint on dN/dt grows as N^{6.62}; if error ~ 1/Δ³, grows as N^{9.93}

### Quality Policy: R² Floor (Sanity Check)

- **Current value**: R² = 0.928 (very good fit)
- **Governance rule**: **If R² drops below 0.92 on re-run, output is UNTRUSTED and Phase 4 scheduling is BLOCKED**
- **Why R² is not primary**: With only 4 exact eigenvalue measurements and no noise, R² ≥ 0.92 is excellent. Higher R² strengthens nothing; slope exponent α is what drives Phase 4 feasibility.
- **Slope is primary**: Small change in α has large impact. E.g., α = −3.2 vs. α = −3.4 changes constraint sensitivity by ~9%.

---

## PIRTM Integration: Non-Blocking Parser

PIRTM can **optionally** read Q2 CSV to populate governance metadata. This is **never required** for Phase 2 runs.

### Parser Contract

```python
from pirtm.integrations.q2_gap import parse_q2_gap_csv, GapFit

# Load Q2 gap data (raises ValueError if CSV malformed or missing)
gap: GapFit = parse_q2_gap_csv(
    csv_path="...../multiplicity/Core/docs/plans/q2/Task1c-gap.csv",
    from_commit_sha="ec9eec5f11869c5faef1e44e59425ca3def34dae"  # optional verification
)

# Access fields
assert gap.slope_exponent in [-3.46, -3.16], f"Slope {gap.slope_exponent} out of bounds"
assert gap.r_squared > 0.92, f"R² = {gap.r_squared} below sanity floor"

print(f"Gap scaling: Δ(N) ~ N^{gap.slope_exponent:.2f}")
```

### Phase 2 Firewall

```python
# Phase 2 code: NEVER reads Q2 data
# Phase 2 runs: Static Ξ^(N) always, no conditional logic based on Q2

# ✅ ALLOWED:
epsilon, _, report, Xi = SpectralGovernor.from_laplacian(params).govern_with_laplacian()

# ❌ NOT ALLOWED (would be Phase 2 leakage):
gap = parse_q2_gap_csv(...)  # ← Never in Phase 2 code path
if gap.slope_exponent < -3.4:
    # ... modify Phase 2 behavior
```

**CI enforcement**: Q2 parser tests run separately; failure never blocks Phase 2 core tests.

---

## Reading the Q2 CSV

If you want to understand the output:

```
N,lambda_1,lambda_2,gap,gap_ratio,ndot_threshold,ndot_safe,scaling_exponent,petc_chain_first5
10,0.00801,0.01185,0.00385,0.480,1.48e-05,1.48e-06,-2.415,2 3 5 7 11
...
```

**Columns**:
- `N`: System size (number of primes considered)
- `lambda_1, lambda_2`: Eigenvalues of L^(N) (ordered, smallest first)
- `gap`: Δ(N) = λ₂ − λ₁
- `gap_ratio`: λ₂ / λ₁
- `ndot_threshold, ndot_safe`: Heuristic safety bounds (Task 1a will refine via theorem)
- `scaling_exponent`: Local N-exponent at that point (used in bootstrap for CI)
- `petc_chain_first5`: First 5 primes in the chain (always [2, 3, 5, 7, 11])

---

## Phase 4 Scheduling: How to Use the Constraint

Once Task 1a is complete (Tue Mar 11), the constraint will specify:

$$\dot{N}_{\max}(N) = f(\Delta(N), \text{theorem choice}) \propto N^{-3.31 \times k}$$

where k = 2 or 3 depending on whether error scales as Δ⁻² or Δ⁻³.

**Phase 4 implementation**:
1. If Ṅ_max(N) grows infeasibly fast (e.g., N^{-9} decay), recommend **batchwise N experiments** (vary N between trajectories, not within)
2. If Ṅ_max(N) permits growth (e.g., N^{-2} decay, slow enough to fit runtime), implement growing N(t) with explicit dwell times
3. Any Phase 4 PR touching N(t) dynamics **must cite** the Q2 constraint as a **blocking condition for merge**

---

## Questions?

- **Data accuracy**: Eigenvalues computed via dense NumPy diagonalization; error < 1e-14
- **Reproducibility**: Deterministic seed in notebook; rerun produces same CSV
- **Update frequency**: Q2 is frozen at pinned SHA (ec9eec5f...) for Phase 2 baseline; will unpin for Phase 4 if new data needed
- **Alternative growth schemes**: If Q2 constraint makes direct N(t) growth infeasible, Phase 4 can explore (a) batchwise experiments, (b) annealing s₁(t) instead of N(t), or (c) proof that semigroup breaks but convergence still holds (OPEN research question)

---

## Governance Binding

| Role | Responsibility | Status |
|---|---|---|
| Q2 Lead | Deliver Task 1a constraint by Tue Mar 11 | On schedule |
| PIRTM maintainer | Add parser + non-blocking test | New effort |
| Phase 4 lead | Decide: grow N(t), or pivot to alternatives? | Wed Mar 12 Go/No-Go |
| Phase 2 lead | Ensure Phase 2 tests stay green (ignore Q2) | Automatic (firewall) |

---

**Status**: EXTERNAL LINK ESTABLISHED  
**Binding**: Non-blocking; Phase 2 always proceeds independently  
**Next**: Task 1a constraint delivery (Tue Mar 11)
