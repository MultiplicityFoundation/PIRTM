"""
PIRTM Dialect Types with Compile-Time Verification

Implements ADR-006: Dialect Type-Layer Gate (Day 0-3)
Spec Reference: PIRTM ADR-004

This module defines:
  - !pirtm.cert(mod=p)     — prime-modulo certificate
  - !pirtm.epsilon(mod=p, value=ε)  — convergence bound
  - !pirtm.op_norm_t(mod=p, norm=n) — operator norm bound
  - !pirtm.session_graph(mod=N, coupling=#pirtm.unresolved_coupling) — session coupling

All types verify mod= constraints at construction time via Miller-Rabin and squarefree tests.
"""

from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum


# ===== Primality Testing =====

def _is_prime_miller_rabin(mod: int) -> bool:
    """
    Miller-Rabin primality test.
    
    Deterministic for mod < 2^64 using standard bases.
    Returns True if mod is prime, False otherwise.
    
    Implements L0 invariant #3: !pirtm.cert requires prime modulus.
    Implements L0 invariant #5: Atomic types require prime modulus.
    """
    if mod < 2:
        return False
    if mod == 2 or mod == 3:
        return True
    if mod % 2 == 0:
        return False
    
    # Write mod - 1 = 2^r * d where d is odd
    d = mod - 1
    r = 0
    while (d & 1) == 0:
        d >>= 1
        r += 1
    
    # Deterministic bases for all mod < 2^64
    bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    
    for a in bases:
        if a >= mod:
            continue
        
        # Compute x = a^d mod mod using modular exponentiation
        x = pow(a, d, mod)
        
        if x == 1 or x == mod - 1:
            continue
        
        composite = True
        for _ in range(r - 1):
            x = pow(x, 2, mod)
            if x == mod - 1:
                composite = False
                break
        
        if composite:
            return False
    
    return True


def _factorize(mod: int) -> Tuple[bool, str]:
    """
    Compute prime factorization of mod.
    
    Returns (is_squarefree, factorization_string) where:
      - is_squarefree: True if μ(mod) ≠ 0 (no repeated factors)
      - factorization_string: "p1^a1 * p2^a2 * ..." in ascending order
    
    Implements L0 invariant #5: Composite mod values must be squarefree.
    """
    if mod <= 1:
        return False, str(mod)
    
    factors = {}
    n = mod
    
    # Trial division up to sqrt(n)
    p = 2
    while p * p <= n:
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
        p += 1
    
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    
    # Check squarefreeness
    is_squarefree = all(count == 1 for count in factors.values())
    
    # Format factorization string
    if not factors:
        fact_str = "1"
    else:
        fact_parts = []
        for prime in sorted(factors.keys()):
            count = factors[prime]
            if count == 1:
                fact_parts.append(str(prime))
            else:
                fact_parts.append(f"{prime}^{count}")
        fact_str = " * ".join(fact_parts)
    
    return is_squarefree, fact_str


# ===== Type Definitions =====

class VerificationError(Exception):
    """Raised when a type constraint verification fails."""
    pass


@dataclass
class CertType:
    """
    !pirtm.cert(mod=p)
    
    Prime-modulo certificate type.
    mod=p must be prime (L0 invariant #3).
    """
    mod: int
    
    def __post_init__(self):
        """Verify mod is prime at construction time."""
        if not _is_prime_miller_rabin(self.mod):
            # Compute factorization for error message
            _, factorization = _factorize(self.mod)
            raise VerificationError(
                f"mod={self.mod} is not prime ({factorization}); "
                f"!pirtm.cert requires prime modulus (L0 invariant #3)"
            )
    
    def __repr__(self) -> str:
        return f"!pirtm.cert(mod={self.mod})"
    
    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class EpsilonType:
    """
    !pirtm.epsilon(mod=p, value=ε)
    
    Convergence bound type.
    mod=p must be prime (L0 invariant #5).
    value=ε is the actual convergence bound (float).
    """
    mod: int
    value: float
    
    def __post_init__(self):
        """Verify mod is prime at construction time."""
        if not _is_prime_miller_rabin(self.mod):
            _, factorization = _factorize(self.mod)
            raise VerificationError(
                f"mod={self.mod} is not prime ({factorization}); "
                f"!pirtm.epsilon requires prime modulus (L0 invariant #5)"
            )
        
        if not (0.0 <= self.value <= 1.0):
            raise VerificationError(
                f"value={self.value} out of range [0, 1]; "
                f"convergence bound must be normalized"
            )
    
    def __repr__(self) -> str:
        return f"!pirtm.epsilon(mod={self.mod}, value={self.value})"
    
    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class OpNormTType:
    """
    !pirtm.op_norm_t(mod=p, norm=n)
    
    Operator norm bound type.
    mod=p must be prime (L0 invariant #5).
    norm=n is the operator norm (float, >= 0).
    """
    mod: int
    norm: float
    
    def __post_init__(self):
        """Verify mod is prime at construction time."""
        if not _is_prime_miller_rabin(self.mod):
            _, factorization = _factorize(self.mod)
            raise VerificationError(
                f"mod={self.mod} is not prime ({factorization}); "
                f"!pirtm.op_norm_t requires prime modulus (L0 invariant #5)"
            )
        
        if self.norm < 0.0:
            raise VerificationError(
                f"norm={self.norm} negative; operator norm must be >= 0"
            )
    
    def __repr__(self) -> str:
        return f"!pirtm.op_norm_t(mod={self.mod}, norm={self.norm})"
    
    def __str__(self) -> str:
        return self.__repr__()


class CouplingType(Enum):
    """Placeholder coupling types for session graphs."""
    UNRESOLVED = "#pirtm.unresolved_coupling"


@dataclass
class SessionGraphType:
    """
    !pirtm.session_graph(mod=N, coupling=coupling_attr)
    
    Session coupling graph type.
    mod=N must be squarefree (L0 invariant #5).
    coupling is one of: #pirtm.unresolved_coupling (transpile-time),
                        actual matrix (link-time).
    
    Implements L0 invariant #4: gain_matrix is never a transpile-time attribute.
    At transpile time, coupling must be #pirtm.unresolved_coupling.
    """
    mod: int
    coupling: CouplingType
    
    def __post_init__(self):
        """Verify mod is squarefree at construction time."""
        is_squarefree, factorization = _factorize(self.mod)
        
        if not is_squarefree:
            raise VerificationError(
                f"mod={self.mod} is not squarefree ({factorization}); "
                f"!pirtm.session_graph requires squarefree modulus (L0 invariant #5)"
            )
        
        # At transpile time, coupling must be unresolved
        if self.coupling != CouplingType.UNRESOLVED:
            raise VerificationError(
                f"coupling={self.coupling} is resolved; "
                f"at transpile time, coupling must be #pirtm.unresolved_coupling "
                f"(L0 invariant #4)"
            )
    
    def __repr__(self) -> str:
        return f"!pirtm.session_graph(mod={self.mod}, coupling={self.coupling.value})"
    
    def __str__(self) -> str:
        return self.__repr__()


# ===== Type Factory =====

def create_cert(mod: int) -> CertType:
    """Factory: create a certificate type with verification."""
    return CertType(mod=mod)


def create_epsilon(mod: int, value: float) -> EpsilonType:
    """Factory: create an epsilon bound type with verification."""
    return EpsilonType(mod=mod, value=value)


def create_op_norm_t(mod: int, norm: float) -> OpNormTType:
    """Factory: create an operator norm type with verification."""
    return OpNormTType(mod=mod, norm=norm)


def create_session_graph(mod: int, coupling: CouplingType = CouplingType.UNRESOLVED) -> SessionGraphType:
    """Factory: create a session graph type with verification."""
    return SessionGraphType(mod=mod, coupling=coupling)


# ===== Utilities for Test Support =====

def is_prime(mod: int) -> bool:
    """Check if mod is prime. Used by tests."""
    return _is_prime_miller_rabin(mod)


def factorize(mod: int) -> str:
    """Get factorization of mod as string. Used by tests."""
    _, fact_str = _factorize(mod)
    return fact_str
