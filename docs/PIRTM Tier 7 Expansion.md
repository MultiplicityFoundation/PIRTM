# PIRTM Tier 7: CSL Operators, Spectral Governance, Multi-Session Orchestration, and ΛProof Bridge — Expanded Specification

## Problem Statement

After Tier 6, PIRTM is a fully gated, telemetry-enabled, audit-chained, Q-ARI-adapted numerical engine with a certified DRMM feedback bridge. Four structural gaps remain before PIRTM operates as a first-class participant in the Multiplicity Theory ecosystem at the protocol layer.

1. **No Conscious Sovereignty Layer (CSL) operators.** The CSL Specification defines four ethical operators — Neutrality (N), Beneficence (B), Silence (S), and Commutation — that govern whether an intent is lawful within the Lambda-Proof ecosystem. PIRTM's `EmissionGate` (Tier 6, #31) implements suppression when contraction predicates fail, but it has no concept of the CSL operators. There is no mechanism to evaluate whether a step is *neutral* (uniform across subjects), *beneficial* (no hidden extraction), or should trigger the *Silence Clause* (NO-OP on operator failure). The CSL requires that `intent ⊗ CSL = CSL ⊗ intent` — commutation — and PIRTM currently lacks this algebraic check.

2. **No spectral governance.** PIRTM's `spectral_decomp.py` computes eigenvalues, spectral entropy, and phase coherence of prime-indexed matrices. Lambda-Proof's Governor layer (M6) performs sidechain routing, cost optimization, and failover. No bridge connects the two: spectral analysis of the recurrence operator \( T \) does not inform governance decisions, and governance constraints do not propagate back to bound the spectral radius of \( T \). The operator norm \( \|T\| \) used by `step()` is a static caller-supplied parameter, not a dynamically governed value.

3. **No multi-session orchestration.** Tier 6's `QARISession` manages a single inference loop. Real deployments require multiple concurrent sessions — federation across nodes, session migration, consensus on certificates. Lambda-Proof's M8 architecture specifies distributed sequencer networks with 50+ parallel shards and cross-shard atomic operations. PIRTM has no session registry, no federation protocol, no mechanism for aggregating certificates across sessions.

4. **No ΛProof bridge.** PIRTM's `AuditChain` (Tier 6, #33) produces Merkle-chained events, but it does not natively submit them to Lambda-Proof's Λ-trace on-chain system. Lambda-Proof manages audit event chains with Merkle checkpoints, capability tokens, and EAS schemas. PIRTM produces compatible data but has no adapter to translate and submit.

Tier 7 closes all four gaps across 6 issues (#36-#41).

***

## Deliverable Inventory

| Issue | Deliverable | File(s) | Purpose |
|-------|-------------|---------|---------|
| #36 | CSL operators | `src/pirtm/csl.py` | Neutrality, Beneficence, Silence, Commutation checks |
| #37 | CSL-gated step | `src/pirtm/csl_gate.py` | Compose CSL operators with EmissionGate |
| #38 | Spectral governor | `src/pirtm/spectral_gov.py` | Eigenvalue-informed governance of operator norm |
| #39 | Multi-session orchestrator | `src/pirtm/orchestrator.py` | Session registry, federation, certificate aggregation |
| #40 | ΛProof bridge | `src/pirtm/lambda_bridge.py` | Submit audit chains to Λ-trace on-chain |
| #41 | PETC-chain integration | `src/pirtm/petc_bridge.py` | Prime-indexed event-triggered chain for session ordering |

***

## Issue #36: CSL Operators (`src/pirtm/csl.py`)

### Problem Statement

The CSL Specification defines four operators with mathematical formulations:

- **Neutrality (N)**: For subjects A, B at the same tier, \( \varphi(I, A) = \varphi(I, B) \) — the intent function produces identical results regardless of subject identity on protected attributes.
- **Beneficence (B)**: \( \neg\exists \text{hidden\_side\_effect}(I) \) — no covert value extraction.
- **Silence (S)**: If any operator check fails, default to NO-OP. No token issued, no action taken, audit event logged.
- **Commutation**: Intent commutes with CSL iff \( [N, B, S] \) all evaluate true. Algebraically: \( I \otimes \text{CSL} = \text{CSL} \otimes I \).

PIRTM needs these operators expressed in terms of the contractive recurrence.

### Proposed Architecture

```python
# src/pirtm/csl.py

"""Conscious Sovereignty Layer operators for PIRTM.

Maps CSL ethical operators (Neutrality, Beneficence, Silence,
Commutation) to predicates over the contractive recurrence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

from .types import StepInfo


@dataclass(frozen=True)
class CSLVerdict:
    """Result of CSL operator evaluation."""
    neutrality: bool
    beneficence: bool
    silence_triggered: bool
    commutes: bool
    violations: list[str]
    detail: dict


# --- Neutrality Operator (N) ---

def neutrality_check(
    T: Callable[[np.ndarray], np.ndarray],
    subjects: Sequence[np.ndarray],
    epsilon_n: float = 1e-6,
) -> tuple[bool, dict]:
    """Verify that transform T produces equivalent outputs for
    all subjects at the same tier.

    Neutrality: for subjects A, B → ||T(A) - T(B)|| < epsilon_n
    when A and B differ only on protected attributes.

    Args:
        T: The bounded operator (transform function).
        subjects: Sequence of state vectors representing
                  different subjects at the same tier.
        epsilon_n: Tolerance for output equivalence.

    Returns:
        (is_neutral, detail_dict)
    """
    if len(subjects) < 2:
        return True, {"pairs_checked": 0, "max_deviation": 0.0}

    outputs = [T(s) for s in subjects]
    max_dev = 0.0
    violations = []

    for i in range(len(outputs)):
        for j in range(i + 1, len(outputs)):
            dev = float(np.linalg.norm(outputs[i] - outputs[j]))
            max_dev = max(max_dev, dev)
            if dev >= epsilon_n:
                violations.append((i, j, dev))

    return len(violations) == 0, {
        "pairs_checked": len(outputs) * (len(outputs) - 1) // 2,
        "max_deviation": max_dev,
        "violations": violations,
    }


# --- Beneficence Operator (B) ---

def beneficence_check(
    X_t: np.ndarray,
    X_next: np.ndarray,
    info: StepInfo,
    *,
    norm_growth_limit: float = 1.0,
    residual_limit: float = 10.0,
    custom_checks: Sequence[Callable[[np.ndarray, np.ndarray, StepInfo], bool]] | None = None,
) -> tuple[bool, dict]:
    """Verify that a step does not covertly extract value or
    introduce hidden side effects.

    Beneficence is operationalized as:
    1. No unbounded norm growth (energy extraction).
    2. Residual within bounds (no divergent side channel).
    3. Custom domain checks pass.

    Args:
        X_t: State before step.
        X_next: State after step.
        info: StepInfo from the step.
        norm_growth_limit: Max allowed ||X_next|| / ||X_t||.
        residual_limit: Max allowed residual.
        custom_checks: Optional additional predicates.

    Returns:
        (is_beneficent, detail_dict)
    """
    violations = []

    # Energy extraction check
    norm_t = float(np.linalg.norm(X_t))
    norm_next = float(np.linalg.norm(X_next))
    if norm_t > 0:
        growth = norm_next / norm_t
    else:
        growth = norm_next  # From zero, any growth is the ratio

    if growth > norm_growth_limit:
        violations.append(f"norm_growth={growth:.4f}>{norm_growth_limit}")

    # Residual check (side-channel leakage proxy)
    if info.residual > residual_limit:
        violations.append(f"residual={info.residual:.4f}>{residual_limit}")

    # Custom domain checks
    if custom_checks:
        for i, check in enumerate(custom_checks):
            if not check(X_t, X_next, info):
                violations.append(f"custom_check_{i}_failed")

    return len(violations) == 0, {
        "norm_growth": growth,
        "residual": info.residual,
        "violations": violations,
    }


# --- Silence Clause (S) ---

@dataclass(frozen=True)
class SilenceEvent:
    """Audit record for a Silence Clause trigger."""
    step: int
    reason: str
    operator_failed: str  # "neutrality" | "beneficence" | "custom"
    detail: dict


def silence_clause(
    neutrality_ok: bool,
    beneficence_ok: bool,
    step_index: int,
    detail: dict,
) -> tuple[bool, SilenceEvent | None]:
    """Apply the Silence Clause: if any CSL operator fails,
    trigger NO-OP.

    Returns:
        (silence_triggered, event_or_none)
    """
    if neutrality_ok and beneficence_ok:
        return False, None

    failed = []
    if not neutrality_ok:
        failed.append("neutrality")
    if not beneficence_ok:
        failed.append("beneficence")

    event = SilenceEvent(
        step=step_index,
        reason=f"CSL operator(s) failed: {', '.join(failed)}",
        operator_failed=failed,
        detail=detail,
    )
    return True, event


# --- Commutation Check ---

def commutation_check(
    T: Callable[[np.ndarray], np.ndarray],
    csl_filter: Callable[[np.ndarray], np.ndarray],
    X: np.ndarray,
    epsilon_c: float = 1e-6,
) -> tuple[bool, dict]:
    """Verify that intent commutes with CSL:
        T(CSL(X)) ≈ CSL(T(X))

    This is the algebraic requirement that the order of
    applying the transform and the CSL filter does not matter.

    Args:
        T: The bounded operator (intent).
        csl_filter: The CSL filtering function.
        X: State vector to test.
        epsilon_c: Tolerance for commutation equivalence.

    Returns:
        (commutes, detail_dict)
    """
    # Path 1: T then CSL
    path1 = csl_filter(T(X))
    # Path 2: CSL then T
    path2 = T(csl_filter(X))

    deviation = float(np.linalg.norm(path1 - path2))
    commutes = deviation < epsilon_c

    return commutes, {
        "deviation": deviation,
        "epsilon_c": epsilon_c,
        "commutes": commutes,
    }


# --- Full CSL Evaluation ---

def evaluate_csl(
    T: Callable[[np.ndarray], np.ndarray],
    X_t: np.ndarray,
    X_next: np.ndarray,
    info: StepInfo,
    step_index: int,
    *,
    subjects: Sequence[np.ndarray] | None = None,
    csl_filter: Callable[[np.ndarray], np.ndarray] | None = None,
    epsilon_n: float = 1e-6,
    epsilon_c: float = 1e-6,
    norm_growth_limit: float = 1.0,
    residual_limit: float = 10.0,
) -> CSLVerdict:
    """Full CSL evaluation: N, B, S, and Commutation.

    Returns a CSLVerdict with all operator results.
    """
    # Neutrality
    if subjects is not None and len(subjects) >= 2:
        n_ok, n_detail = neutrality_check(T, subjects, epsilon_n)
    else:
        n_ok, n_detail = True, {"skipped": True}

    # Beneficence
    b_ok, b_detail = beneficence_check(
        X_t, X_next, info,
        norm_growth_limit=norm_growth_limit,
        residual_limit=residual_limit,
    )

    # Silence
    silence, silence_event = silence_clause(n_ok, b_ok, step_index, {
        "neutrality": n_detail,
        "beneficence": b_detail,
    })

    # Commutation
    if csl_filter is not None:
        c_ok, c_detail = commutation_check(T, csl_filter, X_t, epsilon_c)
    else:
        c_ok, c_detail = True, {"skipped": True}

    violations = []
    if not n_ok:
        violations.append("neutrality")
    if not b_ok:
        violations.append("beneficence")
    if silence:
        violations.append("silence_triggered")
    if not c_ok:
        violations.append("commutation")

    return CSLVerdict(
        neutrality=n_ok,
        beneficence=b_ok,
        silence_triggered=silence,
        commutes=c_ok,
        violations=violations,
        detail={
            "neutrality": n_detail,
            "beneficence": b_detail,
            "commutation": c_detail,
            "silence_event": silence_event,
        },
    )
```

### CSL ↔ PIRTM Mapping

| CSL Operator | PIRTM Mechanism | Predicate |
|-------------|----------------|-----------|
| Neutrality (N) | `neutrality_check()` | \( \|T(A) - T(B)\| < \varepsilon_N \) for subjects at same tier |
| Beneficence (B) | `beneficence_check()` | No unbounded norm growth, residual within bounds |
| Silence (S) | `silence_clause()` | If N or B fails → NO-OP (zero emission) |
| Commutation | `commutation_check()` | \( \|T(\text{CSL}(X)) - \text{CSL}(T(X))\| < \varepsilon_C \) |

### Acceptance Criteria

- `neutrality_check()` returns `False` when \( \|T(A) - T(B)\| \geq \varepsilon_N \) for any pair
- `beneficence_check()` returns `False` when norm growth exceeds limit or residual exceeds bound
- `silence_clause()` returns `True` (triggered) when either N or B fails
- `commutation_check()` returns `False` when path deviation \( \geq \varepsilon_C \)
- `evaluate_csl()` composes all four operators into a single `CSLVerdict`
- `CSLVerdict.violations` lists all failed operators
- Skipped checks (no subjects, no csl_filter) default to pass, flagged as `skipped`
- Zero external dependencies beyond numpy

### Estimated Size

~250 LOC.

***

## Issue #37: CSL-Gated Step (`src/pirtm/csl_gate.py`)

### Problem Statement

Tier 6's `EmissionGate` evaluates contraction predicates. The CSL operators (Issue #36) evaluate ethical predicates. Neither knows about the other. A step must pass *both* the contraction gate and the CSL gate to be emitted. When CSL triggers Silence, the output must be NO-OP — stronger than `SUPPRESS` (which zeros the vector), Silence means the step is as if it never happened.

### Proposed Architecture

```python
# src/pirtm/csl_gate.py

"""CSL-aware emission gate: compose contraction + ethical predicates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

from .recurrence import step
from .gate import EmissionGate, EmissionPolicy, GatedOutput
from .csl import evaluate_csl, CSLVerdict, SilenceEvent
from .types import StepInfo


@dataclass(frozen=True)
class CSLGatedOutput:
    """Result of a CSL-gated step."""
    X_next: np.ndarray
    info: StepInfo
    gate_output: GatedOutput
    csl_verdict: CSLVerdict
    emitted: bool               # True only if BOTH gates pass
    silenced: bool              # True if CSL Silence Clause triggered
    final_policy: str           # "emitted" | "contraction_gated" | "csl_silenced"


class CSLEmissionGate:
    """Two-stage gate: contraction predicate → CSL operators.

    Stage 1: EmissionGate checks q_t contraction.
    Stage 2: CSL operators check N, B, S, Commutation.

    Output is emitted only if both stages pass.
    If CSL Silence triggers, output is the *input* X_t (NO-OP).
    """

    def __init__(
        self,
        contraction_gate: EmissionGate,
        *,
        subjects: Sequence[np.ndarray] | None = None,
        csl_filter: Callable[[np.ndarray], np.ndarray] | None = None,
        epsilon_n: float = 1e-6,
        epsilon_c: float = 1e-6,
        norm_growth_limit: float = 1.0,
        residual_limit: float = 10.0,
    ):
        self.contraction_gate = contraction_gate
        self.subjects = subjects
        self.csl_filter = csl_filter
        self.epsilon_n = epsilon_n
        self.epsilon_c = epsilon_c
        self.norm_growth_limit = norm_growth_limit
        self.residual_limit = residual_limit

    def __call__(
        self,
        X_t: np.ndarray,
        Xi_t: np.ndarray,
        Lam_t: np.ndarray,
        T: Callable,
        G_t: np.ndarray,
        P: Callable,
        step_index: int,
        *,
        epsilon: float = 0.05,
        op_norm_T: float = 1.0,
    ) -> CSLGatedOutput:
        # Stage 1: Contraction gate
        gate_result = self.contraction_gate(
            X_t, Xi_t, Lam_t, T, G_t, P,
            epsilon=epsilon, op_norm_T=op_norm_T,
        )

        if not gate_result.emitted:
            # Contraction gate suppressed — skip CSL (already gated)
            return CSLGatedOutput(
                X_next=gate_result.X_next,
                info=gate_result.info,
                gate_output=gate_result,
                csl_verdict=CSLVerdict(
                    neutrality=True, beneficence=True,
                    silence_triggered=False, commutes=True,
                    violations=[], detail={"skipped": "contraction_gated"},
                ),
                emitted=False,
                silenced=False,
                final_policy="contraction_gated",
            )

        # Stage 2: CSL evaluation
        verdict = evaluate_csl(
            T=T,
            X_t=X_t,
            X_next=gate_result.X_next,
            info=gate_result.info,
            step_index=step_index,
            subjects=self.subjects,
            csl_filter=self.csl_filter,
            epsilon_n=self.epsilon_n,
            epsilon_c=self.epsilon_c,
            norm_growth_limit=self.norm_growth_limit,
            residual_limit=self.residual_limit,
        )

        if verdict.silence_triggered:
            # CSL Silence: NO-OP — return input state unchanged
            return CSLGatedOutput(
                X_next=X_t.copy(),  # NO-OP: state unchanged
                info=gate_result.info,
                gate_output=gate_result,
                csl_verdict=verdict,
                emitted=False,
                silenced=True,
                final_policy="csl_silenced",
            )

        if not verdict.commutes:
            # Non-commuting intent: also silence
            return CSLGatedOutput(
                X_next=X_t.copy(),
                info=gate_result.info,
                gate_output=gate_result,
                csl_verdict=verdict,
                emitted=False,
                silenced=True,
                final_policy="csl_silenced(non_commuting)",
            )

        # Both gates pass
        return CSLGatedOutput(
            X_next=gate_result.X_next,
            info=gate_result.info,
            gate_output=gate_result,
            csl_verdict=verdict,
            emitted=True,
            silenced=False,
            final_policy="emitted",
        )
```

### Emission Truth Table

| Contraction Gate | CSL N | CSL B | CSL Commutes | Output | Policy |
|-----------------|-------|-------|-------------|--------|--------|
| PASS | PASS | PASS | PASS | `X_next` | `emitted` |
| FAIL | — | — | — | per gate policy | `contraction_gated` |
| PASS | FAIL | any | any | `X_t` (NO-OP) | `csl_silenced` |
| PASS | any | FAIL | any | `X_t` (NO-OP) | `csl_silenced` |
| PASS | PASS | PASS | FAIL | `X_t` (NO-OP) | `csl_silenced(non_commuting)` |

### Acceptance Criteria

- `CSLGatedOutput.emitted == True` only when both contraction gate and all CSL operators pass
- `CSLGatedOutput.silenced == True` when CSL Silence Clause triggers
- Silence returns `X_t` (input state), not zero vector — this is NO-OP, not suppression
- Non-commuting intents are silenced even if N and B pass
- When contraction gate fires first, CSL evaluation is skipped (no wasted computation)
- `CSLVerdict` is always populated in the output for audit trail

### Estimated Size

~150 LOC.

***

## Issue #38: Spectral Governor (`src/pirtm/spectral_gov.py`)

### Problem Statement

PIRTM's `spectral_decomp.py` computes eigenvalues and spectral entropy of matrices. The operator norm `op_norm_T` is passed to `step()` as a static float. Lambda-Proof's Governor layer (M6) optimizes routing and manages failover. No feedback loop exists where spectral analysis of \( T \) informs the governance of `epsilon` and `op_norm_T`, or where governance constraints bound the spectral radius.

### Proposed Architecture

```python
# src/pirtm/spectral_gov.py

"""Spectral governor: eigenvalue-informed governance of the operator norm."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .spectral_decomp import spectral_decomposition, spectral_entropy, phase_coherence


@dataclass(frozen=True)
class SpectralReport:
    """Spectral analysis report for governance."""
    spectral_radius: float       # max |eigenvalue|
    spectral_entropy: float      # Information content of spectrum
    phase_coherence: float       # 0 = coherent, 1 = incoherent
    op_norm_estimate: float      # Estimated operator norm
    contraction_feasible: bool   # True if spectral radius < 1
    recommended_epsilon: float   # Governance-recommended epsilon
    eigenvalues: np.ndarray
    detail: dict


class SpectralGovernor:
    """Dynamically governs operator norm and epsilon based on
    spectral analysis of the recurrence operator T.

    The governor:
    1. Estimates the spectral radius of T from sample evaluations.
    2. Recommends epsilon to maintain contraction margin.
    3. Flags non-contractive operators for rejection.
    4. Adapts governance parameters as the spectrum evolves.
    """

    def __init__(
        self,
        dim: int,
        min_epsilon: float = 0.01,
        max_epsilon: float = 0.3,
        safety_margin: float = 0.1,
        entropy_ceiling: float = 2.0,
    ):
        self.dim = dim
        self.min_epsilon = min_epsilon
        self.max_epsilon = max_epsilon
        self.safety_margin = safety_margin
        self.entropy_ceiling = entropy_ceiling
        self._history: list[SpectralReport] = []

    def analyze(
        self,
        T: Callable[[np.ndarray], np.ndarray],
        n_samples: int = 10,
    ) -> SpectralReport:
        """Analyze operator T by constructing its Jacobian
        approximation and computing spectral properties.

        Uses finite-difference Jacobian estimation on random
        unit vectors to approximate the operator matrix.
        """
        # Construct approximate operator matrix via probing
        J = np.zeros((self.dim, self.dim))
        delta = 1e-5

        # Use a reference point near zero
        x0 = np.zeros(self.dim)
        f0 = T(x0)

        for i in range(self.dim):
            e_i = np.zeros(self.dim)
            e_i[i] = delta
            f_i = T(x0 + e_i)
            J[:, i] = (f_i - f0) / delta

        # Spectral analysis
        eigvals, eigvecs = spectral_decomposition(J)
        s_radius = float(np.max(np.abs(eigvals)))
        s_entropy = float(spectral_entropy(eigvals))
        p_coherence = float(phase_coherence(eigvals))

        # Operator norm estimate (2-norm = largest singular value)
        s_values = np.linalg.svd(J, compute_uv=False)
        op_norm = float(s_values) if len(s_values) > 0 else s_radius

        # Governance decisions
        contraction_feasible = s_radius < 1.0

        if contraction_feasible:
            # Recommended epsilon: enough margin above spectral radius
            recommended = min(
                max(1.0 - s_radius - self.safety_margin, self.min_epsilon),
                self.max_epsilon,
            )
        else:
            recommended = self.max_epsilon  # Max epsilon for non-contractive

        report = SpectralReport(
            spectral_radius=s_radius,
            spectral_entropy=s_entropy,
            phase_coherence=p_coherence,
            op_norm_estimate=op_norm,
            contraction_feasible=contraction_feasible,
            recommended_epsilon=recommended,
            eigenvalues=eigvals,
            detail={
                "dim": self.dim,
                "jacobian_norm": float(np.linalg.norm(J)),
                "singular_values": s_values.tolist(),
                "entropy_within_ceiling": s_entropy <= self.entropy_ceiling,
            },
        )
        self._history.append(report)
        return report

    def govern(
        self,
        T: Callable[[np.ndarray], np.ndarray],
    ) -> tuple[float, float, SpectralReport]:
        """Full governance cycle: analyze → recommend epsilon and op_norm.

        Returns: (recommended_epsilon, op_norm_estimate, report)
        """
        report = self.analyze(T)
        return report.recommended_epsilon, report.op_norm_estimate, report

    def trend(self) -> dict:
        """Spectral trend over governance history."""
        if not self._history:
            return {"reports": 0}
        radii = [r.spectral_radius for r in self._history]
        entropies = [r.spectral_entropy for r in self._history]
        return {
            "reports": len(self._history),
            "radius_min": min(radii),
            "radius_max": max(radii),
            "radius_trend": "stable" if max(radii) - min(radii) < 0.05 else "volatile",
            "entropy_mean": sum(entropies) / len(entropies),
            "contraction_rate": sum(1 for r in self._history if r.contraction_feasible) / len(self._history),
        }

    @property
    def history(self) -> list[SpectralReport]:
        return list(self._history)
```

### Governance Flow

```
T (operator)
    │
    ▼
SpectralGovernor.govern(T)
    │
    ├─ Jacobian estimation (finite difference)
    ├─ Eigenvalue decomposition
    ├─ Spectral radius, entropy, phase coherence
    ├─ Operator norm (SVD)
    │
    ▼
(epsilon_recommended, op_norm_estimate, SpectralReport)
    │
    ▼
QARISession.step(... epsilon=eps, op_norm_T=norm ...)
```

### Acceptance Criteria

- `SpectralGovernor.analyze()` returns `SpectralReport` with spectral radius, entropy, coherence
- `contraction_feasible == True` iff spectral radius < 1.0
- `recommended_epsilon` is clamped within `[min_epsilon, max_epsilon]`
- `op_norm_estimate` uses SVD (largest singular value), not just spectral radius
- `trend()` reports stability metrics over governance history
- Jacobian estimation uses finite differences (no symbolic differentiation dependency)
- Zero external dependencies beyond numpy

### Estimated Size

~200 LOC.

***

## Issue #39: Multi-Session Orchestrator (`src/pirtm/orchestrator.py`)

### Problem Statement

Lambda-Proof M8 specifies distributed sequencer networks with 50+ shards, cross-shard atomic operations, and aggregated finality. PIRTM's `QARISession` manages a single loop. Deployments require:

- A registry of active sessions
- Certificate aggregation across sessions
- Session migration (pause, serialize, resume)
- Consensus on cross-session certificates

### Proposed Architecture

```python
# src/pirtm/orchestrator.py

"""Multi-session orchestration: registry, federation, certificate aggregation."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Callable

import numpy as np

from .qari import QARISession, QARIConfig
from .certify import ace_certificate
from .types import Certificate, StepInfo
from .audit import AuditChain


@dataclass(frozen=True)
class SessionDescriptor:
    """Metadata for a registered session."""
    session_id: str
    config: QARIConfig
    created_at: float
    status: str  # "active" | "paused" | "completed" | "failed"


@dataclass(frozen=True)
class AggregatedCertificate:
    """Certificate aggregated across multiple sessions."""
    session_ids: list[str]
    individual_certs: list[Certificate]
    all_certified: bool
    q_max_global: float
    margin_min: float
    aggregate_hash: str  # SHA-256 of all cert hashes


@dataclass
class SessionSnapshot:
    """Serializable snapshot for session migration."""
    session_id: str
    config_dict: dict
    step_count: int
    infos: list[dict]
    epsilon: float
    audit_events: list[dict]
    snapshot_time: float


class SessionOrchestrator:
    """Manages multiple PIRTM sessions with federation support.

    Capabilities:
    - Register and track sessions by ID.
    - Aggregate certificates across sessions.
    - Pause/resume sessions via serializable snapshots.
    - Cross-session audit chain linking.
    """

    def __init__(self):
        self._sessions: dict[str, QARISession] = {}
        self._descriptors: dict[str, SessionDescriptor] = {}
        self._master_audit = AuditChain()

    def register(
        self,
        session_id: str,
        config: QARIConfig,
        **session_kwargs,
    ) -> QARISession:
        """Create and register a new session."""
        if session_id in self._sessions:
            raise ValueError(f"Session '{session_id}' already registered")

        session = QARISession(config, **session_kwargs)
        self._sessions[session_id] = session
        self._descriptors[session_id] = SessionDescriptor(
            session_id=session_id,
            config=config,
            created_at=time.time(),
            status="active",
        )
        return session

    def get(self, session_id: str) -> QARISession:
        """Retrieve a registered session."""
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' not found")
        return self._sessions[session_id]

    def list_sessions(self, status: str | None = None) -> list[SessionDescriptor]:
        """List registered sessions, optionally filtered by status."""
        descs = list(self._descriptors.values())
        if status is not None:
            descs = [d for d in descs if d.status == status]
        return descs

    def aggregate_certificates(
        self,
        session_ids: list[str] | None = None,
        tail_norm: float = 0.0,
    ) -> AggregatedCertificate:
        """Aggregate certificates across specified sessions.

        If session_ids is None, aggregates all active sessions.
        """
        if session_ids is None:
            session_ids = [
                sid for sid, d in self._descriptors.items()
                if d.status in ("active", "completed")
            ]

        certs = []
        for sid in session_ids:
            session = self._sessions[sid]
            cert = session.certify(tail_norm=tail_norm)
            certs.append(cert)

        all_certified = all(c.certified for c in certs)
        q_maxes = [c.q_max for c in certs if hasattr(c, 'q_max')]
        margins = [c.margin for c in certs]

        # Hash all certificates for aggregate integrity
        cert_hashes = []
        for c in certs:
            canonical = json.dumps(asdict(c), sort_keys=True,
                                   separators=(",", ":"), default=str)
            cert_hashes.append(
                hashlib.sha256(canonical.encode()).hexdigest()
            )
        aggregate_hash = hashlib.sha256(
            "".join(cert_hashes).encode()
        ).hexdigest()

        # Record in master audit chain
        self._master_audit._append({
            "type": "aggregate_certificate",
            "session_ids": session_ids,
            "all_certified": all_certified,
            "aggregate_hash": aggregate_hash,
        })

        return AggregatedCertificate(
            session_ids=session_ids,
            individual_certs=certs,
            all_certified=all_certified,
            q_max_global=max(q_maxes) if q_maxes else 0.0,
            margin_min=min(margins) if margins else 0.0,
            aggregate_hash=aggregate_hash,
        )

    def pause(self, session_id: str) -> SessionSnapshot:
        """Pause a session and return a serializable snapshot."""
        session = self.get(session_id)
        infos_dicts = [asdict(i) for i in session.infos]
        audit_export = session.audit_chain.export() if session.audit_chain else []

        snapshot = SessionSnapshot(
            session_id=session_id,
            config_dict=asdict(session.config),
            step_count=session.step_count,
            infos=infos_dicts,
            epsilon=session.current_epsilon,
            audit_events=audit_export,
            snapshot_time=time.time(),
        )

        self._descriptors[session_id] = SessionDescriptor(
            session_id=session_id,
            config=session.config,
            created_at=self._descriptors[session_id].created_at,
            status="paused",
        )
        return snapshot

    def complete(self, session_id: str) -> None:
        """Mark a session as completed."""
        if session_id not in self._descriptors:
            raise KeyError(f"Session '{session_id}' not found")
        desc = self._descriptors[session_id]
        self._descriptors[session_id] = SessionDescriptor(
            session_id=session_id,
            config=desc.config,
            created_at=desc.created_at,
            status="completed",
        )

    def global_summary(self) -> dict:
        """Summary across all sessions."""
        summaries = {}
        for sid, session in self._sessions.items():
            summaries[sid] = session.summary()

        total_steps = sum(s.get("steps", 0) for s in summaries.values())
        total_projections = sum(s.get("projected_count", 0) for s in summaries.values())

        return {
            "total_sessions": len(self._sessions),
            "active": len([d for d in self._descriptors.values() if d.status == "active"]),
            "completed": len([d for d in self._descriptors.values() if d.status == "completed"]),
            "paused": len([d for d in self._descriptors.values() if d.status == "paused"]),
            "total_steps": total_steps,
            "total_projections": total_projections,
            "master_audit_length": len(self._master_audit),
            "per_session": summaries,
        }

    @property
    def master_audit(self) -> AuditChain:
        return self._master_audit
```

### Acceptance Criteria

- `register()` creates and returns a `QARISession` tracked by ID
- `aggregate_certificates()` returns `AggregatedCertificate` with per-session and global fields
- `all_certified` is `True` only if every session's certificate is certified
- `aggregate_hash` is deterministic (same inputs → same hash)
- `pause()` returns a serializable `SessionSnapshot`
- `list_sessions()` filters by status
- `global_summary()` reports total steps, projections, and audit chain length
- Master audit chain records aggregate certificate events
- Duplicate session IDs raise `ValueError`
- Missing session IDs raise `KeyError`

### Estimated Size

~300 LOC.

***

## Issue #40: ΛProof Bridge (`src/pirtm/lambda_bridge.py`)

### Problem Statement

PIRTM's `AuditChain` (Tier 6, #33) produces Merkle-chained events in JSON. Lambda-Proof's Λ-trace system expects audit events with specific schemas (EAS schemas, capability tokens, Merkle checkpoints). No adapter translates between the two formats.

### Proposed Architecture

```python
# src/pirtm/lambda_bridge.py

"""ΛProof bridge: translate PIRTM audit chains to Λ-trace format."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Callable

from .audit import AuditChain, AuditEvent
from .types import Certificate


@dataclass(frozen=True)
class LambdaTraceEvent:
    """Event formatted for Lambda-Proof Λ-trace submission."""
    schema_id: str           # EAS schema identifier
    event_type: str          # "pirtm.step" | "pirtm.certificate" | "pirtm.gate"
    sequence: int
    chain_hash: str          # From PIRTM audit chain
    payload: dict            # Formatted per Λ-trace schema
    capability_token: str    # Scoped capability token for submission
    timestamp: float
    source: str              # "pirtm:<session_id>"


@dataclass(frozen=True)
class SubmissionReceipt:
    """Receipt from Λ-trace submission."""
    batch_id: str
    events_submitted: int
    merkle_root: str         # Root of submitted batch
    status: str              # "pending" | "accepted" | "rejected"
    timestamp: float


class LambdaTraceBridge:
    """Translates PIRTM audit chain events to Lambda-Proof Λ-trace format
    and manages batch submission.

    The bridge:
    1. Reads events from a PIRTM AuditChain.
    2. Translates each to LambdaTraceEvent with EAS schema mapping.
    3. Batches events for submission.
    4. Produces a SubmissionReceipt with the batch Merkle root.

    Actual on-chain submission is delegated to a caller-supplied
    submit function, keeping the bridge transport-agnostic.
    """

    # Default EAS schema IDs (configurable)
    SCHEMA_STEP = "pirtm.step.v1"
    SCHEMA_CERTIFICATE = "pirtm.certificate.v1"
    SCHEMA_GATE = "pirtm.gate.v1"
    SCHEMA_AGGREGATE = "pirtm.aggregate.v1"

    def __init__(
        self,
        session_id: str,
        capability_token: str = "",
        submit_fn: Callable[[list[dict]], SubmissionReceipt] | None = None,
    ):
        self.session_id = session_id
        self.capability_token = capability_token
        self._submit_fn = submit_fn
        self._pending: list[LambdaTraceEvent] = []

    def translate(self, chain: AuditChain) -> list[LambdaTraceEvent]:
        """Translate entire PIRTM audit chain to Λ-trace events."""
        events = []
        for audit_event in chain:
            payload = json.loads(audit_event.payload_json)
            event_type = payload.get("type", "unknown")

            schema_id = {
                "step": self.SCHEMA_STEP,
                "certificate": self.SCHEMA_CERTIFICATE,
                "gate": self.SCHEMA_GATE,
                "aggregate_certificate": self.SCHEMA_AGGREGATE,
            }.get(event_type, f"pirtm.{event_type}.v1")

            trace_event = LambdaTraceEvent(
                schema_id=schema_id,
                event_type=f"pirtm.{event_type}",
                sequence=audit_event.sequence,
                chain_hash=audit_event.chain_hash,
                payload=payload,
                capability_token=self.capability_token,
                timestamp=time.time(),
                source=f"pirtm:{self.session_id}",
            )
            events.append(trace_event)

        self._pending.extend(events)
        return events

    def batch_submit(self) -> SubmissionReceipt:
        """Submit all pending events as a batch.

        If no submit_fn was provided, returns a local receipt
        without actual submission (dry-run mode).
        """
        if not self._pending:
            return SubmissionReceipt(
                batch_id="empty",
                events_submitted=0,
                merkle_root="0" * 64,
                status="empty",
                timestamp=time.time(),
            )

        # Compute batch Merkle root
        hashes = [e.chain_hash for e in self._pending]
        merkle_root = self._compute_merkle_root(hashes)

        batch_id = hashlib.sha256(
            f"{self.session_id}:{merkle_root}:{time.time()}".encode()
        ).hexdigest()[:16]

        batch_payload = [
            {
                "schema_id": e.schema_id,
                "event_type": e.event_type,
                "sequence": e.sequence,
                "chain_hash": e.chain_hash,
                "payload": e.payload,
                "capability_token": e.capability_token,
                "timestamp": e.timestamp,
                "source": e.source,
            }
            for e in self._pending
        ]

        if self._submit_fn is not None:
            receipt = self._submit_fn(batch_payload)
        else:
            receipt = SubmissionReceipt(
                batch_id=batch_id,
                events_submitted=len(self._pending),
                merkle_root=merkle_root,
                status="dry_run",
                timestamp=time.time(),
            )

        self._pending.clear()
        return receipt

    @staticmethod
    def _compute_merkle_root(hashes: list[str]) -> str:
        """Compute a simple Merkle root from a list of hex hashes."""
        if not hashes:
            return "0" * 64

        layer = list(hashes)
        while len(layer) > 1:
            next_layer = []
            for i in range(0, len(layer), 2):
                left = layer[i]
                right = layer[i + 1] if i + 1 < len(layer) else left
                combined = hashlib.sha256(
                    (left + right).encode()
                ).hexdigest()
                next_layer.append(combined)
            layer = next_layer

        return layer

    @property
    def pending_count(self) -> int:
        return len(self._pending)
```

### Acceptance Criteria

- `translate()` maps each PIRTM `AuditEvent` to a `LambdaTraceEvent` with correct schema ID
- Schema IDs follow `pirtm.<type>.v1` convention
- `batch_submit()` computes a Merkle root over chain hashes
- Without `submit_fn`, `batch_submit()` returns a `dry_run` receipt
- With `submit_fn`, the function is called with the full batch payload
- Pending events are cleared after successful submission
- Empty batch returns status `"empty"`
- `_compute_merkle_root()` handles odd-length lists (duplicate last element)
- Zero external dependencies beyond stdlib

### Estimated Size

~200 LOC.

***

## Issue #41: PETC-Chain Integration (`src/pirtm/petc_bridge.py`)

### Problem Statement

PIRTM has a `petc.py` module that validates prime-typed event-triggered chains (PETC) — sequences where each event index is a prime number, forming a verifiable ordering. This PETC structure is not connected to the session orchestrator or the audit chain. For multi-session ordering, each session's events should be assigned prime indices (from the PETC sequence), providing a deterministic, non-colliding ordering across federated sessions.

### Proposed Architecture

```python
# src/pirtm/petc_bridge.py

"""PETC-chain integration: prime-indexed event ordering for sessions."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .petc import _is_prime, petc_invariants, PETCReport
from .audit import AuditChain


def _next_prime(n: int) -> int:
    """Return the smallest prime >= n."""
    candidate = max(n, 2)
    while not _is_prime(candidate):
        candidate += 1
    return candidate


@dataclass(frozen=True)
class PETCAllocation:
    """Prime index allocation for a session."""
    session_id: str
    prime_base: int          # Starting prime for this session
    prime_stride: int        # Nth prime offset (for non-collision)
    allocated_primes: list[int]
    report: PETCReport


class PETCAllocator:
    """Allocates non-overlapping prime indices to sessions.

    Each session gets a unique prime-indexed subsequence,
    guaranteeing non-collision across federated sessions.

    Strategy: Session k gets primes from the k-th prime
    onward, with stride equal to the number of sessions.
    This ensures disjoint prime sets.
    """

    def __init__(self, max_sessions: int = 100):
        self.max_sessions = max_sessions
        self._allocations: dict[str, PETCAllocation] = {}
        self._session_counter = 0

    def allocate(
        self,
        session_id: str,
        event_count: int,
    ) -> PETCAllocation:
        """Allocate prime indices for a session's events."""
        if session_id in self._allocations:
            return self._allocations[session_id]

        # Assign this session a unique offset
        offset = self._session_counter
        self._session_counter += 1

        # Generate primes for this session
        primes = []
        candidate = _next_prime(2 + offset)
        seen = 0
        # Skip primes assigned to other sessions
        while len(primes) < event_count:
            if seen % max(self._session_counter, 1) == offset:
                primes.append(candidate)
            candidate = _next_prime(candidate + 1)
            seen += 1

        # Validate PETC invariants
        report = petc_invariants(primes, min_length=min(3, event_count))

        allocation = PETCAllocation(
            session_id=session_id,
            prime_base=primes if primes else 2,
            prime_stride=self._session_counter,
            allocated_primes=primes,
            report=report,
        )
        self._allocations[session_id] = allocation
        return allocation

    def tag_audit_chain(
        self,
        session_id: str,
        chain: AuditChain,
    ) -> list[tuple[int, str]]:
        """Tag each event in an audit chain with its prime index.

        Returns: list of (prime_index, chain_hash) pairs.
        """
        alloc = self.allocate(session_id, len(chain))
        tagged = []
        for event, prime in zip(chain, alloc.allocated_primes):
            tagged.append((prime, event.chain_hash))
        return tagged

    def verify_global_ordering(self) -> dict:
        """Verify that all allocated primes are globally non-colliding."""
        all_primes: list[int] = []
        for alloc in self._allocations.values():
            all_primes.extend(alloc.allocated_primes)

        unique = set(all_primes)
        collisions = len(all_primes) - len(unique)

        return {
            "total_primes": len(all_primes),
            "unique_primes": len(unique),
            "collisions": collisions,
            "globally_ordered": collisions == 0,
            "sessions": len(self._allocations),
        }

    @property
    def allocations(self) -> dict[str, PETCAllocation]:
        return dict(self._allocations)
```

### Acceptance Criteria

- `PETCAllocator.allocate()` returns unique prime sequences per session
- No prime is allocated to more than one session (`verify_global_ordering()` confirms)
- `tag_audit_chain()` pairs each audit event with its prime index
- `petc_invariants()` validates all allocated sequences
- Allocation is idempotent (calling `allocate()` twice with same session ID returns same result)
- Zero external dependencies beyond stdlib

### Estimated Size

~150 LOC.

***

## Execution Sequence

```
Tier 6 ──► Tier 7
              │
    ┌─────────┼──────────┐
    ▼         ▼          ▼
  #36 CSL   #38 Spec   #41 PETC
  Operators  Governor   Bridge
    │                    │
    ▼                    │
  #37 CSL               │
  Gate                   │
    │         ┌──────────┘
    └────┬────┘
         ▼
    #39 Orchestrator
         │
         ▼
    #40 ΛProof Bridge
```

### Dependencies

| Issue | Depends On | Rationale |
|-------|-----------|-----------|
| #36 CSL Operators | Tier 1 (`StepInfo` types) | Evaluates step metadata |
| #37 CSL Gate | #36 + Tier 6 #31 (`EmissionGate`) | Composes CSL with contraction gate |
| #38 Spectral Governor | PIRTM `spectral_decomp.py` | Extends spectral analysis with governance |
| #39 Orchestrator | Tier 6 #34 (`QARISession`) + Tier 6 #33 (`AuditChain`) | Manages multiple sessions |
| #40 ΛProof Bridge | Tier 6 #33 (`AuditChain`) | Translates audit events |
| #41 PETC Bridge | PIRTM `petc.py` + Tier 6 #33 (`AuditChain`) | Prime-indexes audit events |

Issues #36, #38, and #41 are parallel (no mutual dependencies). Issue #37 follows #36. Issue #39 follows #37 + #38. Issue #40 follows #39.

### Estimated Effort

| Issue | Deliverable | LOC (approx) | Time |
|-------|-------------|-------------|------|
| #36 — CSL Operators | `csl.py` + tests | ~250 | 3-4 hours |
| #37 — CSL Gate | `csl_gate.py` + tests | ~150 | 2-3 hours |
| #38 — Spectral Governor | `spectral_gov.py` + tests | ~200 | 3-4 hours |
| #39 — Orchestrator | `orchestrator.py` + tests | ~300 | 4-5 hours |
| #40 — ΛProof Bridge | `lambda_bridge.py` + tests | ~200 | 3-4 hours |
| #41 — PETC Bridge | `petc_bridge.py` + tests | ~150 | 2-3 hours |

**Total: ~1,250 LOC, 6 issues, 17-23 hours of implementation.**

***

## Post-Tier 7 State

After Tier 7, PIRTM becomes a protocol-layer participant in the Multiplicity Theory ecosystem:

- **CSL Compliance**: Every step is evaluated against the Conscious Sovereignty Layer's Neutrality, Beneficence, Silence, and Commutation operators. Silence produces a true NO-OP — not suppression, but non-occurrence.
- **Spectral Governance**: The operator norm and epsilon are no longer static parameters but dynamically governed by spectral analysis of the recurrence operator. The Spectral Governor feeds eigenvalue data into QARISession configuration.
- **Multi-Session Federation**: An orchestrator manages concurrent sessions with certificate aggregation, session pause/resume via serializable snapshots, and a master audit chain that links all sessions.
- **ΛProof Integration**: Audit events are translated to Lambda-Proof Λ-trace format with EAS schema mapping, batch Merkle roots, and capability-token-scoped submission.
- **PETC Ordering**: Sessions are assigned non-colliding prime-indexed event sequences, providing a deterministic global ordering compatible with the PETC invariant module.

### Full Tier Chain

```
Tier 1 (installable)
  → Tier 2 (complete API)
    → Tier 3 (property tests)
      → Tier 4 (documentation)
        → Tier 5 (governance + CI)
          → Tier 6 (emission gating + telemetry + Q-ARI)
            → Tier 7 (CSL operators + spectral governance
                      + orchestration + ΛProof bridge)
```

The package now operates both as a standalone numerical engine and as a governed, CSL-compliant, spectrally-monitored, multi-session-capable participant in the Lambda-Proof verifiable trust ecosystem.