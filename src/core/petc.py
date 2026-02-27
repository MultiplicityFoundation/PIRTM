from __future__ import annotations

import math
from typing import Iterable

from .types import PETCReport


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    limit = int(math.sqrt(n)) + 1
    for k in range(3, limit, 2):
        if n % k == 0:
            return False
    return True


def petc_invariants(primes: Iterable[int], min_length: int = 3) -> PETCReport:
    """Validate a prime-typed event-triggered chain (PETC)."""

    primes_list = list(primes)
    violations: list[int] = []
    for idx, value in enumerate(primes_list):
        if not _is_prime(int(value)):
            violations.append(idx)

    if primes_list and len(violations) >= max(1, math.ceil(len(primes_list) / 2)):
        raise ValueError("PETC mass violation: majority of entries are not prime")

    satisfied = len(violations) == 0 and len(primes_list) >= min_length
    return PETCReport(
        satisfied=satisfied,
        violations=violations,
        primes_checked=[int(p) for p in primes_list],
    )
