# 📦 recursive_ops.py
# Recursive Feedback Operators and Stability Checks for PIRTM

import numpy as np

def recursive_update(Xi, T, Lambda_m=1.0, Phi=None):
    """
    Apply the core PIRTM recursive update:
        Ξ(t+1) = Λₘ * Ξ(t) @ T + Φ(t)
    
    Parameters:
    - Xi (ndarray): Current recursive state matrix Ξ(t)
    - T (ndarray): Prime-indexed tensor operator Tₚ
    - Lambda_m (float): Universal Multiplicity Constant Λₘ
    - Phi (ndarray or None): Feedback term Φ(t)

    Returns:
    - ndarray: Updated state Ξ(t+1)
    """
    Phi = Phi if Phi is not None else np.zeros_like(Xi)
    op_scale = max(1.0, float(np.linalg.norm(T, 2)))
    return Lambda_m * Xi @ (T / op_scale) + Phi

def contraction_check(tensor_sequence, alpha_weights=None, p_indices=None):
    """
    Compute contraction factor for recursive system convergence:
        k = ∑ |α_p · p^β| · ||T||_{HS} < 1

    Parameters:
    - tensor_sequence (list of ndarrays): List of prime-indexed tensors
    - alpha_weights (list of float): Scalar weights per prime (optional)
    - p_indices (list of int): Corresponding prime values (optional)

    Returns:
    - float: Total contraction coefficient k
    """
    k_total = 0.0
    for i, T in enumerate(tensor_sequence):
        norm = np.linalg.norm(T, 'fro')
        alpha = alpha_weights[i] if alpha_weights is not None else 1.0
        p = p_indices[i] if p_indices is not None else i + 2  # fallback primes
        beta = -0.5
        k_total += abs(alpha * p**beta) * norm
    return k_total

def is_stable(k, epsilon=1e-2):
    """
    Determine if the recursive system is stable under contraction.
    
    Returns:
    - bool: True if k < 1 - epsilon
    """
    return k < (1.0 - epsilon)

def feedback_operator(eta_t, memory_kernel=None):
    """
    Model a recursive feedback operator:
        Φ(t) = η(t) + ∫ K(t-τ) η(τ) dτ

    Parameters:
    - eta_t (ndarray): Current entropy or perturbation input
    - memory_kernel (callable or None): Optional function K(tau)

    Returns:
    - ndarray: Feedback-adjusted signal
    """
    if memory_kernel is None:
        return eta_t
    # Approximate convolution with static kernel over finite past
    history = [eta_t * memory_kernel(tau) for tau in range(1, 5)]
    return eta_t + sum(history)
