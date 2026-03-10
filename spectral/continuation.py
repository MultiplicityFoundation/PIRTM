"""
Complex resonance detection: analytic continuation of Z_N(s) into the
upper half-plane and comparison with -ζ'(s₁+s)/ζ(s₁+s).

Two tracks per ADR-017:
  Track A: HK.1 residual |Z_N(s) + ζ'/ζ(s₁+s)| on complex grid.
  Track B: AAA poles of Z_N on upper half-plane contour Γ_δ.

@spec: ADR-017, CONJECTURE HK.1 (OPEN)
IMPORTANT: All results from this module are EXPERIMENTAL DATA.
No result closes Conjecture HK.1 or L.2. CI must mark all
tests here as xfail or data-only.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
import warnings

from .laplacian import LaplacianParams, von_mangoldt_weights
from .aaa import aaa, AAAResult

# First 20 nontrivial Riemann zero imaginary parts (LMFDB / known values)
RIEMANN_ZEROS_IM = np.array([
    14.134725141734693,  21.022039638771554,  25.010857580145688,
    30.424876125859513,  32.935061587739189,  37.586178158825671,
    40.918719012147495,  43.327073280914999,  48.005150881167159,
    49.773832477672302,  52.970321477714460,  56.446247697063394,
    59.347044002602352,  60.831778524609809,  65.112544048081607,
    67.079810529494172,  69.546401711173979,  72.067157674481907,
    75.704690699083933,  77.144840069745267,
])


# ── Z_N(s) at complex s ─────────────────────────────────────────────────

def Z_N_complex(
    s: complex,
    params: LaplacianParams,
) -> complex:
    """
    @spec: DEFINITION 19.4, ADR-017
    Z_N(s) = (1/2) Σ_p [ 1/s + 1/(s + 4w_p) ]

    Exact partial-fraction form. Valid for all s ∉ {0} ∪ {-4w_p}.
    Poles: at s=0 (order 1, residue N/2) and s=-4w_p (order 1, residue 1/2).
    ALL POLES ARE ON THE NEGATIVE REAL AXIS at finite N.

    For s in the upper half-plane Im(s) > 0: no poles, smooth convergence.
    """
    w = von_mangoldt_weights(params)
    if np.abs(s) < 1e-300:
        raise ValueError("s=0 is a pole of Z_N. Perturb to Im(s)>0.")
    total = complex(0.0)
    for w_p in w:
        denom1 = s
        denom2 = s + 4.0 * w_p
        if np.abs(denom2) < 1e-300:
            raise ValueError(
                f"s = -4w_p is a pole. Use s with Im(s) > 0. "
                f"Offending w_p={w_p:.6f}"
            )
        total += 1.0 / denom1 + 1.0 / denom2
    return 0.5 * total


def Z_N_on_grid(
    sigma_vals: np.ndarray,
    gamma_vals: np.ndarray,
    params: LaplacianParams,
) -> np.ndarray:
    """
    Evaluate Z_N(σ+iγ) on 2D grid (sigma × gamma).
    sigma_vals: real parts (shape P,)
    gamma_vals: imaginary parts (shape Q,)
    Returns complex array shape (P, Q).

    @spec: ADR-017 Track A grid evaluation.
    """
    P, Q = len(sigma_vals), len(gamma_vals)
    out = np.zeros((P, Q), dtype=complex)
    for i, sigma in enumerate(sigma_vals):
        for j, gamma in enumerate(gamma_vals):
            s = complex(sigma, gamma)
            out[i, j] = Z_N_complex(s, params)
    return out


# ── -ζ'(s₁+s)/ζ(s₁+s) reference via mpmath ────────────────────────────

def neg_zeta_log_deriv(
    s: complex,
    s1: float,
    dps: int = 25,
) -> complex:
    """
    @spec: DEFINITION H.2 — RIGHT SIDE of Conjecture HK.1.
    Computes -ζ'(s₁+s)/ζ(s₁+s) via mpmath at high precision.
    Requires s₁ + s ≠ 1 (pole of ζ) and ζ(s₁+s) ≠ 0.

    @spec-constant: s1 > 1
    CONJECTURE HK.1 (OPEN): Z_N(s) should converge to this as N→∞
    in the upper half-plane (away from Riemann zeros ρ-s₁).
    """
    try:
        import mpmath  # type: ignore
    except ImportError:
        raise ImportError(
            "mpmath required for ζ reference. Install with: pip install mpmath"
        )
    mpmath.mp.dps = dps
    z_arg = mpmath.mpc(s1 + s.real, s.imag)  # type: ignore
    zeta_val = mpmath.zeta(z_arg)  # type: ignore
    if abs(complex(zeta_val)) < 1e-300:  # type: ignore
        warnings.warn(
            f"ζ(s₁+s) ≈ 0 near s={s}; this is a Riemann zero location. "
            "Value will be large (near-pole). Expected if s ≈ ρ-s₁."
        )
    dzeta_val = mpmath.diff(mpmath.zeta, z_arg)  # type: ignore
    result = -dzeta_val / zeta_val  # type: ignore
    return complex(result)  # type: ignore


def neg_zeta_log_deriv_grid(
    sigma_vals: np.ndarray,
    gamma_vals: np.ndarray,
    s1: float,
    dps: int = 25,
) -> np.ndarray:
    """
    Evaluate -ζ'(s₁+σ+iγ)/ζ(s₁+σ+iγ) on 2D grid.
    Returns complex array shape (P, Q).
    """
    P, Q = len(sigma_vals), len(gamma_vals)
    out = np.zeros((P, Q), dtype=complex)
    for i, sigma in enumerate(sigma_vals):
        for j, gamma in enumerate(gamma_vals):
            s = complex(sigma, gamma)
            out[i, j] = neg_zeta_log_deriv(s, s1, dps=dps)
    return out


# ── Track A: HK.1 residual measurement ──────────────────────────────────

@dataclass
class TrackAResult:
    """
    @spec: ADR-017 Track A
    HK.1 residual |Z_N(s) + ζ'/ζ(s₁+s)| on complex grid.
    """
    sigma_vals: np.ndarray
    gamma_vals: np.ndarray
    Z_N: np.ndarray          # shape (P, Q), complex
    zeta_ref: np.ndarray     # shape (P, Q), complex
    residual: np.ndarray     # shape (P, Q), real = |Z_N - zeta_ref|
    N: int
    s1: float
    conjecture_status: str = "OPEN — HK.1. Agreement ≠ proof."

    @property
    def max_residual(self) -> float:
        return float(np.nanmax(self.residual))

    @property
    def mean_residual(self) -> float:
        return float(np.nanmean(self.residual))

    def residual_near_zero(self, gamma: float, tol: float = 0.5) -> float:
        """Residual at the imaginary part closest to ρ-s₁ for first zero."""
        rho1_im = RIEMANN_ZEROS_IM[0]
        target_gamma = rho1_im
        j = int(np.argmin(np.abs(self.gamma_vals - target_gamma)))
        sigma_mid = int(len(self.sigma_vals) // 2)
        return float(self.residual[sigma_mid, j])


def run_track_a(
    params: LaplacianParams,
    sigma_range: tuple[float, float] = (-0.8, 0.3),
    gamma_range: tuple[float, float] = (1.0, 80.0),
    n_sigma: int = 30,
    n_gamma: int = 200,
    dps: int = 25,
) -> TrackAResult:
    """
    @spec: ADR-017 Track A
    Compute HK.1 residual |Z_N(s) + ζ'/ζ(s₁+s)| on complex grid.
    All Im(s) > 0 (safe from poles of Z_N on real axis).

    NOTE: This is EXPERIMENTAL DATA for Conjecture HK.1.
    A decreasing residual as N increases is computational support.
    It does NOT prove HK.1.
    """
    sigma_vals = np.linspace(*sigma_range, n_sigma)
    gamma_vals = np.linspace(*gamma_range, n_gamma)

    Z = Z_N_on_grid(sigma_vals, gamma_vals, params)
    ref = neg_zeta_log_deriv_grid(sigma_vals, gamma_vals, params.s1, dps=dps)
    residual = np.abs(Z - ref)

    # NaN out any evaluation failures
    residual = np.where(np.isfinite(residual), residual, np.nan)

    return TrackAResult(
        sigma_vals=sigma_vals,
        gamma_vals=gamma_vals,
        Z_N=Z,
        zeta_ref=ref,
        residual=residual,
        N=params.N,
        s1=params.s1,
    )


# ── Track B: AAA pole detection ──────────────────────────────────────────

@dataclass
class TrackBResult:
    """
    @spec: ADR-017 Track B
    AAA rational approximant to Z_N on upper half-plane contour Γ_δ.
    aaa_result: full AAA output
    poles_upper: poles with Im(pole) > 0 (candidates for Riemann zeros)
    poles_real: poles with Im(pole) ≈ 0 (matches known -4w_p poles)
    comparison: comparison of poles_upper to shifted Riemann zeros ρ-s₁
    """
    contour: np.ndarray          # sample points on Γ_δ
    Z_N_values: np.ndarray       # Z_N evaluated on contour
    aaa_result: AAAResult
    poles_upper: np.ndarray      # poles with Im(s) > 0
    poles_real: np.ndarray       # poles with Im(s) ≈ 0
    comparison: dict[str, object]  # vs. shifted Riemann zeros
    N: int
    s1: float
    delta: float                 # Im of contour Γ_δ
    conjecture_status: str = "OPEN — HK.1. Agreement ≠ proof."


def _compare_to_riemann_zeros(
    poles: np.ndarray,
    s1: float,
    n_zeros: int = 10,
) -> dict[str, object]:
    """
    Compare imaginary parts of upper-half-plane poles to ρ-s₁.
    Returns match statistics.
    @spec: CONJECTURE L.2 (OPEN). Agreement is evidence only.
    """
    if len(poles) == 0:
        return {"n_compared": 0, "distances": [], "mean_distance": None}

    # Shifted zero positions (complex)
    shifted = np.array([
        complex(0.5 - s1, gamma) for gamma in RIEMANN_ZEROS_IM[:n_zeros]
    ])

    # Match by imaginary part
    pole_ims = np.imag(poles)
    zero_ims = np.imag(shifted)

    n = min(len(poles), len(shifted))
    # Sort both by Im part and compare
    poles_sorted = poles[np.argsort(pole_ims)]
    zeros_sorted = shifted[np.argsort(zero_ims)]

    distances = []   # type: ignore
    for k in range(n):
        if k < len(poles_sorted) and k < len(zeros_sorted):
            d = abs(poles_sorted[k] - zeros_sorted[k])
            distances.append(float(d))  # type: ignore

    return {
        "n_compared": n,
        "distances": distances,  # type: ignore
        "mean_distance": float(np.mean(distances)) if distances else None,  # type: ignore
        "max_distance": float(np.max(distances)) if distances else None,  # type: ignore
        "poles_upper": [(complex(p).real, complex(p).imag) for p in poles_sorted[:n]],
        "zeros_shifted": [(complex(z).real, complex(z).imag) for z in zeros_sorted[:n]],
    }


def run_track_b(
    params: LaplacianParams,
    delta: float = 0.5,
    sigma_range: tuple[float, float] = (-0.8, 0.3),
    n_contour: int = 300,
    aaa_tol: float = 1e-10,
    upper_half_plane_tol: float = 0.1,
) -> TrackBResult:
    """
    @spec: ADR-017 Track B
    AAA rational approximant to Z_N on contour Γ_δ = {Re∈σ_range, Im=δ}.

    RATIONALE: If HK.1 holds, Z_N(s) → -ζ'/ζ(s₁+s) as N→∞ on Γ_δ.
    The AAA approximant to Z_N must approximate a function with poles at
    ρ-s₁, so AAA places poles there. These \"proto-resonances\" converge
    to the true resonances ρ-s₁ as N→∞.

    upper_half_plane_tol: poles with Im(pole) > upper_half_plane_tol
    are classified as \"upper half-plane\" candidates.

    @spec: CONJECTURE HK.1 (OPEN). All poles are EXPERIMENTAL.
    """
    sigma_vals = np.linspace(*sigma_range, n_contour)
    contour = sigma_vals + 1j * delta

    # Evaluate Z_N on contour (all Im(s) = δ > 0, safe from poles)
    Z_vals = np.array([Z_N_complex(s, params) for s in contour])

    # AAA approximant
    result = aaa(contour, Z_vals, tol=aaa_tol)

    # Classify poles
    all_poles = result.poles
    upper_mask = np.imag(all_poles) > upper_half_plane_tol
    real_mask  = np.abs(np.imag(all_poles)) <= upper_half_plane_tol

    poles_upper = all_poles[upper_mask]
    poles_real  = all_poles[real_mask]

    comparison = _compare_to_riemann_zeros(poles_upper, params.s1)

    return TrackBResult(
        contour=contour,
        Z_N_values=Z_vals,
        aaa_result=result,
        poles_upper=poles_upper,
        poles_real=poles_real,
        comparison=comparison,
        N=params.N,
        s1=params.s1,
        delta=delta,
    )


# ── Convergence surface across (N, s₁) ──────────────────────────────────

@dataclass
class ConvergenceSurface:
    """
    @spec: ADR-016 (canonical limit order: N→∞ first, then s₁→1⁺)
    Tracks resonance positions across (N, s₁) grid.
    """
    results_A: dict[tuple[int, float], object]   # key: (N, s1) → TrackAResult
    results_B: dict[tuple[int, float], object]   # key: (N, s1) → TrackBResult
    N_values: list[int]
    s1_values: list[float]

    def convergence_table(self) -> list[dict[str, object]]:
        """
        For each (N, s1): mean residual (A) and mean pole distance (B).
        Ordered by N first (ADR-016 limit order).
        """
        rows: list[dict[str, object]] = []  # type: ignore
        for s1 in self.s1_values:
            for N in self.N_values:
                key = (N, s1)
                row: dict[str, object] = {"N": N, "s1": s1}  # type: ignore
                if key in self.results_A:
                    row["mean_residual_A"] = self.results_A[key].mean_residual  # type: ignore
                if key in self.results_B:
                    comp = self.results_B[key].comparison  # type: ignore
                    row["mean_pole_distance_B"] = comp.get("mean_distance")  # type: ignore
                    row["n_upper_poles"] = len(self.results_B[key].poles_upper)  # type: ignore
                rows.append(row)  # type: ignore
        return rows  # type: ignore
