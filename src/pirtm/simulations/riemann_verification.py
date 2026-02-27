# 📦 riemann_verification.py
# Simulating Prime Eigenvalue Interference for PEOH Validation

import numpy as np
import matplotlib.pyplot as plt
from sympy import primerange
from pirtm._legacy import analyze_tensor
from pirtm._legacy import PrimeTensorSystem

def generate_superposition(prime_tensor_sys, num_terms=50):
    """
    Build recursive superposition of eigenvalue spectra:
        Ξ_ζ(s) = ∑ ψ_p e^{-s log p}

    Parameters:
    - prime_tensor_sys (PrimeTensorSystem): Initialized tensor system
    - num_terms (int): Number of primes/spectra to use

    Returns:
    - complex ndarray: Interference field in complex domain
    """
    primes = prime_tensor_sys.primes[:num_terms]
    dim = prime_tensor_sys.dim
    interference_matrix = np.zeros((dim, dim), dtype=complex)

    for i, p in enumerate(primes):
        T = prime_tensor_sys.get_tensor(i)
        eigvals, eigvecs = np.linalg.eig(T)
        decay = np.exp(-0.5 * np.log(p))  # critical line: Re(s) = 1/2
        contribution = sum(eig * decay for eig in eigvals)
        interference_matrix += contribution * np.outer(eigvecs[:, 0], eigvecs[:, 0].conj())

    return interference_matrix

def simulate_peoh_spectrum(prime_tensor_sys, num_terms=50):
    """
    Visualize eigenvalue interference spectrum from prime superposition.

    Parameters:
    - prime_tensor_sys (PrimeTensorSystem)
    - num_terms (int)

    Returns:
    - None (plots spectrum)
    """
    interference_matrix = generate_superposition(prime_tensor_sys, num_terms)
    eigvals, _ = np.linalg.eig(interference_matrix)

    plt.figure(figsize=(6, 6))
    plt.scatter(eigvals.real, eigvals.imag, alpha=0.8, c='darkred')
    plt.title("Simulated Interference Spectrum (Ξ_ζ(s))")
    plt.xlabel("Re(λ)")
    plt.ylabel("Im(λ)")
    plt.grid(True)
    plt.axvline(x=0.5, color='blue', linestyle='--', label="Critical Line")
    plt.legend()
    plt.axis('equal')
    plt.show()

def peoh_diagnostics(prime_tensor_sys, num_terms=50):
    """
    Compute entropy and coherence over simulated interference.

    Parameters:
    - prime_tensor_sys (PrimeTensorSystem)

    Returns:
    - dict with entropy and coherence
    """
    interference_matrix = generate_superposition(prime_tensor_sys, num_terms)
    analysis = analyze_tensor(interference_matrix)
    return {
        'spectral_entropy': analysis['entropy'],
        'phase_coherence': analysis['coherence'],
        'eigvals': analysis['eigvals']
    }

if __name__ == "__main__":
    print("Initializing PIRTM tensor system...")
    pts = PrimeTensorSystem(dim=6, num_primes=80)
    
    print("Simulating Prime Eigenvalue Interference (PEOH)...")
    simulate_peoh_spectrum(pts, num_terms=60)

    print("Running diagnostics...")
    results = peoh_diagnostics(pts, num_terms=60)
    print("Spectral Entropy:", results['spectral_entropy'])
    print("Phase Coherence:", results['phase_coherence'])
