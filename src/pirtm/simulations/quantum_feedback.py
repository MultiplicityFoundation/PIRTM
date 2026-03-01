"""Modernized simulation module (R6).

This module has been migrated off `pirtm._legacy` generator/update/feedback
dependencies and uses core-backed simulation helpers.
"""

import numpy as np

from pirtm.simulations.core_helpers import (
        PrimeTensorBank,
        analyze_tensor_with_plot,
        feedback_operator,
        recursive_update,
)

class QuantumFeedbackSimulator:
    """
    Models dynamic recursive evolution of Ξ(t) with quantum-inspired feedback.
    """

    def __init__(self, dim=4, num_primes=50, Lambda_m=0.9, seed=None):
        self.Lambda_m = Lambda_m
        self.pts = PrimeTensorBank(dim=dim, num_primes=num_primes, seed=seed)
        self.Xi = self.pts.state
        self.history = [self.Xi.copy()]
        self.feedback_history = []

    def eta_entropy(self, t, freq=3.0):
        """
        Defines a rotating phase entropy injection η(t).
        """
        phase = np.pi * np.sin(freq * t / 10)
        return np.eye(self.Xi.shape[0]) * np.exp(1j * phase)

    def memory_kernel(self, tau):
        """
        Basic exponential decay memory kernel K(tau).
        """
        return np.exp(-0.5 * tau)

    def step(self, t, prime_index):
        """
        Evolve Ξ(t) under quantum feedback from η(t) and memory kernel.
        """
        eta_t = self.eta_entropy(t)
        Phi_t = feedback_operator(eta_t, self.memory_kernel)
        self.feedback_history.append(Phi_t)
        T = self.pts.get_tensor(prime_index)
        self.Xi = recursive_update(self.Xi, T, self.Lambda_m, Phi_t)
        self.history.append(self.Xi.copy())

    def run(self, steps=50):
        """
        Run recursive simulation for a number of time steps.
        """
        for t in range(steps):
            self.step(t, prime_index=t % self.pts.num_primes)

    def analyze_final_state(self, plot=True):
        """
        Perform spectral analysis on final state Ξ(T).
        """
        return analyze_tensor_with_plot(self.Xi, plot=plot)

    def get_state_history(self):
        return self.history

    def get_feedback_history(self):
        return self.feedback_history

if __name__ == "__main__":
    print("Launching Quantum Feedback Evolution with PIRTM...")
    sim = QuantumFeedbackSimulator(dim=5, num_primes=40, Lambda_m=0.85)
    sim.run(steps=60)

    print("Analyzing final recursive state...")
    results = sim.analyze_final_state(plot=True)
    print("Spectral Entropy:", results['entropy'])
    print("Phase Coherence:", results['coherence'])
