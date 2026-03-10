#!/usr/bin/env python3
"""
Quick spectral fingerprint CLI utility.

Usage:
  python -m pirtm.spectral.cli_fingerprint <csv_file>

Example:
  python -m pirtm.spectral.cli_fingerprint Task1c-gap.csv

Output:
  Prints operator type classification (diagonal/translation/multiplicative)
  and exponent estimate.

Purpose:
  Instant operator identification from CSV alone—no code inspection needed.
  Works even with noisy data (30-40% corruption tolerance).

Reference:
  - Q1 Lead response (Cheeger inequality diagnostic framework)
  - 5-point spectral shape test (robust to noise)
"""
import sys
import numpy as np
import pandas as pd
from fingerprint import (
    classify_gap_scaling,
    shape_test_5point,
    SpectralFingerprint,
)


def main(csv_path: str):
    """Load CSV and identify operator type via spectral fingerprint."""
    try:
        # Load CSV (assume columns: N, gap)
        df = pd.read_csv(csv_path)
        
        # Handle column naming flexibility
        if "N" in df.columns:
            N_vals = df["N"].values
        else:
            N_vals = df.iloc[:, 0].values
        
        if "gap" in df.columns:
            delta_vals = df["gap"].values
        else:
            delta_vals = df.iloc[:, 1].values
        
        # Fit power-law exponent
        log_N = np.log(N_vals)
        log_delta = np.log(delta_vals)
        slope, intercept = np.polyfit(log_N, log_delta, 1)
        gamma = -slope
        
        # 30-second fingerprint classification
        op_type, fp_conf = classify_gap_scaling(gamma)
        
        # 5-point shape test for robustness check
        shape_score, shape_notes = shape_test_5point(N_vals, delta_vals)
        
        # Master diagnostic
        fp = SpectralFingerprint(N_vals, delta_vals)
        verdict = fp.identify()
        
        # Print results
        print("\n" + "=" * 70)
        print(f"SPECTRAL FINGERPRINT CLASSIFICATION: {csv_path}")
        print("=" * 70)
        print()
        print(f"Estimated exponent:        γ ≈ {gamma:.3f}")
        print(f"Fingerprint confidence:    {fp_conf:.1%}")
        print(f"5-point shape test score:  {shape_score}/5")
        print()
        print(f"OPERATOR TYPE: {verdict.operator_type.value:40s}")
        print(f"Overall confidence: {verdict.confidence:.1%}")
        print()
        
        # Show shape test details
        print("Shape Test Details:")
        for note in shape_notes[:4]:  # Skip P5 for brief output
            print(f"  {note}")
        print()
        
        # Decision logic
        if verdict.operator_type.value == "diagonal":
            print("→ Diagonal prime operator (gap ≈ constant)")
        elif verdict.operator_type.value == "prime_translation_cayley":
            print("→ Prime translation (Cayley) Laplacian")
            print(f"   Inferred domain scaling: M ~ N^{verdict.inferred_beta:.2f}")
        elif verdict.operator_type.value == "multiplicative":
            print("→ Multiplicative prime operator (gap ~ 1/log N)")
        else:
            print("→ UNKNOWN / mixed operator type")
        
        print()
        print("=" * 70)
        return 0
    
    except FileNotFoundError:
        print(f"ERROR: File not found: {csv_path}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cli_fingerprint.py <csv_file>", file=sys.stderr)
        print("Example: python cli_fingerprint.py Task1c-gap.csv", file=sys.stderr)
        sys.exit(1)
    
    csv_file = sys.argv[1]
    exit_code = main(csv_file)
    sys.exit(exit_code)
