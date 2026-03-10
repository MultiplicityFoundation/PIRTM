"""
Prime-Cayley Laplacian construction.

Defines the von Mangoldt weighted Laplacian on the PETC (Prime Encoding Tensor Chain).

@spec: DEFINITION HK.1, ADR-015
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class LaplacianParams:
    """
    Parameters for constructing the prime-Cayley Laplacian L^(N).
    
    Attributes
    ----------
    petc_chain : tuple[int, ...]
        Finite PETC: primes (p_1, ..., p_N).
    s1 : float
        Spectral shift parameter. Must satisfy s1 > 1 (@spec-constant).
    """
    petc_chain: tuple[int, ...]
    s1: float = 1.5

    @property
    def N(self) -> int:
        return len(self.petc_chain)

    def __post_init__(self):
        if self.s1 <= 1.0:
            raise ValueError(f"@spec-constant: s1 > 1 required. Got s1={self.s1}")
        if len(self.petc_chain) == 0:
            raise ValueError("petc_chain must be non-empty.")


def von_mangoldt_weights(params: LaplacianParams) -> np.ndarray:
    """
    Compute von Mangoldt weights w_p^vM = log(p) / p^s1.
    
    @spec: DEFINITION HK.1
    
    Parameters
    ----------
    params : LaplacianParams
        Must have petc_chain and s1 > 1.
    
    Returns
    -------
    np.ndarray
        Shape (N,), weights w_p for each prime.
    """
    weights = np.array([
        np.log(p) / (p ** params.s1)
        for p in params.petc_chain
    ])
    return weights


def laplacian_matrix(params: LaplacianParams) -> np.ndarray:
    """
    Construct diagonal Laplacian L^(N) in PETC basis.
    
    @spec: DEFINITION HK.1
    L^(N) = diag(2w_{p_1}, 2w_{p_2}, ..., 2w_{p_N})
    
    Returns
    -------
    np.ndarray
        Shape (N, N), diagonal matrix with eigenvalues 2*w_p.
    """
    w = von_mangoldt_weights(params)
    return np.diag(2.0 * w)


def spectral_radius(params: LaplacianParams) -> float:
    """
    Spectral radius of I - 2*L^(N).
    
    Since L^(N) is diagonal with eigenvalues 2*w_p > 0,
    the spectral radius of I - L^(N) is max_p |1 - 2*w_p|.
    
    @spec: THEOREM HK.4
    """
    w = von_mangoldt_weights(params)
    return float(np.max(np.abs(1.0 - 2.0 * w)))


def lambda_min(params: LaplacianParams) -> float:
    """
    Minimum eigenvalue of L^(N).
    
    @spec: ADR-015 (laplacian_lambda_min)
    For diagonal L: λ_min = 2 * min(w_p).
    """
    w = von_mangoldt_weights(params)
    return float(2.0 * np.min(w))


def iss_bound(params: LaplacianParams) -> float:
    """
    ISS (Input-to-State Stability) bound: ‖G(0;1,1)‖ = 1/λ_min.
    
    @spec: DEFINITION 19.1, ADR-015
    """
    return 1.0 / lambda_min(params)
