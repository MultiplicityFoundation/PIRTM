"""Legacy-classified simulation module (R6).

This simulation remains non-core because it still depends on legacy tensor
generation/update surfaces (`pirtm._legacy.PrimeTensorSystem`,
`pirtm._legacy.recursive_update`).

Phase 1 migration status:
- migrated off legacy spectral analysis import to
    `pirtm.spectral_decomp.analyze_tensor`.
"""

import numpy as np
from pirtm._legacy import PrimeTensorSystem
from pirtm._legacy import recursive_update
from pirtm.spectral_decomp import analyze_tensor

class QARIEngine:
    """
    Quantum-Adaptive Recursive Intelligence (QARI) tensor evolution core.
    Implements recursive phase evolution using PIRTM structures in quantum calculator architecture.
    """

    def __init__(self, dim=6, Lambda_m=0.88, seed=None):
        self.dim = dim
        self.Lambda_m = Lambda_m
        self.tensors = PrimeTensorSystem(dim=dim, num_primes=100, seed=seed)
        self.Xi = self.tensors.state
        self.prime_count = self.tensors.num_primes
        self.time = 0
        self.state_history = [self.Xi.copy()]

    def quantum_gate(self, t):
        """
        Simulated gate influenced by a dynamic cognitive phase input.
        Encodes decision logic or entropy injection.
        """
        phase_shift = np.exp(1j * 2 * np.pi * np.sin(t / 15))
        return np.eye(self.dim) * phase_shift

    def evolve(self, steps=100):
        """
        Evolves the QARI tensor field Ξ(t) recursively over `steps` iterations.
        """
        for t in range(steps):
            prime_index = t % self.prime_count
            T = self.tensors.get_tensor(prime_index)
            Phi = self.quantum_gate(t)
            self.Xi = recursive_update(self.Xi, T, self.Lambda_m, Phi)
            self.state_history.append(self.Xi.copy())
            self.time += 1

    def entropy_gradient(self):
        """
        Estimates entropy trajectory of the system.
        """
        return [analyze_tensor(X)['entropy'] for X in self.state_history]

    def phase_stability(self):
        """
        Tracks circular variance of Ξ(t) over time.
        """
        return [analyze_tensor(X)['coherence'] for X in self.state_history]

    def get_final_state(self):
        return self.Xi

    def get_history(self):
        return self.state_history

if __name__ == "__main__":
    print("Initializing QARI Tensor Engine...")
    qari = QARIEngine(dim=6, Lambda_m=0.87)
    qari.evolve(steps=100)

    print("Final State Entropy:", analyze_tensor(qari.get_final_state())['entropy'])
    print("Final Phase Coherence:", analyze_tensor(qari.get_final_state())['coherence'])
