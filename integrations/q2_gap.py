"""
Q2 Research Track: Gap scaling data parser.

Optional integration layer for consuming Q2 spectral gap measurements.
PIRTM Phase 2 does NOT depend on this module. Q2 parser can fail or be
missing without affecting Phase 2 core tests.

@spec: docs/q2_external_link.md
@status: Non-blocking integration
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class GapFit:
    """
    Parsed Q2 spectral gap scaling result.
    
    Contract: slope_exponent must be in [-3.46, -3.16] (95% CI).
    r_squared must be > 0.92 (sanity floor).
    """
    
    slope_exponent: float
    """Power-law exponent: Δ(N) ~ N^{slope_exponent}."""
    
    intercept: float
    """Log-space intercept: log(Δ) = intercept + slope_exponent * log(N)."""
    
    r_squared: float
    """Fit quality metric. Sanity floor: R² > 0.92."""
    
    n_data_points: int
    """Number of system sizes measured (N ∈ {10, 20, 50, 100}; typically 4)."""
    
    n_values: list[int]
    """System sizes measured."""
    
    gap_values: list[float]
    """Spectral gaps Δ(N) = λ₂ − λ₁."""
    
    commit_sha: Optional[str] = None
    """Canonical commit SHA from Tooling repo. For audit trail."""
    
    csv_path: Optional[str] = None
    """Source CSV file path. For reproducibility."""
    
    def is_valid(self) -> bool:
        """Check contract constraints."""
        return (
            -3.46 <= self.slope_exponent <= -3.16
            and self.r_squared > 0.92
        )
    
    def validate_or_raise(self) -> None:
        """Raise if contract violated."""
        if not self.is_valid():
            violations = []
            if not (-3.46 <= self.slope_exponent <= -3.16):
                violations.append(
                    f"slope_exponent={self.slope_exponent:.3f} outside [-3.46, -3.16]"
                )
            if self.r_squared <= 0.92:
                violations.append(
                    f"r_squared={self.r_squared:.4f} ≤ 0.92 (sanity floor violated)"
                )
            raise ValueError(f"Q2 gap fit contract violated: {'; '.join(violations)}")
    
    def formula_str(self) -> str:
        """Return formula: Δ(N) ~ 10^intercept * N^exponent."""
        coeff = 10 ** self.intercept
        return f"Δ(N) ≈ {coeff:.1f} × N^({self.slope_exponent:.2f})"


def parse_q2_gap_csv(
    csv_path: str | Path,
    from_commit_sha: Optional[str] = None,
    validate: bool = True,
) -> GapFit:
    """
    Parse Task1c-gap.csv from Q2 research track.
    
    Parameters
    ----------
    csv_path : str | Path
        Path to Task1c-gap.csv in Tooling repo.
    from_commit_sha : str | None
        Expected commit SHA. If provided and doesn't match file's recorded SHA,
        raises warning (audit check only; does not fail).
    validate : bool
        If True (default), call validate_or_raise() after parsing.
    
    Returns
    -------
    GapFit
        Parsed and validated (if validate=True) gap scaling result.
    
    Raises
    ------
    FileNotFoundError
        If csv_path does not exist.
    ValueError
        If CSV has wrong structure or contract is violated (and validate=True).
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Q2 gap CSV not found: {csv_path}\n"
            "Ensure Task 1c output is available at: "
            "multiplicity/Core/docs/plans/q2/Task1c-gap.csv"
        )
    
    # Parse CSV
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas required for Q2 gap parser. "
            "Install: pip install pandas"
        )
    
    df = pd.read_csv(csv_path)
    
    # Validate structure
    required_cols = {'N', 'gap'}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"CSV missing required columns. Found {set(df.columns)}, "
            f"expected at least {required_cols}"
        )
    
    if len(df) < 2:
        raise ValueError(
            f"CSV must have at least 2 data rows for fit. Got {len(df)}"
        )
    
    # Extract data
    N_vals = df['N'].values.astype(float)
    gap_vals = df['gap'].values.astype(float)
    
    # Fit power law: log(gap) = a + b*log(N)
    log_N = np.log(N_vals)
    log_gap = np.log(gap_vals)
    
    coeffs = np.polyfit(log_N, log_gap, 1)
    slope, intercept = coeffs[0], coeffs[1]
    
    # Compute R²
    log_gap_fit = slope * log_N + intercept
    ss_res = np.sum((log_gap - log_gap_fit) ** 2)
    ss_tot = np.sum((log_gap - np.mean(log_gap)) ** 2)
    r_sq = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    # Construct result
    result = GapFit(
        slope_exponent=float(slope),
        intercept=float(intercept),
        r_squared=float(r_sq),
        n_data_points=len(df),
        n_values=list(N_vals.astype(int)),
        gap_values=list(gap_vals),
        commit_sha=from_commit_sha,
        csv_path=str(csv_path),
    )
    
    if validate:
        result.validate_or_raise()
    
    return result


__all__ = ["GapFit", "parse_q2_gap_csv"]
