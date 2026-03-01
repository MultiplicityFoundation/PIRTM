"""Core-backed helpers for simulation modernization (R6).

These helpers provide non-legacy simulation primitives to replace
`pirtm._legacy` dependencies in simulation modules.
"""

from __future__ import annotations

import numpy as np

from pirtm.spectral_decomp import analyze_tensor


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    limit = int(np.sqrt(n)) + 1
    for candidate in range(3, limit, 2):
        if n % candidate == 0:
            return False
    return True


def generate_primes(count: int) -> list[int]:
    primes: list[int] = []
    value = 2
    while len(primes) < count:
        if _is_prime(value):
            primes.append(value)
        value += 1
    return primes


class PrimeTensorBank:
    """Prime-indexed tensor bank using modern local generator logic."""

    def __init__(self, dim: int = 3, num_primes: int = 100, seed: int | None = None):
        self.dim = int(dim)
        self.num_primes = int(num_primes)
        self.primes = generate_primes(self.num_primes)
        self._rng = np.random.default_rng(seed)
        self.state = np.eye(self.dim, dtype=complex)
        self.tensors = self._generate_prime_tensors()

    def _generate_prime_tensors(self) -> dict[int, np.ndarray]:
        tensors: dict[int, np.ndarray] = {}
        for prime in self.primes:
            base = self._rng.standard_normal((self.dim, self.dim))
            q_matrix, _ = np.linalg.qr(base)
            tensors[prime] = q_matrix * np.sqrt(self.dim)
        return tensors

    def get_tensor(self, prime_index: int) -> np.ndarray:
        return self.tensors[self.primes[prime_index]]


def recursive_update(
    Xi: np.ndarray,
    tensor: np.ndarray,
    Lambda_m: float = 1.0,
    Phi: np.ndarray | None = None,
) -> np.ndarray:
    """Norm-safe recurrence update used by modernized simulations."""
    Phi = Phi if Phi is not None else np.zeros_like(Xi)
    op_scale = max(1.0, float(np.linalg.norm(tensor, 2)))
    return Lambda_m * Xi @ (tensor / op_scale) + Phi


def feedback_operator(
    eta_t: np.ndarray,
    memory_kernel: callable | None = None,
) -> np.ndarray:
    """Simulation-local feedback operator replacement for legacy helper."""
    if memory_kernel is None:
        return eta_t
    history = [eta_t * memory_kernel(tau) for tau in range(1, 5)]
    return eta_t + sum(history)


def analyze_tensor_with_plot(tensor: np.ndarray, plot: bool = False) -> dict:
    """Analyze tensor using supported API and optional compatibility plotting."""
    analysis = analyze_tensor(tensor)
    if plot:
        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:  # pragma: no cover - optional runtime branch
            raise RuntimeError(
                "plot=True requires matplotlib; install with legacy/all extras"
            ) from exc

        eigvals = analysis["eigvals"]
        plt.figure(figsize=(6, 6))
        plt.scatter(eigvals.real, eigvals.imag, alpha=0.7)
        plt.axhline(0, color="gray", linewidth=0.5)
        plt.axvline(0, color="gray", linewidth=0.5)
        plt.xlabel("Re(λ)")
        plt.ylabel("Im(λ)")
        plt.title("Eigenvalue Spectrum")
        plt.grid(True)
        plt.axis("equal")
        plt.show()
    return analysis
