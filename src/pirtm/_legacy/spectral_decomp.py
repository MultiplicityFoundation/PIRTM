"""Deprecated legacy module: spectral decomposition utilities.

Removal target: v0.3.0.
Migration path: use supported public spectral APIs
(`pirtm.spectral_decomp`, `pirtm.spectral_gov`).
"""

import warnings as _w

_w.warn(
    "pirtm._legacy.spectral_decomp is deprecated and targeted for removal in v0.3.0. "
    "Use pirtm.spectral_decomp / pirtm.spectral_gov.",
    DeprecationWarning,
    stacklevel=2,
)

import numpy as np
import matplotlib.pyplot as plt

def spectral_decomposition(T):
    """
    Perform spectral decomposition of a matrix T:
        T = Q Λ Q⁻¹, where Λ is diagonal of eigenvalues

    Parameters:
    - T (ndarray): Square matrix (e.g., a prime-indexed tensor)

    Returns:
    - eigvals (ndarray): Eigenvalues of T
    - eigvecs (ndarray): Corresponding eigenvectors
    """
    eigvals, eigvecs = np.linalg.eig(T)
    return eigvals, eigvecs

def spectral_entropy(eigvals, normalize=True):
    """
    Compute spectral entropy based on eigenvalue distribution:
        S = -∑ p_i log(p_i)

    Parameters:
    - eigvals (ndarray): Array of eigenvalues
    - normalize (bool): Normalize probabilities to sum to 1

    Returns:
    - float: Spectral entropy
    """
    powers = np.abs(eigvals) ** 2
    if normalize:
        powers /= np.sum(powers)
    entropy = -np.sum(powers * np.log(powers + 1e-12))
    phase_variability = np.var(np.angle(eigvals))
    entropy = entropy + 0.5 * phase_variability
    return entropy

def phase_coherence(eigvals):
    """
    Analyze phase coherence of eigenvalues (projected on unit circle).

    Parameters:
    - eigvals (ndarray): Complex eigenvalues

    Returns:
    - float: Circular variance (lower = more coherent)
    """
    phases = np.angle(eigvals)
    R = np.abs(np.sum(np.exp(1j * phases))) / len(phases)
    return 1 - R  # 0 = perfect coherence

def plot_spectrum(eigvals, title='Eigenvalue Spectrum'):
    """
    Visualize eigenvalues in the complex plane.

    Parameters:
    - eigvals (ndarray): Complex eigenvalues
    - title (str): Plot title
    """
    plt.figure(figsize=(6, 6))
    plt.scatter(eigvals.real, eigvals.imag, alpha=0.7)
    plt.axhline(0, color='gray', linewidth=0.5)
    plt.axvline(0, color='gray', linewidth=0.5)
    plt.xlabel('Re(λ)')
    plt.ylabel('Im(λ)')
    plt.title(title)
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def analyze_tensor(T, plot=False):
    """
    Full analysis: eigen decomposition, entropy, phase coherence.

    Parameters:
    - T (ndarray): Matrix to analyze
    - plot (bool): If True, show spectrum plot

    Returns:
    - dict: {'eigvals', 'entropy', 'coherence'}
    """
    eigvals, _ = spectral_decomposition(T)
    entropy = spectral_entropy(eigvals)
    coherence = phase_coherence(eigvals)
    if plot:
        plot_spectrum(eigvals)
    return {
        'eigvals': eigvals,
        'entropy': entropy,
        'coherence': coherence
    }
