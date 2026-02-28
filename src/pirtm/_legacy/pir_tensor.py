# 📦 pir_tensor.py
# Prime-Indexed Recursive Tensor Operations for PIRTM

import numpy as np
from sympy import primerange, nextprime

class PrimeTensorSystem:
    """
    Handles recursive tensor operations indexed by prime numbers.
    """

    def __init__(self, dim=3, num_primes=100, seed=None):
        self.dim = dim
        self.num_primes = num_primes
        self.primes = self._generate_primes(num_primes)
        self._rng = np.random.default_rng(seed)
        self.state = np.eye(dim)
        self.tensors = self._generate_prime_tensors()

    @staticmethod
    def _generate_primes(count):
        primes = []
        current = 2
        while len(primes) < count:
            primes.append(int(current))
            current = int(nextprime(current))
        return primes

    def _generate_prime_tensors(self):
        """
        Generate a dictionary of prime-indexed transformation tensors.
        Each tensor is a scaled orthogonal matrix perturbed by its prime index.
        """
        tensors = {}
        for p in self.primes:
            base = self._rng.standard_normal((self.dim, self.dim))
            q, _ = np.linalg.qr(base)  # Orthogonalize
            tensors[p] = q * np.sqrt(self.dim)
        return tensors

    def apply(self, prime_index, feedback=None):
        """
        Apply a prime-indexed tensor to the system's current state.
        Optionally include additive feedback.
        """
        p = self.primes[prime_index]
        T = self.tensors[p]
        feedback_term = feedback if feedback is not None else np.zeros_like(self.state)
        self.state = self.state @ T + feedback_term
        return self.state

    def step(self, prime_index, Lambda_m=1.0, feedback=None):
        """
        Recursive PIRTM step with multiplicity constant Λₘ.
        """
        p = self.primes[prime_index]
        T = self.tensors[p]
        Phi = feedback if feedback is not None else np.zeros_like(self.state)
        self.state = Lambda_m * self.state @ T + Phi
        return self.state

    def reset(self, seed=None):
        """
        Reset the system state.
        """
        self.state = seed if seed is not None else np.eye(self.dim)

    def get_state(self):
        return self.state

    def get_tensor(self, prime_index):
        return self.tensors[self.primes[prime_index]]
