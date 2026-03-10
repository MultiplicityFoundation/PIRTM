"""
Predictive Warning System (Day 30+ optimization, Task 3).

Strategy:
  Compute bounds on spectral radius BEFORE full linking.
  Warn early if projected bounds indicate margin will be insufficient.
  Enable early exit to avoid expensive computation.

Techniques:
  1. Gershgorin Circle Theorem: Bounds eigenvalues using row/column sums
  2. Frobenius norm bound: ρ(A) ≤ ‖A‖_F (loose but fast)
  3. Row-sum bound: ρ(A) ≤ max |row sum| (for non-negative matrices)
  4. Trace and pivot estimators: More refined estimates

Reference: ADR-008 Day 30+ optimization phase
"""

import math
from typing import List, Tuple, Dict, Optional


class PredictiveWarningSystem:
    """Predict spectral radius and warn before full linking."""
    
    SAFE_THRESHOLD = 0.95      # r ≤ this → safe (excellent margin)
    WARNING_THRESHOLD = 0.98   # r > this → need verification
    CRITICAL_THRESHOLD = 0.99  # r > this → likely non-contractive
    
    def __init__(self, early_exit_enabled: bool = True):
        """
        Initialize predictive warning system.
        
        Args:
            early_exit_enabled: If True, allow early exit if bounds indicate non-contractivity
        """
        self.early_exit_enabled = early_exit_enabled
        self.last_estimate = None
        self.last_bounds = None
        self.warnings = []
    
    def predict_and_warn(self, coupling_matrix: List[List[float]]) -> Tuple[str, Dict]:
        """
        Predict spectral radius and emit warnings if needed.
        
        Returns:
            (warning_level, bounds_dict)
            where warning_level is 'safe', 'warning', or 'critical'
        """
        bounds = self.compute_bounds(coupling_matrix)
        self.last_bounds = bounds
        
        lower, upper = bounds['gershgorin_lower'], bounds['gershgorin_upper']
        max_row_sum = bounds['max_row_sum']
        frobenius_bound = bounds['frobenius_bound']
        
        # Use most conservative upper bound
        conservative_bound = max(upper, max_row_sum, frobenius_bound)
        
        # Check margin
        margin = 1.0 - conservative_bound
        
        # Classify warning level
        if conservative_bound <= self.SAFE_THRESHOLD:
            level = 'safe'
            message = f"Safe: predicted r ≤ {conservative_bound:.4f} (margin ≥ {margin:.4f})"
        elif conservative_bound <= self.WARNING_THRESHOLD:
            level = 'warning'
            message = f"⚠️ Warning: predicted r ≤ {conservative_bound:.4f} (margin ≤ {margin:.4f})"
        else:
            level = 'critical'
            message = f"🚨 Critical: predicted r > {conservative_bound:.4f} (margin < {margin:.4f})"
        
        # Store warning
        if level in ['warning', 'critical']:
            self.warnings.append({
                'level': level,
                'message': message,
                'bounds': bounds.copy()
            })
        
        return level, bounds
    
    def compute_bounds(self, matrix: List[List[float]]) -> Dict:
        """
        Compute multiple bounds on spectral radius.
        
        Bounds computation:
          1. Gershgorin: uses diagonal + row sums
          2. Max row sum: ρ(A) ≤ max_i Σ_j |a_ij|
          3. Frobenius: ρ(A) ≤ ‖A‖_F = √(Σ a²_ij)
          4. Trace estimate: uses trace(A^2) / n
        """
        n = len(matrix)
        if n == 0:
            return {'gershgorin_lower': 0.0, 'gershgorin_upper': 0.0}
        
        # Compute row sums
        row_sums = [sum(abs(matrix[i][j]) for j in range(n)) for i in range(n)]
        max_row_sum = max(row_sums) if row_sums else 0.0
        
        # Frobenius norm: ‖A‖_F = √(Σ a²_ij)
        frobenius_norm_sq = sum(matrix[i][j] ** 2 for i in range(n) for j in range(n))
        frobenius_bound = math.sqrt(frobenius_norm_sq)
        
        # Gershgorin circles
        gershgorin_disks = []
        for i in range(n):
            center = matrix[i][i]
            radius = sum(abs(matrix[i][j]) for j in range(n) if j != i)
            gershgorin_disks.append((center, radius))
        
        # Gershgorin bounds: all eigenvalues lie in union of disks
        # Lower bound: min(center - radius) if all centers > 0
        # Upper bound: max(center + radius)
        lower_bound = min(center - radius for center, radius in gershgorin_disks) if gershgorin_disks else 0.0
        upper_bound = max(center + radius for center, radius in gershgorin_disks) if gershgorin_disks else 0.0
        
        # Trace-based estimate (Tr[A^2] / n)
        trace_a2 = sum(matrix[i][i]**2 for i in range(n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    trace_a2 += 2.0 * matrix[i][j] * matrix[j][i]  # Off-diagonal contribution
        
        trace_estimate = math.sqrt(trace_a2 / max(n, 1))
        
        # Compute spectral radius estimate conservative upper bound
        bounds = {
            # Gershgorin
            'gershgorin_lower': max(lower_bound, 0.0),
            'gershgorin_upper': upper_bound,
            'gershgorin_disks': gershgorin_disks,
            
            # Row sum bound
            'max_row_sum': max_row_sum,
            
            # Frobenius
            'frobenius_norm': frobenius_bound,
            'frobenius_bound': frobenius_bound,
            
            # Trace-based
            'trace_estimate': trace_estimate,
            
            # Summary
            'conservative_upper': max(upper_bound, max_row_sum, frobenius_bound),
            'optimistic_lower': max(lower_bound, 0.0),
        }
        
        return bounds
    
    def early_exit_decision(self, coupling_matrix: List[List[float]]) -> Tuple[bool, Optional[str]]:
        """
        Decide whether to exit early based on predictive bounds.
        
        Returns:
            (should_exit, reason)
            - If should_exit=True, skip linking (network will be non-contractive)
            - If should_exit=False, proceed with linking
        """
        if not self.early_exit_enabled:
            return False, None
        
        bounds = self.compute_bounds(coupling_matrix)
        conservative = bounds['conservative_upper']
        
        if conservative >= 1.0:
            return True, f"Predicted r ≥ 1.0 (network non-contractive)"
        elif conservative > self.CRITICAL_THRESHOLD:
            return True, f"Predicted r > {self.CRITICAL_THRESHOLD} (margin < {1.0 - self.CRITICAL_THRESHOLD})"
        
        return False, None
    
    def print_bounds_report(self, coupling_matrix: List[List[float]] = None):
        """Print a detailed bounds report."""
        if coupling_matrix is not None:
            bounds = self.compute_bounds(coupling_matrix)
            self.last_bounds = bounds
        elif self.last_bounds is None:
            print("No bounds computed yet")
            return
        
        bounds = self.last_bounds
        print("\n" + "=" * 70)
        print("SPECTRAL RADIUS BOUNDS REPORT")
        print("=" * 70)
        
        print(f"\nGershgorin Circle Bounds:")
        print(f"  Lower bound: {bounds['gershgorin_lower']:.6f}")
        print(f"  Upper bound: {bounds['gershgorin_upper']:.6f}")
        
        print(f"\nRow Sum Bound (non-negative):")
        print(f"  ρ(A) ≤ max |row sum| = {bounds['max_row_sum']:.6f}")
        
        print(f"\nFrobenius Norm Bound:")
        print(f"  ρ(A) ≤ ‖A‖_F = {bounds['frobenius_bound']:.6f}")
        
        print(f"\nTrace-based Estimate:")
        print(f"  ρ(A) ≈ √(Tr[A²]/n) = {bounds['trace_estimate']:.6f}")
        
        print(f"\nConservative Upper Bound:")
        conservative = bounds['conservative_upper']
        margin = 1.0 - conservative
        print(f"  r ≤ {conservative:.6f}")
        print(f"  margin ≥ {margin:.6f}")
        
        if conservative >= 1.0:
            print(f"\n🚨 WARNING: Upper bound ≥ 1.0 → Network likely non-contractive")
        elif conservative > self.CRITICAL_THRESHOLD:
            print(f"\n⚠️  CAUTION: Upper bound > {self.CRITICAL_THRESHOLD} → Verify carefully")
        elif conservative > self.WARNING_THRESHOLD:
            print(f"\n⚠️  NOTE: Upper bound > {self.WARNING_THRESHOLD} → Approaching threshold")
        
        print("=" * 70 + "\n")
    
    def get_warnings(self) -> List[Dict]:
        """Return all accumulated warnings."""
        return self.warnings.copy()
    
    def clear_warnings(self):
        """Clear warning history."""
        self.warnings = []


class PredictiveLinkerExtension:
    """Extension for PIRTMLinker to add predictive warnings."""
    
    def __init__(self, enable_predictions: bool = True, early_exit: bool = True):
        """Initialize predictor."""
        self.predictor = PredictiveWarningSystem(early_exit_enabled=early_exit)
        self.enable_predictions = enable_predictions
    
    def check_before_linking(self, coupling_matrix: List[List[float]]) -> Tuple[bool, Dict]:
        """
        Pre-linking checks with predictive warnings.
        
        Returns:
            (should_proceed, diagnostics)
        """
        if not self.enable_predictions:
            return True, {}
        
        # Check bounds
        level, bounds = self.predictor.predict_and_warn(coupling_matrix)
        
        # Check for early exit
        should_exit, reason = self.predictor.early_exit_decision(coupling_matrix)
        
        diagnostics = {
            'warning_level': level,
            'bounds': bounds,
            'early_exit': should_exit,
            'exit_reason': reason,
        }
        
        should_proceed = not should_exit
        return should_proceed, diagnostics
