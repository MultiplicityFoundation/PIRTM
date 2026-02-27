from __future__ import annotations

import numpy as np


def spectral_decomposition(T: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    matrix = np.asarray(T, dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("T must be a square matrix")
    eigvals, eigvecs = np.linalg.eig(matrix)
    return eigvals, eigvecs


def spectral_entropy(eigvals: np.ndarray, normalize: bool = True) -> float:
    values = np.asarray(eigvals)
    powers = np.abs(values) ** 2
    total = float(np.sum(powers))
    if normalize and total > 0.0:
        powers = powers / total
    entropy = -float(np.sum(powers * np.log(powers + 1e-12)))
    return entropy


def phase_coherence(eigvals: np.ndarray) -> float:
    values = np.asarray(eigvals)
    if values.size == 0:
        return 0.0
    phases = np.angle(values)
    resultant = float(np.abs(np.mean(np.exp(1j * phases))))
    return 1.0 - resultant


def analyze_tensor(T: np.ndarray) -> dict:
    eigvals, eigvecs = spectral_decomposition(T)
    return {
        "eigvals": eigvals,
        "eigvecs": eigvecs,
        "entropy": spectral_entropy(eigvals),
        "coherence": phase_coherence(eigvals),
    }
