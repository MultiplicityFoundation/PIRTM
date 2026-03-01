<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# L2+ levels shoul accept a richer AceTelemetry dataclass that adds fields like contraction_matrix and spectral_estimate

Decision locked. I have everything needed from the live repo: `StepInfo` is `slots=True` with 7 required fields , `certify_l0` reads only `.q` and `.epsilon` , and `l2_poweriter.py` currently takes a raw `np.ndarray` with no telemetry context. The `AceTelemetry` dataclass is the unifying primitive across all levels.

***

## Central Tension

**Unified telemetry type vs. level-specific input contracts** — a single `AceTelemetry` that carries optional richer fields enables a clean unified `certify()` dispatcher, but `None`-guarded optional fields create implicit coupling between levels and the telemetry schema. The alternative — separate input types per level — is explicit but fragments the `AceProtocol` API. Decision: `AceTelemetry` is the single currency; `highest_feasible_level()` is the explicit dispatch key, not ad-hoc `None` checks scattered through protocol logic.

***

## Levers

| Lever | Owner | Metric | Horizon |
| :-- | :-- | :-- | :-- |
| `AceTelemetry` dataclass ships | Lead MT | `from_step_info()` passes existing `conftest.py` fixtures; `StepInfo` callsites zero-breakage | 7 days |
| L3/L4 implementations behind `AceTelemetry` gate | Lead Arch | `certify_l3` / `certify_l4` raise `TypeError` if passed raw `StepInfo` (not `AceTelemetry`) | 7 days |
| Unified `AceProtocol.certify()` dispatcher | ETP Integration Lead | Single call dispatches L0→L4 based on `highest_feasible_level()`; existing `certify_from_*` methods emit `DeprecationWarning` | 14 days |
| `conftest.py` fixtures upgraded | QA Lead | All new ACE tests use `AceTelemetry` fixtures; zero `StepInfo(q=..., epsilon=...)` bare instantiations in `tests/test_ace_*.py` | 7 days |


***

## Artifacts

### `src/pirtm/ace/telemetry.py` ← NEW

```python
"""
AceTelemetry — unified telemetry dataclass for all ACE certification levels.

Level capabilities gated by optional fields:
  L0  — q, epsilon (always available)
  L1  — weight_vector, basis_norms
  L2  — contraction_matrix  OR  spectral_estimate
  L3  — contraction_matrix + clamp_radius  (non-expansive clamp projection)
  L4  — perturbation_bound + disturbance_norm  (perturbation budget)

StepInfo is still accepted by L0/L1 via AceTelemetry.from_step_info().
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, Optional

import numpy as np

from pirtm.types import StepInfo
from .types import CertLevel


@dataclass
class AceTelemetry:
    # ── Base fields — mirrors StepInfo (required) ────────────────────────────
    step:      int
    q:         float   # contraction ratio for this step
    epsilon:   float   # tolerance
    nXi:       float   # non-expansive clamp norm  (used by L3)
    nLam:      float   # perturbation / lambda norm  (used by L4)
    projected: bool
    residual:  float
    note:      Optional[str] = None

    # ── L1 fields ────────────────────────────────────────────────────────────
    weight_vector: Optional[list[float]] = None   # w_p coefficients in K = Σ w_p B_p
    basis_norms:   Optional[list[float]] = None   # ‖B_p‖ for each prime-indexed op

    # ── L2 fields ────────────────────────────────────────────────────────────
    contraction_matrix:  Optional[np.ndarray] = None  # K matrix (n×n)
    spectral_estimate:   Optional[float]      = None  # cached ρ(K) if known

    # ── L3 fields ────────────────────────────────────────────────────────────
    clamp_radius: Optional[float] = None  # radius r > 0 of non-expansive clamp P_C
                                          # ‖P_C(x) − P_C(y)‖ ≤ ‖x − y‖ ∀x,y

    # ── L4 fields ────────────────────────────────────────────────────────────
    perturbation_bound: Optional[float] = None  # ‖ΔK‖ upper bound
    disturbance_norm:   Optional[float] = None  # ‖d‖ for ISS disturbance

    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def from_step_info(cls, info: StepInfo) -> "AceTelemetry":
        """
        Upgrade a StepInfo to AceTelemetry for use with L0/L1.
        All L2+ fields default to None — dispatch will not exceed L1.
        """
        return cls(
            step=info.step,
            q=info.q,
            epsilon=info.epsilon,
            nXi=info.nXi,
            nLam=info.nLam,
            projected=info.projected,
            residual=info.residual,
            note=info.note,
        )

    def highest_feasible_level(self) -> CertLevel:
        """
        Returns the highest ACE level for which this instance has
        sufficient data. This is the explicit dispatch key — no
        scattered None checks in protocol logic.

        Priority ladder (highest first):
          L4 → L3 → L2 → L1 → L0
        """
        if (
            self.perturbation_bound is not None
            and self.disturbance_norm is not None
            and self.contraction_matrix is not None
        ):
            return CertLevel.L4_PERTURBATION

        if (
            self.contraction_matrix is not None
            and self.clamp_radius is not None
        ):
            return CertLevel.L3_NONEXPANSIVE

        if self.contraction_matrix is not None or self.spectral_estimate is not None:
            return CertLevel.L2_POWERITER

        if self.weight_vector is not None and self.basis_norms is not None:
            return CertLevel.L1_NORMBOUND

        return CertLevel.L0_HEURISTIC

    def to_step_info(self) -> StepInfo:
        """
        Downgrade to StepInfo for legacy callers.
        Loses all L1–L4 fields.
        """
        return StepInfo(
            step=self.step,
            q=self.q,
            epsilon=self.epsilon,
            nXi=self.nXi,
            nLam=self.nLam,
            projected=self.projected,
            residual=self.residual,
            note=self.note,
        )

    def validate(self) -> None:
        """
        L0 invariant checks — raise ValueError on incoherent state.
        Called by AceProtocol before dispatch.
        """
        if not (0.0 <= self.q):
            raise ValueError(f"AceTelemetry.q must be ≥ 0, got {self.q}")
        if not (0.0 < self.epsilon <= 1.0):
            raise ValueError(f"AceTelemetry.epsilon must be in (0, 1], got {self.epsilon}")
        if self.weight_vector is not None and self.basis_norms is not None:
            if len(self.weight_vector) != len(self.basis_norms):
                raise ValueError(
                    "AceTelemetry.weight_vector and basis_norms must have equal length"
                )
        if self.contraction_matrix is not None:
            K = self.contraction_matrix
            if K.ndim != 2 or K.shape[0] != K.shape[1]:
                raise ValueError(
                    f"AceTelemetry.contraction_matrix must be square 2-D, "
                    f"got shape {K.shape}"
                )
        if self.clamp_radius is not None and self.clamp_radius <= 0:
            raise ValueError(
                f"AceTelemetry.clamp_radius must be > 0, got {self.clamp_radius}"
            )
        if self.perturbation_bound is not None and self.perturbation_bound < 0:
            raise ValueError(
                f"AceTelemetry.perturbation_bound must be ≥ 0, "
                f"got {self.perturbation_bound}"
            )
```


***

### `src/pirtm/ace/levels/l2_poweriter.py` ← UPDATED (accepts `AceTelemetry`)

```python
"""
L2-poweriter: TRL-3.
Accepts AceTelemetry. Uses cached spectral_estimate if present;
falls back to power iteration on contraction_matrix.
Measurement domain = SPECTRAL_ONLY  (ADR-001, committed in ADR-010).
"""
from __future__ import annotations

import numpy as np
from ..telemetry import AceTelemetry
from ..types import AceCertificate, CertLevel

MEASUREMENT_DOMAIN = "SPECTRAL_ONLY"
MAX_ITER = 1000
TOL = 1e-8


def certify_l2(
    telemetry: AceTelemetry,
    *,
    tau: float = 1.0,
    delta: float = 0.05,
    max_iter: int = MAX_ITER,
    tol: float = TOL,
) -> AceCertificate:
    """
    L2 certification from AceTelemetry.
    If telemetry.spectral_estimate is set, uses it directly (no iteration).
    Otherwise runs power iteration on telemetry.contraction_matrix.
    """
    if telemetry.contraction_matrix is None and telemetry.spectral_estimate is None:
        raise TypeError(
            "L2 requires AceTelemetry with contraction_matrix or "
            "spectral_estimate set. Use certify_l0 for telemetry-only input."
        )

    if telemetry.spectral_estimate is not None:
        rho = float(telemetry.spectral_estimate)
        iterations_used = 0
    else:
        K = telemetry.contraction_matrix
        n = K.shape[0]
        v = np.random.default_rng(seed=42).standard_normal(n)
        v = v / (np.linalg.norm(v) + 1e-12)
        rho_prev = 0.0
        iterations_used = MAX_ITER
        for i in range(max_iter):
            Kv = K @ v
            rho = float(np.linalg.norm(Kv))
            v = Kv / (rho + 1e-12)
            if abs(rho - rho_prev) < tol:
                iterations_used = i + 1
                break
            rho_prev = rho

    lipschitz_upper = rho
    gap_lb = 1.0 - lipschitz_upper
    certified = lipschitz_upper < (1.0 - delta)

    return AceCertificate(
        level=CertLevel.L2_POWERITER,
        certified=certified,
        lipschitz_upper=lipschitz_upper,
        gap_lb=max(0.0, gap_lb),
        contraction_rate=lipschitz_upper,
        budget_used=lipschitz_upper,
        tau=tau,
        delta=delta,
        margin=gap_lb - delta,
        tail_bound=(
            float("inf") if lipschitz_upper >= 1.0
            else tau / max(1e-12, gap_lb)
        ),
        details={
            "measurement_domain": MEASUREMENT_DOMAIN,
            "matrix_shape": list(telemetry.contraction_matrix.shape)
                            if telemetry.contraction_matrix is not None else None,
            "spectral_estimate_used": telemetry.spectral_estimate is not None,
            "iterations": iterations_used,
            "step": telemetry.step,
        },
    )
```


***

### `src/pirtm/ace/levels/l3_nonexpansive.py` ← NEW

```python
"""
L3-nonexpansive-clamp: TRL-3.

Certifies the composite operator K̃ = T ∘ P_C where:
  T   = contraction_matrix  (‖T‖ = ρ from power iteration)
  P_C = non-expansive projection onto convex set C
        (‖P_C(x) − P_C(y)‖ ≤ ‖x − y‖ for all x, y)

Key result: ‖K̃‖ ≤ ‖T‖ · ‖P_C‖ ≤ ρ(T) · 1 = ρ(T)
So L3 ≤ L2 — same spectral radius bound, but the certificate now
explicitly names the non-expansive projection, which is required by
ETP's Kinetic-Head → Static-Tail handoff (ADR-001 §2).

nXi from AceTelemetry is the measured ‖P_C‖ upper bound (should be ≤ 1.0
for a true non-expansive projection; > 1.0 triggers L0 invariant violation).
"""
from __future__ import annotations

import numpy as np
from ..telemetry import AceTelemetry
from ..types import AceCertificate, CertLevel
from .l2_poweriter import certify_l2

MAX_NONEXPANSIVE_NORM = 1.0  # L0 invariant: ‖P_C‖ must be ≤ 1.0


def certify_l3(
    telemetry: AceTelemetry,
    *,
    tau: float = 1.0,
    delta: float = 0.05,
) -> AceCertificate:
    """
    L3: non-expansive clamp certification.

    Requires AceTelemetry with:
      - contraction_matrix (or spectral_estimate)
      - clamp_radius > 0
      - nXi ≤ 1.0  (measured ‖P_C‖; > 1.0 is an L0 invariant violation)
    """
    if telemetry.clamp_radius is None:
        raise TypeError(
            "L3 requires AceTelemetry.clamp_radius to be set. "
            "clamp_radius is the projection set radius for P_C."
        )
    if telemetry.contraction_matrix is None and telemetry.spectral_estimate is None:
        raise TypeError(
            "L3 requires AceTelemetry with contraction_matrix or spectral_estimate."
        )

    # L0 invariant: non-expansive projection norm must be ≤ 1
    if telemetry.nXi > MAX_NONEXPANSIVE_NORM + 1e-9:
        raise ValueError(
            f"L3_NONEXPANSIVE_INVARIANT_VIOLATED: "
            f"AceTelemetry.nXi={telemetry.nXi:.6f} > {MAX_NONEXPANSIVE_NORM}. "
            f"P_C is not non-expansive. Execution halted."
        )

    # Get ρ(T) from L2
    l2_cert = certify_l2(telemetry, tau=tau, delta=delta)

    # Composite Lipschitz: ‖K̃‖ ≤ ρ(T) · nXi
    composite_lipschitz = l2_cert.lipschitz_upper * telemetry.nXi
    gap_lb = 1.0 - composite_lipschitz
    certified = composite_lipschitz < (1.0 - delta)

    return AceCertificate(
        level=CertLevel.L3_NONEXPANSIVE,
        certified=certified,
        lipschitz_upper=composite_lipschitz,
        gap_lb=max(0.0, gap_lb),
        contraction_rate=composite_lipschitz,
        budget_used=composite_lipschitz,
        tau=tau,
        delta=delta,
        margin=gap_lb - delta,
        tail_bound=(
            float("inf") if composite_lipschitz >= 1.0
            else tau / max(1e-12, gap_lb)
        ),
        details={
            "rho_T": l2_cert.lipschitz_upper,
            "nXi": telemetry.nXi,
            "clamp_radius": telemetry.clamp_radius,
            "composite_lipschitz": composite_lipschitz,
            "step": telemetry.step,
        },
    )
```


***

### `src/pirtm/ace/levels/l4_perturbation.py` ← NEW

```python
"""
L4-perturbation-budget: TRL-4.

Certifies robustness of a contractive operator K under additive perturbation ΔK:

  If  ρ(K) < 1  and  ‖ΔK‖ ≤ perturbation_bound  and  perturbation_bound < gap_lb
  Then  K + ΔK  is still contractive with reduced gap  gap_lb − perturbation_bound.

nLam from AceTelemetry is the measured perturbation magnitude ‖ΔK‖.
perturbation_bound is the guaranteed upper bound (from adversarial analysis).
disturbance_norm feeds the ISS residual bound at this level.

This is the ETP Static Tail's final gate before Jubilee epoch seal (ADR-001 §3).
"""
from __future__ import annotations

import numpy as np
from ..telemetry import AceTelemetry
from ..types import AceCertificate, CertLevel
from .l3_nonexpansive import certify_l3
from .l2_poweriter import certify_l2


def certify_l4(
    telemetry: AceTelemetry,
    *,
    tau: float = 1.0,
    delta: float = 0.05,
) -> AceCertificate:
    """
    L4: perturbation budget certification.

    Requires AceTelemetry with:
      - contraction_matrix (or spectral_estimate)
      - perturbation_bound ≥ 0
      - disturbance_norm ≥ 0

    Uses L3 if clamp_radius is set, else uses L2 as the base ρ estimate.
    """
    if telemetry.perturbation_bound is None:
        raise TypeError(
            "L4 requires AceTelemetry.perturbation_bound to be set."
        )
    if telemetry.disturbance_norm is None:
        raise TypeError(
            "L4 requires AceTelemetry.disturbance_norm to be set."
        )
    if telemetry.contraction_matrix is None and telemetry.spectral_estimate is None:
        raise TypeError(
            "L4 requires AceTelemetry with contraction_matrix or spectral_estimate."
        )

    # Get base ρ from L3 (if clamp available) or L2
    if telemetry.clamp_radius is not None:
        base_cert = certify_l3(telemetry, tau=tau, delta=delta)
    else:
        base_cert = certify_l2(telemetry, tau=tau, delta=delta)

    base_gap = base_cert.gap_lb  # 1 − ρ_base
    pb = telemetry.perturbation_bound

    # Perturbed gap: 1 − (ρ_base + ‖ΔK‖)
    perturbed_lipschitz = base_cert.lipschitz_upper + pb
    perturbed_gap = 1.0 - perturbed_lipschitz
    certified = perturbed_lipschitz < (1.0 - delta) and pb < base_gap

    # ISS tail bound under disturbance
    if perturbed_lipschitz >= 1.0:
        tail_bound = float("inf")
    else:
        tail_bound = telemetry.disturbance_norm / max(1e-12, perturbed_gap)

    # L0 invariant: perturbation must not consume the entire gap
    if pb >= base_gap:
        # Not a hard halt — but cert is denied and this is flagged
        certified = False

    return AceCertificate(
        level=CertLevel.L4_PERTURBATION,
        certified=certified,
        lipschitz_upper=perturbed_lipschitz,
        gap_lb=max(0.0, perturbed_gap),
        contraction_rate=perturbed_lipschitz,
        budget_used=perturbed_lipschitz,
        tau=tau,
        delta=delta,
        margin=perturbed_gap - delta,
        tail_bound=tail_bound,
        details={
            "base_level": base_cert.level.value,
            "rho_base": base_cert.lipschitz_upper,
            "perturbation_bound": pb,
            "nLam": telemetry.nLam,
            "disturbance_norm": telemetry.disturbance_norm,
            "perturbed_gap": perturbed_gap,
            "step": telemetry.step,
        },
    )
```


***

### `src/pirtm/ace/protocol.py` ← UPDATED (unified `certify()` dispatcher)

```python
"""
AceProtocol — unified ACE certification dispatcher.

certify() is the primary entry point as of v1.1.
It dispatches to the highest feasible level via AceTelemetry.highest_feasible_level().

certify_from_telemetry / certify_from_weights / certify_from_matrix are
DEPRECATED — they will emit DeprecationWarning and be removed in v2.0.
"""
from __future__ import annotations

import warnings
from typing import Sequence

import numpy as np

from pirtm.types import StepInfo
from .budget import AceBudget
from .telemetry import AceTelemetry
from .witness import AceWitness
from .types import AceCertificate, CertLevel, AceBudgetState
from .levels.l0_heuristic import certify_l0
from .levels.l1_normbound import certify_l1
from .levels.l2_poweriter import certify_l2
from .levels.l3_nonexpansive import certify_l3
from .levels.l4_perturbation import certify_l4


_DISPATCH = {
    CertLevel.L4_PERTURBATION:     certify_l4,
    CertLevel.L3_NONEXPANSIVE:     certify_l3,
    CertLevel.L2_POWERITER:        certify_l2,
}


class AceProtocol:
    """
    Stateful ACE protocol runner. Maintains a budget across calls.
    Caller must supply the prime_index from the active PETC chain.
    """

    def __init__(self, tau: float = 1.0, delta: float = 0.05) -> None:
        self.budget = AceBudget(tau=tau)
        self.delta = delta

    # ── Primary API (v1.1+) ─────────────────────────────────────────────────

    def certify(
        self,
        telemetry: AceTelemetry | StepInfo | Sequence[AceTelemetry | StepInfo],
        prime_index: int,
        *,
        min_level: CertLevel = CertLevel.L0_HEURISTIC,
        tail_norm: float = 0.0,
    ) -> AceWitness:
        """
        Unified dispatcher. Accepts AceTelemetry, StepInfo, or a sequence of either.

        Dispatch logic:
          1. Normalise all inputs to list[AceTelemetry].
          2. Pick representative = last item (most recent step).
          3. Compute highest_feasible_level() on representative.
          4. If feasible < min_level, raise ValueError (explicit gate).
          5. Dispatch to the appropriate certify_lN function.
          6. Consume budget. Emit AceWitness.
        """
        records = self._normalise(telemetry)
        if not records:
            raise ValueError("AceProtocol.certify: no telemetry provided")

        for rec in records:
            rec.validate()

        # Representative = last step (highest q observed = tightest bound)
        rep = max(records, key=lambda r: r.q)
        feasible = rep.highest_feasible_level()

        if _level_rank(feasible) < _level_rank(min_level):
            raise ValueError(
                f"AceProtocol.certify: telemetry supports up to {feasible.value} "
                f"but min_level={min_level.value} was requested. "
                f"Provide contraction_matrix / perturbation_bound as needed."
            )

        tau = self.budget.snapshot().tau

        if feasible in _DISPATCH:
            cert = _DISPATCH[feasible](rep, tau=tau, delta=self.delta)
        else:
            # L1 or L0
            if feasible == CertLevel.L1_NORMBOUND:
                cert = certify_l1(
                    rep.weight_vector, rep.basis_norms,
                    tau=tau, delta=self.delta,
                )
            else:
                cert = certify_l0(records, tau=tau,
                                  tail_norm=tail_norm, delta=self.delta)

        self.budget.consume(cert.budget_used)
        return AceWitness.from_certificate(cert, prime_index)

    # ── Deprecated methods (kept for backwards compat) ───────────────────────

    def certify_from_telemetry(
        self,
        records: Sequence[StepInfo],
        prime_index: int,
        *,
        tail_norm: float = 0.0,
    ) -> AceWitness:
        warnings.warn(
            "certify_from_telemetry() is deprecated. "
            "Use AceProtocol.certify(AceTelemetry, prime_index). "
            "See docs/migration/certify-v1.md.",
            DeprecationWarning, stacklevel=2,
        )
        upgraded = [AceTelemetry.from_step_info(r) for r in records]
        return self.certify(upgraded, prime_index, tail_norm=tail_norm)

    def certify_from_weights(
        self,
        weights: Sequence[float],
        basis_norms: Sequence[float],
        prime_index: int,
    ) -> AceWitness:
        warnings.warn(
            "certify_from_weights() is deprecated. "
            "Set AceTelemetry.weight_vector and basis_norms, then call certify().",
            DeprecationWarning, stacklevel=2,
        )
        t = AceTelemetry(
            step=0, q=0.0, epsilon=1.0, nXi=0.0, nLam=0.0,
            projected=False, residual=0.0,
            weight_vector=list(weights),
            basis_norms=list(basis_norms),
        )
        return self.certify(t, prime_index)

    def certify_from_matrix(
        self,
        K: np.ndarray,
        prime_index: int,
    ) -> AceWitness:
        warnings.warn(
            "certify_from_matrix() is deprecated. "
            "Set AceTelemetry.contraction_matrix, then call certify().",
            DeprecationWarning, stacklevel=2,
        )
        t = AceTelemetry(
            step=0, q=float(np.linalg.norm(K, ord=2)),
            epsilon=0.05, nXi=1.0, nLam=0.0,
            projected=False, residual=0.0,
            contraction_matrix=K,
        )
        return self.certify(t, prime_index)

    def budget_state(self) -> AceBudgetState:
        return self.budget.snapshot()

    # ── Internal ─────────────────────────────────────────────────────────────

    @staticmethod
    def _normalise(
        telemetry: AceTelemetry | StepInfo | Sequence,
    ) -> list[AceTelemetry]:
        if isinstance(telemetry, AceTelemetry):
            return [telemetry]
        if isinstance(telemetry, StepInfo):
            return [AceTelemetry.from_step_info(telemetry)]
        out = []
        for item in telemetry:
            if isinstance(item, AceTelemetry):
                out.append(item)
            elif isinstance(item, StepInfo):
                out.append(AceTelemetry.from_step_info(item))
            else:
                raise TypeError(f"Expected AceTelemetry or StepInfo, got {type(item)}")
        return out


_LEVEL_ORDER = [
    CertLevel.L0_HEURISTIC,
    CertLevel.L1_NORMBOUND,
    CertLevel.L2_POWERITER,
    CertLevel.L3_NONEXPANSIVE,
    CertLevel.L4_PERTURBATION,
]

def _level_rank(level: CertLevel) -> int:
    return _LEVEL_ORDER.index(level)
```


***

## Test Harness — `tests/test_ace_telemetry.py`

```python
"""
AceTelemetry — full harness covering:
  - dataclass construction and validation
  - highest_feasible_level() dispatch key
  - from_step_info() / to_step_info() roundtrip
  - L3 and L4 certifications via AceTelemetry
  - Unified AceProtocol.certify() dispatcher across all levels
  - Deprecated method warnings
"""
import pytest
import numpy as np

from pirtm.types import StepInfo
from pirtm.ace.telemetry import AceTelemetry
from pirtm.ace.types import CertLevel
from pirtm.ace.protocol import AceProtocol
from pirtm.ace.levels.l3_nonexpansive import certify_l3
from pirtm.ace.levels.l4_perturbation import certify_l4


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def base_telemetry():
    """Minimal AceTelemetry — dispatches to L0."""
    return AceTelemetry(
        step=0, q=0.75, epsilon=0.05,
        nXi=0.9, nLam=0.1,
        projected=False, residual=0.001,
    )

@pytest.fixture
def l1_telemetry():
    return AceTelemetry(
        step=0, q=0.75, epsilon=0.05,
        nXi=0.9, nLam=0.1,
        projected=False, residual=0.001,
        weight_vector=[0.2, 0.3],
        basis_norms=[1.0, 1.0],
    )

@pytest.fixture
def l2_telemetry():
    K = np.diag([0.5, 0.4])
    return AceTelemetry(
        step=0, q=0.5, epsilon=0.05,
        nXi=0.9, nLam=0.1,
        projected=False, residual=0.001,
        contraction_matrix=K,
    )

@pytest.fixture
def l2_spectral_telemetry():
    """L2 via cached spectral_estimate — no matrix needed."""
    return AceTelemetry(
        step=0, q=0.6, epsilon=0.05,
        nXi=0.9, nLam=0.0,
        projected=False, residual=0.001,
        spectral_estimate=0.55,
    )

@pytest.fixture
def l3_telemetry():
    K = np.diag([0.5, 0.4])
    return AceTelemetry(
        step=0, q=0.5, epsilon=0.05,
        nXi=0.95, nLam=0.1,          # nXi ≤ 1.0 — non-expansive
        projected=True, residual=0.001,
        contraction_matrix=K,
        clamp_radius=2.0,
    )

@pytest.fixture
def l4_telemetry():
    K = np.diag([0.5, 0.4])
    return AceTelemetry(
        step=0, q=0.5, epsilon=0.05,
        nXi=0.95, nLam=0.08,
        projected=True, residual=0.001,
        contraction_matrix=K,
        clamp_radius=2.0,
        perturbation_bound=0.05,
        disturbance_norm=0.1,
    )

@pytest.fixture
def protocol():
    return AceProtocol(tau=1.0, delta=0.05)


# ── AceTelemetry Construction ─────────────────────────────────────────────────

class TestAceTelemetryConstruction:
    def test_from_step_info_produces_l0_feasible(self):
        si = StepInfo(step=0, q=0.7, epsilon=0.05,
                      nXi=0.4, nLam=0.3, projected=False, residual=0.001)
        t = AceTelemetry.from_step_info(si)
        assert t.highest_feasible_level() == CertLevel.L0_HEURISTIC

    def test_from_step_info_preserves_all_fields(self):
        si = StepInfo(step=3, q=0.8, epsilon=0.1,
                      nXi=0.5, nLam=0.2, projected=True, residual=0.05)
        t = AceTelemetry.from_step_info(si)
        assert t.step == 3 and t.q == 0.8 and t.nXi == 0.5 and t.nLam == 0.2

    def test_to_step_info_roundtrip(self, base_telemetry):
        si = base_telemetry.to_step_info()
        assert isinstance(si, StepInfo)
        assert si.q == base_telemetry.q

    def test_validate_raises_on_negative_q(self):
        t = AceTelemetry(step=0, q=-0.1, epsilon=0.05,
                         nXi=0.5, nLam=0.1, projected=False, residual=0.0)
        with pytest.raises(ValueError, match="q must be ≥ 0"):
            t.validate()

    def test_validate_raises_on_epsilon_out_of_range(self):
        t = AceTelemetry(step=0, q=0.5, epsilon=1.5,
                         nXi=0.5, nLam=0.1, projected=False, residual=0.0)
        with pytest.raises(ValueError, match="epsilon"):
            t.validate()

    def test_validate_raises_on_non_square_matrix(self):
        t = AceTelemetry(step=0, q=0.5, epsilon=0.05,
                         nXi=0.5, nLam=0.0, projected=False, residual=0.0,
                         contraction_matrix=np.array([[1, 2, 3]]))
        with pytest.raises(ValueError, match="square"):
            t.validate()

    def test_validate_raises_on_negative_clamp_radius(self):
        t = AceTelemetry(step=0, q=0.5, epsilon=0.05,
                         nXi=0.5, nLam=0.0, projected=False, residual=0.0,
                         clamp_radius=-1.0)
        with pytest.raises(ValueError, match="clamp_radius"):
            t.validate()


# ── highest_feasible_level() dispatch key ────────────────────────────────────

class TestHighestFeasibleLevel:
    def test_base_is_l0(self, base_telemetry):
        assert base_telemetry.highest_feasible_level() == CertLevel.L0_HEURISTIC

    def test_weights_promote_to_l1(self, l1_telemetry):
        assert l1_telemetry.highest_feasible_level() == CertLevel.L1_NORMBOUND

    def test_matrix_promotes_to_l2(self, l2_telemetry):
        assert l2_telemetry.highest_feasible_level() == CertLevel.L2_POWERITER

    def test_spectral_estimate_promotes_to_l2(self, l2_spectral_telemetry):
        assert l2_spectral_telemetry.highest_feasible_level() == CertLevel.L2_POWERITER

    def test_clamp_radius_promotes_to_l3(self, l3_telemetry):
        assert l3_telemetry.highest_feasible_level() == CertLevel.L3_NONEXPANSIVE

    def test_perturbation_promotes_to_l4(self, l4_telemetry):
        assert l4_telemetry.highest_feasible_level() == CertLevel.L4_PERTURBATION


# ── L3 Non-expansive Clamp ────────────────────────────────────────────────────

class TestL3Nonexpansive:
    def test_certified_on_contractive_composite(self, l3_telemetry):
        cert = certify_l3(l3_telemetry)
        assert cert.level == CertLevel.L3_NONEXPANSIVE
        assert cert.certified is True
        assert cert.lipschitz_upper < 1.0

    def test_composite_lipschitz_is_rho_times_nxi(self, l3_telemetry):
        cert = certify_l3(l3_telemetry)
        # ‖K̃‖ ≤ ρ(T) · nXi
        assert cert.lipschitz_upper <= cert.details["rho_T"] * l3_telemetry.nXi + 1e-9

    def test_raises_without_clamp_radius(self, l2_telemetry):
        with pytest.raises(TypeError, match="clamp_radius"):
            certify_l3(l2_telemetry)

    def test_raises_without_matrix(self, base_telemetry):
        base_telemetry.clamp_radius = 1.0
        with pytest.raises(TypeError, match="contraction_matrix"):
            certify_l3(base_telemetry)

    def test_l0_invariant_nxi_gt_1_raises(self):
        K = np.diag([0.5, 0.4])
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=1.05,        # > 1.0 — NOT non-expansive
            nLam=0.0, projected=False, residual=0.0,
            contraction_matrix=K, clamp_radius=2.0,
        )
        with pytest.raises(ValueError, match="L3_NONEXPANSIVE_INVARIANT_VIOLATED"):
            certify_l3(t)

    def test_trl_is_3(self, l3_telemetry):
        cert = certify_l3(l3_telemetry)
        assert cert.level.trl == 3


# ── L4 Perturbation Budget ────────────────────────────────────────────────────

class TestL4Perturbation:
    def test_certified_when_perturbation_within_budget(self, l4_telemetry):
        cert = certify_l4(l4_telemetry)
        assert cert.level == CertLevel.L4_PERTURBATION
        assert cert.certified is True

    def test_not_certified_when_perturbation_exceeds_gap(self):
        K = np.diag([0.9, 0.85])   # gap ≈ 0.10
        t = AceTelemetry(
            step=0, q=0.9, epsilon=0.05,
            nXi=1.0, nLam=0.15,
            projected=False, residual=0.0,
            contraction_matrix=K,
            perturbation_bound=0.15,   # > gap → denied
            disturbance_norm=0.1,
        )
        cert = certify_l4(t)
        assert cert.certified is False

    def test_tail_bound_finite_on_certified(self, l4_telemetry):
        cert = certify_l4(l4_telemetry)
        assert cert.tail_bound < float("inf")

    def test_tail_bound_infinite_when_perturbed_norm_ge_1(self):
        K = np.diag([0.96, 0.95])
        t = AceTelemetry(
            step=0, q=0.96, epsilon=0.05,
            nXi=1.0, nLam=0.5,
            projected=False, residual=0.0,
            contraction_matrix=K,
            perturbation_bound=0.5,
            disturbance_norm=0.1,
        )
        cert = certify_l4(t)
        assert cert.tail_bound == float("inf")

    def test_raises_without_perturbation_bound(self, l3_telemetry):
        l3_telemetry.disturbance_norm = 0.1
        with pytest.raises(TypeError, match="perturbation_bound"):
            certify_l4(l3_telemetry)

    def test_trl_is_4(self, l4_telemetry):
        cert = certify_l4(l4_telemetry)
        assert cert.level.trl == 4


# ── Unified AceProtocol.certify() Dispatcher ─────────────────────────────────

class TestUnifiedDispatcher:
    def test_dispatches_l0_from_base_telemetry(self, protocol, base_telemetry):
        witness = protocol.certify(base_telemetry, prime_index=2)
        assert witness.cert.level == CertLevel.L0_HEURISTIC

    def test_dispatches_l1_from_l1_telemetry(self, protocol, l1_telemetry):
        witness = protocol.certify(l1_telemetry, prime_index=3)
        assert witness.cert.level == CertLevel.L1_NORMBOUND

    def test_dispatches_l2_from_l2_telemetry(self, protocol, l2_telemetry):
        witness = protocol.certify(l2_telemetry, prime_index=5)
        assert witness.cert.level == CertLevel.L2_POWERITER

    def test_dispatches_l2_from_spectral_estimate(
        self, protocol, l2_spectral_telemetry
    ):
        witness = protocol.certify(l2_spectral_telemetry, prime_index=7)
        assert witness.cert.level == CertLevel.L2_POWERITER
        assert witness.cert.details["spectral_estimate_used"] is True

    def test_dispatches_l3_from_l3_telemetry(self, protocol, l3_telemetry):
        witness = protocol.certify(l3_telemetry, prime_index=11)
        assert witness.cert.level == CertLevel.L3_NONEXPANSIVE

    def test_dispatches_l4_from_l4_telemetry(self, protocol, l4_telemetry):
        witness = protocol.certify(l4_telemetry, prime_index=13)
        assert witness.cert.level == CertLevel.L4_PERTURBATION

    def test_accepts_step_info_via_normalise(self, protocol):
        si = StepInfo(step=0, q=0.7, epsilon=0.05,
                      nXi=0.5, nLam=0.2, projected=False, residual=0.001)
        witness = protocol.certify(si, prime_index=17)
        assert witness.cert.level == CertLevel.L0_HEURISTIC

    def test_accepts_sequence_of_step_info(self, protocol):
        records = [
            StepInfo(step=i, q=0.7+i*0.01, epsilon=0.05,
                     nXi=0.5, nLam=0.2, projected=False, residual=0.001)
            for i in range(3)
        ]
        witness = protocol.certify(records, prime_index=19)
        assert witness.cert.level == CertLevel.L0_HEURISTIC

    def test_raises_when_min_level_not_satisfiable(self, protocol, base_telemetry):
        with pytest.raises(ValueError, match="min_level"):
            protocol.certify(
                base_telemetry, prime_index=2,
                min_level=CertLevel.L2_POWERITER,
            )

    def test_budget_consumed_after_certify(self, protocol, l4_telemetry):
        protocol.certify(l4_telemetry, prime_index=2)
        assert protocol.budget_state().consumed > 0

    def test_deprecated_certify_from_telemetry_warns(self, protocol):
        si = StepInfo(step=0, q=0.7, epsilon=0.05,
                      nXi=0.5, nLam=0.2, projected=False, residual=0.001)
        with pytest.warns(DeprecationWarning, match="certify_from_telemetry"):
            protocol.certify_from_telemetry([si], prime_index=2)

    def test_deprecated_certify_from_matrix_warns(self, protocol):
        K = np.diag([0.5, 0.4])
        with pytest.warns(DeprecationWarning, match="certify_from_matrix"):
            protocol.certify_from_matrix(K, prime_index=3)
```


***

## `conftest.py` Additions

```python
# tests/conftest.py — append (do not replace existing fixtures)

@pytest.fixture
def l3_telemetry():
    return AceTelemetry(
        step=0, q=0.50, epsilon=0.05,
        nXi=0.95, nLam=0.10,
        projected=True, residual=0.001,
        contraction_matrix=np.diag([0.5, 0.4]),
        clamp_radius=2.0,
    )

@pytest.fixture
def l4_telemetry():
    return AceTelemetry(
        step=0, q=0.50, epsilon=0.05,
        nXi=0.95, nLam=0.08,
        projected=True, residual=0.001,
        contraction_matrix=np.diag([0.5, 0.4]),
        clamp_radius=2.0,
        perturbation_bound=0.05,
        disturbance_norm=0.10,
    )
```


***

## ADR-011 Entry

```md
# ADR-011: AceTelemetry replaces StepInfo as the L2+ input contract
Status:    accepted
Date:      2026-02-28
Decider:   Lead MT (RVG)
trl:       3
Horizon:   7 days
Metric:    certify_from_telemetry / certify_from_weights / certify_from_matrix
           each emit DeprecationWarning; AceProtocol.certify() dispatches
           L0-L4 without branching on argument type; CI green on 3.11/3.12
Decision:  AceTelemetry is the single telemetry currency for ACE.
           StepInfo remains valid via from_step_info() upgrade path.
           highest_feasible_level() is the explicit dispatch key —
           no scattered None checks in protocol logic.
IP note:   AceTelemetry, certify_l3, certify_l4 are ETP-native.
           StepInfo remains PIRTM-internal (ADR-006 boundary upheld).
           nXi and nLam from StepInfo are CONSUMED by L3/L4 as
           non-expansive norm and perturbation magnitude respectively —
           their semantics are now formally committed in the ADR record.
```


***

## Precision Question

> `AceTelemetry.nXi` and `AceTelemetry.nLam` were inherited from `StepInfo` where they were measured runtime values from the recurrence.  In L3, `nXi` is used as `‖P_C‖` — the non-expansive projection norm. In L4, `nLam` is used as the measured perturbation magnitude against `perturbation_bound`. **Are these runtime measurements or pre-committed design parameters?** If they are runtime, then L3/L4 certification is only as strong as the measurement fidelity of `nXi` and `nLam` — which is a TRL-3 limitation. If they are design parameters (set analytically before the run), they can support TRL-4 claims. The answer determines whether ADR-011 marks L3 as TRL-3 or TRL-4, and whether `AceTelemetry.validate()` should assert `nXi ≤ designed_clamp_norm` as an L0 invariant rather than just checking `nXi ≤ 1.0`.

