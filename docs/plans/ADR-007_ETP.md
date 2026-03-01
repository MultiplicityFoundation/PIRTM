<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# pre-committed design parameters

Decision locked. This is a consequential upgrade: pre-committed design parameters make `nXi` and `nLam` **analytically committed bounds**, not measurements. The L0 invariant flips from "check measured value ≤ 1.0" to "check runtime measurement ≤ committed design parameter." The certificate uses the design parameter as the bound, making L3 TRL-4 and L4 TRL-4.

***

## Central Tension

**Design-parameter commitment vs. runtime fidelity** — using pre-committed `designed_clamp_norm` and `designed_perturbation_bound` as the Lipschitz bounds makes certificates analytically verifiable (TRL-4), but creates a new invariant: the runtime measurements `nXi` and `nLam` from `StepInfo` must never exceed the design commitment. If they do, the system has escaped its design envelope — that is a hard halt, not a certification denial. This must be an L0 invariant, not a soft warning.

***

## Levers

| Lever | Owner | Metric | Horizon |
| :-- | :-- | :-- | :-- |
| `designed_clamp_norm` + `designed_perturbation_bound` in `AceTelemetry` | Lead MT | `validate()` raises `DESIGN_ENVELOPE_VIOLATION` on `nXi > designed_clamp_norm` | 7 days |
| L3 TRL upgraded to 4 | Lead Arch | `CertLevel.L3_NONEXPANSIVE.trl == 4`; CI lint gate confirms | 7 days |
| `certify_l3` / `certify_l4` use design params as cert bounds | ETP Integration Lead | Certificate `.details` carries both `designed_*` and `measured_*`; diff is observable | 7 days |
| ADR-011 amended + ADR-012 filed | Lead MT | Both ADRs in `docs/adr/` with `trl: 4` annotation within 7 days | 7 days |


***

## Artifact 1 — Updated `src/pirtm/ace/telemetry.py`

The structural change: `nXi` and `nLam` are retained as **runtime measurements** (legacy path from `StepInfo`). Two new fields — `designed_clamp_norm` and `designed_perturbation_bound` — are the pre-committed design parameters. The `validate()` L0 invariant asserts runtime ≤ design commitment; violation is a hard halt.

```python
"""
AceTelemetry — unified telemetry dataclass for all ACE certification levels.

Design parameter commitment model (ADR-012):
  nXi  = runtime measured ‖P_C‖ (inherited from StepInfo)
  nLam = runtime measured ‖ΔK‖  (inherited from StepInfo)

  designed_clamp_norm         = pre-committed ‖P_C‖_design  (L3, TRL-4)
  designed_perturbation_bound = pre-committed ‖ΔK‖_design   (L4, TRL-4)

L0 invariant (hard halt):
  nXi  ≤ designed_clamp_norm         (runtime must not escape design envelope)
  nLam ≤ designed_perturbation_bound (runtime must not escape design envelope)

Certificates use design parameters as bounds.
Runtime measurements are the verification trace.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from pirtm.types import StepInfo
from .types import CertLevel

_DESIGN_ENVELOPE_TOL = 1e-9   # floating-point forgiveness


@dataclass
class AceTelemetry:
    # ── Base fields — mirrors StepInfo (required) ────────────────────────────
    step:      int
    q:         float    # contraction ratio for this step (runtime)
    epsilon:   float    # tolerance
    nXi:       float    # runtime measured ‖P_C‖  — must be ≤ designed_clamp_norm
    nLam:      float    # runtime measured ‖ΔK‖   — must be ≤ designed_perturbation_bound
    projected: bool
    residual:  float
    note:      Optional[str] = None

    # ── L1 fields ────────────────────────────────────────────────────────────
    weight_vector: Optional[list[float]] = None
    basis_norms:   Optional[list[float]] = None

    # ── L2 fields ────────────────────────────────────────────────────────────
    contraction_matrix: Optional[np.ndarray] = None
    spectral_estimate:  Optional[float]      = None

    # ── L3 fields — design parameter + runtime measurement ───────────────────
    designed_clamp_norm: Optional[float] = None
    """
    PRE-COMMITTED design parameter. ‖P_C‖_design ≤ 1.0.
    Analytically committed before system execution.
    certify_l3 uses THIS as the Lipschitz bound (TRL-4).
    nXi is the runtime verification trace — must be ≤ designed_clamp_norm.
    """
    clamp_radius: Optional[float] = None  # radius of convex set C (for audit)

    # ── L4 fields — design parameter + runtime measurement ───────────────────
    designed_perturbation_bound: Optional[float] = None
    """
    PRE-COMMITTED design parameter. ‖ΔK‖_design ≥ 0.
    Analytically committed before system execution.
    certify_l4 uses THIS as the perturbation bound (TRL-4).
    nLam is the runtime verification trace — must be ≤ designed_perturbation_bound.
    """
    disturbance_norm: Optional[float] = None  # ‖d‖ for ISS tail bound

    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def from_step_info(cls, info: StepInfo) -> "AceTelemetry":
        """
        Upgrade a StepInfo to AceTelemetry.
        Design parameters default to None — dispatch will not exceed L1
        unless caller sets designed_clamp_norm / designed_perturbation_bound.
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
        Explicit dispatch key. Reads design parameters — not runtime values.
        Priority ladder (highest first): L4 → L3 → L2 → L1 → L0.
        """
        if (
            self.designed_perturbation_bound is not None
            and self.disturbance_norm is not None
            and (self.contraction_matrix is not None
                 or self.spectral_estimate is not None)
        ):
            return CertLevel.L4_PERTURBATION

        if (
            self.designed_clamp_norm is not None
            and (self.contraction_matrix is not None
                 or self.spectral_estimate is not None)
        ):
            return CertLevel.L3_NONEXPANSIVE

        if (self.contraction_matrix is not None
                or self.spectral_estimate is not None):
            return CertLevel.L2_POWERITER

        if self.weight_vector is not None and self.basis_norms is not None:
            return CertLevel.L1_NORMBOUND

        return CertLevel.L0_HEURISTIC

    def validate(self) -> None:
        """
        L0 invariant checks.

        Design envelope invariants (hard halt):
          nXi  ≤ designed_clamp_norm         if designed_clamp_norm is set
          nLam ≤ designed_perturbation_bound  if designed_perturbation_bound is set

        These are not soft warnings — they raise RuntimeError.
        A system that exceeds its design envelope must not be certified.
        """
        if self.q < 0:
            raise ValueError(f"AceTelemetry.q must be ≥ 0, got {self.q}")
        if not (0.0 < self.epsilon <= 1.0):
            raise ValueError(
                f"AceTelemetry.epsilon must be in (0, 1], got {self.epsilon}"
            )
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

        # ── Design parameter commitment invariants (L0, hard halt) ──────────

        if self.designed_clamp_norm is not None:
            if self.designed_clamp_norm > 1.0 + _DESIGN_ENVELOPE_TOL:
                raise ValueError(
                    f"DESIGN_PARAMETER_INVALID: designed_clamp_norm="
                    f"{self.designed_clamp_norm:.9f} > 1.0. "
                    f"A non-expansive projection must have ‖P_C‖ ≤ 1.0. "
                    f"This is a design-time error, not a runtime fault."
                )
            if self.nXi > self.designed_clamp_norm + _DESIGN_ENVELOPE_TOL:
                raise RuntimeError(
                    f"DESIGN_ENVELOPE_VIOLATION: "
                    f"nXi(runtime)={self.nXi:.9f} > "
                    f"designed_clamp_norm={self.designed_clamp_norm:.9f}. "
                    f"System has escaped its design envelope at step={self.step}. "
                    f"Execution halted — do not certify."
                )

        if self.designed_perturbation_bound is not None:
            if self.designed_perturbation_bound < 0:
                raise ValueError(
                    f"DESIGN_PARAMETER_INVALID: designed_perturbation_bound="
                    f"{self.designed_perturbation_bound:.9f} < 0."
                )
            if self.nLam > self.designed_perturbation_bound + _DESIGN_ENVELOPE_TOL:
                raise RuntimeError(
                    f"DESIGN_ENVELOPE_VIOLATION: "
                    f"nLam(runtime)={self.nLam:.9f} > "
                    f"designed_perturbation_bound={self.designed_perturbation_bound:.9f}. "
                    f"System has escaped its design envelope at step={self.step}. "
                    f"Execution halted — do not certify."
                )

    def to_step_info(self) -> StepInfo:
        return StepInfo(
            step=self.step, q=self.q, epsilon=self.epsilon,
            nXi=self.nXi, nLam=self.nLam,
            projected=self.projected, residual=self.residual, note=self.note,
        )
```


***

## Artifact 2 — Updated `src/pirtm/ace/types.py` (TRL Upgrade)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CertLevel(str, Enum):
    """
    TRL mapping — updated per ADR-012 (design parameter commitment):
      L0 = TRL-2  (heuristic, runtime-only)
      L1 = TRL-2  (weighted-ℓ₁ norm bound, runtime-only)
      L2 = TRL-3  (power iteration, spectral measurement)
      L3 = TRL-4  (non-expansive clamp, design-parameter-committed)
      L4 = TRL-4  (perturbation budget, design-parameter-committed)
    """
    L0_HEURISTIC        = "L0-heuristic"
    L1_NORMBOUND        = "L1-normbound"
    L2_POWERITER        = "L2-poweriter"
    L3_NONEXPANSIVE     = "L3-nonexpansive-clamp"
    L4_PERTURBATION     = "L4-perturbation-budget"

    @property
    def trl(self) -> int:
        return {
            "L0-heuristic":             2,
            "L1-normbound":             2,
            "L2-poweriter":             3,
            "L3-nonexpansive-clamp":    4,   # ← upgraded from 3: design-param committed
            "L4-perturbation-budget":   4,   # ← confirmed: design-param committed
        }[self.value]

    @property
    def uses_design_parameters(self) -> bool:
        """True iff this level's bound is analytically committed before execution."""
        return self in (
            CertLevel.L3_NONEXPANSIVE,
            CertLevel.L4_PERTURBATION,
        )


@dataclass(frozen=True)
class AceCertificate:
    level:            CertLevel
    certified:        bool
    lipschitz_upper:  float
    gap_lb:           float
    contraction_rate: float
    budget_used:      float
    tau:              float
    delta:            float
    margin:           float
    tail_bound:       float
    details:          dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.certified and self.gap_lb <= 0:
            raise ValueError(
                f"AceCertificate.certified=True requires gap_lb > 0, "
                f"got {self.gap_lb}"
            )
        if self.lipschitz_upper < 0:
            raise ValueError("lipschitz_upper must be ≥ 0")


@dataclass
class AceBudgetState:
    tau:            float = 1.0
    consumed:       float = 0.0
    depletion_rate: float = 0.0

    @property
    def remaining(self) -> float:
        return max(0.0, self.tau - self.consumed)

    @property
    def is_depleted(self) -> bool:
        return self.consumed >= self.tau
```


***

## Artifact 3 — Updated `src/pirtm/ace/levels/l3_nonexpansive.py`

Certificate bound is now `designed_clamp_norm` (design parameter), not `nXi` (runtime measurement). Both are recorded in `details` so the audit trail shows the committed bound and the runtime verification simultaneously.

```python
"""
L3-nonexpansive-clamp: TRL-4 (ADR-012).

‖K̃‖ ≤ ρ(T) · designed_clamp_norm   (design-parameter-committed bound)

  designed_clamp_norm: pre-committed ‖P_C‖_design ≤ 1.0  (TRL-4 claim surface)
  nXi:                 runtime measured ‖P_C‖              (verification trace)
  L0 invariant:        nXi ≤ designed_clamp_norm            (enforced by validate())

The certificate uses designed_clamp_norm as the Lipschitz factor.
nXi appears in .details["measured_clamp_norm"] for audit.
"""
from __future__ import annotations

from ..telemetry import AceTelemetry
from ..types import AceCertificate, CertLevel
from .l2_poweriter import certify_l2

MAX_DESIGNED_CLAMP_NORM = 1.0   # L0 invariant: ‖P_C‖_design ≤ 1.0


def certify_l3(
    telemetry: AceTelemetry,
    *,
    tau: float = 1.0,
    delta: float = 0.05,
) -> AceCertificate:
    """
    L3 certification using the pre-committed designed_clamp_norm.
    validate() must be called before this — it enforces the design
    envelope invariant (nXi ≤ designed_clamp_norm).
    """
    if telemetry.designed_clamp_norm is None:
        raise TypeError(
            "L3 requires AceTelemetry.designed_clamp_norm to be set "
            "(pre-committed design parameter). "
            "Set it analytically before execution."
        )
    if telemetry.contraction_matrix is None and telemetry.spectral_estimate is None:
        raise TypeError(
            "L3 requires AceTelemetry with contraction_matrix or spectral_estimate."
        )

    # Design parameter gate — belt-and-suspenders on top of validate()
    dcn = telemetry.designed_clamp_norm
    if dcn > MAX_DESIGNED_CLAMP_NORM + 1e-9:
        raise ValueError(
            f"L3_DESIGN_PARAMETER_INVALID: "
            f"designed_clamp_norm={dcn:.9f} > 1.0. "
            f"Non-expansive projection must satisfy ‖P_C‖_design ≤ 1.0."
        )

    # Get ρ(T) from L2
    l2_cert = certify_l2(telemetry, tau=tau, delta=delta)

    # Composite Lipschitz uses DESIGN PARAMETER (not runtime nXi)
    composite_lipschitz = l2_cert.lipschitz_upper * dcn
    gap_lb = 1.0 - composite_lipschitz
    certified = composite_lipschitz < (1.0 - delta)

    # Runtime deviation from design commitment
    design_slack = dcn - telemetry.nXi  # > 0 means runtime is within envelope

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
            "rho_T":                l2_cert.lipschitz_upper,
            "designed_clamp_norm":  dcn,           # CLAIM SURFACE
            "measured_clamp_norm":  telemetry.nXi, # VERIFICATION TRACE
            "design_slack":         design_slack,   # dcn − nXi (must be ≥ 0)
            "clamp_radius":         telemetry.clamp_radius,
            "composite_lipschitz":  composite_lipschitz,
            "step":                 telemetry.step,
            "trl":                  4,
        },
    )
```


***

## Artifact 4 — Updated `src/pirtm/ace/levels/l4_perturbation.py`

```python
"""
L4-perturbation-budget: TRL-4 (ADR-012).

Certified robustness bound uses designed_perturbation_bound (design parameter).
nLam is the runtime verification trace.

  designed_perturbation_bound: pre-committed ‖ΔK‖_design   (TRL-4 claim surface)
  nLam:                         runtime measured ‖ΔK‖       (verification trace)
  L0 invariant:                 nLam ≤ designed_perturbation_bound
"""
from __future__ import annotations

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
    L4 certification using designed_perturbation_bound.
    validate() must be called before this to enforce:
      nLam ≤ designed_perturbation_bound (design envelope invariant).
    """
    if telemetry.designed_perturbation_bound is None:
        raise TypeError(
            "L4 requires AceTelemetry.designed_perturbation_bound to be set "
            "(pre-committed design parameter). "
            "Set it analytically before execution."
        )
    if telemetry.disturbance_norm is None:
        raise TypeError("L4 requires AceTelemetry.disturbance_norm to be set.")
    if (telemetry.contraction_matrix is None
            and telemetry.spectral_estimate is None):
        raise TypeError(
            "L4 requires AceTelemetry with contraction_matrix or spectral_estimate."
        )

    dpb = telemetry.designed_perturbation_bound

    # Get base ρ from L3 (design-committed) or L2
    if telemetry.designed_clamp_norm is not None:
        base_cert = certify_l3(telemetry, tau=tau, delta=delta)
    else:
        base_cert = certify_l2(telemetry, tau=tau, delta=delta)

    base_gap = base_cert.gap_lb                          # 1 − ρ_base
    perturbed_lipschitz = base_cert.lipschitz_upper + dpb  # uses DESIGN PARAM
    perturbed_gap = 1.0 - perturbed_lipschitz

    # Certification conditions (both required)
    within_gap = dpb < base_gap
    within_delta = perturbed_lipschitz < (1.0 - delta)
    certified = within_gap and within_delta

    tail_bound = (
        float("inf") if perturbed_lipschitz >= 1.0
        else telemetry.disturbance_norm / max(1e-12, perturbed_gap)
    )

    # Runtime deviation from design commitment
    perturbation_slack = dpb - telemetry.nLam  # > 0 means runtime is within envelope

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
            "base_level":                  base_cert.level.value,
            "rho_base":                    base_cert.lipschitz_upper,
            "designed_perturbation_bound": dpb,           # CLAIM SURFACE
            "measured_perturbation":       telemetry.nLam, # VERIFICATION TRACE
            "perturbation_slack":          perturbation_slack,  # dpb − nLam
            "disturbance_norm":            telemetry.disturbance_norm,
            "perturbed_gap":               perturbed_gap,
            "within_gap":                  within_gap,
            "within_delta":                within_delta,
            "step":                        telemetry.step,
            "trl":                         4,
        },
    )
```


***

## Artifact 5 — Full Test Harness Updates

### `tests/test_ace_telemetry.py` — design envelope section (replaces prior `TestAceTelemetryConstruction`)

```python
# ── Design Envelope Invariants ────────────────────────────────────────────────

class TestDesignEnvelopeInvariants:
    """
    These test the L0 hard-halt invariants introduced by ADR-012.
    They must NEVER be downgraded to warnings.
    """

    def test_nxi_within_designed_clamp_norm_passes(self):
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.90,                        # runtime measurement
            nLam=0.05, projected=False, residual=0.0,
            designed_clamp_norm=0.95,         # design commitment: nXi ≤ 0.95 ✓
        )
        t.validate()  # must not raise

    def test_nxi_exceeds_designed_clamp_norm_halts(self):
        t = AceTelemetry(
            step=3, q=0.5, epsilon=0.05,
            nXi=0.97,                         # runtime exceeds design
            nLam=0.05, projected=False, residual=0.0,
            designed_clamp_norm=0.95,          # 0.97 > 0.95 → halt
        )
        with pytest.raises(RuntimeError, match="DESIGN_ENVELOPE_VIOLATION"):
            t.validate()

    def test_nlam_within_designed_perturbation_bound_passes(self):
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.9, nLam=0.04,               # runtime measurement
            projected=False, residual=0.0,
            designed_perturbation_bound=0.05,  # nLam ≤ 0.05 ✓
        )
        t.validate()

    def test_nlam_exceeds_designed_perturbation_bound_halts(self):
        t = AceTelemetry(
            step=5, q=0.5, epsilon=0.05,
            nXi=0.9, nLam=0.08,               # runtime exceeds design
            projected=False, residual=0.0,
            designed_perturbation_bound=0.05,  # 0.08 > 0.05 → halt
        )
        with pytest.raises(RuntimeError, match="DESIGN_ENVELOPE_VIOLATION"):
            t.validate()

    def test_designed_clamp_norm_gt_1_is_design_error(self):
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.9, nLam=0.0,
            projected=False, residual=0.0,
            designed_clamp_norm=1.05,          # invalid: non-expansive requires ≤ 1
        )
        with pytest.raises(ValueError, match="DESIGN_PARAMETER_INVALID"):
            t.validate()

    def test_designed_perturbation_bound_negative_is_design_error(self):
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.9, nLam=0.0,
            projected=False, residual=0.0,
            designed_perturbation_bound=-0.01,
        )
        with pytest.raises(ValueError, match="DESIGN_PARAMETER_INVALID"):
            t.validate()

    def test_design_slack_in_l3_cert_details(self, l3_telemetry):
        cert = certify_l3(l3_telemetry)
        slack = cert.details["design_slack"]
        assert slack >= 0   # nXi ≤ designed_clamp_norm

    def test_perturbation_slack_in_l4_cert_details(self, l4_telemetry):
        cert = certify_l4(l4_telemetry)
        slack = cert.details["perturbation_slack"]
        assert slack >= 0   # nLam ≤ designed_perturbation_bound


# ── TRL Upgrade Gate ──────────────────────────────────────────────────────────

class TestTRLUpgrade:
    def test_l3_is_trl_4(self, l3_telemetry):
        cert = certify_l3(l3_telemetry)
        assert cert.level.trl == 4

    def test_l4_is_trl_4(self, l4_telemetry):
        cert = certify_l4(l4_telemetry)
        assert cert.level.trl == 4

    def test_l0_l1_still_trl_2(self):
        assert CertLevel.L0_HEURISTIC.trl == 2
        assert CertLevel.L1_NORMBOUND.trl == 2

    def test_l2_still_trl_3(self):
        assert CertLevel.L2_POWERITER.trl == 3

    def test_l3_l4_use_design_parameters(self):
        assert CertLevel.L3_NONEXPANSIVE.uses_design_parameters is True
        assert CertLevel.L4_PERTURBATION.uses_design_parameters is True

    def test_l0_l1_l2_do_not_use_design_parameters(self):
        assert CertLevel.L0_HEURISTIC.uses_design_parameters is False
        assert CertLevel.L1_NORMBOUND.uses_design_parameters is False
        assert CertLevel.L2_POWERITER.uses_design_parameters is False

    def test_l3_cert_details_carry_trl_4(self, l3_telemetry):
        cert = certify_l3(l3_telemetry)
        assert cert.details["trl"] == 4

    def test_l4_cert_details_carry_trl_4(self, l4_telemetry):
        cert = certify_l4(l4_telemetry)
        assert cert.details["trl"] == 4


# ── Claim Surface vs Verification Trace ──────────────────────────────────────

class TestClaimSurfaceVsVerificationTrace:
    """
    Pins the contract: design parameters are the claim surface.
    Runtime measurements are the verification trace.
    Both must appear in .details.
    """

    def test_l3_details_has_designed_and_measured_clamp_norm(self, l3_telemetry):
        cert = certify_l3(l3_telemetry)
        assert "designed_clamp_norm" in cert.details   # CLAIM SURFACE
        assert "measured_clamp_norm" in cert.details   # VERIFICATION TRACE

    def test_l3_claim_surface_uses_design_param_not_runtime(self):
        K = np.diag([0.5, 0.4])
        # design commitment is tighter than runtime measurement
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.80,                  # runtime: tighter than design
            nLam=0.0, projected=False, residual=0.0,
            contraction_matrix=K,
            designed_clamp_norm=0.90,   # design: 0.90
        )
        cert = certify_l3(t)
        # lipschitz_upper uses design param (0.90), not runtime (0.80)
        import numpy as np
        rho_T = cert.details["rho_T"]
        assert abs(cert.lipschitz_upper - rho_T * 0.90) < 1e-9

    def test_l4_details_has_designed_and_measured_perturbation(self, l4_telemetry):
        cert = certify_l4(l4_telemetry)
        assert "designed_perturbation_bound" in cert.details   # CLAIM SURFACE
        assert "measured_perturbation" in cert.details          # VERIFICATION TRACE

    def test_l4_claim_surface_uses_design_param_not_nlam(self):
        K = np.diag([0.5, 0.4])
        t = AceTelemetry(
            step=0, q=0.5, epsilon=0.05,
            nXi=0.95, nLam=0.02,        # runtime: lower than design
            projected=False, residual=0.0,
            contraction_matrix=K,
            designed_clamp_norm=0.95,
            designed_perturbation_bound=0.05,  # design: 0.05
            disturbance_norm=0.1,
        )
        cert = certify_l4(t)
        # perturbed_lipschitz uses 0.05 (design), not 0.02 (runtime nLam)
        rho_base = cert.details["rho_base"]
        assert abs(cert.lipschitz_upper - (rho_base + 0.05)) < 1e-9
```


### Updated `conftest.py` fixtures

```python
# tests/conftest.py — replace l3_telemetry and l4_telemetry fixtures

@pytest.fixture
def l3_telemetry():
    """L3: designed_clamp_norm=0.95 (design param), nXi=0.90 (runtime trace)."""
    return AceTelemetry(
        step=0, q=0.50, epsilon=0.05,
        nXi=0.90,                     # runtime — must be ≤ designed_clamp_norm
        nLam=0.05,
        projected=True, residual=0.001,
        contraction_matrix=np.diag([0.5, 0.4]),
        clamp_radius=2.0,
        designed_clamp_norm=0.95,     # PRE-COMMITTED design parameter
    )

@pytest.fixture
def l4_telemetry():
    """L4: designed params committed; runtime measurements within envelope."""
    return AceTelemetry(
        step=0, q=0.50, epsilon=0.05,
        nXi=0.90,                          # runtime ≤ designed_clamp_norm=0.95
        nLam=0.04,                         # runtime ≤ designed_perturbation_bound=0.05
        projected=True, residual=0.001,
        contraction_matrix=np.diag([0.5, 0.4]),
        clamp_radius=2.0,
        designed_clamp_norm=0.95,          # PRE-COMMITTED
        designed_perturbation_bound=0.05,  # PRE-COMMITTED
        disturbance_norm=0.10,
    )
```


***

## ADR-012 Entry

```md
# ADR-012: nXi and nLam are pre-committed design parameters in AceTelemetry
Status:    accepted
Date:      2026-02-28
Decider:   Lead MT (RVG)
trl:       4
Horizon:   7 days
Metric:
  - designed_clamp_norm / designed_perturbation_bound present in all
    L3/L4 AceTelemetry instances; CI lint gate fails on None
  - CertLevel.L3_NONEXPANSIVE.trl == 4; CertLevel.L4_PERTURBATION.trl == 4
  - DESIGN_ENVELOPE_VIOLATION raised (not warned) in CI test suite

## Decision
AceTelemetry carries two tiers of parameters:

  Tier 1 — Runtime measurements (inherited from StepInfo):
    nXi:  measured ‖P_C‖ during execution
    nLam: measured ‖ΔK‖ during execution

  Tier 2 — Pre-committed design parameters (new, ADR-012):
    designed_clamp_norm:         analytically committed ‖P_C‖_design ≤ 1.0
    designed_perturbation_bound: analytically committed ‖ΔK‖_design ≥ 0

certify_l3 and certify_l4 use Tier-2 parameters as Lipschitz/perturbation
bounds for the certificate (the CLAIM SURFACE).
Tier-1 measurements appear in cert.details as the VERIFICATION TRACE.

L0 invariant (hard halt, not warning):
  nXi  ≤ designed_clamp_norm         (enforced in AceTelemetry.validate())
  nLam ≤ designed_perturbation_bound (enforced in AceTelemetry.validate())

## TRL impact (amends ADR-011)
  L3-nonexpansive-clamp:  TRL-3 → TRL-4
  L4-perturbation-budget: TRL-4 confirmed

## IP note
The distinction between claim surface (Tier-2) and verification trace
(Tier-1) is the formal basis for ETP claim independence from PIRTM
runtime behavior. Tier-2 parameters are ETP-native design decisions.
Tier-1 measurements are PIRTM recurrence outputs. ADR-006 boundary upheld.
```


***

## Precision Question

> `designed_clamp_norm` and `designed_perturbation_bound` are committed before execution — but **who commits them, and when?** Specifically: are they committed by the Lead MT at system-design time (static, checked into repo as constants), or are they committed per-session by the `AceProtocol` caller at instantiation time (dynamic, passed at runtime)? The answer determines whether `AceProtocol.__init__` should accept `designed_clamp_norm` and `designed_perturbation_bound` as protocol-level defaults that get injected into every `AceTelemetry` during `_normalise()`, or whether callers must always set them explicitly on each `AceTelemetry` instance — and it directly gates whether a `StepInfo`-only caller can ever reach L3/L4 without a code change.

