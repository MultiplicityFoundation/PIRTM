"""
PIRTM Contractivity Certification - ACE System (Phase 1+)

ACE (Asymmetric Convergence Envelope) system provides:
1. Convergence proofs via witness commitments
2. Prime-indexed spectral bounds
3. ZK proof generation for trustless verification

Refactored for backend abstraction (Phase 1 Liberation).
See ADR-006 for backend protocol, ADR-004 for contractivity semantics.

Reference: docs/PHASE_1_EXPANDED.md (Days 5 refactoring)
          validators/ace/ (Full ACE implementation)
"""

from typing import Any, Dict, Optional
from ..backend import TensorBackend, Array, Scalar, current_backend


class ContractivityCertificate:
    """
    Certificate that a trajectory is contractive.
    
    Attributes:
        epsilon: Contraction margin (ε in ||q_t|| < 1 - ε)
        confidence: Confidence level (e.g., 0.9999 for 99.99%)
        spectral_radius: Largest eigenvalue of system operator
        state_norm: Norm of final state
        trace_id: Unique identifier for this certification
        ace_proof: Optional ZK proof (Phase 3+)
    """
    
    def __init__(
        self,
        epsilon: Scalar,
        confidence: Scalar,
        spectral_radius: Scalar,
        state_norm: Scalar,
        trace_id: str = "pirtm_cert",
        ace_proof: Optional[Dict[str, Any]] = None,
    ):
        self.epsilon = float(epsilon)
        self.confidence = float(confidence)
        self.spectral_radius = float(spectral_radius)
        self.state_norm = float(state_norm)
        self.trace_id = trace_id
        self.ace_proof = ace_proof or {}
        
        # Verify invariants
        assert self.epsilon > 0, "epsilon must be positive"
        assert 0.0 < self.confidence <= 1.0, "confidence must be in (0, 1]"
        assert self.spectral_radius >= 0, "spectral_radius must be non-negative"
        assert self.state_norm >= 0, "state_norm must be non-negative"
    
    def is_valid(self) -> bool:
        """Check if certificate satisfies L0 invariant."""
        # L0 invariant: state_norm < 1.0 - epsilon
        return self.state_norm < (1.0 - self.epsilon)
    
    def contraction_margin(self) -> Scalar:
        """Remaining contraction margin: 1 - ε - ||q_t||"""
        return (1.0 - self.epsilon) - self.state_norm
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (for storage/transmission)."""
        return {
            "epsilon": self.epsilon,
            "confidence": self.confidence,
            "spectral_radius": self.spectral_radius,
            "state_norm": self.state_norm,
            "trace_id": self.trace_id,
            "is_valid": self.is_valid(),
            "contraction_margin": self.contraction_margin(),
            "ace_proof": self.ace_proof,
        }


def certify_state(
    X: Array,
    epsilon: Scalar = 0.05,
    confidence: Scalar = 0.9999,
    trace_id: str = "pirtm_cert",
    backend: Optional[TensorBackend] = None,
) -> ContractivityCertificate:
    """
    Create contractivity certificate for current state.
    
    Args:
        X: Current state vector
        epsilon: Contraction margin (default 0.05)
        confidence: Confidence level (default 0.9999)
        trace_id: Unique identifier for this trace
        backend: TensorBackend to use
    
    Returns:
        ContractivityCertificate instance
    
    This is the basic runtime certification. Full ACE proof generation
    happens in Phase 2+ via circom circuits + snarkjs.
    """
    if backend is None:
        backend = current_backend()
    
    state_norm = backend.norm(X)
    
    # TODO: Compute spectral radius from operator
    # For now, use state norm as proxy (conservative)
    spectral_radius = state_norm
    
    cert = ContractivityCertificate(
        epsilon=epsilon,
        confidence=confidence,
        spectral_radius=spectral_radius,
        state_norm=state_norm,
        trace_id=trace_id,
    )
    
    return cert


def verify_trajectory(
    trajectory: list[Any],
    epsilon: Scalar = 0.05,
    backend: Optional[TensorBackend] = None,
) -> Dict[str, Any]:
    """
    Verify entire trajectory satisfies contractivity.
    
    Args:
        trajectory: List of state vectors over time
        epsilon: Contraction margin
        backend: TensorBackend to use
    
    Returns:
        Dict with verification results:
        - all_valid: True if all states satisfy invariant
        - violations: List of (t, state_norm) where invariant fails
        - max_margin: Minimum remaining contraction margin
    """
    if backend is None:
        backend = current_backend()
    
    violations = []
    margins = []
    
    margins: list[float] = []
    violations: list[tuple[int, float]] = []
    
    for t, X_t in enumerate(trajectory):
        norm_t = backend.norm(X_t)
        margin = (1.0 - epsilon) - norm_t
        margins.append(margin)
        
        if margin < 0:
            violations.append((t, float(norm_t)))
    
    return {
        "all_valid": len(violations) == 0,
        "violations": violations,
        "max_margin": float(min(margins)) if margins else 0.0,
        "total_steps": len(trajectory),
    }


__all__ = [
    "ContractivityCertificate",
    "certify_state",
    "verify_trajectory",
]
