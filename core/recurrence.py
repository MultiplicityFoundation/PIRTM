"""
PIRTM Recurrence Loop - Core Contractive Iteration (Phase 1+)

The fundamental recurrence relation:
  X_{t+1} = P(Ξ_t X_t + Λ_t T(X_t) + G_t)

Where:
  - P: Projection operator (clipping to [-1, 1])
  - Ξ_t: Identity operator (or general linear operator)
  - Λ_t: Aggregation operator (learns how much to weight transformation)
  - G_t: Growth/guidance term (external input)
  - T: Nonlinear transformation (sigmoid)

Refactored for backend abstraction (Phase 1 Liberation).
See ADR-006 for backend protocol, ADR-004 for contractivity semantics.

Reference: docs/PHASE_1_EXPANDED.md (Days 3-4 refactoring)
"""

from typing import Any, Callable, Dict, Optional, Tuple
from ..backend import Array, Scalar, TensorBackend, current_backend


def step(
    X_t: Array,
    Xi_t: Array,
    Lambda_t: Array,
    G_t: Optional[Array] = None,
    T_func: Optional[Callable[[Array], Array]] = None,
    backend: Optional[TensorBackend] = None,
) -> Tuple[Array, Dict[str, Scalar]]:
    """
    Execute one step of the PIRTM recurrence.
    
    Computes: X_{t+1} = P(Ξ_t X_t + Λ_t T(X_t) + G_t)
    
    Args:
        X_t: Current state vector, shape (n,)
        Xi_t: Linear operator (identity or general), shape (n, n)
        Lambda_t: Aggregation operator, shape (n, n)
        G_t: Optional growth term, shape (n,). Defaults to zeros.
        T_func: Nonlinear transformation. Defaults to sigmoid.
        backend: TensorBackend to use. Defaults to current backend.
    
    Returns:
        Tuple of (X_next, metadata) where:
        - X_next: Next state vector, shape (n,)
        - metadata: Dict with timing/debugging info
    
    Contractivity Guarantee:
        If ||Ξ|| + ||Λ||·||T'|| < 1 - ε, then contraction is certified.
        This is verified at transpile-time (Phase 2+) via MLIR.
    """
    if backend is None:
        backend = current_backend()
    
    if T_func is None:
        T_func = lambda x: backend.sigmoid(x)
    
    if G_t is None:
        G_t = backend.zeros(X_t.shape)
    
    # Compute each term
    term1 = backend.matmul(Xi_t, X_t)
    T_X_t = T_func(X_t)
    term2 = backend.matmul(Lambda_t, T_X_t)
    
    # Sum: Y_t = Ξ X_t + Λ T(X_t) + G_t
    Y_t = backend.add(term1, term2)
    Y_t = backend.add(Y_t, G_t)
    
    # Project: X_{t+1} = P(Y_t) = clip(Y_t, -1, 1)
    X_next = backend.clip(Y_t, -1.0, 1.0)
    
    # Metadata for debugging
    metadata: Dict[str, Any] = {
        "norm_X_t": backend.norm(X_t),
        "norm_X_next": backend.norm(X_next),
        "norm_Y_t": backend.norm(Y_t),
        "backend": backend.name(),
    }
    
    return X_next, metadata


def iterate(
    X_0: Array,
    policy: Any,  # CarryForwardPolicy (imported separately)
    kernel: Any,  # FullAsymmetricAttributionKernel
    steps: int,
    backend: Optional[TensorBackend] = None,
) -> Dict[str, Any]:
    """
    Execute multiple recurrence steps with ledger tracking.
    
    Args:
        X_0: Initial state vector
        policy: CarryForwardPolicy instance (Phase 1+ ledger support)
        kernel: FullAsymmetricAttributionKernel instance
        steps: Number of iterations
        backend: TensorBackend to use
    
    Returns:
        Dict with trajectory and metadata:
        - trajectory: List of state vectors over time
        - metadata: Aggregated timing info
        - ledger_entries: Event history (if ledger tracking enabled)
    
    Note: This function integrates with Multiplicity ledger system (Phase 2+).
    """
    if backend is None:
        backend = current_backend()
    
    trajectory = [X_0]
    X_t = X_0
    
    for t in range(steps):
        # Get operators from policy/kernel
        # (Implementation assumes policy.Xi_t(t), policy.Lambda_t(t), etc.)
        Xi_t = getattr(policy, "Xi_t", lambda t: backend.eye(X_t.shape[0]))  # type: ignore
        Xi_t = Xi_t(t)
        Lambda_t = getattr(policy, "Lambda_t", lambda t: backend.zeros((X_t.shape[0], X_t.shape[0])))  # type: ignore
        Lambda_t = Lambda_t(t)
        G_t = getattr(policy, "G_t", lambda t: backend.zeros(X_t.shape[0]))  # type: ignore
        G_t = G_t(t)
        
        X_t, _ = step(X_t, Xi_t, Lambda_t, G_t, backend=backend)
        trajectory.append(X_t)
    
    return {
        "trajectory": trajectory,
        "final_state": X_t,
        "steps": steps,
        "backend": backend.name(),
    }


__all__ = ["step", "iterate"]
